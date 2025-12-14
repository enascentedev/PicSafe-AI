"""Módulo de geração de relatórios."""

from .annotate import ImageAnnotator
from .report_html import HTMLReportGenerator

__all__ = ["ImageAnnotator", "HTMLReportGenerator"]
