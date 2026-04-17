style
====================

Centralized styling and presentation helpers.

This module defines styling primitives used across pbox for consistent visual output.

It centralizes:

- ANSI color definitions
- emoji conventions
- semantic styling helpers

Typical usage:

::

   from pbox.style import style

   style.insert("added line")
   style.delete("removed line")
   style.fold()

Or for lower-level control:

::

   style.bg(style.BG_GREEN, "text")

- styling is separate from formatting (see ``pbox.fmt``)
- styling is separate from emission (see ``pbox.mark``)
- this module is intentionally opinionated
