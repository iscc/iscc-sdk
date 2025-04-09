"""Installer script for binary dependencies"""

import sys
from loguru import logger as log
import iscc_sdk as idk


def main():
    log.add(sys.stdout)
    log.info(f"Installing tools to {idk.dirs.user_data_dir}")
    idk.tools.install()
    log.info(f"IPFS Version: {idk.tools.ipfs_version_info()}")
    log.info(f"FPCALC Version: {idk.tools.fpcalc_version_info()}")
    log.info(f"FFMPEG Version: {idk.tools.ffmpeg_version_info()}")

    sys.exit(0)


if __name__ == "__main__":
    main()
