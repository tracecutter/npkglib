tty
====================

Terminal-aware utilities for width and capability detection.

This module provides minimal helpers for interacting with the terminal environment, primarily for layout-sensitive rendering.

Currently it exposes terminal width detection with safe fallbacks.

Typical usage:

::

   from pbox.tty import stdout_width

   width = stdout_width()

Used by rendering modules such as:

- pbox.table
- pbox.diff
- pbox.mark

- non-TTY environments return an effectively unbounded width
- fallback values ensure predictable formatting
- avoids raising exceptions during rendering
