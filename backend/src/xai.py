from __future__ import annotations

from pathlib import Path
import numpy as np
import torch
from PIL import Image
import shap
from pytorch_grad_cam import GradCAMPlusPlus
from pytorch_grad_cam.utils.model_targets import BinaryClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image


class ImageWrapper(torch.nn.Module):
    def __init__(self, model, clinical, clinical_mask, image_mask):
        super().__init__()
        self.model = model
        self.clinical = clinical
        self.clinical_mask = clinical_mask
        self.image_mask = image_mask

    def forward(self, x):
        b = x.shape[0]
        images = torch.stack([x, x], dim=1)
        image_mask = self.image_mask.expand(b, -1).clone()
        return self.model(images, image_mask, self.clinical.expand(b, -1), self.clinical_mask.expand(b, -1))["logits"].unsqueeze(1)


def gradcam(model, image_tensor, image_mask, clinical, clinical_mask, out_path: str | Path):
    device = image_tensor.device
    target_layer = model.image_encoder.conv_head if hasattr(model.image_encoder, "conv_head") else list(model.image_encoder.children())[-2]
    wrapper = ImageWrapper(model, clinical, clinical_mask, image_mask)
    wrapper.eval()
    cam = GradCAMPlusPlus(model=wrapper, target_layers=[target_layer])
    input_tensor = image_tensor.unsqueeze(0)
    grayscale = cam(input_tensor=input_tensor, targets=[BinaryClassifierOutputTarget(1)])[0]
    base = image_tensor.detach().cpu().numpy().transpose(1, 2, 0)
    base = (base - base.min()) / (base.max() - base.min() + 1e-8)
    overlay = show_cam_on_image(base.astype(np.float32), grayscale, use_rgb=True)
    Image.fromarray(overlay).save(out_path)


def clinical_shap(predict_fn, background: np.ndarray, sample: np.ndarray):
    """Small-feature SHAP. predict_fn must accept [N, d] and return positive-class probabilities."""
    explainer = shap.KernelExplainer(predict_fn, background)
    values = explainer.shap_values(sample, nsamples="auto")
    return values
