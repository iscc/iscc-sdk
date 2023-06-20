import shutil
import tempfile
from pathlib import Path


__all__ = [
    "TempFile",
]


class TempFile:
    def __init__(self, original_path):
        # type: (str|Path) -> None
        self.original_path = Path(original_path)
        self.temp_dir = None

    def __enter__(self):
        # type: () -> Path
        self.temp_dir = Path(tempfile.mkdtemp())
        temp_filename = self.temp_dir / self.original_path.name
        shutil.copy2(self.original_path, temp_filename)
        return temp_filename

    def __exit__(self, exc_type, exc_value, traceback):
        shutil.rmtree(self.temp_dir)
