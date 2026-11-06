from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request

from src.schemas import TrainingStartRequest, TrainingStatus
from src.training import TrainingJobManager

router = APIRouter(tags=["training"])


def _job(request: Request) -> TrainingJobManager:
    # Lazy initialise the job manager on the app state.
    if not hasattr(request.app.state, "training"):
        from src.config import AppConfig

        config: AppConfig = request.app.state.config
        request.app.state.training = TrainingJobManager(config)
    return request.app.state.training


@router.post("/training/start", response_model=TrainingStatus)
def start_training(
    payload: TrainingStartRequest,
    request: Request,
) -> TrainingStatus:
    manager = _job(request)
    overrides = {
        "epochs": payload.epochs,
        "batch_size": payload.batch_size,
        "image_size": payload.image_size,
        "lr": payload.lr,
    }
    result = manager.start(overrides)
    return TrainingStatus(**result)


@router.get("/training/status", response_model=TrainingStatus)
def training_status(request: Request) -> TrainingStatus:
    return TrainingStatus(**_job(request).status())
