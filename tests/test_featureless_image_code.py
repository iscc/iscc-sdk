"""Tests for `is_featureless_image_code`, the featureless Image-Code predicate."""

import iscc_lib as il
import pytest
from iscc_samples import images, texts
from PIL import Image

import iscc_sdk as idk

VECTORS = [
    ("ISCC:EEAYAAAAAAAAAAAA", "8000000000000000", True),
    ("ISCC:EEAQAAAAAAAAAAAA", "0000000000000000", True),
    ("ISCC:EEA74AAAAAAAAAAA", "fe00000000000000", True),
    ("ISCC:EEA76AAAAAAAAAAA", "ff00000000000000", False),
    ("ISCC:EEDYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", "80" + "00" * 31, True),
    (
        "ISCC:EED74AAAAAAAAAAAVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKQ",
        "fe00000000000000" + "aa" * 24,
        True,
    ),
    (
        "ISCC:EED76AAAAAAAAAAAVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKQ",
        "ff00000000000000" + "aa" * 24,
        False,
    ),
    (
        "ISCC:EED2VKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKAAAAAAAAAAAAA",
        "aa" * 24 + "8000000000000000",
        True,
    ),
    ("ISCC:EED2VKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKVKQ", "aa" * 32, False),
]


def image_code(body):
    """Encode an Image-Code unit from raw body bytes."""
    return "ISCC:" + il.encode_component(il.MT.CONTENT, il.ST.IMAGE, il.VS.V0, len(body) * 8, body)


def ramp():
    """Horizontal left-to-right 0-255 grayscale ramp."""
    img = Image.new("L", (256, 64))
    img.putdata([x for _ in range(64) for x in range(256)])
    return img


@pytest.mark.parametrize("iscc, body_hex, featureless", VECTORS)
def test_is_featureless_image_code_vectors(iscc, body_hex, featureless):
    assert il.iscc_decode(iscc)[4].hex() == body_hex
    assert idk.is_featureless_image_code(iscc) is featureless


def test_is_featureless_image_code_without_prefix():
    assert idk.is_featureless_image_code("EEAYAAAAAAAAAAAA") is True
    assert idk.is_featureless_image_code("EEA76AAAAAAAAAAA") is False


def test_is_featureless_image_code_iscc_code():
    iscc_code = "ISCC:KEAYAAAAAAAAAAAAXFOYGQU2SHFQKF3WF7O5S2NEKM"
    assert il.iscc_decompose(iscc_code)[0] == "EEAYAAAAAAAAAAAA"
    assert idk.is_featureless_image_code(iscc_code) is True


def test_is_featureless_image_code_partial_segment_ignored():
    regular = bytes.fromhex("aa" * 8)
    assert idk.is_featureless_image_code(image_code(regular + bytes(4))) is False
    assert idk.is_featureless_image_code(image_code(bytes(8) + bytes.fromhex("ff" * 4))) is True


def test_is_featureless_image_code_too_short():
    with pytest.raises(ValueError, match="too short"):
        idk.is_featureless_image_code(image_code(bytes(4)))


def test_is_featureless_image_code_other_units():
    data_code = il.gen_data_code_v0(b"a")["iscc"]
    semantic = "ISCC:" + il.encode_component(il.MT.SEMANTIC, il.ST.IMAGE, il.VS.V0, 64, bytes(8))
    text_code = "ISCC:" + il.encode_component(il.MT.CONTENT, il.ST.TEXT, il.VS.V0, 64, bytes(8))
    for iscc in (data_code, semantic, text_code):
        assert idk.is_featureless_image_code(iscc) is False


def test_is_featureless_image_code_invalid():
    with pytest.raises(ValueError):
        idk.is_featureless_image_code("ISCC:NOTANISCC")


@pytest.mark.parametrize("bits", [64, 256])
@pytest.mark.parametrize(
    "img",
    [
        Image.new("RGB", (64, 48), (255, 255, 255)),
        Image.new("RGB", (64, 48), (128, 128, 128)),
        ramp(),
    ],
    ids=["white", "grey", "ramp"],
)
def test_is_featureless_image_code_blank_images(img, bits, tmp_path):
    fp = tmp_path / "blank.png"
    img.save(fp)
    iscc = idk.code_image(fp, bits=bits, create_thumb=False).iscc
    assert idk.is_featureless_image_code(iscc) is True


@pytest.mark.parametrize("bits", [64, 256])
@pytest.mark.parametrize("fp", images(), ids=lambda p: p.name)
def test_is_featureless_image_code_sample_photos(fp, bits):
    iscc = idk.code_image(fp, bits=bits, create_thumb=False).iscc
    assert idk.is_featureless_image_code(iscc) is False


def test_is_featureless_image_code_code_iscc():
    assert idk.is_featureless_image_code(idk.code_iscc(images("jpg")[0]).iscc) is False
    assert idk.is_featureless_image_code(idk.code_iscc(texts("txt")[0]).iscc) is False
