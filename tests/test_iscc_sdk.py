import pkgutil
from importlib import import_module

import iscc_sdk
from iscc_sdk import __version__


def test_version():
    assert __version__ == "0.9.7"


def test_star_import_skips_submodule_names():
    """`from iscc_sdk import *` (exports `__all__`) must not rebind names like `c2pa`."""
    assert "c2pa" not in iscc_sdk.__all__
    assert "image" not in iscc_sdk.__all__
    assert "os" not in iscc_sdk.__all__
    assert callable(iscc_sdk.thumbnail)


def test_star_import_exports_submodule_api():
    """Every name in the `__all__` of a submodule is exported by `from iscc_sdk import *`."""
    modules = [import_module(f"iscc_sdk.{m.name}") for m in pkgutil.iter_modules(iscc_sdk.__path__)]
    exported = [name for module in modules for name in getattr(module, "__all__", [])]
    assert exported
    assert sorted(exported) == sorted(iscc_sdk.__all__)
    assert all(hasattr(iscc_sdk, name) for name in iscc_sdk.__all__)
