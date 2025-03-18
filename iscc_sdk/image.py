"""*Image handling module*."""

import pillow_avif
import base64
import io
import shutil
import sys
import json
import tempfile
from os.path import basename, join
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
    im = img.resize((32, 32), idk.BICUBIC)

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
    # Use exiv2 with -pa to get all metadata in a readable format
    args = ["-pa", fp]
    result = idk.run_exiv2(args)
    encoding = sys.stdout.encoding or "utf-8"
    text = result.stdout.decode(encoding, errors="ignore")

    # Parse the exiv2 output into a structured format
    meta_dict = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue

        # Split the line into key and value parts
        parts = line.split(None, 1)
        if len(parts) == 2:
            key, value = parts
            # Split the key into namespace, group, and tag
            key_parts = key.split(".")
            if len(key_parts) >= 2:
                namespace = key_parts[0]
                if namespace not in meta_dict:
                    meta_dict[namespace] = {}

                # Handle different key formats
                if len(key_parts) >= 3:
                    group = key_parts[1]
                    tag = ".".join(key_parts[2:])

                    if group not in meta_dict[namespace]:
                        meta_dict[namespace][group] = {}

                    meta_dict[namespace][group][tag] = value
                else:
                    # Handle simpler key format
                    group = key_parts[1]
                    meta_dict[namespace][group] = value

    # Map the extracted metadata to IsccMeta schema
    mapped = dict()
    done = set()

    # Helper function to search in the parsed metadata structure
    def search_meta(path):
        parts = path.split(".")
        if len(parts) < 3:
            return None

        namespace, group, tag = parts[0], parts[1], ".".join(parts[2:])

        if namespace in meta_dict and group in meta_dict[namespace]:
            if isinstance(meta_dict[namespace][group], dict) and tag in meta_dict[namespace][group]:
                return meta_dict[namespace][group][tag]
        return None

    # Helper function to clean metadata values
    def clean_value(value):
        if not isinstance(value, str):
            return value

        # Clean LangAlt format: "LangAlt     1  lang="x-default" Concentrated Cat"
        if "LangAlt" in value and 'lang="x-default"' in value:
            parts = value.split('lang="x-default"')
            if len(parts) > 1:
                return parts[1].strip()

        # Clean XmpSeq format: "XmpSeq      1  Some Cat Lover"
        if "XmpSeq" in value and "  " in value:
            parts = value.split("  ")
            if len(parts) > 2:
                return parts[-1].strip()

        # Clean other potential formats with similar patterns
        if "  " in value:
            # Check if the value starts with a known format indicator
            known_formats = ["XmpText", "XmpBag", "XmpAlt"]
            for fmt in known_formats:
                if value.startswith(fmt):
                    parts = value.split("  ")
                    if len(parts) > 2:
                        return parts[-1].strip()

        return value

    # Map metadata using the IMAGE_META_MAP
    for tag, mapped_field in IMAGE_META_MAP.items():
        if mapped_field in done:
            continue

        value = search_meta(tag)
        if value:
            # Handle structured metadata if needed
            if isinstance(value, dict):
                if "lang" in value and "x-default" in value["lang"]:
                    value = value["lang"]["x-default"]
                else:  # pragma: no cover
                    log.critical(f"Structured image metadata skipped: {value}")
                    continue

            # Clean the value to remove format information
            value = clean_value(value)

            log.debug(f"Mapping image metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)

    # Special handling for Licensor URL (acquire field)
    licensor_url = search_meta("Xmp.plus.Licensor.plus.LicensorURL")
    if licensor_url:
        mapped["acquire"] = clean_value(licensor_url)
        log.debug(f"Mapping image metadata: Xmp.plus.Licensor.plus.LicensorURL -> acquire -> {licensor_url}")

    # Add image dimensions
    with Image.open(fp) as img:
        mapped["width"], mapped["height"] = img.size

    return mapped


def image_meta_embed(fp, meta):
    # type: (str, IsccMeta) -> str
    """
    Embed metadata into a copy of the image file.

    :param str fp: Filepath to source image file
    :param IsccMeta meta: Metadata to embed into image
    :return: Filepath to the new image file with updated metadata
    :rtype: str
    """
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

    # Create temp filepaths
    tempdir = tempfile.mkdtemp()
    metafile = join(tempdir, "meta.txt")
    imagefile = shutil.copy(fp, tempdir)

    # Store metadata
    with open(metafile, "wt", encoding="utf-8") as outf:
        outf.write(cmdf)

    # Embed metaadata
    args = ["-m", metafile, imagefile]
    log.debug(f"Embedding {meta.dict(exclude_unset=True)} in {basename(imagefile)}")
    idk.run_exiv2(args)
    return imagefile


def image_meta_delete(fp):
    # type: (str) -> None
    """
    Delete all metadata from image.

    :param str fp: Filepath to image file.
    :rtype: None
    """
    args = ["rm", fp]
    return idk.run_exiv2(args)


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
    img.thumbnail((size, size), resample=idk.LANCZOS)
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
    "Xmp.plus.Licensor[1]/plus:LicensorURL": "acquire",
    "Xmp.plus.Licensor.plus.LicensorURL": "acquire",
    "Xmp.dc.rights": "rights",
    "Xmp.dc.identifier": "identifier",
    "Xmp.xmp.Identifier": "identifier",
    "Xmp.dc.language": "language",
    "Iptc.Application2.Language": "language",
    "Exif.Image.ImageID": "identifier",
    "Exif.Photo.ImageUniqueID": "identifier",
}
