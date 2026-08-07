"""Orquestração segura de uma análise visual."""

import time
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Final

from fastapi import UploadFile

from picsafe_ai.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    AnalysisStatus,
    Detection,
    ImageProcessingError,
    PendingPhoto,
)
from picsafe_ai.checklist import RulesEngine
from picsafe_ai.config import Settings
from picsafe_ai.reporting import HTMLReportGenerator, ImageAnnotator
from picsafe_ai.utils import io
from picsafe_ai.vision import DetectorError, PostProcessor, VisionDetector

DETECTOR_ERROR_CODE: Final = "detector_error"


class AnalysisUnavailableError(RuntimeError):
    """Nenhuma imagem pôde ser processada pelo detector."""


class AnalysisService:
    """Coordena validação, inferência, regras, evidências e retenção."""

    def __init__(
        self,
        *,
        app_settings: Settings,
        detector: VisionDetector,
        post_processor: PostProcessor,
    ) -> None:
        self._settings = app_settings
        self._detector = detector
        self._post_processor = post_processor
        self._rules_engine = RulesEngine()
        self._policy = io.UploadPolicy(
            min_images=app_settings.min_images,
            max_images=app_settings.max_images,
            max_file_size_bytes=app_settings.max_file_size_bytes,
            max_request_size_bytes=app_settings.max_request_size_bytes,
            max_image_pixels=app_settings.max_image_pixels,
        )

    async def analyze(
        self,
        uploads: list[UploadFile],
        request: AnalysisRequest,
    ) -> AnalysisResponse:
        """Executa uma análise e persiste apenas artefatos finais opacos."""
        started_at = time.perf_counter()
        analysis_id = uuid.uuid4().hex
        artifacts: list[Path] = []
        io.cleanup_expired_files(
            self._settings.resolved_reports_dir,
            self._settings.image_retention_days,
        )

        with io.analysis_workspace(self._settings.resolved_temp_dir) as workspace:
            prepared = await io.prepare_uploads(uploads, workspace, self._policy)
            detections = []
            successful = []
            errors: list[ImageProcessingError] = []
            for image in prepared:
                try:
                    detections.extend(
                        self._detector.predict(
                            io.read_bytes(image.path),
                            image.image_id,
                        )
                    )
                    successful.append(image)
                except DetectorError:
                    errors.append(
                        ImageProcessingError(
                            image_id=image.image_id,
                            code=DETECTOR_ERROR_CODE,
                            message="Não foi possível analisar esta imagem",
                        )
                    )

            if not successful:
                message = "O detector não conseguiu processar nenhuma imagem"
                raise AnalysisUnavailableError(message)

            processed = self._post_processor.process_detections(detections)
            checklist, pending = self._rules_engine.apply_rules(
                processed,
                self._detector.metadata,
            )
            pending.extend(
                PendingPhoto(
                    image_id=error.image_id,
                    description="Reenviar uma foto válida deste ângulo",
                    reason=error.message,
                )
                for error in errors
            )
            status = AnalysisStatus.PARTIAL if errors else AnalysisStatus.COMPLETE
            response = AnalysisResponse(
                analysis_id=analysis_id,
                analysis_status=status,
                machine_id=request.machine_id,
                detections=processed,
                checklist=checklist,
                pending_photos=pending,
                image_errors=errors,
                detector=self._detector.metadata,
                report_html="",
                model_version=self._detector.metadata.version,
                confidence_threshold=self._settings.confidence_threshold,
                thresholds={
                    "confidence": self._settings.confidence_threshold,
                    "nms": self._settings.nms_threshold,
                },
                analysis_timestamp=datetime.now(UTC).isoformat(),
                processing_time_seconds=time.perf_counter() - started_at,
            )
            completed = False
            try:
                self._persist_annotated_images(
                    successful,
                    processed,
                    analysis_id,
                    artifacts,
                )
                response.report_html = HTMLReportGenerator.generate_report(response)
                report_path = (
                    self._settings.resolved_reports_dir / f"{analysis_id}-report.html"
                )
                io.write_text(report_path, response.report_html)
                artifacts.append(report_path)
                completed = True
            finally:
                if not completed:
                    io.remove_paths(artifacts)
            return response

    def _persist_annotated_images(
        self,
        images: list[io.PreparedImage],
        detections: list[Detection],
        analysis_id: str,
        artifacts: list[Path],
    ) -> None:
        for image in images:
            annotated = ImageAnnotator.annotate_image(
                str(image.path),
                image.image_id,
                detections,
            )
            output = (
                self._settings.resolved_reports_dir
                / f"{analysis_id}-{image.image_id}.png"
            )
            artifacts.append(output)
            io.save_image(annotated, output)
