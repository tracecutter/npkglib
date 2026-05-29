"""
npkglib.version

Minimal semantic version utilities.

[[version.meta.title]]
Version utilities

[[version.meta.tagline]]
Pure helpers for parsing and incrementing semantic version strings.

[[version.description]]
Provides small, reusable primitives for working with version strings.
These functions operate purely on strings and raise standard exceptions
on invalid input.

No filesystem access, configuration, or project semantics are involved.

[[version.design]]
- Keep implementation minimal and explicit
- Depend on packaging.Version for parsing
- Avoid reimplementing version logic
- No policy, only primitives

[[version.usage]]
Used by tools such as pfig and pfix to update version identifiers in
their respective configuration files.

[[version.notes]]
This module does not enforce full semantic versioning rules. It assumes
a simple MAJOR.MINOR.PATCH structure and ignores pre-release or build
metadata.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: PROPRIETARY, see LICENSE for details.
"""

from packaging.version import Version, InvalidVersion


VALID_LEVELS = {"patch", "minor", "major"}


def semver_bump(v: str, level: str) -> str:
    if level not in VALID_LEVELS:
        raise ValueError(f"invalid level: {level} (expected patch|minor|major)")

    try:
        parsed = Version(v)
    except InvalidVersion as e:
        raise ValueError(f"invalid semantic version: {v}") from e

    if len(parsed.release) < 3:
        raise ValueError(f"invalid semantic version: {v}")

    major, minor, patch = parsed.release[:3]

    if level == "patch":
        patch += 1
    elif level == "minor":
        minor += 1
        patch = 0
    elif level == "major":
        major += 1
        minor = 0
        patch = 0

    return f"{major}.{minor}.{patch}"


def semver_validate(v: str) -> bool:
    """
    Return True if v is a valid MAJOR.MINOR.PATCH semantic version.

    Only accepts strict three-component versions (e.g. 1.2.3).
    Pre-release, post-release, and build metadata are rejected.
    """
    try:
        parsed = Version(v)
    except InvalidVersion:
        return False

    # must be exactly three numeric components
    if parsed.release is None or len(parsed.release) != 3:
        return False

    # reject pre/post/dev/local (e.g. 1.2.3rc1, 1.2.3+abc)
    if parsed.pre is not None or parsed.post is not None or parsed.dev is not None or parsed.local is not None:
        return False

    return True
