"""*Image handling module*."""

from pathlib import Path
import exiv2
import base64
import io
import shutil
import tempfile
from typing import Sequence
from iscc_schema import IsccMeta
from loguru import logger as log
from PIL import Image, ImageEnhance, ImageChops, ImageOps
import iscc_sdk as idk
from pillow_heif import register_heif_opener
import threading


__all__ = [
    "image_normalize",
    "image_exif_transpose",
    "image_fill_transparency",
    "image_trim_border",
    "image_meta_embed",
    "image_meta_extract",
    "image_meta_delete",
    "image_strip_metadata",
    "image_thumbnail",
    "image_to_data_url",
]


register_heif_opener()
_exiv2_lock = threading.Lock()


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
    :return: RGB Image with transparency replaced by a white background
    """
    white = (255, 255, 255)

    # If the image is already RGB, there's nothing to do.
    if img.mode == "RGB":
        log.debug("Image is already RGB, no transparency removal needed.")
        return img

    # Handle modes with explicit alpha channels
    if img.mode in ("RGBA", "LA"):
        log.debug(f"Whitening alpha transparency for mode {img.mode}")
        background = Image.new("RGB", img.size, white)
        # Paste using the alpha channel as a mask
        background.paste(img, mask=img.getchannel("A"))
        return background

    # Handle Palette mode
    elif img.mode == "P":
        # Check if transparency info exists for the palette
        if "transparency" in img.info:
            log.debug("Whitening palette transparency")
            # Convert to RGBA to handle palette transparency correctly
            image_rgba = img.convert("RGBA")
            background = Image.new("RGB", img.size, white)
            # Paste the RGBA version onto the RGB background
            background.paste(image_rgba, mask=image_rgba.getchannel("A"))
            return background
        else:
            # Palette image without transparency, just convert to RGB
            log.debug("Converting opaque P image to RGB")
            return img.convert("RGB")

    # Handle other modes (like L, CMYK, etc.) by converting to RGB
    else:
        log.debug(f"Converting image from mode {img.mode} to RGB")
        return img.convert("RGB")


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
    Extract metadata from image using native exiv2 bindings.

    :param fp: Filepath to image file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    with _exiv2_lock:
        img_exiv = exiv2.ImageFactory.open(fp.as_posix())
        img_exiv.readMetadata()

        # Read and process all metadata types: EXIF, XMP, IPTC
        meta_dict = {}
        meta_dict.update(_process_metadata(img_exiv.exifData()))
        meta_dict.update(_process_metadata(img_exiv.xmpData(), is_xmp=True))
        meta_dict.update(_process_metadata(img_exiv.iptcData()))

        # Map metadata to schema fields
        mapped = {}
        for tag, mapped_field in IMAGE_META_MAP.items():
            if mapped_field in mapped:
                continue
            if tag in meta_dict and meta_dict[tag]:
                try:
                    mapped[mapped_field] = idk.text_sanitize(meta_dict[tag])
                except Exception as e:  # pragma: no cover
                    log.error(f"Failed to sanitize {meta_dict[tag]}: {e}")
                    continue

        # Add image dimensions
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

    # Create temp directory and copy the image
    tempdir = Path(tempfile.mkdtemp())
    imagefile = Path(shutil.copy(fp, tempdir))

    with _exiv2_lock:
        # Register XMP namespaces before opening image
        exiv2.XmpProperties.registerNs("http://purl.org/iscc/schema/", "iscc")
        exiv2.XmpProperties.registerNs("http://purl.org/dc/elements/1.1/", "dc")
        exiv2.XmpProperties.registerNs("http://ns.useplus.org/", "plus")
        exiv2.XmpProperties.registerNs("http://ns.adobe.com/xap/1.0/rights/", "xmpRights")

        # Open the copied image with exiv2
        img_exiv = exiv2.ImageFactory.open(str(imagefile))
        img_exiv.readMetadata()

        # Get metadata collections
        xmp_data = img_exiv.xmpData()

        # Set simple metadata values
        if meta.name:
            xmp_data["Xmp.iscc.name"] = meta.name
            xmp_data["Xmp.dc.title"] = meta.name
        if meta.description:
            xmp_data["Xmp.iscc.description"] = meta.description
            xmp_data["Xmp.dc.description"] = meta.description
        if meta.meta:
            xmp_data["Xmp.iscc.meta"] = meta.meta
        if meta.license:
            xmp_data["Xmp.xmpRights.WebStatement"] = meta.license
        if meta.creator:
            xmp_data["Xmp.dc.creator"] = meta.creator
        if meta.rights:
            xmp_data["Xmp.dc.rights"] = meta.rights
        if meta.identifier:
            xmp_data["Xmp.dc.identifier"] = meta.identifier

        # Set complex metadata values
        if meta.acquire:
            # Set the Licensor URL
            # First create a bag value
            licensor_bag = exiv2.XmpTextValue()
            licensor_bag.setXmpArrayType(exiv2.XmpValue.XmpArrayType.xaBag)
            xmp_data["Xmp.plus.Licensor"] = licensor_bag

            # Then set the LicensorURL with the struct path
            xmp_data["Xmp.plus.Licensor[1]/plus:LicensorURL"] = meta.acquire

        # Write metadata back to the file
        img_exiv.writeMetadata()

        log.debug(f"Embedding {meta.dict(exclude_unset=True)} in {imagefile.name}")
        return imagefile


def image_meta_delete(fp):
    # type: (str|Path) -> None
    """
    Delete all metadata from image.

    :param fp: Filepath to image file.
    """
    fp = Path(fp)
    img_exiv = exiv2.ImageFactory.open(str(fp))
    img_exiv.readMetadata()

    # Clear all metadata
    img_exiv.exifData().clear()
    img_exiv.xmpData().clear()
    img_exiv.iptcData().clear()

    # Write the cleared metadata back to the file
    img_exiv.writeMetadata()

    log.debug(f"Deleted all metadata from {fp.name}")


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


def image_strip_metadata(img):
    # type: (Image.Image) -> Image.Image
    """
    Strip all metadata from Pillow Image object.

    :param img: PIL Image object to strip metadata from.
    :return: Image.Image
    """
    data = list(img.getdata())
    new_img = Image.new(img.mode, img.size)
    new_img.putdata(data)
    return new_img


def image_to_data_url(img):
    # type: (Image.Image) -> str
    """
    Convert PIL Image object to WebP Data-URL.

    :param img: PIL Image object to encode as WebP Data-URL.
    :return: Data-URL string
    """
    format_ = idk.sdk_opts.image_thumbnail_format
    quality = idk.sdk_opts.image_thumbnail_quality
    img = image_strip_metadata(img)
    raw = io.BytesIO()
    img.save(raw, format=format_, quality=quality)
    raw.seek(0)
    enc = base64.b64encode(raw.read()).decode("ascii")
    return f"data:image/{format_.lower()};base64," + enc


def _clean_xmp_value(value):
    # type: (str) -> str
    """
    Clean XMP value by removing language qualifiers.

    :param value: XMP value string that might contain language qualifier
    :return: Cleaned value string
    """
    # Remove language qualifier like 'lang="x-default" '
    if value.startswith('lang="') and '"' in value[6:]:
        lang_end = value.find('"', 6)
        if lang_end > 0 and len(value) > lang_end + 2:
            return value[lang_end + 2 :].strip()
    return value


def _process_metadata(metadata, is_xmp=False):
    # type: (object, bool) -> dict
    """
    Process metadata from exiv2 data collections.

    :param metadata: exiv2 metadata collection (exifData, xmpData, or iptcData)
    :param is_xmp: Whether the metadata is XMP (for special processing)
    :return: Dictionary of processed metadata
    """
    result = {}
    for datum in metadata:
        key = datum.key()
        raw_value = datum.value
        value = raw_value() if callable(raw_value) else raw_value

        if not isinstance(value, str):
            if hasattr(value, "to_string"):
                value = value.to_string()
            else:
                value = str(value)

        value = value.strip()

        # Clean XMP values from language qualifiers
        if is_xmp:
            value = _clean_xmp_value(value)

        result[key] = value

    return result


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
    "Xmp.plus.Licensor[1]/plus:LicensorURL": "acquire",
    "Xmp.dc.rights": "rights",
    "Xmp.dc.identifier": "identifier",
    "Xmp.xmp.Identifier": "identifier",
    "Xmp.dc.language": "language",
    "Iptc.Application2.Language": "language",
    "Exif.Image.ImageID": "identifier",
    "Exif.Photo.ImageUniqueID": "identifier",
}
