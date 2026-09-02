"""Renderización de datos y foto sobre los templates de la cédula."""

from __future__ import annotations

from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from .data_generator import CedulaData
from .templates import ACCENT_COLOR, PHOTO_BOX

# Posiciones (x, y) de cada campo de texto sobre el template del anverso.
FRONT_FIELD_POSITIONS = {
    "first_name": (380, 235),
    "last_name": (380, 275),
    "nationality": (380, 315),
    "birth_date": (380, 365),
    "birth_place": (380, 415),
    "profession": (380, 465),
    "issue_date": (380, 505),
    "expiration_date": (380, 545),
    "signature": (380, 615),
}

FRONT_FIELD_LABELS = {
    "first_name": "NOMBRE",
    "last_name": "APELLIDO",
    "nationality": "NACIONALIDAD",
    "birth_date": "FECHA DE NACIMIENTO",
    "birth_place": "LUGAR DE NACIMIENTO",
    "profession": "OCUPACIÓN",
    "issue_date": "FECHA DE EXPEDICIÓN",
    "expiration_date": "FECHA DE VENCIMIENTO",
    "signature": "FIRMA",
}

BACK_FIELD_POSITIONS = {
    "previous_cedula_number": (60, 110),
    "birth_registration": (60, 255),
    "electoral_college": (505, 110),
    "college_location": (505, 170),
    "residence_address": (505, 230),
    "municipality": (505, 290),
}

BACK_FIELD_LABELS = {
    "previous_cedula_number": "CÉDULA ANTERIOR",
    "electoral_college": "COLEGIO ELECTORAL",
    "college_location": "UBICACIÓN DEL COLEGIO",
    "residence_address": "DIRECCIÓN DE RESIDENCIA",
    "municipality": "MUNICIPIO",
    "birth_registration": "REGISTRO DE NACIMIENTO",
}

MRZ_START_Y_OFFSET = 10  # Desde el tope de la franja MRZ del template.
MRZ_LINE_HEIGHT = 46

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


def _fit_font(text: str, max_width: int, size: int) -> ImageFont.FreeTypeFont:
    """Reduce el tamano solo cuando un valor largo no cabe en su columna."""
    while size > 10:
        font = _load_font(size)
        if font.getbbox(text)[2] <= max_width:
            return font
        size -= 1
    return _load_font(10)


def _fit_mrz_font(text: str, max_width: int) -> ImageFont.FreeTypeFont:
    for size in range(52, 15, -1):
        font = _load_font(size, monospace=True)
        if font.getbbox(text)[2] <= max_width:
            return font
    return _load_font(16, monospace=True)


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
            "first_name": data.first_name,
            "last_name": data.last_name,
            "birth_place": data.birth_place,
            "birth_date": data.birth_date.strftime("%d/%m/%Y"),
            "nationality": data.nationality,
            "profession": data.profession,
            "issue_date": data.issue_date.strftime("%d/%m/%Y"),
            "expiration_date": data.expiration_date.strftime("%d/%m/%Y"),
            "signature": data.signature,
        }

        number_label = "NUMERO DE CEDULA"
        number_font = _fit_font(data.cedula_number, 430, 30)
        draw.text((380, 124), number_label, fill=LABEL_COLOR, font=self.label_font)
        draw.text((380, 145), data.cedula_number, fill=TEXT_COLOR, font=number_font)

        for key, (x, y) in FRONT_FIELD_POSITIONS.items():
            label = FRONT_FIELD_LABELS[key]
            if key in {"signature", "expiration_date"}:
                continue
            max_width = 540 if key in {"first_name", "last_name", "birth_place"} else 270
            value_font = _fit_font(field_values[key], max_width, self.value_font.size)
            draw.text((x, y - 16), label, fill=LABEL_COLOR, font=self.label_font)
            draw.text((x, y), field_values[key], fill=TEXT_COLOR, font=value_font)

        image_data_start_x = 60
        draw.text((image_data_start_x, 520), FRONT_FIELD_LABELS["signature"], fill=LABEL_COLOR, font=self.label_font)
        validity_text = f"VIGENCIA HASTA {field_values['expiration_date']}"
        validity_font = _fit_font(validity_text, 300, self.value_font.size)
        draw.text((image_data_start_x, 545), validity_text, fill=TEXT_COLOR, font=validity_font)

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
            "previous_cedula_number": data.previous_cedula_number,
            "electoral_college": data.electoral_college,
            "college_location": data.college_location,
            "residence_address": data.residence_address,
            "municipality": data.municipality,
            "birth_registration": data.birth_registration,
        }

        for key, (x, y) in BACK_FIELD_POSITIONS.items():
            label = BACK_FIELD_LABELS[key]
            draw.text((x, y - 16), label, fill=LABEL_COLOR, font=self.label_font)
            max_width = 220 if key in {"previous_cedula_number", "birth_registration"} else 330
            value_font = _fit_font(field_values[key], max_width, self.value_font.size)
            draw.text((x, y), field_values[key], fill=TEXT_COLOR, font=value_font)

        self._draw_side_barcode(draw, data.cedula_number, img.width)

        mrz_lines = [data.mrz_line1, data.mrz_line2, data.mrz_line3]
        mrz_top = img.height - 170 + MRZ_START_Y_OFFSET
        for i, line in enumerate(mrz_lines):
            self._draw_stretched_mrz_line(img, line, mrz_top + i * MRZ_LINE_HEIGHT)

        return img

    @staticmethod
    def _draw_stretched_mrz_line(img: Image.Image, line: str, top: int) -> None:
        font = _load_font(26, monospace=True)
        bbox = font.getbbox(line)
        source = Image.new("RGB", (bbox[2] - bbox[0] + 4, 32), (250, 249, 246))
        source_draw = ImageDraw.Draw(source)
        source_draw.text((2 - bbox[0], -bbox[1]), line, fill=TEXT_COLOR, font=font)
        source = source.resize((img.width - 32, 32), Image.Resampling.LANCZOS)
        img.paste(source, (16, top))

    @staticmethod
    def _draw_bottom_barcode(
        draw: ImageDraw.ImageDraw, value: str, width: int, height: int
    ) -> None:
        """Dibuja una barra sintética horizontal de ancho completo."""
        left = 16
        right = width - 16
        top = height - 40
        bottom = height - 8
        draw.rectangle((left, top, right, bottom), fill=(250, 249, 246))
        pattern = "1011"
        for character in value:
            pattern += format(ord(character), "08b") + "10"
        pattern += "1101"
        usable_width = right - left
        for index, bit in enumerate(pattern):
            bar_left = left + (index * usable_width // len(pattern))
            bar_right = left + ((index + 1) * usable_width // len(pattern)) - 1
            if bit == "1":
                draw.rectangle((bar_left, top, bar_right, bottom), fill=TEXT_COLOR)

    @staticmethod
    def _draw_side_barcode(
        draw: ImageDraw.ImageDraw, value: str, width: int
    ) -> None:
        """Dibuja un código de barras sintético vertical junto al monumento."""
        frame_margin = 10
        left = width - 65
        right = width - 15
        top = 92
        bottom = 350
        draw.rectangle(
            (left - frame_margin, top - frame_margin, right + frame_margin, bottom + frame_margin),
            fill=(250, 249, 246),
            outline=ACCENT_COLOR,
            width=3,
        )
        pattern = "1011"
        for character in value:
            pattern += format(ord(character), "08b") + "10"
        pattern += "1101"
        usable_height = bottom - top
        for index, bit in enumerate(pattern):
            bar_top = top + (index * usable_height // len(pattern))
            bar_bottom = top + ((index + 1) * usable_height // len(pattern)) - 1
            if bit == "1":
                draw.rectangle((left, bar_top, right, bar_bottom), fill=ACCENT_COLOR)
