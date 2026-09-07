import csv
from pathlib import Path

from PIL import Image

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
    expected_size = (
        generator.front_template.width + generator.canvas_margin * 2,
        generator.front_template.height + generator.canvas_margin * 2,
    )
    assert front.size == expected_size
    assert back.size == expected_size


def test_render_centers_both_faces(tmp_path):
    generator = DominicanIDGenerator(
        output_dir=str(tmp_path / "out"), seed=14, canvas_margin=20
    )
    front, back = generator.render(generator.generate_data())

    assert front.size == back.size
    assert front.getpixel((0, 0)) == (255, 255, 255)
    assert back.getpixel((0, 0)) == (255, 255, 255)


def test_generator_rejects_negative_canvas_margin(tmp_path):
    try:
        DominicanIDGenerator(output_dir=str(tmp_path / "out"), canvas_margin=-1)
        assert False, "Se esperaba ValueError"
    except ValueError:
        pass


def test_render_pastes_face_photo(tmp_path):
    generator = DominicanIDGenerator(output_dir=str(tmp_path / "out"), seed=15)
    photo = Image.new("RGB", (40, 40), (220, 30, 30))
    front, _ = generator.render(generator.generate_data(), face_photo=photo)

    photo_left, photo_top, photo_right, photo_bottom = (60, 140, 320, 460)
    offset = generator.canvas_margin
    center = (
        offset + (photo_left + photo_right) // 2,
        offset + (photo_top + photo_bottom) // 2,
    )
    assert front.getpixel(center) == (220, 30, 30)


def test_render_includes_front_identity_grid(tmp_path):
    generator = DominicanIDGenerator(output_dir=str(tmp_path / "out"), seed=16)
    data = generator.generate_data()
    front, _ = generator.render(data, face_photo=None)

    assert data.gender_code in {"M", "F"}
    assert data.marital_status
    assert data.blood_group in {"A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"}
    assert front.size == (generator.front_template.width + 96, generator.front_template.height + 96)


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
