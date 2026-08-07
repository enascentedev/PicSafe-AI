"""Pós-processamento das detecções de visão computacional."""

import logging

from picsafe_ai.api.schemas import Detection, DetectionClass
from picsafe_ai.config import settings

logger = logging.getLogger(__name__)


class PostProcessor:
    """Classe para pós-processamento de detecções."""

    def __init__(self) -> None:
        """Inicializa o pós-processador."""
        self.nms_threshold = settings.nms_threshold
        self.confidence_threshold = settings.confidence_threshold

    def process_detections(self, detections: list[Detection]) -> list[Detection]:
        """
        Aplica pós-processamento às detecções.

        Args:
            detections: Lista de detecções brutas.

        Returns:
            Lista de detecções processadas.
        """
        if not detections:
            return detections

        # Aplicar Non-Maximum Suppression (NMS)
        detections = self._apply_nms(detections)

        # Filtrar por confiança
        detections = self._filter_by_confidence(detections)

        # Mesclar detecções similares
        detections = self._merge_similar_detections(detections)

        logger.info(
            f"Pós-processamento aplicado: {len(detections)} detecções restantes"
        )
        return detections

    def _apply_nms(self, detections: list[Detection]) -> list[Detection]:
        """
        Aplica Non-Maximum Suppression para remover detecções sobrepostas.

        Args:
            detections: Lista de detecções.

        Returns:
            Lista filtrada após NMS.
        """
        if len(detections) <= 1:
            return detections

        # Agrupar por classe
        detections_by_class: dict[DetectionClass, list[Detection]] = {}
        for detection in detections:
            class_name = detection.class_name
            if class_name not in detections_by_class:
                detections_by_class[class_name] = []
            detections_by_class[class_name].append(detection)

        filtered_detections = []

        for class_detections in detections_by_class.values():
            # Ordenar por confiança (decrescente)
            class_detections.sort(key=lambda x: x.confidence, reverse=True)

            kept_detections: list[Detection] = []

            for detection in class_detections:
                should_keep = True

                # Verificar overlap com detecções já mantidas
                for kept in kept_detections:
                    if self._calculate_iou(detection, kept) > self.nms_threshold:
                        should_keep = False
                        break

                if should_keep:
                    kept_detections.append(detection)

            filtered_detections.extend(kept_detections)

        return filtered_detections

    def _filter_by_confidence(self, detections: list[Detection]) -> list[Detection]:
        """
        Filtra detecções por threshold de confiança.

        Args:
            detections: Lista de detecções.

        Returns:
            Lista filtrada por confiança.
        """
        return [d for d in detections if d.confidence >= self.confidence_threshold]

    def _merge_similar_detections(self, detections: list[Detection]) -> list[Detection]:
        """
        Mescla detecções similares da mesma classe.

        Args:
            detections: Lista de detecções.

        Returns:
            Lista com detecções mescladas.
        """
        # Por simplicidade, manter como está por enquanto
        # TODO: Implementar merge inteligente baseado em proximidade
        return detections

    def _calculate_iou(self, detection1: Detection, detection2: Detection) -> float:
        """
        Calcula Intersection over Union (IoU) entre duas detecções.

        Args:
            detection1: Primeira detecção.
            detection2: Segunda detecção.

        Returns:
            Valor do IoU (0-1).
        """
        bbox1 = detection1.bbox
        bbox2 = detection2.bbox

        # Calcular coordenadas da interseção
        x_left = max(bbox1.x_min, bbox2.x_min)
        y_top = max(bbox1.y_min, bbox2.y_min)
        x_right = min(bbox1.x_max, bbox2.x_max)
        y_bottom = min(bbox1.y_max, bbox2.y_max)

        if x_right <= x_left or y_bottom <= y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)

        # Calcular áreas individuais
        bbox1_area = (bbox1.x_max - bbox1.x_min) * (bbox1.y_max - bbox1.y_min)
        bbox2_area = (bbox2.x_max - bbox2.x_min) * (bbox2.y_max - bbox2.y_min)

        union_area = bbox1_area + bbox2_area - intersection_area

        return intersection_area / union_area if union_area > 0 else 0.0
