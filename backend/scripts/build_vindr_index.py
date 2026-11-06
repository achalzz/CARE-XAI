"""Build study/patient-level dual-view index for VinDr-Mammo (PhysioNet)."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def parse_vindr(root: Path, output_csv: Path, seed: int = 42):
    csv_candidates = list(root.glob("*breast-level*.csv")) + list(root.glob("*.csv"))
    if not csv_candidates:
        raise FileNotFoundError(f"No annotations CSV found in {root}")

    df = pd.read_csv(csv_candidates[0])
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

    study_col = next((c for c in df.columns if "study" in c), None)
    img_col = next((c for c in df.columns if "image" in c), None)
    view_col = next((c for c in df.columns if "view" in c), None)
    birads_col = next((c for c in df.columns if "birad" in c or "rad" in c), None)
    split_col = next((c for c in df.columns if "split" in c), None)

    if not study_col or not img_col or not view_col:
        raise RuntimeError(f"Required columns missing in {csv_candidates[0]}. Found: {list(df.columns)}")

    def map_birads(v):
        s = str(v).upper()
        if "BI-RADS 1" in s or "BI-RADS 2" in s or "BI-RADS 3" in s:
            return 0
        if "BI-RADS 4" in s or "BI-RADS 5" in s or "BI-RADS 6" in s:
            return 1
        return np.nan

    if birads_col:
        df["label"] = df[birads_col].apply(map_birads)
    else:
        df["label"] = 0

    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)

    # Search for all DICOM files
    dicom_map = {}
    for dcm in root.rglob("*.dcm"):
        dicom_map[dcm.stem.lower()] = str(dcm)

    patients = []
    for sid, group in df.groupby(study_col):
        cc_row = group[group[view_col].astype(str).str.upper().str.contains("CC")]
        mlo_row = group[group[view_col].astype(str).str.upper().str.contains("MLO")]

        cc_path, mlo_path = "", ""
        if not cc_row.empty:
            img_id = str(cc_row.iloc[0][img_col]).strip().lower()
            cc_path = dicom_map.get(img_id, "")
        if not mlo_row.empty:
            img_id = str(mlo_row.iloc[0][img_col]).strip().lower()
            mlo_path = dicom_map.get(img_id, "")

        if not cc_path and not mlo_path:
            continue

        label_val = int(group["label"].max())
        orig_split = str(group[split_col].iloc[0]).lower() if split_col and not group[split_col].empty else ""

        patients.append({
            "patient_id": str(sid),
            "cc_path": cc_path,
            "mlo_path": mlo_path,
            "age": np.nan,  # VinDr does not always report age per study
            "label": label_val,
            "orig_split": orig_split,
            "dataset_source": "VinDr-Mammo",
        })

    if not patients:
        raise RuntimeError(f"No valid VinDr studies found in {root}")

    res_df = pd.DataFrame(patients)

    # Assign splits
    if any(res_df["orig_split"].str.contains("train")) and any(res_df["orig_split"].str.contains("test")):
        res_df["split"] = res_df["orig_split"].apply(lambda s: "test" if "test" in s else "train")
        # carve out 15% val from train
        train_mask = res_df["split"] == "train"
        train_indices = res_df[train_mask].index
        t_idx, v_idx = train_test_split(train_indices, test_size=0.15, random_state=seed)
        res_df.loc[v_idx, "split"] = "val"
    else:
        train_idx, temp_idx = train_test_split(res_df.index, test_size=0.3, stratify=res_df["label"] if res_df["label"].nunique() > 1 else None, random_state=seed)
        val_idx, test_idx = train_test_split(temp_idx, test_size=0.5, stratify=res_df.loc[temp_idx, "label"] if res_df.loc[temp_idx, "label"].nunique() > 1 else None, random_state=seed)
        res_df["split"] = "train"
        res_df.loc[val_idx, "split"] = "val"
        res_df.loc[test_idx, "split"] = "test"

    res_df = res_df.drop(columns=["orig_split"])
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    res_df.to_csv(output_csv, index=False)
    print(f"VinDr-Mammo index generated: {len(res_df)} cases -> {output_csv}")


def main():
    ap = argparse.ArgumentParser(description="Build VinDr-Mammo index.")
    ap.add_argument("--raw-dir", default="backend/data/raw/VinDr-Mammo", help="VinDr raw root")
    ap.add_argument("--output", default="backend/data/processed/vindr_index.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    parse_vindr(Path(args.raw_dir).resolve(), Path(args.output).resolve(), args.seed)


if __name__ == "__main__":
    main()
