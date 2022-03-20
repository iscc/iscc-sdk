"""*Video handling module*"""
import subprocess
import sys
import tempfile
from os.path import join, basename
import iscc_sdk as idk
import iscc_schema as iss


__all__ = [
    "video_meta_extract",
    "video_meta_embed",
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
                mapped[mapped_field] = value
    return mapped


def video_meta_embed(fp, meta):
    # type: (str, iss.IsccMeta) -> str
    """
    Embed metadata into video.

    Supported fields: name, description, meta, creator, license, aquire

    :param str fp: Filepath to video file
    :param IsccMeta meta: Metadata to embed into image
    :return: Filepath to video file with updated metadata
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

    # TODO Escape metadata:
    # Metadata keys or values containing special characters (‘=’, ‘;’, ‘#’, ‘\’ and a newline)
    # must be escaped with a backslash ‘\’.

    # Prepare metadata file
    cmdf = ";FFMETADATA1\n"
    for field in write_map.keys():
        value = getattr(meta, field)
        if value:
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
