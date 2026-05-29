api_gen
=======

Dependency-free semantic API registry and decorator.

This module provides the core ``api`` decorator used to declare semantic API entities within a package.

Decorated objects may include:

- functions
- classes
- exceptions
- other public package entities

The module is intentionally designed to remain dependency-free with respect to the rest of ``npkglib`` so that it may be safely imported from any package module without introducing circular dependencies.

The decorator records annotated objects in a lightweight registry and optionally promotes them onto the owning package namespace.

Typical usage:

::

   from npkglib.api_gen import api

   @api
   def render_diff(...):
       ...

   @api(group="backend")
   class Backend:
       ...

Decorated objects are:

- recorded in the internal registry
- optionally exported onto the package namespace
- included in the package ``__all__``

Higher-level tooling (e.g. psym) may inspect the registry to derive structured documentation, semantic API references, or symbol tables.
