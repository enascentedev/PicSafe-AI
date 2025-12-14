#!/usr/bin/env python3
"""
Script para executar inferência em lote em uma pasta de imagens.

Uso:
    python scripts/run_inference_folder.py /caminho/para/imagens/ --output results.json
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from pathlib import Path

import aiofiles

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from picsafe_ai.api.schemas import AnalysisResponse
from picsafe_ai.checklist import RulesEngine
from picsafe_ai.config import settings
from picsafe_ai.reporting import HTMLReportGenerator
from picsafe_ai.utils import setup_logging
from picsafe_ai.vision import PostProcessor, VisionDetector

logger = logging.getLogger(__name__)


async def process_images_batch(
    image_paths: list[Path],
    detector: VisionDetector,
    post_processor: PostProcessor,
    rules_engine: RulesEngine
) -> AnalysisResponse:
    """
    Processa um lote de imagens.

    Args:
        image_paths: Lista de caminhos das imagens.
        detector: Detector de visão.
        post_processor: Pós-processador.
        rules_engine: Motor de regras.

    Returns:
        Resposta da análise.
    """
    start_time = time.time()

    all_detections = []

    for image_path in image_paths:
        try:
            async with aiofiles.open(image_path, "rb") as f:
                image_bytes = await f.read()

            detections = detector.predict(image_bytes, str(image_path))
            all_detections.extend(detections)

            logger.info(f"Processada: {image_path.name} - {len(detections)} detecções")

        except Exception as e:
            logger.error(f"Erro ao processar {image_path}: {e}")
            continue

    # Pós-processamento
    processed_detections = post_processor.process_detections(all_detections)

    # Aplicar regras
    checklist, pending_photos = rules_engine.apply_rules(processed_detections)

    # Gerar resposta
    response = AnalysisResponse(
        machine_id=f"batch_{int(time.time())}",
        detections=processed_detections,
        checklist=checklist,
        pending_photos=pending_photos,
        report_html="",  # Será gerado depois
        model_version=settings.model_version,
        confidence_threshold=settings.confidence_threshold,
        analysis_timestamp="2024-01-01T00:00:00Z",  # Placeholder
        processing_time_seconds=time.time() - start_time
    )

    # Gerar HTML
    response.report_html = HTMLReportGenerator.generate_report(response)

    return response


async def run_inference_on_folder(
    input_dir: str,
    output_file: str,
    max_images: int = None,
    batch_size: int = 10
) -> None:
    """
    Executa inferência em todas as imagens de uma pasta.

    Args:
        input_dir: Diretório com imagens.
        output_file: Arquivo de saída JSON.
        max_images: Máximo de imagens a processar.
        batch_size: Tamanho do lote de processamento.
    """
    input_path = Path(input_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Diretório não encontrado: {input_path}")

    # Encontrar imagens
    image_extensions = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
    image_paths = [
        f for f in input_path.rglob("*")
        if f.is_file() and f.suffix.lower() in image_extensions
    ]

    if not image_paths:
        logger.warning(f"Nenhuma imagem encontrada em {input_path}")
        return

    if max_images:
        image_paths = image_paths[:max_images]

    logger.info(f"Encontradas {len(image_paths)} imagens")

    # Inicializar componentes
    detector = VisionDetector()
    post_processor = PostProcessor()
    rules_engine = RulesEngine()

    # Processar em lotes
    all_responses = []

    for i in range(0, len(image_paths), batch_size):
        batch_paths = image_paths[i:i + batch_size]
        logger.info(f"Processando lote {i//batch_size + 1}: {len(batch_paths)} imagens")

        response = await process_images_batch(
            batch_paths, detector, post_processor, rules_engine
        )
        all_responses.append(response)

    # Salvar resultados
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    results = {
        "summary": {
            "total_images": len(image_paths),
            "total_batches": len(all_responses),
            "total_detections": sum(len(r.detections) for r in all_responses),
            "processing_time_seconds": sum(r.processing_time_seconds for r in all_responses),
        },
        "batches": [r.dict() for r in all_responses]
    }

    async with aiofiles.open(output_path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(results, indent=2, ensure_ascii=False))

    logger.info(f"Resultados salvos em: {output_path}")
    logger.info(f"Resumo: {results['summary']}")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Executar inferência em lote")
    parser.add_argument("input_dir", help="Diretório com imagens")
    parser.add_argument(
        "--output",
        "-o",
        default="inference_results.json",
        help="Arquivo de saída JSON (padrão: inference_results.json)"
    )
    parser.add_argument(
        "--max-images",
        "-m",
        type=int,
        help="Máximo de imagens a processar"
    )
    parser.add_argument(
        "--batch-size",
        "-b",
        type=int,
        default=10,
        help="Tamanho do lote (padrão: 10)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Log detalhado"
    )

    args = parser.parse_args()

    # Configurar logging
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level)

    try:
        asyncio.run(run_inference_on_folder(
            args.input_dir,
            args.output,
            args.max_images,
            args.batch_size
        ))
        print("✅ Inferência concluída com sucesso!")
        return 0

    except Exception as e:
        logger.error(f"Erro durante inferência: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
