"""
npkglib.toml_io

TOML document I/O and navigation utilities.

[[toml_io.meta.title]]
toml_io

[[toml_io.meta.tagline]]
Round-trippable TOML handling with dotted-key access.

[[toml_io.description]]
This module provides low-level helpers for working with TOML documents
using ``tomlkit``. All operations preserve formatting, comments, and
ordering where possible.

The module supports:

- loading and saving TOML documents
- serialization and cloning
- safe navigation via dotted keys
- access to live nodes for mutation

[[toml_io.design]]
Design principles:

- no domain knowledge
- no validation or policy
- preserve formatting fidelity
- explicit separation of read vs mutation
- predictable, minimal behavior

This module operates purely at the structural level. It does not interpret
or validate configuration semantics.

[[toml_io.usage]]
Typical usage:

```python
    from npkglib import toml_io as toml

    doc = toml.load(path)
    working_copy = toml.clone(doc)

    value = toml.get_by_dotted_key(doc, "project.name")
    node = toml.ref_by_dotted_key(doc, "project")

    text = toml.dump(doc)
    toml.save(doc, path)
```

[[toml_io.notes]]
- ``get_by_dotted_key`` returns plain Python values (dict/list/scalar)
- ``ref_by_dotted_key`` returns live tomlkit nodes for mutation
- missing keys return ``None`` (get) or raise ``KeyError`` (ref)
- cloning uses serialization to avoid shared object graphs

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""

from __future__ import annotations

from pathlib import Path
from typing import cast, Any

import tomlkit
from tomlkit.toml_document import TOMLDocument
from tomlkit.items import Table


def get_by_dotted_key(doc: TOMLDocument, dotted: str) -> Any | None:
    """
    Resolve a dotted key into nested TOML structures.

    Returns:
        - scalar (str/int/bool)
        - list
        - dict
        - None (if missing)
    """
    parts = dotted.split(".")
    cur: Any = doc

    for part in parts:
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None

    if isinstance(cur, Table):
        return dict(cur)

    if isinstance(cur, list):
        return list(cur)

    return cur


def ref_by_dotted_key(doc: TOMLDocument, dotted: str) -> Any:
    """
    Resolve a dotted key and return the live tomlkit node.

    Intended for mutation. Raises KeyError if the path is missing.
    """
    cur: Any = doc
    for part in dotted.split("."):
        try:
            cur = cur[part]
        except Exception as e:
            raise KeyError(f'Key "{dotted}" not found') from e
    return cur


# ---------------------------------------------------------------------------
# Core TOML operations
# ---------------------------------------------------------------------------


def load(path: Path) -> TOMLDocument:
    """
    Load a TOML document from disk.
    """
    return cast(TOMLDocument, tomlkit.parse(path.read_text(encoding="utf-8")))


def dump(doc: TOMLDocument) -> str:
    """
    Serialize a TOML document.
    """
    return tomlkit.dumps(doc)


def save(doc: TOMLDocument, path: Path) -> None:
    """
    Save a TOML document to disk.
    """
    path.write_text(dump(doc), encoding="utf-8")


def clone(doc: TOMLDocument) -> TOMLDocument:
    """
    Create a fully isolated copy of a TOML document.

    This reconstructs via serialization to avoid shared object graphs.
    """
    return cast(TOMLDocument, tomlkit.parse(tomlkit.dumps(doc)))
