table
====================

Lightweight tabular rendering with deterministic layout.

This module provides utilities for rendering tabular data in a consistent, terminal-friendly format.

Data producers supply rows as dictionaries. The Table class handles:

- column inference and ordering
- width calculation
- padding and alignment
- truncation

Typical usage:

::

   rows = [
       {"name": "alice", "count": 3},
       {"name": "bob", "count": 42},
   ]

   print(Table(rows=rows))

Optional explicit column ordering:

::

   Table(rows=rows, columns=["name", "count"])

- last column is truncated to respect terminal width
- values are stringified without styling
- formatting is stable and diff-friendly

Formatting concerns are intentionally separate from styling (see ``npkglib.style``).
