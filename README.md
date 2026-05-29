<!--
psym :: documentation rendered from source.
Do not edit this artifact directly.
-->
# npkglib

**A small, composable Python utility library for reuse across npkg projects.**

<p align="center">
  <img src="docs/psym/assets/npkglib.png" width="180" alt="npkglib logo">
</p>

<p align="center">
<a href="https://tracecutter.github.io/npkglib/">
<img src="https://img.shields.io/badge/docs-GitHub%20Pages-blue" alt="Docs">
</a>
<img src="https://img.shields.io/badge/python-3.11%2B-blue" alt="Python">
<img src="https://img.shields.io/badge/status-experimental-lightgrey" alt="Status">
<a href="./LICENSE">
<img src="https://img.shields.io/badge/license-proprietary-lightgrey" alt="License">
</a>
</p>

---

<details>
<summary><strong>Table of Contents</strong></summary>

- [Installation](#installation)
- [Modules](#modules)
- [Overview](#overview)
- [Usage](#usage)
- [Development](#development)
- [Changelog](#changelog)
- [Links](#links)

</details>

---

## Installation 

Install from source (development):

    pip install -e .

Or from a package index:

    pip install npkglib

---

## Modules 

- **api_gen** — Bootstrap semantic API decorator registry.
- **diff** — Diff / delta detection and rendering utilities.
- **exceptions** — Core exception types for npkglib.
- **fmt** — Formatting primitives.
- **guppy** — Minimal runtime event pipeline.
- **mark** — Message emission and presentation helpers.
- **result** — Result emission helpers.
- **signal** — Runtime signalling primitives.
- **style** — Styling primitives and presentation policy.
- **table** — Tabular data rendering utilities.
- **toml_io** — TOML document I/O and navigation utilities.
- **tty** — Terminal environment helpers.
- **version** — Minimal semantic version utilities.

---

## Overview 

npkglib provides a collection of small, focused utilities that form the
shared foundation of the npkg ecosystem.

It emphasizes:

- minimal dependencies
- composable building blocks
- consistent conventions across projects

Rather than re-implementing common patterns, projects depend on npkglib
to supply a stable, reusable core.

---

## Usage 

Import and use utilities directly:

    from npkglib import diff, table, tty

Modules are designed to be independent and safe to use in isolation.

---

## Development 

Clone and install in editable mode:

```bash
git clone https://github.com/tracecutter/npkglib.git
cd npkglib
make install
```

To build docs locally:

```bash
make docs
```

Run checks:

```bash
make check
```

Run tests:

```bash
pytest
```

Update README usage:

```bash
make readme
```

---

## Changelog 

### v1.0.0
- Initial public release
- Dependency inspection and mutation
- README usage auto-generation
- Designed as a reference implementation for `npkg`

---

## Links 

- GitHub: https://github.com/tracecutter/npkglib
- Documentation: https://tracecutter.github.io/npkglib/

