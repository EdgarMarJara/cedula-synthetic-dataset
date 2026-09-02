"""Renderización de datos y foto sobre los templates de la cédula."""

from __future__ import annotations

from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .data_generator import CedulaData
from .templates import PHOTO_BOX

# Posiciones (x, y) de cada campo de texto sobre el template del anverso.
FRONT_FIELD_POSITIONS = {
    "cedula_number": (360, 150),
    "full_name": (360, 205),
    "address": (360, 260),
    "birth_date": (360, 340),
    "gender_label": (700, 340),
    "nationality": (360, 395),
    "marital_status": (700, 395),
    "profession": (360, 450),
    "issue_date": (360, 505),
    "expiration_date": (700, 505),
}

FRONT_FIELD_LABELS = {
    "cedula_number": "No. CÉDULA",
    "full_name": "NOMBRE COMPLETO",
    "address": "DOMICILIO",
    "birth_date": "FECHA DE NACIMIENTO",
    "gender_label": "SEXO",
    "nationality": "NACIONALIDAD",
    "marital_status": "ESTADO CIVIL",
    "profession": "OCUPACIÓN",
    "issue_date": "FECHA DE EXPEDICIÓN",
    "expiration_date": "FECHA DE VENCIMIENTO",
}

BACK_FIELD_POSITIONS = {
    "full_name": (40, 110),
    "cedula_number": (40, 150),
    "birth_date": (40, 190),
    "profession": (40, 230),
}

BACK_FIELD_LABELS = {
    "full_name": "NOMBRE",
    "cedula_number": "CÉDULA",
    "birth_date": "NACIMIENTO",
    "profession": "OCUPACIÓN",
}

MRZ_START_Y_OFFSET = 30  # Desde el tope de la franja MRZ del template.
MRZ_LINE_HEIGHT = 40

TEXT_COLOR = (20, 25, 30)
LABEL_COLOR = (90, 100, 110)


def _load_font(size: int, monospace: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        if monospace
        else [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
    )
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


class IDRenderer:
    """Coloca texto, foto y MRZ sobre los templates de anverso/reverso."""

    def __init__(self, label_font_size: int = 14, value_font_size: int = 20, mrz_font_size: int = 26):
        self.label_font = _load_font(label_font_size)
        self.value_font = _load_font(value_font_size)
        self.mrz_font = _load_font(mrz_font_size, monospace=True)

    def render_front(
        self,
        template: Image.Image,
        data: CedulaData,
        face_photo: Optional[Image.Image] = None,
    ) -> Image.Image:
        img = template.copy()
        draw = ImageDraw.Draw(img)

        field_values = {
            "cedula_number": data.cedula_number,
            "full_name": data.full_name,
            "address": data.address,
            "birth_date": data.birth_date.strftime("%d/%m/%Y"),
            "gender_label": data.gender_label,
            "nationality": data.nationality,
            "marital_status": data.marital_status,
            "profession": data.profession,
            "issue_date": data.issue_date.strftime("%d/%m/%Y"),
            "expiration_date": data.expiration_date.strftime("%d/%m/%Y"),
        }

        for key, (x, y) in FRONT_FIELD_POSITIONS.items():
            label = FRONT_FIELD_LABELS[key]
            draw.text((x, y - 16), label, fill=LABEL_COLOR, font=self.label_font)
            draw.text((x, y), field_values[key], fill=TEXT_COLOR, font=self.value_font)

        if face_photo is not None:
            img = self.paste_face_photo(img, face_photo)

        return img

    def paste_face_photo(self, img: Image.Image, face_photo: Image.Image) -> Image.Image:
        left, top, right, bottom = PHOTO_BOX
        box_w, box_h = right - left, bottom - top
        photo = face_photo.convert("RGB").resize((box_w, box_h))
        img.paste(photo, (left, top))
        return img

    def render_back(self, template: Image.Image, data: CedulaData) -> Image.Image:
        img = template.copy()
        draw = ImageDraw.Draw(img)

        field_values = {
            "full_name": data.full_name,
            "cedula_number": data.cedula_number,
            "birth_date": data.birth_date.strftime("%d/%m/%Y"),
            "profession": data.profession,
        }

        for key, (x, y) in BACK_FIELD_POSITIONS.items():
            label = BACK_FIELD_LABELS[key]
            draw.text((x, y - 16), label, fill=LABEL_COLOR, font=self.label_font)
            draw.text((x, y), field_values[key], fill=TEXT_COLOR, font=self.value_font)

        mrz_lines = [data.mrz_line1, data.mrz_line2, data.mrz_line3]
        mrz_top = img.height - 170 + MRZ_START_Y_OFFSET
        for i, line in enumerate(mrz_lines):
            draw.text((60, mrz_top + i * MRZ_LINE_HEIGHT), line, fill=TEXT_COLOR, font=self.mrz_font)

        return img
