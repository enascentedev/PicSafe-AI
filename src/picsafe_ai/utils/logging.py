"""Configuração de logging estruturado para o PicSafe AI."""

import logging
import sys
from pathlib import Path
from typing import Optional

from structlog import configure, get_logger, stdlib
from structlog.processors import JSONRenderer, TimeStamper

from ..config import settings


def setup_logging(log_level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configura logging estruturado com structlog.

    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR).
        log_file: Caminho opcional para arquivo de log.
    """
    # Configurar nível de logging
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Processadores para structlog
    processors = [
        stdlib.filter_by_level,
        stdlib.add_logger_name,
        stdlib.add_log_level,
        stdlib.PositionalArgumentsFormatter(),
        TimeStamper(fmt="iso"),
        stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # Adicionar saída para arquivo se especificado
    if log_file:
        processors.append(write_to_file(Path(log_file)))

    # Adicionar renderização JSON
    processors.append(JSONRenderer())

    # Configurar structlog
    configure(
        processors=processors,
        context_class=dict,
        logger_factory=stdlib.WriteLoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configurar logging padrão do Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    # Configurar loggers específicos
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Obtém logger configurado com structlog.

    Args:
        name: Nome do logger.

    Returns:
        Logger configurado.
    """
    return get_logger(name)
