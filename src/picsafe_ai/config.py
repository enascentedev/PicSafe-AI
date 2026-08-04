"""Configurações da aplicação PicSafe AI."""

import os
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configurações da aplicação carregadas de variáveis de ambiente."""

    # Configurações da API
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # Configurações do modelo de visão
    model_version: str = "v1.0.0"
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.45

    # Configurações de logging
    log_level: str = "INFO"

    # Configurações de privacidade/retention
    image_retention_days: int = 30

    # Paths
    base_dir: Path = Path(__file__).parent.parent.parent
    uploads_dir: Path = base_dir / "uploads"
    reports_dir: Path = base_dir / "reports"
    temp_dir: Path = base_dir / "temp"

    class Config:
        """Configuração do Pydantic."""
        # config.env é o arquivo documentado no README e no compose; .env é
        # aceito como override local. O último da sequência tem precedência.
        env_file = ("config.env", ".env")
        env_file_encoding = "utf-8"
        case_sensitive = False
        # Chaves do arquivo que não correspondem a um campo acima são
        # ignoradas. Sem isso, uma variável de outro serviço no mesmo
        # config.env (POSTGRES_PASSWORD, por exemplo) derruba a aplicação
        # no import com extra_forbidden.
        extra = "ignore"

    def create_directories(self) -> None:
        """Cria diretórios necessários se não existirem."""
        for directory in [self.uploads_dir, self.reports_dir, self.temp_dir]:
            directory.mkdir(parents=True, exist_ok=True)


# Instância global das configurações
settings = Settings()
settings.create_directories()
