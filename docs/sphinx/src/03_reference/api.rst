api
====================

Decorator-based declaration of public API entities.

This module provides the public ``api`` decorator used to mark functions, classes, and other objects as part of the supported public surface of npkglib.

The decorator is backed by the lightweight registry implemented in ``npkglib._api``. It allows public interface declarations to remain close to the code they describe while staying dependency-light and safe to import broadly.

Typical usage:

::

   from npkglib import api

   @api()
   def my_function():
       ...

Optional metadata may be attached to help organize or describe API entities for downstream tooling:

::

   @api(group="diff")
   def render_diff(...):
       ...

This module is the public facade for API declaration.

Implementation details of registration and low-level registry management live in ``npkglib._api``.

Documentation tooling such as psym may later consume this registry to derive structured documentation symbols from declared API entities.
