from PIL import Image

from cedula_synthetic.augmentation import AugmentationConfig, ImageAugmentor


def _sample_image():
    return Image.new("RGB", (400, 250), (200, 200, 200))


def test_apply_returns_same_size_image():
    augmentor = ImageAugmentor(seed=7)
    img = _sample_image()
    result = augmentor.apply(img)
    assert result.size == img.size
    assert result.mode == "RGB"


def test_apply_is_deterministic_with_seed():
    img = _sample_image()
    result1 = ImageAugmentor(seed=99).apply(img)
    result2 = ImageAugmentor(seed=99).apply(img)
    assert list(result1.getdata()) == list(result2.getdata())


def test_individual_steps_can_be_disabled():
    config = AugmentationConfig(
        apply_rotation=False,
        apply_perspective=False,
        apply_brightness_contrast=False,
        apply_noise=False,
        apply_blur=False,
        apply_lighting=False,
    )
    augmentor = ImageAugmentor(config=config, seed=1)
    img = _sample_image()
    result = augmentor.apply(img)
    assert list(result.getdata()) == list(img.getdata())


def test_rotation_range_respected():
    config = AugmentationConfig(rotation_range=(0.0, 0.0))
    augmentor = ImageAugmentor(config=config, seed=5)
    img = _sample_image()
    rotated = augmentor.rotate(augmentor._to_cv(img))
    assert rotated.shape[:2] == (250, 400)
