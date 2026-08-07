"""Schemas estáveis da API v1 do PicSafe AI."""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class DetectionClass(StrEnum):
    """Classes visuais reconhecidas pelo contrato da PoC."""

    EMERGENCY_STOP = "emergency_stop"
    GUARD = "guard"
    EXPOSED_MOVING_PART = "exposed_moving_part"
    DANGER_ZONE_OPENING = "danger_zone_opening"
    SAFETY_SIGN = "safety_sign"


class ChecklistStatus(StrEnum):
    """Estados conservadores do checklist."""

    OK = "OK"
    ATENCAO = "ATENÇÃO"
    DESCONHECIDO = "DESCONHECIDO"


class DetectorMode(StrEnum):
    """Origem real ou simulada das detecções."""

    REAL = "real"
    SIMULATED = "simulated"


class AnalysisStatus(StrEnum):
    """Resultado global do processamento."""

    COMPLETE = "complete"
    PARTIAL = "partial"


class BoundingBox(BaseModel):
    """Bounding box normalizada no intervalo de zero a um."""

    x_min: float = Field(ge=0.0, le=1.0)
    y_min: float = Field(ge=0.0, le=1.0)
    x_max: float = Field(ge=0.0, le=1.0)
    y_max: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def validate_coordinates(self) -> "BoundingBox":
        """Garante área positiva."""
        if self.x_min >= self.x_max or self.y_min >= self.y_max:
            message = "Bounding box precisa ter área positiva"
            raise ValueError(message)
        return self


class DetectorMetadata(BaseModel):
    """Metadados públicos e não sensíveis do detector."""

    name: str
    version: str
    mode: DetectorMode
    configuration: dict[str, str] = Field(default_factory=dict)


class Detection(BaseModel):
    """Detecção ligada a uma imagem opaca."""

    class_name: DetectionClass
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: BoundingBox
    image_id: str
    image_path: str = Field(description="Alias compatível contendo apenas image_id")


class EvidenceReference(BaseModel):
    """Rastreabilidade estruturada de uma evidência."""

    image_id: str
    bbox: BoundingBox
    detector_name: str
    detector_version: str
    detector_mode: DetectorMode
    confidence: float = Field(ge=0.0, le=1.0)


class ChecklistItem(BaseModel):
    """Item auditável do checklist de pré-avaliação."""

    rule_id: str
    description: str
    status: ChecklistStatus
    evidence: str | None = None
    evidence_refs: list[EvidenceReference] = Field(default_factory=list)
    notes: str | None = None


class PendingPhoto(BaseModel):
    """Evidência adicional solicitada ao operador."""

    description: str
    reason: str
    image_id: str | None = None


class ImageProcessingError(BaseModel):
    """Falha segura associada a uma imagem opaca."""

    image_id: str
    code: str
    message: str


class AnalysisRequest(BaseModel):
    """Metadados opcionais enviados junto às imagens."""

    machine_id: str | None = Field(default=None, max_length=80)
    notes: str | None = Field(default=None, max_length=500)


class AnalysisResponse(BaseModel):
    """Resposta aditiva da API v1."""

    analysis_id: str
    analysis_status: AnalysisStatus
    machine_id: str | None = None
    detections: list[Detection] = Field(default_factory=list)
    checklist: list[ChecklistItem] = Field(default_factory=list)
    pending_photos: list[PendingPhoto] = Field(default_factory=list)
    image_errors: list[ImageProcessingError] = Field(default_factory=list)
    detector: DetectorMetadata
    report_html: str
    model_version: str
    confidence_threshold: float
    thresholds: dict[str, float]
    analysis_timestamp: str
    processing_time_seconds: float


class HealthResponse(BaseModel):
    """Estado operacional sem afirmar capacidade de visão real."""

    status: str
    version: str
    detector: DetectorMetadata
    timestamp: str


class ApiError(BaseModel):
    """Erro público padronizado."""

    code: str
    message: str
    context: dict[str, Any] = Field(default_factory=dict)
