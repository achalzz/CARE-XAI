"""Build patient-level dual-view index for EMBED (Emory Breast Imaging Dataset)."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def parse_embed(root: Path, output_csv: Path, seed: int = 42):
    csv_candidates = list(root.glob("*.csv"))
    if not csv_candidates:
        raise FileNotFoundError(f"No EMBED CSV files found in {root}")

    df = pd.read_csv(csv_candidates[0])
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

    pid_col = next((c for c in df.columns if "empi" in c or "patient" in c), None)
    view_col = next((c for c in df.columns if "view" in c), None)
    path_col = next((c for c in df.columns if "path" in c and "image" in c) or (c for c in df.columns if "path" in c), None)
    pathology_col = next((c for c in df.columns if "pathology" in c or "label" in c or "diag" in c), None)
    age_col = next((c for c in df.columns if "age" in c), None)

    if not pid_col or not view_col:
        raise RuntimeError(f"Missing required columns in {csv_candidates[0]}. Found: {list(df.columns)}")

    def map_pathology(v):
        s = str(v).upper()
        if "MALIGNANT" in s or "CANCER" in s:
            return 1
        if "BENIGN" in s or "NORMAL" in s:
            return 0
        return np.nan

    if pathology_col:
        df["label"] = df[pathology_col].apply(map_pathology)
    else:
        df["label"] = 0

    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)

    # Search for all DICOM files
    dicom_map = {}
    for dcm in root.rglob("*.dcm"):
        dicom_map[dcm.name.lower()] = str(dcm)
        dicom_map[dcm.stem.lower()] = str(dcm)

    patients = []
    for pid, group in df.groupby(pid_col):
        cc_row = group[group[view_col].astype(str).str.upper().str.contains("CC")]
        mlo_row = group[group[view_col].astype(str).str.upper().str.contains("MLO")]

        cc_path, mlo_path = "", ""
        if not cc_row.empty:
            raw_p = str(cc_row.iloc[0].get(path_col, "")) if path_col else ""
            if raw_p and Path(raw_p).exists():
                cc_path = raw_p
            elif raw_p and (root / raw_p).exists():
                cc_path = str(root / raw_p)
            else:
                p_dir = root / "images" / str(pid)
                if (p_dir / "CC.dcm").exists():
                    cc_path = str(p_dir / "CC.dcm")

        if not mlo_row.empty:
            raw_p = str(mlo_row.iloc[0].get(path_col, "")) if path_col else ""
            if raw_p and Path(raw_p).exists():
                mlo_path = raw_p
            elif raw_p and (root / raw_p).exists():
                mlo_path = str(root / raw_p)
            else:
                p_dir = root / "images" / str(pid)
                if (p_dir / "MLO.dcm").exists():
                    mlo_path = str(p_dir / "MLO.dcm")

        if not cc_path and not mlo_path:
            continue

        age_val = np.nan
        if age_col and not group[age_col].dropna().empty:
            try:
                age_val = float(group[age_col].dropna().iloc[0])
            except Exception:
                age_val = np.nan

        label_val = int(group["label"].max())
        patients.append({
            "patient_id": str(pid),
            "cc_path": cc_path,
            "mlo_path": mlo_path,
            "age": age_val,
            "label": label_val,
            "dataset_source": "EMBED",
        })

    if not patients:
        raise RuntimeError(f"No valid EMBED cases resolved in {root}")

    res_df = pd.DataFrame(patients)

    def safe_stratify(labels):
        if labels is None or len(labels) == 0:
            return None
        counts = pd.Series(labels).value_counts()
        if len(counts) > 1 and counts.min() >= 2:
            return labels
        return None

    train_idx, temp_idx = train_test_split(res_df.index, test_size=0.3, stratify=safe_stratify(res_df["label"]), random_state=seed)
    val_idx, test_idx = train_test_split(temp_idx, test_size=0.5, stratify=safe_stratify(res_df.loc[temp_idx, "label"]), random_state=seed)

    res_df["split"] = "train"
    res_df.loc[val_idx, "split"] = "val"
    res_df.loc[test_idx, "split"] = "test"

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(output_csv, index=False)
    print(f"EMBED index generated: {len(res_df)} patients -> {output_csv}")


def main():
    ap = argparse.ArgumentParser(description="Build EMBED patient index.")
    ap.add_argument("--raw-dir", default="backend/data/raw/EMBED", help="EMBED raw root")
    ap.add_argument("--output", default="backend/data/processed/embed_index.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    parse_embed(Path(args.raw_dir).resolve(), Path(args.output).resolve(), args.seed)


if __name__ == "__main__":
    main()
