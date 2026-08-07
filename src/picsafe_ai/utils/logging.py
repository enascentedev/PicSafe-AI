"""Configuração mínima de logging sem dados de imagens."""

import logging


def setup_logging(log_level: str = "INFO") -> None:
    """Configura logging padrão em formato acionável."""
    level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


def get_logger(name: str) -> logging.Logger:
    """Obtém logger nomeado."""
    return logging.getLogger(name)
