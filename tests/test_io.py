"""Validação binária, limites, limpeza e retenção."""

import os
import time
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pytest
from starlette.datastructures import Headers, UploadFile

from picsafe_ai.utils.io import (
    UploadPolicy,
    UploadValidationError,
    analysis_workspace,
    cleanup_expired_files,
    prepare_uploads,
)


def upload(content: bytes, content_type: str = "image/png") -> UploadFile:
    return UploadFile(
        BytesIO(content),
        filename="photo.png",
        headers=Headers({"content-type": content_type}),
    )


def policy(**overrides: int) -> UploadPolicy:
    values = {
        "min_images": 4,
        "max_images": 12,
        "max_file_size_bytes": 10_000,
        "max_request_size_bytes": 100_000,
        "max_image_pixels": 10_000,
    }
    values.update(overrides)
    return UploadPolicy(**values)


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [4, 12])
async def test_accepts_boundary_counts(
    count: int,
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    with analysis_workspace(temporary_base) as workspace:
        prepared = await prepare_uploads(
            [upload(image_factory()) for _ in range(count)],
            workspace,
            policy(),
        )
        assert len(prepared) == count
        assert all(item.path.suffix == ".png" for item in prepared)
        assert all(item.image_id not in {"photo", "photo.png"} for item in prepared)


@pytest.mark.asyncio
@pytest.mark.parametrize("count", [0, 3, 13])
async def test_rejects_counts_outside_policy(
    count: int,
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    files = [upload(image_factory()) for _ in range(count)]
    with (
        analysis_workspace(temporary_base) as workspace,
        pytest.raises(UploadValidationError, match="entre 4 e 12"),
    ):
        await prepare_uploads(
            files,
            workspace,
            policy(),
        )
    assert all(item.file.closed for item in files)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("content", "media_type", "code"),
    [
        (b"not-an-image", "image/png", "invalid_image_content"),
        (b"not-an-image", "text/plain", "invalid_media_type"),
    ],
)
async def test_rejects_invalid_uploads_atomically(
    content: bytes,
    media_type: str,
    code: str,
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    files = [upload(image_factory()) for _ in range(3)] + [upload(content, media_type)]
    workspace_path: Path
    with (
        analysis_workspace(temporary_base) as workspace_path,
        pytest.raises(UploadValidationError) as captured,
    ):
        await prepare_uploads(files, workspace_path, policy())
    assert captured.value.code == code
    assert all(item.file.closed for item in files)
    assert not workspace_path.exists()


@pytest.mark.asyncio
async def test_rejects_mime_mismatch(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    jpeg = image_factory("JPEG")
    with (
        analysis_workspace(temporary_base) as workspace,
        pytest.raises(UploadValidationError) as captured,
    ):
        await prepare_uploads(
            [upload(jpeg) for _ in range(4)],
            workspace,
            policy(),
        )
    assert captured.value.code == "media_type_mismatch"


@pytest.mark.asyncio
async def test_enforces_file_request_and_pixel_limits(
    image_factory: Callable[..., bytes],
    temporary_base: Path,
) -> None:
    content = image_factory(size=(20, 20))
    cases = [
        (policy(max_file_size_bytes=10), "file_too_large"),
        (
            policy(max_file_size_bytes=1_000, max_request_size_bytes=100),
            "request_too_large",
        ),
        (policy(max_image_pixels=100), "image_too_large"),
    ]
    for active_policy, code in cases:
        with (
            analysis_workspace(temporary_base) as workspace,
            pytest.raises(UploadValidationError) as captured,
        ):
            await prepare_uploads(
                [upload(content) for _ in range(4)],
                workspace,
                active_policy,
            )
        assert captured.value.code == code


def test_retention_removes_only_expired_files(temporary_base: Path) -> None:
    old = temporary_base / "old.html"
    recent = temporary_base / "recent.html"
    old.write_text("old", encoding="utf-8")
    recent.write_text("recent", encoding="utf-8")
    old_time = time.time() - 3 * 24 * 60 * 60
    os.utime(old, (old_time, old_time))
    assert cleanup_expired_files(temporary_base, retention_days=2) == 1
    assert not old.exists()
    assert recent.exists()
