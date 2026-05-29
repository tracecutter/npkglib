result
======

Primary output channel for command results.

This module provides a minimal abstraction for emitting primary command results to stdout.

It represents the “result channel” of a tool, distinct from:

- mark (narration / diagnostics → stderr)
- guppy (events / telemetry → optional pipeline)

Typical usage:

::

   import npkglib.result as result

   result.configure(ResultContext(mode="nominal"))
   result.text("hello world")

This module is intentionally small and may evolve as guppy-based result flows mature.
