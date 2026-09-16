# cedula-synthetic-dataset

Generador sintético de cédulas brasileñas para entrenamiento de modelos de OCR y reconocimiento documental. Este repositorio surge como extensión de un generador previo basado en templates de identidad, reutilizando la misma arquitectura para facilitar la adaptación y expansión a nuevos países o diseños. En este caso, el foco principal es la cédula brasileña, aunque el proyecto conserva algunos elementos heredados del flujo original dominicano para mantener la estructura modular y reutilizable.

La idea principal es crear datos sintéticos, templates visuales inspirados en documentos reales y una pipeline completa para producir imágenes de anverso y reverso con metadatos asociados, sin utilizar documentos reales ni rostros reales.

## Instalación

```bash
pip install -r requirements.txt
```

## Uso rápido para Brasil

```python
from cedula_synthetic import BrazilIDGenerator

generator = BrazilIDGenerator(output_dir="mi_dataset_br", seed=42)

# Generar una sola cédula (frente + dorso)
front, back, data = generator.generate_single()
front.save("front.jpg")
back.save("back.jpg")

# Generar un dataset en batch con metadatos en CSV
metadata_csv = generator.generate_batch(num_samples=1000)
```

También puedes usar los ejemplos incluidos:

```bash
python examples/generate_brazil_template_example.py
python examples/generate_batch_brazil_example.py --num-samples 1000 --output-dir synthetic_dataset_br --seed 42
```

## Estructura del proyecto

- `cedula_synthetic/brasil_template.py` – template visual del frente y dorso inspirados en la cédula brasileña, con fondos, cajas de texto, foto y marca de agua.
- `cedula_synthetic/brasil_data_generator.py` – generación de datos sintéticos brasileños: nombre, nome social, Registro Geral, fechas, naturalidad, filiación, conjunto de datos que alimenta el render.
- `cedula_synthetic/brasil_renderer.py` – renderizado de texto, foto y MRZ sobre los templates BR.
- `cedula_synthetic/brasil_generator.py` – clase principal `BrazilIDGenerator` que integra datos, render y almacenamiento.
- `cedula_synthetic/generator.py` – pipeline principal original para identificación dominicana, mantenido como referencia y base modular.
- `cedula_synthetic/data_generator.py` – generación de datos sintéticos dominicanos, usada como base para construir variaciones y adaptar nuevos países.
- `cedula_synthetic/templates.py` – templates alternativos generados para otros diseños de identificación.
- `cedula_synthetic/augmentation.py` – pipeline de aumentación visual: rotación, perspectiva, brillo/contraste, ruido, desenfoque y variaciones de iluminación.
- `cedula_synthetic/storage.py` – guarda imágenes y metadatos en CSV con validación básica.
- `examples/` – scripts de ejemplo para generar templates, batches y muestras aisladas.
- `tests/` – pruebas unitarias del proyecto.

## Nota importante

No se distribuye ninguna imagen real de cédulas ni rostros reales. Los templates, textos, fotos sintéticas y los datasets creados se generan de forma programática para evitar problemas de privacidad, derechos de imagen y dependencia de documentos auténticos.

El repositorio está diseñado de forma modular para que sea sencillo:
- adaptar nuevos países,
- cambiar layouts,
- extender tipos de documentos,
- mantener el código más limpio y escalable que un único archivo monolítico.

## Tests

```bash
pip install pytest
pytest tests/
```
