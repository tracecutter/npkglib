"""
pbox._api

Bootstrap API decorator registry.

[[_api.meta.title]]
_api

[[_api.meta.tagline]]
Minimal dependency-free API registry and decorator.

[[_api.description]]
This module provides the core ``api`` decorator used to declare public
API entities within a package.

It is intentionally designed to be dependency-free with respect to the
rest of ``pbox`` so that it can be safely imported from any module
without introducing circular dependencies.

The decorator records annotated objects in a lightweight registry and
optionally promotes them to the package namespace.

[[_api.design.constraints]]
- must remain dependency-free (standard library only)
- must not import higher-level modules (e.g. pbox.api)
- safe for broad import across package modules

[[_api.usage]]
Typical usage:

    from pbox import api

    @api(group="backend")
    class Backend:
        ...

Decorated objects are:

- recorded in the internal registry
- optionally exported onto the package namespace
- included in the package ``__all__``

[[_api.notes]]
Higher-level tooling (e.g. psym) may inspect the registry to derive
structured documentation or API references.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

import sys
import importlib
import pkgutil
from typing import Any
from collections.abc import Callable


class _API:
    """
    Registry for objects declared as part of a project's public API.
    """

    def __init__(self) -> None:
        self._registry: list[tuple[Any, dict[str, Any]]] = []

    def __call__(self, **meta) -> Callable:
        def decorator(obj: Any) -> Any:
            info = {
                "name": obj.__name__,
                "module": obj.__module__,
                "kind": "class" if isinstance(obj, type) else "function",
                **meta,
            }

            self._registry.append((obj, info))

            package = obj.__module__.split(".", 1)[0]
            pkg = sys.modules.get(package)

            if pkg is not None:
                setattr(pkg, obj.__name__, obj)

                if not hasattr(pkg, "__all__"):
                    pkg.__all__ = []  # type: ignore[attr-defined]

                all_list = pkg.__all__  # type: ignore[attr-defined]

                if obj.__name__ not in all_list:
                    all_list.append(obj.__name__)

            return obj

        return decorator

    def discover(self, package: str) -> None:
        """Import all modules in a package to trigger decorators."""
        root = importlib.import_module(package)

        if not hasattr(root, "__path__"):
            return

        for mod in pkgutil.walk_packages(root.__path__, root.__name__ + "."):
            importlib.import_module(mod.name)


api = _API()
