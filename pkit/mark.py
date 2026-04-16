"""
pkit.mark

Message emission and presentation helpers.

[[mark.meta.title]]
mark

[[mark.meta.tagline]]
Context-aware message emission for CLI-style output.

[[mark.description]]
This module provides helpers for emitting user-facing messages with
consistent formatting and behavior across pkit-based tools.

It interprets presentation context (quiet, verbose, emoji) to decide
when and how messages are emitted.

[[mark.design]]
Design principles:

- no business logic
- no command-level decisions
- context-driven output behavior
- consistent formatting across tools

The module separates *what to say* from *how and when to say it*.

[[mark.architecture]]
Core components:

- MarkContext: controls output behavior (quiet, verbose, emoji)
- Marks: accumulates messages for deferred rendering
- emit helpers: section, info, warn, error, verbose

Output is written to stderr.

[[mark.usage]]
Typical usage:

    import pkit.mark as mark

    mark.configure(mark.MarkContext(verbose=True))

    mark.section("Starting")
    mark.info("Processing file")
    mark.warn("Minor issue detected")
    mark.error("Something failed")

[[mark.notes]]
- wrapping respects terminal width
- indentation from caller is preserved
- multi-line messages are not re-wrapped
- section output is never wrapped

Formatting is intentionally simple and stable.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

import sys
import textwrap
from dataclasses import dataclass, field

from pkit.utils.tty import stdout_width


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@dataclass
class MarkContext:
    quiet: bool = False
    verbose: bool = False
    emoji: bool = True


@dataclass
class Marks:
    infos: list[str] = field(default_factory=list)
    warns: list[str] = field(default_factory=list)
    errs: list[str] = field(default_factory=list)

    def ok(self) -> bool:
        return not self.errs

    def extend(self, other: Marks) -> None:
        self.infos.extend(other.infos)
        self.warns.extend(other.warns)
        self.errs.extend(other.errs)

    def render(self) -> None:
        for msg in self.infos:
            info(msg)
        for msg in self.warns:
            warn(msg)
        for msg in self.errs:
            error(msg)


_ctx: MarkContext = MarkContext()


_EMOJI = {
    "section": "\n▶ ",
    "error": "❌ ",
    "warn": "⚠️  ",
    "verbose": "🔍 ",
    "info": "ℹ️  ",
}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def configure(ctx: MarkContext) -> None:
    global _ctx
    _ctx = ctx


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _wrap_msg(msg: str, prefix: str, *, no_wrap: bool) -> list[str]:
    """
    Wrap a message while preserving any leading indentation
    supplied by the caller.
    """
    if no_wrap or "\n" in msg:
        return [msg]

    # Preserve caller indentation
    stripped = msg.lstrip(" ")
    indent = msg[: len(msg) - len(stripped)]

    width = stdout_width()
    usable = max(40, width - len(prefix) - len(indent))

    wrapped = textwrap.wrap(
        stripped,
        width=usable,
        break_long_words=False,
        break_on_hyphens=False,
    )

    return [indent + line for line in wrapped]


def _emit(level: str, msg: str, *, no_wrap: bool = False) -> None:
    if _ctx.quiet:
        return

    if level == "verbose" and not _ctx.verbose:
        return

    # Section is special: never wrapped, preserves structure
    if level == "section":
        if _ctx.emoji:
            prefix = _EMOJI["section"]
            print(f"{prefix}{msg}", file=sys.stderr)
        else:
            print(f"\n{msg}", file=sys.stderr)
        return

    prefix = _EMOJI.get(level, "") if _ctx.emoji else ""

    lines = _wrap_msg(msg, prefix, no_wrap=no_wrap)

    for i, line in enumerate(lines):
        if i == 0:
            print(f"{prefix}{line}", file=sys.stderr)
        else:
            print(f"{' ' * len(prefix)}{line}", file=sys.stderr)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def section(title: str, *, no_wrap: bool = False) -> None:
    # no_wrap accepted for interface symmetry; ignored intentionally
    _emit("section", title, no_wrap=True)


def info(msg: str, *, no_wrap: bool = False) -> None:
    _emit("info", msg, no_wrap=no_wrap)


def verbose(msg: str, *, no_wrap: bool = False) -> None:
    _emit("verbose", msg, no_wrap=no_wrap)


def warn(msg: str, *, no_wrap: bool = False) -> None:
    _emit("warn", msg, no_wrap=no_wrap)


def error(msg: str, *, no_wrap: bool = False) -> None:
    _emit("error", msg, no_wrap=no_wrap)
