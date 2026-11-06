from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import pandas as pd
import pydicom
from sklearn.model_selection import train_test_split
from tqdm import tqdm

ID_RE = re.compile(r"[A-Z]\d-\d{4}", re.I)


def norm_id(x):
    if pd.isna(x):
        return ""
    m = ID_RE.search(str(x).upper())
    return m.group(0) if m else str(x).strip().upper()


def find_col(df, patterns, numeric=False):
    for col in df.columns:
        s = str(col).strip().lower()
        if any(p in s for p in patterns):
            if numeric:
                vals = pd.to_numeric(df[col], errors="coerce")
                if vals.notna().mean() > 0.7:
                    return col
            else:
                return col
    return None


def detect_label_col(df):
    preferred = [c for c in df.columns if any(k in str(c).lower() for k in ["category", "classification", "pathology", "diagnosis"])]
    candidates = preferred + list(df.columns)
    best = None
    best_score = -1
    for col in candidates:
        vals = df[col].dropna().astype(str).str.strip().str.lower()
        uniq = set(vals.unique())
        has_b = any("benign" == v or v.startswith("benign") for v in uniq)
        has_m = any("malignant" == v or v.startswith("malignant") for v in uniq)
        score = int(has_b) + int(has_m)
        if score == 2 and len(uniq) <= 10:
            if any(k in str(col).lower() for k in ["category", "classification", "pathology", "diagnosis"]):
                score += 2
            if score > best_score:
                best, best_score = col, score
    if best is None:
        raise RuntimeError("Could not auto-detect the benign/malignant label column. Pass --label-col explicitly.")
    return best


def label_to_int(v):
    s = str(v).strip().lower()
    if s.startswith("malignant"):
        return 1
    if s.startswith("benign"):
        return 0
    return np.nan


def main():
    ap = argparse.ArgumentParser(description="Build a patient-level CMMD1 multimodal index.")
    ap.add_argument("--image-root", default="backend/data/raw/CMMD", help="Root directory containing CMMD DICOMs")
    ap.add_argument("--clinical-xlsx", default="backend/data/raw/CMMD_clinicaldata_revision.xlsx", help="CMMD_clinicaldata_revision.xlsx")
    ap.add_argument("--output", default="backend/data/processed/cmmd1_index.csv")
    ap.add_argument("--label-col", default=None)
    ap.add_argument("--age-col", default=None)
    args = ap.parse_args()

    clinical_path = Path(args.clinical_xlsx)
    image_root = Path(args.image_root)

    if not clinical_path.exists():
        # Try relative to current script directory if default path wasn't found
        alt_path = Path(__file__).resolve().parent.parent / "data" / "raw" / "CMMD_clinicaldata_revision.xlsx"
        if alt_path.exists():
            clinical_path = alt_path

    if not clinical_path.exists():
        raise FileNotFoundError(f"Clinical file not found at {args.clinical_xlsx}. Run synthetic generator or download dataset.")

    clinical = pd.read_excel(clinical_path)
    id_cols = [c for c in clinical.columns if "id" in str(c).lower()]
    if not id_cols:
        raise RuntimeError(f"No ID-like columns found. Columns: {list(clinical.columns)}")

    age_col = args.age_col or find_col(clinical, ["age"], numeric=True)
    if age_col is None:
        raise RuntimeError(f"Could not find age column. Columns: {list(clinical.columns)}")

    label_col = args.label_col or detect_label_col(clinical)
    print(f"Using age column: {age_col}")
    print(f"Using label column: {label_col}")
    print(f"ID columns: {id_cols}")

    clin = clinical.copy()
    clin["age_num"] = pd.to_numeric(clin[age_col], errors="coerce")
    clin["label_num"] = clin[label_col].map(label_to_int)
    clin["patient_key"] = ""
    alias_map = {}
    for _, r in clin.iterrows():
        aliases = [norm_id(r[c]) for c in id_cols]
        aliases = [a for a in aliases if a]
        if not aliases:
            continue
        patient_key = next((a for a in aliases if a.upper().startswith("D1-")), aliases[0])
        row = {"patient_key": patient_key, "age": r["age_num"], "label": r["label_num"]}
        for a in aliases:
            alias_map[a] = row

    if not image_root.exists():
        alt_img_root = Path(__file__).resolve().parent.parent / "data" / "raw" / "CMMD"
        if alt_img_root.exists():
            image_root = alt_img_root

    dcm_paths = list(image_root.rglob("*.dcm")) + list(image_root.rglob("*.DCM"))
    if not dcm_paths:
        raise RuntimeError(f"No DICOM files found under {image_root}")

    groups = {}
    failures = 0
    for path in tqdm(dcm_paths, desc="Indexing DICOM headers"):
        try:
            ds = pydicom.dcmread(str(path), stop_before_pixels=True, force=True)
            pid = norm_id(getattr(ds, "PatientID", ""))
            if not pid or pid not in alias_map:
                continue
            info = alias_map[pid]
            if not str(info["patient_key"]).upper().startswith("D1-"):
                continue
            view = str(getattr(ds, "ViewPosition", "")).upper().strip()
            if view not in {"CC", "MLO"}:
                continue
            laterality = str(getattr(ds, "ImageLaterality", "")).upper().strip()
            key = info["patient_key"]
            groups.setdefault(key, []).append((view, laterality, str(path)))
        except Exception:
            failures += 1

    rows = []
    for patient_id, files in groups.items():
        info = alias_map.get(patient_id)
        if info is None or pd.isna(info["label"]):
            continue
        by_view = {"CC": [], "MLO": []}
        for view, laterality, path in files:
            by_view[view].append(path)
        cc_path = sorted(by_view["CC"])[0] if by_view["CC"] else ""
        mlo_path = sorted(by_view["MLO"])[0] if by_view["MLO"] else ""
        if not cc_path and not mlo_path:
            continue
        rows.append({
            "patient_id": patient_id,
            "cc_path": cc_path,
            "mlo_path": mlo_path,
            "age": float(info["age"]) if pd.notna(info["age"]) else np.nan,
            "label": int(info["label"]),
        })

    df = pd.DataFrame(rows).drop_duplicates("patient_id").reset_index(drop=True)
    if len(df) < 4:
        raise RuntimeError(f"Only {len(df)} patients matched. Check DICOM/clinical IDs before training.")

    def safe_stratify(labels):
        if labels is None or len(labels) == 0:
            return None
        counts = pd.Series(labels).value_counts()
        if len(counts) > 1 and counts.min() >= 2:
            return labels
        return None

    train_ids, temp_ids = train_test_split(df.index, test_size=0.40, random_state=42, stratify=safe_stratify(df["label"]))
    val_ids, test_ids = train_test_split(temp_ids, test_size=0.50, random_state=42, stratify=safe_stratify(df.loc[temp_ids, "label"]))
    split = pd.Series("train", index=df.index)
    split.loc[val_ids] = "val"
    split.loc[test_ids] = "test"
    df["split"] = split

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} patient rows to {out}")
    print(df.groupby(["split", "label"]).size().unstack(fill_value=0))
    print(f"DICOM header read failures: {failures}")


if __name__ == "__main__":
    main()
