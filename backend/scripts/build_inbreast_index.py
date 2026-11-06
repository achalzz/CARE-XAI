"""Build patient-level dual-view index for INbreast."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def parse_inbreast(root: Path, output_csv: Path, seed: int = 42):
    csv_candidates = list(root.glob("*.csv"))
    if not csv_candidates:
        raise FileNotFoundError(f"No INbreast CSV file found in {root}")

    df = pd.read_csv(csv_candidates[0], sep=None, engine="python")
    df.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in df.columns]

    pid_col = next((c for c in df.columns if "patient" in c and "id" in c), None)
    view_col = next((c for c in df.columns if "view" in c), None)
    file_col = next((c for c in df.columns if "file" in c or "name" in c), None)
    birads_col = next((c for c in df.columns if "rad" in c), None)
    age_col = next((c for c in df.columns if "age" in c), None)

    if not pid_col or not view_col:
        raise RuntimeError(f"Could not identify required columns in {csv_candidates[0]}. Columns: {list(df.columns)}")

    # Map BI-RADS to binary label: 1, 2, 3 -> 0; 4, 5, 6 -> 1
    def map_birads(v):
        try:
            val = float(str(v).replace("a", "").replace("b", "").replace("c", "").strip())
            if val in [1.0, 2.0, 3.0]:
                return 0
            if val >= 4.0:
                return 1
        except Exception:
            pass
        return np.nan

    if birads_col:
        df["label"] = df[birads_col].apply(map_birads)
    else:
        df["label"] = 0

    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)

    # Search for all DICOM files in root
    dicom_map = {}
    for dcm in root.rglob("*.dcm"):
        stem = dcm.stem.lower()
        dicom_map[stem] = str(dcm)

    patients = []
    for pid, group in df.groupby(pid_col):
        cc_row = group[group[view_col].astype(str).str.upper().str.contains("CC")]
        mlo_row = group[group[view_col].astype(str).str.upper().str.contains("MLO")]

        cc_path, mlo_path = "", ""
        if not cc_row.empty and file_col:
            fn = str(cc_row.iloc[0][file_col]).strip().lower()
            cc_path = dicom_map.get(fn, dicom_map.get(fn.replace(".dcm", ""), ""))
        if not mlo_row.empty and file_col:
            fn = str(mlo_row.iloc[0][file_col]).strip().lower()
            mlo_path = dicom_map.get(fn, dicom_map.get(fn.replace(".dcm", ""), ""))

        # Fallback search by patient ID in mapped filenames
        if not cc_path or not mlo_path:
            for stem, p in dicom_map.items():
                if str(pid).lower() in stem:
                    if "cc" in stem and not cc_path:
                        cc_path = p
                    elif "mlo" in stem and not mlo_path:
                        mlo_path = p

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
            "dataset_source": "INbreast",
        })

    if not patients:
        raise RuntimeError(f"No patient records matched with DICOMs in {root}")

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
    print(f"INbreast index generated: {len(res_df)} patients -> {output_csv}")


def main():
    ap = argparse.ArgumentParser(description="Build INbreast patient index.")
    ap.add_argument("--raw-dir", default="backend/data/raw/INbreast", help="INbreast raw root")
    ap.add_argument("--output", default="backend/data/processed/inbreast_index.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    parse_inbreast(Path(args.raw_dir).resolve(), Path(args.output).resolve(), args.seed)


if __name__ == "__main__":
    main()
