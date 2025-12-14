"""Testes para schemas Pydantic da API."""

import pytest
from pydantic import ValidationError

from picsafe_ai.api.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    BoundingBox,
    ChecklistItem,
    ChecklistStatus,
    Detection,
    DetectionClass,
    PendingPhoto,
)


class TestSchemas:
    """Testes para validação de schemas."""

    def test_detection_schema_valid(self):
        """Testa schema de detecção válido."""
        detection = Detection(
            class_name=DetectionClass.EMERGENCY_STOP,
            confidence=0.85,
            bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
            image_path="test.jpg"
        )

        assert detection.class_name == DetectionClass.EMERGENCY_STOP
        assert detection.confidence == 0.85
        assert detection.image_path == "test.jpg"

    def test_detection_schema_invalid_confidence(self):
        """Testa schema de detecção com confiança inválida."""
        with pytest.raises(ValidationError):
            Detection(
                class_name=DetectionClass.EMERGENCY_STOP,
                confidence=1.5,  # Inválido: deve ser <= 1.0
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_path="test.jpg"
            )

    def test_detection_schema_invalid_bbox(self):
        """Testa schema de detecção com bbox inválido."""
        with pytest.raises(ValidationError):
            Detection(
                class_name=DetectionClass.EMERGENCY_STOP,
                confidence=0.85,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=1.5, y_max=0.3),  # x_max > 1.0
                image_path="test.jpg"
            )

    def test_checklist_item_schema(self):
        """Testa schema de item do checklist."""
        item = ChecklistItem(
            rule_id="R-001",
            description="Teste de regra",
            status=ChecklistStatus.ATENCAO,
            evidence="Evidência encontrada",
            notes="Notas adicionais"
        )

        assert item.rule_id == "R-001"
        assert item.status == ChecklistStatus.ATENCAO
        assert item.evidence == "Evidência encontrada"

    def test_pending_photo_schema(self):
        """Testa schema de foto pendente."""
        photo = PendingPhoto(
            description="Foto do posto de operação",
            reason="Botão não localizado"
        )

        assert "posto" in photo.description.lower()
        assert "botão" in photo.reason.lower()

    def test_analysis_request_schema(self):
        """Testa schema de requisição de análise."""
        request = AnalysisRequest(
            machine_id="MAQ-001",
            notes="Máquina de teste"
        )

        assert request.machine_id == "MAQ-001"
        assert request.notes == "Máquina de teste"

    def test_analysis_response_schema(self):
        """Testa schema de resposta de análise."""
        response = AnalysisResponse(
            machine_id="MAQ-001",
            detections=[],
            checklist=[],
            pending_photos=[],
            report_html="<html>Teste</html>",
            model_version="v1.0.0",
            confidence_threshold=0.5,
            analysis_timestamp="2024-01-01T10:00:00Z",
            processing_time_seconds=2.5
        )

        assert response.machine_id == "MAQ-001"
        assert response.model_version == "v1.0.0"
        assert response.processing_time_seconds == 2.5
        assert "<html>" in response.report_html

    def test_all_detection_classes(self):
        """Testa todas as classes de detecção."""
        classes = [
            DetectionClass.EMERGENCY_STOP,
            DetectionClass.GUARD,
            DetectionClass.EXPOSED_MOVING_PART,
            DetectionClass.DANGER_ZONE_OPENING,
            DetectionClass.SAFETY_SIGN,
        ]

        for cls in classes:
            detection = Detection(
                class_name=cls,
                confidence=0.8,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_path="test.jpg"
            )
            assert detection.class_name == cls

    def test_all_checklist_statuses(self):
        """Testa todos os status do checklist."""
        statuses = [
            ChecklistStatus.OK,
            ChecklistStatus.ATENCAO,
            ChecklistStatus.DESCONHECIDO,
        ]

        for status in statuses:
            item = ChecklistItem(
                rule_id="R-001",
                description="Teste",
                status=status
            )
            assert item.status == status
