"""
npkglib.api

Declarative public API support for npkglib.

[[api.meta.title]]
api

[[api.meta.tagline]]
Decorator-based declaration of public API entities.

[[api.description]]
This module provides the public ``api`` decorator used to mark
functions, classes, and other objects as part of the supported
public surface of npkglib.

The decorator is backed by the lightweight registry implemented in
``npkglib._api``. It allows public interface declarations to remain
close to the code they describe while staying dependency-light and
safe to import broadly.

[[api.usage]]
Typical usage:

    from npkglib import api

    @api()
    def my_function():
        ...

Optional metadata may be attached to help organize or describe API
entities for downstream tooling:

    @api(group="diff")
    def render_diff(...):
        ...

[[api.notes]]
This module is the public facade for API declaration.

Implementation details of registration and low-level registry
management live in ``npkglib._api``.

Documentation tooling such as psym may later consume this registry
to derive structured documentation symbols from declared API
entities.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

from npkglib._api import api

__all__ = ["api"]
