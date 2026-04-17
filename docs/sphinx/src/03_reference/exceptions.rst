exceptions
====================

Base exception hierarchy for pbox.

This module defines the base exception type used across pbox.

All domain-specific errors should derive from ``PboxError`` to allow callers to catch pbox-specific failures without masking unrelated exceptions.

Typical usage:

::

   from pbox.exceptions import PboxError

   try:
       ...
   except PboxError:
       ...

Keep the exception hierarchy intentionally shallow. Prefer a single base type unless specific error categories provide clear value.
