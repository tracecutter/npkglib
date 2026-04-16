"""
pbox.fmt

Formatting primitives.

[[fmt.meta.title]]
fmt

[[fmt.meta.tagline]]
Deterministic formatting utilities for presentation-ready values.

[[fmt.description]]
This module provides pure formatting functions for converting values
into stable, presentation-ready string representations.

The functions are designed to produce deterministic output suitable for:

- logging
- diffing
- tabular display
- CLI output

[[fmt.design]]
Design principles:

- no side effects
- no styling (no ANSI, no emoji)
- fixed-width where appropriate
- stable output for diff/grep workflows

Formatting is intentionally opinionated to reduce variability across tools.

[[fmt.usage]]
Typical usage:

    from pbox import fmt

    fmt.duration(1.234)
    fmt.number(0.5)
    fmt.field("percent", 0.42)

[[fmt.notes]]
This module focuses purely on value formatting. Styling concerns
(color, emphasis, layout) are handled separately by ``pbox.style``.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

Scalar = str | int | float | bool

# ---------------------------------------------------------------------------
# Duration formatting
# ---------------------------------------------------------------------------


def duration(seconds: float) -> str:
    """
    Format duration using fixed-width engineering notation.

    Format:
        DD.DDD<unit>

    Units auto-scale across:
        ns, µs, ms, s, m, h

    Guarantees:
        - 2 digits left of decimal (zero padded)
        - 3 digits right of decimal
        - stable width for alignment

    Examples:
        0.000123  -> 00.123ms
        0.005     -> 05.000ms
        1.234     -> 01.234s
        12.345    -> 12.345s
        65        -> 01.083m
    """
    units = (
        (3600.0, "h"),
        (60.0, "m"),
        (1.0, "s"),
        (1e-3, "ms"),
        (1e-6, "µs"),
        (1e-9, "ns"),
    )

    # ---- pass 1: prefer human-scale (>=1)
    for scale, suffix in units:
        value = seconds / scale
        if 1 <= value < 100:
            return f"{value:06.3f}{suffix}"

    # ---- pass 2: fallback (small values)
    for scale, suffix in reversed(units):
        value = seconds / scale
        if value < 100:
            return f"{value:06.3f}{suffix}"

    # ---- extreme fallback
    value = seconds / 3600.0
    return f"{value:06.3f}h"


# ---------------------------------------------------------------------------
# Generic fixed-width number
# ---------------------------------------------------------------------------


def number(value: float) -> str:
    """
    Fixed-width numeric formatter.

    Format:
        DD.DDD

    Useful for:
        - metrics
        - ratios
        - normalized values

    Examples:
        0.5     -> 00.500
        1.234   -> 01.234
        12.3    -> 12.300
    """

    return f"{value:06.3f}"


# ---------------------------------------------------------------------------
# Optional: integer width helper (lightweight, may grow later)
# ---------------------------------------------------------------------------


def integer(value: int, width: int = 2) -> str:
    """
    Zero-padded integer.

    Examples:
        integer(5)       -> "05"
        integer(42)      -> "42"
        integer(7, 3)    -> "007"
    """

    return f"{value:0{width}d}"


# ---------------------------------------------------------------------------
# Field formatting
# ---------------------------------------------------------------------------


def field(t: str, v: Scalar) -> str:
    if t == "duration":
        return duration(float(v))
    elif t == "count":
        return integer(int(v))
    elif t == "number":
        return number(float(v))
    elif t == "percent":
        return f"{number(float(v))}%"
    elif t == "bool":
        return "true" if v else "false"
    elif t == "iso_time":
        return str(v)  # stub for now
    elif t == "string":
        return v if isinstance(v, str) else str(v)

    # unknown type → graceful fallback
    return str(v)
