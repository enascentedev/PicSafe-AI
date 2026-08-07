#!/usr/bin/env python3
"""
Script para extração de frames de vídeo para análise.

Uso:
    python scripts/extract_frames.py video.mp4 --output-dir frames/ --fps 1
"""

import argparse
import logging
import sys
from pathlib import Path

import cv2

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from picsafe_ai.utils import setup_logging

logger = logging.getLogger(__name__)


def extract_frames(
    video_path: str, output_dir: str, fps: float = 1.0, quality: int = 95
) -> int:
    """
    Extrai frames de um vídeo.

    Args:
        video_path: Caminho do vídeo.
        output_dir: Diretório de saída.
        fps: Frames por segundo a extrair.
        quality: Qualidade JPEG (1-100).

    Returns:
        Número de frames extraídos.
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)

    if not video_path.exists():
        msg = f"Vídeo não encontrado: {video_path}"
        raise FileNotFoundError(msg)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Abrir vídeo
    cap = cv2.VideoCapture(str(video_path))

    if not cap.isOpened():
        msg = f"Não foi possível abrir o vídeo: {video_path}"
        raise ValueError(msg)

    # Obter propriedades do vídeo
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    logger.info(f"Vídeo: {total_frames} frames a {video_fps:.2f} FPS")
    logger.info(f"Extraindo frames a {fps} FPS")

    # Calcular intervalo de frames
    frame_interval = int(video_fps / fps) if fps > 0 else 1

    frame_count = 0
    extracted_count = 0

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Extrair frame baseado no intervalo
        if frame_count % frame_interval == 0:
            # Nome do arquivo de saída
            timestamp = frame_count / video_fps
            output_filename = f"frame_{frame_count:06d}_{timestamp:.2f}s.jpg"

            output_path = output_dir / output_filename

            # Salvar frame como JPEG
            success = cv2.imwrite(
                str(output_path), frame, [cv2.IMWRITE_JPEG_QUALITY, quality]
            )

            if success:
                extracted_count += 1
                logger.debug(f"Frame extraído: {output_path}")
            else:
                logger.warning(f"Falha ao salvar frame: {output_path}")

        frame_count += 1

    cap.release()

    logger.info(f"Extração concluída: {extracted_count} frames salvos em {output_dir}")
    return extracted_count


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Extrair frames de vídeo")
    parser.add_argument("video", help="Caminho do vídeo de entrada")
    parser.add_argument(
        "--output-dir",
        "-o",
        default="frames",
        help="Diretório de saída (padrão: frames)",
    )
    parser.add_argument(
        "--fps",
        "-f",
        type=float,
        default=1.0,
        help="Frames por segundo a extrair (padrão: 1.0)",
    )
    parser.add_argument(
        "--quality",
        "-q",
        type=int,
        default=95,
        choices=range(1, 101),
        help="Qualidade JPEG 1-100 (padrão: 95)",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Log detalhado")

    args = parser.parse_args()

    # Configurar logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    try:
        extracted = extract_frames(args.video, args.output_dir, args.fps, args.quality)
        print(f"✅ {extracted} frames extraídos com sucesso!")
        return 0

    except Exception as e:
        logger.exception(f"Erro durante extração: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
