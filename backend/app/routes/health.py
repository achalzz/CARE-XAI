from __future__ import annotations

from fastapi import APIRouter, Depends

from src.config import AppConfig
from src.schemas import HealthResponse
from src.service import ModelService

from ..deps import get_config, get_service

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health_check(
    config: AppConfig = Depends(get_config),
    service: ModelService = Depends(get_service),
) -> HealthResponse:
    status = service.status()
    return HealthResponse(
        status="ok",
        model_loaded=status["model_loaded"],
        device=status["device"],
        checkpoint=str(config.checkpoint_path),
        backbone=status["backbone"],
        version=config.api_version,
    )
