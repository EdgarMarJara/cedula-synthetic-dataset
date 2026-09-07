"""Clase principal ``DominicanIDGenerator`` que integra todo el pipeline."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Optional

from PIL import Image

from .augmentation import AugmentationConfig, ImageAugmentor
from .data_generator import CedulaData, DominicanDataGenerator
from .renderer import IDRenderer
from .storage import StorageManager
from .templates import load_or_create_templates


def _center_on_canvas(image: Image.Image, margin: int) -> Image.Image:
    """Centra una cara de la cedula en un lienzo exterior uniforme."""
    if margin == 0:
        return image
    canvas = Image.new(
        "RGB",
        (image.width + margin * 2, image.height + margin * 2),
        (255, 255, 255),
    )
    offset = ((canvas.width - image.width) // 2, (canvas.height - image.height) // 2)
    canvas.paste(image, offset)
    return canvas


def _generate_placeholder_face(width: int = 260, height: int = 320, seed: Optional[int] = None) -> Image.Image:
    """Genera una "cara" sintética simple (silueta) cuando no se provee una foto real.

    Esto evita depender de datasets de rostros reales (con implicaciones de
    privacidad) manteniendo el pipeline de renderizado totalmente funcional.
    """
    rng = random.Random(seed)
    skin_tones = [(255, 224, 189), (241, 194, 125), (198, 134, 66), (141, 85, 36)]
    bg = rng.choice([(230, 230, 235), (220, 225, 230), (210, 215, 222)])
    skin = rng.choice(skin_tones)

    img = Image.new("RGB", (width, height), bg)
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    # Cabeza (óvalo) + hombros simples para simular una foto tipo carnet.
    draw.ellipse([width * 0.25, height * 0.12, width * 0.75, height * 0.62], fill=skin)
    draw.ellipse(
        [width * 0.05, height * 0.65, width * 0.95, height * 1.15],
        fill=skin,
    )
    return img


class DominicanIDGenerator:
    """Orquesta la generación de cédulas dominicanas sintéticas (anverso/reverso).

    Combina generación de datos (``DominicanDataGenerator``), renderizado
    sobre templates (``IDRenderer``), aumentación (``ImageAugmentor``) y
    almacenamiento con metadatos (``StorageManager``).
    """

    def __init__(
        self,
        output_dir: str = "synthetic_dataset",
        front_template_path: Optional[str] = None,
        back_template_path: Optional[str] = None,
        augmentation_config: Optional[AugmentationConfig] = None,
        seed: Optional[int] = None,
        canvas_margin: int = 48,
    ):
        if canvas_margin < 0:
            raise ValueError("canvas_margin debe ser mayor o igual a 0")
        self.front_template, self.back_template = load_or_create_templates(
            front_template_path, back_template_path
        )
        self.data_generator = DominicanDataGenerator(seed=seed)
        self.renderer = IDRenderer()
        self.augmentor = ImageAugmentor(config=augmentation_config, seed=seed)
        self.storage = StorageManager(output_dir)
        self._rng = random.Random(seed)
        self.canvas_margin = canvas_margin

    def generate_data(self) -> CedulaData:
        """Genera únicamente los datos sintéticos de una cédula."""
        return self.data_generator.generate()

    def render(
        self, data: CedulaData, face_photo: Optional[Image.Image] = None
    ) -> tuple[Image.Image, Image.Image]:
        """Renderiza el anverso y reverso a partir de datos (sin aumentación)."""
        if face_photo is None:
            face_photo = _generate_placeholder_face(seed=self._rng.random())
        front = self.renderer.render_front(self.front_template, data, face_photo)
        back = self.renderer.render_back(self.back_template, data)
        return (
            _center_on_canvas(front, self.canvas_margin),
            _center_on_canvas(back, self.canvas_margin),
        )

    def augment(self, image: Image.Image) -> Image.Image:
        """Aplica el pipeline de aumentación a una imagen ya renderizada."""
        return self.augmentor.apply(image)

    def generate_single(
        self, apply_augmentation: bool = True, face_photo: Optional[Image.Image] = None
    ) -> tuple[Image.Image, Image.Image, CedulaData]:
        """Genera un único par de imágenes (anverso/reverso) con sus datos."""
        data = self.generate_data()
        front, back = self.render(data, face_photo=face_photo)
        if apply_augmentation:
            front = self.augment(front)
            back = self.augment(back)
        return front, back, data

    def generate_batch(
        self,
        num_samples: int,
        apply_augmentation: bool = True,
        image_format: str = "jpg",
        progress_every: int = 100,
    ) -> str:
        """Genera ``num_samples`` cédulas sintéticas y guarda imágenes + metadatos CSV.

        Retorna la ruta al archivo CSV de metadatos generado.
        """
        if num_samples <= 0:
            raise ValueError("num_samples debe ser mayor que 0")

        for i in range(num_samples):
            front, back, data = self.generate_single(apply_augmentation=apply_augmentation)
            record = self.storage.save_sample(i, front, back, data, image_format=image_format)
            if not self.storage.validate_record(record):
                raise ValueError(f"Registro inválido generado para la muestra {i}: {record}")

            if progress_every and (i + 1) % progress_every == 0:
                print(f"Generadas {i + 1}/{num_samples} cédulas...")

        metadata_path = self.storage.write_metadata()
        print(f"Dataset completo: {num_samples} cédulas generadas en '{self.storage.output_dir}'")
        return str(metadata_path)
