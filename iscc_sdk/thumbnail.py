"""*Generate thumbnails for media assets*"""

from typing import Optional
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
    # type: (str) -> Optional[Image.Image]
    """
    Create a thumbnail for a media asset.

    :param str fp: Filepath to media file.
    :return: Thumbnail image as PIL Image object
    :rtype: Image.Image|None
    """
    mime, mode = idk.mediatype_and_mode(fp)
    thumbnailer = THUMBNAILERS.get(mode)
    if thumbnailer:
        return thumbnailer(fp)
