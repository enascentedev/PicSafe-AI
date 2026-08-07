"""Anotação de imagens com bounding boxes das detecções."""

import logging
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from picsafe_ai.api.schemas import Detection

logger = logging.getLogger(__name__)


class ImageAnnotator:
    """Classe para anotação de imagens com detecções."""

    # Cores para cada classe (RGB)
    CLASS_COLORS = {
        "emergency_stop": (255, 0, 0),  # Vermelho
        "guard": (0, 255, 0),  # Verde
        "exposed_moving_part": (255, 165, 0),  # Laranja
        "danger_zone_opening": (255, 0, 255),  # Magenta
        "safety_sign": (0, 0, 255),  # Azul
    }

    @staticmethod
    def annotate_image(
        image_path: str, detections: list[Detection], output_path: str
    ) -> str:
        """
        Anota imagem com bounding boxes das detecções.

        Args:
            image_path: Caminho da imagem original.
            detections: Lista de detecções para anotar.
            output_path: Caminho onde salvar imagem anotada.

        Returns:
            Caminho da imagem anotada.
        """
        try:
            # Abrir imagem
            image = Image.open(image_path)
            draw = ImageDraw.Draw(image)

            # Tentar carregar fonte, usar default se falhar
            font: ImageFont.FreeTypeFont | ImageFont.ImageFont
            try:
                font = ImageFont.truetype("arial.ttf", 16)
            except OSError:
                font = ImageFont.load_default()

            # Filtrar detecções para esta imagem
            image_detections = [d for d in detections if d.image_path == image_path]

            for detection in image_detections:
                ImageAnnotator._draw_detection(draw, detection, image.size, font)

            # Salvar imagem anotada
            output_path_obj = Path(output_path)
            output_path_obj.parent.mkdir(parents=True, exist_ok=True)
            image.save(output_path_obj)

            logger.info(f"Imagem anotada salva em: {output_path}")
            return output_path

        except Exception as e:
            logger.exception(f"Erro ao anotar imagem {image_path}: {e}")
            return image_path

    @staticmethod
    def _draw_detection(
        draw: ImageDraw.ImageDraw,
        detection: Detection,
        image_size: tuple[int, int],
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ) -> None:
        """
        Desenha uma detecção na imagem.

        Args:
            draw: Objeto ImageDraw.
            detection: Detecção a ser desenhada.
            image_size: Tamanho da imagem (largura, altura).
            font: Fonte para texto.
        """
        img_width, img_height = image_size

        # Converter coordenadas normalizadas para pixels
        bbox = detection.bbox
        x_min = int(bbox.x_min * img_width)
        y_min = int(bbox.y_min * img_height)
        x_max = int(bbox.x_max * img_width)
        y_max = int(bbox.y_max * img_height)

        # Cor da classe
        color = ImageAnnotator.CLASS_COLORS.get(
            detection.class_name.value, (128, 128, 128)
        )

        # Desenhar retângulo
        draw.rectangle([x_min, y_min, x_max, y_max], outline=color, width=3)

        # Preparar texto
        confidence_pct = int(detection.confidence * 100)
        label = f"{detection.class_name.value} ({confidence_pct}%)"

        # Calcular tamanho do texto
        try:
            bbox_text = draw.textbbox((0, 0), label, font=font)
            text_width = bbox_text[2] - bbox_text[0]
            text_height = bbox_text[3] - bbox_text[1]
        except AttributeError:
            # Fallback para versões antigas do PIL
            text_width, text_height = draw.textsize(label, font=font)  # type: ignore[attr-defined]

        # Fundo do texto
        text_bg = [x_min, y_min - text_height - 4, x_min + text_width + 4, y_min]
        draw.rectangle(text_bg, fill=color)

        # Texto
        draw.text((x_min + 2, y_min - text_height - 2), label, fill="white", font=font)
