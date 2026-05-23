guppy
====================

Lightweight event bus and publication pipeline.

This module provides a minimal runtime event system for emitting, routing, and optionally transforming events within a process.

The system is intentionally simple and designed for:

- tracing
- telemetry
- structured logging
- lightweight observability

Typical usage:

::

   import npkglib.guppy as guppy

   guppy.bootstrap()
   guppy.post(EventMsg(stream="trace", name="start"))

Sinks must be registered explicitly on the EventBus.

This module is intentionally unopinionated about:

- persistence
- transport
- formatting (delegated to sinks)

Formatting helpers are provided via ``npkglib.fmt``.
