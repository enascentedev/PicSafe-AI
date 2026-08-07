"""Fixtures compartilhadas da suíte."""

import os
from collections.abc import Callable
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("DETECTOR_BACKEND", "stub")


@pytest.fixture
def image_factory() -> Callable[..., bytes]:
    def make_image(
        image_format: str = "PNG",
        size: tuple[int, int] = (16, 16),
    ) -> bytes:
        buffer = BytesIO()
        Image.new("RGB", size, color=(30, 90, 150)).save(
            buffer,
            format=image_format,
        )
        return buffer.getvalue()

    return make_image


@pytest.fixture
def temporary_base(tmp_path: Path) -> Path:
    return tmp_path
