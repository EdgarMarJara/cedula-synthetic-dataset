"""Template sintético inspirado en la cédula brasileña (frente y dorso).

Este módulo se basa en la referencia visual de la imagen BR cortada en dos
mitades, y genera un template limpio para servir como base del pipeline de
generación sintética. Se mantiene en un formato simple y determinista para
poder ajustarse manualmente más adelante.
"""

from __future__ import annotations

import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

CARD_WIDTH = 900
CARD_HEIGHT = 500
BG = (250, 250, 250)
BORDER = (200, 200, 200)
BLUE = (8, 97, 54)
GREEN = (0, 120, 70)
TEXT = (20, 20, 20)
LIGHT = (235, 235, 235)
HEADER_GREEN = (8, 97, 54)

# Semilla fija para que las texturas de fondo sean deterministas entre corridas.
_TEXTURE_SEED = 20240517

# Caja de la foto, alineada con el texto de la derecha ("Nome").
PHOTO_BOX = (20, 170, 225, 365)

# Posiciones (x, y) de las etiquetas de cada campo del anverso; el valor se
# dibuja justo debajo, en ``y + FRONT_VALUE_OFFSET``.
FRONT_VALUE_OFFSET = 16
FRONT_FIELD_POSITIONS = {
    "full_name": (260, 170),
    "social_name": (260, 208),
    "registro_geral": (260, 254),
    "sexo": (610, 254),
    "birth_date": (260, 306),
    "nationality": (610, 306),
    "birth_place": (260, 358),
    "expiration_date": (610, 358),
}
FRONT_FIELD_LABELS = {
    "full_name": "Nome / Name",
    "social_name": "Nome Social / Social Name",
    "registro_geral": "Registro Geral - CPF / Personal Number",
    "sexo": "Sexo / Sex",
    "birth_date": "Data de Nascimento / Date of Birth",
    "nationality": "Nacionalidade / Nationality",
    "birth_place": "Naturalidade / Place of Birth",
    "expiration_date": "Data de Validade / Date of Expiry",
}

# Posiciones (x, y) de las etiquetas de cada campo del dorso.
BACK_VALUE_OFFSET = 20
BACK_FIELD_POSITIONS = {
    "filiation": (270, 90),
    "issuer": (270, 170),
    "issue_place": (270, 250),
    "issue_date": (650, 250),
}
BACK_FIELD_LABELS = {
    "filiation": "Filiação / Filiation",
    "issuer": "Órgão Expedidor / Card Issuer",
    "issue_place": "Local / Place of Issue",
    "issue_date": "Data de Emissão / Issue Date",
}

# Posición y alto de línea de la franja MRZ (3 líneas) del dorso.
MRZ_TOP = 382
MRZ_LINE_HEIGHT = 28

# Manchas amarillentas: reciben una textura de piedra (moteado irregular).
_YELLOW_SHAPES = [
    ([(0, 24), (112, 0), (196, 0), (170, 68), (78, 94), (0, 80)], (242, 215, 88, 95)),
    ([(492, 0), (650, 0), (704, 72), (638, 122), (536, 88)], (242, 220, 104, 105)),
    ([(244, 112), (338, 92), (436, 132), (414, 228), (302, 210), (228, 168)], (246, 218, 93, 90)),
    ([(820, 146), (900, 116), (900, 276), (842, 248), (772, 214)], (242, 215, 86, 100)),
    ([(28, 286), (116, 238), (236, 274), (222, 380), (112, 402), (0, 354)], (239, 216, 91, 95)),
    ([(616, 254), (724, 226), (824, 292), (794, 386), (686, 402), (590, 338)], (239, 216, 91, 95)),
    ([(266, 414), (382, 384), (478, 428), (504, 500), (292, 500)], (244, 220, 98, 90)),
]

# Manchas celestes/azul verdosas: reciben un efecto de puntillismo.
_BLUE_SHAPES = [
    ([(220, 0), (360, 0), (402, 52), (342, 108), (244, 82)], (53, 161, 146, 80)),
    ([(760, 0), (900, 0), (900, 104), (840, 132), (754, 76)], (43, 145, 137, 70)),
    ([(0, 128), (92, 98), (182, 130), (152, 220), (46, 246), (0, 210)], (42, 151, 143, 85)),
    ([(520, 120), (612, 96), (734, 150), (688, 238), (574, 226), (500, 180)], (47, 157, 146, 75)),
    ([(300, 252), (402, 224), (504, 278), (468, 382), (354, 396), (274, 334)], (44, 148, 140, 80)),
    ([(0, 430), (102, 386), (194, 426), (174, 500), (0, 500)], (44, 148, 140, 75)),
    ([(600, 412), (704, 384), (820, 428), (900, 410), (900, 500), (650, 500)], (44, 148, 140, 75)),
]


def _shapes_mask(size: tuple[int, int], shapes: list) -> Image.Image:
    """Construye una máscara "L" con la unión de los polígonos indicados."""
    mask = Image.new("L", size, 0)
    mask_draw = ImageDraw.Draw(mask)
    for points, _ in shapes:
        mask_draw.polygon(points, fill=255)
    return mask


def _apply_pointillism(img: Image.Image, shapes: list) -> None:
    """Salpica puntos pequeños y claros sobre las zonas celestes (efecto puntillismo)."""
    mask = _shapes_mask(img.size, shapes)
    bbox = mask.getbbox()
    if bbox is None:
        return

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    rng = random.Random(_TEXTURE_SEED)
    palette = [(150, 205, 214), (120, 190, 200), (170, 214, 220), (100, 175, 188)]

    min_x, min_y, max_x, max_y = bbox
    for y in range(min_y, max_y, 5):
        for x in range(min_x, max_x, 5):
            jitter_x = x + rng.randint(-2, 2)
            jitter_y = y + rng.randint(-2, 2)
            if 0 <= jitter_x < img.width and 0 <= jitter_y < img.height and mask.getpixel((jitter_x, jitter_y)):
                color = rng.choice(palette)
                radius = rng.choice((1, 1, 2))
                overlay_draw.ellipse(
                    (jitter_x - radius, jitter_y - radius, jitter_x + radius, jitter_y + radius),
                    fill=(*color, 65),
                )
    img.paste(overlay, (0, 0), overlay.getchannel("A"))


def _apply_stone_texture(img: Image.Image, shapes: list) -> None:
    """Añade un veteado tipo piedra (manchas irregulares suaves) sobre las zonas amarillentas."""
    mask = _shapes_mask(img.size, shapes)
    bbox = mask.getbbox()
    if bbox is None:
        return

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    rng = random.Random(_TEXTURE_SEED + 1)
    palette = [(214, 196, 150), (222, 206, 168), (198, 182, 132), (232, 214, 176)]

    min_x, min_y, max_x, max_y = bbox
    step = 9
    for y in range(min_y, max_y, step):
        for x in range(min_x, max_x, step):
            if mask.getpixel((x, y)):
                color = rng.choice(palette)
                width = rng.randint(4, 9)
                height = rng.randint(3, 7)
                offset_x = rng.randint(-3, 3)
                offset_y = rng.randint(-3, 3)
                overlay_draw.ellipse(
                    (x + offset_x, y + offset_y, x + offset_x + width, y + offset_y + height),
                    fill=(*color, 45),
                )
    img.paste(overlay, (0, 0), overlay.getchannel("A"))


def _draw_card_background(img: Image.Image, white_from: int | None = None) -> None:
    """Dibuja la textura cromática compartida por ambas caras de la cédula."""
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((0, 0, CARD_WIDTH, CARD_HEIGHT), fill=(228, 236, 174, 255))

    # Manchas irregulares base para la textura de camuflaje amarillo y azul verdoso.
    for points, color in _YELLOW_SHAPES:
        draw.polygon(points, fill=color)
    for points, color in _BLUE_SHAPES:
        draw.polygon(points, fill=color)

    # Textura de piedra sobre las zonas amarillentas y puntillismo sobre las celestes.
    _apply_stone_texture(img, _YELLOW_SHAPES)
    _apply_pointillism(img, _BLUE_SHAPES)

    draw = ImageDraw.Draw(img, "RGBA")

    # Líneas muy finas de seguridad para conservar el aspecto impreso del original.
    for offset in range(-CARD_HEIGHT, CARD_WIDTH + CARD_HEIGHT, 150):
        draw.line((offset, 0, offset + CARD_HEIGHT, CARD_HEIGHT), fill=(52, 180, 170, 40), width=1)

    # Velo claro para que el patrón funcione como fondo y no compita con los datos.
    draw.rectangle((0, 0, CARD_WIDTH, CARD_HEIGHT), fill=(255, 255, 255, 115))

    if white_from is not None:
        draw.rectangle((0, white_from, CARD_WIDTH, CARD_HEIGHT), fill=(255, 255, 255, 255))


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    if bold:
        candidates = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def create_brazil_front_template() -> Image.Image:
    """Genera un template sintético del frente de la cédula BR."""
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG)
    _draw_card_background(img)
    draw = ImageDraw.Draw(img)

    # Encabezado
    shield_candidates = [
        Path(__file__).resolve().parent.parent / "elementos" / "escudo do br.webp",
        Path(__file__).resolve().parent.parent / "elementos" / "Escudo-nacional.png",
    ]
    for shield_path in shield_candidates:
        if shield_path.exists():
            shield = Image.open(shield_path).convert("RGBA")
            shield.thumbnail((84, 84), Image.Resampling.LANCZOS)
            img.paste(shield, (10, 10), shield)
            break

    map_path = Path(__file__).resolve().parent.parent / "elementos" / "mapa_do_br_.jpeg"
    if map_path.exists():
        brazil_map = Image.open(map_path).convert("RGB")
        brazil_map.thumbnail((100, 90), Image.Resampling.LANCZOS)
        brazil_map = brazil_map.convert("RGBA")
        # Recorta el fondo blanco del recorte del mapa para que quede sobre la cédula.
        pixels = [
            (r, g, b, 0) if r > 235 and g > 235 and b > 235 else (r, g, b, a)
            for r, g, b, a in brazil_map.getdata()
        ]
        brazil_map.putdata(pixels)
        map_x = CARD_WIDTH - brazil_map.width - 14
        map_y = 8
        img.paste(brazil_map, (map_x, map_y), brazil_map)

    draw.text((120, 12), "REPÚBLICA FEDERATIVA DO BRASIL", fill=HEADER_GREEN, font=_load_font(28, bold=True))

    gov_font = _load_font(17, bold=True)
    gov_text = "GOVERNO FEDERAL"
    gov_bbox = draw.textbbox((0, 0), gov_text, font=gov_font)
    gov_x = (CARD_WIDTH - (gov_bbox[2] - gov_bbox[0])) / 2
    draw.text((gov_x, 44), gov_text, fill=HEADER_GREEN, font=gov_font)

    subtitle_font = _load_font(12)
    subtitle_line_1 = "Unidade da Federação"
    subtitle_line_2 = "Secretaria de Segurança da Unidade da Federação"
    subtitle_1_bbox = draw.textbbox((0, 0), subtitle_line_1, font=subtitle_font)
    subtitle_2_bbox = draw.textbbox((0, 0), subtitle_line_2, font=subtitle_font)
    subtitle_1_x = (CARD_WIDTH - (subtitle_1_bbox[2] - subtitle_1_bbox[0])) / 2
    subtitle_2_x = (CARD_WIDTH - (subtitle_2_bbox[2] - subtitle_2_bbox[0])) / 2
    draw.text((subtitle_1_x, 64), subtitle_line_1, fill=(90, 90, 90), font=subtitle_font)
    draw.text((subtitle_2_x, 78), subtitle_line_2, fill=(90, 90, 90), font=_load_font(10))

    # Título principal
    draw.text((235, 100), "CARTEIRA DE IDENTIDADE", fill=TEXT, font=_load_font(34, bold=True))

    # Foto tipo documento, alineada con el texto de la derecha ("Nome").
    draw.rounded_rectangle(PHOTO_BOX, radius=8, outline=(180, 180, 180), width=2, fill=(220, 220, 220))
    photo = Image.new("RGB", (182, 192), (220, 220, 220))
    photo_draw = ImageDraw.Draw(photo)
    photo_draw.ellipse((30, 24, 152, 120), fill=(192, 192, 192))
    photo_draw.ellipse((0, 120, 182, 192), fill=(192, 192, 192))
    img.paste(photo, (35, 187))

    # Etiquetas de los campos (los valores los agrega ``BrazilIDRenderer``).
    label_font = _load_font(10)
    for key, (x, y) in FRONT_FIELD_POSITIONS.items():
        draw.text((x, y), FRONT_FIELD_LABELS[key], fill=(80, 80, 80), font=label_font)

    # Espacio de firma (sin línea, solo el rótulo indicando dónde firmar)
    signature_left = 390
    signature_right = 770
    signature_text = "Assinatura do Titular / Cardholder's Signature"
    signature_bbox = draw.textbbox((0, 0), signature_text, font=label_font)
    signature_width = signature_bbox[2] - signature_bbox[0]
    signature_x = signature_left + ((signature_right - signature_left) - signature_width) / 2
    draw.text((signature_x, 434), signature_text, fill=(80, 80, 80), font=label_font)

    # Sección inferior: documento de la cédula
    draw.line((0, 460, CARD_WIDTH, 460), fill=(180, 180, 180), width=1)
    draw.text((35, 472), "Válida em todo o território nacional - Lei n° XXX", fill=(60, 60, 60), font=_load_font(10, bold=True))

    return img


def create_brazil_back_template() -> Image.Image:
    """Genera un template sintético del reverso de la cédula BR."""
    img = Image.new("RGB", (CARD_WIDTH, CARD_HEIGHT), BG)
    _draw_card_background(img, white_from=360)
    draw = ImageDraw.Draw(img)

    # Marco del QR / código de barras
    qr_frame = (40, 80, 220, 240)
    draw.rectangle(qr_frame, outline=(120, 120, 120), width=2, fill=(255, 255, 255))
    for x in range(52, 208, 10):
        for y in range(92, 228, 10):
            if (x + y) % 2 == 0:
                draw.rectangle((x, y, x + 4, y + 4), fill=(30, 30, 30))

    # Etiquetas de los campos (los valores los agrega ``BrazilIDRenderer``).
    for key, (x, y) in BACK_FIELD_POSITIONS.items():
        draw.text((x, y), BACK_FIELD_LABELS[key], fill=TEXT, font=_load_font(12, bold=True))

    # Línea de firma del expedidor
    draw.line((270, 330, 620, 330), fill=(80, 80, 80), width=1)
    draw.text((310, 334), "Assinatura do Expedidor / Card Issuer Signature", fill=(80, 80, 80), font=_load_font(9))

    # MRZ / zona de código (las líneas las agrega ``BrazilIDRenderer``).
    draw.rounded_rectangle((35, 360, 865, 470), radius=12, fill=(245, 245, 245), outline=(150, 150, 150), width=1)

    # Footer
    draw.text((60, 480), "VÁLIDA EM TODO O TERRITÓRIO NACIONAL - LEI N° XXX", fill=(60, 60, 60), font=_load_font(10, bold=True))

    return img
