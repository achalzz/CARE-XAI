from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add backend directory to sys.path if not present
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import pandas as pd
import torch
from torch.utils.data import DataLoader

from src.data import CMMDDualViewDataset
from src.model import CAREXAI
from src.uncertainty import mc_predict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="backend/data/processed/cmmd1_index.csv")
    ap.add_argument("--checkpoint", default="backend/checkpoints/care_xai_best.pt")
    ap.add_argument("--patient-id", required=True)
    ap.add_argument("--mc-samples", type=int, default=15)
    args = ap.parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    ckpt_path = Path(args.checkpoint)
    if not ckpt_path.exists():
        alt_ckpt = BACKEND_DIR / "checkpoints" / "care_xai_best.pt"
        if alt_ckpt.exists():
            ckpt_path = alt_ckpt
        else:
            raise FileNotFoundError(f"Checkpoint not found at {args.checkpoint}. Train model first.")

    index_path = Path(args.index)
    if not index_path.exists():
        alt_index = BACKEND_DIR / "data" / "processed" / "cmmd1_index.csv"
        if alt_index.exists():
            index_path = alt_index
        else:
            raise FileNotFoundError(f"Index file not found at {args.index}.")

    ckpt = torch.load(ckpt_path, map_location=device)
    model = CAREXAI(backbone=ckpt["backbone"]).to(device)
    model.load_state_dict(ckpt["model"])

    ds = CMMDDualViewDataset(index_path, "test", ckpt.get("image_size", 384), False,
                             age_mean=ckpt.get("age_mean", 45.92), age_std=ckpt.get("age_std", 11.5))
    matches = [i for i in range(len(ds)) if str(ds.df.iloc[i].patient_id) == args.patient_id]
    if not matches:
        raise SystemExit("Patient not found in test split. For a demo, choose a test patient from the index.")
    batch = ds[matches[0]]
    batch = {k: (v.unsqueeze(0) if torch.is_tensor(v) else [v]) for k, v in batch.items()}
    mean, var, entropy = mc_predict(model, batch, device, args.mc_samples)
    p = float(mean[0])
    uncertainty = float((var[0] ** 0.5))
    ent = float(entropy[0])
    result = {
        "patient_id": args.patient_id,
        "malignant_probability": p,
        "predicted_class": "malignant" if p >= 0.5 else "benign",
        "mc_predictive_std": uncertainty,
        "predictive_entropy": ent,
        "safety_flag": "HIGH_UNCERTAINTY" if uncertainty >= 0.10 else "LOW_MODERATE_UNCERTAINTY",
        "clinical_input": {"age": float(ds.df.iloc[matches[0]].age) if pd.notna(ds.df.iloc[matches[0]].age) else None},
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
