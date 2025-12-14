#!/usr/bin/env python3
"""
Script para gerar relatório HTML a partir de resultados JSON.

Uso:
    python scripts/build_report.py results.json --output report.html
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from picsafe_ai.api.schemas import AnalysisResponse
from picsafe_ai.reporting import HTMLReportGenerator
from picsafe_ai.utils import setup_logging

logger = logging.getLogger(__name__)


def build_report_from_json(json_file: str, output_file: str) -> None:
    """
    Gera relatório HTML a partir de arquivo JSON.

    Args:
        json_file: Arquivo JSON com resultados.
        output_file: Arquivo HTML de saída.
    """
    json_path = Path(json_file)
    if not json_path.exists():
        raise FileNotFoundError(f"Arquivo JSON não encontrado: {json_path}")

    # Carregar dados JSON
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    logger.info(f"Dados carregados de: {json_path}")

    # Verificar se é resultado de lote ou análise única
    if "batches" in data:
        # Resultado de lote - combinar em uma análise
        logger.info("Processando resultado de lote")

        combined_detections = []
        combined_checklist = []
        combined_pending = []

        for batch in data["batches"]:
            response = AnalysisResponse(**batch)
            combined_detections.extend(response.detections)
            combined_checklist.extend(response.checklist)
            combined_pending.extend(response.pending_photos)

        # Usar dados do primeiro batch como base
        if data["batches"]:
            base_response = AnalysisResponse(**data["batches"][0])
            base_response.detections = combined_detections
            base_response.checklist = combined_checklist
            base_response.pending_photos = combined_pending
            base_response.machine_id = f"combined_{len(data['batches'])}_batches"
        else:
            raise ValueError("Nenhum batch encontrado no arquivo JSON")

    else:
        # Análise única
        logger.info("Processando análise única")
        base_response = AnalysisResponse(**data)

    # Regenerar HTML
    base_response.report_html = HTMLReportGenerator.generate_report(base_response)

    # Salvar relatório
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(base_response.report_html)

    logger.info(f"Relatório HTML salvo em: {output_path}")
    logger.info(f"Resumo: {len(base_response.detections)} detecções, {len(base_response.checklist)} itens no checklist")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description="Gerar relatório HTML")
    parser.add_argument("json_file", help="Arquivo JSON com resultados")
    parser.add_argument(
        "--output",
        "-o",
        default="report.html",
        help="Arquivo HTML de saída (padrão: report.html)"
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
        build_report_from_json(args.json_file, args.output)
        print("✅ Relatório gerado com sucesso!"        return 0

    except Exception as e:
        logger.error(f"Erro ao gerar relatório: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
