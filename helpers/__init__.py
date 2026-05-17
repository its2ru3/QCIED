"""Helpers package.

Automatically import all helper submodules when the package is imported.
"""

import importlib
import pkgutil

__all__ = []

for finder, name, ispkg in pkgutil.iter_modules(__path__):
    if name == "__init__":
        continue

    module = importlib.import_module(f".{name}", __name__)
    __all__.append(name)
    globals()[name] = module
