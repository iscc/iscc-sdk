"""*Image handling module*."""

import base64
import io
import shutil
import tempfile
import threading
from pathlib import Path

import exiv2
import iscc_lib as il
from loguru import logger as log
from PIL import Image, ImageChops, ImageEnhance, ImageOps, PngImagePlugin
from pillow_heif import register_heif_opener

import iscc_sdk as idk

__all__ = [
    "image_exif_transpose",
    "image_fill_transparency",
    "image_meta_delete",
    "image_meta_embed",
    "image_meta_extract",
    "image_normalize",
    "image_strip_metadata",
    "image_thumbnail",
    "image_to_data_url",
    "image_trim_border",
    "image_trim_tolerant",
    "is_featureless_image_code",
]


register_heif_opener()
_exiv2_lock = threading.Lock()


Image.MAX_IMAGE_PIXELS = idk.sdk_opts.image_max_pixels

# Upper bound for repeated tolerant trim passes (guards against crafted nested borders)
TRIM_MAX_PASSES = 16

# Photoshop-exported PNGs often embed large zTXt chunks (e.g. tiff:37724
# layer data) that decompress past PIL's 1 MB default. Allow up to 4 MB so
# such covers don't fail thumbnail extraction.
PngImagePlugin.MAX_TEXT_CHUNK = 4 * 1024 * 1024


def image_normalize(img, **options):
    # type: (Image.Image, Any) -> Sequence[int]
    """
    Normalize image for hash calculation.

    :param img: Pillow Image Object
    :param options: Keyword arguments forwarded to ``sdk_opts``:
        **image_exif_transpose** - Transpose image according to EXIF Orientation tag. Default: True;
        **image_fill_transparency** - Add white background to transparent images. Default: True;
        **image_trim_border** - Crop uniform colored borders. Default: True;
        **image_trim_tolerant** - Repeated tolerant crop of near-uniform borders (instead of the
        exact crop). Default: True
    :return: Normalized and flattened image as 1024-pixel array (from 32x32 gray pixels)
    """
    opts = idk.sdk_opts.override(options)

    # Transpose image according to EXIF Orientation tag
    if opts.image_exif_transpose:
        img = image_exif_transpose(img)

    # Add white background to image if it has alpha transparency
    if opts.image_fill_transparency:
        img = image_fill_transparency(img)

    # Trim near-uniform (tolerant) or uniform (exact) colored border if there is one
    if opts.image_trim_border:
        img = image_trim_tolerant(img) if opts.image_trim_tolerant else image_trim_border(img)

    # Convert to grayscale
    img = img.convert("L")

    # Resize to 32x32
    im = img.resize((32, 32), idk.BICUBIC)

    # A flattened sequence of grayscale pixel values (1024 pixels)
    pixels = im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata()

    return pixels


def image_exif_transpose(img):
    # type: (Image.Image) -> Image.Image
    """
    Transpose image according to EXIF Orientation tag

    :param img: Pillow Image Object
    :return: EXIF transposed image
    """
    img = ImageOps.exif_transpose(img)
    log.debug("Image exif transpose applied")
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
    if img.mode in ("RGB", "L"):
        bbox = image_border_bbox(img, 0)
    else:
        # Other modes keep Pillow difference semantics (alpha-only bbox for RGBA/LA, palette indices)
        bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff)
        bbox = diff.getbbox()
    if bbox is None or bbox == (0, 0) + img.size:
        return img
    log.debug("Image has been trimmed")
    return img.crop(bbox)


def image_trim_tolerant(img, tolerance=16):
    # type: (Image.Image, int) -> Image.Image
    """Trim near-uniform colored borders repeatedly until stable.

    Each pass takes the upper left pixel as reference for border color and crops to the bounding
    box of all pixels where any RGB channel differs from the reference by more than `tolerance`.
    Passes repeat until a pass crops nothing (no pixel differs or the bounding box covers the
    whole image), or at most `TRIM_MAX_PASSES` times.

    :param img: Pillow Image Object
    :param tolerance: Maximum per-channel difference (0-255) of a border pixel to the reference
    :return: Image with near-uniform colored borders removed.
    """
    # "RGB" and "L" give the same mask directly, other modes are compared in RGB
    mask_img = img if img.mode in ("RGB", "L") else img.convert("RGB")
    for passes in range(TRIM_MAX_PASSES):
        bbox = image_border_bbox(mask_img, tolerance)
        if bbox is None or bbox == (0, 0) + mask_img.size:
            break
        img, mask_img = img.crop(bbox), mask_img.crop(bbox)
    else:
        passes = TRIM_MAX_PASSES
    if passes:
        log.debug(f"Image has been trimmed with tolerance ({passes} passes)")
    return img


def image_border_bbox(img, tolerance):
    # type: (Image.Image, int) -> tuple[int, int, int, int] | None
    """Bounding box of pixels that differ from the upper left pixel by more than `tolerance`.

    A pixel counts as different if any of its channels differs by more than `tolerance`.

    :param img: Pillow Image Object in mode "RGB" or "L"
    :param tolerance: Maximum per-channel difference (0-255) of a border pixel to the reference
    :return: Bounding box (left, upper, right, lower) or None if no pixel differs.
    """
    ref = img.getpixel((0, 0))
    ref = ref if isinstance(ref, tuple) else (ref,)
    # Per-band lookup table maps values within tolerance of the reference to 0
    lut = [255 if abs(v - c) > tolerance else 0 for c in ref for v in range(256)]
    return img.point(lut).getbbox()


def is_featureless_image_code(iscc):
    # type: (str) -> bool
    """Check if an ISCC holds a featureless Image-Code.

    Featureless images (uniform colors, one-axis brightness gradients, plain stripes, some symmetric
    graphics) get nearly identical Image-Codes that match each other regardless of content. Code
    generation is unaffected; applications such as matching services use this check to skip them,
    like the quality score of Meta's PDQ lets applications discard featureless images.

    Rule: An Image-Code is featureless if any complete 64-bit segment of its body has fewer than 8
    bits set to 1. Segments are consecutive 64-bit big-endian words from the start of the body.
    Trailing bits of a body whose length is not a multiple of 64 are not checked. A regular segment
    has 32 one-bits (median split of 64 DCT coefficients), fewer than 8 means at least 26 ties.

    - Image-Code unit (MainType CONTENT, SubType IMAGE): checked by the rule.
    - ISCC-CODE: its Image-Code unit is checked, False if it has none.
    - Any other ISCC unit: False.

    :param iscc: ISCC string (with or without "ISCC:" prefix)
    :return: True if the ISCC holds a featureless Image-Code
    :raises ValueError: If the Image-Code is shorter than 64 bits and cannot be judged.
    """
    mt, st, _, _, body = il.iscc_decode(iscc)
    if mt == il.MT.ISCC:
        return any(is_featureless_image_code(unit) for unit in il.iscc_decompose(iscc))
    if mt != il.MT.CONTENT or st != il.ST.IMAGE:
        return False
    if len(body) < 8:
        raise ValueError(f"Image-Code with {len(body) * 8} bits is too short to judge (min 64)")
    words = (int.from_bytes(body[i : i + 8], "big") for i in range(0, len(body) - 7, 8))
    return any(word.bit_count() < 8 for word in words)


def image_meta_extract(fp, file_name=None):
    # type: (str|Path, Optional[str]) -> dict
    """
    Extract metadata from image using native exiv2 bindings.

    :param fp: Filepath to image file.
    :param file_name: Custom filename for MIME type guessing (overrides actual filename).
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    mt, _ = idk.mediatype_and_mode(fp, file_name=file_name)
    if mt == "image/svg+xml":
        return idk.svg_meta_extract(fp)
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
            if meta_dict.get(tag):
                try:
                    mapped[mapped_field] = idk.text_sanitize(meta_dict[tag])
                except Exception as e:  # pragma: no cover
                    log.error(f"Failed to sanitize {meta_dict[tag]}: {e}")
                    continue

        # Add image dimensions
        mapped["width"], mapped["height"] = img_exiv.pixelWidth(), img_exiv.pixelHeight()

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
    mt, _ = idk.mediatype_and_mode(fp)
    if mt == "image/svg+xml":
        return idk.svg_meta_embed(fp, meta)

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
    mt, _ = idk.mediatype_and_mode(fp)
    if mt == "image/svg+xml":
        return idk.svg_meta_delete(fp)
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
    mt, _ = idk.mediatype_and_mode(fp)
    if mt == "image/svg+xml":
        return idk.svg_thumbnail(fp)
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
    data = list(img.get_flattened_data() if hasattr(img, "get_flattened_data") else img.getdata())
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
        try:
            # XMP struct containers stringify as the placeholder 'type="Struct"'
            if is_xmp and datum.value().xmpStruct():
                continue
            # Metadatum.toString() raises a catchable exiv2.Exiv2Error on values that
            # cannot be converted to UTF-8, while str(datum.value()) escalates the same
            # C++ exception to std::terminate and aborts the process.
            # Windows XP* tags are UCS-2 bytes that only print() decodes to text.
            value = datum.print() if key.startswith("Exif.Image.XP") else datum.toString()
            value = decode_latin1_fallback(value)
        except Exception as e:
            log.warning(f"Skipping unreadable metadata field {key}: {e}")
            continue

        value = value.strip()

        # Clean XMP values from language qualifiers
        if is_xmp:
            value = _clean_xmp_value(value)

        result[key] = value

    return result


def decode_latin1_fallback(value):
    # type: (str) -> str
    """
    Re-decode a metadata value that holds bytes which are not valid UTF-8 as Latin-1.

    exiv2 returns such bytes as lone surrogates. Legacy IPTC text is the common case, as IPTC
    defaults to Latin-1 when no UTF-8 CodedCharacterSet is declared.

    :param value: Metadata value as returned by exiv2
    :return: The value unchanged if it is valid text, otherwise its bytes decoded as Latin-1
    :raises UnicodeEncodeError: If the value holds surrogates that do not stand for raw bytes
    """
    try:
        value.encode("utf-8")
    except UnicodeEncodeError:
        return value.encode("utf-8", "surrogateescape").decode("latin-1")
    return value


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
