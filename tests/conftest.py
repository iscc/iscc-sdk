from pathlib import Path

import pytest
from iscc_samples import images, texts, audios, videos
import shutil
from PIL import Image, ImageDraw


@pytest.fixture(scope="module")
def jpg_file(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "img.jpg"
    shutil.copy(images("jpg")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def png_file(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "img.png"
    shutil.copy(images("png")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def bmp_file(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "img.bmp"
    shutil.copy(images("bmp")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def mp3_file(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "audio.mp3"
    shutil.copy(audios("mp3")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def mp3_cover(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "audio.mp3"
    shutil.copy(audios("mp3")[1], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def wav_file(tmp_path_factory) -> str:
    dst = tmp_path_factory.mktemp("data") / "audio.wav"
    shutil.copy(audios("wav")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def doc_file(tmp_path_factory) -> str:
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


@pytest.fixture(scope="module")
def mp4_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "video.mp4"
    shutil.copy(videos("mp4")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def mov_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "video.mov"
    shutil.copy(videos("mov")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def ogv_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "video.ogv"
    shutil.copy(videos("ogv")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def docx_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "text.docx"
    shutil.copy(texts("docx")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def pdf_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "text.pdf"
    shutil.copy(texts("pdf")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def epub_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "text.epub"
    shutil.copy(texts("epub")[0], dst)
    return dst.as_posix()


@pytest.fixture(scope="module")
def asset_tree(tmp_path_factory):
    dst = Path(tmp_path_factory.mktemp("data"))
    for img_path in videos()[:3]:
        shutil.copy2(img_path, dst)
    subdir = dst / "subdir"
    subdir.mkdir()
    for audio_path in audios()[:2]:
        shutil.copy2(audio_path, subdir)
    return dst
