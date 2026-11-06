from __future__ import annotations

from fastapi import APIRouter, Depends

from src.config import AppConfig
from src.schemas import ConfigResponse, ModelStatusResponse
from src.service import ModelService

from ..deps import get_config, get_service

router = APIRouter(tags=["config"])


@router.get("/config", response_model=ConfigResponse)
def runtime_config(config: AppConfig = Depends(get_config)) -> ConfigResponse:
    return ConfigResponse(
        image_size=config.image_size,
        batch_size=config.batch_size,
        epochs=config.epochs,
        lr=config.lr,
        mc_samples=config.mc_samples,
        backbone=config.backbone,
        checkpoint_path=str(config.checkpoint_path),
        clinical_missing_prob=config.clinical_missing_prob,
        image_missing_prob=config.image_missing_prob,
    )


@router.get("/model/status", response_model=ModelStatusResponse)
def model_status(service: ModelService = Depends(get_service)) -> ModelStatusResponse:
    return ModelStatusResponse(**service.status())
