style
====================

Centralized styling and presentation helpers.

This module defines styling primitives used across npkglib for consistent visual output.

It centralizes:

- ANSI color definitions
- emoji conventions
- semantic styling helpers

Typical usage:

::

   from npkglib.style import style

   style.insert("added line")
   style.delete("removed line")
   style.fold()

Or for lower-level control:

::

   style.bg(style.BG_GREEN, "text")

- styling is separate from formatting (see ``npkglib.fmt``)
- styling is separate from emission (see ``npkglib.mark``)
- this module is intentionally opinionated
