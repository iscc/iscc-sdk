"""Regenerate the C2PA soft binding test vectors in iscc_sdk/c2pa_vectors.json."""

import base64
import hashlib
import io
import json
import tempfile
from pathlib import Path

import iscc_samples
import numpy as np
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

# Black frame widths (left, top, right, bottom) around the product image
FRAME = (6, 4, 2, 8)


def white_png():
    # type: () -> bytes
    """Create a small uniform white PNG (its Image-Code is featureless)."""
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (255, 255, 255)).save(buf, "PNG", optimize=True)
    return buf.getvalue()


def png(pixels):
    # type: (np.ndarray) -> bytes
    """Encode RGB pixels (height x width x 3) as PNG."""
    buf = io.BytesIO()
    Image.fromarray(pixels, "RGB").save(buf, "PNG", optimize=True)
    return buf.getvalue()


def noisy_white(rng, height, width):
    # type: (np.random.Generator, int, int) -> np.ndarray
    """Faintly noisy white RGB pixels (grey levels 248 to 252)."""
    return np.repeat(rng.integers(248, 253, (height, width, 1), dtype=np.uint8), 3, axis=2)


def texture(rng, height, width):
    # type: (np.random.Generator, int, int) -> np.ndarray
    """Textured RGB pixels: blocks of 4x4 random colors (levels 0 to 200, far from white)."""
    blocks = rng.integers(0, 201, (height // 4 + 1, width // 4 + 1, 3), dtype=np.uint8)
    return blocks.repeat(4, axis=0).repeat(4, axis=1)[:height, :width]


def product():
    # type: () -> np.ndarray
    """
    Textured product on a faintly noisy white background (64x48), trimmed to (12, 12, 48, 36).

    A faint yellow detail sticks out left of the product. It differs from the background in the
    blue channel only (about 3 grey levels), so a trim of grey values would cut it off.
    """
    rng = np.random.default_rng(0)
    pixels = noisy_white(rng, 48, 64)
    pixels[12:36, 16:48] = texture(rng, 24, 32)
    pixels[20:28, 12:16, 2] = 220
    return pixels


def product_png():
    # type: () -> bytes
    """Product on a noisy white background, trimmed in one pass."""
    return png(product())


def framed_product_png():
    # type: () -> bytes
    """Product image in an uneven black frame, trimmed in two passes to the same pixels."""
    left, top, right, bottom = FRAME
    return png(np.pad(product(), ((top, bottom), (left, right), (0, 0))))


def sky_png():
    # type: () -> bytes
    """Faintly noisy sky gradient (grey 230 to 120) above texture, a one-sided border to keep."""
    rng = np.random.default_rng(1)
    pixels = np.zeros((48, 64, 3), dtype=np.int16)
    pixels[:24] = np.linspace(230, 120, 24).round().astype(np.int16)[:, None, None]
    pixels[:24] += rng.integers(-3, 4, (24, 64, 1))
    pixels[24:] = texture(rng, 24, 64)
    return png(pixels.clip(0, 255).astype(np.uint8))


def caption_bar_png():
    # type: () -> bytes
    """Faintly noisy white bar above texture, a flat one-sided border to cut."""
    rng = np.random.default_rng(2)
    pixels = texture(rng, 48, 64)
    pixels[:10] = noisy_white(rng, 10, 64)
    return png(pixels)


# Embedded input bytes with the expected crop box of the tolerant border trim (None: no check)
BYTES_CASES = [
    ("featureless_image", white_png, None),
    ("image_trim_noisy_background", product_png, (12, 12, 48, 36)),
    ("image_trim_black_frame", framed_product_png, (18, 16, 54, 40)),
    ("image_trim_gradient_kept", sky_png, (0, 0, 64, 48)),
    ("image_trim_caption_bar", caption_bar_png, (0, 10, 64, 48)),
]


def check_crop(fp, crop):
    # type: (Path, tuple[int, int, int, int]) -> None
    """Raise ValueError if the tolerant border trim does not crop the image to `crop`."""
    with Image.open(fp) as img:
        trimmed, expected = idk.image_trim_tolerant(img), img.crop(crop)
        if (trimmed.size, trimmed.tobytes()) != (expected.size, expected.tobytes()):
            raise ValueError(f"Tolerant trim crops {fp.name} to {trimmed.size}, expected {crop}")


def vector(data, fp, inputs, crop=None):
    # type: (bytes, Path, dict, tuple[int, int, int, int]|None) -> dict
    """Build one test vector from the input bytes, a file with these bytes and the input fields."""
    sb = idk.soft_binding(fp, semantic=False)
    outputs = {
        "units": list(sb.units),
        "value": sb.value.hex(),
        "base64": base64.b64encode(sb.value).decode("ascii"),
    }
    if crop:
        check_crop(fp, crop)
        outputs["image_crop"] = list(crop)
    return {
        "inputs": {**inputs, "sha256": hashlib.sha256(data).hexdigest(), "semantic": False},
        "outputs": outputs,
    }


def main():
    """Write all soft binding test vectors."""
    root = Path(iscc_samples.ROOT)
    vectors = {}
    for name, rel in FILE_CASES:
        fp = root / rel
        vectors[name] = vector(fp.read_bytes(), fp, {"file": rel})
    with tempfile.TemporaryDirectory() as tmp:
        fp = Path(tmp) / "input"
        for name, create, crop in BYTES_CASES:
            data = create()
            fp.write_bytes(data)
            b64 = base64.b64encode(data).decode("ascii")
            vectors[name] = vector(data, fp, {"bytes_b64": b64}, crop)
    tests = {f"test_{i:04d}_{name}": v for i, (name, v) in enumerate(vectors.items(), start=1)}
    with open(DST, "wt", encoding="utf-8", newline="\n") as outf:
        json.dump({"soft_binding": tests}, outf, indent=2)
        outf.write("\n")


if __name__ == "__main__":
    main()
