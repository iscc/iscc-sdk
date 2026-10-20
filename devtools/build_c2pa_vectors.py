"""Regenerate the C2PA soft binding test vectors in iscc_sdk/c2pa_vectors.json."""

import base64
import hashlib
import io
import json
import tempfile
from pathlib import Path

import iscc_samples
from PIL import Image

import iscc_sdk as idk

HERE = Path(__file__).parent
DST = HERE.parent / "iscc_sdk" / "c2pa_vectors.json"

FILE_CASES = [
    ("image_with_title", "image/demo.jpg"),
    ("image_without_title", "image/demo.bmp"),
    ("text", "text/demo.txt"),
    ("audio", "audio/demo.mp3"),
    ("video", "video/demo.mp4"),
    ("unsupported", "text/demo.sqlite"),
]


def white_png():
    # type: () -> bytes
    """Create a small uniform white PNG (its Image-Code is featureless)."""
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (255, 255, 255)).save(buf, "PNG", optimize=True)
    return buf.getvalue()


def vector(data, fp, inputs):
    # type: (bytes, Path, dict) -> dict
    """Build one test vector from the input bytes, a file with these bytes and the input fields."""
    sb = idk.soft_binding(fp, semantic=False)
    return {
        "inputs": {**inputs, "sha256": hashlib.sha256(data).hexdigest(), "semantic": False},
        "outputs": {
            "units": sb.units,
            "value": sb.value.hex(),
            "base64": base64.b64encode(sb.value).decode("ascii"),
        },
    }


def main():
    """Write all soft binding test vectors."""
    root = Path(iscc_samples.ROOT)
    vectors = {}
    for name, rel in FILE_CASES:
        fp = root / rel
        vectors[name] = vector(fp.read_bytes(), fp, {"file": rel})
    with tempfile.TemporaryDirectory() as tmp:
        data = white_png()
        fp = Path(tmp) / "input"
        fp.write_bytes(data)
        b64 = base64.b64encode(data).decode("ascii")
        vectors["featureless_image"] = vector(data, fp, {"bytes_b64": b64})
    tests = {f"test_{i:04d}_{name}": v for i, (name, v) in enumerate(vectors.items(), start=1)}
    with open(DST, "wt", encoding="utf-8", newline="\n") as outf:
        json.dump({"soft_binding": tests}, outf, indent=2)
        outf.write("\n")


if __name__ == "__main__":
    main()
