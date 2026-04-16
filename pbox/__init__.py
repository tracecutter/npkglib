"""
pbox

Curated utility toolbox for npkg-based projects.

[[meta.title]]
pbox

[[meta.tagline]]
A small, composable Python utility library for reuse across npkg projects.

[[section.quickstart.install]]
Install from source (development):

    pip install -e .

Or from a package index:

    pip install pbox

[[section.overview]]
pbox provides a collection of small, focused utilities that form the
shared foundation of the npkg ecosystem.

It emphasizes:

- minimal dependencies
- composable building blocks
- consistent conventions across projects

Rather than re-implementing common patterns, projects depend on pbox
to supply a stable, reusable core.

[[section.usage]]
Import and use utilities directly:

    from pbox import diff, table, tty

Modules are designed to be independent and safe to use in isolation.

[[section.links]]
- GitHub: https://github.com/tracecutter/pbox
- Documentation: https://tracecutter.github.io/pbox/

INTERNAL

This module defines the public metadata surface for pbox and is used
by documentation tooling to extract structured symbols.

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from importlib.metadata import PackageNotFoundError, version

from ._api import api
from . import diff, fmt, guppy, mark, result, signal, style, table, tty

try:
    __version__ = version("pbox")
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
