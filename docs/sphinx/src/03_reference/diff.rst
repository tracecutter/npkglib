diff
====================

Structured diff detection and rendering utilities.

This module provides utilities for detecting and rendering differences between structured or textual inputs.

Diff detectors produce a ``Delta`` (a sequence of ``Row`` objects) describing changes. Renderers consume these rows and present them in human-readable formats such as side-by-side (2up) or line-based views.

Typical usage:

::

   delta = diff.text(before, after)
   diff.render(delta)

This module is commonly used to support ``--dry-run`` style workflows where proposed changes are displayed before being applied.
