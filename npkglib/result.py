"""
npkglib.result

Result emission helpers.

[[result.meta.title]]
result

[[result.meta.tagline]]
Primary output channel for command results.

[[result.description]]
This module provides a minimal abstraction for emitting primary
command results to stdout.

It represents the "result channel" of a tool, distinct from:

- mark (narration / diagnostics → stderr)
- guppy (events / telemetry → optional pipeline)

[[result.design]]
Design principles:

- single responsibility: emit final results
- minimal policy surface
- context-driven behavior
- stdout only

Commands are responsible for mapping user intent (e.g. --dry-run,
--diff, --check) into a ResultContext.

[[result.modes]]
Supported modes:

- nominal: normal output
- proof: reserved for verification-style output
- diff: reserved for structured diff output
- null: suppress all output

[[result.usage]]
Typical usage:

    import npkglib.result as result

    result.configure(ResultContext(mode="nominal"))
    result.text("hello world")

[[result.notes]]
This module is intentionally small and may evolve as guppy-based
result flows mature.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


ResultMode = Literal["nominal", "proof", "diff", "null"]


@dataclass
class ResultContext:
    mode: ResultMode = "nominal"


_ctx: ResultContext = ResultContext()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


def configure(ctx: ResultContext) -> None:
    """
    Configure the emission context.

    Commands are responsible for translating user intent
    (flags such as --dry-run, --diff, --check) into emit_mode.
    """
    global _ctx
    _ctx = ctx


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def text(msg: str = "") -> None:
    """
    Result primary payload text.

    Suppressed entirely when emit_mode is 'null'.
    """
    if _ctx.mode == "null":
        return

    print(msg, file=sys.stdout)
