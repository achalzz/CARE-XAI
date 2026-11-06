from __future__ import annotations

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from src.schemas import Counterfactual, ExplainResponse, Prediction
from src.service import ModelService

from ..deps import get_service

router = APIRouter(tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
async def explain(
    file: UploadFile = File(...),
    age: float = Form(..., ge=17, le=100),
    mc_samples: int = Form(15, ge=1, le=100),
    service: ModelService = Depends(get_service),
) -> ExplainResponse:
    try:
        data = await file.read()
        result = service.predict(data, file.filename or "upload.png", age, mc_samples)
        cam = service.grad_cam(data, file.filename or "upload.png", age, mc_samples)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    prediction = Prediction(
        probability=result["probability"],
        label=result["label"],
        uncertainty_std=result["uncertainty_std"],
        entropy=result["entropy"],
        high_uncertainty=result["high_uncertainty"],
        counterfactual=Counterfactual(**result["counterfactual"]),
        risk_note=result.get("risk_note"),
    )
    return ExplainResponse(
        prediction=prediction,
        gradcam_base64=cam["gradcam_base64"],
        gradcam_mime=cam["gradcam_mime"],
    )
