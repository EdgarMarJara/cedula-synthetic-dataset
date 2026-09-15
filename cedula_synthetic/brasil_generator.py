"""Clase ``BrazilIDGenerator`` que integra el pipeline para la cédula BR."""

from __future__ import annotations

import random
from typing import Optional

from PIL import Image

from .augmentation import AugmentationConfig, ImageAugmentor
from .brasil_data_generator import BrazilCedulaData, BrazilDataGenerator
from .brasil_renderer import BrazilIDRenderer
from .brasil_template import create_brazil_back_template, create_brazil_front_template
from .generator import _center_on_canvas, _generate_placeholder_face
from .storage import BRAZIL_METADATA_FIELDS, StorageManager


class BrazilIDGenerator:
    """Orquesta la generación de cédulas brasileñas sintéticas (frente/dorso).

    Combina generación de datos (``BrazilDataGenerator``), renderizado sobre
    el template (``BrazilIDRenderer``), aumentación (``ImageAugmentor``) y
    almacenamiento con metadatos (``StorageManager``).
    """

    def __init__(
        self,
        output_dir: str = "synthetic_dataset_br",
        augmentation_config: Optional[AugmentationConfig] = None,
        seed: Optional[int] = None,
        canvas_margin: int = 48,
    ):
        if canvas_margin < 0:
            raise ValueError("canvas_margin debe ser mayor o igual a 0")
        self.front_template = create_brazil_front_template()
        self.back_template = create_brazil_back_template()
        self.data_generator = BrazilDataGenerator(seed=seed)
        self.renderer = BrazilIDRenderer()
        self.augmentor = ImageAugmentor(config=augmentation_config, seed=seed)
        self.storage = StorageManager(output_dir, metadata_fields=BRAZIL_METADATA_FIELDS)
        self._rng = random.Random(seed)
        self.canvas_margin = canvas_margin

    def generate_data(self) -> BrazilCedulaData:
        """Genera únicamente los datos sintéticos de una cédula."""
        return self.data_generator.generate()

    def render(
        self, data: BrazilCedulaData, face_photo: Optional[Image.Image] = None
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
    ) -> tuple[Image.Image, Image.Image, BrazilCedulaData]:
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
