import pytest
from iscc_samples import images
import shutil


@pytest.fixture(scope="module")
def jpg_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "img.jpg"
    shutil.copy(images("jpg")[0], dst)
    return dst


@pytest.fixture(scope="module")
def png_file(tmp_path_factory):
    dst = tmp_path_factory.mktemp("data") / "img.png"
    shutil.copy(images("png")[0], dst)
    return dst
