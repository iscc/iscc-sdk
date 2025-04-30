import pytest
import iscc_sdk as idk


# Skip tests if packages are not installed
sci_installed = idk.is_installed("iscc_sci")
sct_installed = idk.is_installed("iscc_sct")


@pytest.mark.skipif(sci_installed, reason="iscc-sci is installed")
def test_code_image_semantic_raises(doc_file):
    with pytest.raises(idk.EnvironmentError):
        idk.code_image_semantic(doc_file)


@pytest.mark.skipif(sct_installed, reason="iscc-sct is installed")
def test_code_text_semantic_raises(doc_file):
    with pytest.raises(idk.EnvironmentError):
        idk.code_text_semantic(doc_file)


@pytest.mark.skipif(not sci_installed, reason="iscc-sci not installed")
def test_code_image_semantic(jpg_file):
    assert idk.code_image_semantic(jpg_file).dict() == {"iscc": "ISCC:CEAQYWTPK2Q7ZTK4"}


@pytest.mark.skipif(not sct_installed, reason="iscc-sct not installed")
def test_code_text_semantic(doc_file):
    assert idk.code_text_semantic(doc_file).dict() == {
        "iscc": "ISCC:CAA7X3SMP7IQ4Z65",
        "characters": 6068,
    }
