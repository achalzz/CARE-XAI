from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Add backend directory to sys.path if not present
BACKEND_DIR = Path(__file__).resolve().parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import roc_auc_score
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from tqdm import tqdm

from src.data import CMMDDualViewDataset
from src.metrics import best_youden_threshold, compute_metrics
from src.model import CAREXAI
from src.utils import save_json, set_seed


def make_loader(ds, batch_size, num_workers, shuffle):
    return DataLoader(ds, batch_size=batch_size, shuffle=shuffle, num_workers=num_workers,
                      pin_memory=torch.cuda.is_available(), persistent_workers=num_workers > 0)


def run_epoch(model, loader, criterion, device, optimizer=None, scaler=None):
    train = optimizer is not None
    model.train(train)
    ys, ps, losses = [], [], []
    for batch in tqdm(loader, leave=False):
        images = batch["images"].to(device, non_blocking=True)
        image_mask = batch["image_mask"].to(device, non_blocking=True)
        clinical = batch["clinical"].to(device, non_blocking=True)
        clinical_mask = batch["clinical_mask"].to(device, non_blocking=True)
        y = batch["label"].to(device, non_blocking=True)

        if train:
            optimizer.zero_grad(set_to_none=True)
        with autocast(enabled=device.type == "cuda"):
            out = model(images, image_mask, clinical, clinical_mask)
            loss = criterion(out["logits"], y)
        if train:
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            scaler.step(optimizer)
            scaler.update()
        losses.append(float(loss.detach().cpu()))
        ys.append(y.detach().cpu().numpy())
        ps.append(out["prob"].detach().cpu().numpy())
    return float(np.mean(losses)), np.concatenate(ys), np.concatenate(ps)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default="backend/data/processed/cmmd1_index.csv")
    ap.add_argument("--epochs", type=int, default=20)
    ap.add_argument("--batch-size", type=int, default=4)
    ap.add_argument("--num-workers", type=int, default=2)
    ap.add_argument("--image-size", type=int, default=384)
    ap.add_argument("--lr", type=float, default=8e-5)
    ap.add_argument("--backbone", default="tf_efficientnetv2_s.in21k_ft_in1k")
    ap.add_argument("--out", default="backend/checkpoints/care_xai_best.pt")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--patience", type=int, default=5)
    args = ap.parse_args()

    index_path = Path(args.index)
    if not index_path.exists():
        alt_index = BACKEND_DIR / "data" / "processed" / "cmmd1_index.csv"
        if alt_index.exists():
            index_path = alt_index
        else:
            raise FileNotFoundError(f"Index file {args.index} not found. Run scripts/build_index.py first.")

    set_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print("Device:", device)

    index = pd.read_csv(index_path)
    train_df = index[index.split == "train"]
    age_mean = pd.to_numeric(train_df.age, errors="coerce").mean()
    age_std = pd.to_numeric(train_df.age, errors="coerce").std()
    pos = max(int(train_df.label.sum()), 1)
    neg = max(len(train_df) - pos, 1)
    pos_weight = torch.tensor([neg / pos], dtype=torch.float32, device=device)

    train_ds = CMMDDualViewDataset(index_path, "train", args.image_size, True, age_mean=age_mean, age_std=age_std)
    val_ds = CMMDDualViewDataset(index_path, "val", args.image_size, False, age_mean=age_mean, age_std=age_std)
    test_ds = CMMDDualViewDataset(index_path, "test", args.image_size, False, age_mean=age_mean, age_std=age_std)
    train_loader = make_loader(train_ds, args.batch_size, args.num_workers, True)
    val_loader = make_loader(val_ds, args.batch_size, args.num_workers, False)
    test_loader = make_loader(test_ds, args.batch_size, args.num_workers, False)

    model = CAREXAI(backbone=args.backbone).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=args.epochs)
    scaler = GradScaler(enabled=device.type == "cuda")

    best_auc = -np.inf
    wait = 0
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        train_loss, _, _ = run_epoch(model, train_loader, criterion, device, optimizer, scaler)
        with torch.no_grad():
            val_loss, yv, pv = run_epoch(model, val_loader, criterion, device)
        val_auc = roc_auc_score(yv, pv) if len(np.unique(yv)) > 1 else 0.0
        print(f"Epoch {epoch:02d} | train_loss={train_loss:.4f} | val_loss={val_loss:.4f} | val_auc={val_auc:.4f}")
        scheduler.step()
        if val_auc > best_auc + 1e-4:
            best_auc = val_auc
            wait = 0
            torch.save({
                "model": model.state_dict(),
                "backbone": args.backbone,
                "image_size": args.image_size,
                "age_mean": float(age_mean), "age_std": float(age_std),
            }, out_path)
        else:
            wait += 1
            if wait >= args.patience:
                print("Early stopping.")
                break

    ckpt = torch.load(out_path, map_location=device)
    model.load_state_dict(ckpt["model"])
    with torch.no_grad():
        _, yv, pv = run_epoch(model, val_loader, criterion, device)
        _, yt, pt = run_epoch(model, test_loader, criterion, device)
    threshold = best_youden_threshold(yv, pv)
    val_metrics = compute_metrics(yv, pv, threshold)
    test_metrics = compute_metrics(yt, pt, threshold)
    report = {
        "device": str(device),
        "checkpoint": str(out_path),
        "age_mean": float(age_mean), "age_std": float(age_std),
        "val": val_metrics, "test": test_metrics,
    }
    metrics_out = BACKEND_DIR / "outputs" / "metrics.json"
    save_json(report, metrics_out)
    print("Validation:", val_metrics)
    print("Test:", test_metrics)


if __name__ == "__main__":
    main()
