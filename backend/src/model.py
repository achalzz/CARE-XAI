from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
import timm


class ClinicalEncoder(nn.Module):
    def __init__(self, out_dim: int = 256):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(1, 64), nn.LayerNorm(64), nn.GELU(), nn.Dropout(0.20),
            nn.Linear(64, out_dim), nn.GELU(), nn.Dropout(0.20),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.net(x)


class AdaptiveFusion(nn.Module):
    """Patient-specific gating between image and clinical embeddings."""
    def __init__(self, dim: int = 256):
        super().__init__()
        self.gate = nn.Sequential(
            nn.Linear(dim * 2, dim), nn.GELU(), nn.Dropout(0.15), nn.Linear(dim, 2)
        )
        self.proj = nn.Sequential(nn.Linear(dim, dim), nn.LayerNorm(dim), nn.GELU(), nn.Dropout(0.20))

    def forward(self, image_feat, clinical_feat, image_available, clinical_available):
        pair = torch.cat([image_feat, clinical_feat], dim=-1)
        logits = self.gate(pair)
        availability = torch.stack([image_available, clinical_available], dim=-1)
        logits = logits.masked_fill(availability <= 0, -1e4)
        weights = torch.softmax(logits, dim=-1)
        fused = weights[:, 0:1] * image_feat + weights[:, 1:2] * clinical_feat
        none_available = availability.sum(dim=-1, keepdim=True) == 0
        fused = torch.where(none_available, torch.zeros_like(fused), fused)
        return self.proj(fused), weights


class CAREXAI(nn.Module):
    def __init__(self, backbone: str = "tf_efficientnetv2_s.in21k_ft_in1k", embed_dim: int = 256):
        super().__init__()
        self.image_encoder = timm.create_model(backbone, pretrained=True, num_classes=0, global_pool="avg")
        image_dim = self.image_encoder.num_features
        self.image_proj = nn.Sequential(
            nn.Linear(image_dim, embed_dim), nn.LayerNorm(embed_dim), nn.GELU(), nn.Dropout(0.25)
        )
        self.clinical_encoder = ClinicalEncoder(embed_dim)
        self.fusion = AdaptiveFusion(embed_dim)
        self.classifier = nn.Sequential(
            nn.Linear(embed_dim, 128), nn.GELU(), nn.Dropout(0.30), nn.Linear(128, 1)
        )
        self.image_missing_token = nn.Parameter(torch.zeros(1, embed_dim))
        self.clinical_missing_token = nn.Parameter(torch.zeros(1, embed_dim))

    def encode_images(self, images: torch.Tensor, image_mask: torch.Tensor) -> torch.Tensor:
        b, v, c, h, w = images.shape
        flat = images.view(b * v, c, h, w)
        feats = self.image_encoder(flat).view(b, v, -1)
        feats = self.image_proj(feats)
        vm = image_mask.unsqueeze(-1)
        denom = vm.sum(dim=1).clamp_min(1.0)
        feat = (feats * vm).sum(dim=1) / denom
        all_missing = image_mask.sum(dim=1, keepdim=True) == 0
        feat = torch.where(all_missing, self.image_missing_token.expand(b, -1), feat)
        return feat

    def forward(self, images, image_mask, clinical, clinical_mask, **kwargs):
        image_feat = self.encode_images(images, image_mask)
        clinical_feat = self.clinical_encoder(clinical)
        clinical_feat = torch.where(clinical_mask.sum(dim=1, keepdim=True) > 0,
                                    clinical_feat,
                                    self.clinical_missing_token.expand_as(clinical_feat))
        image_available = (image_mask.sum(dim=1) > 0).float()
        clinical_available = (clinical_mask.sum(dim=1) > 0).float()
        fused, weights = self.fusion(image_feat, clinical_feat, image_available, clinical_available)
        logits = self.classifier(fused).squeeze(-1)
        return {
            "logits": logits,
            "prob": torch.sigmoid(logits),
            "image_feat": image_feat,
            "clinical_feat": clinical_feat,
            "fused_feat": fused,
            "fusion_weights": weights,
        }
