"""Genera el template sintético de la cédula brasileña.

Este ejemplo usa la referencia visual de la imagen BR cortada por la línea de
la firma del titular y crea un template base para generar variantes ficticias.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cedula_synthetic import create_brazil_front_template, create_brazil_back_template


def main() -> None:
    front = create_brazil_front_template()
    back = create_brazil_back_template()

    front.save("cedula_br_template_front.png")
    back.save("cedula_br_template_back.png")

    print("Template BR generado:")
    print("- cedula_br_template_front.png")
    print("- cedula_br_template_back.png")


if __name__ == "__main__":
    main()
