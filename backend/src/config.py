from __future__ import annotations

import os
from pathlib import Path
from typing import List

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Centralised, environment-aware application configuration.

    Values are resolved with the following precedence (highest first):
      1. `CAREXAI_*` environment variables
      2. `backend/config.yaml`
      3. hard-coded defaults below
    """

    # Training / data pipeline
    seed: int = 42
    image_size: int = 384
    batch_size: int = 4
    num_workers: int = 2
    epochs: int = 20
    lr: float = 0.00008
    weight_decay: float = 0.0001
    early_stopping_patience: int = 5

    # Uncertainty / robustness
    mc_samples: int = 15
    clinical_missing_prob: float = 0.20
    image_missing_prob: float = 0.05

    # Model
    backbone: str = "tf_efficientnetv2_s.in21k_ft_in1k"
    checkpoint_path: Path = Path("backend/checkpoints/care_xai_best.pt")
    age_mean: float = 45.92
    age_std: float = 11.5

    # Data
    index_csv: Path = Path("backend/data/processed/cmmd1_index.csv")
    data_split: str = "test"

    # API server
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ]
    )

    # Service metadata
    api_version: str = "1.0.0"
    app_name: str = "CARE-XAI"

    @classmethod
    def load(cls) -> "AppConfig":
        """Build configuration from YAML + environment overrides."""
        raw: dict = {}
        yaml_path = Path("backend/config.yaml")
        if yaml_path.exists():
            import yaml

            loaded = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
            if isinstance(loaded, dict):
                raw.update(loaded)

        # Environment overrides (`CAREXAI_<FIELD>`) take precedence over YAML.
        for field in cls.model_fields:
            env_key = "CAREXAI_" + field.upper()
            if env_key not in os.environ:
                continue
            value: object = os.environ[env_key]
            if field == "cors_origins":
                raw[field] = [v.strip() for v in value.split(",") if v.strip()]
            else:
                raw[field] = value

        return cls(**raw)
