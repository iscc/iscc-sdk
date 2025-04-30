import time
import shutil
import tempfile
from functools import cache
from pathlib import Path
from loguru import logger as log


__all__ = [
    "TempFile",
    "timer",
    "is_installed",
]


class TempFile:
    def __init__(self, original_path):
        # type: (str|Path) -> None
        self.original_path = Path(original_path)
        self.temp_dir: Path | None = None

    def __enter__(self):
        # type: () -> Path
        self.temp_dir = Path(tempfile.mkdtemp())
        temp_filename = self.temp_dir / self.original_path.name
        shutil.copy2(self.original_path, temp_filename)
        return temp_filename

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.temp_dir)


class timer:
    def __init__(self, message: str):
        self.message = message

    def __enter__(self):
        # Record the start time
        self.start_time = time.perf_counter()

    def __exit__(self, exc_type, exc_value, traceback):
        # Calculate the elapsed time
        elapsed_time = time.perf_counter() - self.start_time
        # Log the message with the elapsed time
        log.debug(f"{self.message} {elapsed_time:.4f} seconds")


@cache
def is_installed(package_name):
    # type: (str) -> bool
    """
    Check if a Python package is installed.

    :param str package_name: The name of the package to check
    :return: True if the package is installed, False otherwise
    :rtype: bool
    """
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False
