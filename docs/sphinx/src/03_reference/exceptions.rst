exceptions
====================

Base exception hierarchy for npkglib.

This module defines the base exception type used across npkglib.

All domain-specific errors should derive from ``NpkglibError`` to allow callers to catch npkglib-specific failures without masking unrelated exceptions.

Typical usage:

::

   from npkglib.exceptions import NpkglibError

   try:
       ...
   except NpkglibError:
       ...

Keep the exception hierarchy intentionally shallow. Prefer a single base type unless specific error categories provide clear value.
