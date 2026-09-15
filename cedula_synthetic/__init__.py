"""Generador de imágenes sintéticas de cédulas de identidad."""

from .generator import DominicanIDGenerator
from .data_generator import DominicanDataGenerator
from .augmentation import ImageAugmentor
from .storage import StorageManager
from .brasil_template import create_brazil_front_template, create_brazil_back_template
from .brasil_data_generator import BrazilDataGenerator, BrazilCedulaData
from .brasil_renderer import BrazilIDRenderer
from .brasil_generator import BrazilIDGenerator

__all__ = [
    "DominicanIDGenerator",
    "DominicanDataGenerator",
    "ImageAugmentor",
    "StorageManager",
    "create_brazil_front_template",
    "create_brazil_back_template",
    "BrazilDataGenerator",
    "BrazilCedulaData",
    "BrazilIDRenderer",
    "BrazilIDGenerator",
]

__version__ = "0.1.0"
