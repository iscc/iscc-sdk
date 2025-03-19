"""*Image handling module*."""

from pathlib import Path

import pillow_avif
import base64
import io
import shutil
import sys
import json
import tempfile
from typing import Sequence
import jmespath
from iscc_schema import IsccMeta
from loguru import logger as log
from PIL import Image, ImageEnhance, ImageChops, ImageOps
import iscc_sdk as idk
from pillow_heif import register_heif_opener

register_heif_opener()


__all__ = [
    "image_normalize",
    "image_exif_transpose",
    "image_fill_transparency",
    "image_trim_border",
    "image_meta_embed",
    "image_meta_extract",
    "image_meta_delete",
    "image_thumbnail",
    "image_to_data_url",
]


Image.MAX_IMAGE_PIXELS = idk.sdk_opts.image_max_pixels


def image_normalize(img):
    # type: (Image.Image) -> Sequence[int]
    """
    Normalize image for hash calculation.

    :param img: Pillow Image Object
    :return: Normalized and flattened image as 1024-pixel array (from 32x32 gray pixels)
    """

    # Transpose image according to EXIF Orientation tag
    if idk.sdk_opts.image_exif_transpose:
        img = image_exif_transpose(img)

    # Add white background to image if it has alpha transparency
    if idk.sdk_opts.image_fill_transparency:
        img = image_fill_transparency(img)

    # Trim uniform colored (empty) border if there is one
    if idk.sdk_opts.image_trim_border:
        img = image_trim_border(img)

    # Convert to grayscale
    img = img.convert("L")

    # Resize to 32x32
    im = img.resize((32, 32), idk.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.getdata()

    return pixels


def image_exif_transpose(img):
    # type: (Image.Image) -> Image.Image
    """
    Transpose image according to EXIF Orientation tag

    :param img: Pillow Image Object
    :return: EXIF transposed image
    """
    img = ImageOps.exif_transpose(img)
    log.debug(f"Image exif transpose applied")
    return img


def image_fill_transparency(img):
    # type: (Image.Image) -> Image.Image
    """
    Add white background to image if it has alpha transparency.

    :param img: Pillow Image Object
    :return: Image with transparency replaced by white background
    """
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    bg = Image.new("RGBA", img.size, (255, 255, 255))
    img = Image.alpha_composite(bg, img)
    log.debug(f"Image transparency filled with white background")
    return img


def image_trim_border(img):
    # type: (Image.Image) -> Image.Image
    """Trim uniform colored (empty) border.

    Takes the upper left pixel as reference for border color.

    :param img: Pillow Image Object
    :return: Image with uniform colored (empty) border removed.
    """

    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox != (0, 0) + img.size:
        log.debug(f"Image has been trimmed")
        return img.crop(bbox)
    return img


def image_meta_extract(fp):
    # type: (str|Path) -> dict
    """
    Extract metadata from image.

    :param fp: Filepath to image file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    args = ["--all", fp]
    result = idk.run_exiv2json(args)
    encoding = sys.stdout.encoding or "utf-8"
    text = result.stdout.decode(encoding, errors="ignore")

    # We may get all sorts of crazy control-chars, delete them.
    mpa = dict.fromkeys(range(32))
    clean = text.translate(mpa)

    meta = json.loads(clean)
    mapped = dict()
    done = set()
    for tag, mapped_field in IMAGE_META_MAP.items():
        if mapped_field in done:
            continue
        value = jmespath.search(tag, meta)
        if value:
            if isinstance(value, dict):
                value = jmespath.search('lang."x-default"', value)
                if not value:  # pragma: no cover
                    log.critical(f"Structured image metdata skipped: {value}")
                    continue
            log.debug(f"Mapping image metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)

    with Image.open(fp) as img:
        mapped["width"], mapped["height"] = img.size

    return mapped


def image_meta_embed(fp, meta):
    # type: (str|Path, IsccMeta) -> Path
    """
    Embed metadata into a copy of the image file.

    :param fp: Filepath to source image file
    :param meta: Metadata to embed into image
    :return: Filepath to the new image file with updated metadata
    """
    fp = Path(fp)
    cmdf = "reg iscc http://purl.org/iscc/schema\n"
    cmdf += "reg dc http://purl.org/dc/elements/1.1/\n"

    if meta.name:
        cmdf += f"set Xmp.iscc.name {meta.name}\n"
        cmdf += f"set Xmp.dc.title {meta.name}\n"
    if meta.description:
        cmdf += f"set Xmp.iscc.description {meta.description}\n"
        cmdf += f"set Xmp.dc.description {meta.description}\n"
    if meta.meta:
        cmdf += f"set Xmp.iscc.meta {meta.meta}\n"
    if meta.license:
        cmdf += f"set Xmp.xmpRights.WebStatement {meta.license}\n"
    if meta.acquire:
        cmdf += f"set Xmp.plus.Licensor XmpText type=Bag\n"
        cmdf += f"set Xmp.plus.Licensor[1]/plus:LicensorURL XmpText {meta.acquire}\n"
    if meta.creator:
        cmdf += f"set Xmp.dc.creator {meta.creator}\n"
    if meta.rights:
        cmdf += f"set Xmp.dc.rights {meta.rights}\n"
    if meta.identifier:
        cmdf += f"set Xmp.dc.identifier {meta.identifier}\n"

    # Create temp filepaths
    tempdir = Path(tempfile.mkdtemp())
    metafile = tempdir / "meta.txt"
    imagefile = Path(shutil.copy(fp, tempdir))

    # Store metadata
    with open(metafile, "wt", encoding="utf-8") as outf:
        outf.write(cmdf)

    # Embed metaadata
    args = ["-m", metafile, imagefile]
    log.debug(f"Embedding {meta.dict(exclude_unset=True)} in {imagefile.name}")
    idk.run_exiv2(args)
    return imagefile


def image_meta_delete(fp):
    # type: (str|Path) -> None
    """
    Delete all metadata from image.

    :param fp: Filepath to image file.
    """
    fp = Path(fp)
    args = ["rm", fp]
    return idk.run_exiv2(args)


def image_thumbnail(fp):
    # type: (str|Path) -> Image.Image
    """
    Create a thumbnail for an image.

    :param fp: Filepath to image file.
    :return: Thumbnail image as PIL Image object
    """
    fp = Path(fp)
    size = idk.sdk_opts.image_thumbnail_size
    img = Image.open(fp)

    # Convert to RGB before resizing
    img = img.convert("RGB")

    img.thumbnail((size, size), resample=idk.LANCZOS)
    return ImageEnhance.Sharpness(img).enhance(1.4)


def image_to_data_url(img):
    # type: (Image.Image) -> str
    """
    Convert PIL Image object to WebP Data-URL.

    :param img: PIL Image object to encode as WebP Data-URL.
    :return: Data-URL string
    """
    quality = idk.sdk_opts.image_thumbnail_quality
    raw = io.BytesIO()
    img.save(raw, format="WEBP", lossless=False, quality=quality, method=6)
    raw.seek(0)
    enc = base64.b64encode(raw.read()).decode("ascii")
    return "data:image/webp;base64," + enc


IMAGE_META_MAP = {
    "Xmp.iscc.name": "name",
    "Xmp.iscc.description": "description",
    "Xmp.iscc.meta": "meta",
    "Xmp.dc.title": "name",
    "Xmp.xmp.Nickname": "name",
    "Xmp.xmpDM.shotName": "name",
    "Xmp.photoshop.Headline": "name",
    "Xmp.iptcExt.AOTitle": "name",
    "Iptc.Application2.Headline": "name",
    "Iptc.Application2.BylineTitle": "name",
    "Iptc.Application2.ObjectName": "name",
    "Exif.Image.XPTitle": "name",
    "Xmp.dc.description": "description",
    "Xmp.dc.creator": "creator",
    "Iptc.Application2.Byline": "creator",
    "Exif.Image.Artist": "creator",
    "Xmp.xmpRights.WebStatement": "license",
    "Xmp.plus.Licensor[0].plus.LicensorURL": "acquire",
    "Xmp.dc.rights": "rights",
    "Xmp.dc.identifier": "identifier",
    "Xmp.xmp.Identifier": "identifier",
    "Xmp.dc.language": "language",
    "Iptc.Application2.Language": "language",
    "Exif.Image.ImageID": "identifier",
    "Exif.Photo.ImageUniqueID": "identifier",
}
