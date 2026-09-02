"""Creación y carga de templates (anverso/reverso) de la cédula dominicana.

No se distribuye ninguna imagen oficial de cédula real (por motivos legales y
de privacidad). En su lugar, este módulo genera de forma programática un
template genérico "tipo cédula" que reproduce la disposición general de
campos (foto, texto, franja MRZ) descrita en los requisitos. Si el usuario
dispone de un template propio (por ejemplo un diseño oficial en blanco), puede
usarlo pasando ``front_template_path`` / ``back_template_path`` al generador.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw

# Dimensiones estándar de una tarjeta ID-1 a 300 DPI aprox.
CARD_WIDTH = 1011
CARD_HEIGHT = 638

BACKGROUND_COLOR_FRONT = (235, 240, 245)
BACKGROUND_COLOR_BACK = (225, 230, 238)
ACCENT_COLOR = (20, 60, 120)
LINE_COLOR = (180, 190, 200)

# Zonas (bounding boxes) usadas como referencia visual del template y también
# reutilizadas por el renderer para saber dónde colocar la foto.
PHOTO_BOX = (60, 140, 320, 460)


def _draw_placeholder_photo_box(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle(PHOTO_BOX, outline=ACCENT_COLOR, width=3, fill=(210, 214, 218))


def create_front_template(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> Image.Image:
    """Crea un template genérico para el anverso de la cédula."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR_FRONT)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width - 1, 90], fill=ACCENT_COLOR)
    draw.text((30, 25), "REPÚBLICA DOMINICANA", fill=(255, 255, 255))
    draw.text((30, 55), "CÉDULA DE IDENTIDAD Y ELECTORAL", fill=(255, 255, 255))

    _draw_placeholder_photo_box(draw)

    for y in range(140, height - 40, 55):
        draw.line([(360, y + 40), (width - 40, y + 40)], fill=LINE_COLOR, width=1)

    draw.rectangle([0, height - 4, width - 1, height - 1], fill=ACCENT_COLOR)
    return img


def create_back_template(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> Image.Image:
    """Crea un template genérico para el reverso de la cédula (con franja MRZ)."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR_BACK)
    draw = ImageDraw.Draw(img)

    draw.rectangle([0, 0, width - 1, 60], fill=ACCENT_COLOR)
    draw.text((30, 18), "INFORMACIÓN ADICIONAL", fill=(255, 255, 255))

    for y in range(90, height - 200, 40):
        draw.line([(40, y), (width - 40, y)], fill=LINE_COLOR, width=1)

    # Franja MRZ (fondo claro monoespaciado) al pie de la tarjeta.
    mrz_top = height - 170
    draw.rectangle([0, mrz_top, width - 1, height - 1], fill=(245, 245, 245))
    draw.line([(0, mrz_top), (width - 1, mrz_top)], fill=ACCENT_COLOR, width=2)

    return img


def load_or_create_templates(
    front_template_path: Optional[str] = None,
    back_template_path: Optional[str] = None,
) -> tuple[Image.Image, Image.Image]:
    """Carga templates desde disco si se proveen rutas, o crea unos genéricos."""
    if front_template_path:
        front = Image.open(front_template_path).convert("RGB")
    else:
        front = create_front_template()

    if back_template_path:
        back = Image.open(back_template_path).convert("RGB")
    else:
        back = create_back_template()

    return front, back


def save_default_templates(output_dir: str) -> tuple[Path, Path]:
    """Genera y guarda los templates por defecto en ``output_dir``."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    front_path = out / "cedula_front_template.png"
    back_path = out / "cedula_back_template.png"
    create_front_template().save(front_path)
    create_back_template().save(back_path)
    return front_path, back_path
