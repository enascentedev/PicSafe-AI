"""Schemas, pós-processamento e regras conservadoras."""

import pytest
from pydantic import ValidationError

from picsafe_ai.api.schemas import (
    BoundingBox,
    ChecklistStatus,
    Detection,
    DetectionClass,
    DetectorMetadata,
    DetectorMode,
)
from picsafe_ai.checklist import RulesEngine
from picsafe_ai.vision import PostProcessor


def make_detection(
    class_name: DetectionClass,
    image_id: str = "image-a",
    confidence: float = 0.9,
    bbox: BoundingBox | None = None,
) -> Detection:
    return Detection(
        class_name=class_name,
        confidence=confidence,
        bbox=bbox or BoundingBox(x_min=0.1, y_min=0.1, x_max=0.5, y_max=0.5),
        image_id=image_id,
        image_path=image_id,
    )


def metadata(mode: DetectorMode = DetectorMode.REAL) -> DetectorMetadata:
    return DetectorMetadata(name="detector", version="1", mode=mode)


def test_bounding_box_requires_positive_area() -> None:
    with pytest.raises(ValidationError, match="área positiva"):
        BoundingBox(x_min=0.5, y_min=0.1, x_max=0.5, y_max=0.7)


def test_postprocessor_filters_and_applies_nms_per_image() -> None:
    processor = PostProcessor(confidence_threshold=0.5, nms_threshold=0.3)
    detections = [
        make_detection(DetectionClass.GUARD, confidence=0.9),
        make_detection(DetectionClass.GUARD, confidence=0.8),
        make_detection(DetectionClass.GUARD, image_id="image-b"),
        make_detection(DetectionClass.SAFETY_SIGN, confidence=0.2),
    ]
    processed = processor.process_detections(detections)
    assert len(processed) == 2
    assert {item.image_id for item in processed} == {"image-a", "image-b"}
    assert processor.calculate_iou(detections[0], detections[2]) == 0


def test_rules_do_not_associate_boxes_from_different_images() -> None:
    detections = [
        make_detection(DetectionClass.EXPOSED_MOVING_PART, "image-a"),
        make_detection(DetectionClass.GUARD, "image-b"),
    ]
    checklist, _pending = RulesEngine().apply_rules(detections, metadata())
    rule = next(item for item in checklist if item.rule_id == "R-001")
    assert rule.status is ChecklistStatus.ATENCAO
    assert [item.image_id for item in rule.evidence_refs] == ["image-a"]


def test_rules_produce_traceable_ok_only_for_real_evidence() -> None:
    detections = [
        make_detection(DetectionClass.EXPOSED_MOVING_PART),
        make_detection(DetectionClass.GUARD),
        make_detection(DetectionClass.EMERGENCY_STOP),
        make_detection(DetectionClass.SAFETY_SIGN),
    ]
    checklist, pending = RulesEngine().apply_rules(detections, metadata())
    assert all(item.status is ChecklistStatus.OK for item in checklist)
    assert all(item.evidence_refs for item in checklist)
    assert pending == []


def test_simulated_evidence_never_produces_ok() -> None:
    detections = [
        make_detection(DetectionClass.EMERGENCY_STOP),
        make_detection(DetectionClass.SAFETY_SIGN),
    ]
    checklist, _pending = RulesEngine().apply_rules(
        detections,
        metadata(DetectorMode.SIMULATED),
    )
    assert all(item.status is ChecklistStatus.DESCONHECIDO for item in checklist)
    assert all(item.status is not ChecklistStatus.OK for item in checklist)


def test_danger_zone_requests_same_image_evidence() -> None:
    detections = [
        make_detection(DetectionClass.DANGER_ZONE_OPENING, "danger"),
        make_detection(DetectionClass.SAFETY_SIGN, "other"),
    ]
    _checklist, pending = RulesEngine().apply_rules(detections, metadata())
    assert any(item.image_id == "danger" for item in pending)


def test_bbox_iou_handles_disjoint_boxes() -> None:
    first = BoundingBox(x_min=0.0, y_min=0.0, x_max=0.2, y_max=0.2)
    second = BoundingBox(x_min=0.8, y_min=0.8, x_max=1.0, y_max=1.0)
    assert RulesEngine.bbox_iou(first, second) == 0
