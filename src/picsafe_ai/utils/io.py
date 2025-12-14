"""Utilitários para operações de I/O e arquivos."""

import hashlib
import logging
from pathlib import Path
from typing import Optional

from fastapi import UploadFile

logger = logging.getLogger(__name__)


def save_uploaded_file(upload_file: UploadFile, destination_dir: Path) -> str:
    """
    Salva arquivo enviado via FastAPI em diretório temporário.

    Args:
        upload_file: Arquivo enviado via FastAPI.
        destination_dir: Diretório de destino.

    Returns:
        Caminho completo do arquivo salvo.
    """
    # Criar diretório se não existir
    destination_dir.mkdir(parents=True, exist_ok=True)

    # Gerar nome único baseado no conteúdo
    content = upload_file.file.read()
    file_hash = hashlib.md5(content).hexdigest()[:8]

    # Resetar ponteiro do arquivo
    upload_file.file.seek(0)

    # Criar nome do arquivo
    file_extension = Path(upload_file.filename).suffix.lower()
    filename = f"{file_hash}_{upload_file.filename}"
    file_path = destination_dir / filename

    # Salvar arquivo
    with open(file_path, "wb") as f:
        f.write(content)

    logger.info(f"Arquivo salvo: {file_path}")
    return str(file_path)


def cleanup_old_files(directory: Path, max_age_days: int = 7) -> int:
    """
    Remove arquivos antigos de um diretório.

    Args:
        directory: Diretório a limpar.
        max_age_days: Idade máxima dos arquivos em dias.

    Returns:
        Número de arquivos removidos.
    """
    import time

    if not directory.exists():
        return 0

    current_time = time.time()
    max_age_seconds = max_age_days * 24 * 60 * 60

    removed_count = 0
    for file_path in directory.glob("*"):
        if file_path.is_file():
            file_age = current_time - file_path.stat().st_mtime
            if file_age > max_age_seconds:
                try:
                    file_path.unlink()
                    removed_count += 1
                except Exception as e:
                    logger.warning(f"Erro ao remover {file_path}: {e}")

    if removed_count > 0:
        logger.info(f"Removidos {removed_count} arquivos antigos de {directory}")

    return removed_count


def get_file_info(file_path: str) -> Optional[dict]:
    """
    Obtém informações básicas sobre um arquivo.

    Args:
        file_path: Caminho do arquivo.

    Returns:
        Dicionário com informações ou None se arquivo não existir.
    """
    path = Path(file_path)
    if not path.exists():
        return None

    stat = path.stat()
    return {
        "path": str(path),
        "size": stat.st_size,
        "modified": stat.st_mtime,
        "extension": path.suffix.lower(),
    }


def ensure_directory(directory: Path) -> None:
    """
    Garante que um diretório existe, criando se necessário.

    Args:
        directory: Diretório a verificar/criar.
    """
    directory.mkdir(parents=True, exist_ok=True)
