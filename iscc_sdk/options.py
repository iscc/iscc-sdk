"""SDK options can be configured using environment variables. Variables are defined as
class-atributes on the `SdkOptions` instance.

!!! example "Example how to access configuration options"
    ```python
    import iscc_sdk as idk

    # To access ISCC_SDK_VIDEO_FPS setting use
    fps: int = idk.sdk_opts.video_fps

    # Configuration of the `iscc-core` dependency is also available
    # To access ISCC_CORE_IMAGE_BITS use
    image_bits: int = idk.core_opts.image_bits
    ```


"""

from typing import Optional

try:
    from pydantic.v1 import Field, validator, BaseSettings
except ImportError:  # pragma: no cover
    from pydantic import Field, validator, BaseSettings
from PIL import Image
import iscc_core


__all__ = [
    "SdkOptions",
    "sdk_opts",
    "core_opts",
]


class SdkOptions(BaseSettings):
    """SDK Configuration Options"""

    class Config:
        validate_assignment = True
        env_prefix = "ISCC_SDK_"
        env_file = "iscc-sdk.env"
        env_file_encoding = "utf-8"

    granular: bool = Field(
        False,
        description="ISCC_SDK_GRANULAR - Generate additional granular fingerprints for ISCC-CODES",
    )

    extract_metadata: bool = Field(
        True,
        description="ISCC_EXTRACT_METADATA - Extract metadata from digital assets (defaut: True)",
    )

    create_thumbnail: bool = Field(
        True,
        description="ISCC_CREATE_THUMBNAIL - Create thumbail for digital assets (defaut: True)",
    )

    image_exif_transpose: bool = Field(
        True,
        description="ISCC_SDK_IMAGE_EXIF_TRANSPOSE - Transpose image according to EXIF Orientation tag",
    )

    image_fill_transparency: bool = Field(
        True,
        description="ISCC_SDK_IMAGE_FILL_TRANSPARENCY - Add white background to image if it has alpha transparency",
    )

    image_trim_border: bool = Field(
        True, description="ISCC_SDK_IMAGE_TRIM_BORDER - Crop empty borders of images"
    )

    image_thumbnail_size: int = Field(
        128,
        description="ISCC_SDK_IMAGE_THUMBNAIL_SIZE - Size of larger side of thumbnail in number of pixels",
    )

    image_thumbnail_quality: int = Field(
        60,
        description="ISCC_SDK_IMAGE_THUMBNAIL_QUALITY - Thumbnail image compression setting (0-100)",
    )

    image_max_pixels: Optional[int] = Field(
        128000000,
        description="ISCC_SDK_IMAGE_MAX_PIXELS - Maximum number of pixels allowed for processing (default 128Mpx / 0.5GB RGB)",
    )

    text_avg_chunk_size: int = Field(
        1024,
        description="ISCC_SDK_TEXT_AVG_CHUNK_SIZE - Avg number of characters per text chunk for granular fingerprints",
    )

    video_fps: int = Field(
        5,
        description="ISCC_SDK_VIDEO_FPS - Frames per second to process for video hash (ignored when 0).",
    )

    video_store_mp7sig: bool = Field(
        False,
        description="ISCC_SDK_VIDEO_STORE_MP7SIG - Store extracted MP7 Video as <videofile>.iscc.mp7sig",
    )

    @validator("image_max_pixels")
    def set_pillow(cls, v):
        Image.MAX_IMAGE_PIXELS = v
        return v


sdk_opts = SdkOptions()
core_opts = iscc_core.core_opts
