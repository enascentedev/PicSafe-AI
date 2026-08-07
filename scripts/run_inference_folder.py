"""Executa o detector configurado sobre uma pasta, sem expor nomes de arquivos."""

import argparse
import json
import sys
import uuid
from pathlib import Path

from picsafe_ai.checklist import RulesEngine
from picsafe_ai.config import settings
from picsafe_ai.vision import DetectorError, PostProcessor, build_detector

SUPPORTED_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp"}


def run_folder(folder: Path) -> dict[str, object]:
    """Retorna resultados com identificadores opacos e falhas declaradas."""
    detector = build_detector(settings)
    post_processor = PostProcessor(
        confidence_threshold=settings.confidence_threshold,
        nms_threshold=settings.nms_threshold,
    )
    detections = []
    errors: list[dict[str, str]] = []
    paths = sorted(
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_SUFFIXES
    )
    for path in paths:
        image_id = uuid.uuid4().hex
        try:
            detections.extend(detector.predict(path.read_bytes(), image_id))
        except DetectorError:
            errors.append(
                {
                    "image_id": image_id,
                    "code": "detector_error",
                    "message": "Não foi possível analisar esta imagem",
                }
            )
    processed = post_processor.process_detections(detections)
    checklist, pending = RulesEngine().apply_rules(processed, detector.metadata)
    return {
        "detector": detector.metadata.model_dump(mode="json"),
        "detections": [item.model_dump(mode="json") for item in processed],
        "checklist": [item.model_dump(mode="json") for item in checklist],
        "pending_photos": [item.model_dump(mode="json") for item in pending],
        "image_errors": errors,
    }


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> int:
    arguments = parse_arguments()
    result = json.dumps(run_folder(arguments.folder), ensure_ascii=False, indent=2)
    if arguments.output:
        arguments.output.write_text(result, encoding="utf-8")
    else:
        sys.stdout.write(f"{result}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
