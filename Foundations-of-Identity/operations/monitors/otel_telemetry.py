"""T2.G v0: OpenTelemetry telemetry helper for monitor instrumentation.

Shared OTel setup module used by M1, M6, and (extensible to) other monitors.
Emits metrics to a local file in OTLP-compatible JSON-lines format. Each
monitor invocation appends its metrics as one or more JSON records to
memory/otel_metrics.jsonl. External tools (OTel collectors, observability
platforms, custom dashboards) can tail/parse this file.

For v0 we use file-based emission rather than a network collector because
(a) no collector currently runs in the daemon, (b) file-based is the
zero-dependency reliable path, (c) collector integration is a discrete
future iteration.

Metric format follows OTLP JSON encoding for metrics:
{
  "resource": {"attributes": {...}},
  "scope_metrics": [{
    "scope": {"name": "...", "version": "..."},
    "metrics": [{...}]
  }]
}

Integrated implementation plan #11 (Tier 2 T2.G). Builds on M1/M6.
"""
import json
import os
import socket
import time
from datetime import datetime
from pathlib import Path

CLAWD = Path(r"C:\Users\mercu\clawd")
OTEL_METRICS_PATH = CLAWD / "memory" / "otel_metrics.jsonl"


class MonitorTelemetry:
    """Per-monitor telemetry collector. Buffers metrics in-memory during a
    monitor run, then flushes to OTEL_METRICS_PATH as a single OTLP-format
    JSON record when emit() is called.

    Usage:
        tel = MonitorTelemetry(monitor_name="M1", monitor_version="v0.1.0")
        tel.counter("channels_checked", 6)
        tel.gauge("channels_silent", 1)
        tel.histogram("check_duration_seconds", 0.066)
        tel.counter("cross_correlation_signatures_fired", 1,
                    attributes={"signature": "selective_channel_death"})
        tel.emit()
    """

    def __init__(self, monitor_name: str, monitor_version: str = "v0.1.0",
                 service_name: str = "clawd.monitors"):
        self.monitor_name = monitor_name
        self.monitor_version = monitor_version
        self.service_name = service_name
        self.metrics = []
        self.start_ts = datetime.now()
        self.start_unix_nano = int(self.start_ts.timestamp() * 1_000_000_000)

    def counter(self, name: str, value: int, attributes: dict = None,
                description: str = ""):
        self.metrics.append({
            "name": f"{self.monitor_name}.{name}",
            "description": description,
            "unit": "1",
            "sum": {
                "data_points": [{
                    "attributes": _attrs(attributes or {}),
                    "start_time_unix_nano": self.start_unix_nano,
                    "time_unix_nano": int(time.time() * 1_000_000_000),
                    "as_int": value,
                }],
                "aggregation_temporality": 2,  # CUMULATIVE
                "is_monotonic": True,
            },
        })

    def gauge(self, name: str, value: float, attributes: dict = None,
              description: str = "", unit: str = "1"):
        self.metrics.append({
            "name": f"{self.monitor_name}.{name}",
            "description": description,
            "unit": unit,
            "gauge": {
                "data_points": [{
                    "attributes": _attrs(attributes or {}),
                    "time_unix_nano": int(time.time() * 1_000_000_000),
                    "as_double": float(value),
                }],
            },
        })

    def histogram(self, name: str, value: float, attributes: dict = None,
                  description: str = "", unit: str = "s"):
        self.metrics.append({
            "name": f"{self.monitor_name}.{name}",
            "description": description,
            "unit": unit,
            "histogram": {
                "data_points": [{
                    "attributes": _attrs(attributes or {}),
                    "start_time_unix_nano": self.start_unix_nano,
                    "time_unix_nano": int(time.time() * 1_000_000_000),
                    "count": 1,
                    "sum": value,
                    "bucket_counts": [1],
                    "explicit_bounds": [],
                }],
                "aggregation_temporality": 2,
            },
        })

    def emit(self) -> None:
        if not self.metrics:
            return
        record = {
            "resource": {
                "attributes": _attrs({
                    "service.name": self.service_name,
                    "service.version": self.monitor_version,
                    "host.name": socket.gethostname(),
                    "monitor.name": self.monitor_name,
                    "process.pid": os.getpid(),
                }),
            },
            "scope_metrics": [{
                "scope": {
                    "name": f"clawd.monitor.{self.monitor_name.lower()}",
                    "version": self.monitor_version,
                },
                "metrics": self.metrics,
            }],
            "emitted_at": datetime.now().isoformat(),
        }
        OTEL_METRICS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(OTEL_METRICS_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")


def _attrs(d: dict) -> list:
    """Convert dict to OTLP attributes list format."""
    out = []
    for k, v in d.items():
        if isinstance(v, bool):
            out.append({"key": str(k), "value": {"bool_value": v}})
        elif isinstance(v, int):
            out.append({"key": str(k), "value": {"int_value": v}})
        elif isinstance(v, float):
            out.append({"key": str(k), "value": {"double_value": v}})
        else:
            out.append({"key": str(k), "value": {"string_value": str(v)}})
    return out


# ============================================================================
# Reader helpers (for verification / downstream tools)
# ============================================================================

def read_metrics(monitor_name: str = None, last_n: int = None) -> list:
    """Read OTLP metrics records from the metrics file.

    Filters by monitor_name if given; limits to last_n records if given.
    """
    if not OTEL_METRICS_PATH.exists():
        return []
    out = []
    with open(OTEL_METRICS_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                if monitor_name:
                    # Filter on resource.monitor.name
                    res_attrs = {a["key"]: a["value"] for a in rec.get("resource", {}).get("attributes", [])}
                    mn = res_attrs.get("monitor.name", {}).get("string_value", "")
                    if mn != monitor_name:
                        continue
                out.append(rec)
            except json.JSONDecodeError:
                continue
    if last_n:
        out = out[-last_n:]
    return out


if __name__ == "__main__":
    # Self-test: emit some sample metrics and read them back
    import sys
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    print("=== otel_telemetry.py self-test ===")
    tel = MonitorTelemetry(monitor_name="SELF_TEST", monitor_version="v0.1.0")
    tel.counter("test_counter", 42, description="self-test counter")
    tel.gauge("test_gauge", 3.14, description="self-test gauge")
    tel.histogram("test_histogram_seconds", 0.123, description="self-test histogram")
    tel.counter("typed_counter", 1, attributes={"signature": "self_test"})
    tel.emit()
    print(f"  Emitted 4 metrics for SELF_TEST")

    recs = read_metrics(monitor_name="SELF_TEST", last_n=1)
    if recs:
        rec = recs[-1]
        n_metrics = sum(len(sm.get("metrics", [])) for sm in rec.get("scope_metrics", []))
        print(f"  Last SELF_TEST record has {n_metrics} metrics")
        for sm in rec.get("scope_metrics", []):
            for m in sm.get("metrics", []):
                print(f"    {m['name']}  ({list(m.keys())[3]})")
    else:
        print("  FAIL: no SELF_TEST records found after emission")
