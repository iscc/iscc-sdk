# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
import iscc_core as ic
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
    assert im == {"iscc": "ISCC:MEAJU5AXCPOIOYFL"}


def test_IsccMeta_json():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.json() == (
        '{"@context": "http://purl.org/iscc/context/0.4.0.jsonld", "@type": '
        '"CreativeWork", "$schema": "http://purl.org/iscc/schema/0.4.0.json", "iscc": '
        '"ISCC:MEAJU5AXCPOIOYFL"}'
    )


def test_IsccMeta_jcs():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.jcs() == (
        b'{"$schema":"http://purl.org/iscc/schema/0.4.0.json","@context":"http://purl.'
        b'org/iscc/context/0.4.0.jsonld","@type":"CreativeWork","iscc":"ISCC:MEAJU5AXC'
        b'POIOYFL"}'
    )


def test_IsccMeta_iscc_obj():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert isinstance(im.iscc_obj, ic.Code)
