"""
npkglib.api_gen

Bootstrap semantic API decorator registry.

[[api_gen.meta.title]]
api_gen

[[api_gen.meta.tagline]]
Dependency-free semantic API registry and decorator.

[[api_gen.description]]
This module provides the core ``api`` decorator used to declare
semantic API entities within a package.

Decorated objects may include:

- functions
- classes
- exceptions
- other public package entities

The module is intentionally designed to remain dependency-free with
respect to the rest of ``npkglib`` so that it may be safely imported
from any package module without introducing circular dependencies.

The decorator records annotated objects in a lightweight registry and
optionally promotes them onto the owning package namespace.

[[api_gen.design.constraints]]
- must remain dependency-free (standard library only)
- must not import higher-level modules
- safe for broad import across package modules

[[api_gen.usage]]
Typical usage:

    from npkglib.api_gen import api

    @api
    def render_diff(...):
        ...

    @api(group="backend")
    class Backend:
        ...

Decorated objects are:

- recorded in the internal registry
- optionally exported onto the package namespace
- included in the package ``__all__``

[[api_gen.notes]]
Higher-level tooling (e.g. psym) may inspect the registry to derive
structured documentation, semantic API references, or symbol tables.

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

    def __call__(self, obj: Any | None = None, **meta: Any) -> Callable:
        """
        Decorate an object as part of the public API.  Supports forms:

            @api
            def foo():
                ...

            @api(group="backend")
            def foo():
                ...
        """

        def decorator(obj: Any) -> Any:
            info = {
                "name": obj.__name__,
                "module": obj.__module__,
                "kind": "class" if isinstance(obj, type) else "function",
                **meta,
            }

            self._registry.append((obj, info))

            # Promote symbols onto the owning top-level package namespace.
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

        if obj is not None:
            return decorator(obj)

        return decorator

    def discover(self, package: str) -> None:
        """
        Import all modules in a package to trigger API decorators.

        This allows downstream tooling (e.g. psym) to discover semantic
        API declarations without requiring explicit module imports.
        """
        root = importlib.import_module(package)

        if not hasattr(root, "__path__"):
            return

        for mod in pkgutil.walk_packages(root.__path__, root.__name__ + "."):
            importlib.import_module(mod.name)


api = _API()
