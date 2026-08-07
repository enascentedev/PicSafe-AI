"""Renderização de bounding boxes por imagem opaca."""

from typing import ClassVar, cast

from PIL import Image, ImageDraw, ImageFont

from picsafe_ai.api.schemas import Detection


class ImageAnnotationError(RuntimeError):
    """Falha explícita ao produzir evidência anotada."""


class ImageAnnotator:
    """Anota somente detecções pertencentes à imagem informada."""

    CLASS_COLORS: ClassVar[dict[str, tuple[int, int, int]]] = {
        "emergency_stop": (220, 38, 38),
        "guard": (22, 163, 74),
        "exposed_moving_part": (234, 88, 12),
        "danger_zone_opening": (192, 38, 211),
        "safety_sign": (37, 99, 235),
    }

    @classmethod
    def annotate_image(
        cls,
        image_path: str,
        image_id: str,
        detections: list[Detection],
    ) -> Image.Image:
        """Retorna cópia RGB anotada sem persistir paths por conta própria."""
        try:
            with Image.open(image_path) as source:
                image = source.convert("RGB")
        except OSError as exc:
            message = "Não foi possível abrir a imagem validada para anotação"
            raise ImageAnnotationError(message) from exc

        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default()
        for detection in detections:
            if detection.image_id == image_id:
                cls._draw_detection(draw, detection, image.size, font)
        return cast("Image.Image", image)

    @classmethod
    def _draw_detection(
        cls,
        draw: ImageDraw.ImageDraw,
        detection: Detection,
        image_size: tuple[int, int],
        font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    ) -> None:
        width, height = image_size
        bbox = detection.bbox
        coordinates = (
            int(bbox.x_min * width),
            int(bbox.y_min * height),
            int(bbox.x_max * width),
            int(bbox.y_max * height),
        )
        color = cls.CLASS_COLORS[detection.class_name.value]
        draw.rectangle(coordinates, outline=color, width=3)
        label = f"{detection.class_name.value} ({detection.confidence:.2f})"
        text_box = draw.textbbox((coordinates[0], coordinates[1]), label, font=font)
        draw.rectangle(text_box, fill=color)
        draw.text(
            (coordinates[0], coordinates[1]),
            label,
            fill="white",
            font=font,
        )
