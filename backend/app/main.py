from __future__ import annotations

import logging
import sys
from pathlib import Path

# Ensure `backend/` is importable so `src.*` modules resolve regardless of
# whether uvicorn is launched from the repo root or the `backend/` directory.
BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.config import AppConfig
from src.service import ModelService

from .routes import config as config_router
from .routes import explain, health, metrics, predict, training

logger = logging.getLogger("carexai")
logging.basicConfig(level=logging.INFO)


def create_app() -> FastAPI:
    config = AppConfig.load()
    app = FastAPI(
        title="CARE-XAI API",
        version=config.api_version,
        description=(
            "Confidence-Aware Robust Explainable Multimodal AI for Mammography "
            "and Clinical Fusion."
        ),
    )
    app.state.config = config
    app.state.service = ModelService(config)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        response = await call_next(request)
        logger.info("=> %s %s %s", request.method, request.url.path, response.status_code)
        return response

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error for %s %s: %s", request.method, request.url.path, exc)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "error": str(exc)},
        )

    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(config_router.router, prefix=api_prefix)
    app.include_router(predict.router, prefix=api_prefix)
    app.include_router(explain.router, prefix=api_prefix)
    app.include_router(metrics.router, prefix=api_prefix)
    app.include_router(training.router, prefix=api_prefix)

    return app


app = create_app()
