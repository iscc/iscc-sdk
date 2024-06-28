"""*Generate thumbnails for media assets*"""

from pathlib import Path
from PIL import Image
import iscc_sdk as idk

__all__ = [
    "thumbnail",
]

THUMBNAILERS = {
    "image": idk.image_thumbnail,
    "video": idk.video_thumbnail,
    "text": idk.text_thumbnail,
    "audio": idk.audio_thumbnail,
}


def thumbnail(fp):
    # type: (str|Path) -> Image.Image|None
    """
    Create a thumbnail for a media asset.

    :param fp: Filepath to media file.
    :return: Thumbnail image as PIL Image object
    """
    fp = Path(fp)
    mime, mode = idk.mediatype_and_mode(fp)
    thumbnailer = THUMBNAILERS.get(mode)
    if thumbnailer:
        return thumbnailer(fp)
