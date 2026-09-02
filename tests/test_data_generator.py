import re
from datetime import date

from cedula_synthetic.data_generator import DominicanDataGenerator


def test_generate_returns_all_expected_fields():
    gen = DominicanDataGenerator(seed=1)
    data = gen.generate()

    assert re.match(r"^\d{3}-\d{8}$", data.cedula_number)
    assert data.full_name.strip() != ""
    assert data.gender_code in ("M", "F")
    assert data.nationality == "Dominicana"
    assert data.address.strip() != ""
    assert data.marital_status != ""
    assert data.profession != ""


def test_cedula_numbers_are_unique():
    gen = DominicanDataGenerator(seed=2)
    numbers = {gen.generate_cedula_number() for _ in range(200)}
    assert len(numbers) == 200


def test_dates_are_consistent():
    gen = DominicanDataGenerator(seed=3)
    for _ in range(20):
        data = gen.generate()
        assert data.birth_date < data.issue_date
        assert data.issue_date < data.expiration_date
        assert data.issue_date <= date.today()
        # La persona debe ser mayor de edad en la fecha de expedición.
        age_at_issue = data.issue_date.year - data.birth_date.year
        assert age_at_issue >= 18


def test_mrz_lines_have_expected_length():
    gen = DominicanDataGenerator(seed=4)
    data = gen.generate()
    assert len(data.mrz_line1) == 30
    assert len(data.mrz_line2) == 30
    assert len(data.mrz_line3) == 30


def test_seed_reproducibility():
    gen1 = DominicanDataGenerator(seed=123)
    gen2 = DominicanDataGenerator(seed=123)
    data1 = gen1.generate()
    data2 = gen2.generate()
    assert data1.full_name == data2.full_name
    assert data1.address == data2.address
