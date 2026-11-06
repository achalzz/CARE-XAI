from __future__ import annotations

import torch
import torch.nn as nn


def enable_dropout(module):
    if isinstance(module, (nn.Dropout, nn.Dropout2d, nn.Dropout3d, nn.AlphaDropout)):
        module.train()


@torch.no_grad()
def mc_predict(model, batch, device, samples=15):
    """MC-dropout predictive distribution. Returns mean probability, variance and entropy."""
    model.eval()
    probs = []
    for _ in range(samples):
        model.apply(enable_dropout)
        out = model(
            batch["images"].to(device), batch["image_mask"].to(device),
            batch["clinical"].to(device), batch["clinical_mask"].to(device)
        )
        probs.append(out["prob"].detach().cpu())
    p = torch.stack(probs)
    mean = p.mean(0)
    var = p.var(0, unbiased=False)
    eps = 1e-6
    entropy = -(mean.clamp(eps, 1-eps) * mean.clamp(eps, 1-eps).log() +
                (1-mean).clamp(eps, 1-eps) * (1-mean).clamp(eps, 1-eps).log())
    return mean, var, entropy
