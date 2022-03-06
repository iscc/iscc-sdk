"""Image handling module"""
import os
import sys
import json
import tempfile
import subprocess
from copy import copy
from os.path import basename
import jmespath
from loguru import logger as log
import iscc_sdk as idk
from iscc_schema.schema import ISCC


__all__ = [
    "image_meta_embed",
    "image_meta_extract",
    "image_meta_delete",
]


IMAGE_META_MAP = {
    "Xmp.iscc.name": "name",
    "Xmp.iscc.description": "description",
    "Xmp.iscc.meta": "meta",
    "Xmp.dc.title": "name",
    "Xmp.xmp.Nickname": "name",
    "Xmp.xmpDM.shotName": "name",
    "Xmp.photoshop.Headline": "name",
    "Xmp.iptcExt.AOTitle": "name",
    "Iptc.Application2.Headline": "name",
    "Iptc.Application2.BylineTitle": "name",
    "Iptc.Application2.ObjectName": "name",
    "Exif.Image.XPTitle": "name",
    "Xmp.dc.description": "description",
    "Xmp.dc.creator": "creator",
    "Iptc.Application2.Byline": "creator",
    "Exif.Image.Artist": "creator",
    "Xmp.dc.identifier": "identifier",
    "Xmp.xmp.Identifier": "identifier",
    "Xmp.dc.language": "language",
    "Iptc.Application2.Language": "language",
    "Exif.Image.ImageID": "identifier",
    "Exif.Photo.ImageUniqueID": "identifier",
}


def image_meta_embed(fp, meta):
    # type: (str, ISCC) -> None
    """Embed metadata into image."""
    cmdf = "reg iscc http://purl.org/iscc/schema\n"
    cmdf += f"set Xmp.iscc.name {meta.name}\n"
    if meta.description:
        cmdf += f"set Xmp.iscc.description {meta.description}\n"
    if meta.meta:
        cmdf += f"set Xmp.iscc.meta {meta.meta}\n"

    with tempfile.NamedTemporaryFile("w+b", delete=False) as outf:
        metafilepath = copy(outf.name)
        outf.write(cmdf.encode("utf-8"))
    cmd = [idk.exiv2_bin(), "-m", metafilepath, fp]
    log.debug(f"Embedding {meta.dict(exclude_unset=True)} in {basename(fp)}")
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    os.remove(metafilepath)


def image_meta_extract(fp):
    # type: (str) -> dict
    """Extract metadata from image."""
    cmd = [idk.exiv2json_bin(), "--all", fp]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
    text = result.stdout.decode(sys.stdout.encoding)

    # We may get all sorts of crazy control-chars, delete them.
    mpa = dict.fromkeys(range(32))
    clean = text.translate(mpa)
    try:
        meta = json.loads(clean)
    except json.JSONDecodeError:  # pragma: no cover
        log.critical(f"Failed to decode exiv2 result: {clean}")
        return {}

    mapped = dict()
    done = set()
    for tag, mapped_field in IMAGE_META_MAP.items():
        if mapped_field in done:
            continue
        value = jmespath.search(tag, meta)
        if value:
            if isinstance(value, dict):
                value = jmespath.search('lang."x-default"', value)
                if not value:  # pragma: no cover
                    log.critical(f"Structured image metdata skipped: {value}")
                    continue
            log.debug(f"Mapping metadata: {tag} -> {mapped_field} -> {value}")
            mapped[mapped_field] = value
            done.add(mapped_field)

    return dict(mapped)


def image_meta_delete(fp):
    # type: (str) -> None
    """Delete all metadata from image."""
    cmd = [idk.exiv2_bin(), "rm", fp]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
