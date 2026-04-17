mark
====================

Context-aware message emission for CLI-style output.

This module provides helpers for emitting user-facing messages with consistent formatting and behavior across pbox-based tools.

It interprets presentation context (quiet, verbose, emoji) to decide when and how messages are emitted.

Typical usage:

::

   import pbox.mark as mark

   mark.configure(mark.MarkContext(verbose=True))

   mark.section("Starting")
   mark.info("Processing file")
   mark.warn("Minor issue detected")
   mark.error("Something failed")

- wrapping respects terminal width
- indentation from caller is preserved
- multi-line messages are not re-wrapped
- section output is never wrapped

Formatting is intentionally simple and stable.
