"""Aplicação FastAPI do PicSafe AI."""

from datetime import UTC, datetime
from typing import Annotated

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from picsafe_ai import __version__
from picsafe_ai.api.analysis import AnalysisService, AnalysisUnavailableError
from picsafe_ai.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    ApiError,
    HealthResponse,
)
from picsafe_ai.config import Settings, settings
from picsafe_ai.utils.io import UploadValidationError
from picsafe_ai.utils.logging import setup_logging
from picsafe_ai.vision import PostProcessor, VisionDetector, build_detector


def _error_response(status_code: int, error: ApiError) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=error.model_dump())


def create_app(
    app_settings: Settings | None = None,
    detector: VisionDetector | None = None,
) -> FastAPI:
    """Cria uma aplicação com dependências substituíveis em testes."""
    active_settings = app_settings or settings
    active_settings.create_directories()
    setup_logging(active_settings.log_level)
    active_detector = detector or build_detector(active_settings)
    service = AnalysisService(
        app_settings=active_settings,
        detector=active_detector,
        post_processor=PostProcessor(
            confidence_threshold=active_settings.confidence_threshold,
            nms_threshold=active_settings.nms_threshold,
        ),
    )
    application = FastAPI(
        title="PicSafe AI — pré-avaliação visual",
        description=(
            "PoC de apoio à triagem visual. Não emite laudo nem declara "
            "conformidade com a NR-12."
        ),
        version=__version__,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=active_settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    @application.exception_handler(UploadValidationError)
    async def upload_error_handler(
        _request: Request,
        exc: UploadValidationError,
    ) -> JSONResponse:
        return _error_response(
            422,
            ApiError(code=exc.code, message=exc.public_message),
        )

    @application.exception_handler(AnalysisUnavailableError)
    async def detector_error_handler(
        _request: Request,
        _exc: AnalysisUnavailableError,
    ) -> JSONResponse:
        return _error_response(
            503,
            ApiError(
                code="analysis_unavailable",
                message="A análise visual está temporariamente indisponível",
            ),
        )

    @application.get("/", response_class=HTMLResponse)
    async def root() -> HTMLResponse:
        return HTMLResponse(
            "<h1>PicSafe AI</h1>"
            "<p>Pré-avaliação visual experimental; requer validação por "
            "profissional habilitado.</p>"
        )

    @application.post("/v1/analisar", response_model=AnalysisResponse)
    async def analyze_images(
        files: Annotated[list[UploadFile], File()],
        machine_id: Annotated[str | None, Form(max_length=80)] = None,
        notes: Annotated[str | None, Form(max_length=500)] = None,
    ) -> AnalysisResponse:
        metadata = AnalysisRequest(machine_id=machine_id, notes=notes)
        return await service.analyze(files, metadata)

    @application.get("/health", response_model=HealthResponse)
    async def health_check() -> HealthResponse:
        return HealthResponse(
            status="healthy",
            version=__version__,
            detector=active_detector.metadata,
            timestamp=datetime.now(UTC).isoformat(),
        )

    return application


app = create_app()
