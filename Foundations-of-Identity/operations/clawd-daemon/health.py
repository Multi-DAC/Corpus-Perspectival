"""
Health Check System — Probes subsystems and alerts on failures.

Checks Claude CLI and Telegram connectivity.
Sends alerts to Clayton via Telegram on status transitions.
Updates the router's circuit breaker directly.
"""
import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Optional

import config

logger = logging.getLogger("clawd.health")


@dataclass
class SubsystemStatus:
    name: str
    healthy: bool = True
    last_check: float = 0.0
    last_error: str = ""
    consecutive_failures: int = 0


class HealthChecker:
    """Periodic health checks for all subsystems."""

    def __init__(self, router, telegram_bot=None):
        self.router = router
        self.telegram_bot = telegram_bot
        self.running = False
        self._task: Optional[asyncio.Task] = None
        self._statuses: dict[str, SubsystemStatus] = {
            "claude_cli": SubsystemStatus(name="Claude Code CLI"),
            "telegram": SubsystemStatus(name="Telegram Bot"),
        }
        # Initialize all as healthy (assume working until proven otherwise)
        for status in self._statuses.values():
            status.healthy = True
            status.last_check = time.time()

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Health checker started: every {config.HEALTH_CHECK_INTERVAL}s")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Health checker stopped.")

    async def _loop(self):
        # Initial check after 30s (let everything start up first)
        await asyncio.sleep(30)
        while self.running:
            try:
                await self._check_all()
            except Exception as e:
                logger.error(f"Health check error: {e}", exc_info=True)
            await asyncio.sleep(config.HEALTH_CHECK_INTERVAL)

    async def _check_all(self):
        """Run all health checks concurrently."""
        checks = [
            self._check_claude_cli(),
            self._check_telegram(),
        ]
        await asyncio.gather(*checks, return_exceptions=True)

    async def _check_claude_cli(self):
        """Check Claude Code CLI availability."""
        key = "claude_cli"
        try:
            proc = await asyncio.create_subprocess_exec(
                config.CLAUDE_BIN, "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=10)
            if proc.returncode == 0:
                await self._update_status(key, healthy=True)
            else:
                stderr_text = stderr.decode("utf-8", errors="replace")[:200] if stderr else ""
                await self._update_status(
                    key, healthy=False,
                    error=f"Exit code {proc.returncode}: {stderr_text}"
                )
        except FileNotFoundError as e:
            await self._update_status(key, healthy=False, error=f"CLI not found ({config.CLAUDE_BIN}): {e}")
        except asyncio.TimeoutError:
            await self._update_status(key, healthy=False, error="Timed out")
        except Exception as e:
            await self._update_status(key, healthy=False, error=f"{type(e).__name__}: {e}")

    async def _check_telegram(self):
        """Check Telegram bot connectivity."""
        key = "telegram"
        if not self.telegram_bot or not self.telegram_bot.bot:
            return  # Not initialized
        try:
            me = await asyncio.wait_for(
                self.telegram_bot.bot.get_me(),
                timeout=10,
            )
            if me:
                await self._update_status(key, healthy=True)
            else:
                await self._update_status(key, healthy=False, error="get_me returned None")
        except Exception as e:
            await self._update_status(key, healthy=False, error=str(e))

    async def _update_status(self, key: str, healthy: bool, error: str = ""):
        """Update status and fire alerts on transitions."""
        status = self._statuses[key]
        was_healthy = status.healthy
        status.last_check = time.time()

        if healthy:
            status.healthy = True
            status.last_error = ""
            status.consecutive_failures = 0

            # Recovery alert
            if not was_healthy:
                logger.info(f"[HEALTH RECOVERY] {status.name} is back UP")
                await self._send_alert(f"[HEALTH RECOVERY] {status.name} is back UP")

                # Update circuit breaker for Claude CLI
                if key == "claude_cli":
                    from models import CircuitState
                    self.router.health.force_state("opus", CircuitState.HALF_OPEN)
        else:
            status.consecutive_failures += 1
            status.healthy = False
            status.last_error = error

            # Failure alert (only on transition or every 10th failure)
            if was_healthy or status.consecutive_failures % 10 == 0:
                logger.warning(f"[HEALTH ALERT] {status.name} is DOWN: {error}")
                await self._send_alert(
                    f"[HEALTH ALERT] {status.name} is DOWN: {error}"
                )

                # Update circuit breaker for Claude CLI
                if key == "claude_cli":
                    from models import CircuitState
                    self.router.health.force_state("opus", CircuitState.OPEN)

    async def _send_alert(self, message: str):
        """Send alert to Clayton via Telegram."""
        if self.telegram_bot:
            try:
                await self.telegram_bot.send_to_clayton(message)
            except Exception as e:
                logger.error(f"Failed to send health alert: {e}")

    def get_status_report(self) -> str:
        """Generate a formatted status report for /health command."""
        lines = ["*Clawd Health Status*\n"]
        for key, status in self._statuses.items():
            icon = "OK" if status.healthy else "DOWN"
            age = int(time.time() - status.last_check)
            line = f"`{icon:>4}` | {status.name}"
            if age > 0:
                line += f" (checked {age}s ago)"
            if not status.healthy and status.last_error:
                line += f"\n       Error: {status.last_error}"
            if status.consecutive_failures > 0:
                line += f" (failures: {status.consecutive_failures})"
            lines.append(line)

        # Model circuit breaker status
        lines.append("\n*Model Health:*")
        model_status = self.router.health.get_status()
        for model, info in model_status.items():
            state = info.get("state", "unknown")
            failures = info.get("consecutive_failures", 0)
            icon = "OK" if state == "closed" else ("PROBE" if state == "half_open" else "OPEN")
            lines.append(f"`{icon:>5}` | {model} ({state}, {failures} failures)")

        # Dashboard metrics summary
        try:
            from tools.dashboard import generate_dashboard
            dashboard_data = generate_dashboard("json", 1)
            if isinstance(dashboard_data, str):
                import json
                dashboard_data = json.loads(dashboard_data)
            if isinstance(dashboard_data, dict):
                lines.append("\n*Dashboard Metrics:*")
                if "success_rate" in dashboard_data:
                    lines.append(f"  Success rate: {dashboard_data['success_rate']}")
                if "active_model" in dashboard_data:
                    lines.append(f"  Active model: {dashboard_data['active_model']}")
                if "stall_rate" in dashboard_data:
                    lines.append(f"  Stall rate: {dashboard_data['stall_rate']}")
        except Exception as e:
            logger.debug(f"Dashboard metrics in health report skipped: {e}")

        # WAL size
        try:
            from tools.sqlite_store import DB_PATH
            wal_path = DB_PATH.with_suffix(".db-wal")
            if wal_path.exists():
                wal_size = wal_path.stat().st_size
                lines.append(f"\n*SQLite WAL:* {wal_size / 1024:.1f} KB")
        except Exception as e:
            logger.warning(f"Failed to load SQLite WAL size for health report: {e}")

        return "\n".join(lines)

    async def run_check_now(self) -> str:
        """Run an immediate health check and return the report."""
        await self._check_all()
        return self.get_status_report()
