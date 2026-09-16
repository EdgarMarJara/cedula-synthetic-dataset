"""Generación de datos sintéticos para cédulas de identidad brasileñas."""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Optional

from faker import Faker

BRAZIL_FIRST_NAMES_MALE = [
    "João", "Pedro", "Lucas", "Gabriel", "Matheus", "Rafael", "Carlos",
    "Bruno", "Felipe", "Ricardo", "André", "Marcos", "Paulo", "Eduardo",
    "Vinícius", "Thiago", "Rodrigo", "Gustavo", "Leonardo", "Diego",
]

BRAZIL_FIRST_NAMES_FEMALE = [
    "Maria", "Ana", "Juliana", "Fernanda", "Camila", "Beatriz", "Larissa",
    "Patrícia", "Aline", "Bruna", "Carla", "Débora", "Gabriela", "Letícia",
    "Mariana", "Natália", "Priscila", "Renata", "Vanessa", "Vitória",
]

BRAZIL_LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Souza", "Rodrigues", "Ferreira", "Alves",
    "Pereira", "Lima", "Gomes", "Costa", "Ribeiro", "Martins", "Carvalho",
    "Almeida", "Lopes", "Soares", "Fernandes", "Vieira", "Barbosa",
]

BRAZIL_STATES = [
    "Acre", "Alagoas", "Amapá", "Amazonas", "Bahia", "Ceará",
    "Distrito Federal", "Espírito Santo", "Goiás", "Maranhão",
    "Mato Grosso", "Mato Grosso do Sul", "Minas Gerais", "Pará", "Paraíba",
    "Paraná", "Pernambuco", "Piauí", "Rio de Janeiro", "Rio Grande do Norte",
    "Rio Grande do Sul", "Rondônia", "Roraima", "Santa Catarina",
    "São Paulo", "Sergipe", "Tocantins",
]

BRAZIL_CITIES = [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Salvador", "Curitiba",
    "Recife", "Fortaleza", "Manaus", "Porto Alegre", "Brasília", "Goiânia",
    "Belém", "Vitória", "Natal", "Campo Grande",
]

ISSUER_ORGANS = [
    "SSP/SP", "SSP/RJ", "SSP/MG", "SSP/BA", "SSP/PR", "SSP/PE", "SSP/CE",
    "SSP/RS", "SSP/GO", "SSP/DF",
]

GENDERS = [("M", "Masculino"), ("F", "Feminino")]

NATIONALITY = "Brasileira"


@dataclass
class BrazilCedulaData:
    """Estructura de datos completa para una cédula brasileña sintética."""

    registro_geral: str
    full_name: str
    social_name: str
    gender_code: str
    gender_label: str
    birth_date: date
    birth_place: str
    nationality: str
    father_name: str    # Esta linea es la de primer apellido
    mother_name: str    # Esta linea es la de segundo apellido
    issuer_organ: str
    issue_place: str
    issue_date: date
    expiration_date: date
    mrz_line1: str = field(default="")
    mrz_line2: str = field(default="")
    mrz_line3: str = field(default="")

    def to_dict(self) -> dict:
        data = asdict(self)
        data["birth_date"] = self.birth_date.isoformat()
        data["issue_date"] = self.issue_date.isoformat()
        data["expiration_date"] = self.expiration_date.isoformat()
        return data


def _mrz_fill(text: str, length: int) -> str:
    """Rellena/recorta ``text`` a ``length`` usando ``<`` como en el estándar MRZ."""
    normalized = "".join(
        c if c.isalnum() else "<"
        for c in text.upper().replace(" ", "<")
    )
    normalized = normalized.ljust(length, "<")[:length]
    return normalized


def _safe_date(year: int, month: int, day: int) -> date:
    """Crea una fecha ajustando el 29 de febrero en años no bisiestos."""
    while True:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1


class BrazilDataGenerator:
    """Genera datos sintéticos y consistentes para cédulas brasileñas."""

    def __init__(self, seed: Optional[int] = None):
        self.faker = Faker("pt_BR")
        self._rng = random.Random(seed)
        if seed is not None:
            self.faker.seed_instance(seed)
        self._used_registro_geral: set[str] = set()

    def generate_registro_geral(self) -> str:
        """Genera un número de Registro Geral único con formato ``NN.NNN.NNN-N``."""
        while True:
            body = "".join(self._rng.choices(string.digits, k=8))
            check = self._rng.choice(string.digits)
            number = f"{body[:2]}.{body[2:5]}.{body[5:8]}-{check}"
            if number not in self._used_registro_geral:
                self._used_registro_geral.add(number)
                return number

    def generate_name(self, gender_code: str) -> tuple[str, str]:
        if gender_code == "M":
            first = self._rng.choice(BRAZIL_FIRST_NAMES_MALE)
        else:
            first = self._rng.choice(BRAZIL_FIRST_NAMES_FEMALE)
        last = f"{self._rng.choice(BRAZIL_LAST_NAMES)} {self._rng.choice(BRAZIL_LAST_NAMES)}"
        return first, last

    def generate_dates(self) -> tuple[date, date, date]:
        """Genera fechas de nascimento, emissão y validade consistentes entre sí."""
        today = date.today()
        birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=85)
        earliest_issue = _safe_date(birth_date.year + 18, birth_date.month, birth_date.day)
        if earliest_issue > today:
            earliest_issue = today
        issue_days_range = max((today - earliest_issue).days, 0)
        issue_date = earliest_issue + timedelta(days=self._rng.randint(0, issue_days_range))
        expiration_date = _safe_date(issue_date.year + 10, issue_date.month, issue_date.day)
        return birth_date, issue_date, expiration_date

    def build_mrz(self, data: "BrazilCedulaData") -> tuple[str, str, str]:
        """Construye 3 líneas MRZ (formato tipo TD1) a partir de los datos generados."""
        doc_number = data.registro_geral.replace(".", "").replace("-", "")
        line1 = f"IDBRA{_mrz_fill(doc_number, 9)}<{_mrz_fill('', 15)}"[:30]

        birth = data.birth_date.strftime("%y%m%d")
        expiry = data.expiration_date.strftime("%y%m%d")
        sex = data.gender_code
        line2 = f"{birth}<{sex}{expiry}<BRA<<<<<<<<<<<<<<"[:30]

        last_name_mrz = _mrz_fill(data.full_name.split(" ", 1)[-1], 20)
        first_name_mrz = _mrz_fill(data.full_name.split(" ", 1)[0], 9)
        line3 = f"{last_name_mrz}<<{first_name_mrz}"[:30].ljust(30, "<")
        return line1, line2, line3

    def generate(self) -> BrazilCedulaData:
        gender_code, gender_label = self._rng.choice(GENDERS)
        first_name, last_name = self.generate_name(gender_code)
        birth_date, issue_date, expiration_date = self.generate_dates()
        father_first, _ = self.generate_name("M")
        mother_first, _ = self.generate_name("F")

        data = BrazilCedulaData(
            registro_geral=self.generate_registro_geral(),
            full_name=f"{first_name} {last_name}",
            social_name=f"{first_name} {last_name}",
            gender_code=gender_code,
            gender_label=gender_label,
            birth_date=birth_date,
            birth_place=f"{self._rng.choice(BRAZIL_CITIES)} - {self._rng.choice(BRAZIL_STATES)}",
            nationality=NATIONALITY,
            father_name=f"{father_first} {self._rng.choice(BRAZIL_LAST_NAMES)} {last_name.split(' ')[-1]}",
            mother_name=f"{mother_first} {self._rng.choice(BRAZIL_LAST_NAMES)} {last_name.split(' ')[-1]}",
            issuer_organ=self._rng.choice(ISSUER_ORGANS),
            issue_place=f"{self._rng.choice(BRAZIL_CITIES)} - {self._rng.choice(BRAZIL_STATES)}",
            issue_date=issue_date,
            expiration_date=expiration_date,
        )
        data.mrz_line1, data.mrz_line2, data.mrz_line3 = self.build_mrz(data)
        return data
