import base64
import io

import PIL.Image
import pytest
from PIL.Image import Image

import iscc_sdk as idk


def test_thumbnail_jpg(jpg_file):
    assert isinstance(idk.thumbnail(jpg_file), Image)


def test_thumbnail_pdf(pdf_file):
    assert isinstance(idk.thumbnail(pdf_file), Image)


def test_thumbnail_wav(wav_file):
    assert idk.thumbnail(wav_file) is None


def test_thumbnail_mp4(mp4_file):
    assert isinstance(idk.thumbnail(mp4_file), Image)


THUMB_FILES = ["jpg_file", "svg_file", "pdf_file", "epub_file", "mp3_cover", "mp4_file"]


def data_url_image(durl):
    """Decode the image of a base64 Data-URL."""
    return PIL.Image.open(io.BytesIO(base64.b64decode(durl.split(",", 1)[1])))


@pytest.mark.parametrize("fixture", THUMB_FILES)
def test_thumbnail_per_call_size(fixture, request):
    """Per-call `image_thumbnail_size` reaches every thumbnailer, the global setting is unchanged."""
    fp = request.getfixturevalue(fixture)
    assert max(idk.thumbnail(fp).size) > 64
    assert max(idk.thumbnail(fp, image_thumbnail_size=64).size) == 64
    assert idk.sdk_opts.image_thumbnail_size == 128


def test_image_to_data_url_per_call_format_and_quality(jpg_file):
    img = idk.thumbnail(jpg_file)
    assert idk.image_to_data_url(img).startswith("data:image/webp;base64,")
    jpeg = idk.image_to_data_url(img, image_thumbnail_format="JPEG")
    assert jpeg.startswith("data:image/jpeg;base64,")
    assert data_url_image(jpeg).format == "JPEG"
    better = idk.image_to_data_url(img, image_thumbnail_format="JPEG", image_thumbnail_quality=90)
    assert len(better) > len(jpeg)
    assert idk.sdk_opts.image_thumbnail_format == "WEBP"


@pytest.mark.parametrize(
    "code_func, fixture",
    [
        ("code_iscc", "jpg_file"),
        ("code_image", "jpg_file"),
        ("code_image", "svg_file"),
        ("code_text", "pdf_file"),
        ("code_audio", "mp3_cover"),
        ("code_video", "mp4_file"),
    ],
)
def test_code_per_call_thumbnail_options(code_func, fixture, request):
    """Per-call thumbnail options of the `code_*` functions reach the thumbnail."""
    fp = request.getfixturevalue(fixture)
    opts = {"image_thumbnail_size": 64, "image_thumbnail_format": "JPEG"}
    meta = getattr(idk, code_func)(fp, **opts)
    assert meta.thumbnail.startswith("data:image/jpeg;base64,")
    assert max(data_url_image(meta.thumbnail).size) == 64
