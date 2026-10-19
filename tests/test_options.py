import pytest
from iscc_samples import images
from PIL import Image

import iscc_sdk as idk

fp = images("jpg")[0].as_posix()


def test_image_max_pixels_small(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_max_pixels", 10)
    with pytest.raises(Image.DecompressionBombError):
        idk.code_image(fp)


def test_image_max_pixels_None(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_max_pixels", None)
    r = idk.code_image(fp)
    assert r.iscc == "ISCC:EEA4GQZQTY6J5DTH"


def test_sdk_options_default():
    assert isinstance(idk.sdk_opts, idk.SdkOptions)
    assert idk.sdk_opts.granular is False
    assert idk.sdk_opts.extract_meta is True
    assert idk.sdk_opts.create_thumb is True


def test_sdk_options_override():
    new_opts = idk.sdk_opts.override({"granular": True, "extract_meta": False})
    assert new_opts.granular is True
    assert new_opts.extract_meta is False
    assert new_opts.create_thumb is True  # Unchanged
    assert idk.sdk_opts.granular is False  # Original instance unchanged
    assert idk.sdk_opts.extract_meta is True  # Original instance unchanged


def test_sdk_options_override_invalid_field():
    with pytest.raises(ValueError, match="Invalid field: invalid_field"):
        idk.sdk_opts.override({"invalid_field": True})


def test_sdk_options_image_max_pixels():
    original_max_pixels = Image.MAX_IMAGE_PIXELS
    new_opts = idk.SdkOptions(image_max_pixels=1000000)
    assert new_opts.image_max_pixels == 1000000
    assert Image.MAX_IMAGE_PIXELS == 1000000

    # Reset to original value
    Image.MAX_IMAGE_PIXELS = original_max_pixels


def test_sdk_options_override_empty():
    new_opts = idk.sdk_opts.override()
    assert new_opts.granular == idk.sdk_opts.granular
    assert new_opts.extract_meta == idk.sdk_opts.extract_meta
    assert new_opts.create_thumb == idk.sdk_opts.create_thumb


def test_sdk_options_override_multiple_fields():
    new_opts = idk.sdk_opts.override(
        {
            "granular": True,
            "extract_meta": False,
            "create_thumb": False,
        }
    )
    assert new_opts.granular is True
    assert new_opts.extract_meta is False
    assert new_opts.create_thumb is False


def test_sdk_options_override_image_max_pixels_differing_raises(monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", Image.MAX_IMAGE_PIXELS)
    before = Image.MAX_IMAGE_PIXELS
    with pytest.raises(ValueError, match="process-wide.*ISCC_SDK_IMAGE_MAX_PIXELS"):
        idk.sdk_opts.override({"image_max_pixels": 500000})
    with pytest.raises(ValueError, match="process-wide"):
        idk.sdk_opts.override({"image_max_pixels": None})
    assert Image.MAX_IMAGE_PIXELS == before
    assert idk.sdk_opts.image_max_pixels == before


def test_code_image_per_call_image_max_pixels_raises(monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", Image.MAX_IMAGE_PIXELS)
    before = Image.MAX_IMAGE_PIXELS
    with pytest.raises(ValueError, match="process-wide"):
        idk.code_image(fp, image_max_pixels=10)
    with pytest.raises(ValueError, match="process-wide"):
        idk.code_iscc(fp, image_max_pixels=10)
    assert Image.MAX_IMAGE_PIXELS == before


def test_sdk_options_override_image_max_pixels_equal_passes(monkeypatch):
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", Image.MAX_IMAGE_PIXELS)
    current = idk.sdk_opts.image_max_pixels
    new_opts = idk.sdk_opts.override({"image_max_pixels": current, "granular": True})
    assert new_opts.image_max_pixels == current
    assert new_opts.granular is True
    assert Image.MAX_IMAGE_PIXELS == current
    r = idk.code_image(fp, image_max_pixels=current)
    assert r.iscc == "ISCC:EEA4GQZQTY6J5DTH"


def test_sdk_options_override_image_max_pixels_follows_global(monkeypatch):
    monkeypatch.setattr(idk.sdk_opts, "image_max_pixels", 500000)
    assert Image.MAX_IMAGE_PIXELS == 500000
    assert idk.sdk_opts.override({"image_max_pixels": 500000}).image_max_pixels == 500000
    with pytest.raises(ValueError, match="process-wide"):
        idk.sdk_opts.override({"image_max_pixels": 128000000})
