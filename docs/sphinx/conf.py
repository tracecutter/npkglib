# ---------------------------------------------------------------------------
# Sphinx configuration — npkglib
# Rendering only (content produced by npkglib)
# ---------------------------------------------------------------------------

from __future__ import annotations
from datetime import datetime

# ---------------------------------------------------------------------------
# Project metadata
# ---------------------------------------------------------------------------

project = "npkglib"
author = "John Fogelin"
copyright = f"{datetime.now().year}, {author}"

release = globals().get("release", "dev")
version = release

# ---------------------------------------------------------------------------
# General configuration
# ---------------------------------------------------------------------------

extensions = [
    "sphinx.ext.autosectionlabel",  # cross-ref sections
    "sphinx.ext.graphviz",  # diagrams (pdep!)
    "sphinx.ext.mathjax",  # we like math!
]

# templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Make section labels nicer (optional but helpful)
autosectionlabel_prefix_document = True

# ---------------------------------------------------------------------------
# Graphviz configuration
# ---------------------------------------------------------------------------

graphviz_output_format = "svg"  # crisp, scalable
graphviz_dot_args = [
    "-Gfontname=DejaVu Sans",
    "-Nfontname=DejaVu Sans",
    "-Efontname=DejaVu Sans",
]

# ---------------------------------------------------------------------------
# HTML output
# ---------------------------------------------------------------------------

html_theme = "furo"

html_static_path = ["_static"]
html_logo = "_static/npkglib.png"
html_title = f"{project} {release}"

html_theme_options = {
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
}

html_css_files = [
    "custom.css",
]

# ---------------------------------------------------------------------------
# LaTeX / PDF output
# ---------------------------------------------------------------------------

latex_elements = {
    "papersize": "a4paper",
    "pointsize": "11pt",
    "classoptions": ",oneside,openany",
    "maketitle": r"""
\begin{titlepage}
\centering
\vspace*{3cm}

{\Huge\bfseries npkglib\par}
\vspace{0.5cm}
{\Large A Python project CLI\par}

\vfill

{\large John Fogelin\par}
\vspace{0.3cm}
{\small \today\par}

\vspace*{2cm}
\end{titlepage}
""",
    "preamble": r"""
\usepackage{geometry}
\geometry{margin=1in}
\usepackage{titlesec}
\titleformat{\chapter}{\Large\bfseries}{\thechapter}{1em}{}
\usepackage{setspace}
\setstretch{1.1}
\usepackage{graphicx}
\usepackage{enumitem}
\setlistdepth{9}
\usepackage[skip=6pt]{parskip}
""",
}

latex_elements[
    "preamble"
] += r"""
\usepackage{fvextra}
\DefineVerbatimEnvironment{Verbatim}{Verbatim}{
  fontsize=\small,
  frame=single,
  framerule=0.2pt
}
"""

latex_documents = [
    ("index", "npkglib.tex", "npkglib Documentation", author, "manual"),
]

latex_toplevel_sectioning = "chapter"

latex_show_urls = "inline"

# ---------------------------------------------------------------------------
# EPUB output
# ---------------------------------------------------------------------------

epub_show_urls = "footnote"
epub_title = project
epub_author = author
epub_language = "en"
