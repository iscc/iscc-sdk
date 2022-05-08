"""Installer script for binary dependencies"""
import sys
from loguru import logger as log
from . import tools


def main():
    log.add(sys.stdout)
    tools.install()
    log.info(f"IPFS Version: {tools.ipfs_version_info()}")
    log.info(f"Exiv2 Version: {tools.exiv2_version_info()}")
    log.info(f"FPCALC Version: {tools.fpcalc_version_info()}")
    log.info(f"FFMPEG Version: {tools.ffmpeg_version_info()}")
    log.info(f"JAVA Version: {tools.java_version_info()}")
    log.info(f"TIKA Version: {tools.tika_version_info()}")

    sys.exit(0)


if __name__ == "__main__":
    main()
