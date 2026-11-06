from __future__ import annotations

from fastapi import APIRouter, Depends

from src.service import ModelService

from ..deps import get_service

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics(service: ModelService = Depends(get_service)) -> dict:
    return service.metrics()
