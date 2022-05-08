"""IPFS wrapper"""
import sys
from os.path import basename
import iscc_sdk as idk


__all__ = [
    "ipfs_cidv1",
    "ipfs_cidv1_base16",
]


def ipfs_cidv1(fp, wrap=False):
    # type: (str) -> str
    """
    Create default IPFS CIDv1 for file at filepath `fp`.

    If `wrap` is True, the file will be wrapped with a directory and the filname will be appended
    to the directory CIDv1 with a `/`.

    :param str fp: Filepath
    :return: IPFS CIDv1 of the file
    :rtype: str
    """
    args = ["add", "--only-hash", "--cid-version=1", "--offline", "--quieter"]
    if wrap:
        args.append("--wrap-with-directory")
    args.append(fp)
    result = idk.run_ipfs(args)
    cid = result.stdout.decode(sys.stdout.encoding).strip()
    if wrap:
        cid += f"/{basename(fp)}"
    return cid


def ipfs_cidv1_base16(fp):
    # type: (str) -> str
    """
    Create IPFS CIDv1 with base16 encoding.

    :param str fp: Filepath
    :return: IPFS CIDv1 of the file in base16 (hex)
    :rtype: str
    """
    args = [
        "add",
        "--only-hash",
        "--cid-version=1",
        "--offline",
        "--quieter",
        "--cid-base=base16",
        fp,
    ]
    result = idk.run_ipfs(args)
    return result.stdout.decode(sys.stdout.encoding).strip()
