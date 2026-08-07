"""I/O seguro e centralizado para imagens e relatórios."""

import logging
import time
import uuid
import warnings
from collections.abc import AsyncIterator, Iterator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import cast

from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

logger = logging.getLogger(__name__)

READ_CHUNK_SIZE = 64 * 1024
FORMAT_POLICY: dict[str, tuple[str, str]] = {
    "JPEG": (".jpg", "image/jpeg"),
    "PNG": (".png", "image/png"),
    "WEBP": (".webp", "image/webp"),
}


class UploadValidationError(ValueError):
    """Erro público e seguro de validação de upload."""

    def __init__(self, code: str, public_message: str) -> None:
        super().__init__(public_message)
        self.code = code
        self.public_message = public_message


@dataclass(frozen=True, slots=True)
class UploadPolicy:
    """Limites aplicados de forma idêntica a toda requisição."""

    min_images: int
    max_images: int
    max_file_size_bytes: int
    max_request_size_bytes: int
    max_image_pixels: int


@dataclass(frozen=True, slots=True)
class PreparedImage:
    """Imagem validada com identidade opaca."""

    image_id: str
    path: Path
    media_type: str
    image_format: str
    size_bytes: int


@contextmanager
def analysis_workspace(base_dir: Path) -> Iterator[Path]:
    """Cria e sempre remove um diretório exclusivo por análise."""
    base_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="analysis-", dir=base_dir) as temporary:
        yield Path(temporary)


async def prepare_uploads(
    uploads: Sequence[UploadFile],
    workspace: Path,
    policy: UploadPolicy,
) -> list[PreparedImage]:
    """Valida quantidade, tamanho, MIME e conteúdo decodificável."""
    try:
        count = len(uploads)
        if count < policy.min_images or count > policy.max_images:
            message = f"Envie entre {policy.min_images} e {policy.max_images} imagens"
            raise UploadValidationError("invalid_image_count", message)

        prepared: list[PreparedImage] = []
        request_size = 0
        for upload in uploads:
            image, request_size = await _prepare_upload(
                upload,
                workspace,
                policy,
                request_size,
            )
            prepared.append(image)
        return prepared
    finally:
        for upload in uploads:
            await upload.close()


async def _prepare_upload(
    upload: UploadFile,
    workspace: Path,
    policy: UploadPolicy,
    request_size: int,
) -> tuple[PreparedImage, int]:
    if not upload.filename:
        raise UploadValidationError("missing_filename", "Arquivo sem nome")
    if upload.content_type not in {item[1] for item in FORMAT_POLICY.values()}:
        raise UploadValidationError(
            "invalid_media_type",
            "Use somente imagens JPEG, PNG ou WebP",
        )

    image_id = uuid.uuid4().hex
    temporary_path = workspace / f"{image_id}.upload"
    file_size = 0
    with temporary_path.open("wb") as destination:
        async for chunk in _upload_chunks(upload):
            file_size += len(chunk)
            request_size += len(chunk)
            if file_size > policy.max_file_size_bytes:
                raise UploadValidationError(
                    "file_too_large",
                    "Uma imagem excede o limite permitido",
                )
            if request_size > policy.max_request_size_bytes:
                raise UploadValidationError(
                    "request_too_large",
                    "A requisição excede o limite total permitido",
                )
            destination.write(chunk)

    image_format = _validate_image_content(temporary_path, policy.max_image_pixels)
    suffix, expected_media_type = FORMAT_POLICY[image_format]
    if upload.content_type != expected_media_type:
        raise UploadValidationError(
            "media_type_mismatch",
            "O MIME declarado não corresponde ao conteúdo da imagem",
        )
    final_path = temporary_path.with_suffix(suffix)
    temporary_path.replace(final_path)
    return (
        PreparedImage(
            image_id=image_id,
            path=final_path,
            media_type=expected_media_type,
            image_format=image_format,
            size_bytes=file_size,
        ),
        request_size,
    )


async def _upload_chunks(upload: UploadFile) -> AsyncIterator[bytes]:
    await upload.seek(0)
    while chunk := await upload.read(READ_CHUNK_SIZE):
        yield chunk


def _validate_image_content(path: Path, max_pixels: int) -> str:
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as image:
                image_format = image.format
                if image.width * image.height > max_pixels:
                    raise UploadValidationError(
                        "image_too_large",
                        "A imagem excede o limite de pixels permitido",
                    )
                image.verify()
            with Image.open(path) as decoded:
                decoded.load()
    except UploadValidationError:
        raise
    except (Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise UploadValidationError(
            "image_too_large",
            "A imagem excede o limite de pixels permitido",
        ) from exc
    except (OSError, UnidentifiedImageError) as exc:
        raise UploadValidationError(
            "invalid_image_content",
            "O conteúdo enviado não é uma imagem válida",
        ) from exc
    if image_format is None or image_format not in FORMAT_POLICY:
        raise UploadValidationError(
            "unsupported_image_format",
            "Use somente imagens JPEG, PNG ou WebP",
        )
    return cast("str", image_format)


def read_bytes(path: Path) -> bytes:
    """Lê bytes de um path interno já validado."""
    return path.read_bytes()


def save_image(image: Image.Image, path: Path) -> None:
    """Persiste imagem anotada em path interno controlado."""
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG")


def write_text(path: Path, content: str) -> None:
    """Persiste relatório textual em path interno controlado."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def remove_paths(paths: Sequence[Path]) -> None:
    """Remove artefatos parciais, registrando falhas sem esconder a causa."""
    for path in paths:
        try:
            path.unlink(missing_ok=True)
        except OSError:
            logger.exception("Falha ao remover artefato parcial")


def cleanup_expired_files(directory: Path, retention_days: int) -> int:
    """Aplica de verdade a janela configurada aos relatórios persistentes."""
    if not directory.exists():
        return 0
    cutoff = time.time() - retention_days * 24 * 60 * 60
    removed = 0
    for path in directory.iterdir():
        if path.is_file() and path.stat().st_mtime < cutoff:
            try:
                path.unlink()
                removed += 1
            except OSError:
                logger.exception("Falha ao aplicar retenção a um artefato")
    return removed
