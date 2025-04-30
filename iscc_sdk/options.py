"""SDK options can be configured using environment variables. Variables are defined as
class-atributes on the `SdkOptions` instance.

!!! example "Example how to access configuration options"
    ```python
    import iscc_sdk as idk

    # To access ISCC_SDK_VIDEO_FPS setting use
    fps: int = idk.sdk_opts.video_fps
    ```


"""

from typing import Optional, Literal
import copy

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
        default=False,
        description="ISCC_SDK_GRANULAR - Generate additional granular fingerprints for ISCC-CODES",
    )

    byte_offsets: bool = Field(
        False,
        description="ISCC_SDK_BYTE_OFFSETS - Use UTF-8 byte offsets instead of character offsets for granular fingerprints",
    )

    process_container: bool = Field(
        default=False,
        description="ISCC_SDK_PROCESS_CONTAINER - Process embedded elements in container formats",
    )

    experimental: bool = Field(
        default=False,
        description="ISCC_SDK_EXPERIMENTAL - Enable experimental features like Semantic Code units",
    )

    min_image_size: int = Field(
        default=256,
        description="ISCC_SDK_MIN_IMAGE_SIZE - Minimum image size in pixels for container processing",
    )

    add_units: bool = Field(
        default=False,
        description="ISCC_SDK_ADD_UNITS - Add ISCC-UNITS to ISCC metadata (in 'units' property)",
    )

    bits: int = Field(
        default=64,
        description="ISCC_SDK_BITS - Bit size of ISCC-UNITS in ISCC metadata (in 'units' property)",
    )

    wide: bool = Field(
        default=False,
        description="ISCC_SDK_WIDE - For ISCC-SUM with Data & Instance codes only support wide mode",
    )

    extract_meta: bool = Field(
        default=True,
        description="ISCC_EXTRACT_META - Extract metadata from digital assets (defaut: True)",
    )

    create_meta: bool = Field(
        default=True,
        description="ISCC_CREATE_META - Create Meta-Code from embedded metadata (defaut: True)",
    )

    create_thumb: bool = Field(
        default=True,
        description="ISCC_CREATE_THUMBNAIL - Create thumbail for digital assets (defaut: True)",
    )

    image_exif_transpose: bool = Field(
        default=True,
        description="ISCC_SDK_IMAGE_EXIF_TRANSPOSE - Transpose image according to EXIF Orientation tag",
    )

    image_fill_transparency: bool = Field(
        default=True,
        description="ISCC_SDK_IMAGE_FILL_TRANSPARENCY - Add white background to image if it has alpha transparency",
    )

    image_trim_border: bool = Field(
        default=True, description="ISCC_SDK_IMAGE_TRIM_BORDER - Crop empty borders of images"
    )

    image_thumbnail_size: int = Field(
        default=128,
        description="ISCC_SDK_IMAGE_THUMBNAIL_SIZE - Size of larger side of thumbnail in number of pixels",
    )

    image_thumbnail_quality: int = Field(
        default=30,
        description="ISCC_SDK_IMAGE_THUMBNAIL_QUALITY - Thumbnail image compression setting (0-100)",
    )

    image_thumbnail_format: Literal["JPEG", "WEBP", "AVIF"] = Field(
        default="WEBP",
        description="ISCC_SDK_IMAGE_THUMBNAIL_FORMAT - Format for thumbnail images (JPEG, WEBP, or AVIF)",
    )

    image_max_pixels: Optional[int] = Field(
        default=128000000,
        description="ISCC_SDK_IMAGE_MAX_PIXELS - Maximum number of pixels allowed for processing (default 128Mpx / 0.5GB RGB)",
    )

    text_keep: bool = Field(
        default=False,
        description="ISCC_SDK_TEXT_KEEP - Keep extracted plainext on `IsccMata.text` property",
    )

    text_avg_chunk_size: int = Field(
        default=512,
        description="ISCC_SDK_TEXT_AVG_CHUNK_SIZE - Avg number of characters per text chunk for Content-Code Text granular fingerprints",
    )

    video_fps: int = Field(
        default=5,
        description="ISCC_SDK_VIDEO_FPS - Frames per second to process for video hash (ignored when 0).",
    )

    video_scene_limit: float = Field(
        default=0.4,
        description="ISCC_SDK_VIDEO_SCENE_LIMIT - Threshold value above which a scene cut is created (default 0.4)",
    )

    video_store_mp7sig: bool = Field(
        default=False,
        description="ISCC_SDK_VIDEO_STORE_MP7SIG - Store extracted MP7 Video as <videofile>.iscc.mp7sig",
    )

    fallback: bool = Field(
        default=False,
        description="ISCC_SDK_FALLBACK - Create 2-UNIT ISCC-SUM for unsupported media types",
    )

    @validator("image_max_pixels")
    def set_pillow(cls, v):
        Image.MAX_IMAGE_PIXELS = v
        return v

    def override(self, update=None):
        # type: (dict|None) -> SdkOptions
        """Returns an updated and validated deep copy of the current settings instance."""

        update = update or {}  # sets {} if update is None

        opts = copy.deepcopy(self)
        # We need update fields individually so validation gets triggered
        for field, value in update.items():
            if hasattr(self, field):
                setattr(opts, field, value)
            else:
                raise ValueError(f"Invalid field: {field}")
        return opts


sdk_opts = SdkOptions()
core_opts = iscc_core.core_opts
