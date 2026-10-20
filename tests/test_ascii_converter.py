"""Unit tests for the AsciiConverter core module."""

import time

import numpy as np
from PIL import Image

from src.core.ascii_converter import AsciiConfig, AsciiConverter, ColorMode


def test_ascii_config_defaults() -> None:
    config = AsciiConfig()
    assert config.width == 120
    assert config.aspect_ratio_correction == 0.55
    assert len(config.charset) > 0
    assert config.color_mode == ColorMode.RGB


def test_ascii_config_fallbacks() -> None:
    config = AsciiConfig(charset="", width=5, aspect_ratio_correction=-1.0)
    assert len(config.charset) > 0
    assert config.width == 10
    assert config.aspect_ratio_correction == 0.55


def test_convert_solid_colors() -> None:
    # 100x100 solid black
    black_img = np.zeros((100, 100, 3), dtype=np.uint8)
    config = AsciiConfig(width=20, charset=" #", color_mode=ColorMode.MONOCHROME)
    frame = AsciiConverter.convert(black_img, config)

    assert frame.width == 20
    assert frame.height == 11  # 100 * (20/100) * 0.55 = 11
    assert frame.colors is None
    # All characters should be space
    for line in frame.chars:
        assert line == " " * 20

    # 100x100 solid white
    white_img = np.full((100, 100, 3), 255, dtype=np.uint8)
    frame_white = AsciiConverter.convert(white_img, config)
    for line in frame_white.chars:
        assert line == "#" * 20

    # Inverted white should map to space
    config_inv = AsciiConfig(width=20, charset=" #", invert=True)
    frame_inv = AsciiConverter.convert(white_img, config_inv)
    for line in frame_inv.chars:
        assert line == " " * 20


def test_color_mode_rgb() -> None:
    # Create an image with red top half and blue bottom half
    img = np.zeros((50, 50, 3), dtype=np.uint8)
    img[:25, :, 0] = 255  # Red in RGB (if is_rgb_input=True)
    img[25:, :, 2] = 255  # Blue in RGB

    config = AsciiConfig(width=10, color_mode=ColorMode.RGB)
    frame = AsciiConverter.convert(img, config, is_rgb_input=True)

    assert frame.colors is not None
    assert frame.colors.shape == (frame.height, frame.width, 3)
    assert frame.colors.dtype == np.uint8
    # Check that colors are preserved
    assert frame.colors[0, 0, 0] > 200  # Red channel active
    assert frame.colors[-1, 0, 2] > 200  # Blue channel active


def test_pil_image_and_grayscale_input() -> None:
    pil_img = Image.new("RGB", (60, 40), color=(128, 128, 128))
    config = AsciiConfig(width=30)
    frame = AsciiConverter.convert(pil_img, config)
    assert frame.width == 30
    assert len(frame.chars) == frame.height
    assert len(frame.text) > 0

    gray_array = np.full((40, 60), 200, dtype=np.uint8)
    frame_gray = AsciiConverter.convert(gray_array, config)
    assert frame_gray.width == 30


def test_conversion_performance() -> None:
    # 1920x1080 full HD frame
    hd_frame = np.random.randint(0, 256, (1080, 1920, 3), dtype=np.uint8)
    config = AsciiConfig(width=120, color_mode=ColorMode.RGB)

    start = time.perf_counter()
    frame = AsciiConverter.convert(hd_frame, config)
    duration_ms = (time.perf_counter() - start) * 1000.0

    assert frame.width == 120
    assert frame.height > 0
    # The conversion of a full HD frame should comfortably be under 15ms for real-time video playback
    assert duration_ms < 20.0, f"Conversion took {duration_ms:.2f}ms, expected < 20ms"
