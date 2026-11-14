"""
npkglib.guppy

Minimal runtime event pipeline.

[[guppy.meta.title]]
guppy

[[guppy.meta.tagline]]
Lightweight event bus and publication pipeline.

[[guppy.description]]
This module provides a minimal runtime event system for emitting,
routing, and optionally transforming events within a process.

The system is intentionally simple and designed for:

- tracing
- telemetry
- structured logging
- lightweight observability

[[guppy.architecture]]
Core flow:

    trigger → post(Event) → EventBus → sinks

Some sinks may transform events into higher-level outputs:

    Event → PublisherSink → Publication → subscribers

If the system is not bootstrapped, events are silently dropped.

[[guppy.design]]
Design principles:

- minimal surface area
- no external dependencies
- synchronous dispatch
- opt-in activation via bootstrap()

This keeps the system safe to import anywhere without side effects.

[[guppy.usage]]
Typical usage:

    import npkglib.guppy as guppy

    guppy.bootstrap()
    guppy.post(EventMsg(stream="trace", name="start"))

Sinks must be registered explicitly on the EventBus.

[[guppy.notes]]
This module is intentionally unopinionated about:

- persistence
- transport
- formatting (delegated to sinks)

Formatting helpers are provided via ``npkglib.fmt``.

INTERNAL

:copyright: Copyright (c) 2026 John Fogelin.
:license: MIT, see LICENSE for details.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from collections.abc import Callable
from npkglib import fmt
import time


Scalar = str | int | float | bool
Field = tuple[str, Scalar]  # (type, value)

FIELD_TYPES: set[str] = {
    "string",
    "number",
    "count",
    "duration",
    "percent",
    "bool",
    "iso_time",
}


def known_field_types() -> tuple[str, ...]:
    """Return supported NTX field types."""
    return tuple(sorted(FIELD_TYPES))


# ---------------------------------------------------------------------------
# Event model
# ---------------------------------------------------------------------------


@dataclass
class Event:
    """Base runtime event."""

    timestamp: float = field(default_factory=time.time, init=False)


@dataclass
class EventMsg(Event):
    stream: str
    name: str
    fields: dict[str, Field] | None = None


# ---------------------------------------------------------------------------
# Publication model
# ---------------------------------------------------------------------------


@dataclass
class Publication:
    """
    Curated output derived from events.

    Produced by PublisherSink instances and delivered to subscribers.
    """

    topic: str
    payload: dict
    timestamp: float = field(default_factory=time.time, init=False)


# ---------------------------------------------------------------------------
# EventBus
# ---------------------------------------------------------------------------


class EventBus:

    def __init__(self):
        self._sinks: list[Sink] = []

    def sink_add(self, sink: Sink) -> None:
        self._sinks.append(sink)

    def sink_remove(self, sink: Sink) -> None:
        self._sinks.remove(sink)

    def dispatch(self, event: Event) -> None:
        for sink in self._sinks:
            sink.handle(event)


# ---------------------------------------------------------------------------
# Global runtime state
# ---------------------------------------------------------------------------


_EVENT_BUS: EventBus | None = None


# ---------------------------------------------------------------------------
# Bootstrapping
# ---------------------------------------------------------------------------


def bootstrap() -> None:
    """
    Initialize the global event bus.
    """
    global _EVENT_BUS

    if _EVENT_BUS is None:
        _EVENT_BUS = EventBus()


def event_bus() -> EventBus:
    if _EVENT_BUS is None:
        raise RuntimeError("guppy not bootstrapped")

    return _EVENT_BUS


def field_types() -> tuple[str, ...]:
    return known_field_types()


# ---------------------------------------------------------------------------
# Event emission
# ---------------------------------------------------------------------------


def post(event: Event) -> None:
    """
    Post an event to the runtime bus.

    If guppy is not bootstrapped, events are dropped.
    """
    if not isinstance(event, Event):
        raise TypeError("post() requires Event instance")

    if _EVENT_BUS is None:
        return

    _EVENT_BUS.dispatch(event)


# ---------------------------------------------------------------------------
# Sink interface
# ---------------------------------------------------------------------------


class Sink:
    """Base event sink."""

    def handle(self, event: Event) -> None:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Publisher sink
# ---------------------------------------------------------------------------


class PublisherSink(Sink):
    """
    Sink that converts events into curated publications.

    Subscribers can register to receive publications.
    """

    def __init__(self):
        self._subscribers: list[Callable[[Publication], None]] = []

    # ---------------------------------------------------------------------

    def subscribe(self, fn: Callable[[Publication], None]) -> None:
        self._subscribers.append(fn)

    # ---------------------------------------------------------------------

    def publish(self, pub: Publication) -> None:

        for sub in self._subscribers:
            sub(pub)


# ---------------------------------------------------------------------------
# Sink renderers
# ---------------------------------------------------------------------------


class FlatRenderer(Sink):
    """
    1-up renderer (flattened output).

    All streams rendered linearly.
    """

    def handle(self, event: Event) -> None:

        if not isinstance(event, EventMsg):
            return

        msg = f"{event.stream}: " + event.name

        if event.fields:
            parts = [f"{k}={fmt.field(t, v)}" for k, (t, v) in event.fields.items()]
            msg = f"{msg} " + " ".join(parts)

        print(msg)


class ColumnRenderer(Sink):
    """
    Simple N-up renderer.

    Column 1: result
    Column 2: narrate
    Column 3+: signals
    """

    def __init__(self):

        self.columns: dict[str, int] = {
            "result": 0,
            "narrate": 1,
        }

        self.next_column = 2

    # ---------------------------------------------------------------------

    def _ensure_column(self, stream: str) -> int:

        if stream not in self.columns:
            self.columns[stream] = self.next_column
            self.next_column += 1

        return self.columns[stream]

    # ---------------------------------------------------------------------

    def handle(self, event: Event) -> None:

        if not isinstance(event, EventMsg):
            return

        col = self._ensure_column(event.stream)

        # build a one-off row
        max_col = self.next_column - 1

        cells = [""] * (max_col + 1)
        msg = event.name

        if event.fields:
            parts = []

            for k, (t, v) in event.fields.items():
                parts.append(f"{k}={fmt.field(t, v)}")

            msg = f"{msg} " + " ".join(parts)

        cells[col] = msg

        print(" | ".join(cells))
