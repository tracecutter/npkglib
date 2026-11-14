"""
npkglib.signal

Runtime signalling primitives.

[[signal.meta.title]]
signal

[[signal.meta.tagline]]
Lightweight runtime signalling and tracing helpers.

[[signal.description]]
This module provides primitives for emitting structured runtime signals
with near-zero overhead when disabled.

Signals represent occurrences within a program but perform no routing
themselves. They are translated into events and forwarded to the
``npkglib.guppy`` event pipeline.

[[signal.architecture]]
Core flow:

    signaller → Signal → trigger() → EventMsg → guppy.post()
             → EventBus → sinks

Signals are inert unless explicitly enabled.

[[signal.design]]
Design principles:

- extremely low overhead when disabled
- synchronous instrumentation
- explicit enable/disable control
- composable signal types
- decorator + inline usage

This allows signals to be left in production code safely.

[[signal.usage]]
Three primary usage patterns:

Inline watchpoint:

    trace("event", count=3)

Function decorator:

    @trace
    def work():
        ...

Class decorator (selected methods):

    @trace("run", "execute")
    class Worker:
        ...

[[signal.types]]
Built-in signal streams:

- trace: structural execution tracing
- telemetry: runtime metrics and measurements

[[signal.notes]]
- signals do not format output (handled by sinks)
- signals do not persist data
- signals are intended to compose with ``npkglib.guppy``

This module forms the instrumentation layer of npkglib.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""

import functools
import time

from npkglib import guppy
from npkglib.guppy import Scalar, EventMsg


# ---------------------------------------------------------------------------
# Signal base
# ---------------------------------------------------------------------------


class Signal:
    stream = "signal"
    enabled = False
    __slots__ = ("timestamp", "name", "fields")

    def __init__(self, name: str, **fields):
        self.timestamp = time.time()
        self.name = name

        self.fields: dict[str, tuple[str, Scalar]] | None

        if fields:
            self.fields = {k: self._normalize_field(k, v) for k, v in fields.items()}
        else:
            self.fields = None

    @classmethod
    def enable(cls) -> None:
        cls.enabled = True

    @classmethod
    def disable(cls) -> None:
        cls.enabled = False

    @staticmethod
    def _normalize_field(key: str, value: object) -> tuple[str, Scalar]:
        # already typed → trust caller (but assert shape)
        if isinstance(value, tuple):
            t, v = value
            return (t, v)  # assume v is Scalar
        if key == "duration" and isinstance(value, (int, float)):
            return ("duration", float(value))
        if key in ("count", "n") and isinstance(value, int):
            return ("count", value)
        if isinstance(value, bool):
            return ("bool", value)
        if isinstance(value, (int, float)):
            return ("number", float(value))
        return ("string", str(value))


class TraceSignal(Signal):
    stream = "trace"


class TelemetrySignal(Signal):
    stream = "telemetry"


# ---------------------------------------------------------------------------
# Primitive
# ---------------------------------------------------------------------------


def trigger(signal: Signal) -> None:
    if not type(signal).enabled:
        return

    guppy.post(EventMsg(stream=signal.stream, name=signal.name, fields=signal.fields))


# ---------------------------------------------------------------------------
# Signal helper factory
# ---------------------------------------------------------------------------


def _make_signal_helper(signal_cls: type[Signal]):
    """
    Build a signal helper supporting:

        helper("event", foo=x)          inline watchpoint
        @helper                         function decorator
        @helper("method1","method2")    class decorator
    """

    def _wrap(func):
        name = f"{func.__module__}.{func.__qualname__}"
        cls = signal_cls

        @functools.wraps(func)
        def wrapper(*f_args, **f_kwargs):
            if not cls.enabled:
                return func(*f_args, **f_kwargs)

            start = time.perf_counter()
            trigger(cls(f"{name}.enter"))
            try:
                return func(*f_args, **f_kwargs)
            finally:
                duration = time.perf_counter() - start
                trigger(cls(f"{name}.exit", duration=duration))

        return wrapper

    def helper(*args, **payload):
        # ---- Inline watchpoint (payload OR single string)
        if payload or (len(args) == 1 and isinstance(args[0], str)):
            if not signal_cls.enabled:
                return None

            name = args[0] if args else ""
            trigger(signal_cls(name, **payload))
            return None

        # ---- Function decorator
        if len(args) == 1 and callable(args[0]):
            return _wrap(args[0])

        # ---- Class decorator
        if args and all(isinstance(m, str) for m in args):
            method_names = args

            def decorate_class(cls):
                for method_name in method_names:
                    if not hasattr(cls, method_name):
                        raise AttributeError(f"{cls.__name__} has no method '{method_name}'")

                    func = getattr(cls, method_name)

                    if not callable(func):
                        continue

                    setattr(cls, method_name, _wrap(func))

                return cls

            return decorate_class

        raise TypeError("Invalid use of signal helper")

    return helper


# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

trace = _make_signal_helper(TraceSignal)
telemetry = _make_signal_helper(TelemetrySignal)

# ---------------------------------------------------------------------------
# Signal registry
# ---------------------------------------------------------------------------

_SIGNAL_REGISTRY = {
    TraceSignal.stream: TraceSignal,
    TelemetrySignal.stream: TelemetrySignal,
}


def signal_types() -> tuple[str, ...]:
    """
    Return supported signal stream names.
    """
    return tuple(_SIGNAL_REGISTRY.keys())


def configure(enabled: tuple[str, ...] | None) -> None:
    enabled = enabled or ()

    for cls in _SIGNAL_REGISTRY.values():
        cls.disable()

    for name in enabled:
        sig_cls = _SIGNAL_REGISTRY.get(name)
        if sig_cls is None:
            continue

        sig_cls.enable()
