"""ISCC - Software Development Kit."""
import os
from platformdirs import PlatformDirs

__version__ = "0.2.0"
APP_NAME = "iscc-sdk"
APP_AUTHOR = "iscc"
dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)


# Import full api to toplevel
from iscc_sdk.options import *
from iscc_sdk.tools import *
from iscc_sdk.mediatype import *
from iscc_sdk.image import *
from iscc_sdk.main import *
from iscc_sdk.models import *
from iscc_sdk.text import *
from iscc_sdk.ipfs import *
