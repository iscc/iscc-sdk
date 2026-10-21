"""Tests for C2PA soft bindings (`io.iscc.v0`, IEP-0020)."""

import base64
import json
import shutil

import iscc_lib as il
import numpy as np
import pytest
from iscc_samples import images, texts
from loguru import logger
from PIL import Image
from pypdf import PdfWriter
from typer.testing import CliRunner

import iscc_sdk as idk
from iscc_sdk.c2pa import encode_seq, soft_binding_check_unit
from iscc_sdk.cli import app

runner = CliRunner()

VECTOR_1_UNITS = [
    "ISCC:AADVPDD4R6733NMPFH3D57VTQ4KVH6VHL74XIWGUT37V5ZG56NV3NSI",
    "ISCC:EAD2RASIYU5IKLENP2OFI4CHZGRWYQCSW2WKX3Y6FJGOCXSYNYGLGBI",
    "ISCC:GADQLNA7GRZESMRF2J7NZPNWGI3II2ST5YUN5SS6GVQ2ZQGJXPPYDNI",
    "ISCC:IAD2KIVPJIWJZP3KQCESJL6SVT5APEZUPOJWM6HVTAXCF7OT3VFA4NY",
]
VECTOR_1_HEX = (
    "0007578c7c8fbfbdb58f29f63efeb3871553faa75ff97458d49eff5ee4ddf36bb6c92007a88248c53a852c8d7e9c"
    "547047c9a36c4052b6acabef1e2a4ce15e586e0cb305300705b41f3472493225d27edcbdb63236846a53ee28deca"
    "5e3561acc0c9bbdf81b54007a522af4a2c9cbf6a808924afd2acfa0793347b936678f5982e22fdd3dd4a0e37"
)
VECTOR_1_BASE64 = (
    "AAdXjHyPv721jyn2Pv6zhxVT+qdf+XRY1J7/XuTd82u2ySAHqIJIxTqFLI1+nFRwR8mjbEBStqyr7x4qTOFeWG4MswUw"
    "BwW0HzRySTIl0n7cvbYyNoRqU+4o3speNWGswMm734G1QAelIq9KLJy/aoCJJK/SrPoHkzR7k2Z49ZguIv3T3UoONw=="
)
VECTOR_2_UNITS = [
    "ISCC:EEAYYNMFG5XOELK2",
    "ISCC:EIBZ6B7T76PAAYP7H334X77754376",
    "ISCC:GADQLNA7GRZESMRF2J7NZPNWGI3II2ST5YUN5SS6GVQ2ZQGJXPPYDNI",
]
VECTOR_2_HEX = (
    "21018c3585376ee22d5a22039f07f3ff9e0061ff3ef7cbffffef37ff300705b41f3472493225d27edcbdb6323684"
    "6a53ee28deca5e3561acc0c9bbdf81b5"
)

sci_installed = idk.is_installed("iscc_sci")
sct_installed = idk.is_installed("iscc_sct")


@pytest.fixture
def warnings():
    """Collect loguru warning messages."""
    messages = []
    handler = logger.add(lambda msg: messages.append(msg.record["message"]), level="WARNING")
    yield messages
    logger.remove(handler)


def prefixes(units):
    """Return the first three characters (MainType, SubType, Length) of each unit code."""
    return [unit.removeprefix("ISCC:")[:3] for unit in units]


def test_encode_seq_vector_1():
    value = encode_seq(VECTOR_1_UNITS)
    assert len(value) == 136
    assert value.hex() == VECTOR_1_HEX
    assert base64.b64encode(value).decode("ascii") == VECTOR_1_BASE64


def test_encode_seq_vector_2():
    assert encode_seq(VECTOR_2_UNITS).hex() == VECTOR_2_HEX


def test_soft_binding_image(jpg_file):
    sb = idk.soft_binding(jpg_file, semantic=False)
    assert isinstance(sb, idk.SoftBinding)
    assert prefixes(sb.units) == ["AAD", "EED", "GAD", "IAD"]
    for unit in sb.units:
        _, _, version, length, body = il.iscc_decode(unit)
        assert (version, length, len(body)) == (0, 7, 32)
    with open(jpg_file, "rb") as infile:
        instance = il.gen_instance_code_v0(infile, bits=256)["iscc"]
    assert sb.units[-1] == instance
    assert sb.value == encode_seq(sb.units)


def test_soft_binding_no_title_ignores_file_name(tmp_path):
    first = tmp_path / "first.bmp"
    second = tmp_path / "renamed-copy.bmp"
    shutil.copy(images("bmp")[0], first)
    shutil.copy(images("bmp")[0], second)
    sb = idk.soft_binding(first, semantic=False)
    assert prefixes(sb.units) == ["EED", "GAD", "IAD"]
    assert idk.soft_binding(second, semantic=False) == sb


def test_soft_binding_unsupported(warnings):
    sb = idk.soft_binding(texts("sqlite")[0], semantic=True)
    assert prefixes(sb.units) == ["GAD", "IAD"]
    assert any("Data-Code and Instance-Code only" in msg for msg in warnings)


def test_soft_binding_featureless_image(tmp_path, warnings):
    fp = tmp_path / "white.png"
    Image.new("RGB", (64, 48), (255, 255, 255)).save(fp)
    sb = idk.soft_binding(fp, semantic=False)
    assert prefixes(sb.units) == ["GAD", "IAD"]
    assert any("Featureless Image-Code" in msg for msg in warnings)


@pytest.fixture
def blank_pdf(tmp_path):
    """Create a PDF with a single blank page (no extractable text)."""
    fp = tmp_path / "blank.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.write(fp)
    return fp


def test_soft_binding_no_text(blank_pdf, warnings):
    sb = idk.soft_binding(blank_pdf, semantic=False)
    assert prefixes(sb.units) == ["GAD", "IAD"]
    assert any("No text extracted" in msg for msg in warnings)


def test_soft_binding_no_text_whitespace(tmp_path, warnings):
    """A non-PDF document with only whitespace gets Data-Code and Instance-Code."""
    fp = tmp_path / "blank.txt"
    fp.write_text("   \n\t  \n")
    sb = idk.soft_binding(fp, semantic=False)
    assert prefixes(sb.units) == ["GAD", "IAD"]
    assert any("No text extracted" in msg for msg in warnings)


def test_soft_binding_unparseable_text(tmp_path, warnings):
    """A document Tika cannot parse gets Data-Code and Instance-Code (no Meta-Code)."""
    fp = tmp_path / "empty.txt"
    fp.write_bytes(b"")
    sb = idk.soft_binding(fp, semantic=False)
    assert prefixes(sb.units) == ["GAD", "IAD"]
    assert any("Text-Codes left out" in msg for msg in warnings)
    assert any("Meta-Code left out" in msg for msg in warnings)


@pytest.fixture
def product_png(tmp_path):
    """Create a textured product on a faintly noisy white background (trim settings matter)."""
    rng = np.random.default_rng(0)
    a = rng.normal(250, 2, (300, 400, 3)).round().clip(0, 255).astype(np.uint8)
    a[80:220, 120:300] = rng.integers(0, 256, (140, 180, 3), dtype=np.uint8)
    fp = tmp_path / "product.png"
    Image.fromarray(a, "RGB").save(fp)
    return fp


def test_soft_binding_ignores_sdk_settings(product_png, monkeypatch):
    """SDK settings from environment variables or iscc-sdk.env do not change a soft binding."""
    expected = idk.soft_binding(product_png, semantic=False)
    image_code = idk.code_image(product_png, bits=256).iscc
    settings = {
        "image_trim_tolerant": False,
        "image_trim_border": False,
        "image_fill_transparency": False,
        "image_exif_transpose": False,
        "bits": 64,
    }
    for field, value in settings.items():
        monkeypatch.setattr(idk.sdk_opts, field, value)
    assert idk.code_image(product_png, bits=256).iscc != image_code
    assert idk.soft_binding(product_png, semantic=False) == expected


def test_soft_binding_video_ignores_sdk_settings(mp4_file, tmp_path, monkeypatch):
    """Video settings neither change a soft binding nor write a signature file next to the asset."""
    fp = shutil.copy(mp4_file, tmp_path / "video.mp4")
    expected = idk.soft_binding(fp, semantic=False)
    monkeypatch.setattr(idk.sdk_opts, "video_fps", 1)
    monkeypatch.setattr(idk.sdk_opts, "video_store_mp7sig", True)
    assert idk.soft_binding(fp, semantic=False) == expected
    assert list(tmp_path.iterdir()) == [tmp_path / "video.mp4"]


@pytest.mark.parametrize("fp", [images("jpg")[0], texts("txt")[0]], ids=["image", "text"])
def test_soft_binding_semantic_missing(fp, monkeypatch):
    monkeypatch.setattr(idk, "is_installed", lambda name: False)
    with pytest.raises(idk.EnvironmentError, match=r"iscc-sdk\[c2pa\]"):
        idk.soft_binding(fp)


def test_soft_binding_check_unit():
    soft_binding_check_unit(VECTOR_1_UNITS[0])
    with pytest.raises(idk.IsccError, match="256 bits"):
        soft_binding_check_unit("ISCC:EEAYYNMFG5XOELK2")


def test_soft_binding_definition(jpg_file):
    sb = idk.soft_binding(jpg_file, semantic=False)
    assert idk.soft_binding_definition(sb) == {
        "label": "c2pa.soft-binding",
        "created": True,
        "data": {
            "alg": "io.iscc.v0",
            "blocks": [{"scope": {}, "value": list(sb.value)}],
            "bindingMetadata": {
                "informationalUrl": "https://ieps.iscc.codes/iep-0020/",
                "io.iscc.generator": {"name": "iscc-sdk", "version": idk.__version__},
            },
        },
    }


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_soft_binding_semantic_image(jpg_file):
    sb = idk.soft_binding(jpg_file)
    assert prefixes(sb.units) == ["AAD", "CED", "EED", "GAD", "IAD"]
    assert sb.units[1:] != idk.soft_binding(jpg_file, semantic=False).units[1:]


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_soft_binding_semantic_svg(svg_file):
    sb = idk.soft_binding(svg_file)
    assert prefixes(sb.units) == ["AAD", "CED", "EED", "GAD", "IAD"]


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_soft_binding_semantic_text():
    sb = idk.soft_binding(texts("txt")[0])
    assert prefixes(sb.units) == ["CAD", "EAD", "GAD", "IAD"]


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_soft_binding_semantic_image_ignores_sci_settings(product_png, monkeypatch):
    """iscc-sci settings (ISCC_SCI_* environment variables, .env) do not change a soft binding."""
    import iscc_sci

    expected = idk.soft_binding(product_png)
    semantic = idk.code_image_semantic(product_png, bits=256).iscc
    monkeypatch.setattr(iscc_sci.sci_opts, "image_trim_tolerant", False)
    monkeypatch.setattr(iscc_sci.sci_opts, "bits", 64)
    assert idk.code_image_semantic(product_png, bits=256).iscc != semantic
    assert idk.soft_binding(product_png) == expected


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_soft_binding_semantic_text_ignores_sct_settings(monkeypatch):
    """iscc-sct settings (ISCC_SCT_* environment variables, .env) do not change a soft binding."""
    import iscc_sct

    fp = texts("txt")[0]
    text = il.text_clean(idk.text_extract(fp))
    expected = idk.soft_binding(fp)
    semantic = idk.code_text_semantic(fp, text, bits=256).iscc
    monkeypatch.setattr(iscc_sct.sct_opts, "max_tokens", 32)
    monkeypatch.setattr(iscc_sct.sct_opts, "overlap", 8)
    monkeypatch.setattr(iscc_sct.sct_opts, "bits", 64)
    assert idk.code_text_semantic(fp, text, bits=256).iscc != semantic
    assert idk.soft_binding(fp) == expected


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_soft_binding_semantic_no_text(blank_pdf):
    assert prefixes(idk.soft_binding(blank_pdf).units) == ["GAD", "IAD"]


def test_cli_soft_binding(jpg_file):
    result = runner.invoke(app, ["soft-binding", "--no-semantic", jpg_file])
    assert result.exit_code == 0
    sb = idk.soft_binding(jpg_file, semantic=False)
    assert json.loads(result.stdout) == idk.soft_binding_definition(sb)
    assert result.stderr.split() == sb.units
    lines = result.stdout.splitlines()
    value_lines = [line for line in lines if '"value"' in line]
    assert value_lines == [f'        "value": {json.dumps(list(sb.value))}']
    assert len(lines) < 25


def test_cli_soft_binding_missing_file(tmp_path):
    result = runner.invoke(app, ["soft-binding", "--no-semantic", str(tmp_path / "missing.jpg")])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert result.stderr.startswith("Error:")


def test_cli_soft_binding_semantic_missing(jpg_file, monkeypatch):
    monkeypatch.setattr(idk, "is_installed", lambda name: False)
    result = runner.invoke(app, ["soft-binding", jpg_file])
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "iscc-sdk[c2pa]" in result.stderr
