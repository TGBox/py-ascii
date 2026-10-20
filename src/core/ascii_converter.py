"""Vectorized ASCII art converter for images and video frames."""

from dataclasses import dataclass
from enum import Enum

import cv2
import numpy as np
from PIL import Image

DEFAULT_CHARSETS: dict[str, str] = {
    "Standard": " .:-=+*#%@",
    "Dense": " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$",
    "Minimal": " .oO@",
    "Blocks": " ░▒▓█",
}


class ColorMode(Enum):
    """Rendering color modes for ASCII output."""

    MONOCHROME = "monochrome"
    RGB = "rgb"


@dataclass
class AsciiConfig:
    """Configuration options for ASCII conversion."""

    width: int = 120
    aspect_ratio_correction: float = 0.55
    charset: str = DEFAULT_CHARSETS["Standard"]
    brightness: float = 1.0
    contrast: float = 1.0
    invert: bool = False
    color_mode: ColorMode = ColorMode.RGB
    fg_color: tuple[int, int, int] = (255, 255, 255)  # RGB
    bg_color: tuple[int, int, int] = (0, 0, 0)  # RGB

    def __post_init__(self) -> None:
        if not self.charset:
            self.charset = DEFAULT_CHARSETS["Standard"]
        self.width = max(self.width, 10)
        if self.aspect_ratio_correction <= 0:
            self.aspect_ratio_correction = 0.55


@dataclass
class AsciiFrame:
    """Represents a converted frame containing ASCII characters and color data."""

    chars: list[str]
    colors: np.ndarray | None  # Shape: (height, width, 3), dtype uint8 RGB
    width: int
    height: int

    @property
    def text(self) -> str:
        """Returns the frame as multiline plain text."""
        return "\n".join(self.chars)


class AsciiConverter:
    """High-performance ASCII converter utilizing vectorized NumPy operations."""

    @staticmethod
    def _normalize_image_to_rgb(image: Image.Image | np.ndarray) -> np.ndarray:
        """Normalizes PIL Image or OpenCV/NumPy array to an (H, W, 3) RGB uint8 array."""
        if isinstance(image, Image.Image):
            rgb_image = image.convert("RGB")
            return np.array(rgb_image, dtype=np.uint8)

        if not isinstance(image, np.ndarray):
            msg = f"Unsupported image input type: {type(image)}"
            raise TypeError(msg)

        if image.ndim == 2:
            # Grayscale (H, W) -> (H, W, 3)
            return cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        if image.ndim == 3:
            channels = image.shape[2]
            if channels == 4:
                # BGRA or RGBA -> Convert to RGB assuming standard OpenCV BGR/BGRA input
                return cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            if channels == 3:
                # Assume OpenCV BGR -> RGB
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        msg = f"Invalid image array shape: {image.shape}"
        raise ValueError(msg)

    @classmethod
    def convert(
        cls,
        image: Image.Image | np.ndarray,
        config: AsciiConfig | None = None,
        is_rgb_input: bool = False,
    ) -> AsciiFrame:
        """Converts an image or video frame into an AsciiFrame.

        Args:
            image: PIL Image or NumPy array.
            config: Conversion configuration parameters.
            is_rgb_input: Set to True if NumPy input is already RGB (not OpenCV BGR).

        Returns:
            AsciiFrame containing characters and optional RGB color matrix.
        """
        if config is None:
            config = AsciiConfig()

        if (
            isinstance(image, np.ndarray)
            and is_rgb_input
            and image.ndim == 3
            and image.shape[2] == 3
        ):
            rgb = image
        else:
            rgb = cls._normalize_image_to_rgb(image)

        orig_h, orig_w = rgb.shape[:2]
        if orig_h == 0 or orig_w == 0:
            return AsciiFrame(chars=[], colors=None, width=0, height=0)

        # Compute target dimensions
        target_w = max(1, config.width)
        target_h = max(1, round(orig_h * (target_w / orig_w) * config.aspect_ratio_correction))

        # Downsample using OpenCV INTER_AREA for crisp character block downscaling
        small_rgb = cv2.resize(rgb, (target_w, target_h), interpolation=cv2.INTER_AREA)

        # Apply contrast and brightness adjustments in float32
        small_float = small_rgb.astype(np.float32)
        adjusted = (small_float - 128.0) * config.contrast + 128.0 * config.brightness
        adjusted_rgb = np.clip(adjusted, 0.0, 255.0).astype(np.uint8)

        # Standard Rec. 601 luminance: 0.299*R + 0.587*G + 0.114*B
        luminance = (
            0.299 * adjusted_rgb[:, :, 0]
            + 0.587 * adjusted_rgb[:, :, 1]
            + 0.114 * adjusted_rgb[:, :, 2]
        )

        if config.invert:
            luminance = 255.0 - luminance

        # Map brightness directly to character indices
        charset = config.charset
        num_chars = len(charset)
        scaled_indices = (luminance * (num_chars - 1) / 255.0).round().astype(np.int32)
        indices = np.clip(scaled_indices, 0, num_chars - 1)

        # Vectorized string conversion using character lookup
        char_table = np.array(list(charset))
        char_matrix = char_table[indices]
        lines = ["".join(row) for row in char_matrix]

        # Determine colors to return
        colors: np.ndarray | None = None
        if config.color_mode == ColorMode.RGB:
            colors = adjusted_rgb

        return AsciiFrame(
            chars=lines,
            colors=colors,
            width=target_w,
            height=target_h,
        )
