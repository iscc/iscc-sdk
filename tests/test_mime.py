import pytest

import iscc_sdk as idk


GIF_HEADER = bytes.fromhex("474946383961")
OGG_HEADER = bytes.fromhex(
    "4f67675300020000000000000000dbb48522000000005340fe7b012a807468656f7261030201000b00090000b00000"
    "9000000000001800000001000001000001"
)


def test_mime_and_mode(jpg_file):
    assert idk.mime_and_mode(jpg_file) == ("image/jpeg", "image")


def test_mime_guess_data():
    assert idk.mime_guess(GIF_HEADER) == "image/gif"


def test_mime_guess_data_filename():
    assert idk.mime_guess(GIF_HEADER, file_name="sample.gif") == "image/gif"


def test_mime_guess_extension_overrides_data():
    assert idk.mime_guess(GIF_HEADER, file_name="sample.bmp") == "image/bmp"


def test_mime_guess_ogg_missdetection_fix():
    assert idk.mime_guess(OGG_HEADER) == "video/ogg"


def test_mime_normalize():
    assert idk.mime_normalize("audio/x-aiff") == "audio/aiff"


def test_mime_normalize_unmapped():
    assert idk.mime_normalize("dont/touch/me") == "dont/touch/me"


def test_mime_to_mode():
    assert idk.mime_to_mode("image/bmp") == "image"
    assert idk.mime_to_mode("application/pdf") == "text"


def test_mime_to_mode_fallback():
    assert idk.mime_to_mode("image/avif") == "image"


def test_mime_to_mode_raises():
    with pytest.raises(ValueError):
        idk.mime_to_mode("application/fits")


def test_mime_clean():
    assert idk.mime_clean("") == ""
    assert idk.mime_clean("text/html ") == "text/html"
    assert idk.mime_clean(["text/html", "audio/mp3"]) == "text/html"
    assert idk.mime_clean([" text/html", "audio/mp3"]) == "text/html"
    assert idk.mime_clean(" text/plain; charset=windows-1252 ") == "text/plain"
    assert idk.mime_clean([" text/plain; charset=windows-1252 ", "audio/mp3"]) == "text/plain"


def test_mime_supported():
    assert idk.mime_supported("audio/x-aiff") is True
    assert idk.mime_supported("audio/aiff") is True
    assert idk.mime_supported("something/unknown") is False
    for mt in idk.SUPPORTED_MEDIATYPES.keys():
        assert idk.mime_supported(mt) is True
