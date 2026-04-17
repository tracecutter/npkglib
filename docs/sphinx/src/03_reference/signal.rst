signal
====================

Lightweight runtime signalling and tracing helpers.

This module provides primitives for emitting structured runtime signals with near-zero overhead when disabled.

Signals represent occurrences within a program but perform no routing themselves. They are translated into events and forwarded to the ``pbox.guppy`` event pipeline.

Three primary usage patterns:

Inline watchpoint:

::

   trace("event", count=3)

Function decorator:

::

   @trace
   def work():
       ...

Class decorator (selected methods):

::

   @trace("run", "execute")
   class Worker:
       ...

- signals do not format output (handled by sinks)
- signals do not persist data
- signals are intended to compose with ``pbox.guppy``

This module forms the instrumentation layer of pbox.
