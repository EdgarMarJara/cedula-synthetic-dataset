# cedula-synthetic-dataset
Generador de imágenes sintéticas de cédulas de identidad de República Dominicana para training de modelos de OCR y reconocimiento de documentos

## Instalación

```bash
pip install -r requirements.txt
```

## Uso rápido

```python
from cedula_synthetic import DominicanIDGenerator

generator = DominicanIDGenerator(output_dir="mi_dataset", seed=42)

# Generar una sola cédula (anverso + reverso)
front, back, data = generator.generate_single()
front.save("front.jpg")
back.save("back.jpg")

# Generar un dataset en batch con metadatos en CSV
metadata_csv = generator.generate_batch(num_samples=1000)
```

También puedes ejecutar los ejemplos incluidos:

```bash
python examples/generate_single_example.py
python examples/generate_batch_example.py --num-samples 1000 --output-dir synthetic_dataset --seed 42
```

## Estructura del proyecto

- `cedula_synthetic/data_generator.py` – datos sintéticos dominicanos (nombres, cédula, domicilio, fechas, MRZ) usando `Faker`.
- `cedula_synthetic/templates.py` – templates genéricos de anverso/reverso (o carga de templates propios).
- `cedula_synthetic/renderer.py` – coloca texto, foto y MRZ sobre los templates.
- `cedula_synthetic/augmentation.py` – pipeline de aumentación: rotación, perspectiva, brillo/contraste, ruido gaussiano, desenfoque e iluminación.
- `cedula_synthetic/storage.py` – guarda imágenes y metadatos (CSV) con validación básica.
- `cedula_synthetic/generator.py` – clase principal `DominicanIDGenerator` que integra todo el pipeline.
- `examples/` – scripts de ejemplo de uso individual y en batch.
- `tests/` – pruebas unitarias de cada módulo.

> **Nota:** No se distribuye ninguna imagen de cédula real ni rostros reales. Los templates y las fotos de rostro se generan de forma programática para evitar cualquier problema de privacidad o derechos de imagen. Si dispones de un template propio (por ejemplo, un diseño oficial en blanco), puedes pasar sus rutas con `front_template_path` / `back_template_path` al crear el `DominicanIDGenerator`.

## Tests

```bash
pip install pytest
pytest tests/
```
