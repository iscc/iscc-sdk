import io
import struct
import zipfile
import zlib

import pytest
from PIL import Image as PILImage
from PIL.Image import Image

import iscc_sdk as idk


def test_epub_thumbnail(epub_file):
    thumb = idk.epub_thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_text_thumbnail_with_epub(epub_file):
    thumb = idk.text_thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_thumbnail_with_epub(epub_file):
    thumb = idk.thumbnail(epub_file)
    assert isinstance(thumb, Image)


def test_epub_extract_metadata(epub_file):
    meta = idk.extract_metadata(epub_file)
    assert meta.dict() == {
        "name": "Children's Literature",
        "creator": "Charles Madison Curry, Erle Elsworth Clippinger",
        "rights": "Public domain in the USA.",
    }


def test_epub_meta_embed(epub_file):
    meta = idk.IsccMeta(
        name="Name", description="Description", creator="Creator", keywords="some, keywords"
    )
    new_file = idk.epub_meta_embed(epub_file, meta)
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {
        "description": "Description",
        "name": "Children's Literature",
        "creator": "Creator",
        "rights": "Public domain in the USA.",
    }


def test_text_meta_embed_with_epub(epub_file):
    meta = idk.IsccMeta(
        name="Name",
        description="Iñtërnâtiônàlizætiøn☃",
        creator="Creator",
        keywords="some, keywords",
    )
    new_file = idk.text_meta_embed(epub_file, meta)
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {
        "description": "Iñtërnâtiônàlizætiøn☃",
        "name": "Children's Literature",
        "creator": "Creator",
        "rights": "Public domain in the USA.",
    }


def test_embed_metadata_with_epub(epub_file):
    meta = idk.IsccMeta(
        name="Name",
        description="Iñtërnâtiônàlizætiøn☃",
        creator="Creator",
        keywords="some, keywords",
    )
    new_file = idk.embed_metadata(epub_file, meta)
    meta = idk.extract_metadata(new_file)
    assert meta.dict() == {
        "description": "Iñtërnâtiônàlizætiøn☃",
        "name": "Children's Literature",
        "creator": "Creator",
        "rights": "Public domain in the USA.",
    }


class _RawNameZipInfo(zipfile.ZipInfo):
    """ZipInfo that writes pre-encoded raw filename bytes without forcing
    the ZIP UTF-8 flag (bit 11). Used to reproduce real-world EPUBs whose
    packagers stored UTF-8 filename bytes in CP437-flagged entries.
    """

    def __init__(self, raw_bytes):
        super().__init__(raw_bytes.decode("cp437"))
        self._raw_bytes = raw_bytes

    def _encodeFilenameFlags(self):
        return self._raw_bytes, self.flag_bits


_DEFAULT_CONTAINER = (
    b'<?xml version="1.0"?>'
    b'<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    b'<rootfiles><rootfile full-path="OEBPS/content.opf" '
    b'media-type="application/oebps-package+xml"/></rootfiles></container>'
)

_NAV = (
    b'<?xml version="1.0"?>'
    b'<html xmlns="http://www.w3.org/1999/xhtml"><head><title>n</title></head><body/></html>'
)


def _opf(*manifest_items, meta_extra=""):
    """Build minimal OPF XML containing the given manifest <item> strings
    plus a default nav item. `meta_extra` is appended inside <metadata>.
    """
    items = "".join(manifest_items)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
        '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        '<dc:identifier id="id">x</dc:identifier>'
        "<dc:title>T</dc:title><dc:language>en</dc:language>" + meta_extra + "</metadata>"
        "<manifest>"
        + items
        + '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        '</manifest><spine><itemref idref="nav"/></spine></package>'
    ).encode("utf-8")


def _jpeg_bytes():
    buf = io.BytesIO()
    PILImage.new("RGB", (32, 32), (200, 0, 0)).save(buf, format="JPEG")
    return buf.getvalue()


def _png_with_large_ztxt(decompressed_size):
    """Return PNG bytes with a zTXt chunk that decompresses to ~decompressed_size."""
    buf = io.BytesIO()
    PILImage.new("RGB", (4, 4), (200, 0, 0)).save(buf, format="PNG")
    png = buf.getvalue()
    iend_start = png.rfind(b"IEND") - 4
    head, tail = png[:iend_start], png[iend_start:]
    keyword = b"Raw profile type tiff:37724"
    payload = b"X" * decompressed_size
    chunk_data = keyword + b"\x00\x00" + zlib.compress(payload, level=9)
    crc = zlib.crc32(b"zTXt" + chunk_data)
    chunk = struct.pack(">I", len(chunk_data)) + b"zTXt" + chunk_data + struct.pack(">I", crc)
    return head + chunk + tail


def _build_epub(
    path, *, opf_xml=None, container_xml=_DEFAULT_CONTAINER, omit_container=False, entries=()
):
    """Build a minimal EPUB at `path`. `entries` is an iterable of
    (name_or_zipinfo, bytes) pairs added after the OPF/nav. When
    `opf_xml` is None, the OPF and nav are not written (useful for
    triggering missing-OPF errors).
    """
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", zipfile.ZIP_STORED)
        if not omit_container:
            z.writestr("META-INF/container.xml", container_xml)
        if opf_xml is not None:
            z.writestr("OEBPS/content.opf", opf_xml)
            z.writestr("OEBPS/nav.xhtml", _NAV)
        for name, data in entries:
            z.writestr(name, data)


def test_epub_thumbnail_utf8_filename_without_flag(tmp_path):
    """Regression: EPUBs whose entry filenames are UTF-8 bytes stored
    without the ZIP UTF-8 flag (bit 11) must still resolve cover paths.
    Real-world example: cover_path_missing_in_archive__9786185314958.epub
    (Greek title 'Θ_ΤΟΜΟΣ.jpg' packaged with CP437-flagged headers).
    """
    opf = _opf(
        '<item id="cover" href="image/%CE%98_%CE%A4%CE%9F%CE%9C%CE%9F%CE%A3.jpg" '
        'media-type="image/jpeg" properties="cover-image"/>',
    )
    cover_raw = "OEBPS/image/Θ_ΤΟΜΟΣ.jpg".encode("utf-8")
    epub_path = tmp_path / "mis_flagged.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[(_RawNameZipInfo(cover_raw), _jpeg_bytes())])

    with zipfile.ZipFile(epub_path) as z:
        cover_info = next(i for i in z.infolist() if i.filename.endswith(".jpg"))
        assert not (cover_info.flag_bits & 0x800), "test fixture invalid: UTF-8 flag is set"

    thumb = idk.epub_thumbnail(epub_path.as_posix())
    assert isinstance(thumb, Image)


def test_epub_cover_relative_href_with_dot_segments(tmp_path):
    """Regression: OPF in a subdirectory referencing a cover via a relative
    href like '../Images/cover.jpg' must resolve to the actual archive
    entry at OEBPS/Images/cover.jpg. pathlib leaves '..' uncollapsed so
    we explicitly normalize before the archive lookup.
    """
    container = (
        b'<?xml version="1.0"?>'
        b'<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        b'<rootfiles><rootfile full-path="OEBPS/Text/content.opf" '
        b'media-type="application/oebps-package+xml"/></rootfiles></container>'
    )
    opf = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="id">'
        b'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        b'<dc:identifier id="id">x</dc:identifier>'
        b"<dc:title>T</dc:title><dc:language>en</dc:language></metadata>"
        b"<manifest>"
        b'<item id="cv" href="../Images/cover.jpg" media-type="image/jpeg" properties="cover-image"/>'
        b'<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>'
        b'</manifest><spine><itemref idref="nav"/></spine></package>'
    )
    epub_path = tmp_path / "nested_opf.epub"
    with zipfile.ZipFile(epub_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), b"application/epub+zip", zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container)
        z.writestr("OEBPS/Text/content.opf", opf)
        z.writestr("OEBPS/Text/nav.xhtml", _NAV)
        z.writestr("OEBPS/Images/cover.jpg", _jpeg_bytes())
    assert isinstance(idk.epub_thumbnail(epub_path.as_posix()), Image)


def test_epub_cover_via_metadata_cover(tmp_path):
    """Cover located via EPUB2 <meta name='cover' content='id'/>."""
    opf = _opf(
        '<item id="cv" href="cover.jpg" media-type="image/jpeg"/>',
        meta_extra='<meta name="cover" content="cv"/>',
    )
    epub_path = tmp_path / "meta_cover.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/cover.jpg", _jpeg_bytes())])
    assert isinstance(idk.epub_thumbnail(epub_path.as_posix()), Image)


def test_epub_cover_via_multi_token_properties(tmp_path):
    """Cover located when properties has multiple space-separated tokens."""
    opf = _opf(
        '<item id="cv" href="img.jpg" media-type="image/jpeg" properties="cover-image svg"/>',
    )
    epub_path = tmp_path / "multi_prop.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/img.jpg", _jpeg_bytes())])
    assert isinstance(idk.epub_thumbnail(epub_path.as_posix()), Image)


def test_epub_cover_via_name_scan(tmp_path):
    """Cover located by 'cover' substring in href when no metadata indicators."""
    opf = _opf('<item id="i" href="art/the_cover.jpg" media-type="image/jpeg"/>')
    epub_path = tmp_path / "name_scan.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/art/the_cover.jpg", _jpeg_bytes())])
    assert isinstance(idk.epub_thumbnail(epub_path.as_posix()), Image)


def test_epub_cover_no_cover_indicators(tmp_path):
    """Raises when images exist but none are identifiable as cover."""
    opf = _opf('<item id="i" href="art/foo.jpg" media-type="image/jpeg"/>')
    epub_path = tmp_path / "no_cover.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/art/foo.jpg", _jpeg_bytes())])
    with pytest.raises(idk.IsccThumbExtractionError, match="No cover image found"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_cover_no_image_raises(tmp_path):
    """Raises when manifest has no images at all."""
    epub_path = tmp_path / "no_image.epub"
    _build_epub(epub_path, opf_xml=_opf())
    with pytest.raises(idk.IsccThumbExtractionError, match="No cover image found"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_cover_path_missing_skips_unicode_errors(tmp_path):
    """Cover path not in archive raises; resolver loop skips entries
    whose filenames can't be re-encoded to CP437 (proper UTF-8 entries
    with non-CP437 chars). Covers both the UnicodeError branch in the
    resolver and the not-found raise in epub_cover.
    """
    opf = _opf(
        '<item id="cv" href="missing.jpg" media-type="image/jpeg" properties="cover-image"/>',
    )
    epub_path = tmp_path / "missing_cover.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/Θ.txt", b"x")])
    with pytest.raises(idk.IsccExtractionError, match="not found in archive"):
        idk.epub_cover(epub_path.as_posix())


def test_resolve_archive_path_skips_utf8_decode_error(tmp_path):
    """Entries without the UTF-8 flag whose CP437->UTF-8 re-encoding
    raises UnicodeDecodeError are silently skipped by the resolver.
    CP437 byte 0x80 ('Ç') is invalid as a lone UTF-8 start byte.
    """
    opf = _opf(
        '<item id="cv" href="cover.jpg" media-type="image/jpeg" properties="cover-image"/>',
    )
    raw_name = b"OEBPS/\x80.txt"
    epub_path = tmp_path / "decode_err.epub"
    _build_epub(
        epub_path,
        opf_xml=opf,
        entries=[
            (_RawNameZipInfo(raw_name), b"x"),
            ("OEBPS/cover.jpg", _jpeg_bytes()),
        ],
    )
    thumb = idk.epub_thumbnail(epub_path.as_posix())
    assert isinstance(thumb, Image)


def test_epub_cover_missing_container_raises(tmp_path):
    """Raises when META-INF/container.xml is missing."""
    epub_path = tmp_path / "no_container.epub"
    _build_epub(epub_path, omit_container=True)
    with pytest.raises(idk.IsccExtractionError, match="Missing META-INF/container.xml"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_cover_bad_zip_raises(tmp_path):
    """Raises on non-ZIP file."""
    epub_path = tmp_path / "bad.epub"
    epub_path.write_bytes(b"not a zip")
    with pytest.raises(idk.IsccExtractionError, match="Invalid EPUB"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_cover_malformed_container_raises(tmp_path):
    """Raises when container.xml has no <rootfile> (xpath returns empty)."""
    bad_container = (
        b'<?xml version="1.0"?>'
        b'<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        b"<rootfiles/></container>"
    )
    epub_path = tmp_path / "malformed.epub"
    _build_epub(epub_path, container_xml=bad_container)
    with pytest.raises(idk.IsccExtractionError, match="Failed to parse EPUB metadata"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_cover_missing_opf_raises(tmp_path):
    """Raises when container.xml references a non-existent OPF file."""
    epub_path = tmp_path / "no_opf.epub"
    _build_epub(epub_path, opf_xml=None)
    with pytest.raises(idk.IsccExtractionError, match="not found within EPUB archive"):
        idk.epub_cover(epub_path.as_posix())


def test_epub_thumbnail_png_cover_with_large_ztxt(tmp_path):
    """Regression: PNG covers exported from Photoshop carry zTXt chunks
    (e.g. 'Raw profile type tiff:37724') that decompress past PIL's 1 MB
    default. Real-world example: png_decompressed_too_large__9788896736463.epub.
    """
    opf = _opf(
        '<item id="cv" href="cover.png" media-type="image/png" properties="cover-image"/>',
    )
    epub_path = tmp_path / "ztxt_cover.epub"
    _build_epub(
        epub_path, opf_xml=opf, entries=[("OEBPS/cover.png", _png_with_large_ztxt(1_500_000))]
    )
    assert isinstance(idk.epub_thumbnail(epub_path.as_posix()), Image)


def test_epub_thumbnail_svg_cover(tmp_path):
    """SVG cover images are rasterized via resvg before thumbnailing."""
    svg_data = (
        b'<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100">'
        b'<rect width="100" height="100" fill="red"/></svg>'
    )
    opf = _opf(
        '<item id="cv" href="cover.svg" media-type="image/svg+xml" properties="cover-image"/>',
    )
    epub_path = tmp_path / "svg_cover.epub"
    _build_epub(epub_path, opf_xml=opf, entries=[("OEBPS/cover.svg", svg_data)])
    thumb = idk.epub_thumbnail(epub_path.as_posix())
    assert isinstance(thumb, Image)
