"""*Image handling module*."""
import base64
import io
import os
import sys
import json
import tempfile
import subprocess
from copy import copy
from os.path import basename
from typing import Sequence
import jmespath
from iscc_schema import IsccMeta
from loguru import logger as log
from PIL import Image, ImageEnhance, ImageChops, ImageOps
import iscc_sdk as idk


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


def image_normalize(img):
    # type: (Image.Image) -> Sequence[int]
    """
    Normalize image for hash calculation.

    :param Image.Image img: Pillow Image Object
    :return: Normalized and flattened image as 1024-pixel array (from 32x32 gray pixels)
    :rtype: Sequence[int]
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
    im = img.resize((32, 32), Image.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.getdata()

    return pixels


def image_exif_transpose(img):
    # type: (Image.Image) -> Image.Image
    """
    Transpose image according to EXIF Orientation tag

    :param Image.Image img: Pillow Image Object
    :return: EXIF transposed image
    :rtype: Image.Image
    """
    img = ImageOps.exif_transpose(img)
    log.debug(f"Image exif transpose applied")
    return img


def image_fill_transparency(img):
    # type: (Image.Image) -> Image.Image
    """
    Add white background to image if it has alpha transparency.

    :param Image.Image img: Pillow Image Object
    :return: Image with transparency replaced by white background
    :rtype: Image.Image
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

    :param Image.Image img: Pillow Image Object
    :return: Image with uniform colored (empty) border removed.
    :rtype: Image.Image
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
    # type: (str) -> dict
    """
    Extract metadata from image.

    :param str fp: Filepath to image file.
    :return: Metadata mapped to IsccMeta schema
    :rtype: dict
    """
    cmd = [idk.exiv2json_bin(), "--all", fp]
    result = subprocess.run(cmd, capture_output=True, check=True)
    text = result.stdout.decode(sys.stdout.encoding, errors="ignore")

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
            log.debug(f"Mapping metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)

    with Image.open(fp) as img:
        mapped["width"], mapped["height"] = img.size

    return mapped


def image_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> None
    """
    Embed metadata into image.

    :param str fp: Filepath to image file
    :param IsccMeta meta: Metadata to embed into image
    :return: None
    """
    cmdf = "reg iscc http://purl.org/iscc/schema\n"
    cmdf += f"set Xmp.iscc.name {meta.name}\n"
    if meta.description:
        cmdf += f"set Xmp.iscc.description {meta.description}\n"
    if meta.meta:
        cmdf += f"set Xmp.iscc.meta {meta.meta}\n"
    if meta.license:
        cmdf += f"set Xmp.xmpRights.WebStatement {meta.license}\n"
    if meta.acquire:
        cmdf += f"set Xmp.plus.Licensor XmpText type=Bag\n"
        cmdf += f"set Xmp.plus.Licensor[1]/plus:LicensorURL XmpText {meta.acquire}\n"

    with tempfile.NamedTemporaryFile("w+b", delete=False) as outf:
        metafilepath = copy(outf.name)
        outf.write(cmdf.encode("utf-8"))
    cmd = [idk.exiv2_bin(), "-m", metafilepath, fp]
    log.debug(f"Embedding {meta.dict(exclude_unset=True)} in {basename(fp)}")
    subprocess.run(cmd, capture_output=True, check=True)
    os.remove(metafilepath)


def image_meta_delete(fp):
    # type: (str) -> None
    """
    Delete all metadata from image.

    :param str fp: Filepath to image file.
    :rtype: None
    """
    cmd = [idk.exiv2_bin(), "rm", fp]
    subprocess.run(cmd, capture_output=True)


def image_thumbnail(fp):
    # type: (str) -> Image.Image
    """
    Create a thumbnail for an image.

    :param str fp: Filepath to image file.
    :return: Thumbnail image as PIL Image object
    :rtype: Image.Image
    """
    size = idk.sdk_opts.image_thumbnail_size
    img = Image.open(fp)
    img.thumbnail((size, size), resample=Image.LANCZOS)
    return ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)


def image_to_data_url(img):
    # type: (Image.Image) -> str
    """
    Convert PIL Image object to WebP Data-URL.

    :param Image.Image img: PIL Image object to encode as WebP Data-URL.
    :return: Data-URL string
    :rtype: str
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
    "Xmp.dc.identifier": "identifier",
    "Xmp.xmp.Identifier": "identifier",
    "Xmp.dc.language": "language",
    "Iptc.Application2.Language": "language",
    "Exif.Image.ImageID": "identifier",
    "Exif.Photo.ImageUniqueID": "identifier",
}
