"""Check `soft_binding` against the shipped C2PA soft binding test vectors."""

import base64
import hashlib
import io
import json
from importlib.resources import files
from pathlib import Path

import iscc_samples
import pytest
from PIL import Image

import iscc_sdk as idk

VECTORS = json.loads(files("iscc_sdk").joinpath("c2pa_vectors.json").read_text("utf-8"))
TRIM_VECTORS = [n for n, v in VECTORS["soft_binding"].items() if "image_crop" in v["outputs"]]


@pytest.mark.parametrize("name", list(VECTORS["soft_binding"]))
def test_c2pa_vector(name, tmp_path):
    inputs, outputs = VECTORS["soft_binding"][name].values()
    if "file" in inputs:
        fp = Path(iscc_samples.ROOT) / inputs["file"]
    else:
        fp = tmp_path / "input"
        fp.write_bytes(base64.b64decode(inputs["bytes_b64"]))
    assert hashlib.sha256(fp.read_bytes()).hexdigest() == inputs["sha256"]
    sb = idk.soft_binding(fp, semantic=inputs["semantic"])
    assert list(sb.units) == outputs["units"]
    assert sb.value.hex() == outputs["value"]
    assert base64.b64encode(sb.value).decode("ascii") == outputs["base64"]


def test_c2pa_vectors_cover_border_trim():
    assert len(TRIM_VECTORS) == 4


@pytest.mark.parametrize("name", TRIM_VECTORS)
def test_c2pa_vector_image_crop(name):
    """The tolerant border trim crops the embedded image to the box given as `image_crop`."""
    inputs, outputs = VECTORS["soft_binding"][name].values()
    with Image.open(io.BytesIO(base64.b64decode(inputs["bytes_b64"]))) as img:
        trimmed, expected = idk.image_trim_tolerant(img), img.crop(outputs["image_crop"])
        assert (trimmed.size, trimmed.tobytes()) == (expected.size, expected.tobytes())
