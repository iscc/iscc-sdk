"""*SDK configuration and options*."""
from typing import Optional

from iscc_core.options import CoreOptions
from pydantic import Field


__all__ = [
    "SdkOptions",
    "sdk_opts",
]


class SdkOptions(CoreOptions):

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

    video_fps: int = Field(
        5,
        description="Frames per second to process for video hash (ignored when 0).",
    )


sdk_opts = SdkOptions()
