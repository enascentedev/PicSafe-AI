"""Configuração de logging estruturado para o PicSafe AI."""

import logging
import sys
from pathlib import Path
from typing import Any, cast

from structlog import configure, stdlib
from structlog import get_logger as _structlog_get_logger
from structlog.processors import JSONRenderer, TimeStamper


def setup_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    Configura logging estruturado com structlog.

    Args:
        log_level: Nível de logging (DEBUG, INFO, WARNING, ERROR).
        log_file: Caminho opcional para arquivo de log.
    """
    # Configurar nível de logging
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Processadores para structlog
    processors: list[Any] = [
        stdlib.filter_by_level,
        stdlib.add_logger_name,
        stdlib.add_log_level,
        stdlib.PositionalArgumentsFormatter(),
        TimeStamper(fmt="iso"),
        stdlib.ProcessorFormatter.wrap_for_formatter,
    ]

    # Adicionar renderização JSON
    processors.append(JSONRenderer())

    # Configurar structlog
    configure(
        processors=processors,
        context_class=dict,
        logger_factory=stdlib.LoggerFactory(),
        wrapper_class=stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configurar logging padrão do Python
    handlers: list[logging.Handler] = [logging.StreamHandler(sys.stdout)]
    if log_file:
        handlers.append(logging.FileHandler(Path(log_file), encoding="utf-8"))

    logging.basicConfig(
        format="%(message)s",
        level=level,
        handlers=handlers,
        force=True,
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
    return cast("logging.Logger", _structlog_get_logger(name))
