import iscc_sdk as idk


def test_ipfs_cidv1(jpg_file):
    assert idk.ipfs_cidv1(jpg_file) == "bafkreibpvnkawhupqto4zouc3nve5rjyahddf33agrksajkdos3q2ud4iq"


def test_ipfs_cidv1_wrap(jpg_file):
    assert (
        idk.ipfs_cidv1(jpg_file, wrap=True)
        == "bafybeicg5clgwhge6eyzzvuvtsch6eenqjhc2osm42qmuza6xbrgui3kpy/img.jpg"
    )


def test_ipfs_cidv1_base16(jpg_file):
    assert (
        idk.ipfs_cidv1_base16(jpg_file)
        == "f015512202fab540b1e8f84ddccba82db6a4ec53801c632ef60345520254374b70d507c44"
    )
