"""
npkglib.exceptions

Core exception types for npkglib.

[[exceptions.meta.title]]
exceptions

[[exceptions.meta.tagline]]
Base exception hierarchy for npkglib.

[[exceptions.description]]
This module defines the base exception type used across npkglib.

All domain-specific errors should derive from ``NpkglibError`` to allow
callers to catch npkglib-specific failures without masking unrelated
exceptions.

[[exceptions.usage]]
Typical usage:

    from npkglib.exceptions import NpkglibError

    try:
        ...
    except NpkglibError:
        ...

[[exceptions.notes]]
Keep the exception hierarchy intentionally shallow. Prefer a single
base type unless specific error categories provide clear value.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""


class NpkglibError(Exception):
    """Base class for all npkglib errors."""

    pass
