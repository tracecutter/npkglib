"""
pbox.exceptions

Core exception types for pbox.

[[exceptions.meta.title]]
exceptions

[[exceptions.meta.tagline]]
Base exception hierarchy for pbox.

[[exceptions.description]]
This module defines the base exception type used across pbox.

All domain-specific errors should derive from ``PboxError`` to allow
callers to catch pbox-specific failures without masking unrelated
exceptions.

[[exceptions.usage]]
Typical usage:

    from pbox.exceptions import PboxError

    try:
        ...
    except PboxError:
        ...

[[exceptions.notes]]
Keep the exception hierarchy intentionally shallow. Prefer a single
base type unless specific error categories provide clear value.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""


class PboxError(Exception):
    """Base class for all pbox errors."""

    pass
