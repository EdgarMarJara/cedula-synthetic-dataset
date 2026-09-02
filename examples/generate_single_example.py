"""Ejemplo: generar una única cédula sintética (anverso + reverso)."""

from cedula_synthetic import DominicanIDGenerator


def main() -> None:
    generator = DominicanIDGenerator(output_dir="output_single_example", seed=42)
    front, back, data = generator.generate_single(apply_augmentation=True)

    front.save("cedula_ejemplo_front.jpg")
    back.save("cedula_ejemplo_back.jpg")

    print("Datos generados:")
    for key, value in data.to_dict().items():
        print(f"  {key}: {value}")

    print("\nImágenes guardadas: cedula_ejemplo_front.jpg, cedula_ejemplo_back.jpg")


if __name__ == "__main__":
    main()
