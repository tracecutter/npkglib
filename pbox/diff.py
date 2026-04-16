"""
pbox.diff

Diff / delta detection and rendering utilities.

[[diff.meta.title]]
diff

[[diff.meta.tagline]]
Structured diff detection and rendering utilities.

[[diff.description]]
This module provides utilities for detecting and rendering differences
between structured or textual inputs.

Diff detectors produce a ``Delta`` (a sequence of ``Row`` objects)
describing changes. Renderers consume these rows and present them in
human-readable formats such as side-by-side (2up) or line-based views.

[[diff.design]]
The diff system is intentionally split into two layers:

- detectors: compute structured differences
- renderers: format and display those differences

This separation allows consistent diff logic to be reused across
different output styles and tools.

[[diff.color_policy]]
Foreground color is always chosen explicitly.

- black foreground is permitted only on light backgrounds
- saturated backgrounds (red/green) must force high contrast
- implicit terminal defaults are never relied upon

This ensures readability across light and dark terminal themes.

[[diff.usage]]
Typical usage:

    delta = diff.text(before, after)
    diff.render(delta)

[[diff.notes]]
This module is commonly used to support ``--dry-run`` style workflows
where proposed changes are displayed before being applied.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from dataclasses import dataclass
import difflib
import re
from collections.abc import Iterable

import tomlkit
from tomlkit.toml_document import TOMLDocument

from pbox.tty import stdout_width
from pbox.style import style


# -------------------------------------------------------------------
# Data model (delta)
# -------------------------------------------------------------------


@dataclass(frozen=True)
class Row:
    kind: str  # "equal", "insert", "delete", "replace", "fold"
    left: str | None
    right: str | None


@dataclass(frozen=True)
class Delta:
    rows: list[Row]

    @property
    def changed(self) -> bool:
        return bool(self.rows)


# -------------------------------------------------------------------
# Renderer helpers
# -------------------------------------------------------------------

MAX_COL_WIDTH = 40
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


# -------------------------------------------------------------------
# Renderer helpers
# -------------------------------------------------------------------

MAX_COL_WIDTH = 40

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def _visible_len(s: str) -> int:
    return len(ANSI_RE.sub("", s))


def _pad_visible(s: str, width: int) -> str:
    return s + (" " * max(0, width - _visible_len(s)))


def _colorize(row: Row, *, color: bool) -> tuple[str, str]:
    left = row.left or ""
    right = row.right or ""

    if not color:
        return left, right

    if row.kind == "insert":
        return "", style.insert(right)

    if row.kind == "delete":
        return style.delete(left), ""

    if row.kind == "replace":
        return style.replace_left(left), style.replace_right(right)

    if row.kind == "fold":
        label = style.fold()
        return label, label

    return left, right  # equal


def _compute_2up_widths() -> tuple[int, int]:
    """
    Compute left/right column widths for 2up diff.
    Defaults to 120 columns total, split 40/80.
    """
    total = stdout_width(120)

    MIN_TOTAL = 90
    SEAM = 3  # " │ "

    if total < MIN_TOTAL:
        return 32, max(32, total - 32 - SEAM)

    available = total - SEAM

    left = min(40, available // 3)
    right = available - left

    return left, right


def _truncate_middle(s: str, width: int) -> str:
    """
    Truncate string to fit width, preserving start and end context.
    """
    ellipsis = style.ELLIPSIS

    if _visible_len(s) <= width:
        return s

    if width <= _visible_len(ellipsis) + 2:
        return ellipsis[:width]

    keep = (width - _visible_len(ellipsis)) // 2
    return s[:keep] + ellipsis + s[-keep:]


# -------------------------------------------------------------------
# Diff detector helpers
# -------------------------------------------------------------------


def _emit_equal(rows: list[Row], lines: list[str], context: int) -> None:
    n = len(lines)
    if n <= context * 2 + 1:
        for line in lines:
            rows.append(Row("equal", line, line))
        return

    for line in lines[:context]:
        rows.append(Row("equal", line, line))

    rows.append(Row("fold", None, None))

    for line in lines[-context:]:
        rows.append(Row("equal", line, line))


def _emit_replace(rows: list[Row], left: list[str], right: list[str]) -> None:
    max_len = max(len(left), len(right))
    for i in range(max_len):
        l_str = left[i] if i < len(left) else None
        r_str = right[i] if i < len(right) else None
        rows.append(Row("replace", l_str, r_str))


def _sequence_diff(before: Iterable[str], after: Iterable[str], *, context: int = 3) -> Delta:
    """
    Generic line-based diff producing Delta rows.
    """
    before_lines = list(before)
    after_lines = list(after)

    if before_lines == after_lines:
        return Delta([])

    matcher = difflib.SequenceMatcher(a=before_lines, b=after_lines)
    rows: list[Row] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            _emit_equal(rows, before_lines[i1:i2], context)

        elif tag == "insert":
            for line in after_lines[j1:j2]:
                rows.append(Row("insert", None, line))

        elif tag == "delete":
            for line in before_lines[i1:i2]:
                rows.append(Row("delete", line, None))

        elif tag == "replace":
            _emit_replace(rows, before_lines[i1:i2], after_lines[j1:j2])

    return Delta(rows)


# -------------------------------------------------------------------
# Diff detectors by source
# -------------------------------------------------------------------


def text(before: str, after: str, *, context: int = 3) -> Delta:
    """
    Return a Delta describing differences between two text blobs.
    """
    return _sequence_diff(
        before.splitlines(),
        after.splitlines(),
        context=context,
    )


def toml(before: TOMLDocument, after: TOMLDocument, *, strict: bool = False) -> Delta:
    """
    Return a Delta describing differences between two TOML documents.

    strict=False ignores comments and formatting (future).
    strict=True includes syntactic changes (future).
    """
    before_text = tomlkit.dumps(before)
    after_text = tomlkit.dumps(after)

    return _sequence_diff(
        before_text.splitlines(),
        after_text.splitlines(),
        context=3,
    )


# -------------------------------------------------------------------
# Renderers
# -------------------------------------------------------------------


def render(delta: Delta, *, mode: str = "2up", color: bool = True) -> None:
    """
    Render a Delta using the selected output mode.
    """
    if not delta.rows:
        return

    if mode == "2up":
        render_2up(delta, color=color)
    elif mode == "lines":
        render_lines(delta)
    else:
        raise ValueError(f"Unknown diff render mode: {mode}")


def render_2up(delta: Delta, *, color: bool = True) -> None:
    rows = delta.rows
    if not rows:
        return

    left_width, right_width = _compute_2up_widths()

    for row in rows:
        left, right = _colorize(row, color=color)

        left = _truncate_middle(left, left_width)
        right = _truncate_middle(right, right_width)

        left_cell = _pad_visible(left, left_width)
        print(f"{left_cell} │ {right}")


def render_lines(delta: Delta) -> None:
    """
    Render a Delta in traditional unified (+/-) format.
    """
    for row in delta.rows:
        if row.kind == "equal":
            print(f" {row.left}")
        elif row.kind == "insert":
            print(f"+{row.right}")
        elif row.kind == "delete":
            print(f"-{row.left}")
        elif row.kind == "replace":
            if row.left is not None:
                print(f"-{row.left}")
            if row.right is not None:
                print(f"+{row.right}")
        elif row.kind == "fold":
            print(f"... {style.FOLD_LABEL} ...")
