toml_io
====================

Round-trippable TOML handling with dotted-key access.

This module provides low-level helpers for working with TOML documents using ``tomlkit``. All operations preserve formatting, comments, and ordering where possible.

The module supports:

- loading and saving TOML documents
- serialization and cloning
- safe navigation via dotted keys
- access to live nodes for mutation

Typical usage:

.. code:: python

       from npkglib import toml_io as toml

       doc = toml.load(path)
       working_copy = toml.clone(doc)

       value = toml.get_by_dotted_key(doc, "project.name")
       node = toml.ref_by_dotted_key(doc, "project")

       text = toml.dump(doc)
       toml.save(doc, path)

- ``get_by_dotted_key`` returns plain Python values (dict/list/scalar)
- ``ref_by_dotted_key`` returns live tomlkit nodes for mutation
- missing keys return ``None`` (get) or raise ``KeyError`` (ref)
- cloning uses serialization to avoid shared object graphs
