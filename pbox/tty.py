"""
pbox.tty

Terminal environment helpers.

[[tty.meta.title]]
tty

[[tty.meta.tagline]]
Terminal-aware utilities for width and capability detection.

[[tty.description]]
This module provides minimal helpers for interacting with the terminal
environment, primarily for layout-sensitive rendering.

Currently it exposes terminal width detection with safe fallbacks.

[[tty.design]]
Design principles:

- minimal surface area
- no external dependencies
- safe defaults for non-interactive environments
- deterministic behavior for rendering code

[[tty.usage]]
Typical usage:

    from pbox.tty import stdout_width

    width = stdout_width()

Used by rendering modules such as:

- pbox.table
- pbox.diff
- pbox.mark

[[tty.notes]]
- non-TTY environments return an effectively unbounded width
- fallback values ensure predictable formatting
- avoids raising exceptions during rendering

INTERNAL

Return terminal width when stdout is a TTY; otherwise return unbounded width.

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

import sys
import shutil

_UNBOUNDED = 12345


def stdout_width(default: int = 120) -> int:
    if not sys.stdout.isatty():
        return _UNBOUNDED

    try:
        return shutil.get_terminal_size().columns
    except OSError:
        return default
