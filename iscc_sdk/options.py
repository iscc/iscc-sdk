"""*SDK configuration and options*."""
from typing import Optional

from iscc_core.options import CoreOptions
from pydantic import Field, validator
from PIL import Image


__all__ = [
    "SdkOptions",
    "sdk_opts",
]


class SdkOptions(CoreOptions):
    class Config:
        validate_assignment = True

    granular: bool = Field(
        False,
        description="Generate additional granular fingerprints for ISCC-CODES",
    )

    image_exif_transpose: bool = Field(
        True,
        description="Transpose image according to EXIF Orientation tag",
    )

    image_fill_transparency: bool = Field(
        True, description="Add white background to image if it has alpha transparency"
    )

    image_trim_border: bool = Field(True, description="Crop empty borders of images")

    image_thumbnail_size: int = Field(
        128, description="Size of larger side of thumbnail in number of pixels"
    )

    image_thumbnail_quality: int = Field(
        60, description="Thumbnail image compression setting (0-100)"
    )

    image_max_pixels: Optional[int] = Field(
        128000000,
        description="Maximum number of pixels allowed for processing (default 128Mpx / 0.5GB RGB)",
    )

    text_avg_chunk_size: int = Field(
        1024,
        description="Avg number of characters per text chunk for granular fingerprints",
    )

    video_fps: int = Field(
        5,
        description="Frames per second to process for video hash (ignored when 0).",
    )

    @validator("image_max_pixels")
    def set_pillow(cls, v):
        Image.MAX_IMAGE_PIXELS = v
        return v


sdk_opts = SdkOptions()
