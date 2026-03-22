"""Compatibility helpers."""

from PIL import Image

__all__ = [
    "BICUBIC",
    "LANCZOS",
]

LANCZOS = Image.Resampling.LANCZOS
BICUBIC = Image.Resampling.BICUBIC
