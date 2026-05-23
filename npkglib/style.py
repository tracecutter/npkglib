"""
npkglib.style

Styling primitives and presentation policy.

[[style.meta.title]]
style

[[style.meta.tagline]]
Centralized styling and presentation helpers.

[[style.description]]
This module defines styling primitives used across npkglib for
consistent visual output.

It centralizes:

- ANSI color definitions
- emoji conventions
- semantic styling helpers

[[style.design]]
Design principles:

- centralized styling policy
- no business logic
- stable visual vocabulary
- safe defaults across terminal themes

Higher-level modules (diff, mark, etc.) delegate styling decisions
to this module to avoid duplication and inconsistency.

[[style.policy]]
Color policy:

- foreground is always chosen explicitly
- black foreground only on light backgrounds
- high-contrast colors on saturated backgrounds
- default foreground used where theme sensitivity is preferred

This ensures readability across dark and light terminals.

[[style.usage]]
Typical usage:

    from npkglib.style import style

    style.insert("added line")
    style.delete("removed line")
    style.fold()

Or for lower-level control:

    style.bg(style.BG_GREEN, "text")

[[style.notes]]
- styling is separate from formatting (see ``npkglib.fmt``)
- styling is separate from emission (see ``npkglib.mark``)
- this module is intentionally opinionated

INTERNAL

This module exports styley freaky to avoid look and feel leaky.

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""


class Style:
    def __init__(self):
        self.emoji = {
            "error": "❌ ",
            "warn": "⚠️  ",
            "info": "ℹ️  ",
            "section": "\n▶ ",
        }

        # ANSI
        self.RESET = "\x1b[0m"

        self.FG_WHITE = "\x1b[97m"
        self.FG_BLACK = "\x1b[30m"
        self.FG_DEFAULT = "\x1b[39m"

        self.BG_RED = "\x1b[41m"
        self.BG_GREEN = "\x1b[42m"
        self.BG_FOLD = "\x1b[47m"

        self.ELLIPSIS = " [ … ] "
        self.FOLD_LABEL = "<---- folded ---->"

    def paint(self, text: str, fg: str = "", bg: str = "") -> str:
        return f"{bg}{fg}{text}{self.RESET}"

    # ------------------------------------------------------------------
    # Policy-aware helpers (THIS is the real win)
    # ------------------------------------------------------------------

    def bg(self, bg: str, text: str) -> str:
        """
        Apply background + safe foreground pairing.

        POLICY:
        - BG_FOLD  -> black fg (light background)
        - BG_RED   -> white fg
        - BG_GREEN -> default fg (theme-respecting)
        """
        if bg == self.BG_FOLD:
            fg = self.FG_BLACK
        elif bg == self.BG_RED:
            fg = self.FG_WHITE
        elif bg == self.BG_GREEN:
            fg = self.FG_DEFAULT
        else:
            fg = self.FG_DEFAULT

        return self.paint(text, fg=fg, bg=bg)

    # semantic helpers (optional but powerful)

    def insert(self, text: str) -> str:
        return self.bg(self.BG_GREEN, text)

    def delete(self, text: str) -> str:
        return self.bg(self.BG_RED, text)

    def replace_left(self, text: str) -> str:
        return self.bg(self.BG_RED, text)

    def replace_right(self, text: str) -> str:
        return self.bg(self.BG_GREEN, text)

    def fold(self) -> str:
        return self.bg(self.BG_FOLD, self.FOLD_LABEL)


style = Style()
