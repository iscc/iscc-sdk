"""IPFS wrapper"""

import sys
from pathlib import Path
import iscc_sdk as idk


__all__ = [
    "ipfs_cidv1",
    "ipfs_cidv1_base16",
]


def ipfs_cidv1(fp, wrap=False):
    # type: (str|Path) -> str
    """
    Create default IPFS CIDv1 for file at filepath `fp`.

    If `wrap` is True, the file will be wrapped with a directory and the filname will be appended
    to the directory CIDv1 with a `/`.

    :param fp: Filepath
    :return: IPFS CIDv1 of the file
    """
    fp = Path(fp)
    args = ["add", "--only-hash", "--cid-version=1", "--offline", "--quieter"]
    if wrap:
        args.append("--wrap-with-directory")
    args.append(fp)
    result = idk.run_ipfs(args)
    encoding = sys.stdout.encoding or "utf-8"
    cid = result.stdout.decode(encoding).strip()
    if wrap:
        cid += f"/{fp.name}"
    return cid


def ipfs_cidv1_base16(fp):
    # type: (str|Path) -> str
    """
    Create IPFS CIDv1 with base16 encoding.

    :param fp: Filepath
    :return: IPFS CIDv1 of the file in base16 (hex)
    """
    fp = Path(fp)
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
    encoding = sys.stdout.encoding or "utf-8"
    return result.stdout.decode(encoding).strip()
