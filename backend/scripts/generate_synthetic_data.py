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
    
    # Generate a synthetic mammogram-like circular intensity field
    y, x = np.ogrid[:256, :256]
    center_y, center_x = 128, 64 if laterality == "L" else 192
    mask = (x - center_x) ** 2 + (y - center_y) ** 2 <= 100 ** 2
    img = np.zeros((256, 256), dtype=np.uint16)
    img[mask] = (np.random.normal(2000, 300, size=mask.sum())).clip(500, 4095).astype(np.uint16)
    
    ds.PixelData = img.tobytes()
    ds.save_as(str(file_path), write_like_original=False)


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic CMMD1 DICOM and clinical data for testing.")
    ap.add_argument("--raw-dir", default="backend/data/raw", help="Output raw data directory")
    ap.add_argument("--num-patients", type=int, default=20, help="Number of synthetic patients to generate")
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir)
    cmmd_dir = raw_dir / "CMMD"
    cmmd_dir.mkdir(parents=True, exist_ok=True)

    clinical_rows = []
    print(f"Generating {args.num_patients} synthetic CMMD1 patients...")
    for i in range(1, args.num_patients + 1):
        patient_id = f"D1-{i:04d}"
        age = np.random.randint(25, 75)
        classification = "Malignant" if (i % 2 == 0) else "Benign"
        
        # Save DICOMs for CC and MLO views
        p_dir = cmmd_dir / patient_id
        create_synthetic_dicom(p_dir / "CC.dcm", patient_id, "CC", "L")
        create_synthetic_dicom(p_dir / "MLO.dcm", patient_id, "MLO", "L")

        clinical_rows.append({
            "ID1": patient_id,
            "ID2": patient_id,
            "Age": age,
            "classification": classification,
        })

    clin_df = pd.DataFrame(clinical_rows)
    xlsx_path = raw_dir / "CMMD_clinicaldata_revision.xlsx"
    clin_df.to_excel(xlsx_path, index=False)
    print(f"Synthetic clinical spreadsheet saved to: {xlsx_path}")
    print(f"Synthetic DICOM images saved under: {cmmd_dir}")


if __name__ == "__main__":
    main()
