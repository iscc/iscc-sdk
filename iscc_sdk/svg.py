"""*SVG handling module*."""

import io
import re
import tempfile
from pathlib import Path

import xml.etree.ElementTree as StdET

import resvg_py
from defusedxml import ElementTree as ET
from loguru import logger as log
from PIL import Image, ImageEnhance

import iscc_sdk as idk


__all__ = [
    "svg_rasterize",
    "svg_meta_extract",
    "svg_meta_embed",
    "svg_meta_delete",
    "svg_thumbnail",
]

SVG_NS = "http://www.w3.org/2000/svg"
StdET.register_namespace("", SVG_NS)

_DIMENSION_RE = re.compile(r"^\s*([\d.]+(?:[eE][+-]?\d+)?)\s*(px|cm|mm|in|pt|pc)?\s*$")
_XML_COMMENT_RE = re.compile(rb"<!--.*?-->", re.DOTALL)
_SVG_MAX_RENDER_SIZE = 4096

# CSS absolute-unit to pixel conversion factors (at standard 96 DPI)
_UNIT_TO_PX = {
    None: 1.0,
    "px": 1.0,
    "cm": 96.0 / 2.54,
    "mm": 96.0 / 25.4,
    "in": 96.0,
    "pt": 96.0 / 72.0,
    "pc": 96.0 / 6.0,
}


def svg_rasterize(fp, max_size=_SVG_MAX_RENDER_SIZE):
    # type: (str|Path, int) -> Image.Image
    """
    Rasterize an SVG file to a PIL Image via resvg.

    Renders at native size when it fits within max_size, caps oversized SVGs.

    :param fp: Filepath to SVG file.
    :param max_size: Maximum pixel dimension on any side (default 4096).
    :return: Rasterized image as PIL Image object
    """
    fp = Path(fp)

    # Normalize CSS-unit dimensions to pixels (resvg only supports bare numbers/px)
    render_path, root = _svg_normalize_units(fp)

    # Render at native size when it fits, cap oversized SVGs
    native_w, native_h = _svg_native_size(root)
    if native_w and native_h and native_w <= max_size and native_h <= max_size:
        render_w, render_h = native_w, native_h
    else:
        render_w, render_h = max_size, max_size

    png_bytes = resvg_py.svg_to_bytes(
        svg_path=str(render_path),
        width=render_w,
        height=render_h,
        resources_dir=str(fp.parent),
    )
    return Image.open(io.BytesIO(bytes(png_bytes)))


def svg_meta_extract(fp):
    # type: (str|Path) -> dict
    """
    Extract metadata from SVG file.

    Parses title, description, and dimensions from SVG XML.

    :param fp: Filepath to SVG file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    tree = ET.parse(fp)
    root = tree.getroot()

    mapped = {}

    title_el = root.find(f"{{{SVG_NS}}}title")
    if title_el is not None and title_el.text:
        mapped["name"] = idk.text_sanitize(title_el.text.strip())

    desc_el = root.find(f"{{{SVG_NS}}}desc")
    if desc_el is not None and desc_el.text:
        mapped["description"] = idk.text_sanitize(desc_el.text.strip())

    width, height = _svg_native_size(root)
    if width:
        mapped["width"] = width
    if height:
        mapped["height"] = height

    return mapped


def svg_meta_embed(fp, meta):
    # type: (str|Path, idk.IsccMeta) -> Path
    """
    Embed metadata into a copy of the SVG file.

    Sets or updates title and desc elements in the SVG XML.

    :param fp: Filepath to source SVG file.
    :param meta: Metadata to embed into SVG.
    :return: Filepath to the new SVG file with updated metadata
    """
    fp = Path(fp)
    tree = ET.parse(fp)
    root = tree.getroot()

    if meta.name:
        title_el = root.find(f"{{{SVG_NS}}}title")
        if title_el is None:
            title_el = StdET.SubElement(root, f"{{{SVG_NS}}}title")
            # Insert title as first child
            root.remove(title_el)
            root.insert(0, title_el)
        title_el.text = meta.name

    if meta.description:
        desc_el = root.find(f"{{{SVG_NS}}}desc")
        if desc_el is None:
            desc_el = StdET.SubElement(root, f"{{{SVG_NS}}}desc")
            # Insert desc after title (or as first child)
            title_el = root.find(f"{{{SVG_NS}}}title")
            idx = list(root).index(title_el) + 1 if title_el is not None else 0
            root.remove(desc_el)
            root.insert(idx, desc_el)
        desc_el.text = meta.description

    tempdir = Path(tempfile.mkdtemp())
    outfile = tempdir / fp.name
    _svg_write_preserving_prolog(root, fp, outfile)

    log.debug(f"Embedding metadata in {fp.name}")
    return outfile


def svg_meta_delete(fp):
    # type: (str|Path) -> None
    """
    Delete all metadata from SVG file (in place).

    Removes title, desc, and metadata elements from the SVG XML.

    :param fp: Filepath to SVG file.
    """
    fp = Path(fp)

    tree = ET.parse(fp)
    root = tree.getroot()

    for tag in ("title", "desc", "metadata"):
        el = root.find(f"{{{SVG_NS}}}{tag}")
        if el is not None:
            root.remove(el)

    _svg_write_preserving_prolog(root, fp, fp)
    log.debug(f"Deleted all metadata from {fp.name}")


def svg_thumbnail(fp, img=None):
    # type: (str|Path, Image.Image|None) -> Image.Image
    """
    Create a thumbnail for an SVG file.

    :param fp: Filepath to SVG file.
    :param img: Pre-rasterized PIL Image to reuse (avoids re-rasterization).
    :return: Thumbnail image as PIL Image object
    """
    if img is None:
        img = svg_rasterize(fp)
    else:
        img = img.copy()

    size = idk.sdk_opts.image_thumbnail_size
    img = img.convert("RGB")
    img.thumbnail((size, size), resample=idk.LANCZOS)
    return ImageEnhance.Sharpness(img).enhance(1.4)


def _svg_write_preserving_prolog(root, source_fp, target_fp):
    # type: (StdET.Element, Path, Path) -> None
    """
    Serialize modified SVG root while preserving the original file's XML prolog.

    Keeps processing instructions, DOCTYPE, and comments that precede the root
    ``<svg>`` element, replacing only the element tree itself.

    :param root: Modified SVG root element to serialize.
    :param source_fp: Original SVG file (read for prolog extraction).
    :param target_fp: Output path (may be the same as source_fp for in-place writes).
    """
    original = source_fp.read_bytes()
    # Blank comments to find real <svg> position (preserves byte offsets)
    cleaned = _XML_COMMENT_RE.sub(lambda m: b" " * len(m.group()), original)
    svg_start = re.search(rb"<svg\b", cleaned)
    if svg_start is None:
        StdET.ElementTree(root).write(target_fp, xml_declaration=True, encoding="utf-8")
        return
    prolog = original[: svg_start.start()]
    # Ensure encoding declaration matches UTF-8 output
    prolog = re.sub(rb"encoding=[\"'][^\"']*[\"']", b'encoding="utf-8"', prolog)
    new_root = StdET.tostring(root, encoding="unicode").encode("utf-8")
    target_fp.write_bytes(prolog + new_root)


_CSS_UNIT_RE = re.compile(r"^\s*[\d.]+(?:[eE][+-]?\d+)?\s*(cm|mm|in|pt|pc)\s*$")


def _svg_normalize_units(fp):
    # type: (Path) -> tuple[Path, StdET.Element]
    """
    Return a render-ready SVG path with CSS-unit dimensions converted to pixels.

    resvg only supports bare numbers and px. If the SVG uses absolute CSS units
    (cm, mm, in, pt, pc), a temporary copy with pixel-equivalent values is created
    via targeted byte replacement to preserve processing instructions and DOCTYPE.
    Returns the original path unchanged if no conversion is needed.

    :param fp: Filepath to SVG file.
    :return: Tuple of (path to SVG file, parsed root element)
    """
    tree = ET.parse(fp)
    root = tree.getroot()

    w_attr = root.get("width", "")
    h_attr = root.get("height", "")

    needs_conversion = bool(_CSS_UNIT_RE.match(w_attr) or _CSS_UNIT_RE.match(h_attr))
    if not needs_conversion:
        return fp, root

    # Targeted byte replacement within <svg> tag preserves PIs, DOCTYPE, and comments
    content = fp.read_bytes()
    # Blank comments to find real <svg> tag position (preserves byte offsets)
    cleaned = _XML_COMMENT_RE.sub(lambda m: b" " * len(m.group()), content)
    svg_open = re.search(rb"<svg\b[^>]*>", cleaned)
    if svg_open:
        tag = content[svg_open.start() : svg_open.end()]
        for attr in ("width", "height"):
            val = root.get(attr, "")
            if not _CSS_UNIT_RE.match(val):
                continue
            px = _parse_svg_dimension(val)
            if px is not None:
                # Match full attribute pattern (handles whitespace around =)
                pattern = (
                    re.escape(attr.encode()) + rb"\s*=\s*([\"'])" + re.escape(val.encode()) + rb"\1"
                )
                repl = attr.encode() + b'="' + str(px).encode() + b'"'
                tag = re.sub(pattern, repl, tag, count=1)
        content = content[: svg_open.start()] + tag + content[svg_open.end() :]

    tempdir = Path(tempfile.mkdtemp())
    outfile = tempdir / fp.name
    outfile.write_bytes(content)
    return outfile, root


def _svg_native_size(root):
    # type: (StdET.Element) -> tuple[int|None, int|None]
    """
    Determine native pixel dimensions of an SVG from its XML attributes.

    Checks width/height attributes first, then falls back to viewBox.
    May return partial results like (width, None) when only one dimension is available.

    :param root: Parsed SVG root element.
    :return: Tuple of (width, height) — either or both may be None
    """
    width = _parse_svg_dimension(root.get("width"))
    height = _parse_svg_dimension(root.get("height"))
    if width and height:
        return width, height

    # Fall back to viewBox dimensions
    viewbox = root.get("viewBox")
    if viewbox:
        parts = viewbox.replace(",", " ").split()
        if len(parts) == 4:
            try:
                vb_w, vb_h = float(parts[2]), float(parts[3])
                # One explicit dimension + viewBox: compute missing side from aspect ratio
                if width and not height and vb_w > 0:
                    return width, int(width * vb_h / vb_w)
                if height and not width and vb_h > 0:
                    return int(height * vb_w / vb_h), height
                return int(vb_w), int(vb_h)
            except (ValueError, IndexError, ZeroDivisionError):
                pass

    return width, height


def _parse_svg_dimension(value):
    # type: (str|None) -> int|None
    """
    Parse an SVG dimension attribute value.

    Handles bare numbers, px, and absolute CSS units (cm, mm, in, pt, pc).
    Returns None for relative units (%, em, ex) or missing values.

    :param value: SVG dimension string (e.g. "100", "100px", "10cm").
    :return: Dimension as integer pixels or None
    """
    if value is None:
        return None
    match = _DIMENSION_RE.match(value)
    if match:
        num = float(match.group(1))
        unit = match.group(2)
        factor = _UNIT_TO_PX.get(unit)
        if factor is not None:
            return int(num * factor)
    return None
