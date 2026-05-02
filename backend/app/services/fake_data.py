import uuid
from random import choice, randint
from typing import Any

from faker import Faker
from faker.providers import automotive

_fake = Faker()
_fake.add_provider(automotive)

CAR_MODELS: dict[str, list[str]] = {
    "BMW": ["M3", "M5", "3 Series", "5 Series", "7 Series", "X3", "X5", "X7", "M8", "iX", "i4", "X6"],
    "Mercedes-Benz": [
        "C-Class", "E-Class", "S-Class", "GLC", "GLE", "G-Wagon",
        "GLA", "GLB", "GLS", "AMG GT",
    ],
    "Audi": ["A3", "A4", "A6", "Q3", "Q5", "Q7", "RS6", "RS7", "e-tron", "A8", "Q8", "R8"],
    "Toyota": [
        "Camry", "Corolla", "RAV4", "Highlander", "4Runner", "Tundra",
        "Tacoma", "Prius", "Sienna", "Land Cruiser",
    ],
    "Honda": ["Civic", "Accord", "CR-V", "Pilot", "Odyssey", "Ridgeline", "HR-V", "Passport", "Fit"],
    "Ford": [
        "F-150", "Mustang", "Explorer", "Bronco", "Escape",
        "Edge", "Ranger", "Expedition", "Mach-E",
    ],
    "Tesla": ["Model 3", "Model Y", "Model S", "Model X", "Cybertruck", "Roadster"],
    "Porsche": [
        "911", "Cayenne", "Macan", "Panamera", "Taycan",
        "718 Cayman", "718 Boxster", "GT3", "GT2 RS",
    ],
    "Ferrari": ["488", "F8 Tributo", "SF90", "Roma", "812", "Portofino", "LaFerrari"],
    "Lamborghini": ["Urus", "Huracán", "Aventador", "Revuelto", "Countach"],
}

FAKER_METHODS: dict[str, Any] = {
    "name": _fake.name,
    "email": _fake.email,
    "phone": lambda: f"({randint(100, 999)})-{randint(100, 999)}-{randint(1000, 9999)}",
    "address": _fake.address,
    "company": _fake.company,
    "job": _fake.job,
    "date": lambda: _fake.date_time().strftime("%Y-%m-%d %H:%M:%S"),
    "number": lambda: _fake.random_number(digits=5),
    "text": _fake.text,
    "boolean": _fake.boolean,
    "uuid": lambda: str(uuid.uuid4()),
    "url": _fake.url,
    "ip": _fake.ipv4,
    "credit_card": _fake.credit_card_number,
    "car_make": lambda: choice(list(CAR_MODELS.keys())),
    "car_vin": _fake.vin,
    "car_year": lambda: randint(1990, 2024),
    "car_color": _fake.color_name,
    "car_fuel": lambda: choice(["Gasoline", "Diesel", "Electric", "Hybrid"]),
    "car_transmission": lambda: choice(["Automatic", "Manual"]),
    "license_plate": _fake.license_plate,
}

SUPPORTED_TYPES: list[str] = list(FAKER_METHODS.keys()) + ["car_model"]


def generate_fake_data(
    field_names: list[str], field_types: list[str], num_records: int
) -> list[dict[str, Any]]:
    if num_records < 0:
        num_records = 0
    if num_records > 1000:
        num_records = 1000

    data: list[dict[str, Any]] = []
    for _ in range(num_records):
        record: dict[str, Any] = {}
        make: str | None = None
        for name, type_ in zip(field_names, field_types):
            if type_ == "car_make":
                make = choice(list(CAR_MODELS.keys()))
                record[name] = make
            elif type_ == "car_model":
                if make is None:
                    make = choice(list(CAR_MODELS.keys()))
                record[name] = choice(CAR_MODELS[make])
            elif type_ in FAKER_METHODS:
                record[name] = FAKER_METHODS[type_]()
        data.append(record)
    return data
