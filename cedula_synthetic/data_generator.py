"""Generación de datos sintéticos para cédulas de identidad dominicanas."""

from __future__ import annotations

import random
import string
from dataclasses import dataclass, field, asdict
from datetime import date, timedelta
from typing import Optional

from faker import Faker

# Nombres y apellidos comunes en República Dominicana. Se usan junto con
# ``Faker`` (locale ``es_ES``) para producir combinaciones plausibles sin
# depender de un proveedor específico para RD (no disponible en Faker).
DOMINICAN_FIRST_NAMES_MALE = [
    "Juan", "Luis", "José", "Carlos", "Pedro", "Rafael", "Manuel", "Ramón",
    "Francisco", "Miguel", "Ángel", "Antonio", "Wilson", "Yeuri", "Wandy",
    "Elvin", "Yoel", "Fernando", "Alberto", "Julio", "Héctor", "Cristian",
]

DOMINICAN_FIRST_NAMES_FEMALE = [
    "María", "Ana", "Rosa", "Carmen", "Yolanda", "Altagracia", "Yesenia",
    "Francisca", "Juana", "Miguelina", "Yudelka", "Scarlet", "Massiel",
    "Marleny", "Xiomara", "Yaneris", "Luz", "Esperanza", "Mercedes", "Digna",
]

DOMINICAN_LAST_NAMES = [
    "Pérez", "Rodríguez", "García", "Martínez", "Sánchez", "Reyes", "Díaz",
    "De la Cruz", "De los Santos", "Jiménez", "Fernández", "Peña", "Cabrera",
    "Ramírez", "Guzmán", "Mercedes", "Rosario", "Feliz", "Batista", "Familia",
    "Santana", "Tavárez", "Encarnación", "Polanco", "Estévez",
]

DOMINICAN_PROVINCES = [
    "Distrito Nacional", "Santo Domingo", "Santiago", "La Vega", "San Cristóbal",
    "Puerto Plata", "La Romana", "San Pedro de Macorís", "Duarte", "Espaillat",
    "Barahona", "Azua", "Monseñor Nouel", "María Trinidad Sánchez", "Peravia",
]

DOMINICAN_STREET_TYPES = ["Calle", "Avenida", "Callejón", "Prolongación"]

DOMINICAN_STREET_NAMES = [
    "Duarte", "Independencia", "Mella", "27 de Febrero", "Winston Churchill",
    "John F. Kennedy", "Máximo Gómez", "Sánchez", "Restauración", "Bolívar",
    "Nuñez de Cáceres", "San Martín", "Luperón", "Padre Billini", "Las Carreras",
]

PROFESSIONS = [
    "Ingeniero/a", "Abogado/a", "Médico/a", "Docente", "Comerciante",
    "Estudiante", "Contador/a", "Agricultor/a", "Chofer", "Enfermero/a",
    "Arquitecto/a", "Militar", "Policía", "Empleado/a Privado/a",
    "Empleado/a Público/a", "Ama de Casa", "Técnico/a", "Vendedor/a",
]

MARITAL_STATUSES = ["Soltero/a", "Casado/a", "Divorciado/a", "Viudo/a", "Unión Libre"]

GENDERS = [("M", "Masculino"), ("F", "Femenino")]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]

NATIONALITY = "Dominicana"


@dataclass
class CedulaData:
    """Estructura de datos completa para una cédula sintética."""

    cedula_number: str
    previous_cedula_number: str
    first_name: str
    last_name: str
    full_name: str
    gender_code: str
    gender_label: str
    blood_group: str
    birth_date: date
    birth_place: str
    nationality: str
    marital_status: str
    profession: str
    address: str
    province: str
    residence_address: str
    municipality: str
    electoral_college: str
    college_location: str
    birth_registration: str
    issue_date: date
    expiration_date: date
    signature: str = "NO FIRMA"
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
        c if (c.isalnum()) else "<"
        for c in text.upper().replace(" ", "<")
    )
    normalized = normalized.ljust(length, "<")[:length]
    return normalized


class DominicanDataGenerator:
    """Genera datos sintéticos y consistentes para cédulas dominicanas."""

    def __init__(self, seed: Optional[int] = None):
        self.faker = Faker("es_ES")
        self._rng = random.Random(seed)
        if seed is not None:
            self.faker.seed_instance(seed)
        self._used_cedula_numbers: set[str] = set()

    def generate_cedula_number(self) -> str:
        """Genera un número de cédula único con formato ``NNN-NNNNNNN-N``."""
        while True:
            serial = "".join(self._rng.choices(string.digits, k=3))
            body = "".join(self._rng.choices(string.digits, k=7))
            check = self._rng.choice(string.digits)
            number = f"{serial}-{body}{check}"
            if number not in self._used_cedula_numbers:
                self._used_cedula_numbers.add(number)
                return number

    def generate_name(self, gender_code: str) -> tuple[str, str]:
        if gender_code == "M":
            first = self._rng.choice(DOMINICAN_FIRST_NAMES_MALE)
        else:
            first = self._rng.choice(DOMINICAN_FIRST_NAMES_FEMALE)
        last = f"{self._rng.choice(DOMINICAN_LAST_NAMES)} {self._rng.choice(DOMINICAN_LAST_NAMES)}"
        return first, last

    def generate_address(self) -> str:
        street_type = self._rng.choice(DOMINICAN_STREET_TYPES)
        street_name = self._rng.choice(DOMINICAN_STREET_NAMES)
        number = self._rng.randint(1, 250)
        sector = self._rng.choice(DOMINICAN_PROVINCES)
        return f"{street_type} {street_name} #{number}, {sector}, República Dominicana"

    def generate_dates(self) -> tuple[date, date, date]:
        """Genera fechas de nacimiento, expedición y vencimiento consistentes entre sí."""
        today = date.today()
        birth_date = self.faker.date_of_birth(minimum_age=18, maximum_age=85)
        # La expedición debe ser posterior a la fecha en que la persona cumplió
        # 18 años, y no puede ser futura.
        earliest_issue = date(birth_date.year + 18, birth_date.month, birth_date.day)
        if earliest_issue > today:
            earliest_issue = today
        issue_days_range = max((today - earliest_issue).days, 0)
        issue_date = earliest_issue + timedelta(days=self._rng.randint(0, issue_days_range))
        expiration_date = date(issue_date.year + 10, issue_date.month, issue_date.day)
        return birth_date, issue_date, expiration_date

    def build_mrz(self, data: "CedulaData") -> tuple[str, str, str]:
        """Construye 3 líneas MRZ (formato tipo TD1) a partir de los datos generados."""
        doc_number = data.cedula_number.replace("-", "")
        line1 = f"IDDOM{_mrz_fill(doc_number, 9)}<{_mrz_fill('', 15)}"[:30]

        birth = data.birth_date.strftime("%y%m%d")
        expiry = data.expiration_date.strftime("%y%m%d")
        sex = data.gender_code
        line2 = f"{birth}<{sex}{expiry}<DOM<<<<<<<<<<<<<<"[:30]

        last_name_mrz = _mrz_fill(data.last_name, 20)
        first_name_mrz = _mrz_fill(data.first_name, 9)
        line3 = f"{last_name_mrz}<<{first_name_mrz}"[:30].ljust(30, "<")
        return line1, line2, line3

    def generate(self) -> CedulaData:
        gender_code, gender_label = self._rng.choice(GENDERS)
        first_name, last_name = self.generate_name(gender_code)
        birth_date, issue_date, expiration_date = self.generate_dates()

        data = CedulaData(
            cedula_number=self.generate_cedula_number(),
            previous_cedula_number=self.generate_cedula_number(),
            first_name=first_name,
            last_name=last_name,
            full_name=f"{first_name} {last_name}",
            gender_code=gender_code,
            gender_label=gender_label,
            blood_group=self._rng.choice(BLOOD_GROUPS),
            birth_date=birth_date,
            birth_place=self._rng.choice(DOMINICAN_PROVINCES),
            nationality=NATIONALITY,
            marital_status=self._rng.choice(MARITAL_STATUSES),
            profession=self._rng.choice(PROFESSIONS),
            address=self.generate_address(),
            province=self._rng.choice(DOMINICAN_PROVINCES),
            residence_address=self.generate_address(),
            municipality=self._rng.choice(DOMINICAN_PROVINCES),
            electoral_college=f"COLEGIO ELECTORAL {self._rng.randint(1, 9999):04d}",
            college_location=f"Centro Educativo {self._rng.choice(['Duarte', 'Independencia', 'Las Americas', 'Quisqueya'])}",
            birth_registration=f"REGISTRO DE NACIMIENTO {self._rng.randint(100000, 999999)}",
            issue_date=issue_date,
            expiration_date=expiration_date,
            signature="NO FIRMA",
        )
        data.mrz_line1, data.mrz_line2, data.mrz_line3 = self.build_mrz(data)
        return data
