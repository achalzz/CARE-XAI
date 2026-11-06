from __future__ import annotations

from pathlib import Path
from typing import Tuple

import numpy as np
import pydicom
from PIL import Image, ImageFilter


def load_dicom(path: str | Path) -> tuple[np.ndarray, dict]:
    ds = pydicom.dcmread(str(path), force=True)
    arr = ds.pixel_array.astype(np.float32)
    slope = float(getattr(ds, "RescaleSlope", 1.0))
    intercept = float(getattr(ds, "RescaleIntercept", 0.0))
    arr = arr * slope + intercept

    photometric = str(getattr(ds, "PhotometricInterpretation", ""))
    if photometric == "MONOCHROME1":
        arr = np.max(arr) - arr

    meta = {
        "patient_id": str(getattr(ds, "PatientID", "")).strip(),
        "view_position": str(getattr(ds, "ViewPosition", "")).upper().strip(),
        "laterality": str(getattr(ds, "ImageLaterality", "")).upper().strip(),
        "manufacturer": str(getattr(ds, "Manufacturer", "")).strip(),
        "image_id": str(getattr(ds, "SOPInstanceUID", path)),
    }
    return arr, meta


def robust_normalize(arr: np.ndarray) -> np.ndarray:
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    nonzero = arr[arr > 0]
    if nonzero.size < 32:
        lo, hi = np.min(arr), np.max(arr)
    else:
        lo, hi = np.percentile(nonzero, [1.0, 99.5])
    if hi <= lo:
        hi = lo + 1.0
    arr = np.clip(arr, lo, hi)
    arr = (arr - lo) / (hi - lo)
    return arr


def crop_foreground(arr: np.ndarray, margin: float = 0.02) -> np.ndarray:
    """Remove large black borders while keeping the breast region."""
    if arr.ndim != 2:
        raise ValueError(f"Expected 2D mammogram, got {arr.shape}")
    mask = arr > np.percentile(arr, 2.0)
    ys, xs = np.where(mask)
    if len(xs) < 100:
        return arr
    h, w = arr.shape
    dx, dy = int(w * margin), int(h * margin)
    x0, x1 = max(0, xs.min() - dx), min(w, xs.max() + dx + 1)
    y0, y1 = max(0, ys.min() - dy), min(h, ys.max() + dy + 1)
    return arr[y0:y1, x0:x1]


def standardize_orientation(arr: np.ndarray, laterality: str) -> np.ndarray:
    """Mirror right-breast images so both laterality classes share an orientation."""
    if laterality == "R":
        return np.fliplr(arr)
    return arr


def to_pil(arr: np.ndarray, size: int = 384) -> Image.Image:
    arr = robust_normalize(arr)
    arr = crop_foreground(arr)
    img = Image.fromarray((arr * 255).astype(np.uint8), mode="L")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    img = img.resize((size, size), Image.Resampling.BICUBIC)
    return img.convert("RGB")
