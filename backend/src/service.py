from __future__ import annotations

import base64
import io
import tempfile
from pathlib import Path
from typing import Optional

import numpy as np
import torch
from PIL import Image

from .config import AppConfig
from .model import CAREXAI
from .preprocess import load_dicom, standardize_orientation, to_pil
from .uncertainty import mc_predict
from .utils import load_json
from .xai import gradcam


class ModelService:
    """Encapsulates model lifecycle + inference for the REST API.

    The model is loaded lazily on first request so the API can boot even
    when no checkpoint is present (e.g. before training).
    """

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._model: Optional[CAREXAI] = None
        self._ckpt: Optional[dict] = None
        self._device: Optional[torch.device] = None

    # ------------------------------------------------------------------ #
    # Model lifecycle
    # ------------------------------------------------------------------ #
    @property
    def device(self) -> torch.device:
        if self._device is None:
            self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return self._device

    @property
    def checkpoint_exists(self) -> bool:
        return Path(self.config.checkpoint_path).exists()

    def load(self) -> None:
        if self._model is not None:
            return
        ckpt_path = Path(self.config.checkpoint_path)
        if not ckpt_path.exists():
            raise FileNotFoundError(
                f"Checkpoint not found at `{ckpt_path}`. Run `python backend/train.py` first."
            )
        ckpt = torch.load(ckpt_path, map_location=self.device)
        model = CAREXAI(backbone=ckpt.get("backbone", self.config.backbone)).to(self.device)
        model.load_state_dict(ckpt["model"])
        model.eval()
        self._model = model
        self._ckpt = ckpt
        self.config.age_mean = float(ckpt.get("age_mean", self.config.age_mean))
        self.config.age_std = float(ckpt.get("age_std", self.config.age_std))

    def status(self) -> dict:
        return {
            "model_loaded": self._model is not None,
            "device": str(self.device),
            "checkpoint_exists": self.checkpoint_exists,
            "checkpoint_path": str(self.config.checkpoint_path),
            "backbone": (
                self._ckpt.get("backbone", self.config.backbone)
                if self._ckpt
                else self.config.backbone
            ),
            "image_size": self.config.image_size,
            "age_mean": self.config.age_mean,
            "age_std": self.config.age_std,
        }

    # ------------------------------------------------------------------ #
    # Inference helpers
    # ------------------------------------------------------------------ #
    def _build_batch(
        self,
        image_tensor: torch.Tensor,
        age: float,
        image_available: bool = True,
        clinical_available: bool = True,
    ) -> dict:
        age_norm = (
            (float(age) - self.config.age_mean) / max(self.config.age_std, 1e-6)
            if clinical_available
            else 0.0
        )
        zero = torch.zeros_like(image_tensor)
        images = torch.stack([image_tensor, zero], dim=0).unsqueeze(0).to(self.device)
        image_mask = torch.tensor(
            [[1.0, 0.0]] if image_available else [[0.0, 0.0]],
            dtype=torch.float32,
            device=self.device,
        )
        clinical = torch.tensor([[age_norm]], dtype=torch.float32, device=self.device)
        clinical_mask = torch.tensor(
            [[1.0]] if clinical_available else [[0.0]],
            dtype=torch.float32,
            device=self.device,
        )
        return {
            "images": images,
            "image_mask": image_mask,
            "clinical": clinical,
            "clinical_mask": clinical_mask,
        }

    def _tensorize(self, pil_img: Image.Image) -> torch.Tensor:
        import torchvision.transforms as T

        t = T.Compose(
            [
                T.Resize((self.config.image_size, self.config.image_size)),
                T.ToTensor(),
                T.Normalize([0.485] * 3, [0.229] * 3),
            ]
        )
        return t(pil_img)

    def _process_upload(self, data: bytes, filename: str):
        suffix = Path(filename).suffix.lower()
        meta = {"view_position": "UPLOAD", "laterality": ""}
        if suffix in {".dcm", ".dicom"}:
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                f.write(data)
                tmp = Path(f.name)
            try:
                arr, meta = load_dicom(tmp)
                arr = standardize_orientation(arr, meta.get("laterality", ""))
                pil = to_pil(arr, self.config.image_size)
            finally:
                tmp.unlink(missing_ok=True)
        else:
            pil = (
                Image.open(io.BytesIO(data))
                .convert("RGB")
                .resize((self.config.image_size, self.config.image_size))
            )
        return pil, meta

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    def predict(
        self,
        image_bytes: bytes,
        filename: str,
        age: float,
        mc_samples: Optional[int] = None,
    ) -> dict:
        """Run multimodal MC-dropout prediction plus counterfactual ablation."""
        self.load()
        samples = mc_samples or self.config.mc_samples
        pil, meta = self._process_upload(image_bytes, filename)
        image_tensor = self._tensorize(pil).to(self.device)
        batch = self._build_batch(image_tensor, age)

        mean_p, variance, entropy = mc_predict(self._model, batch, self.device, samples=samples)
        p = float(mean_p[0])
        std = float(torch.sqrt(variance[0]))
        ent = float(entropy[0])
        label = "MALIGNANT" if p >= 0.5 else "BENIGN"
        high_unc = std >= 0.10 or ent >= 0.65

        with torch.no_grad():
            img_batch = self._build_batch(image_tensor, age, True, False)
            clin_batch = self._build_batch(image_tensor, age, False, True)
            p_img = float(self._model(**img_batch)["prob"][0])
            p_clin = float(self._model(**clin_batch)["prob"][0])
            weights = self._model(**batch)["fusion_weights"][0].detach().cpu().numpy()

        return {
            "probability": p,
            "label": label,
            "uncertainty_std": std,
            "entropy": ent,
            "high_uncertainty": high_unc,
            "counterfactual": {
                "image_only_probability": p_img,
                "clinical_only_probability": p_clin,
                "image_weight": float(weights[0]),
                "clinical_weight": float(weights[1]),
            },
            "risk_note": (
                "High model predictive uncertainty. Recommend clinical expert review."
                if high_unc
                else "Confidence score within standard thresholds."
            ),
            "view": meta.get("view_position"),
            "laterality": meta.get("laterality"),
            "mc_samples": samples,
        }

    def grad_cam(
        self,
        image_bytes: bytes,
        filename: str,
        age: float,
        mc_samples: Optional[int] = None,
    ) -> dict:
        """Generate Grad-CAM++ heatmap overlay, returned as base64-encoded PNG."""
        self.load()
        pil, _ = self._process_upload(image_bytes, filename)
        image_tensor = self._tensorize(pil).to(self.device)
        batch = self._build_batch(image_tensor, age)
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "gradcam.png"
            gradcam(
                self._model,
                image_tensor,
                batch["image_mask"][0],
                batch["clinical"][0],
                batch["clinical_mask"][0],
                out,
            )
            b64 = base64.b64encode(out.read_bytes()).decode("ascii")
        return {"gradcam_base64": b64, "gradcam_mime": "image/png"}

    def metrics(self) -> dict:
        """Return persisted evaluation metrics, or an empty dict if absent."""
        path = Path("backend/outputs/metrics.json")
        if path.exists():
            return load_json(path)
        return {}
