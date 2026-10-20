"""Check `soft_binding` against the shipped C2PA soft binding test vectors."""

import base64
import hashlib
import json
from importlib.resources import files
from pathlib import Path

import iscc_samples
import pytest

import iscc_sdk as idk

VECTORS = json.loads(files("iscc_sdk").joinpath("c2pa_vectors.json").read_text("utf-8"))


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
    assert sb.units == outputs["units"]
    assert sb.value.hex() == outputs["value"]
    assert base64.b64encode(sb.value).decode("ascii") == outputs["base64"]
