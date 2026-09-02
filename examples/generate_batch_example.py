"""Ejemplo: generar un batch de cédulas sintéticas con metadatos en CSV."""

import argparse

from cedula_synthetic import DominicanIDGenerator


def main() -> None:
    parser = argparse.ArgumentParser(description="Genera un dataset de cédulas sintéticas")
    parser.add_argument("--num-samples", type=int, default=100, help="Cantidad de cédulas a generar")
    parser.add_argument("--output-dir", type=str, default="synthetic_dataset", help="Directorio de salida")
    parser.add_argument("--seed", type=int, default=None, help="Semilla para reproducibilidad")
    parser.add_argument("--no-augmentation", action="store_true", help="Deshabilita la aumentación de imágenes")
    args = parser.parse_args()

    generator = DominicanIDGenerator(output_dir=args.output_dir, seed=args.seed)
    metadata_path = generator.generate_batch(
        num_samples=args.num_samples,
        apply_augmentation=not args.no_augmentation,
    )
    print(f"Metadatos guardados en: {metadata_path}")


if __name__ == "__main__":
    main()
