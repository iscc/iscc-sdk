import pkgutil
from importlib import import_module

import iscc_sdk
from iscc_sdk import __version__


def test_version():
    assert __version__ == "0.9.7"


def test_star_import_skips_submodule_names():
    """`from iscc_sdk import *` must not rebind names like `c2pa` (the c2pa-python SDK)."""
    namespace = {}
    exec("from iscc_sdk import *", namespace)  # noqa: S102 - a star import needs module scope
    assert "c2pa" not in namespace
    assert "image" not in namespace
    assert "os" not in namespace
    assert callable(namespace["thumbnail"])


def test_star_import_exports_submodule_api():
    """Every name in the `__all__` of a submodule is exported by `from iscc_sdk import *`."""
    namespace = {}
    exec("from iscc_sdk import *", namespace)  # noqa: S102 - a star import needs module scope
    modules = [import_module(f"iscc_sdk.{m.name}") for m in pkgutil.iter_modules(iscc_sdk.__path__)]
    exported = [name for module in modules for name in getattr(module, "__all__", [])]
    assert exported
    assert set(exported) <= set(namespace)
    assert sorted(exported) == sorted(iscc_sdk.__all__)
