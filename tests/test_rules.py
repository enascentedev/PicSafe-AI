"""Testes para o motor de regras NR-12."""

from picsafe_ai.api.schemas import (
    BoundingBox,
    ChecklistStatus,
    Detection,
    DetectionClass,
)
from picsafe_ai.checklist.rules import RulesEngine


class TestRulesEngine:
    """Testes para o motor de regras."""

    def test_rule_r001_exposed_part_with_guard(self):
        """Testa R-001: parte exposta COM proteção."""
        detections = [
            Detection(
                class_name=DetectionClass.EXPOSED_MOVING_PART,
                confidence=0.8,
                bbox=BoundingBox(x_min=0.2, y_min=0.3, x_max=0.4, y_max=0.5),
                image_path="test.jpg",
            ),
            Detection(
                class_name=DetectionClass.GUARD,
                confidence=0.9,
                bbox=BoundingBox(x_min=0.15, y_min=0.25, x_max=0.45, y_max=0.55),
                image_path="test.jpg",
            ),
        ]

        checklist, _ = RulesEngine.apply_rules(detections)

        r001_item = next(item for item in checklist if item.rule_id == "R-001")
        assert r001_item.status == ChecklistStatus.OK
        assert "proteção adequada" in r001_item.evidence.lower()

    def test_rule_r001_exposed_part_without_guard(self):
        """Testa R-001: parte exposta SEM proteção."""
        detections = [
            Detection(
                class_name=DetectionClass.EXPOSED_MOVING_PART,
                confidence=0.8,
                bbox=BoundingBox(x_min=0.2, y_min=0.3, x_max=0.4, y_max=0.5),
                image_path="test.jpg",
            )
        ]

        checklist, _ = RulesEngine.apply_rules(detections)

        r001_item = next(item for item in checklist if item.rule_id == "R-001")
        assert r001_item.status == ChecklistStatus.ATENCAO
        assert "sem proteção" in r001_item.evidence.lower()

    def test_rule_r002_emergency_stop_present(self):
        """Testa R-002: botão de emergência presente."""
        detections = [
            Detection(
                class_name=DetectionClass.EMERGENCY_STOP,
                confidence=0.85,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_path="test.jpg",
            )
        ]

        checklist, _ = RulesEngine.apply_rules(detections)

        r002_item = next(item for item in checklist if item.rule_id == "R-002")
        assert r002_item.status == ChecklistStatus.OK
        assert "detectado" in r002_item.evidence.lower()

    def test_rule_r002_emergency_stop_missing(self):
        """Testa R-002: botão de emergência ausente."""
        detections = [
            Detection(
                class_name=DetectionClass.GUARD,
                confidence=0.9,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_path="test.jpg",
            )
        ]

        checklist, pending = RulesEngine.apply_rules(detections)

        r002_item = next(item for item in checklist if item.rule_id == "R-002")
        assert r002_item.status == ChecklistStatus.DESCONHECIDO

        # Deve gerar pendência de foto do posto de operação
        posto_pending = next(
            (p for p in pending if "posto de operação" in p.description.lower()), None
        )
        assert posto_pending is not None
        assert "botão de emergência" in posto_pending.reason.lower()

    def test_rule_r003_safety_sign_present(self):
        """Testa R-003: sinalização presente."""
        detections = [
            Detection(
                class_name=DetectionClass.SAFETY_SIGN,
                confidence=0.7,
                bbox=BoundingBox(x_min=0.7, y_min=0.1, x_max=0.9, y_max=0.25),
                image_path="test.jpg",
            )
        ]

        checklist, _ = RulesEngine.apply_rules(detections)

        r003_item = next(item for item in checklist if item.rule_id == "R-003")
        assert r003_item.status == ChecklistStatus.OK

    def test_rule_r003_safety_sign_missing(self):
        """Testa R-003: sinalização ausente."""
        detections = []  # Nenhuma detecção

        checklist, _ = RulesEngine.apply_rules(detections)

        r003_item = next(item for item in checklist if item.rule_id == "R-003")
        assert r003_item.status == ChecklistStatus.DESCONHECIDO

    def test_multiple_rules_applied(self):
        """Testa aplicação simultânea de múltiplas regras."""
        detections = [
            # Parte móvel sem proteção (R-001 = ATENÇÃO)
            Detection(
                class_name=DetectionClass.EXPOSED_MOVING_PART,
                confidence=0.8,
                bbox=BoundingBox(x_min=0.2, y_min=0.3, x_max=0.4, y_max=0.5),
                image_path="test.jpg",
            ),
            # Botão presente (R-002 = OK)
            Detection(
                class_name=DetectionClass.EMERGENCY_STOP,
                confidence=0.85,
                bbox=BoundingBox(x_min=0.1, y_min=0.1, x_max=0.3, y_max=0.3),
                image_path="test.jpg",
            ),
        ]

        checklist, _ = RulesEngine.apply_rules(detections)

        # Verificar que temos 3 regras
        assert len(checklist) == 3

        # Verificar status de cada regra
        r001 = next(item for item in checklist if item.rule_id == "R-001")
        r002 = next(item for item in checklist if item.rule_id == "R-002")
        r003 = next(item for item in checklist if item.rule_id == "R-003")

        assert r001.status == ChecklistStatus.ATENCAO
        assert r002.status == ChecklistStatus.OK
        assert r003.status == ChecklistStatus.DESCONHECIDO

    def test_bbox_overlap_calculation(self):
        """Testa cálculo de sobreposição de bounding boxes."""
        bbox1 = BoundingBox(x_min=0.2, y_min=0.3, x_max=0.4, y_max=0.5)
        bbox2 = BoundingBox(x_min=0.15, y_min=0.25, x_max=0.45, y_max=0.55)

        overlap = RulesEngine._bboxes_overlap(bbox1, bbox2)
        assert overlap > 0.5  # Deve haver sobreposição significativa

        # Testar sem sobreposição
        bbox3 = BoundingBox(x_min=0.6, y_min=0.6, x_max=0.8, y_max=0.8)
        no_overlap = RulesEngine._bboxes_overlap(bbox1, bbox3)
        assert no_overlap == 0.0
