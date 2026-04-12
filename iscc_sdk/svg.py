"""*SVG handling module*."""

import io
import re
import tempfile
from pathlib import Path

import resvg_py
from lxml import etree
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
RDF_NS = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
DC_NS = "http://purl.org/dc/elements/1.1/"
CC_NS = "http://creativecommons.org/ns#"
ISCC_NS = "http://purl.org/iscc/schema/"

_RDF_NSMAP = {"rdf": RDF_NS, "dc": DC_NS, "cc": CC_NS, "iscc": ISCC_NS}

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


def _safe_parse(source):
    # type: (str|Path) -> etree._ElementTree
    """Parse XML with entity resolution and network access disabled.

    Rejects documents containing entity declarations to prevent entity
    expansion attacks and preserve safety when the prolog is copied to output.
    """
    content = Path(source).read_bytes()
    cleaned = _XML_COMMENT_RE.sub(b"", content)
    if b"<!ENTITY" in cleaned:
        raise etree.XMLSyntaxError("Entity declarations are forbidden in SVG files", None, 0, 0)
    parser = etree.XMLParser(resolve_entities=False, no_network=True)
    return etree.parse(source, parser)


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

    Extracts from ISCC namespace in RDF, SVG native elements, and Dublin Core/CC
    in RDF, with ISCC namespace taking highest priority.

    :param fp: Filepath to SVG file.
    :return: Metadata mapped to IsccMeta schema
    """
    fp = Path(fp)
    tree = _safe_parse(fp)
    root = tree.getroot()

    mapped = {}
    containers = _rdf_find_containers(root)

    # Priority: ISCC namespace > SVG native elements > DC/CC namespace
    for c in containers:
        _try_set(mapped, "name", _rdf_text(c, ISCC_NS, "name"))
        _try_set(mapped, "description", _rdf_text(c, ISCC_NS, "description"))
        _try_set(mapped, "meta", _rdf_text(c, ISCC_NS, "meta"))

    _try_set(mapped, "name", _svg_el_text(root, "title"))
    _try_set(mapped, "description", _svg_el_text(root, "desc"))

    for c in containers:
        _try_set(mapped, "name", _rdf_text(c, DC_NS, "title"))
        _try_set(mapped, "description", _rdf_text(c, DC_NS, "description"))
        _try_set(mapped, "creator", _rdf_text_or_bag(c, DC_NS, "creator"))
        _try_set(mapped, "rights", _rdf_text(c, DC_NS, "rights"))
        _try_set(mapped, "identifier", _rdf_text(c, DC_NS, "identifier"))
        _try_set(mapped, "language", _rdf_text(c, DC_NS, "language"))
        _try_set(mapped, "license", _rdf_resource(c, CC_NS, "license"))

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

    Writes to SVG native elements (title, desc) and RDF/Dublin Core in the
    metadata element, mirroring the image module's dual ISCC+DC strategy.

    :param fp: Filepath to source SVG file.
    :param meta: Metadata to embed into SVG.
    :return: Filepath to the new SVG file with updated metadata
    """
    fp = Path(fp)
    tree = _safe_parse(fp)
    root = tree.getroot()

    # SVG native elements
    if meta.name:
        title_el = root.find(f"{{{SVG_NS}}}title")
        if title_el is None:
            title_el = etree.SubElement(root, f"{{{SVG_NS}}}title")
            # Insert title as first child
            root.remove(title_el)
            root.insert(0, title_el)
        title_el.text = meta.name

    if meta.description:
        desc_el = root.find(f"{{{SVG_NS}}}desc")
        if desc_el is None:
            desc_el = etree.SubElement(root, f"{{{SVG_NS}}}desc")
            # Insert desc after title (or as first child)
            title_el = root.find(f"{{{SVG_NS}}}title")
            idx = list(root).index(title_el) + 1 if title_el is not None else 0
            root.remove(desc_el)
            root.insert(idx, desc_el)
        desc_el.text = meta.description

    # RDF metadata in <metadata> element
    desc_el = _rdf_ensure_description(root)
    if meta.name:
        _rdf_set_text(desc_el, ISCC_NS, "name", meta.name)
        _rdf_set_text(desc_el, DC_NS, "title", meta.name)
    if meta.description:
        _rdf_set_text(desc_el, ISCC_NS, "description", meta.description)
        _rdf_set_text(desc_el, DC_NS, "description", meta.description)
    if meta.meta:
        _rdf_set_text(desc_el, ISCC_NS, "meta", meta.meta)
    if meta.creator:
        _rdf_set_text(desc_el, DC_NS, "creator", meta.creator)
    if meta.rights:
        _rdf_set_text(desc_el, DC_NS, "rights", meta.rights)
    if meta.identifier:
        _rdf_set_text(desc_el, DC_NS, "identifier", meta.identifier)
    if meta.license:
        _rdf_set_resource(desc_el, CC_NS, "license", meta.license)

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

    tree = _safe_parse(fp)
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


def _try_set(d, key, value):
    # type: (dict, str, str|None) -> None
    """Set key in dict only if not already present and value is truthy."""
    if key not in d and value:
        d[key] = idk.text_sanitize(value)


def _svg_el_text(root, local_name):
    # type: (etree._Element, str) -> str|None
    """Get text content from a direct SVG child element."""
    el = root.find(f"{{{SVG_NS}}}{local_name}")
    if el is not None and el.text:
        return el.text.strip()
    return None


def _rdf_find_containers(root):
    # type: (etree._Element) -> list[etree._Element]
    """Find all RDF container elements (rdf:Description, cc:Work) inside ``<metadata>``."""
    metadata = root.find(f"{{{SVG_NS}}}metadata")
    if metadata is None:
        return []
    containers = []
    for tag in (f"{{{RDF_NS}}}Description", f"{{{CC_NS}}}Work"):
        containers.extend(metadata.findall(f".//{tag}"))
    return containers


def _rdf_text(desc, ns, local_name):
    # type: (etree._Element, str, str) -> str|None
    """Get text content of an RDF child element."""
    el = desc.find(f"{{{ns}}}{local_name}")
    if el is not None and el.text:
        return el.text.strip()
    return None


def _rdf_text_or_bag(desc, ns, local_name):
    # type: (etree._Element, str, str) -> str|None
    """Get text from element directly or from first rdf:li in rdf:Bag/rdf:Seq."""
    el = desc.find(f"{{{ns}}}{local_name}")
    if el is None:
        return None
    li = el.find(f".//{{{RDF_NS}}}li")
    if li is not None and li.text:
        return li.text.strip()
    if el.text:
        return el.text.strip()
    return None


def _rdf_resource(desc, ns, local_name):
    # type: (etree._Element, str, str) -> str|None
    """Get rdf:resource attribute of an RDF child element."""
    el = desc.find(f"{{{ns}}}{local_name}")
    if el is not None:
        return el.get(f"{{{RDF_NS}}}resource")
    return None


def _rdf_ensure_description(root):
    # type: (etree._Element) -> etree._Element
    """Ensure ``<metadata>/<rdf:RDF>/<rdf:Description>`` structure exists."""
    metadata = root.find(f"{{{SVG_NS}}}metadata")
    if metadata is None:
        metadata = etree.SubElement(root, f"{{{SVG_NS}}}metadata")
    rdf = metadata.find(f"{{{RDF_NS}}}RDF")
    if rdf is None:
        rdf = etree.SubElement(metadata, f"{{{RDF_NS}}}RDF", nsmap=_RDF_NSMAP)
    desc = rdf.find(f"{{{RDF_NS}}}Description")
    if desc is None:
        desc = etree.SubElement(rdf, f"{{{RDF_NS}}}Description")
        desc.set(f"{{{RDF_NS}}}about", "")
    return desc


def _rdf_set_text(desc, ns, local_name, value):
    # type: (etree._Element, str, str, str) -> None
    """Set text content of an RDF child element, creating it if needed.

    Clears existing children (e.g. rdf:Bag from Inkscape) to prevent stale
    structured values from shadowing the new text on re-extraction.
    """
    tag = f"{{{ns}}}{local_name}"
    el = desc.find(tag)
    if el is None:
        el = etree.SubElement(desc, tag)
    for child in list(el):
        el.remove(child)
    el.text = value


def _rdf_set_resource(desc, ns, local_name, url):
    # type: (etree._Element, str, str, str) -> None
    """Set rdf:resource attribute on an RDF child element, creating it if needed."""
    tag = f"{{{ns}}}{local_name}"
    el = desc.find(tag)
    if el is None:
        el = etree.SubElement(desc, tag)
    el.set(f"{{{RDF_NS}}}resource", url)


def _svg_write_preserving_prolog(root, source_fp, target_fp):
    # type: (etree._Element, Path, Path) -> None
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
        etree.ElementTree(root).write(target_fp, xml_declaration=True, encoding="utf-8")
        return
    prolog = original[: svg_start.start()]
    # Ensure encoding declaration matches UTF-8 output
    prolog = re.sub(rb"encoding=[\"'][^\"']*[\"']", b'encoding="utf-8"', prolog)
    new_root = etree.tostring(root, encoding="unicode").encode("utf-8")
    target_fp.write_bytes(prolog + new_root)


_CSS_UNIT_RE = re.compile(r"^\s*[\d.]+(?:[eE][+-]?\d+)?\s*(cm|mm|in|pt|pc)\s*$")


def _svg_normalize_units(fp):
    # type: (Path) -> tuple[Path, etree._Element]
    """
    Return a render-ready SVG path with CSS-unit dimensions converted to pixels.

    resvg only supports bare numbers and px. If the SVG uses absolute CSS units
    (cm, mm, in, pt, pc), a temporary copy with pixel-equivalent values is created
    via targeted byte replacement to preserve processing instructions and DOCTYPE.
    Returns the original path unchanged if no conversion is needed.

    :param fp: Filepath to SVG file.
    :return: Tuple of (path to SVG file, parsed root element)
    """
    tree = _safe_parse(fp)
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
    # type: (etree._Element) -> tuple[int|None, int|None]
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
