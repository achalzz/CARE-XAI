from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score, average_precision_score, balanced_accuracy_score,
    brier_score_loss, confusion_matrix, f1_score, precision_score,
    recall_score, roc_auc_score, roc_curve
)


def best_youden_threshold(y_true, y_prob) -> float:
    y_true = np.asarray(y_true)
    if len(np.unique(y_true)) < 2:
        return 0.5
    try:
        fpr, tpr, thresholds = roc_curve(y_true, y_prob)
        j = tpr - fpr
        if not np.any(np.isfinite(j)):
            return 0.5
        idx = int(np.nanargmax(j))
        t = thresholds[idx]
        if not np.isfinite(t):
            t = 0.5
        return float(np.clip(t, 0.05, 0.95))
    except Exception:
        return 0.5


def expected_calibration_error(y_true, y_prob, bins: int = 10) -> float:
    y_true = np.asarray(y_true)
    y_prob = np.asarray(y_prob)
    edges = np.linspace(0.0, 1.0, bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (y_prob >= lo) & (y_prob < hi if hi < 1 else y_prob <= hi)
        if not np.any(mask):
            continue
        conf = np.mean(y_prob[mask])
        acc = np.mean((y_prob[mask] >= 0.5) == y_true[mask])
        ece += np.mean(mask) * abs(acc - conf)
    return float(ece)


def compute_metrics(y_true, y_prob, threshold: float = 0.5) -> dict:
    y_true = np.asarray(y_true).astype(int)
    y_prob = np.asarray(y_prob)
    y_pred = (y_prob >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    specificity = tn / max(tn + fp, 1)
    out = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "sensitivity_recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "specificity": float(specificity),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "brier": float(brier_score_loss(y_true, y_prob)),
        "ece": expected_calibration_error(y_true, y_prob),
        "threshold": float(threshold),
    }
    if len(np.unique(y_true)) == 2:
        out["roc_auc"] = float(roc_auc_score(y_true, y_prob))
        out["pr_auc"] = float(average_precision_score(y_true, y_prob))
    else:
        out["roc_auc"] = float("nan")
        out["pr_auc"] = float("nan")
    return out
