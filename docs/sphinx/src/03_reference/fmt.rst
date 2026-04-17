fmt
====================

Deterministic formatting utilities for presentation-ready values.

This module provides pure formatting functions for converting values into stable, presentation-ready string representations.

The functions are designed to produce deterministic output suitable for:

- logging
- diffing
- tabular display
- CLI output

Typical usage:

::

   from pbox import fmt

   fmt.duration(1.234)
   fmt.number(0.5)
   fmt.field("percent", 0.42)

This module focuses purely on value formatting. Styling concerns (color, emphasis, layout) are handled separately by ``pbox.style``.
