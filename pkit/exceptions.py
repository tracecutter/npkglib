"""
pkit.exceptions

Core exception types for pkit.

[[exceptions.meta.title]]
exceptions

[[exceptions.meta.tagline]]
Base exception hierarchy for pkit.

[[exceptions.description]]
This module defines the base exception type used across pkit.

All domain-specific errors should derive from ``PkitError`` to allow
callers to catch pkit-specific failures without masking unrelated
exceptions.

[[exceptions.usage]]
Typical usage:

    from pkit.exceptions import PkitError

    try:
        ...
    except PkitError:
        ...

[[exceptions.notes]]
Keep the exception hierarchy intentionally shallow. Prefer a single
base type unless specific error categories provide clear value.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""


class PkitError(Exception):
    """Base class for all pkit errors."""

    pass
