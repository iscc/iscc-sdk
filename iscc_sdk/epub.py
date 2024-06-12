"""*EPUB handling module*."""

import io
import shutil
import tempfile

import ebookmeta
from PIL import Image, ImageEnhance
import iscc_sdk as idk


__all__ = [
    "epub_thumbnail",
    "epub_meta_embed",
]


def epub_thumbnail(fp):
    # type: (str) -> Image.Image
    """
    Creat thumbnail from EPUB document cover image.

    :param str fp: Filepath to EPUB document.
    :return: Thumbnail image as PIL Image object
    :rtype: Image.Image
    """
    meta = ebookmeta.get_metadata(fp)
    data = meta.cover_image_data
    img = Image.open(io.BytesIO(data))
    size = idk.sdk_opts.image_thumbnail_size
    img.thumbnail((size, size), resample=idk.LANCZOS)
    return ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)


def epub_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the EPUB file.

    :param str fp: Filepath to source EPUB file
    :param IsccMeta meta: Metadata to embed into EPUB
    :return: Filepath to the new PDF file with updated metadata
    :rtype: str
    """
    tempdir = tempfile.mkdtemp()
    tempepub = shutil.copy(fp, tempdir)
    new_meta = ebookmeta.get_metadata(tempepub)
    if meta.name:
        new_meta.title = meta.name
    if meta.description:
        new_meta.description = meta.description
    if meta.creator:
        if isinstance(meta.creator, str):
            new_meta.set_author_list_from_string(meta.creator)
    ebookmeta.set_metadata(tempepub, new_meta)
    return tempepub
