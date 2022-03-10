import iscc_sdk as idk


def test_ipfs_cidv1_base16(jpg_file):
    assert (
        idk.ipfs_cidv1_base16(jpg_file)
        == "f015512202fab540b1e8f84ddccba82db6a4ec53801c632ef60345520254374b70d507c44"
    )
