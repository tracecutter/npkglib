"""
npkglib

Curated utility toolbox for npkg-based projects.

[[pkg.meta.title]]
npkglib

[[pkg.meta.tagline]]
A small, composable Python utility library for reuse across npkg projects.

[[section.quickstart.install]]
Install from source (development):

    pip install -e .

Or from a package index:

    pip install npkglib

[[section.overview]]
npkglib provides a collection of small, focused utilities that form the
shared foundation of the npkg ecosystem.

It emphasizes:

- minimal dependencies
- composable building blocks
- consistent conventions across projects

Rather than re-implementing common patterns, projects depend on npkglib
to supply a stable, reusable core.

[[section.usage]]
Import and use utilities directly:

    from npkglib import diff, table, tty

Modules are designed to be independent and safe to use in isolation.

[[section.links]]
- GitHub: https://github.com/tracecutter/npkglib
- Documentation: https://tracecutter.github.io/npkglib/

INTERNAL

This module defines the public metadata surface for npkglib and is used
by documentation tooling to extract structured symbols.

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""

from importlib.metadata import PackageNotFoundError, version

from . import api_gen, diff, fmt, guppy, mark, result, signal, style, table, toml_io, tty

try:
    __version__ = version("npkglib")
except PackageNotFoundError:
    __version__ = "x.y.z"

__all__ = [
    "api_gen",
    "diff",
    "fmt",
    "guppy",
    "mark",
    "result",
    "signal",
    "style",
    "table",
    "toml_io",
    "tty",
]
