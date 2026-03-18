# -*- coding: utf-8 -*-
import pytest

from pydantic import ValidationError
import iscc_sdk as idk


def test_IsccMeta_extra_forbid():
    with pytest.raises(ValidationError):
        idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL", somefield="not allowed")

    with pytest.raises(ValueError):
        im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
        im.other = "test"


def test_IsccMeta_validate_assignment():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    with pytest.raises(ValidationError):
        im.iscc = "MEAJU5AXCPOIOYFL"


def test_IsccMeta_dict_defaults_exclude_none_unset():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.dict() == {"iscc": "ISCC:MEAJU5AXCPOIOYFL"}


def test_IsccMeta_json():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.json() == (
        '{"@context":"http://purl.org/iscc/context/0.5.0.jsonld",'
        '"@type":"CreativeWork",'
        '"$schema":"http://purl.org/iscc/schema/0.5.0.json",'
        '"iscc":"ISCC:MEAJU5AXCPOIOYFL"}'
    )


def test_IsccMeta_jcs():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.jcs() == (
        b'{"$schema":"http://purl.org/iscc/schema/0.5.0.json",'
        b'"@context":"http://purl.org/iscc/context/0.5.0.jsonld",'
        b'"@type":"CreativeWork",'
        b'"iscc":"ISCC:MEAJU5AXCPOIOYFL"}'
    )


def test_IsccMeta_iscc_obj():
    """Test iscc_obj raises ImportError when iscc-core is not installed."""
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    with pytest.raises(ImportError, match="iscc-core"):
        im.iscc_obj
