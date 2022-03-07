# -*- coding: utf-8 -*-
import pytest
from pydantic import ValidationError

from iscc_sdk.models import IsccMeta


def test_IsccMeta_extra_forbid():
    with pytest.raises(ValidationError):
        IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL", somefield="not allowed")

    with pytest.raises(ValueError):
        im = IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
        im.other = "test"


def test_IsccMeta_validate_assignment():
    im = IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    with pytest.raises(ValidationError):
        im.iscc = "MEAJU5AXCPOIOYFL"


def test_IsccMeta_dict_defaults_exclude_none_unset():
    im = IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im == {"iscc": "ISCC:MEAJU5AXCPOIOYFL"}


def test_IsccMeta_json_ld():
    im = IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert im.json_ld() == (
        b'{"$schema":"http://purl.org/iscc/schema/0.3.3.json","@context":"http://purl.'
        b'org/iscc/context/0.3.3.jsonld","@type":"CreativeWork","iscc":"ISCC:MEAJU5AXC'
        b'POIOYFL"}'
    )
