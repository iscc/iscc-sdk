"""*C2PA soft bindings with ISCC-UNITs (`io.iscc.v0`) as specified by IEP-0020*."""

import base64
from pathlib import Path
from typing import NamedTuple

import iscc_lib as il
from loguru import logger as log

import iscc_sdk as idk

__all__ = [
    "SoftBinding",
    "soft_binding",
    "soft_binding_definition",
]

SOFT_BINDING_ALG = "io.iscc.v0"
SOFT_BINDING_BITS = 256
IEP_0020_URL = "https://ieps.iscc.codes/iep-0020/"
SOFT_BINDING_HINT = "Install `iscc-sdk[c2pa]` or disable Semantic-Codes (`--no-semantic`)."
SEMANTIC_PACKAGES = {"image": "iscc_sci", "text": "iscc_sct"}


class SoftBinding(NamedTuple):
    """ISCC soft binding of an asset.

    :ivar units: ISCC-UNITs in fixed order (Meta, Semantic, Content, Data, Instance)
    :ivar value: ISCC-SEQ bytes of the units (content of `blocks[].value`)
    """

    units: list[str]
    value: bytes


def soft_binding(fp, semantic=True):
    # type: (str|Path, bool) -> SoftBinding
    """
    Create an ISCC soft binding (IEP-0020) for a file.

    Every ISCC-UNIT is Version 0 with a 256-bit body. The units are, in this order:

    - Meta-Code: only if the embedded metadata yields a title (never from the file name)
    - Semantic-Code: image and text mode, if `semantic` is True
    - Content-Code: image, audio, video and text mode (a featureless Image-Code is left out)
    - Data-Code and Instance-Code: always

    Unsupported media types and documents without extractable text get only a Data-Code and an
    Instance-Code (plus a Meta-Code if there is a title).

    :param fp: Filepath of the asset, processed as a whole exactly as it will be signed.
    :param semantic: Include Semantic-Codes (requires iscc-sci for images, iscc-sct for text).
    :return: Soft binding with ISCC-UNITs and ISCC-SEQ value.
    :raises idk.EnvironmentError: If `semantic` is True and the required package is missing.
    """
    fp = Path(fp)
    mode = soft_binding_mode(fp)
    package = SEMANTIC_PACKAGES.get(mode or "")
    if semantic and package and not idk.is_installed(package):
        raise idk.EnvironmentError(
            f"Semantic-Code {mode} requires `{package}`. {SOFT_BINDING_HINT}"
        )
    units = [unit for unit in soft_binding_media_units(fp, mode, semantic) if unit]
    units += il.gen_sum_code_v0(fp, bits=SOFT_BINDING_BITS, add_units=True)["units"]
    for unit in units:
        soft_binding_check_unit(unit)
    return SoftBinding(units=units, value=encode_seq(units))


def soft_binding_definition(sb):
    # type: (SoftBinding) -> dict
    """
    Create the `c2pa.soft-binding` assertion for a c2pa-rs manifest definition.

    The value is a list of integers (0-255). c2pa-rs releases with PR 2757 store it as a CBOR byte
    string, earlier releases as a CBOR array of integers. IEP-0020 readers accept both.

    :param sb: Soft binding from `soft_binding`.
    :return: Assertion definition with label, created flag and data.
    """
    return {
        "label": "c2pa.soft-binding",
        "created": True,
        "data": {
            "alg": SOFT_BINDING_ALG,
            "blocks": [{"scope": {}, "value": list(sb.value)}],
            "bindingMetadata": {
                "informationalUrl": IEP_0020_URL,
                "io.iscc.generator": {"name": "iscc-sdk", "version": idk.__version__},
            },
        },
    }


def soft_binding_mode(fp):
    # type: (Path) -> str|None
    """Detect the processing mode of a file, None for unsupported media types (with a warning)."""
    try:
        return str(idk.mediatype_and_mode(fp)[1])
    except idk.IsccUnsupportedMediatype as e:
        log.warning(f"{e} - soft binding with Data-Code and Instance-Code only (byte-level match)")
        return None


def soft_binding_media_units(fp, mode, semantic):
    # type: (Path, str|None, bool) -> list[str|None]
    """Create Meta-, Semantic- and Content-Code of a file (None where a unit is left out)."""
    if mode is None:
        return []
    opts = dict(bits=SOFT_BINDING_BITS, extract_meta=False, create_thumb=False)
    if mode == "image":
        content = idk.code_image(fp, **opts).iscc
        if idk.is_featureless_image_code(content):
            log.warning(f"Featureless Image-Code {content} of {fp.name} left out of soft binding")
            content = None
        sem = soft_binding_image_semantic(fp) if semantic else None
    elif mode == "text":
        text = soft_binding_text(fp)
        if not text:
            return [soft_binding_meta(fp), None, None]
        content = idk.code_text(fp, text, **opts).iscc
        sem = soft_binding_text_semantic(fp, text) if semantic else None
    else:
        content = idk.code_content(fp, **opts).iscc
        sem = None
    return [soft_binding_meta(fp), sem, content]


def soft_binding_text(fp):
    # type: (Path) -> str
    """Extract cleaned text of a document, empty (with a warning) if it has no extractable text."""
    try:
        text = il.text_clean(idk.text_extract(fp))
    except idk.IsccExtractionError as e:
        log.warning(f"{e} - Text-Codes left out of soft binding")
        return ""
    if not text:
        log.warning(f"No text extracted from {fp.name} - Text-Codes left out of soft binding")
    return text


def soft_binding_image_semantic(fp):  # pragma: nocover
    # type: (Path) -> str
    """Create the 256-bit Semantic-Code Image with the SDK image trim setting."""
    trim = idk.sdk_opts.image_trim_tolerant
    return idk.code_image_semantic(fp, bits=SOFT_BINDING_BITS, image_trim_tolerant=trim).iscc


def soft_binding_text_semantic(fp, text):  # pragma: nocover
    # type: (Path, str) -> str
    """Create the 256-bit Semantic-Code Text from cleaned text."""
    return idk.code_text_semantic(fp, text, bits=SOFT_BINDING_BITS).iscc


def soft_binding_meta(fp):
    # type: (Path) -> str|None
    """
    Create the 256-bit Meta-Code from the embedded title and description of a file.

    Returns None if the metadata cannot be read or the title is empty after normalization. Unlike
    `code_meta` there is no fallback to the file name, so renaming a file does not change its soft
    binding.
    """
    try:
        meta = idk.extract_metadata(fp)
    except idk.IsccExtractionError as e:
        log.warning(f"{e} - Meta-Code left out of soft binding")
        return None
    name = il.text_trim(
        il.text_remove_newlines(il.text_clean(meta.name or "")), il.core_opts.meta_trim_name
    )
    if not name:
        return None
    return il.gen_meta_code_v0(
        name=meta.name, description=meta.description, bits=SOFT_BINDING_BITS
    )["iscc"]


def soft_binding_check_unit(unit):
    # type: (str) -> None
    """Raise IsccError if an ISCC-UNIT is not Version 0 with a 256-bit body."""
    _, _, version, length, _ = il.iscc_decode(unit)
    if version != 0 or length != 7:
        raise idk.IsccError(f"Soft binding requires Version 0 ISCC-UNITs with 256 bits, got {unit}")


def encode_seq(units):
    # type: (list[str]) -> bytes
    """Encode ISCC-UNITs as an ISCC-SEQ (concatenated header and body bytes of each unit)."""
    codes = [unit.removeprefix("ISCC:") for unit in units]
    return b"".join(base64.b32decode(code + "=" * (-len(code) % 8)) for code in codes)
