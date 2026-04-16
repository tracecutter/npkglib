"""
pkit

Curated utility toolbox for npkg-based projects.

[[meta.title]]
pkit

[[meta.tagline]]
A reusable Python utility library with a declarative public API.

[[meta.brief]]
pkit provides a collection of small, composable utilities and
subsystems used across npkg-based projects. It establishes a
shared vocabulary (diff, mark, style, signal, etc.) and a
consistent API declaration mechanism.

[[meta.author]]
John Fogelin

[[meta.copyright]]
Copyright (c) 2026 John Fogelin. All rights reserved.

[[meta.license]]
PROPRIETARY. See LICENSE for details.

[[section.overview]]
pkit is the foundational toolbox for the npkg ecosystem.

It is designed to be:

\b
- dependency-light
- broadly reusable
- opinionated in defaults
- safe to import in any context

Projects built with npkg typically depend on pkit for shared
functionality rather than re-implementing common patterns.

[[section.design]]
pkit favors strong defaults and composability over configuration.

\b
- behavior is provided directly, not configured indirectly
- shared conventions reduce duplication across projects
- divergence is handled via pfork rather than runtime switches

[[section.api.intro]]
Public API elements in pkit are declared using the api decorator:

    from pkit import api

    @api()
    def my_function():
        ...

This keeps API definition close to implementation while enabling
introspection and documentation tooling.

[[section.api.subsystem]]
The API subsystem provides:

\b
- declaration of public API entities via @api(...)
- a registry of decorated objects and metadata
- export of API entities onto the package namespace
- maintenance of __all__

[[section.api.future]]
The API registry is intended to serve as an input layer for
documentation systems such as psym.

In that model, API-decorated objects may be translated into
structured documentation symbols describing:

\b
- entity kind
- defining module
- grouping metadata
- summary text

[[section.status]]
- Python 3.11+
- Library (no CLI entrypoint)
- Proprietary license

[[section.links]]
- Docs: https://tracecutter.github.io/pkit/
- GitHub: https://github.com/tracecutter/pkit
- Author: https://github.com/tracecutter

INTERNAL

This module serves as the root symbol surface for pkit and is
processed by documentation tooling to extract package metadata and
curated public API structure.

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from importlib.metadata import PackageNotFoundError, version

from ._api import api
from . import diff, fmt, guppy, mark, result, signal, style, table, tty

try:
    __version__ = version("pkit")
except PackageNotFoundError:
    __version__ = "x.y.z"

__all__ = [
    "api",
    "diff",
    "fmt",
    "guppy",
    "mark",
    "result",
    "signal",
    "style",
    "table",
    "tty",
]
