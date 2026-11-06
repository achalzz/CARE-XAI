"""Build patient-level dual-view index for CBIS-DDSM."""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


def find_files(root: Path, patterns: list[str]) -> list[Path]:
    matches = []
    for pat in patterns:
        matches.extend(root.glob(pat))
    return matches


def parse_cbis_ddsm(root: Path, output_csv: Path, seed: int = 42):
    csv_candidates = find_files(root, ["*case_description*.csv", "*train_set.csv", "*test_set.csv"])
    if not csv_candidates:
        raise FileNotFoundError(f"No CBIS-DDSM description CSV files found in {root}")

    dfs = []
    for p in csv_candidates:
        try:
            df = pd.read_csv(p)
            # Normalize column names
            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
            dfs.append(df)
        except Exception as e:
            print(f"Warning: Could not read {p}: {e}")

    if not dfs:
        raise RuntimeError(f"Could not load any valid CBIS metadata files in {root}")

    all_df = pd.concat(dfs, ignore_index=True).drop_duplicates()

    # Find relevant columns
    pid_col = next((c for c in all_df.columns if "patient_id" in c), None)
    view_col = next((c for c in all_df.columns if "view" in c), None)
    pathology_col = next((c for c in all_df.columns if "pathology" in c), None)
    path_col = next((c for c in all_df.columns if "image_file_path" in c or "path" in c), None)
    age_col = next((c for c in all_df.columns if "age" in c), None)

    if not pid_col or not view_col or not pathology_col:
        raise RuntimeError(f"Missing required columns in CBIS metadata. Found: {list(all_df.columns)}")

    # Map labels: MALIGNANT -> 1, BENIGN / BENIGN_WITHOUT_CALLBACK -> 0
    def map_label(val):
        s = str(val).upper().strip()
        if "MALIGNANT" in s:
            return 1
        if "BENIGN" in s:
            return 0
        return np.nan

    all_df["label"] = all_df[pathology_col].apply(map_label)
    all_df = all_df.dropna(subset=["label"]).copy()
    all_df["label"] = all_df["label"].astype(int)

    # Group by patient
    patients = []
    for pid, group in all_df.groupby(pid_col):
        cc_row = group[group[view_col].astype(str).str.upper().str.contains("CC")]
        mlo_row = group[group[view_col].astype(str).str.upper().str.contains("MLO")]

        cc_path, mlo_path = "", ""

        # Resolve paths: either from path_col or search directory tree
        if path_col and not cc_row.empty:
            raw_p = str(cc_row.iloc[0][path_col])
            cc_path = str(root / raw_p) if not Path(raw_p).is_absolute() else raw_p
        if path_col and not mlo_row.empty:
            raw_p = str(mlo_row.iloc[0][path_col])
            mlo_path = str(root / raw_p) if not Path(raw_p).is_absolute() else raw_p

        # Fallback direct search in patient directory
        p_dir = root / pid
        if p_dir.exists():
            for f in p_dir.glob("*.dcm"):
                fn = f.name.upper()
                if "CC" in fn and not cc_path:
                    cc_path = str(f)
                elif "MLO" in fn and not mlo_path:
                    mlo_path = str(f)

        if not cc_path and not mlo_path:
            continue

        age_val = np.nan
        if age_col and not group[age_col].dropna().empty:
            try:
                age_val = float(group[age_col].dropna().iloc[0])
            except Exception:
                age_val = np.nan

        # Label: if any case in group is malignant, consider malignant (1)
        label_val = int(group["label"].max())

        patients.append({
            "patient_id": str(pid),
            "cc_path": cc_path,
            "mlo_path": mlo_path,
            "age": age_val,
            "label": label_val,
            "dataset_source": "CBIS-DDSM",
        })

    if not patients:
        raise RuntimeError(f"No patients with paired DICOMs resolved in {root}")

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
    print(f"CBIS-DDSM index generated: {len(res_df)} patients -> {output_csv}")
    print(res_df["split"].value_counts().to_string())


def main():
    ap = argparse.ArgumentParser(description="Build CBIS-DDSM patient index.")
    ap.add_argument("--raw-dir", default="backend/data/raw/CBIS-DDSM", help="CBIS-DDSM raw root")
    ap.add_argument("--output", default="backend/data/processed/cbis_ddsm_index.csv")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()

    raw_dir = Path(args.raw_dir).resolve()
    out_file = Path(args.output).resolve()
    parse_cbis_ddsm(raw_dir, out_file, args.seed)


if __name__ == "__main__":
    main()
