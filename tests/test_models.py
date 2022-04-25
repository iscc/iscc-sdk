# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError
import iscc_schema as iss
import iscc_core as ic


def test_IsccMeta_extra_forbid():
    with pytest.raises(ValidationError):
        iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL", somefield="not allowed")

    with pytest.raises(ValueError):
        im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
        im.other = "test"


def test_IsccMeta_validate_assignment():
    im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    with pytest.raises(ValidationError):
        im.iscc = "MEAJU5AXCPOIOYFL"


def test_IsccMeta_dict_defaults_exclude_none_unset():
    im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im == {"iscc": "ISCC:MEAJU5AXCPOIOYFL"}


def test_IsccMeta_json():
    im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.json() == (
        '{"@context": "http://purl.org/iscc/context/0.3.7.jsonld", "@type": '
        '"CreativeWork", "$schema": "http://purl.org/iscc/schema/0.3.7.json", "iscc": '
        '"ISCC:MEAJU5AXCPOIOYFL"}'
    )


def test_IsccMeta_jcs():
    im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.jcs() == (
        b'{"$schema":"http://purl.org/iscc/schema/0.3.7.json","@context":"http://purl.'
        b'org/iscc/context/0.3.7.jsonld","@type":"CreativeWork","iscc":"ISCC:MEAJU5AXC'
        b'POIOYFL"}'
    )


def test_IsccMeta_iscc_obj():
    im = iss.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert isinstance(im.iscc_obj, ic.Code)
