"""Observability — Lightweight tracing for tool calls, beats, and model requests.

OpenTelemetry-compatible span format. Exports to local JSON log file.
Can be extended to push to OTLP endpoint when one is configured.

SOTA gap: B3 (structured observability/tracing).
"""
import json
import logging
import time
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.observability")

TRACE_LOG = config.CLAWD_HOME / "logs" / "traces.jsonl"
_buffer: deque = deque(maxlen=1000)
_active_spans: dict[str, dict] = {}


class Span:
    """A lightweight span compatible with OpenTelemetry semantics."""

    def __init__(self, name: str, parent_id: str = None, attributes: dict = None):
        self.trace_id = parent_id.split(":")[0] if parent_id else uuid.uuid4().hex[:16]
        self.span_id = uuid.uuid4().hex[:16]
        self.parent_id = parent_id
        self.name = name
        self.start_time = time.time()
        self.end_time: Optional[float] = None
        self.status = "OK"
        self.attributes = attributes or {}
        self.events: list[dict] = []
        _active_spans[self.span_id] = self.__dict__

    def set_attribute(self, key: str, value):
        """Set a span attribute."""
        self.attributes[key] = value

    def add_event(self, name: str, attributes: dict = None):
        """Add an event to the span."""
        self.events.append({
            "name": name,
            "timestamp": time.time(),
            "attributes": attributes or {},
        })

    def set_error(self, error: str):
        """Mark span as errored."""
        self.status = "ERROR"
        self.attributes["error.message"] = error

    def end(self):
        """End the span and flush to buffer."""
        self.end_time = time.time()
        _active_spans.pop(self.span_id, None)
        record = {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_id": self.parent_id,
            "name": self.name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration_ms": round((self.end_time - self.start_time) * 1000, 2),
            "status": self.status,
            "attributes": self.attributes,
            "events": self.events,
        }
        _buffer.append(record)
        _maybe_flush()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.set_error(f"{exc_type.__name__}: {exc_val}")
        self.end()
        return False


def start_span(name: str, parent_id: str = None, **attributes) -> Span:
    """Create and start a new span."""
    return Span(name, parent_id, attributes)


def trace_tool_call(tool_name: str, beat_number: int = 0, parent_span_id: str = None) -> Span:
    """Create a span for a tool call."""
    return Span(
        name=f"tool.{tool_name}",
        parent_id=parent_span_id,
        attributes={
            "tool.name": tool_name,
            "beat.number": beat_number,
            "span.kind": "tool",
        },
    )


def trace_beat(beat_number: int, time_context: str) -> Span:
    """Create a span for a heartbeat beat."""
    return Span(
        name=f"beat.{beat_number}",
        attributes={
            "beat.number": beat_number,
            "beat.time_context": time_context,
            "span.kind": "heartbeat",
        },
    )


def trace_model_request(model: str, message_preview: str = "") -> Span:
    """Create a span for a model API request."""
    return Span(
        name=f"model.{model}",
        attributes={
            "model.name": model,
            "model.message_preview": message_preview[:100],
            "span.kind": "model",
        },
    )


def get_recent_traces(limit: int = 50) -> list[dict]:
    """Get recent traces from the buffer."""
    return list(_buffer)[-limit:]


def get_active_spans() -> list[dict]:
    """Get currently active (unclosed) spans."""
    return list(_active_spans.values())


def _maybe_flush():
    """Flush buffer to disk when it reaches a threshold."""
    if len(_buffer) < 50:
        return
    try:
        TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_LOG, "a", encoding="utf-8") as f:
            while _buffer:
                entry = _buffer.popleft()
                f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        logger.debug(f"Trace flush failed: {e}")


def flush_all():
    """Force flush all buffered traces."""
    if not _buffer:
        return
    try:
        TRACE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACE_LOG, "a", encoding="utf-8") as f:
            while _buffer:
                entry = _buffer.popleft()
                f.write(json.dumps(entry, default=str) + "\n")
    except Exception as e:
        logger.debug(f"Trace flush failed: {e}")
