"""Merge multiple processed cohort indices into a unified multi-center index.

Combines available indices from:
- CMMD
- CBIS-DDSM
- INbreast
- VinDr-Mammo
- EMBED

Enables joint training and cross-dataset validation.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import pandas as pd


STANDARD_COLUMNS = ["patient_id", "cc_path", "mlo_path", "age", "label", "split", "dataset_source"]


def load_and_standardize(path: Path, default_source: str) -> pd.DataFrame | None:
    if not path.exists():
        return None
    try:
        df = pd.read_csv(path)
        if "dataset_source" not in df.columns:
            df["dataset_source"] = default_source
        # Ensure all standard columns exist
        for c in STANDARD_COLUMNS:
            if c not in df.columns:
                df[c] = None
        return df[STANDARD_COLUMNS]
    except Exception as e:
        print(f"Warning: Failed to load {path}: {e}")
        return None


def main():
    ap = argparse.ArgumentParser(description="Merge processed cohort indices into a unified multi-center index.")
    ap.add_argument("--processed-dir", default="backend/data/processed", help="Processed data directory")
    ap.add_argument("--output", default="backend/data/processed/multicenter_index.csv", help="Combined output CSV")
    args = ap.parse_args()

    proc_dir = Path(args.processed_dir).resolve()
    out_path = Path(args.output).resolve()

    dataset_map = {
        proc_dir / "cmmd1_index.csv": "CMMD",
        proc_dir / "cbis_ddsm_index.csv": "CBIS-DDSM",
        proc_dir / "inbreast_index.csv": "INbreast",
        proc_dir / "vindr_index.csv": "VinDr-Mammo",
        proc_dir / "embed_index.csv": "EMBED",
    }

    dfs = []
    print("=== Scanning Available Dataset Indices ===")
    for path, source in dataset_map.items():
        sub_df = load_and_standardize(path, source)
        if sub_df is not None and not sub_df.empty:
            print(f"  [+] Found {source}: {len(sub_df)} cases ({path.name})")
            dfs.append(sub_df)
        else:
            print(f"  [-] Skipped {source}: {path.name} not found")

    if not dfs:
        raise RuntimeError("No processed dataset index files found to merge! Run individual build scripts first.")

    combined = pd.concat(dfs, ignore_index=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    combined.to_csv(out_path, index=False)

    print("\n=== Combined Multi-Center Index Summary ===")
    print(f"Total Cohort Size: {len(combined)} patient/study records")
    print(f"Destination: {out_path}\n")
    print("Distribution by Dataset & Split:")
    summary = pd.crosstab(combined["dataset_source"], combined["split"], margins=True)
    print(summary.to_string())
    print("\nMalignancy Prevalence by Dataset:")
    prev = combined.groupby("dataset_source")["label"].mean().apply(lambda x: f"{x*100:.1f}%")
    print(prev.to_string())


if __name__ == "__main__":
    main()
