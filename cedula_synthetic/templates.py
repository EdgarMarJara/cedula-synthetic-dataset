"""Creación y carga de templates (anverso/reverso) de la cédula dominicana.

No se distribuye ninguna imagen oficial de cédula real (por motivos legales y
de privacidad). En su lugar, este módulo genera de forma programática un
template genérico "tipo cédula" que reproduce la disposición general de
campos (foto, texto, franja MRZ) descrita en los requisitos. Si el usuario
dispone de un template propio (por ejemplo un diseño oficial en blanco), puede
usarlo pasando ``front_template_path`` / ``back_template_path`` al generador.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont, ImageOps

# Dimensiones estándar de una tarjeta ID-1 a 300 DPI aprox.
CARD_WIDTH = 1011
CARD_HEIGHT = 638

BACKGROUND_COLOR_FRONT = (248, 248, 245)
BACKGROUND_COLOR_BACK = (247, 248, 246)
ACCENT_COLOR = (18, 48, 83)
LINE_COLOR = (174, 195, 218)
PINK_SECURITY = (238, 180, 201)
BLUE_SECURITY = (182, 207, 232)
PINK_STAIN = (244, 194, 208)
PINK_STAIN_LIGHT = (249, 221, 228)

# Zonas (bounding boxes) usadas como referencia visual del template y también
# reutilizadas por el renderer para saber dónde colocar la foto.
PHOTO_BOX = (60, 140, 320, 460)
SHIELD_PATH = Path(__file__).resolve().parent.parent / "elementos" / "Escudo-nacional.png"
JCE_LOGO_PATH = Path(__file__).resolve().parent.parent / "elementos" / "Logo jce.png"


def _draw_placeholder_photo_box(draw: ImageDraw.ImageDraw) -> None:
    draw.rectangle(PHOTO_BOX, outline=LINE_COLOR, width=2, fill=BACKGROUND_COLOR_FRONT)


def _draw_security_background(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    for y in range(105, height, 48):
        primary_points = []
        secondary_points = []
        for x in range(0, width + 8, 8):
            wave = math.sin((x / 52) * math.tau) * 7
            primary_points.append((x, y + wave))
            secondary_points.append((x, y + 16 + wave))
        draw.line(primary_points, fill=BLUE_SECURITY, width=2)
        draw.line(secondary_points, fill=PINK_SECURITY, width=1)


def _draw_corner_stains(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    draw.ellipse((width - 290, -105, width + 115, 215), fill=PINK_STAIN_LIGHT)
    draw.ellipse((width - 250, -65, width + 75, 175), fill=PINK_STAIN)
    draw.ellipse((-115, height - 225, 290, height + 105), fill=PINK_STAIN_LIGHT)
    draw.ellipse((-75, height - 185, 250, height + 65), fill=PINK_STAIN)


def _paste_faded_monument(img: Image.Image, width: int) -> None:
    monument_path = Path(__file__).resolve().parent.parent / "elementos" / "monumento de la restauracion.png"
    if not monument_path.exists():
        return
    monument = Image.open(monument_path).convert("RGB")
    monument.thumbnail((300, 300), Image.Resampling.LANCZOS)
    grayscale = ImageOps.grayscale(monument)
    tinted = ImageOps.colorize(grayscale, (170, 55, 78), (255, 205, 216)).convert("RGBA")
    alpha = grayscale.point(lambda value: max(0, min(125, (value - 100) * 3)))
    tinted.putalpha(alpha)
    img.paste(tinted, (width - monument.width - 55, 32), tinted)


def _paste_faded_duarte(img: Image.Image, width: int, height: int) -> None:
    duarte_path = Path(__file__).resolve().parent.parent / "elementos" / "Juan Pablo Duarte.png"
    if not duarte_path.exists():
        return
    source = Image.open(duarte_path).convert("RGB")
    crop = source.crop((source.width // 10, source.height // 5, source.width * 6 // 10, source.height))
    crop.thumbnail((245, 245), Image.Resampling.LANCZOS)
    grayscale = ImageOps.grayscale(crop)
    tinted = ImageOps.colorize(grayscale, (32, 76, 145), (190, 215, 250)).convert("RGBA")
    alpha = grayscale.point(lambda value: max(0, min(125, (255 - value) // 2)))
    tinted.putalpha(alpha)
    img.paste(tinted, (width - tinted.width - 22, height - tinted.height - 38), tinted)


def _paste_blue_jce_logo(img: Image.Image) -> None:
    if not JCE_LOGO_PATH.exists():
        return
    logo = Image.open(JCE_LOGO_PATH).convert("RGB")
    logo.thumbnail((58, 82), Image.Resampling.LANCZOS)
    grayscale = ImageOps.grayscale(logo)
    tinted = ImageOps.colorize(grayscale, (25, 70, 125), (185, 215, 245)).convert("RGBA")
    tinted.putalpha(150)
    img.paste(tinted, (495 - tinted.width, 320), tinted)


def _header_fonts() -> tuple[ImageFont.FreeTypeFont, ImageFont.FreeTypeFont]:
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    regular_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try:
        return ImageFont.truetype(bold_path, 18), ImageFont.truetype(regular_path, 12)
    except OSError:
        return ImageFont.load_default(), ImageFont.load_default()


def _draw_header(draw: ImageDraw.ImageDraw, width: int, include_jce_logo: bool = False) -> None:
    bold_font, regular_font = _header_fonts()
    left_text = "REPUBLICA DOMINICANA"
    center_text = "JUNTA CENTRAL ELECTORAL"
    right_text = "CEDULA DE IDENTIDAD Y ELECTORAL"
    center_box = draw.textbbox((0, 0), center_text, font=regular_font)
    right_box = draw.textbbox((0, 0), right_text, font=bold_font)
    right_width = right_box[2] - right_box[0]
    if SHIELD_PATH.exists():
        shield = Image.open(SHIELD_PATH).convert("RGBA")
        shield.thumbnail((50, 50), Image.Resampling.LANCZOS)
        draw._image.paste(shield, (12, 9), shield)
    draw.text((68, 24), left_text, fill=ACCENT_COLOR, font=bold_font)
    center_width = center_box[2] - center_box[0]
    if include_jce_logo and JCE_LOGO_PATH.exists():
        logo = Image.open(JCE_LOGO_PATH).convert("RGB")
        logo.thumbnail((28, 48), Image.Resampling.LANCZOS)
        group_width = logo.width + 6 + center_width
        group_left = (width - group_width) / 2
        draw._image.paste(logo, (round(group_left), 9))
        draw.text((round(group_left + logo.width + 6), 28), center_text, fill=ACCENT_COLOR, font=regular_font)
        right_x = max(width - right_width - 18, round(group_left + group_width + 24))
    else:
        draw.text(((width - center_width) / 2, 28), center_text, fill=ACCENT_COLOR, font=regular_font)
        right_x = width - right_width - 18
    draw.text((right_x, 24), right_text, fill=ACCENT_COLOR, font=bold_font)


def create_front_template(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> Image.Image:
    """Crea un template sintético inspirado en una tarjeta dominicana ID-1."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR_FRONT)
    draw = ImageDraw.Draw(img)
    _draw_security_background(draw, width, height)
    _draw_corner_stains(draw, width, height)
    _paste_faded_duarte(img, width, height)

    _draw_header(draw, width, include_jce_logo=True)
    draw.text((width - 245, 25), "MUESTRA SINTETICA", fill=(151, 48, 78))
    draw.text((width - 150, 52), "ID-1", fill=ACCENT_COLOR)

    _draw_placeholder_photo_box(draw)

    draw.rounded_rectangle([0, height - 24, width - 1, height - 1], radius=8, fill=ACCENT_COLOR)
    draw.text((width - 290, height - 19), "DOCUMENTO FICTICIO", fill=(255, 255, 255))

    return img


def create_back_template(width: int = CARD_WIDTH, height: int = CARD_HEIGHT) -> Image.Image:
    """Crea el reverso sintético con zona QR, código de barras y MRZ."""
    img = Image.new("RGB", (width, height), BACKGROUND_COLOR_BACK)
    draw = ImageDraw.Draw(img)
    _draw_security_background(draw, width, height)
    _draw_corner_stains(draw, width, height)
    _paste_faded_monument(img, width)

    draw.rectangle([300, 105, 495, 290], fill=(252, 252, 249), outline=ACCENT_COLOR, width=2)
    for x in range(308, 488, 12):
        for y in range(113, 283, 12):
            if (x * 3 + y * 5) % 7 < 3:
                draw.rectangle([x, y, x + 7, y + 7], fill=ACCENT_COLOR)
    _paste_blue_jce_logo(img)

    # Franja MRZ (fondo claro monoespaciado) al pie de la tarjeta.
    mrz_top = height - 170
    draw.rectangle([0, mrz_top, width - 1, height - 1], fill=(250, 249, 246))
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
