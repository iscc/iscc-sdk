"""*Audio handdling module*."""
from loguru import logger as log
import json
import iscc_sdk as idk
import subprocess
import taglib


__all__ = [
    "audio_meta_embed",
    "audio_meta_extract",
    "audio_features_extract",
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


def audio_meta_extract(fp):
    # type: (str) -> dict
    """
    Extract metadata from audio file.

    :param str fp: Filepath to audio file.
    :return: Metadata mapped to IsccMeta schema
    :rtype: dict
    """
    obj = taglib.File(fp)
    meta = dict(obj.tags)
    mapped = dict()
    done = set()
    for tag, mapped_field in AUDIO_META_MAP.items():
        if mapped_field in done:
            continue
        value = meta.get(tag)
        if value:
            log.debug(f"Mapping metadata: {tag} -> {mapped_field} -> {value[0]}")
            mapped[mapped_field] = value[0]
            done.add(mapped_field)
    mapped["duration"] = obj.length
    # Todo - add bitrate, channels, samplerate to iscc-schema
    # mapped["bitrate"] = obj.bitrate
    # mapped["channels"] = obj.channels
    # mapped["samplerate"] = obj.sampleRate
    obj.close()
    return mapped


def audio_meta_embed(fp, meta):
    # type: (str, idk.IsccMeta) -> None
    """
    Embed metadata into audio.

    :param str fp: Filepath to audio file
    :param IsccMeta meta: Metadata to embed into audio file
    :return: None
    """
    obj = taglib.File(fp)
    if meta.name:
        obj.tags["ISCC:TITLE"] = [meta.name]
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


def audio_features_extract(fp):
    # type: (str) -> dict
    """
    Exctracts chromprint fingerprint.

    :param str fp: Filepath
    :return: A dict with `duration` in seconds and `fingerprint` 32-bit integers
    :rtype: dict
    """
    cmd = [idk.fpcalc_bin(), "-raw", "-json", "-signed", "-length", "0", fp]
    proc = subprocess.run(cmd, capture_output=True, check=True)
    result = json.loads(proc.stdout)
    return result
