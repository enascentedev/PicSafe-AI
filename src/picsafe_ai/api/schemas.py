"""Schemas Pydantic para a API do PicSafe AI."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class DetectionClass(str, Enum):
    """Classes de detecção suportadas."""
    EMERGENCY_STOP = "emergency_stop"
    GUARD = "guard"
    EXPOSED_MOVING_PART = "exposed_moving_part"
    DANGER_ZONE_OPENING = "danger_zone_opening"
    SAFETY_SIGN = "safety_sign"


class ChecklistStatus(str, Enum):
    """Estados possíveis do checklist."""
    OK = "OK"
    ATENCAO = "ATENÇÃO"
    DESCONHECIDO = "DESCONHECIDO"


class BoundingBox(BaseModel):
    """Bounding box de uma detecção."""
    x_min: float = Field(..., ge=0.0, le=1.0, description="Coordenada X mínima normalizada (0-1)")
    y_min: float = Field(..., ge=0.0, le=1.0, description="Coordenada Y mínima normalizada (0-1)")
    x_max: float = Field(..., ge=0.0, le=1.0, description="Coordenada X máxima normalizada (0-1)")
    y_max: float = Field(..., ge=0.0, le=1.0, description="Coordenada Y máxima normalizada (0-1)")


class Detection(BaseModel):
    """Detecção de um objeto em uma imagem."""
    class_name: DetectionClass = Field(..., description="Classe detectada")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confiança da detecção (0-1)")
    bbox: BoundingBox = Field(..., description="Bounding box da detecção")
    image_path: str = Field(..., description="Caminho relativo da imagem")


class ChecklistItem(BaseModel):
    """Item do checklist de triagem."""
    rule_id: str = Field(..., description="ID da regra aplicada (ex: R-001)")
    description: str = Field(..., description="Descrição do item do checklist")
    status: ChecklistStatus = Field(..., description="Estado do item")
    evidence: Optional[str] = Field(None, description="Evidência associada (caminho da imagem + bbox)")
    notes: Optional[str] = Field(None, description="Notas adicionais")


class PendingPhoto(BaseModel):
    """Foto pendente solicitada."""
    description: str = Field(..., description="Descrição do que deve ser fotografado")
    reason: str = Field(..., description="Razão pela qual a foto é necessária")


class AnalysisRequest(BaseModel):
    """Requisição de análise de imagens."""
    machine_id: Optional[str] = Field(None, description="ID opcional da máquina analisada")
    notes: Optional[str] = Field(None, description="Notas adicionais sobre a análise")


class AnalysisResponse(BaseModel):
    """Resposta da análise completa."""
    machine_id: Optional[str] = Field(None, description="ID da máquina analisada")
    detections: List[Detection] = Field(default_factory=list, description="Lista de detecções encontradas")
    checklist: List[ChecklistItem] = Field(default_factory=list, description="Itens do checklist avaliados")
    pending_photos: List[PendingPhoto] = Field(default_factory=list, description="Fotos pendentes solicitadas")
    report_html: str = Field(..., description="Relatório em formato HTML")
    model_version: str = Field(..., description="Versão do modelo utilizado")
    confidence_threshold: float = Field(..., description="Threshold de confiança utilizado")
    analysis_timestamp: str = Field(..., description="Timestamp da análise (ISO 8601)")
    processing_time_seconds: float = Field(..., description="Tempo de processamento em segundos")
