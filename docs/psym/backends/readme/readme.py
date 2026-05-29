"""
docs.psym.backends.readme

Render the README.md documentation artifact.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

from pathlib import Path
import importlib
import pkgutil

from psym import symbol_add
from psym import Backend, BackendContext, RenderJob, Template


# ---------------------------------------------------------------------------
# Backend
# ---------------------------------------------------------------------------


def _discover_modules(pkg_name: str):
    pkg = importlib.import_module(pkg_name)

    if not hasattr(pkg, "__path__"):
        return []

    out = []

    for mod in pkgutil.iter_modules(pkg.__path__):
        name = mod.name

        if name.startswith("_"):
            continue

        full = f"{pkg_name}.{name}"

        try:
            module = importlib.import_module(full)
        except Exception:
            continue

        doc = (module.__doc__ or "").strip().splitlines()

        summary = ""

        if len(doc) >= 3:
            summary = doc[2].strip()
        elif len(doc) >= 1:
            # fallback (just in case someone breaks convention)
            first = doc[0].strip()
            if first != full:
                summary = first

        out.append(
            {
                "name": name,
                "summary": summary,
            }
        )

    return sorted(out, key=lambda x: x["name"])


def _value_modules(mods: list[dict[str, str]]) -> str:
    lines = []

    for mod in mods:
        if mod["summary"]:
            lines.append(f"- **{mod['name']}** — {mod['summary']}")
        else:
            lines.append(f"- **{mod['name']}**")

    return "\n".join(lines)


class ReadmeBackend(Backend):
    """
    README backend.

    Produces a single README.md artifact using the shared
    documentation symbol universe.
    """

    def render_literal(self, value: str, *, lang: str | None, indent: str) -> str:
        lang = lang or ""

        lines = value.splitlines()

        out = []
        out.append("")  # ensure separation

        out.append(f"{indent}```{lang}")
        for line in lines:
            out.append(f"{indent}{line}" if line else "")
        out.append(f"{indent}```")

        out.append("")  # ensure separation

        return "\n".join(out)

    def build(self, ctx: BackendContext):
        template = Template.from_file(ctx.docs_root / "templates/readme.md.pf")

        sym = ctx.symbols.get("project.name")
        pkg_name = sym.value if sym else "npkglib"

        modules = _discover_modules(pkg_name)

        symbol_add(
            ctx.symbols,
            "dynamic.modules",
            _value_modules(modules),
            origin="readme.symtab",
            fmt="md",
        )

        yield RenderJob(
            template=template,
            symbols=ctx.symbols,
            output_path=Path("readme/README.md"),
            fmt="md",
            render_hooks=self,
        )


# Announcement
PSYM_BACKEND = ReadmeBackend(
    requests=["project", "fs", "dynamic", "api"],
    code=[
        Path("__init__.py"),
    ],
)
