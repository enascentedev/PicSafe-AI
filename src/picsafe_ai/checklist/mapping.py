"""Mapeamento e constantes para o motor de regras."""

from picsafe_ai.api.schemas import DetectionClass

# Mapeamento de classes críticas para regras específicas
CRITICAL_CLASSES = [
    DetectionClass.EMERGENCY_STOP,
    DetectionClass.GUARD,
    DetectionClass.EXPOSED_MOVING_PART,
]

# Thresholds de confiança por classe (mais baixos para classes críticas)
CONFIDENCE_THRESHOLDS: dict[DetectionClass, float] = {
    DetectionClass.EMERGENCY_STOP: 0.6,  # Mais rigoroso
    DetectionClass.GUARD: 0.5,
    DetectionClass.EXPOSED_MOVING_PART: 0.5,
    DetectionClass.DANGER_ZONE_OPENING: 0.4,
    DetectionClass.SAFETY_SIGN: 0.4,
}

# Descrições das regras aplicadas
RULE_DESCRIPTIONS = {
    "R-001": "Parte móvel exposta sem proteção adequada",
    "R-002": "Ausência de botão/cabo de emergência visível",
    "R-003": "Ausência de sinalização de segurança adequada",
}

# Regras que requerem evidência visual obrigatória
MANDATORY_EVIDENCE_RULES = ["R-001", "R-002"]

# Estados que indicam necessidade de atenção do profissional
ATTENTION_REQUIRED_STATUSES = ["ATENÇÃO", "DESCONHECIDO"]
