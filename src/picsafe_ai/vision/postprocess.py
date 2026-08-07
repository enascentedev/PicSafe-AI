"""Pós-processamento isolado por imagem e classe."""

from collections import defaultdict

from picsafe_ai.api.schemas import Detection


class PostProcessor:
    """Aplica limiar e NMS sem cruzar imagens distintas."""

    def __init__(self, *, confidence_threshold: float, nms_threshold: float) -> None:
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold

    def process_detections(self, detections: list[Detection]) -> list[Detection]:
        """Filtra detecções e aplica NMS em grupos independentes."""
        eligible = [
            detection
            for detection in detections
            if detection.confidence >= self.confidence_threshold
        ]
        grouped: dict[tuple[str, str], list[Detection]] = defaultdict(list)
        for detection in eligible:
            key = (detection.image_id, detection.class_name.value)
            grouped[key].append(detection)

        processed: list[Detection] = []
        for group in grouped.values():
            kept: list[Detection] = []
            for detection in sorted(
                group,
                key=lambda item: item.confidence,
                reverse=True,
            ):
                if all(
                    self.calculate_iou(detection, current) <= self.nms_threshold
                    for current in kept
                ):
                    kept.append(detection)
            processed.extend(kept)
        return processed

    @staticmethod
    def calculate_iou(first: Detection, second: Detection) -> float:
        """Calcula intersection over union entre duas detecções."""
        if first.image_id != second.image_id:
            return 0.0
        x_left = max(first.bbox.x_min, second.bbox.x_min)
        y_top = max(first.bbox.y_min, second.bbox.y_min)
        x_right = min(first.bbox.x_max, second.bbox.x_max)
        y_bottom = min(first.bbox.y_max, second.bbox.y_max)
        if x_right <= x_left or y_bottom <= y_top:
            return 0.0
        intersection = (x_right - x_left) * (y_bottom - y_top)
        first_area = (first.bbox.x_max - first.bbox.x_min) * (
            first.bbox.y_max - first.bbox.y_min
        )
        second_area = (second.bbox.x_max - second.bbox.x_min) * (
            second.bbox.y_max - second.bbox.y_min
        )
        union = first_area + second_area - intersection
        return intersection / union if union > 0 else 0.0
