"""Tests for the exact and tolerant image border trims and the `image_trim_tolerant` option."""

import numpy as np
import pytest
from iscc_samples import images
from PIL import Image, ImageChops

import iscc_sdk as idk

OBJECT_BOX = (60, 40, 140, 100)


def trim_border_oracle(img):
    """Previous `image_trim_border` implementation based on `ImageChops.difference`."""
    bg = Image.new(img.mode, img.size, img.getpixel((0, 0)))
    diff = ImageChops.difference(img, bg)
    diff = ImageChops.add(diff, diff)
    bbox = diff.getbbox()
    if bbox != (0, 0) + img.size:
        return img.crop(bbox)
    return img


def trim_tolerant_pass_oracle(img, tol=16):
    """Single tolerant pass from iscc-watermark-drift `codes.py` (slow, numpy based)."""
    a = np.asarray(img.convert("RGB"), dtype=np.int16)
    keep = (np.abs(a - a[0, 0]) > tol).any(axis=2)
    rows, cols = np.flatnonzero(keep.any(axis=1)), np.flatnonzero(keep.any(axis=0))
    if rows.size == 0:
        return img
    return img.crop((int(cols[0]), int(rows[0]), int(cols[-1]) + 1, int(rows[-1]) + 1))


def trim_tolerant_oracle(img, tol=16, max_passes=16):
    """Repeat the single tolerant pass until it crops nothing (at most `max_passes` times)."""
    for _ in range(max_passes):
        out = trim_tolerant_pass_oracle(img, tol)
        if out.size == img.size:
            return out
        img = out
    return img


def noisy_white(seed=0, size=(200, 150)):
    """Create an off-white RGB image with sigma 2 noise and a dark object at OBJECT_BOX."""
    rng = np.random.default_rng(seed)
    a = rng.normal(250, 2, (size[1], size[0], 3)).round().clip(0, 255).astype(np.uint8)
    x0, y0, x1, y1 = OBJECT_BOX
    a[y0:y1, x0:x1] = (60, 90, 120)
    return Image.fromarray(a, "RGB")


def same(a, b):
    """Check that two images have identical mode, size and pixels."""
    return a.mode == b.mode and a.size == b.size and a.tobytes() == b.tobytes()


def normalize_reference(img, tolerant):
    """Rebuild `image_normalize` from its steps (tolerant or exact border trim)."""
    img = idk.image_fill_transparency(idk.image_exif_transpose(img))
    img = idk.image_trim_tolerant(img) if tolerant else idk.image_trim_border(img)
    im = img.convert("L").resize((32, 32), idk.BICUBIC)
    return list(im.get_flattened_data() if hasattr(im, "get_flattened_data") else im.getdata())


def framed(color=(0, 0, 0), size=(10, 20, 30, 15), inner=None):
    """Place an image (default noisy white photo) in an exact frame of `color` (side widths)."""
    inner = inner or noisy_white()
    left, top, right, bottom = size
    img = Image.new("RGB", (inner.width + left + right, inner.height + top + bottom), color)
    img.paste(inner, (left, top))
    return img


@pytest.mark.parametrize("fp", images(), ids=lambda p: p.name)
def test_image_trim_border_matches_oracle_samples(fp):
    with Image.open(fp) as img:
        img.load()
        for candidate in (img, idk.image_fill_transparency(img)):
            assert same(idk.image_trim_border(candidate), trim_border_oracle(candidate))


def test_image_trim_border_matches_oracle_noisy_white():
    for seed in range(5):
        img = noisy_white(seed)
        assert same(idk.image_trim_border(img), trim_border_oracle(img))


def test_image_trim_border_matches_oracle_frame():
    for color in [(0, 0, 0), (255, 255, 255), (200, 30, 30)]:
        img = framed(color)
        result = idk.image_trim_border(img)
        assert same(result, trim_border_oracle(img))
        assert result.size == noisy_white().size


def test_image_trim_border_matches_oracle_one_side():
    for size in [(7, 0, 0, 0), (0, 7, 0, 0), (0, 0, 7, 0), (0, 0, 0, 7)]:
        img = framed((0, 0, 0), size)
        # Opposite photo corner as reference when the frame is on the right or bottom side
        flipped = img.rotate(180)
        for candidate in (img, flipped):
            assert same(idk.image_trim_border(candidate), trim_border_oracle(candidate))


def test_image_trim_border_uniform_unchanged():
    for img in (Image.new("RGB", (50, 40), (10, 20, 30)), Image.new("L", (50, 40), 77)):
        result = idk.image_trim_border(img)
        assert result is img
        assert same(result, trim_border_oracle(img))


def test_image_trim_border_matches_oracle_near_uniform():
    img = noisy_white().crop((0, 0, 50, 30))
    assert same(idk.image_trim_border(img), trim_border_oracle(img))


def test_image_trim_border_matches_oracle_tiny():
    tiny = [Image.new("RGB", (1, 1), (1, 2, 3)), Image.new("L", (1, 1), 9)]
    for size in [(1, 9), (9, 1)]:
        img = Image.new("RGB", size, (255, 255, 255))
        img.putpixel((size[0] // 2, size[1] // 2), (0, 0, 0))
        tiny += [img, img.convert("L"), Image.new("RGB", size, (5, 5, 5))]
    for img in tiny:
        assert same(idk.image_trim_border(img), trim_border_oracle(img))


@pytest.mark.parametrize("mode", ["RGB", "L", "RGBA", "LA", "P", "CMYK", "1"])
def test_image_trim_border_matches_oracle_modes(mode):
    for img in (framed(), noisy_white(), Image.new("RGB", (30, 20), (40, 50, 60))):
        img = img.convert(mode)
        result = idk.image_trim_border(img)
        assert result.mode == mode
        assert same(result, trim_border_oracle(img))


def test_image_trim_border_mode_i_unsupported():
    img = framed().convert("I")
    with pytest.raises(ValueError):
        trim_border_oracle(img)
    with pytest.raises(ValueError):
        idk.image_trim_border(img)


def reviewer_case(patches=False, frame=False):
    """Dark subject with a lighter inner detail on a pure white background."""
    img = Image.new("RGB", (200, 150), (255, 255, 255))
    img.paste((60, 90, 120), (60, 45, 140, 105))
    img.paste((150, 170, 190), (70, 55, 125, 90))
    if patches:
        # Faint watermark-like change of one or two grey levels in the background
        img.paste((254, 254, 254), (5, 5, 30, 12))
        img.paste((253, 253, 253), (170, 130, 195, 145))
    return framed(size=(20, 20, 20, 20), inner=img) if frame else img


def nested_rings(rings=20, width=2):
    """Grayscale image of nested rings whose values alternate by more than the tolerance."""
    size = 2 * rings * width + 20
    img = Image.new("L", (size, size), 0)
    for i in range(rings):
        box = (i * width, i * width, size - i * width, size - i * width)
        img.paste(100 if i % 2 else 0, box)
    return img


@pytest.mark.parametrize("fp", images(), ids=lambda p: p.name)
def test_image_trim_tolerant_matches_oracle_samples(fp):
    with Image.open(fp) as img:
        img.load()
        for candidate in (img, idk.image_fill_transparency(img)):
            assert same(idk.image_trim_tolerant(candidate), trim_tolerant_oracle(candidate))


@pytest.mark.parametrize("fp", images(), ids=lambda p: p.name)
def test_image_trim_tolerant_idempotent_samples(fp):
    with Image.open(fp) as img:
        img.load()
        for candidate in (img, idk.image_fill_transparency(img)):
            trimmed = idk.image_trim_tolerant(candidate)
            assert idk.image_trim_tolerant(trimmed) is trimmed


def test_image_trim_tolerant_matches_oracle_noisy_white():
    for seed in range(5):
        img = noisy_white(seed)
        assert same(idk.image_trim_tolerant(img), trim_tolerant_oracle(img))


def test_image_trim_tolerant_matches_oracle_colored_padding():
    img = framed((200, 30, 30), (20, 15, 20, 15))
    result = idk.image_trim_tolerant(img)
    assert same(result, trim_tolerant_oracle(img))
    assert same(result, noisy_white().crop(OBJECT_BOX))


def test_image_trim_tolerant_uniform_unchanged():
    img = Image.new("RGB", (50, 40), (255, 255, 255))
    assert idk.image_trim_tolerant(img) is img
    assert trim_tolerant_oracle(img) is img


def test_image_trim_tolerant_near_uniform_unchanged():
    img = noisy_white().crop((0, 0, 50, 30))
    assert idk.image_trim_tolerant(img) is img
    assert trim_tolerant_oracle(img) is img


def test_image_trim_tolerant_no_border_unchanged():
    img = noisy_white()
    img.putpixel((0, 0), (0, 0, 0))
    img.putpixel((199, 149), (0, 0, 0))
    assert idk.image_trim_tolerant(img) is img


def test_image_trim_tolerant_matches_oracle_l():
    img = noisy_white().convert("L")
    result = idk.image_trim_tolerant(img)
    assert result.mode == "L"
    assert same(result, trim_tolerant_oracle(img))
    assert result.size == (80, 60)


@pytest.mark.parametrize("mode", ["RGBA", "P", "LA", "CMYK"])
def test_image_trim_tolerant_matches_oracle_other_modes(mode):
    for img in (framed(), noisy_white(), reviewer_case(frame=True)):
        img = img.convert(mode)
        result = idk.image_trim_tolerant(img)
        assert result.mode == mode
        assert same(result, trim_tolerant_oracle(img))


def test_image_trim_tolerant_tolerance():
    img = Image.new("L", (30, 20), 200)
    img.paste(220, (10, 5, 20, 15))
    assert idk.image_trim_tolerant(img).size == (10, 10)
    assert idk.image_trim_tolerant(img, tolerance=20) is img
    assert idk.image_trim_tolerant(img, tolerance=19).size == (10, 10)


def test_image_trim_tolerant_crops_noisy_white_to_object():
    img = noisy_white()
    assert idk.image_trim_border(img).size == img.size
    assert same(idk.image_trim_tolerant(img), img.crop(OBJECT_BOX))


def test_image_trim_tolerant_stable_under_small_background_change():
    base = Image.new("RGB", (200, 150), (250, 250, 250))
    base.paste((60, 90, 120), OBJECT_BOX)
    # Faint watermark-like change of one or two grey levels in the background
    marked = base.copy()
    marked.paste((252, 252, 252), (5, 5, 30, 12))
    marked.paste((249, 249, 249), (170, 130, 195, 145))
    assert not same(idk.image_trim_border(base), idk.image_trim_border(marked))
    assert same(idk.image_trim_tolerant(base), idk.image_trim_tolerant(marked))
    assert same(idk.image_trim_tolerant(base), base.crop(OBJECT_BOX))


def test_image_trim_tolerant_reviewer_case():
    variants = [reviewer_case(), reviewer_case(patches=True), reviewer_case(frame=True)]
    variants.append(reviewer_case(patches=True, frame=True))
    expected = reviewer_case().crop((70, 55, 125, 90))
    for img in variants:
        result = idk.image_trim_tolerant(img)
        assert same(result, trim_tolerant_oracle(img))
        assert same(result, expected)
    pixels = [list(idk.image_normalize(img)) for img in variants]
    assert all(p == pixels[0] for p in pixels)


def test_image_trim_tolerant_noisy_frame():
    photo = noisy_white()
    rng = np.random.default_rng(1)
    a = (8 + rng.integers(-2, 3, (photo.height + 40, photo.width + 60, 3))).astype(np.uint8)
    img = Image.fromarray(a, "RGB")
    img.paste(photo, (30, 20))
    assert idk.image_trim_border(img).size == img.size
    result = idk.image_trim_tolerant(img)
    assert same(result, idk.image_trim_tolerant(photo))
    assert same(result, trim_tolerant_oracle(img))


def test_image_trim_tolerant_max_passes():
    img = nested_rings()
    assert idk.image.TRIM_MAX_PASSES == 16
    result = idk.image_trim_tolerant(img)
    assert result.size == (img.width - 64, img.height - 64)
    assert same(result, trim_tolerant_oracle(img))
    assert trim_tolerant_oracle(img, max_passes=100).size == (24, 24)


def test_image_trim_tolerant_option_default_on():
    assert idk.SdkOptions().image_trim_tolerant is True
    assert idk.sdk_opts.image_trim_tolerant is True


def test_image_trim_tolerant_option_env(monkeypatch):
    monkeypatch.setenv("ISCC_SDK_IMAGE_TRIM_TOLERANT", "false")
    assert idk.SdkOptions().image_trim_tolerant is False


def test_image_normalize_tolerant_off_unchanged(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    img = noisy_white()
    assert list(idk.image_normalize(img)) == normalize_reference(img, tolerant=False)


def test_image_normalize_tolerant_on(monkeypatch):
    img = noisy_white()
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    off = list(idk.image_normalize(img))
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", True)
    on = list(idk.image_normalize(img))
    assert on == normalize_reference(img, tolerant=True)
    assert on != off


def test_image_normalize_tolerant_on_without_tolerant_crop(monkeypatch, jpg_obj):
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    off = list(idk.image_normalize(jpg_obj))
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", True)
    assert list(idk.image_normalize(jpg_obj)) == off


def test_image_normalize_tolerant_requires_trim_border(monkeypatch):
    img = noisy_white()
    monkeypatch.setattr(idk.sdk_opts, "image_trim_border", False)
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    off = list(idk.image_normalize(img))
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", True)
    assert list(idk.image_normalize(img)) == off


@pytest.fixture
def noisy_png(tmp_path):
    """Noisy white test image in a black frame, saved as PNG."""
    fp = tmp_path / "noisy.png"
    framed().save(fp)
    return fp


def test_image_normalize_per_call_options():
    img = noisy_white()
    before = idk.sdk_opts.model_dump()
    default = list(idk.image_normalize(img))
    off = list(idk.image_normalize(img, image_trim_tolerant=False))
    assert default == normalize_reference(img, tolerant=True)
    assert off == normalize_reference(img, tolerant=False)
    assert off != default
    assert idk.sdk_opts.model_dump() == before


def test_code_image_per_call_tolerant_off(noisy_png, monkeypatch):
    before = idk.sdk_opts.model_dump()
    default = idk.code_image(noisy_png, create_thumb=False)
    per_call = idk.code_image(noisy_png, create_thumb=False, image_trim_tolerant=False)
    assert idk.sdk_opts.model_dump() == before
    assert per_call.iscc != default.iscc
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    assert idk.code_image(noisy_png, create_thumb=False).iscc == per_call.iscc


def test_code_image_per_call_trim_border_off(noisy_png, monkeypatch):
    default = idk.code_image(noisy_png, create_thumb=False)
    per_call = idk.code_image(noisy_png, create_thumb=False, image_trim_border=False)
    assert idk.sdk_opts.image_trim_border is True
    assert per_call.iscc != default.iscc
    monkeypatch.setattr(idk.sdk_opts, "image_trim_border", False)
    assert idk.code_image(noisy_png, create_thumb=False).iscc == per_call.iscc


def test_code_iscc_per_call_tolerant_off(noisy_png, monkeypatch):
    before = idk.sdk_opts.model_dump()
    per_call = idk.code_iscc(noisy_png, add_units=True, image_trim_tolerant=False)
    assert idk.sdk_opts.model_dump() == before
    default_unit = idk.code_image(noisy_png, create_thumb=False).iscc
    assert default_unit not in per_call.units
    monkeypatch.setattr(idk.sdk_opts, "image_trim_tolerant", False)
    global_unit = idk.code_image(noisy_png, create_thumb=False).iscc
    assert global_unit in per_call.units
    assert idk.code_iscc(noisy_png, add_units=True).iscc == per_call.iscc
