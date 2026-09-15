"""Renderización de datos y foto sobre los templates de la cédula brasileña."""

from __future__ import annotations

from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .brasil_data_generator import BrazilCedulaData
from .brasil_template import (
    BACK_FIELD_POSITIONS,
    BACK_VALUE_OFFSET,
    FRONT_FIELD_POSITIONS,
    FRONT_VALUE_OFFSET,
    MRZ_LINE_HEIGHT,
    MRZ_TOP,
    PHOTO_BOX,
)

TEXT_COLOR = (20, 20, 20)


def _load_font(size: int, bold: bool = False, monospace: bool = False) -> ImageFont.FreeTypeFont:
    if monospace:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"]
    elif bold:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    else:
        candidates = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def _fit_font(text: str, max_width: int, size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Reduce el tamaño solo cuando un valor largo no cabe en su columna."""
    while size > 10:
        font = _load_font(size, bold=bold)
        if font.getbbox(text)[2] <= max_width:
            return font
        size -= 1
    return _load_font(10, bold=bold)


class BrazilIDRenderer:
    """Coloca texto, foto y MRZ sobre los templates de la cédula brasileña."""

    def __init__(self, value_font_size: int = 17, mrz_font_size: int = 28):
        self.value_font_size = value_font_size
        self.mrz_font_size = mrz_font_size

    def render_front(
        self,
        template: Image.Image,
        data: BrazilCedulaData,
        face_photo: Optional[Image.Image] = None,
    ) -> Image.Image:
        img = template.copy()
        draw = ImageDraw.Draw(img)

        field_values = {
            "full_name": data.full_name,
            "social_name": data.social_name,
            "registro_geral": data.registro_geral,
            "sexo": data.gender_label,
            "birth_date": data.birth_date.strftime("%d / %m / %Y"),
            "nationality": data.nationality,
            "birth_place": data.birth_place,
            "expiration_date": data.expiration_date.strftime("%d / %m / %Y"),
        }

        for key, (x, y) in FRONT_FIELD_POSITIONS.items():
            value = field_values[key]
            max_width = 330 if key in {"sexo", "nationality", "expiration_date"} else 340
            font = _fit_font(value, max_width, self.value_font_size)
            draw.text((x, y + FRONT_VALUE_OFFSET), value, fill=TEXT_COLOR, font=font)

        if face_photo is not None:
            self.paste_face_photo(img, face_photo)

        return img

    def paste_face_photo(self, img: Image.Image, face_photo: Image.Image) -> Image.Image:
        left, top, right, bottom = PHOTO_BOX
        box_w, box_h = right - left, bottom - top
        photo = face_photo.convert("RGB").resize((box_w - 6, box_h - 6))
        img.paste(photo, (left + 3, top + 3))
        return img

    def render_back(self, template: Image.Image, data: BrazilCedulaData) -> Image.Image:
        img = template.copy()
        draw = ImageDraw.Draw(img)

        field_values = {
            "filiation": f"{data.father_name} / {data.mother_name}",
            "issuer": data.issuer_organ,
            "issue_place": data.issue_place,
            "issue_date": data.issue_date.strftime("%d / %m / %Y"),
        }

        for key, (x, y) in BACK_FIELD_POSITIONS.items():
            value = field_values[key]
            max_width = 570 if key == "filiation" else 240
            font = _fit_font(value, max_width, 10, bold=True)
            draw.text((x, y + BACK_VALUE_OFFSET), value, fill=TEXT_COLOR, font=font)

        mrz_lines = [data.mrz_line1, data.mrz_line2, data.mrz_line3]
        mrz_font = _load_font(self.mrz_font_size, bold=True, monospace=True)
        for i, line in enumerate(mrz_lines):
            draw.text((50, MRZ_TOP + i * MRZ_LINE_HEIGHT), line, fill=TEXT_COLOR, font=mrz_font)

        return img
