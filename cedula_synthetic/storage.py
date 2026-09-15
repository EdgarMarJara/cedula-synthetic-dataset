"""Gestión de almacenamiento de imágenes y metadatos generados en batch."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Optional

from PIL import Image

from .data_generator import CedulaData

METADATA_FIELDS = [
    "id",
    "front_image",
    "back_image",
    "cedula_number",
    "previous_cedula_number",
    "full_name",
    "gender_code",
    "gender_label",
    "blood_group",
    "birth_date",
    "nationality",
    "marital_status",
    "profession",
    "address",
    "province",
    "residence_address",
    "municipality",
    "electoral_college",
    "college_location",
    "birth_registration",
    "issue_date",
    "expiration_date",
    "mrz_line1",
    "mrz_line2",
    "mrz_line3",
]

BRAZIL_METADATA_FIELDS = [
    "id",
    "front_image",
    "back_image",
    "registro_geral",
    "full_name",
    "social_name",
    "gender_code",
    "gender_label",
    "birth_date",
    "birth_place",
    "nationality",
    "father_name",
    "mother_name",
    "issuer_organ",
    "issue_place",
    "issue_date",
    "expiration_date",
    "mrz_line1",
    "mrz_line2",
    "mrz_line3",
]


class StorageManager:
    """Guarda las imágenes generadas y un CSV con los metadatos asociados."""

    metadata_fields: list[str] = METADATA_FIELDS

    def __init__(
        self,
        output_dir: str,
        metadata_filename: str = "metadata.csv",
        metadata_fields: Optional[list[str]] = None,
    ):
        self.output_dir = Path(output_dir)
        self.front_dir = self.output_dir / "front"
        self.back_dir = self.output_dir / "back"
        self.metadata_path = self.output_dir / metadata_filename
        self.metadata_fields = metadata_fields or METADATA_FIELDS
        self._records: list[dict] = []

        self.front_dir.mkdir(parents=True, exist_ok=True)
        self.back_dir.mkdir(parents=True, exist_ok=True)

    def save_sample(
        self,
        sample_id: int,
        front_image: Image.Image,
        back_image: Image.Image,
        data: CedulaData,
        image_format: str = "jpg",
    ) -> dict:
        """Guarda un par de imágenes (anverso/reverso) y registra sus metadatos."""
        front_name = f"cedula_{sample_id:06d}_front.{image_format}"
        back_name = f"cedula_{sample_id:06d}_back.{image_format}"

        front_path = self.front_dir / front_name
        back_path = self.back_dir / back_name

        front_image.convert("RGB").save(front_path, quality=95)
        back_image.convert("RGB").save(back_path, quality=95)

        record = {
            "id": sample_id,
            "front_image": str(front_path.relative_to(self.output_dir)),
            "back_image": str(back_path.relative_to(self.output_dir)),
            **data.to_dict(),
        }
        self._records.append(record)
        return record

    def validate_record(self, record: dict) -> bool:
        """Valida que un registro contenga todos los campos requeridos y no vacíos."""
        for field_name in self.metadata_fields:
            if field_name not in record:
                return False
            value = record[field_name]
            if value is None or (isinstance(value, str) and not value.strip()):
                return False
        return True

    def write_metadata(self) -> Path:
        """Escribe todos los registros acumulados en el CSV de metadatos."""
        with open(self.metadata_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.metadata_fields)
            writer.writeheader()
            for record in self._records:
                writer.writerow({key: record.get(key, "") for key in self.metadata_fields})
        return self.metadata_path

    @property
    def records(self) -> Iterable[dict]:
        return list(self._records)
