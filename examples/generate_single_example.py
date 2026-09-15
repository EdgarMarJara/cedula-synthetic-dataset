"""Ejemplo: generar una única cédula sintética (anverso + reverso)."""

from cedula_synthetic import DominicanIDGenerator
from pathlib import Path


def main() -> None:
    output_dir = Path("output_single_example")
    output_dir.mkdir(parents=True, exist_ok=True)
    generator = DominicanIDGenerator(output_dir=str(output_dir), seed=42)
    front, back, data = generator.generate_single(apply_augmentation=True)

    front.save(output_dir / "cedula_ejemplo_front.jpg")
    back.save(output_dir / "cedula_ejemplo_back.jpg")

    print("Datos generados:")
    for key, value in data.to_dict().items():
        print(f"  {key}: {value}")

    print(
        f"\nImágenes guardadas: {output_dir / 'cedula_ejemplo_front.jpg'}, "
        f"{output_dir / 'cedula_ejemplo_back.jpg'}"
    )


if __name__ == "__main__":
    main()
