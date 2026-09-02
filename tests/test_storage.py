from PIL import Image

from cedula_synthetic.data_generator import DominicanDataGenerator
from cedula_synthetic.storage import StorageManager


def test_save_sample_and_validate(tmp_path):
    storage = StorageManager(str(tmp_path))
    data = DominicanDataGenerator(seed=1).generate()
    front = Image.new("RGB", (100, 60), (255, 0, 0))
    back = Image.new("RGB", (100, 60), (0, 255, 0))

    record = storage.save_sample(0, front, back, data)

    assert storage.validate_record(record)
    assert (tmp_path / record["front_image"]).exists()
    assert (tmp_path / record["back_image"]).exists()


def test_validate_record_detects_missing_fields():
    storage = StorageManager.__new__(StorageManager)
    incomplete_record = {"id": 0}
    assert storage.validate_record(incomplete_record) is False


def test_write_metadata_creates_csv(tmp_path):
    storage = StorageManager(str(tmp_path))
    data = DominicanDataGenerator(seed=2).generate()
    front = Image.new("RGB", (100, 60))
    back = Image.new("RGB", (100, 60))
    storage.save_sample(0, front, back, data)
    metadata_path = storage.write_metadata()
    assert metadata_path.exists()
    content = metadata_path.read_text(encoding="utf-8")
    assert "cedula_number" in content
