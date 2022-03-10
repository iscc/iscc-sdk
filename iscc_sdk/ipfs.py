"""IPFS wrapper"""
import sys
import iscc_sdk as idk
import subprocess


__all__ = [
    "ipfs_cidv1",
    "ipfs_cidv1_base16",
]


def ipfs_cidv1(fp):
    # type: (str) -> str
    """
    Create default IPFS CIDv1.

    :param str fp: Filepath
    :return: IPFS CIDv1 of the file
    :rtype: str
    """
    cmd = [
        idk.ipfs_bin(),
        "add",
        "--only-hash",
        "--cid-version=1",
        "--offline",
        "--quieter",
        fp,
    ]

    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode(sys.stdout.encoding).strip()


def ipfs_cidv1_base16(fp):
    # type: (str) -> str
    """
    Create IPFS CIDv1 with base16 encoding.

    :param str fp: Filepath
    :return: IPFS CIDv1 of the file in base16 (hex)
    :rtype: str
    """
    cmd = [
        idk.ipfs_bin(),
        "add",
        "--only-hash",
        "--cid-version=1",
        "--offline",
        "--quieter",
        "--cid-base=base16",
        fp,
    ]

    result = subprocess.run(cmd, capture_output=True, check=True)
    return result.stdout.decode(sys.stdout.encoding).strip()
