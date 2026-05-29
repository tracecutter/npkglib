Version utilities
=================

Pure helpers for parsing and incrementing semantic version strings.

Provides small, reusable primitives for working with version strings. These functions operate purely on strings and raise standard exceptions on invalid input.

No filesystem access, configuration, or project semantics are involved.

Used by tools such as pfig and pfix to update version identifiers in their respective configuration files.

This module does not enforce full semantic versioning rules. It assumes a simple MAJOR.MINOR.PATCH structure and ignores pre-release or build metadata.
