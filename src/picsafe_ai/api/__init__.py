"""Módulo da API FastAPI."""

from .main import app
from .schemas import (
    AnalysisRequest,
    AnalysisResponse,
    BoundingBox,
    ChecklistItem,
    ChecklistStatus,
    Detection,
    DetectionClass,
    PendingPhoto,
)

__all__ = [
    "app",
    "AnalysisRequest",
    "AnalysisResponse",
    "BoundingBox",
    "ChecklistItem",
    "ChecklistStatus",
    "Detection",
    "DetectionClass",
    "PendingPhoto",
]
