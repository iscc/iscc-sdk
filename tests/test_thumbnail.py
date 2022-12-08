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
