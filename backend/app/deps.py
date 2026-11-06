from __future__ import annotations

from fastapi import Request

from src.config import AppConfig
from src.service import ModelService


def get_config(request: Request) -> AppConfig:
    return request.app.state.config


def get_service(request: Request) -> ModelService:
    return request.app.state.service
