from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
import torch
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

from .preprocess import load_dicom, standardize_orientation, to_pil


CLINICAL_FEATURES = ["age"]


def _identity(x):
    return x


class CMMDDualViewDataset(Dataset):
    """Patient-level dataset for CMMD1.

    Expected index columns:
      patient_id, cc_path, mlo_path, age, label, split
    Missing CC/MLO/age are allowed and represented by modality masks.
    """

    def __init__(
        self,
        index_csv: str | Path,
        split: str,
        image_size: int = 384,
        train: bool = False,
        clinical_missing_prob: float = 0.0,
        image_missing_prob: float = 0.0,
        age_mean: float = 45.92,
        age_std: float = 11.5,
    ) -> None:
        df = pd.read_csv(index_csv)
        df = df[df["split"].astype(str).str.lower() == split.lower()].reset_index(drop=True)
        if df.empty:
            raise ValueError(f"No rows found for split={split} in {index_csv}")
        self.df = df
        self.image_size = image_size
        self.train = train
        self.clinical_missing_prob = clinical_missing_prob if train else 0.0
        self.image_missing_prob = image_missing_prob if train else 0.0
        self.age_mean = float(age_mean)
        self.age_std = max(float(age_std), 1e-6)

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(p=0.0),
            transforms.RandomAffine(degrees=4, translate=(0.02, 0.02), scale=(0.96, 1.04)) if train else transforms.Lambda(_identity),
            transforms.ColorJitter(brightness=0.08, contrast=0.12) if train else transforms.Lambda(_identity),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.485, 0.485], std=[0.229, 0.229, 0.229]),
        ])

    def __len__(self) -> int:
        return len(self.df)

    def _load_view(self, path_value: str | float) -> Optional[torch.Tensor]:
        if not isinstance(path_value, str) or not path_value or path_value.lower() == "nan":
            return None
        path = Path(path_value)
        if not path.exists():
            return None
        try:
            arr, meta = load_dicom(path)
            arr = standardize_orientation(arr, meta.get("laterality", ""))
            img = to_pil(arr, self.image_size)
            return self.transform(img)
        except Exception:
            return None

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor | str]:
        row = self.df.iloc[idx]

        cc = self._load_view(row.get("cc_path", ""))
        mlo = self._load_view(row.get("mlo_path", ""))
        image_missing = self.train and np.random.rand() < self.image_missing_prob
        if image_missing:
            cc, mlo = None, None

        zero_image = torch.zeros(3, self.image_size, self.image_size, dtype=torch.float32)
        images = torch.stack([
            cc if cc is not None else zero_image,
            mlo if mlo is not None else zero_image,
        ])
        image_mask = torch.tensor([
            1.0 if cc is not None else 0.0,
            1.0 if mlo is not None else 0.0,
        ], dtype=torch.float32)

        age = row.get("age", np.nan)
        age_valid = 1.0 if pd.notna(age) else 0.0
        age_value = float(age) if pd.notna(age) else 0.0
        age_value = (age_value - self.age_mean) / self.age_std
        if self.train and np.random.rand() < self.clinical_missing_prob:
            age_value = 0.0
            age_valid = 0.0

        clinical = torch.tensor([age_value], dtype=torch.float32)
        clinical_mask = torch.tensor([age_valid], dtype=torch.float32)
        label = torch.tensor(float(row["label"]), dtype=torch.float32)
        dataset_source = str(row.get("dataset_source", "CMMD"))

        return {
            "images": images,
            "image_mask": image_mask,
            "clinical": clinical,
            "clinical_mask": clinical_mask,
            "label": label,
            "patient_id": str(row["patient_id"]),
            "dataset_source": dataset_source,
        }


# Alias for multi-center and general dataset usage
MultimodalDualViewDataset = CMMDDualViewDataset
