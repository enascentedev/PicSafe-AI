"""Constantes públicas do motor de regras."""

from picsafe_ai.api.schemas import ChecklistStatus, DetectionClass

CRITICAL_CLASSES: tuple[DetectionClass, ...] = (
    DetectionClass.EMERGENCY_STOP,
    DetectionClass.GUARD,
    DetectionClass.EXPOSED_MOVING_PART,
)

CONFIDENCE_THRESHOLDS: dict[DetectionClass, float] = {
    DetectionClass.EMERGENCY_STOP: 0.6,
    DetectionClass.GUARD: 0.5,
    DetectionClass.EXPOSED_MOVING_PART: 0.5,
    DetectionClass.DANGER_ZONE_OPENING: 0.4,
    DetectionClass.SAFETY_SIGN: 0.4,
}

RULE_DESCRIPTIONS: dict[str, str] = {
    "R-001": "Partes móveis expostas e proteções",
    "R-002": "Dispositivo de emergência",
    "R-003": "Sinalização de segurança",
}

ATTENTION_REQUIRED_STATUSES: tuple[ChecklistStatus, ...] = (
    ChecklistStatus.ATENCAO,
    ChecklistStatus.DESCONHECIDO,
)
