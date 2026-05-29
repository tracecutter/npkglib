"""
docs.psym.backends.sphinx

Render the Sphinx documentation set.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from __future__ import annotations

from pathlib import Path
import importlib
import pkgutil

from psym import Backend, BackendContext, RenderJob, Template
from psym import symbol_add
from psym import symbols_code_extract


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
        if doc:
            first = doc[0].strip()
            if first != full:
                summary = first

        out.append((name, summary))

    return sorted(out, key=lambda x: x[0])


class SphinxBackend(Backend):
    # ------------------------------------------------------------------
    # discovery
    # ------------------------------------------------------------------
    def _discover_sections(self, docs_root: Path) -> list[str]:
        """
        Discover section directories under templates/sphinx.

        Returns list of section names (including 'index').
        """
        base = docs_root / "templates/sphinx"

        sections: list[str] = []

        # root index
        if (base / "index.rst.pf").exists():
            sections.append("index")

        # sub-sections (directories with index.rst.pf)
        for p in sorted(base.iterdir()):
            if not p.is_dir():
                continue
            if (p / "index.rst.pf").exists():
                sections.append(p.name)

        return sections

    def _build_toctree(self, sections: list[str]) -> str:
        """
        Build Sphinx toctree entries from discovered sections.
        """
        lines: list[str] = []

        for name in sections:
            if name == "index":
                continue
            lines.append(f"   {name}/index")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # rendering helpers
    # ------------------------------------------------------------------

    def render_literal(self, value: str, *, lang: str | None, indent: str) -> str:
        lang = lang or "text"

        lines = value.splitlines()

        out = []
        out.append("")
        out.append(f"{indent}.. code-block:: {lang}")
        out.append("")

        for line in lines:
            if line:
                out.append(f"{indent}   {line}")
            else:
                out.append("")

        out.append("")
        return "\n".join(out)

    # ------------------------------------------------------------------
    # build
    # ------------------------------------------------------------------

    def build(self, ctx: BackendContext):
        sym = ctx.symbols.get("project.name")
        pkg_name = sym.value if sym else "npkglib"

        modules = _discover_modules(pkg_name)
        module_names = [name for name, _ in modules]
        sections = self._discover_sections(ctx.docs_root)
        toctree_modules = "\n".join(f"   {m}" for m in module_names)

        lines = []
        for name, summary in modules:
            if summary:
                lines.append(f"* **{name}** — {summary}")
            else:
                lines.append(f"* **{name}**")

        # ---- backend-owned symbol
        symbol_add(ctx.symbols, "dynamic.toctree", self._build_toctree(sections), origin="sphinx", fmt="rst")
        symbol_add(ctx.symbols, "dynamic.toctree.modules", toctree_modules, origin="sphinx", fmt="rst")
        symbol_add(ctx.symbols, "dynamic.modules", "\n".join(lines), origin="sphinx", fmt="rst")

        # ---- render each section
        base = ctx.docs_root / "templates/sphinx"

        for name in sections:

            if name == "index":
                template_path = base / "index.rst.pf"
                output_path = Path("sphinx/index.rst")
            else:
                template_path = base / name / "index.rst.pf"
                output_path = Path(f"sphinx/{name}/index.rst")

            template = Template.from_file(template_path)

            yield RenderJob(
                template=template,
                symbols=ctx.symbols.clone(),
                output_path=output_path,
                fmt="rst",
                render_hooks=self,
            )

            module_template = Template.from_file(ctx.docs_root / "templates/sphinx/03_reference/module.rst.pf")

            for name, _ in modules:
                symtab = ctx.symbols.clone()

                pkg = importlib.import_module(pkg_name)
                pkg_dir = Path(pkg.__file__).parent
                module_path = pkg_dir / f"{name}.py"

                # extract module symbols, produces: code.<module>.*
                symbols_code_extract(symtab, [module_path])

                # project module scope: code.<module>.* → dynamic.code.*
                prefix = f"code.{name}."

                for key, value in list(symtab.items()):
                    if not key.startswith(prefix):
                        continue

                    short = "dynamic.code." + key[len(prefix) :]

                    # RST requires document titles to be followed by an underline
                    # of matching length. We special-case the projected module title here.
                    if short == "dynamic.code.meta.title":
                        value = f"{value}\n{'=' * len(value)}"
                        fmt = "rst"
                        origin = "backend.sphinx"
                    else:
                        fmt = "md"
                        origin = "backend.sphinx"

                    symbol_add(symtab, short, value, fmt=fmt, origin=origin)

                # yield module RenderJob
                yield RenderJob(
                    template=module_template,
                    symbols=symtab,
                    output_path=Path(f"sphinx/03_reference/{name}.rst"),
                    fmt="rst",
                    render_hooks=self,
                )


# ---------------------------------------------------------------------------
# Announcement
# ---------------------------------------------------------------------------

PSYM_BACKEND = SphinxBackend(
    requests=["project", "fs", "dynamic"],
    code=[
        Path("__init__.py"),
    ],
)
