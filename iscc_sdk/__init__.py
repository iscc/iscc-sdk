import os
from platformdirs import PlatformDirs

__version__ = "0.1.0"
APP_NAME = "iscc-sdk"
APP_AUTHOR = "iscc"
dirs = PlatformDirs(appname=APP_NAME, appauthor=APP_AUTHOR)
os.makedirs(dirs.user_data_dir, exist_ok=True)

# Import full api to toplevel
from iscc_sdk.mime import *
