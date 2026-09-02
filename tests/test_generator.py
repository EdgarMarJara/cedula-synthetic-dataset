import csv
from pathlib import Path

from cedula_synthetic import DominicanIDGenerator


def test_generate_single_produces_images_and_data(tmp_path):
    generator = DominicanIDGenerator(output_dir=str(tmp_path / "out"), seed=10)
    front, back, data = generator.generate_single(apply_augmentation=True)

    assert front.size == back.size
    assert data.full_name.strip() != ""
    assert data.cedula_number.strip() != ""


def test_generate_single_without_augmentation_matches_render(tmp_path):
    generator = DominicanIDGenerator(output_dir=str(tmp_path / "out"), seed=11)
    front, back, data = generator.generate_single(apply_augmentation=False)
    assert front.size == generator.front_template.size
    assert back.size == generator.back_template.size


def test_generate_batch_creates_csv_and_images(tmp_path):
    output_dir = tmp_path / "dataset"
    generator = DominicanIDGenerator(output_dir=str(output_dir), seed=12)
    metadata_path = generator.generate_batch(num_samples=3, apply_augmentation=False, progress_every=0)

    metadata_file = Path(metadata_path)
    assert metadata_file.exists()

    with open(metadata_file, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))

    assert len(rows) == 3
    for row in rows:
        assert row["cedula_number"]
        front_path = output_dir / row["front_image"]
        back_path = output_dir / row["back_image"]
        assert front_path.exists()
        assert back_path.exists()

    cedula_numbers = {row["cedula_number"] for row in rows}
    assert len(cedula_numbers) == 3


def test_generate_batch_rejects_non_positive_samples(tmp_path):
    generator = DominicanIDGenerator(output_dir=str(tmp_path / "out"), seed=13)
    try:
        generator.generate_batch(num_samples=0)
        assert False, "Se esperaba ValueError"
    except ValueError:
        pass
