"""Configuração validada do PicSafe AI."""

from enum import StrEnum
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def _default_cors_origins() -> list[str]:
    return ["http://localhost:3000", "http://127.0.0.1:3000"]


class Environment(StrEnum):
    """Ambientes suportados pela aplicação."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


class DetectorBackend(StrEnum):
    """Backends de detector reconhecidos pela configuração."""

    DISABLED = "disabled"
    STUB = "stub"
    REAL = "real"


class StubScenario(StrEnum):
    """Cenários determinísticos disponibilizados pelo stub."""

    EMPTY = "empty"
    SAMPLE = "sample"


class Settings(BaseSettings):
    """Configurações carregadas de ``config.env`` e do ambiente."""

    model_config = SettingsConfigDict(
        env_file="config.env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    environment: Environment = Environment.DEVELOPMENT
    api_host: str = "0.0.0.0"
    api_port: int = Field(default=8000, ge=1, le=65_535)
    cors_origins: list[str] = Field(default_factory=_default_cors_origins)

    detector_backend: DetectorBackend = DetectorBackend.DISABLED
    stub_scenario: StubScenario = StubScenario.EMPTY
    model_version: str = "stub-v1"
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    nms_threshold: float = Field(default=0.45, ge=0.0, le=1.0)

    min_images: int = Field(default=4, ge=1)
    max_images: int = Field(default=12, ge=1)
    max_file_size_bytes: int = Field(default=10 * 1024 * 1024, ge=1)
    max_request_size_bytes: int = Field(default=60 * 1024 * 1024, ge=1)
    max_image_pixels: int = Field(default=40_000_000, ge=1)
    image_retention_days: int = Field(default=30, ge=1)

    log_level: str = "INFO"
    base_dir: Path = Path(__file__).resolve().parents[2]
    reports_dir: Path | None = None
    temp_dir: Path | None = None

    @model_validator(mode="after")
    def validate_policy(self) -> "Settings":
        """Recusa combinações inseguras ou incoerentes."""
        if self.min_images > self.max_images:
            message = "MIN_IMAGES não pode ser maior que MAX_IMAGES"
            raise ValueError(message)
        if self.max_file_size_bytes > self.max_request_size_bytes:
            message = "MAX_FILE_SIZE_BYTES não pode exceder MAX_REQUEST_SIZE_BYTES"
            raise ValueError(message)
        if (
            self.environment is Environment.PRODUCTION
            and self.detector_backend is not DetectorBackend.REAL
        ):
            message = "Produção exige um detector real explicitamente configurado"
            raise ValueError(message)
        return self

    @property
    def resolved_reports_dir(self) -> Path:
        """Diretório persistente de relatórios."""
        return self.reports_dir or self.base_dir / "reports"

    @property
    def resolved_temp_dir(self) -> Path:
        """Diretório-base dos workspaces efêmeros."""
        return self.temp_dir or self.base_dir / "temp"

    def create_directories(self) -> None:
        """Cria somente os diretórios necessários em runtime."""
        self.resolved_reports_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_temp_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
