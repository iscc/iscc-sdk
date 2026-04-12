"""Tests for SVG handling module."""

import shutil

from PIL import Image

import iscc_sdk as idk
from iscc_sdk.svg import _parse_svg_dimension, _svg_write_preserving_prolog


def test_svg_rasterize(svg_file):
    img = idk.svg_rasterize(svg_file)
    assert isinstance(img, Image.Image)
    # Small SVGs render at native size (100x100), not upscaled to max_size
    assert img.width == 100
    assert img.height == 100
    assert img.mode == "RGBA"


def test_svg_meta_extract(svg_file):
    meta = idk.svg_meta_extract(svg_file)
    assert meta == {
        "name": "Red Circle",
        "description": "A simple red circle",
        "width": 100,
        "height": 100,
    }


def test_svg_meta_extract_no_metadata(tmp_path):
    fp = tmp_path / "bare.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="150">'
        "<rect width='200' height='150' fill='blue'/>"
        "</svg>"
    )
    meta = idk.svg_meta_extract(fp)
    assert meta == {"width": 200, "height": 150}


def test_svg_meta_extract_viewbox_fallback(tmp_path):
    fp = tmp_path / "viewbox.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 200">'
        "<rect width='300' height='200' fill='green'/>"
        "</svg>"
    )
    meta = idk.svg_meta_extract(fp)
    assert meta["width"] == 300
    assert meta["height"] == 200


def test_svg_meta_extract_no_dimensions(tmp_path):
    """SVG with no width/height/viewBox omits dimensions from metadata."""
    fp = tmp_path / "nodims.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<circle cx='50' cy='50' r='40' fill='red'/>"
        "</svg>"
    )
    meta = idk.svg_meta_extract(fp)
    assert "width" not in meta
    assert "height" not in meta


def test_svg_meta_extract_width_only(tmp_path):
    """Only the known dimension is reported when the other cannot be determined."""
    fp = tmp_path / "wonly.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50000">'
        "<rect width='100' height='100' fill='red'/>"
        "</svg>"
    )
    meta = idk.svg_meta_extract(fp)
    assert meta["width"] == 50000
    assert "height" not in meta


def test_svg_native_size_invalid_viewbox(tmp_path):
    """Invalid viewBox values return None dimensions."""
    from defusedxml import ElementTree as ET

    from iscc_sdk.svg import _svg_native_size

    fp = tmp_path / "bad_viewbox.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 abc def">'
        "<rect width='50' height='50' fill='blue'/>"
        "</svg>"
    )
    root = ET.parse(fp).getroot()
    w, h = _svg_native_size(root)
    assert w is None
    assert h is None


def test_svg_native_size_width_only_with_viewbox(tmp_path):
    """One explicit dimension + viewBox computes the missing side from aspect ratio."""
    from defusedxml import ElementTree as ET

    from iscc_sdk.svg import _svg_native_size

    fp = tmp_path / "widthonly.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="600" viewBox="0 0 200 100">'
        "<rect width='200' height='100' fill='green'/>"
        "</svg>"
    )
    root = ET.parse(fp).getroot()
    w, h = _svg_native_size(root)
    assert w == 600
    assert h == 300


def test_svg_native_size_height_only_with_viewbox(tmp_path):
    """Height-only + viewBox computes width from aspect ratio."""
    from defusedxml import ElementTree as ET

    from iscc_sdk.svg import _svg_native_size

    fp = tmp_path / "heightonly.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" height="300" viewBox="0 0 200 100">'
        "<rect width='200' height='100' fill='blue'/>"
        "</svg>"
    )
    root = ET.parse(fp).getroot()
    w, h = _svg_native_size(root)
    assert w == 600
    assert h == 300


def test_svg_meta_embed(svg_file):
    meta = idk.IsccMeta(name="New Title", description="New Description")
    new_file = idk.svg_meta_embed(svg_file, meta)
    assert new_file is not None

    extracted = idk.svg_meta_extract(new_file)
    assert extracted["name"] == "New Title"
    assert extracted["description"] == "New Description"


def test_svg_meta_embed_creates_elements(tmp_path):
    fp = tmp_path / "bare.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<rect width='50' height='50' fill='blue'/>"
        "</svg>"
    )
    meta = idk.IsccMeta(name="Added Title", description="Added Description")
    new_file = idk.svg_meta_embed(fp, meta)

    extracted = idk.svg_meta_extract(new_file)
    assert extracted["name"] == "Added Title"
    assert extracted["description"] == "Added Description"


def test_svg_thumbnail(svg_file):
    thumb = idk.svg_thumbnail(svg_file)
    assert isinstance(thumb, Image.Image)
    assert thumb.mode == "RGB"
    assert max(thumb.size) <= idk.sdk_opts.image_thumbnail_size


def test_svg_thumbnail_preloaded(svg_file):
    img = idk.svg_rasterize(svg_file)
    thumb = idk.svg_thumbnail(svg_file, img=img)
    assert isinstance(thumb, Image.Image)
    assert thumb.mode == "RGB"


def test_svg_rasterize_bounded(tmp_path):
    """Large SVGs are capped to prevent excessive memory usage."""
    fp = tmp_path / "large.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50000 30000">'
        "<rect width='50000' height='30000' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp)
    assert max(img.size) <= 4096


def test_svg_rasterize_custom_max_size(tmp_path):
    """Custom max_size bounds the output."""
    fp = tmp_path / "wide.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="10000" height="5000">'
        "<rect width='10000' height='5000' fill='blue'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp, max_size=512)
    assert max(img.size) <= 512


def test_svg_rasterize_one_dimension_capped(tmp_path):
    """SVG with one explicit large dimension + viewBox is still capped."""
    fp = tmp_path / "onewide.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50000" viewBox="0 0 100 100">'
        "<rect width='100' height='100' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp)
    assert max(img.size) <= 4096


def test_svg_rasterize_css_units_capped(tmp_path):
    """SVG with large absolute CSS units is still capped."""
    fp = tmp_path / "huge_cm.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200cm" height="100cm">'
        "<rect width='100%' height='100%' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp)
    assert max(img.size) <= 4096


def test_svg_rasterize_css_units_width_only(tmp_path):
    """SVG with CSS-unit width and no viewBox is bounded."""
    fp = tmp_path / "wideonly.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="200cm">'
        "<rect width='100%' height='100' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp, max_size=512)
    assert img.width <= 512


def test_svg_rasterize_css_units_height_only(tmp_path):
    """SVG with CSS-unit height and no viewBox is bounded."""
    fp = tmp_path / "tallonly.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" height="200cm">'
        "<rect width='100' height='100%' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp, max_size=512)
    assert max(img.size) <= 512


def test_svg_rasterize_extreme_aspect_ratio(tmp_path):
    """Extremely tall SVG is bounded on both axes."""
    fp = tmp_path / "extreme.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10000">'
        "<rect width='10' height='10000' fill='red'/>"
        "</svg>"
    )
    img = idk.svg_rasterize(fp, max_size=512)
    assert max(img.size) <= 512


def test_svg_extensionless_file(svg_file, tmp_path):
    """SVG without .svg extension is detected by mediatype and processed correctly."""
    noext = tmp_path / "tempfile"
    shutil.copy(svg_file, noext)
    result = idk.code_iscc(noext)
    assert result.dict(exclude={"generator"})["mediatype"] == "image/svg+xml"
    assert result.iscc.startswith("ISCC:K")


def test_svg_meta_delete(tmp_path):
    """svg_meta_delete removes title, desc, and metadata elements."""
    fp = tmp_path / "meta.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<title>My Title</title>"
        "<desc>My Desc</desc>"
        "<metadata><rdf/></metadata>"
        "<rect width='50' height='50' fill='blue'/>"
        "</svg>"
    )
    idk.svg_meta_delete(fp)
    meta = idk.svg_meta_extract(fp)
    assert "name" not in meta
    assert "description" not in meta


def test_svg_meta_delete_no_metadata(tmp_path):
    """svg_meta_delete on SVG without metadata elements is a no-op."""
    fp = tmp_path / "bare.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<rect width='50' height='50' fill='blue'/>"
        "</svg>"
    )
    idk.svg_meta_delete(fp)
    meta = idk.svg_meta_extract(fp)
    assert "name" not in meta


def test_image_meta_delete_svg(tmp_path):
    """image_meta_delete routes SVG files through svg_meta_delete."""
    fp = tmp_path / "meta.svg"
    fp.write_text(
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<title>Test Title</title>"
        "<desc>Test Desc</desc>"
        "<rect width='50' height='50' fill='red'/>"
        "</svg>"
    )
    idk.image_meta_delete(fp)
    meta = idk.svg_meta_extract(fp)
    assert "name" not in meta
    assert "description" not in meta


def test_svg_meta_embed_preserves_prolog(tmp_path):
    """Processing instructions before <svg> are preserved through metadata embed."""
    fp = tmp_path / "styled.svg"
    fp.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<?xml-stylesheet type="text/css" href="style.css"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<rect width='50' height='50' fill='red'/>"
        "</svg>"
    )
    meta = idk.IsccMeta(name="Title")
    new_file = idk.svg_meta_embed(fp, meta)
    content = new_file.read_text(encoding="utf-8")
    assert "xml-stylesheet" in content
    assert "style.css" in content
    extracted = idk.svg_meta_extract(new_file)
    assert extracted["name"] == "Title"


def test_svg_meta_delete_preserves_prolog(tmp_path):
    """Processing instructions before <svg> are preserved through metadata delete."""
    fp = tmp_path / "styled.svg"
    fp.write_text(
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<?xml-stylesheet type="text/css" href="style.css"?>\n'
        '<svg xmlns="http://www.w3.org/2000/svg" width="50" height="50">'
        "<title>Remove Me</title>"
        "<rect width='50' height='50' fill='red'/>"
        "</svg>"
    )
    idk.svg_meta_delete(fp)
    content = fp.read_text(encoding="utf-8")
    assert "xml-stylesheet" in content
    assert "style.css" in content
    assert "Remove Me" not in content


def test_svg_write_preserving_prolog_fallback(tmp_path):
    """Fallback to full ElementTree write when source has no <svg> tag."""
    import xml.etree.ElementTree as StdET

    fp = tmp_path / "nosvg.xml"
    fp.write_text("<root><child/></root>")
    root = StdET.fromstring("<root><child/></root>")
    outfile = tmp_path / "out.xml"
    _svg_write_preserving_prolog(root, fp, outfile)
    assert outfile.exists()
    assert b"<root>" in outfile.read_bytes()


def test_parse_svg_dimension():
    assert _parse_svg_dimension("100") == 100
    assert _parse_svg_dimension("100px") == 100
    assert _parse_svg_dimension("100.5") == 100
    assert _parse_svg_dimension("  200  ") == 200
    assert _parse_svg_dimension("50%") is None
    assert _parse_svg_dimension("10em") is None
    assert _parse_svg_dimension(None) is None
    assert _parse_svg_dimension("") is None
    # Absolute CSS units (96 DPI standard)
    assert _parse_svg_dimension("1in") == 96
    assert _parse_svg_dimension("72pt") == 96
    assert _parse_svg_dimension("6pc") == 96
    assert _parse_svg_dimension("2.54cm") == 96
    assert _parse_svg_dimension("25.4mm") == 96
    assert _parse_svg_dimension("10cm") == 377
    assert _parse_svg_dimension("210mm") == 793
    # Scientific notation
    assert _parse_svg_dimension("1e2") == 100
    assert _parse_svg_dimension("1.5E+3") == 1500
    assert _parse_svg_dimension("1e2px") == 100
