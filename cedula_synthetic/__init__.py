"""Generador de imágenes sintéticas de cédulas de identidad de República Dominicana."""

from .generator import DominicanIDGenerator
from .data_generator import DominicanDataGenerator
from .augmentation import ImageAugmentor
from .storage import StorageManager

__all__ = [
    "DominicanIDGenerator",
    "DominicanDataGenerator",
    "ImageAugmentor",
    "StorageManager",
]

__version__ = "0.1.0"
