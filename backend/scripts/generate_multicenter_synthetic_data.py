"""Generate synthetic multi-center mammography datasets for testing CARE-XAI.

Creates realistic directory structures, DICOM files, and clinical metadata for:
1. CMMD
2. CBIS-DDSM
3. INbreast
4. VinDr-Mammo
5. EMBED
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
import pydicom
from pydicom.dataset import Dataset, FileDataset
from pydicom.uid import ExplicitVRLittleEndian, SecondaryCaptureImageStorage, generate_uid


def create_synthetic_dicom(file_path: Path, patient_id: str, view_position: str, laterality: str = "L"):
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_meta = Dataset()
    file_meta.MediaStorageSOPClassUID = SecondaryCaptureImageStorage
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    
    ds = FileDataset(str(file_path), {}, file_meta=file_meta, preamble=b"\0" * 128)
    ds.PatientID = patient_id
    ds.ViewPosition = view_position
    ds.ImageLaterality = laterality
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    ds.Rows = 256
    ds.Columns = 256
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0
    ds.RescaleSlope = "1"
    ds.RescaleIntercept = "0"
    ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
    
    # Generate synthetic breast shape
    y, x = np.ogrid[:256, :256]
    center_y, center_x = 128, 64 if laterality == "L" else 192
    mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= 100 ** 2
    img = np.zeros((256, 256), dtype=np.uint16)
    img[mask] = (np.random.normal(2000, 300, size=mask.sum())).clip(500, 4095).astype(np.uint16)
    
    ds.PixelData = img.tobytes()
    ds.save_as(str(file_path), write_like_original=False)


def generate_cmmd(raw_dir: Path, n: int):
    cmmd_dir = raw_dir / "CMMD"
    cmmd_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"Generating CMMD ({n} patients)...")
    for i in range(1, n + 1):
        pid = f"D1-{i:04d}"
        age = np.random.randint(25, 75)
        label = "Malignant" if (i % 2 == 0) else "Benign"
        p_dir = cmmd_dir / pid
        create_synthetic_dicom(p_dir / "CC.dcm", pid, "CC", "L")
        create_synthetic_dicom(p_dir / "MLO.dcm", pid, "MLO", "L")
        rows.append({"ID1": pid, "Age": age, "classification": label})
    pd.DataFrame(rows).to_excel(raw_dir / "CMMD_clinicaldata_revision.xlsx", index=False)


def generate_cbis_ddsm(raw_dir: Path, n: int):
    cbis_dir = raw_dir / "CBIS-DDSM"
    cbis_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"Generating CBIS-DDSM ({n} patients)...")
    for i in range(1, n + 1):
        pid = f"P_{i:05d}"
        density = np.random.choice([1, 2, 3, 4])
        pathology = "MALIGNANT" if (i % 2 == 0) else "BENIGN"
        p_dir = cbis_dir / pid
        cc_file = p_dir / f"{pid}_LEFT_CC.dcm"
        mlo_file = p_dir / f"{pid}_LEFT_MLO.dcm"
        create_synthetic_dicom(cc_file, pid, "CC", "L")
        create_synthetic_dicom(mlo_file, pid, "MLO", "L")
        
        # CC row
        rows.append({
            "patient_id": pid,
            "breast_density": density,
            "left or right breast": "LEFT",
            "image view": "CC",
            "pathology": pathology,
            "image file path": str(cc_file.relative_to(raw_dir.parent)),
            "age": np.random.randint(35, 80),
        })
        # MLO row
        rows.append({
            "patient_id": pid,
            "breast_density": density,
            "left or right breast": "LEFT",
            "image view": "MLO",
            "pathology": pathology,
            "image file path": str(mlo_file.relative_to(raw_dir.parent)),
            "age": np.random.randint(35, 80),
        })
    df = pd.DataFrame(rows)
    half = len(df) // 2
    df.iloc[:half].to_csv(cbis_dir / "mass_case_description_train_set.csv", index=False)
    df.iloc[half:].to_csv(cbis_dir / "mass_case_description_test_set.csv", index=False)


def generate_inbreast(raw_dir: Path, n: int):
    inbreast_dir = raw_dir / "INbreast"
    dicom_dir = inbreast_dir / "AllDICOMs"
    dicom_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"Generating INbreast ({n} patients)...")
    for i in range(1, n + 1):
        pid = f"{1000 + i}"
        age = np.random.randint(30, 80)
        birads = 5 if (i % 2 == 0) else 2
        acr = np.random.choice([1, 2, 3, 4])
        
        cc_fn = f"{pid}_CC.dcm"
        mlo_fn = f"{pid}_MLO.dcm"
        create_synthetic_dicom(dicom_dir / cc_fn, pid, "CC", "L")
        create_synthetic_dicom(dicom_dir / mlo_fn, pid, "MLO", "L")
        
        rows.append({
            "Patient ID": pid,
            "Patient age": age,
            "Laterality": "L",
            "View": "CC",
            "File Name": f"{pid}_CC",
            "Bi-Rads": birads,
            "ACR": acr,
        })
        rows.append({
            "Patient ID": pid,
            "Patient age": age,
            "Laterality": "L",
            "View": "MLO",
            "File Name": f"{pid}_MLO",
            "Bi-Rads": birads,
            "ACR": acr,
        })
    pd.DataFrame(rows).to_csv(inbreast_dir / "INbreast.csv", index=False)


def generate_vindr(raw_dir: Path, n: int):
    vindr_dir = raw_dir / "VinDr-Mammo"
    img_dir = vindr_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"Generating VinDr-Mammo ({n} patients/studies)...")
    for i in range(1, n + 1):
        study_id = f"study_{i:04d}"
        p_dir = img_dir / study_id
        cc_id = f"img_cc_{i:04d}"
        mlo_id = f"img_mlo_{i:04d}"
        create_synthetic_dicom(p_dir / f"{cc_id}.dcm", study_id, "CC", "L")
        create_synthetic_dicom(p_dir / f"{mlo_id}.dcm", study_id, "MLO", "L")
        
        birads = "BI-RADS 5" if (i % 2 == 0) else "BI-RADS 1"
        density = "DENSITY C"
        
        rows.append({
            "study_id": study_id,
            "series_id": f"series_{i}",
            "image_id": cc_id,
            "laterality": "L",
            "view_position": "CC",
            "breast_birads": birads,
            "breast_density": density,
            "split": "training" if i <= int(0.8 * n) else "test",
        })
        rows.append({
            "study_id": study_id,
            "series_id": f"series_{i}",
            "image_id": mlo_id,
            "laterality": "L",
            "view_position": "MLO",
            "breast_birads": birads,
            "breast_density": density,
            "split": "training" if i <= int(0.8 * n) else "test",
        })
    pd.DataFrame(rows).to_csv(vindr_dir / "breast-level_annotations.csv", index=False)


def generate_embed(raw_dir: Path, n: int):
    embed_dir = raw_dir / "EMBED"
    img_dir = embed_dir / "images"
    img_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    print(f"Generating EMBED ({n} patients)...")
    for i in range(1, n + 1):
        pid = f"EMBED_{i:04d}"
        p_dir = img_dir / pid
        cc_file = p_dir / "CC.dcm"
        mlo_file = p_dir / "MLO.dcm"
        create_synthetic_dicom(cc_file, pid, "CC", "L")
        create_synthetic_dicom(mlo_file, pid, "MLO", "L")
        
        pathology = "Malignant" if (i % 2 == 0) else "Benign"
        age = np.random.randint(30, 85)
        
        rows.append({
            "empi_anon": pid,
            "acc_anon": f"ACC_{i:04d}",
            "view_position": "CC",
            "laterality": "L",
            "age": age,
            "pathology": pathology,
            "image_path": str(cc_file.relative_to(raw_dir.parent)),
            "split": "train" if i <= int(0.7 * n) else ("val" if i <= int(0.85 * n) else "test"),
        })
        rows.append({
            "empi_anon": pid,
            "acc_anon": f"ACC_{i:04d}",
            "view_position": "MLO",
            "laterality": "L",
            "age": age,
            "pathology": pathology,
            "image_path": str(mlo_file.relative_to(raw_dir.parent)),
            "split": "train" if i <= int(0.7 * n) else ("val" if i <= int(0.85 * n) else "test"),
        })
    pd.DataFrame(rows).to_csv(embed_dir / "embed_metadata.csv", index=False)


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic multi-center mammography datasets.")
    ap.add_argument("--raw-dir", default="backend/data/raw", help="Target raw data root directory")
    ap.add_argument("--num-patients-per-dataset", type=int, default=10, help="Number of synthetic cases per dataset")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir).resolve()
    raw_dir.mkdir(parents=True, exist_ok=True)
    n = args.num_patients_per_dataset

    print(f"=== Generating Multi-Center Synthetic Datasets in {raw_dir} ===")
    generate_cmmd(raw_dir, n)
    generate_cbis_ddsm(raw_dir, n)
    generate_inbreast(raw_dir, n)
    generate_vindr(raw_dir, n)
    generate_embed(raw_dir, n)
    print("=== Multi-Center Synthetic Data Generation Complete! ===")


if __name__ == "__main__":
    main()
