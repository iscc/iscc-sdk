"""*Container format processing module*."""

from pathlib import Path
from typing import List, Dict, Callable, Optional
import iscc_sdk as idk

__all__ = [
    "process_container",
    "register_container_processor",
]

# Registry for container processors
_CONTAINER_PROCESSORS: Dict[str, Callable] = {}


def register_container_processor(mediatype: str, processor: Callable):
    """Register a processor function for a specific container mediatype."""
    _CONTAINER_PROCESSORS[mediatype] = processor


def process_container(fp, **options):
    # type: (str|Path, Any) -> Optional[List[idk.IsccMeta]]
    """
    Process embedded elements in a container file.

    :param fp: Filepath to container file
    :param options: Processing options
    :return: List of IsccMeta objects for embedded elements or None
    """
    fp = Path(fp)
    mediatype, _ = idk.mediatype_and_mode(fp)

    processor = _CONTAINER_PROCESSORS.get(mediatype)
    if processor:
        return processor(fp, **options)
    return None
