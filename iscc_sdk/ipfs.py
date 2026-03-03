"""Pure Python IPFS CIDv1 computation (Kubo-compatible)."""

import hashlib
from base64 import b32encode
from pathlib import Path


__all__ = [
    "ipfs_cidv1",
    "ipfs_cidv1_base16",
]

# Kubo defaults for CIDv1
CHUNK_SIZE = 262144  # 256 KB fixed-size chunker
MAX_LINKS = 174  # DefaultLinksPerBlock
SHA2_256 = 0x12
DIGEST_LENGTH = 0x20
CODEC_RAW = 0x55
CODEC_DAG_PB = 0x70
UNIXFS_FILE = 2
UNIXFS_DIRECTORY = 1


def _varint_encode(n):
    """Encode unsigned integer as LEB128 varint."""
    buf = bytearray()
    while n > 0x7F:
        buf.append((n & 0x7F) | 0x80)
        n >>= 7
    buf.append(n & 0x7F)
    return bytes(buf)


def _sha256_digest(data):
    """Compute raw SHA-256 digest."""
    return hashlib.sha256(data).digest()


def _make_multihash(digest):
    """Prepend sha2-256 multihash header to digest."""
    return _varint_encode(SHA2_256) + _varint_encode(DIGEST_LENGTH) + digest


def _cid_bytes(codec, data):
    """Build CIDv1 binary from codec and data to hash."""
    digest = _sha256_digest(data)
    return _varint_encode(1) + _varint_encode(codec) + _make_multihash(digest)


def _cid_base32(cid_bytes):
    """Encode CID bytes as base32lower with 'b' prefix (no padding)."""
    return "b" + b32encode(cid_bytes).decode("ascii").lower().rstrip("=")


def _cid_base16(cid_bytes):
    """Encode CID bytes as base16 (hex) with 'f' prefix."""
    return "f" + cid_bytes.hex()


def _encode_varint_field(field_num, value):
    """Encode a protobuf varint field (wire type 0)."""
    return _varint_encode(field_num << 3 | 0) + _varint_encode(value)


def _encode_bytes_field(field_num, data):
    """Encode a protobuf length-delimited field (wire type 2)."""
    return _varint_encode(field_num << 3 | 2) + _varint_encode(len(data)) + data


def _encode_unixfs_data(type_val, filesize=None, blocksizes=None):
    """Encode UnixFS Data protobuf message."""
    buf = _encode_varint_field(1, type_val)
    if filesize is not None:
        buf += _encode_varint_field(3, filesize)
    if blocksizes:
        for bs in blocksizes:
            buf += _encode_varint_field(4, bs)
    return buf


def _encode_pb_link(cid_bytes, tsize, name=""):
    """Encode a dag-pb PBLink protobuf message.

    Kubo always serializes the Name field (even as empty string for file links).
    """
    buf = _encode_bytes_field(1, cid_bytes)
    buf += _encode_bytes_field(2, name.encode("utf-8"))
    buf += _encode_varint_field(3, tsize)
    return buf


def _encode_pb_node(links_bytes, unixfs_data):
    """Encode a dag-pb PBNode (Links before Data per spec)."""
    buf = b""
    for link in links_bytes:
        buf += _encode_bytes_field(2, link)
    buf += _encode_bytes_field(1, unixfs_data)
    return buf


def _build_balanced_dag(leaves):
    """Build balanced DAG from leaf tuples, return (cid_bytes, tsize, data_size)."""
    while len(leaves) > 1:
        next_level = []
        for i in range(0, len(leaves), MAX_LINKS):
            batch = leaves[i : i + MAX_LINKS]
            data_size = sum(leaf[2] for leaf in batch)
            blocksizes = [leaf[2] for leaf in batch]
            unixfs = _encode_unixfs_data(UNIXFS_FILE, filesize=data_size, blocksizes=blocksizes)
            links = [_encode_pb_link(leaf[0], leaf[1]) for leaf in batch]
            node_bytes = _encode_pb_node(links, unixfs)
            cid = _cid_bytes(CODEC_DAG_PB, node_bytes)
            tsize = len(node_bytes) + sum(leaf[1] for leaf in batch)
            next_level.append((cid, tsize, data_size))
        leaves = next_level
    return leaves[0]


def _process_file(fp):
    """Process file into CID, returning (cid_bytes, tsize, data_size)."""
    fp = Path(fp)
    leaves = []
    with open(fp, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            cid = _cid_bytes(CODEC_RAW, chunk)
            leaves.append((cid, len(chunk), len(chunk)))

    if not leaves:
        # Empty file: single empty raw leaf
        cid = _cid_bytes(CODEC_RAW, b"")
        return cid, 0, 0

    if len(leaves) == 1:
        return leaves[0]

    return _build_balanced_dag(leaves)


def ipfs_cidv1(fp, wrap=False):
    # type: (str|Path, bool) -> str
    """Compute IPFS CIDv1 for file (Kubo-compatible, pure Python).

    :param fp: Filepath to hash.
    :param wrap: Wrap file in a directory and append filename to CID path.
    :return: IPFS CIDv1 base32lower string.
    """
    fp = Path(fp)
    file_cid, file_tsize, _ = _process_file(fp)

    if not wrap:
        return _cid_base32(file_cid)

    # Directory wrapping: create dag-pb directory node with one named link
    unixfs = _encode_unixfs_data(UNIXFS_DIRECTORY)
    link = _encode_pb_link(file_cid, file_tsize, name=fp.name)
    dir_node = _encode_pb_node([link], unixfs)
    dir_cid = _cid_bytes(CODEC_DAG_PB, dir_node)
    return _cid_base32(dir_cid) + f"/{fp.name}"


def ipfs_cidv1_base16(fp):
    # type: (str|Path) -> str
    """Compute IPFS CIDv1 with base16 encoding (Kubo-compatible, pure Python).

    :param fp: Filepath to hash.
    :return: IPFS CIDv1 base16 (hex) string.
    """
    file_cid, _, _ = _process_file(fp)
    return _cid_base16(file_cid)
