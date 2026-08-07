"""Gera um relatório HTML a partir de uma resposta JSON validada."""

import argparse
from pathlib import Path

from picsafe_ai.api.schemas import AnalysisResponse
from picsafe_ai.reporting import HTMLReportGenerator
from picsafe_ai.utils.io import write_text


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Resposta JSON da API")
    parser.add_argument("output", type=Path, help="Destino HTML")
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    response = AnalysisResponse.model_validate_json(
        arguments.input.read_text(encoding="utf-8")
    )
    write_text(
        arguments.output,
        HTMLReportGenerator.generate_report(response),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
