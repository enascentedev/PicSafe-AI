"""Módulo de checklist e motor de regras NR-12."""

from .mapping import CRITICAL_CLASSES, RULE_DESCRIPTIONS
from .rules import RulesEngine

__all__ = ["RulesEngine", "CRITICAL_CLASSES", "RULE_DESCRIPTIONS"]
