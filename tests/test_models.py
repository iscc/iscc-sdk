import iscc_schema
import pytest
from pydantic import ValidationError

import iscc_sdk as idk

# iscc-schema stamps its own version into the @context and $schema URLs.
SCHEMA_VERSION = iscc_schema.__version__


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
        f'{{"@context":"http://purl.org/iscc/context/{SCHEMA_VERSION}.jsonld",'
        '"@type":"CreativeWork",'
        f'"$schema":"http://purl.org/iscc/schema/{SCHEMA_VERSION}.json",'
        '"iscc":"ISCC:MEAJU5AXCPOIOYFL"}'
    )


def test_IsccMeta_jcs():
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    assert (
        im.jcs()
        == (
            f'{{"$schema":"http://purl.org/iscc/schema/{SCHEMA_VERSION}.json",'
            f'"@context":"http://purl.org/iscc/context/{SCHEMA_VERSION}.jsonld",'
            '"@type":"CreativeWork",'
            '"iscc":"ISCC:MEAJU5AXCPOIOYFL"}'
        ).encode()
    )


def test_IsccMeta_iscc_obj():
    """Test iscc_obj raises ImportError when iscc-core is not installed."""
    im = idk.IsccMeta(iscc="ISCC:MEAJU5AXCPOIOYFL")
    with pytest.raises(ImportError, match="iscc-core"):
        im.iscc_obj
