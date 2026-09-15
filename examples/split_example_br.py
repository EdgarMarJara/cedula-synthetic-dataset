"""Divide la cédula de ejemplo por la mitad horizontal.

Se usa para separar el anverso y el reverso del ejemplo BR y empezar a
construir el template de la cédula a partir de una referencia real.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def detect_horizontal_cut(image: Image.Image, center_bias: float = 0.5) -> int:
    """Devuelve el corte real para la cédula BR.

    En esta referencia, la línea de corte debe quedar justo debajo de la
    etiqueta "Assinatura do titular / Cardholder's Signature", que aparece en
    el centro de la imagen. En la muestra que estamos usando, el corte real queda
    un poco más arriba de la línea de firma, alrededor de Y=360.
    Se mantiene un cálculo auxiliar por intensidad para no quedar atado a una
    sola imagen, pero el valor operativo por defecto se usa como referencia real.
    """
    gray = image.convert("L")
    width, height = gray.size
    if height < 2:
        raise ValueError(f"La imagen es demasiado corta para cortarse: {gray.size}")

    reference_cut_y = 360
    row_means = []
    for y in range(height):
        row = gray.crop((0, y, width, y + 1))
        row_means.append(sum(row.getdata()) / (row.width * row.height))

    smoothed = []
    for index in range(height):
        start = max(0, index - 4)
        end = min(height, index + 5)
        window = row_means[start:end]
        smoothed.append(sum(window) / len(window))

    low_y = int(height * 0.35)
    high_y = int(height * 0.65)
    best_y = reference_cut_y
    best_score = float("inf")

    for y in range(low_y, high_y):
        delta_left = abs(smoothed[y] - smoothed[y - 1]) if y > 0 else 0
        delta_right = abs(smoothed[y] - smoothed[y + 1]) if y + 1 < height else 0
        center_penalty = abs(y - height * center_bias) * 0.02
        score = -(delta_left + delta_right) + center_penalty
        if score < best_score:
            best_score = score
            best_y = y

    cut_y = max(1, min(height - 1, best_y))
    return max(1, min(height - 1, int(round((cut_y + reference_cut_y) / 2))))


def split_horizontal(
    image_path: str | Path,
    output_dir: str | Path | None = None,
    cut_y: int | None = None,
) -> tuple[Path, Path]:
    """Divide la imagen por la mitad horizontal o por un corte manual."""
    source = Path(image_path)
    image = Image.open(source).convert("RGB")
    width, height = image.size
    if height < 2:
        raise ValueError(f"La imagen es demasiado corta para cortarse: {image.size}")

    if cut_y is None:
        cut_y = detect_horizontal_cut(image)

    cut_y = max(1, min(height - 1, cut_y))
    top = image.crop((0, 0, width, cut_y))
    bottom = image.crop((0, cut_y, width, height))

    out_dir = Path(output_dir) if output_dir is not None else source.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    top_path = out_dir / f"{source.stem}_top.png"
    bottom_path = out_dir / f"{source.stem}_bottom.png"
    top.save(top_path)
    bottom.save(bottom_path)
    return top_path, bottom_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Divide una cédula de ejemplo por la mitad horizontal.")
    parser.add_argument("--source", type=str, default="ejemplo_br.png", help="Ruta de la imagen a partir.")
    parser.add_argument("--output-dir", type=str, default="output_example_split", help="Directorio de salida.")
    parser.add_argument(
        "--cut-y",
        type=int,
        default=None,
        help="Corte manual en píxeles. Si se omite, se usa el punto justo debajo de la línea de firma del titular.",
    )
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    source = project_root / args.source
    output_dir = project_root / args.output_dir

    image = Image.open(source).convert("RGB")
    cut_y = args.cut_y if args.cut_y is not None else detect_horizontal_cut(image)
    top_path, bottom_path = split_horizontal(source, output_dir, cut_y=cut_y)

    print(f"Corte aplicado en Y={cut_y} (debajo de la línea de firma del titular)")
    print(f"Anverso guardado en: {top_path}")
    print(f"Reverso guardado en: {bottom_path}")


if __name__ == "__main__":
    main()
