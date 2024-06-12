"""*Audio handling module*."""

import shutil
import tempfile
from os.path import join, basename
from typing import Optional

from PIL import Image, ImageEnhance
from loguru import logger as log
import json
import taglib
import iscc_sdk as idk


__all__ = [
    "audio_meta_embed",
    "audio_meta_extract",
    "audio_features_extract",
    "audio_thumbnail",
]


AUDIO_META_MAP = {
    "ISCC:NAME": "name",
    "ISCC:DESCRIPTION": "description",
    "ISCC:META": "meta",
    "ISCC:LICENSE": "license",
    "ISCC:ACQUIRE": "acquire",
    "TITLE": "name",
    # "ALBUM": "album",
    # "GENRE": "genre",
    "COMPOSER": "creator",
    "ORIGINALARTIST": "creator",
    "ARTIST": "creator",
    "ALBUMARTIST": "creator",
    "LICENSE": "license",
    "COPYRIGHT": "rights",
    "LANGUAGE": "language",
    "URL": "acquire",
    "ARTISTWEBPAGE": "acquire",
}


def audio_thumbnail(fp):
    # type: (str) -> Optional[Image.Image]
    """
    Create a thumbnail from embedded cover art.

    :param str fp: Filepath to audio file.
    :return: Thumbnail image as PIL Image object
    :rtype: Image.Image|None
    """
    tempdir = tempfile.mkdtemp()
    tempimg = join(tempdir, "cover.jpg")
    cmd = ["-i", fp, "-an", "-vcodec", "copy", tempimg]
    size = idk.sdk_opts.image_thumbnail_size
    try:
        idk.run_ffmpeg(cmd)
        img = Image.open(tempimg)
    except Exception:
        img = None
    if img:
        img.thumbnail((size, size), resample=idk.LANCZOS)
        img = ImageEnhance.Sharpness(img.convert("RGB")).enhance(1.4)

    shutil.rmtree(tempdir, ignore_errors=True)
    return img


def audio_meta_extract(fp):
    # type: (str) -> dict
    """
    Extract metadata from audio file.

    :param str fp: Filepath to audio file.
    :return: Metadata mapped to IsccMeta schema
    :rtype: dict
    """
    mapped = dict()
    done = set()

    try:
        obj = taglib.File(fp)
        meta = dict(obj.tags)
        mapped["duration"] = obj.length
        obj.close()
    except OSError as e:  # pragma: no cover
        # This is a workaround for the issue that taglib requires exclusive access even for reading.
        log.warning(f"Create tempfile for taglib access {basename(fp)}: {e}")
        try:
            with idk.TempFile(fp) as tmp_path:
                obj = taglib.File(tmp_path.as_posix())
                meta = dict(obj.tags)
                mapped["duration"] = obj.length
                obj.close()
        except Exception as e:
            log.warning(f"Failed metadata extraction for {basename(fp)}: {e}")
            return mapped

    for tag, mapped_field in AUDIO_META_MAP.items():
        if mapped_field in done:
            continue
        value = meta.get(tag)
        if value:
            log.debug(f"Mapping audio metadata: {tag} -> {mapped_field} -> {value[0]}")
            mapped[mapped_field] = value[0]
            done.add(mapped_field)
    # Todo - add bitrate, channels, samplerate to iscc-schema
    # mapped["bitrate"] = obj.bitrate
    # mapped["channels"] = obj.channels
    # mapped["samplerate"] = obj.sampleRate
    return mapped


def audio_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> str
    """
    Embed metadata into a copy of the audio file.

    :param str fp: Filepath to source audio file
    :param IsccMeta meta: Metadata to embed into audio file
    :return: Filepath to new audio file with updated metadata
    :rtype: str
    """
    tdir = tempfile.mkdtemp()
    tfile = shutil.copy(fp, tdir)
    obj = taglib.File(tfile)
    if meta.name:
        obj.tags["TITLE"] = [meta.name]
        obj.tags["ISCC:NAME"] = [meta.name]
    if meta.description:
        obj.tags["ISCC:DESCRIPTION"] = [meta.description]
    if meta.meta:
        obj.tags["ISCC:META"] = [meta.meta]
    if meta.license:
        obj.tags["ISCC:LICENSE"] = [meta.license]
    if meta.acquire:
        obj.tags["ISCC:ACQUIRE"] = [meta.acquire]
    obj.save()
    obj.close()
    return tfile


def audio_features_extract(fp):
    # type: (str) -> dict
    """
    Exctracts chromprint fingerprint.

    :param str fp: Filepath
    :return: A dict with `duration` in seconds and `fingerprint` 32-bit integers
    :rtype: dict
    """
    args = ["-raw", "-json", "-signed", "-length", "0", fp]
    proc = idk.run_fpcalc(args)
    result = json.loads(proc.stdout)
    return result
