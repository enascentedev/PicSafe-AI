"""Configuração e contrato do detector."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from picsafe_ai.api.schemas import DetectorMode
from picsafe_ai.config import (
    DetectorBackend,
    Environment,
    Settings,
    StubScenario,
)
from picsafe_ai.vision import (
    DetectorConfigurationError,
    DetectorError,
    StubVisionDetector,
    build_detector,
)


def test_settings_create_directories(temporary_base: Path) -> None:
    app_settings = Settings(
        environment=Environment.TEST,
        detector_backend=DetectorBackend.STUB,
        base_dir=temporary_base,
    )
    app_settings.create_directories()
    assert app_settings.resolved_reports_dir.is_dir()
    assert app_settings.resolved_temp_dir.is_dir()


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"min_images": 5, "max_images": 4}, "MIN_IMAGES"),
        (
            {"max_file_size_bytes": 11, "max_request_size_bytes": 10},
            "MAX_FILE_SIZE_BYTES",
        ),
        (
            {
                "environment": Environment.PRODUCTION,
                "detector_backend": DetectorBackend.STUB,
            },
            "Produção exige",
        ),
    ],
)
def test_settings_reject_unsafe_combinations(
    values: dict[str, object],
    message: str,
) -> None:
    with pytest.raises(ValidationError, match=message):
        Settings(**values)


def test_detector_must_be_explicit() -> None:
    with pytest.raises(DetectorConfigurationError, match="explicitamente"):
        build_detector(Settings(detector_backend=DetectorBackend.DISABLED))


def test_real_detector_is_not_faked() -> None:
    app_settings = Settings(
        environment=Environment.PRODUCTION,
        detector_backend=DetectorBackend.REAL,
    )
    with pytest.raises(DetectorConfigurationError, match="Nenhum detector real"):
        build_detector(app_settings)


def test_stub_metadata_and_scenario(image_factory: object) -> None:
    make_image = image_factory
    assert callable(make_image)
    detector = StubVisionDetector(
        version="test-v1",
        confidence_threshold=0.9,
        scenario=StubScenario.SAMPLE,
    )
    detections = detector.predict(make_image(), "opaque")
    assert detector.metadata.mode is DetectorMode.SIMULATED
    assert len(detections) == 2
    assert all(item.confidence >= 0.9 for item in detections)
    assert all(item.image_path == "opaque" for item in detections)


def test_stub_rejects_invalid_content() -> None:
    detector = StubVisionDetector(
        version="test-v1",
        confidence_threshold=0.5,
        scenario=StubScenario.EMPTY,
    )
    with pytest.raises(DetectorError, match="imagem válida"):
        detector.predict(b"not-an-image", "opaque")
