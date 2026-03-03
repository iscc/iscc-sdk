import os

import pytest

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


@pytest.fixture
def write_test_file(tmp_path):
    """Write test data to a temporary file and return its path."""

    def _write(data, name):
        fp = os.path.join(tmp_path, name)
        with open(fp, "wb") as f:
            f.write(data)
        return fp

    return _write


def test_ipfs_cidv1_single_chunk(write_test_file):
    """262144 bytes = exactly 1 chunk (raw leaf CID)."""
    fp = write_test_file(bytes(range(256)) * 1024, "iscc_test_262144.bin")
    assert idk.ipfs_cidv1(fp) == "bafkreibdci4uxwmvixm54ey4etx3paphmwwbv3beh4xnsndvs6tzhjav5e"
    assert (
        idk.ipfs_cidv1_base16(fp)
        == "f015512202312394bd99545d9de131c24efb781e765ac1aec243f2ed9347597a793a415e9"
    )


def test_ipfs_cidv1_two_chunks(write_test_file):
    """262145 bytes = 2 chunks (balanced DAG with dag-pb root)."""
    fp = write_test_file(bytes(range(256)) * 1024 + b"\x00", "iscc_test_262145.bin")
    assert idk.ipfs_cidv1(fp) == "bafybeibp4affrl5svfd2wwp3l2srpu76awzmvyc37zmrtap5iqydfxffuy"
    assert (
        idk.ipfs_cidv1_base16(fp)
        == "f017012202fe00a58afb2a947ab59fb5ea517d3fe05b2cae05bfe591981fd443032dca5a6"
    )


def test_ipfs_cidv1_two_full_chunks(write_test_file):
    """524288 bytes = 2 full chunks."""
    fp = write_test_file(bytes(range(256)) * 2048, "iscc_test_524288.bin")
    assert idk.ipfs_cidv1(fp) == "bafybeidskqir6ikiqxozidrejcofr3zho3eenlrvzlx56zysq2nqepsqhe"
    assert (
        idk.ipfs_cidv1_base16(fp)
        == "f017012207254111f214885dd940e24489c58ef2776c846ae35caefdf6712869b023e5039"
    )


def test_ipfs_cidv1_four_chunks(write_test_file):
    """1048576 bytes = 4 chunks."""
    fp = write_test_file(bytes(range(256)) * 4096, "iscc_test_1048576.bin")
    assert idk.ipfs_cidv1(fp) == "bafybeiclphklsx6bfzfb5aezogjldbkeicyyvma6wrfnielfg7haplwahy"
    assert (
        idk.ipfs_cidv1_base16(fp)
        == "f017012204b79d4b95fc12e4a1e80997192b1854440b18ab01eb44ad4116537ce07aec03e"
    )


def test_ipfs_cidv1_wrap_multi_chunk(write_test_file):
    """Directory wrapping for a multi-chunk file."""
    fp = write_test_file(bytes(range(256)) * 1024 + b"\x00", "iscc_test_262145.bin")
    assert (
        idk.ipfs_cidv1(fp, wrap=True)
        == "bafybeid26x42uk5em2jex75unscxde7h76iapcj24ezcplqjr7qsvybctu/iscc_test_262145.bin"
    )


def test_ipfs_cidv1_empty_file(write_test_file):
    """Empty file produces a valid raw leaf CID."""
    fp = write_test_file(b"", "empty.bin")
    cid = idk.ipfs_cidv1(fp)
    assert cid.startswith("bafkrei")
