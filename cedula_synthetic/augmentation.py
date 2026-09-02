"""Pipeline de aumentación/transformaciones para imágenes de cédulas."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

import cv2
import numpy as np
from PIL import Image


@dataclass
class AugmentationConfig:
    """Parámetros configurables del pipeline de aumentación."""

    rotation_range: tuple[float, float] = (-15.0, 15.0)
    perspective_strength: int = 25
    brightness_range: tuple[float, float] = (0.75, 1.25)
    contrast_range: tuple[float, float] = (0.75, 1.25)
    noise_std_range: tuple[float, float] = (0.0, 12.0)
    blur_probability: float = 0.35
    blur_kernel_choices: tuple[int, ...] = (3, 5)
    apply_rotation: bool = True
    apply_perspective: bool = True
    apply_brightness_contrast: bool = True
    apply_noise: bool = True
    apply_blur: bool = True
    apply_lighting: bool = True


class ImageAugmentor:
    """Aplica rotación, perspectiva, ruido, brillo/contraste y desenfoque."""

    def __init__(self, config: Optional[AugmentationConfig] = None, seed: Optional[int] = None):
        self.config = config or AugmentationConfig()
        self._rng = random.Random(seed)
        self._np_rng = np.random.default_rng(seed)

    def _to_cv(self, image: Image.Image) -> np.ndarray:
        return cv2.cvtColor(np.array(image.convert("RGB")), cv2.COLOR_RGB2BGR)

    def _to_pil(self, image: np.ndarray) -> Image.Image:
        return Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    def rotate(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        angle = self._rng.uniform(*self.config.rotation_range)
        center = (w // 2, h // 2)
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(
            image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE
        )

    def perspective(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        margin = self.config.perspective_strength
        pts1 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
        pts2 = np.float32(
            [
                [self._rng.randint(0, margin), self._rng.randint(0, margin)],
                [w - self._rng.randint(0, margin), self._rng.randint(0, margin)],
                [self._rng.randint(0, margin), h - self._rng.randint(0, margin)],
                [w - self._rng.randint(0, margin), h - self._rng.randint(0, margin)],
            ]
        )
        matrix = cv2.getPerspectiveTransform(pts1, pts2)
        return cv2.warpPerspective(
            image, matrix, (w, h), borderMode=cv2.BORDER_REPLICATE
        )

    def brightness_contrast(self, image: np.ndarray) -> np.ndarray:
        contrast = self._rng.uniform(*self.config.contrast_range)
        brightness = self._rng.uniform(*self.config.brightness_range)
        beta = (brightness - 1.0) * 60
        return cv2.convertScaleAbs(image, alpha=contrast, beta=beta)

    def gaussian_noise(self, image: np.ndarray) -> np.ndarray:
        std = self._rng.uniform(*self.config.noise_std_range)
        if std <= 0:
            return image
        noise = self._np_rng.normal(0, std, image.shape)
        noisy = image.astype(np.float32) + noise
        return np.clip(noisy, 0, 255).astype(np.uint8)

    def blur(self, image: np.ndarray) -> np.ndarray:
        if self._rng.random() > self.config.blur_probability:
            return image
        kernel = self._rng.choice(self.config.blur_kernel_choices)
        return cv2.GaussianBlur(image, (kernel, kernel), 0)

    def lighting_variation(self, image: np.ndarray) -> np.ndarray:
        h, w = image.shape[:2]
        gradient_angle = self._rng.uniform(0, 2 * np.pi)
        x = np.linspace(-1, 1, w)
        y = np.linspace(-1, 1, h)
        xv, yv = np.meshgrid(x, y)
        gradient = xv * np.cos(gradient_angle) + yv * np.sin(gradient_angle)
        gradient = (gradient - gradient.min()) / (gradient.max() - gradient.min() + 1e-8)
        strength = self._rng.uniform(-40, 40)
        lighting = (gradient * strength)[..., None]
        result = image.astype(np.float32) + lighting
        return np.clip(result, 0, 255).astype(np.uint8)

    def apply(self, image: Image.Image) -> Image.Image:
        """Aplica el pipeline completo de aumentación a una imagen PIL."""
        cv_image = self._to_cv(image)

        if self.config.apply_rotation:
            cv_image = self.rotate(cv_image)
        if self.config.apply_perspective:
            cv_image = self.perspective(cv_image)
        if self.config.apply_lighting:
            cv_image = self.lighting_variation(cv_image)
        if self.config.apply_brightness_contrast:
            cv_image = self.brightness_contrast(cv_image)
        if self.config.apply_noise:
            cv_image = self.gaussian_noise(cv_image)
        if self.config.apply_blur:
            cv_image = self.blur(cv_image)

        return self._to_pil(cv_image)
