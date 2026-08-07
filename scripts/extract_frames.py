"""Extrai frames de vídeo para preparação manual de dataset."""

import argparse
import logging
from pathlib import Path

import cv2

from picsafe_ai.utils.logging import setup_logging

logger = logging.getLogger(__name__)


def extract_frames(video_path: Path, output_dir: Path, interval: int) -> int:
    """Extrai um frame a cada ``interval`` quadros."""
    if interval < 1:
        message = "O intervalo precisa ser positivo"
        raise ValueError(message)
    capture = cv2.VideoCapture(str(video_path))
    if not capture.isOpened():
        message = "Não foi possível abrir o vídeo informado"
        raise OSError(message)
    output_dir.mkdir(parents=True, exist_ok=True)
    frame_index = 0
    saved = 0
    try:
        while True:
            available, frame = capture.read()
            if not available:
                break
            if frame_index % interval == 0:
                destination = output_dir / f"frame-{saved:06d}.jpg"
                if not cv2.imwrite(str(destination), frame):
                    message = "Não foi possível persistir um frame"
                    raise OSError(message)
                saved += 1
            frame_index += 1
    finally:
        capture.release()
    logger.info("Extração concluída: %d frames", saved)
    return saved


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("video", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--interval", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    setup_logging()
    arguments = parse_arguments()
    extract_frames(arguments.video, arguments.output, arguments.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
