import pytest
from iscc_samples import images, texts, audios
import shutil
from PIL import Image, ImageDraw


@pytest.fixture(scope="module")
def jpg_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "img.jpg"
    shutil.copy(images("jpg")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def png_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "img.png"
    shutil.copy(images("png")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def bmp_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "img.bmp"
    shutil.copy(images("bmp")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def mp3_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "audio.mp3"
    shutil.copy(audios("mp3")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def wav_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "audio.wav"
    shutil.copy(audios("wav")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def doc_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "text.doc"
    shutil.copy(texts("doc")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def jpg_obj(jpg_file):
    return Image.open(jpg_file)


@pytest.fixture(scope="module")
def png_obj(png_file):
    return Image.open(png_file)


@pytest.fixture(scope="module")
def png_obj_alpha(tmp_path_factory):
    img = Image.new("RGBA", (100, 100), (255, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse((25, 25, 75, 75), fill=(126, 126, 126))
    return img
