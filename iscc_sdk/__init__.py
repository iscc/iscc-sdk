"""ISCC - Software Development Kit."""

import os
import sys
from importlib import metadata
from platformdirs import PlatformDirs


__version__ = metadata.version("iscc-sdk")
APP_NAME = "iscc-sdk"
APP_AUTHOR = "iscc"
dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)
os.environ["LOGURU_AUTOINIT"] = "False"

import pillow_avif

# Import full api to toplevel
from iscc_sdk.monkeys import *
from iscc_sdk.compat import *
from iscc_sdk.options import *
from iscc_sdk.tools import *
from iscc_sdk.mediatype import *
from iscc_sdk.container import *
from iscc_sdk.image import *
from iscc_sdk.svg import *
from iscc_sdk.main import *
from iscc_sdk.text import *
from iscc_sdk.ipfs import *
from iscc_sdk.audio import *
from iscc_sdk.video import *
from iscc_sdk.mp7 import *
from iscc_sdk.exceptions import *
from iscc_sdk.metadata import *
from iscc_sdk.pdf import *
from iscc_sdk.epub import *
from iscc_sdk.docx_ import *
from iscc_sdk.thumbnail import *
from iscc_sdk.utils import *
from iscc_sdk.c2pa import *


# Star imports export the public API of the submodules, but not the submodule names themselves
# (`from iscc_sdk import *` must not rebind `c2pa` of the c2pa-python SDK, for example).
__all__ = [
    name
    for module in (
        "compat",
        "options",
        "tools",
        "mediatype",
        "container",
        "image",
        "svg",
        "main",
        "text",
        "ipfs",
        "audio",
        "video",
        "mp7",
        "exceptions",
        "metadata",
        "pdf",
        "epub",
        "docx_",
        "thumbnail",
        "utils",
        "c2pa",
    )
    for name in sys.modules[f"iscc_sdk.{module}"].__all__
]
