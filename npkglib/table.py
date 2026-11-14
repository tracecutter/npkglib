"""
npkglib.table

Tabular data rendering utilities.

[[table.meta.title]]
table

[[table.meta.tagline]]
Lightweight tabular rendering with deterministic layout.

[[table.description]]
This module provides utilities for rendering tabular data in a
consistent, terminal-friendly format.

Data producers supply rows as dictionaries. The Table class handles:

- column inference and ordering
- width calculation
- padding and alignment
- truncation

[[table.design]]
Design principles:

- no domain knowledge
- deterministic layout
- minimal configuration
- terminal-width awareness

This module focuses purely on presentation. It does not interpret or
transform data beyond string conversion.

[[table.usage]]
Typical usage:

    rows = [
        {"name": "alice", "count": 3},
        {"name": "bob", "count": 42},
    ]

    print(Table(rows=rows))

Optional explicit column ordering:

    Table(rows=rows, columns=["name", "count"])

[[table.notes]]
- last column is truncated to respect terminal width
- values are stringified without styling
- formatting is stable and diff-friendly

Formatting concerns are intentionally separate from styling
(see ``npkglib.style``).

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence

from npkglib.tty import stdout_width


_WS_RE = re.compile(r"\s+")


# -------------------------------------------------------------------
# Data model
# -------------------------------------------------------------------


class Table:
    def __init__(self, *, rows: list[dict[str, object]], columns: Sequence[str] | None = None):
        self.rows = rows
        self.columns = list(columns) if columns else self._infer_columns()

    def _infer_columns(self) -> list[str]:
        if not self.rows:
            return []
        return list(self.rows[0].keys())

    @property
    def empty(self) -> bool:
        return not self.rows

    # ---------------------------------------------------------------
    # Developer view
    # ---------------------------------------------------------------

    def __repr__(self) -> str:
        return f"Table(rows={len(self.rows)}, columns={self.columns})"

    # ---------------------------------------------------------------
    # Human rendering
    # ---------------------------------------------------------------

    def __str__(self) -> str:
        if self.empty:
            return ""

        rows = self._stringify_rows()
        widths = self._column_widths(rows)

        # Respect terminal width (truncate only last column)
        term_width = stdout_width()
        fixed = sum(widths[c] + 2 for c in self.columns[:-1])
        last = self.columns[-1]

        if fixed + widths[last] > term_width:
            widths[last] = max(8, term_width - fixed)

        lines: list[str] = []

        # Header
        header = self._format_row(
            {c: c for c in self.columns},
            widths,
        )
        lines.append(header)
        lines.append("-" * len(header))

        # Rows
        for row in rows:
            lines.append(self._format_row(row, widths))

        return "\n".join(lines)

    # ---------------------------------------------------------------
    # Internals
    # ---------------------------------------------------------------

    def _stringify_rows(self) -> list[dict[str, str]]:
        cooked: list[dict[str, str]] = []

        for row in self.rows:
            out: dict[str, str] = {}
            for col in self.columns:
                value = row.get(col, "")
                out[col] = self._stringify(value)
            cooked.append(out)

        return cooked

    @staticmethod
    def _stringify(value: object) -> str:
        if value is None:
            return ""
        return str(value)

    def _column_widths(self, rows: Iterable[dict[str, str]]) -> dict[str, int]:
        widths = {c: len(c) for c in self.columns}

        for row in rows:
            for col in self.columns:
                widths[col] = max(widths[col], len(row.get(col, "")))

        return widths

    def _format_row(self, row: dict[str, str], widths: dict[str, int]) -> str:
        cells = []
        for col in self.columns:
            val = row.get(col, "")
            val = _truncate(val, widths[col])
            cells.append(val.ljust(widths[col]))
        return "  ".join(cells)


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------


def _truncate(s: str, width: int) -> str:
    if len(s) <= width:
        return s
    if width <= 3:
        return s[:width]
    return s[: width - 3] + "..."
