"""Regression tests for known iscc-sdk failures.

Each test reproduces a formerly failing real-world EPUB processing scenario with a
minimal synthesized fixture so the offending file does not need to be checked in.
The underlying issues are fixed in iscc-tika >= 0.5.0; these tests guard against
regressions.
"""

import io
import zipfile
from pathlib import Path

import iscc_sdk as idk

CONTAINER_XML = (
    b'<?xml version="1.0"?>'
    b'<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
    b"<rootfiles>"
    b'<rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>'
    b"</rootfiles>"
    b"</container>"
)

NCX_XML = (
    b'<?xml version="1.0"?>'
    b'<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
    b'<head><meta name="dtb:uid" content="urn:uuid:12345"/></head>'
    b"<docTitle><text>Test</text></docTitle>"
    b"<navMap/>"
    b"</ncx>"
)


def write_epub(path, opf, extra_files):
    """Write a minimal EPUB with the given OPF and extra payload files."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zout:
        info = zipfile.ZipInfo("mimetype")
        info.compress_type = zipfile.ZIP_STORED
        zout.writestr(info, b"application/epub+zip")
        zout.writestr("META-INF/container.xml", CONTAINER_XML)
        zout.writestr("OEBPS/content.opf", opf)
        zout.writestr("OEBPS/toc.ncx", NCX_XML)
        for name, content in extra_files.items():
            zout.writestr(name, content)
    Path(path).write_bytes(buf.getvalue())


def test_epub_with_path_traversal_in_spine(tmp_path):
    """Reproduces TIKA-198 IOException: spine references manifest item with ``../`` path.

    Original failing fixture: tika-198-ioexception_9788412435931.epub.
    The OPF places content.opf in OEBPS/ and references ``../toc.xhtml`` in
    its manifest, then includes that item in the spine. Tika's EpubParser
    raises an IOException while resolving the path that escapes the OPF root.
    """
    opf = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">'
        b'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        b"<dc:title>Test</dc:title>"
        b'<dc:identifier id="bookid">urn:uuid:12345</dc:identifier>'
        b"<dc:language>en</dc:language>"
        b"</metadata>"
        b"<manifest>"
        b'<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        b'<item id="ch1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>'
        b'<item id="ext" href="../external.xhtml" media-type="application/xhtml+xml"/>'
        b"</manifest>"
        b'<spine toc="ncx">'
        b'<itemref idref="ch1"/>'
        b'<itemref idref="ext"/>'
        b"</spine>"
        b"</package>"
    )
    chapter = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<html xmlns="http://www.w3.org/1999/xhtml">'
        b"<head><title>Chapter 1</title></head>"
        b"<body><p>Hello world</p></body>"
        b"</html>"
    )
    external = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<html xmlns="http://www.w3.org/1999/xhtml">'
        b"<head><title>External</title></head>"
        b"<body><p>External content</p></body>"
        b"</html>"
    )
    epub_path = tmp_path / "tika_198.epub"
    write_epub(
        epub_path,
        opf,
        {
            "OEBPS/chapter1.xhtml": chapter,
            "external.xhtml": external,
        },
    )

    text = idk.text_extract(epub_path.as_posix())
    assert "Hello world" in text


def test_epub_with_deeply_nested_xml(tmp_path):
    """Reproduces TIKA-237 SAXException: deeply nested XML in a content document.

    Original failing fixture: tika-237-saxexception_9791220847322.epub.
    Its chapter.3.xhtml (a poetic Beowulf rendering) opens a fresh ``<div>``
    for every line, building a nesting depth of 257. Tika's underlying SAX
    parser rejects element trees deeper than ~99 levels and raises a
    SAXException from DefaultParser.
    """
    depth = 260
    inner = "Beowulf"
    for _ in range(depth):
        inner = f"<div>{inner}"
    inner += "</div>" * depth
    chapter = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml">'
        "<head><title>Chapter</title></head>"
        f"<body>{inner}</body>"
        "</html>"
    ).encode()

    opf = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="bookid">'
        b'<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
        b"<dc:title>Test</dc:title>"
        b'<dc:identifier id="bookid">urn:uuid:12345</dc:identifier>'
        b"<dc:language>en</dc:language>"
        b"</metadata>"
        b"<manifest>"
        b'<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        b'<item id="ch" href="chapter.xhtml" media-type="application/xhtml+xml"/>'
        b"</manifest>"
        b'<spine toc="ncx"><itemref idref="ch"/></spine>'
        b"</package>"
    )
    epub_path = tmp_path / "tika_237.epub"
    write_epub(epub_path, opf, {"OEBPS/chapter.xhtml": chapter})

    text = idk.text_extract(epub_path.as_posix())
    assert "Beowulf" in text
