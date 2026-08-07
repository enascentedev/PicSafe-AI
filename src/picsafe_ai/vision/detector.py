"""Contrato de detector e implementação simulada explícita."""

from io import BytesIO
from typing import Protocol, runtime_checkable

from PIL import Image, UnidentifiedImageError

from picsafe_ai.api.schemas import (
    BoundingBox,
    Detection,
    DetectionClass,
    DetectorMetadata,
    DetectorMode,
)
from picsafe_ai.config import DetectorBackend, Environment, Settings, StubScenario


class DetectorError(RuntimeError):
    """Falha acionável durante uma inferência."""


class DetectorConfigurationError(RuntimeError):
    """Configuração incapaz de fornecer um detector seguro."""


@runtime_checkable
class VisionDetector(Protocol):
    """Interface substituível para detectores visuais."""

    @property
    def metadata(self) -> DetectorMetadata:
        """Descreve o detector sem expor configuração sensível."""
        ...

    def predict(self, image_bytes: bytes, image_id: str) -> list[Detection]:
        """Retorna detecções ou levanta ``DetectorError``."""
        ...


class StubVisionDetector:
    """Detector determinístico e explicitamente simulado para dev/test."""

    def __init__(
        self,
        *,
        version: str,
        confidence_threshold: float,
        scenario: StubScenario,
    ) -> None:
        self._confidence_threshold = confidence_threshold
        self._scenario = scenario
        self._metadata = DetectorMetadata(
            name="stub-vision-detector",
            version=version,
            mode=DetectorMode.SIMULATED,
            configuration={
                "scenario": scenario.value,
                "confidence_threshold": str(confidence_threshold),
            },
        )

    @property
    def metadata(self) -> DetectorMetadata:
        """Metadados que impedem confundir o stub com modelo real."""
        return self._metadata

    def predict(self, image_bytes: bytes, image_id: str) -> list[Detection]:
        """Valida a imagem e produz um cenário simulado controlado."""
        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image.verify()
        except (OSError, UnidentifiedImageError) as exc:
            message = "O detector recebeu conteúdo que não é uma imagem válida"
            raise DetectorError(message) from exc

        if self._scenario is StubScenario.EMPTY:
            return []
        return [
            self._detection(
                DetectionClass.EMERGENCY_STOP,
                confidence=0.85,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_id=image_id,
            ),
            self._detection(
                DetectionClass.GUARD,
                confidence=0.78,
                bbox=BoundingBox(x_min=0.35, y_min=0.2, x_max=0.8, y_max=0.7),
                image_id=image_id,
            ),
        ]

    def _detection(
        self,
        class_name: DetectionClass,
        *,
        confidence: float,
        bbox: BoundingBox,
        image_id: str,
    ) -> Detection:
        confidence = max(confidence, self._confidence_threshold)
        return Detection(
            class_name=class_name,
            confidence=confidence,
            bbox=bbox,
            image_id=image_id,
            image_path=image_id,
        )


def build_detector(app_settings: Settings) -> VisionDetector:
    """Constrói somente um detector permitido no ambiente atual."""
    backend = app_settings.detector_backend
    if backend is DetectorBackend.DISABLED:
        message = "Defina DETECTOR_BACKEND explicitamente antes de iniciar a API"
        raise DetectorConfigurationError(message)
    if backend is DetectorBackend.REAL:
        message = "Nenhum detector real foi integrado nesta PoC"
        raise DetectorConfigurationError(message)
    if app_settings.environment not in {Environment.DEVELOPMENT, Environment.TEST}:
        message = "O detector stub só pode ser usado em development ou test"
        raise DetectorConfigurationError(message)
    return StubVisionDetector(
        version=app_settings.model_version,
        confidence_threshold=app_settings.confidence_threshold,
        scenario=app_settings.stub_scenario,
    )
