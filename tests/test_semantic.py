import pytest
import iscc_sdk as idk


# Skip tests if packages are not installed
sci_installed = idk.is_installed("iscc_sci")
sct_installed = idk.is_installed("iscc_sct")


@pytest.mark.skipif(sct_installed, reason="iscc-sct is installed")
def test_code_text_semantic_raises(doc_file):
    with pytest.raises(idk.EnvironmentError):
        idk.code_text_semantic(doc_file)


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_code_text_semantic(doc_file):
    assert idk.code_text_semantic(doc_file).dict() == {
        "iscc": "ISCC:CAA7X3SMP7IQ4Z65",
        "characters": 6068,
    }
