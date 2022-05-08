"""Installer script for binary dependencies"""
import sys
from loguru import logger as log
from . import tools


def main():
    log.add(sys.stdout)

    tools.ipfs_install()
    log.info(f"IPFS Version: {tools.ipfs_version_info()}")

    tools.exiv2_install()
    log.info(f"Exiv2 Version: {tools.exiv2_version_info()}")

    tools.fpcalc_install()
    log.info(f"FPCALC Version: {tools.fpcalc_version_info()}")

    tools.ffprobe_install()
    log.info(f"FFPROBE Version: {tools.ffprobe_version_info()}")

    tools.ffmpeg_install()
    log.info(f"FFMPEG Version: {tools.ffmpeg_version_info()}")

    tools.java_install()
    log.info(f"JAVA Version: {tools.java_version_info()}")

    tools.tika_install()
    log.info(f"TIKA Version: {tools.tika_version_info()}")

    sys.exit(0)


if __name__ == "__main__":
    main()
