"""*Video handling module*"""
import os
from typing import Sequence, Tuple, List

from loguru import logger as log
import io
import subprocess
import sys
import tempfile
from os.path import join, basename
from pathlib import Path
from secrets import token_hex
from PIL import Image, ImageEnhance
import iscc_sdk as idk
import iscc_schema as iss


__all__ = [
    "video_meta_extract",
    "video_meta_embed",
    "video_thumbnail",
    "video_mp7sig_extract",
    "video_features_extract",
]

VIDEO_META_MAP = {
    "iscc_name": "name",
    "iscc_description": "description",
    "iscc_meta": "meta",
    "title": "name",
    "track": "name",
    "show": "name",
    "album": "name",
    "description": "description",
    "synopsis": "description",
    "comment": "description",
    "author": "creator",
    "composer": "creator",
    "artist": "creator",
    "album_artist": "creator",
    "copyright": "rights",
    "license": "license",
    "acquire": "acquire",
}


def video_meta_extract(fp):
    # type: (str) -> dict
    """
    Extract metadata from video.

    :param str fp: Filepath to video file
    :return: Metdata mpped to IsccMeta schema
    :rtype: dict
    """

    cmd = [idk.ffmpeg_bin(), "-i", fp, "-movflags", "use_metadata_tags", "-f", "ffmetadata", "-"]

    result = subprocess.run(cmd, capture_output=True, check=True)
    text = result.stdout.decode(sys.stdout.encoding, errors="ignore")

    mapped = dict()
    for line in text.splitlines(keepends=False):
        if not line.startswith(";FFMETA"):
            key, value = line.split("=", 1)
            mapped_field = VIDEO_META_MAP.get(key.lower())
            if mapped_field:
                mapped[mapped_field] = (
                    value.replace(r"\=", "=")
                    .replace(r"\;", ";")
                    .replace(r"\#", "#")
                    .replace(r"\;", ";")
                    .replace(r"\\n", "\n")
                    .replace(r"\\", "\\")
                )
    return mapped


def video_meta_embed(fp, meta):
    # type: (str, iss.IsccMeta) -> str
    """
    Embed metadata into a copy of the video file.

    Supported fields: name, description, meta, creator, license, aquire

    :param str fp: Filepath to source video file
    :param IsccMeta meta: Metadata to embed into video
    :return: Filepath to new video file with updated metadata
    :rtype: str
    """

    write_map = {
        "name": "iscc_name",
        "description": "iscc_description",
        "meta": "iscc_meta",
        "creator": "author",
        "rights": "copyright",
        "license": "license",
        "acquire": "acquire",
    }

    # Metadata keys or values containing special characters (‘=’, ‘;’, ‘#’, ‘\’ and a newline)
    # must be escaped with a backslash ‘\’.
    escape = str.maketrans(
        {
            "=": r"\=",
            ";": r"\;",
            "#": r"\#",
            "\\": r"\\",
            "\n": r"\\n",
        }
    )

    # Prepare metadata file
    cmdf = ";FFMETADATA1\n"
    for field in write_map.keys():
        value = getattr(meta, field)
        if value:
            value = value.translate(escape)
            cmdf += f"{write_map[field]}={value}\n"

    # Create temp filepaths
    tempdir = tempfile.mkdtemp()
    metafile = join(tempdir, "meta.txt")
    videofile = join(tempdir, basename(fp))

    # Store metadata
    with open(metafile, "wt", encoding="utf-8") as outf:
        outf.write(cmdf)

    # Embed metadata
    # See: http://ffmpeg.org/ffmpeg-formats.html#Metadata-1
    cmd = [
        idk.ffmpeg_bin(),
        "-i",
        fp,
        "-i",
        metafile,
        "-movflags",
        "use_metadata_tags",
        "-map_metadata",
        "1",
        "-codec",
        "copy",
        videofile,
    ]
    subprocess.run(cmd, capture_output=True, check=True)
    return videofile


def video_thumbnail(fp):
    # type: (str) -> Image.Image
    """
    Create a thumbnail for a video.

    :param str fp: Filepath to video file.
    :return: Raw PNG byte data
    :rtype: bytes
    """
    size = idk.sdk_opts.image_thumbnail_size

    cmd = [
        idk.ffmpeg_bin(),
        "-i",
        fp,
        "-vf",
        f"thumbnail,scale={size}:-1",
        "-frames:v",
        "1",
        "-c:v",
        "png",
        "-f",
        "image2pipe",
        "-",
    ]

    result = subprocess.run(cmd, capture_output=True)
    img_obj = Image.open(io.BytesIO(result.stdout))
    return ImageEnhance.Sharpness(img_obj.convert("RGB")).enhance(1.4)


def video_features_extract(fp):
    # type: (str) -> List[Tuple[int, ...]]
    """
    Extract video features.

    :param str fp: Filepath to video file.
    :return: A sequence of frame signatures.
    :rtype: Sequence[Tuple[int, ...]]
    """
    sig = video_mp7sig_extract(fp)
    frames = idk.read_mp7_signature(sig)
    return [tuple(frame.vector.tolist()) for frame in frames]


def video_mp7sig_extract(fp):
    # type: (str) -> bytes
    """Extract MPEG-7 Video Signature.

    :param str fp: Filepath to video file.
    :return: raw signature data
    :rtype: bytes
    """

    sigfile_path = Path(tempfile.mkdtemp(), token_hex(16) + ".bin")
    sigfile_path_escaped = sigfile_path.as_posix().replace(":", "\\\\:")

    # Extract MP7 Signature
    vf = f"signature=format=binary:filename={sigfile_path_escaped}"
    vf = f"fps=fps={idk.sdk_opts.video_fps}," + vf
    cmd = [idk.ffmpeg_bin()]
    cmd.extend(["-i", fp, "-vf", vf, "-f", "null", "-"])
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    with open(sigfile_path, "rb") as sig:
        sigdata = sig.read()
    os.remove(sigfile_path)
    return sigdata