import pytest

import iscc_sdk as idk
import iscc_samples as iss


GIF_HEADER = bytes.fromhex("474946383961")
OGG_HEADER = bytes.fromhex(
    "4f67675300020000000000000000dbb48522000000005340fe7b012a807468656f7261030201000b00090000b00000"
    "9000000000001800000001000001000001"
)


def test_mime_and_mode(jpg_file):
    assert idk.mediatype_and_mode(jpg_file) == ("image/jpeg", "image")


def test_mime_guess_data():
    assert idk.mediatype_guess(GIF_HEADER) == "image/gif"


def test_mime_guess_data_filename():
    assert idk.mediatype_guess(GIF_HEADER, file_name="sample.gif") == "image/gif"


def test_mime_guess_filename_preferred_when_both_supported():
    """Filename wins when both map to supported types (original behavior)."""
    assert idk.mediatype_guess(GIF_HEADER, file_name="sample.bmp") == "image/bmp"


def test_mime_guess_ogg_missdetection_fix():
    assert idk.mediatype_guess(OGG_HEADER) == "video/ogg"


def test_mime_guess_audio_ogg_not_misdetected_as_video():
    """Audio OGG/OPUS files must be detected as audio/ogg, not video/ogg."""
    for fp in iss.audios("ogg") + iss.audios("opus"):
        with open(fp, "rb") as f:
            data = f.read(4096)
        result = idk.mediatype_guess(data, file_name=fp.name)
        assert result == "audio/ogg", f"{fp.name}: expected audio/ogg, got {result}"


def test_mime_normalize():
    assert idk.mediatype_normalize("audio/x-aiff") == "audio/aiff"


def test_mime_normalize_unmapped():
    assert idk.mediatype_normalize("dont/touch/me") == "dont/touch/me"


def test_mime_to_mode():
    assert idk.mediatype_to_mode("image/bmp") == "image"
    assert idk.mediatype_to_mode("application/pdf") == "text"


def test_mime_to_mode_fallback():
    assert idk.mediatype_to_mode("image/avif") == "image"


def test_mime_to_mode_raises():
    with pytest.raises(idk.IsccUnsupportedMediatype):
        idk.mediatype_to_mode("application/fits")


def test_mime_clean():
    assert idk.mediatype_clean("") == ""
    assert idk.mediatype_clean("text/html ") == "text/html"
    assert idk.mediatype_clean(["text/html", "audio/mp3"]) == "text/html"
    assert idk.mediatype_clean([" text/html", "audio/mp3"]) == "text/html"
    assert idk.mediatype_clean(" text/plain; charset=windows-1252 ") == "text/plain"
    assert idk.mediatype_clean([" text/plain; charset=windows-1252 ", "audio/mp3"]) == "text/plain"


def test_mime_supported():
    assert idk.mediatype_supported("audio/x-aiff") is True
    assert idk.mediatype_supported("audio/aiff") is True
    assert idk.mediatype_supported("something/unknown") is False
    for mt in idk.SUPPORTED_MEDIATYPES.keys():
        assert idk.mediatype_supported(mt) is True


def test_mime_guess_no_detection():
    # Test case where no mediatype can be detected - should return octet-stream fallback
    empty_data = b""
    assert idk.mediatype_guess(empty_data) == "application/octet-stream"


def test_mime_from_name_compressed():
    """Compressed variants like .svgz return None (not directly processable)."""
    assert idk.mediatype_from_name("file.svgz") is None
    assert idk.mediatype_from_name("archive.tar.gz") is None
    assert idk.mediatype_from_name("file.svg") == "image/svg+xml"


def test_mime_from_data_exception_handling():
    # Test the exception handling in mediatype_from_data
    # Use invalid data that causes magic.from_buffer to fail
    invalid_data = None
    assert idk.mediatype_from_data(invalid_data) is None


def test_mime_samples():
    for sample in iss.all():
        # skiplist
        if sample.suffix in (".mobi", ".sqlite"):
            continue
        mediatype, mode = idk.mediatype_and_mode(sample)
        assert all((mediatype, mode))


def test_media_type_and_mode_raises():
    with pytest.raises(idk.IsccUnsupportedMediatype):
        idk.mediatype_and_mode(iss.texts("mobi")[0].as_posix())


def test_mime_supported_svg():
    assert idk.mediatype_supported("image/svg+xml") is True
    assert idk.mediatype_to_mode("image/svg+xml") == "image"


def test_mime_guess_svg_in_xml():
    """SVG content detected correctly even when filename suggests text/xml."""
    svg_data = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
    assert idk.mediatype_guess(svg_data, file_name="drawing.xml") == "image/svg+xml"


def test_mime_guess_svg_filename_over_generic_xml():
    """SVG filename wins when content sniffing returns generic text/xml."""
    # Simulates libmagic installs that report SVG as text/xml
    from unittest.mock import patch

    svg_data = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
    with patch("iscc_sdk.mediatype.mediatype_from_data", return_value="text/xml"):
        assert idk.mediatype_guess(svg_data, file_name="image.svg") == "image/svg+xml"


def test_mime_guess_svg_content_over_generic_xml_extensionless():
    """SVG content is detected even without .svg filename when libmagic returns text/xml."""
    from unittest.mock import patch

    svg_data = b'<svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg>'
    with patch("iscc_sdk.mediatype.mediatype_from_data", return_value="text/xml"):
        # Extensionless file
        assert idk.mediatype_guess(svg_data) == "image/svg+xml"
        # .xml extension
        assert idk.mediatype_guess(svg_data, file_name="drawing.xml") == "image/svg+xml"


def test_mime_guess_non_svg_xml_with_embedded_svg():
    """XML document with embedded <svg> element is NOT misclassified as SVG."""
    from unittest.mock import patch

    xml_data = b'<doc><svg xmlns="http://www.w3.org/2000/svg"><circle r="10"/></svg></doc>'
    with patch("iscc_sdk.mediatype.mediatype_from_data", return_value="text/xml"):
        assert idk.mediatype_guess(xml_data) == "text/xml"


def test_mime_guess_svg_root_wrong_namespace():
    """XML with <svg> root but non-SVG namespace is NOT classified as SVG."""
    from unittest.mock import patch

    xml_data = b'<svg xmlns="urn:test"><rect width="10" height="10"/></svg>'
    with patch("iscc_sdk.mediatype.mediatype_from_data", return_value="text/xml"):
        assert idk.mediatype_guess(xml_data) == "text/xml"


def test_mime_guess_svg_in_xml_comment():
    """SVG tag inside an XML comment is NOT misclassified as SVG."""
    from unittest.mock import patch

    xml_data = b'<?xml version="1.0"?><!-- <svg xmlns="http://www.w3.org/2000/svg"> --><doc/>'
    with patch("iscc_sdk.mediatype.mediatype_from_data", return_value="text/xml"):
        assert idk.mediatype_guess(xml_data) == "text/xml"


def test_mime_guess_extension_wins_for_containers():
    """Filename wins for container formats where sniffing returns generic type (e.g., zip)."""
    # DOCX/EPUB/PPTX are zip archives; filename provides the specific type
    zip_header = bytes.fromhex("504b0304")
    assert idk.mediatype_guess(zip_header, file_name="doc.docx") == (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


def test_mediatype_and_mode_with_file_name(jpg_file, tmp_path):
    import shutil

    noext = tmp_path / "tempfile"
    shutil.copy(jpg_file, noext)
    assert idk.mediatype_and_mode(noext, file_name="photo.jpg") == ("image/jpeg", "image")
