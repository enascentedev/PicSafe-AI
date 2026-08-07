"""Contrato HTTP e comportamento integral da análise."""

from collections.abc import Callable
from pathlib import Path

from fastapi.testclient import TestClient

from picsafe_ai.api.main import create_app
from picsafe_ai.api.schemas import DetectorMetadata, DetectorMode
from picsafe_ai.config import DetectorBackend, Environment, Settings, StubScenario
from picsafe_ai.vision import DetectorError, StubVisionDetector


class SelectiveFailureDetector(StubVisionDetector):
    """Falha em uma imagem ou em todas para testar degradação segura."""

    def __init__(self, *, fail_all: bool) -> None:
        super().__init__(
            version="failure-test",
            confidence_threshold=0.5,
            scenario=StubScenario.EMPTY,
        )
        self._fail_all = fail_all
        self._calls = 0

    @property
    def metadata(self) -> DetectorMetadata:
        return DetectorMetadata(
            name="test-detector",
            version="1",
            mode=DetectorMode.REAL,
        )

    def predict(self, image_bytes: bytes, image_id: str) -> list:
        self._calls += 1
        if self._fail_all or self._calls == 1:
            message = "controlled detector failure"
            raise DetectorError(message)
        return super().predict(image_bytes, image_id)


def settings_for(base: Path) -> Settings:
    return Settings(
        environment=Environment.TEST,
        detector_backend=DetectorBackend.STUB,
        base_dir=base,
        reports_dir=base / "reports",
        temp_dir=base / "temp",
    )


def multipart(image: bytes, count: int = 4) -> list[tuple[str, tuple[str, bytes, str]]]:
    return [
        ("files", (f"photo-{index}.png", image, "image/png")) for index in range(count)
    ]


def test_health_discloses_simulated_detector(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    del image_factory
    client = TestClient(create_app(settings_for(temporary_base)))
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["detector"]["mode"] == "simulated"


def test_analysis_is_honest_and_escapes_report(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    client = TestClient(create_app(settings_for(temporary_base)))
    response = client.post(
        "/v1/analisar",
        files=multipart(image_factory()),
        data={"machine_id": "<script>alert(1)</script>"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_status"] == "complete"
    assert body["detector"]["mode"] == "simulated"
    assert {item["status"] for item in body["checklist"]} == {"DESCONHECIDO"}
    assert "&lt;script&gt;" in body["report_html"]
    assert "<script>alert(1)</script>" not in body["report_html"]
    assert list((temporary_base / "temp").iterdir()) == []
    assert len(list((temporary_base / "reports").iterdir())) == 5


def test_invalid_upload_is_atomic_422(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    client = TestClient(create_app(settings_for(temporary_base)))
    response = client.post(
        "/v1/analisar",
        files=multipart(image_factory(), count=3),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "invalid_image_count"
    assert list((temporary_base / "reports").iterdir()) == []


def test_detector_failure_produces_declared_partial_result(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    client = TestClient(
        create_app(
            settings_for(temporary_base),
            detector=SelectiveFailureDetector(fail_all=False),
        )
    )
    response = client.post("/v1/analisar", files=multipart(image_factory()))
    assert response.status_code == 200
    body = response.json()
    assert body["analysis_status"] == "partial"
    assert len(body["image_errors"]) == 1
    assert body["image_errors"][0]["code"] == "detector_error"


def test_total_detector_failure_returns_safe_503(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    client = TestClient(
        create_app(
            settings_for(temporary_base),
            detector=SelectiveFailureDetector(fail_all=True),
        )
    )
    response = client.post("/v1/analisar", files=multipart(image_factory()))
    assert response.status_code == 503
    assert response.json()["code"] == "analysis_unavailable"
    assert list((temporary_base / "temp").iterdir()) == []
    assert list((temporary_base / "reports").iterdir()) == []
