from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    model_loaded: bool = False
    device: str = "cpu"
    checkpoint: Optional[str] = None
    backbone: Optional[str] = None
    version: str = "1.0.0"


class ModelStatusResponse(BaseModel):
    model_loaded: bool
    device: str
    checkpoint_exists: bool
    checkpoint_path: str
    backbone: str
    image_size: int
    age_mean: float
    age_std: float


class ConfigResponse(BaseModel):
    image_size: int
    batch_size: int
    epochs: int
    lr: float
    mc_samples: int
    backbone: str
    checkpoint_path: str
    clinical_missing_prob: float
    image_missing_prob: float


class Counterfactual(BaseModel):
    image_only_probability: float
    clinical_only_probability: float
    image_weight: float
    clinical_weight: float


class Prediction(BaseModel):
    probability: float
    label: str
    uncertainty_std: float
    entropy: float
    high_uncertainty: bool
    counterfactual: Counterfactual
    risk_note: Optional[str] = None


class PredictResponse(BaseModel):
    prediction: Prediction
    patient_id: Optional[str] = None
    view: Optional[str] = None
    laterality: Optional[str] = None
    mc_samples: int


class ExplainResponse(BaseModel):
    prediction: Prediction
    gradcam_base64: Optional[str] = None
    gradcam_mime: Optional[str] = None


class TrainingStartRequest(BaseModel):
    epochs: Optional[int] = Field(default=None, ge=1, le=200)
    batch_size: Optional[int] = Field(default=None, ge=1, le=64)
    image_size: Optional[int] = Field(default=None, ge=128, le=512)
    lr: Optional[float] = Field(default=None, gt=0.0)


class TrainingStatus(BaseModel):
    state: str = "idle"
    pid: Optional[int] = None
    started_at: Optional[str] = None
    finished_at: Optional[str] = None
    message: Optional[str] = None
    logs: List[str] = []
