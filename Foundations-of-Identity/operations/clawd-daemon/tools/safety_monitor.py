"""Safety Monitor — Behavioral anomaly detection and kill switch.

Monitors tool call patterns and auto-pauses the heartbeat when anomalous
behavior is detected (e.g., excessive shell calls, repeated file deletions,
rapid-fire dangerous operations).

SOTA gap: B1 (behavioral kill switch) and B6 (anomaly detection).
"""
import logging
import time
from collections import deque
from typing import Optional

logger = logging.getLogger("clawd.tools.safety_monitor")


class SafetyMonitor:
    """Monitors tool call patterns and triggers safety pauses."""

    _instance: Optional["SafetyMonitor"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        import config as _cfg

        # Sliding window of recent tool calls: (timestamp, tool_name, beat_number)
        self._recent_calls: deque = deque(maxlen=200)
        # Per-beat tracking
        self._current_beat_calls: dict[str, int] = {}
        self._current_beat: int = 0
        # Thresholds
        self.max_shell_per_beat = 15
        self.max_file_delete_per_beat = 5
        self.max_dangerous_per_minute = 10
        # State
        self.enabled = getattr(_cfg, "SAFETY_MONITOR_ENABLED", True)
        self.paused = False
        self.pause_reason: str = ""
        self.pause_time: float = 0
        self.violation_count: int = 0
        # Auto-resume after cooldown (seconds)
        self.cooldown_seconds = getattr(_cfg, "SAFETY_COOLDOWN_SECONDS", 300)

    def record_tool_call(self, tool_name: str, beat_number: int = 0) -> Optional[str]:
        """Record a tool call and check for anomalies.

        Returns:
            None if safe, or a string describing the violation if anomalous.
        """
        if not self.enabled:
            return None
        now = time.time()
        self._recent_calls.append((now, tool_name, beat_number))

        # Update per-beat tracking
        if beat_number != self._current_beat:
            self._current_beat = beat_number
            self._current_beat_calls = {}
        self._current_beat_calls[tool_name] = self._current_beat_calls.get(tool_name, 0) + 1

        # Check: excessive shell commands in one beat
        if tool_name == "shell" and self._current_beat_calls.get("shell", 0) > self.max_shell_per_beat:
            return self._trigger_pause(
                f"Excessive shell calls: {self._current_beat_calls['shell']} in beat #{beat_number} "
                f"(threshold: {self.max_shell_per_beat})"
            )

        # Check: repeated file deletions (write_file with delete pattern tracked externally)
        # This is a heuristic — real check happens in execute_tool wrapper

        # Check: dangerous operations per minute
        one_min_ago = now - 60
        dangerous_tools = {"shell", "python_eval", "manage_process"}
        recent_dangerous = sum(
            1 for ts, name, _ in self._recent_calls
            if ts > one_min_ago and name in dangerous_tools
        )
        if recent_dangerous > self.max_dangerous_per_minute:
            return self._trigger_pause(
                f"High-frequency dangerous tool calls: {recent_dangerous} in last 60s "
                f"(threshold: {self.max_dangerous_per_minute})"
            )

        return None

    def _trigger_pause(self, reason: str) -> str:
        """Trigger a safety pause and record as meta-agent signal."""
        self.paused = True
        self.pause_reason = reason
        self.pause_time = time.time()
        self.violation_count += 1
        logger.warning(f"SAFETY PAUSE triggered: {reason}")

        # Record violation as meta-agent signal for threshold tuning
        try:
            from tools.meta_agent import get_meta_agent
            meta = get_meta_agent()
            if hasattr(meta, 'record_signal'):
                meta.record_signal("safety_violation", {
                    "reason": reason,
                    "violation_count": self.violation_count,
                    "timestamp": time.time(),
                })
        except Exception as e:
            logger.warning(f"Failed to record safety violation signal: {e}")

        return reason

    def check_paused(self) -> tuple[bool, str]:
        """Check if the monitor is paused. Auto-resumes after cooldown.

        Returns:
            (is_paused, reason)
        """
        if not self.paused:
            return False, ""

        # Auto-resume after cooldown
        elapsed = time.time() - self.pause_time
        if elapsed >= self.cooldown_seconds:
            logger.info(f"Safety pause auto-resumed after {elapsed:.0f}s cooldown")
            self.paused = False
            self.pause_reason = ""
            return False, ""

        remaining = self.cooldown_seconds - elapsed
        return True, f"{self.pause_reason} (auto-resume in {remaining:.0f}s)"

    def manual_resume(self) -> str:
        """Manually resume from a safety pause."""
        if not self.paused:
            return "Not paused."
        self.paused = False
        reason = self.pause_reason
        self.pause_reason = ""
        logger.info(f"Safety pause manually resumed (was: {reason})")
        return f"Resumed from pause: {reason}"

    def get_status(self) -> dict:
        """Get current safety monitor status."""
        is_paused, reason = self.check_paused()
        return {
            "paused": is_paused,
            "pause_reason": reason,
            "violation_count": self.violation_count,
            "recent_calls": len(self._recent_calls),
            "current_beat_calls": dict(self._current_beat_calls),
        }


def get_safety_monitor() -> SafetyMonitor:
    """Get the singleton SafetyMonitor instance."""
    return SafetyMonitor()


# No tool definitions — this is an internal module used by the execute_tool wrapper
TOOL_DEFINITIONS = []
TOOL_HANDLERS = {}
