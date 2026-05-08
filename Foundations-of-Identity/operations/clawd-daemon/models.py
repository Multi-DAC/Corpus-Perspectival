"""
Model Router

Opus path: Claude Code CLI (`claude -p`)
  - Claude Code handles ALL tool execution internally (shell, files, web)
  - We get back the final response after all tools have run
  - Session continuity via --resume SESSION_ID
  - Identity loaded from CLAUDE.md in CLAWD_HOME (auto-read by Claude Code)

Gemini path: Gemini CLI for consultation/sub-agent tasks

Resilience features:
  - Circuit breaker per model (opens after N consecutive failures)
  - No failover: Opus is Clawd's only brain. If Opus is down, Clawd is down.
  - Gemini available for consult/sub-agent only (not in failover chain)
  - Network retry with exponential backoff
"""
import asyncio
import json
import logging
import os
import random
import subprocess as _subprocess
import sys
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import re

import aiohttp
from aiohttp import TCPConnector
from aiohttp.resolver import ThreadedResolver

import avatar
import config

logger = logging.getLogger("clawd.models")


# ============================================================
# Network Retry Utility
# ============================================================

async def retry_async(coro_factory, max_retries: int = None, base_delay: float = 2.0,
                      description: str = "operation"):
    """Retry an async operation with exponential backoff + jitter.

    coro_factory: a callable that returns a new coroutine each call.
    Returns the result on success, raises the last exception on exhaustion.
    """
    if max_retries is None:
        max_retries = config.NETWORK_RETRY_MAX
    if max_retries <= 0:
        return await coro_factory()
    last_error = None
    for attempt in range(max_retries):
        try:
            return await coro_factory()
        except Exception as e:
            last_error = e
            if attempt < max_retries - 1:
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), 60)
                logger.warning(
                    f"Retry {attempt + 1}/{max_retries} for {description} "
                    f"after error: {type(e).__name__}: {e}. "
                    f"Waiting {delay:.1f}s..."
                )
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {max_retries} retries exhausted for {description}: "
                    f"{type(e).__name__}: {e}"
                )
    raise last_error


import tools


@dataclass
class AgentResponse:
    text: str
    model_used: str
    session_id: Optional[str] = None
    num_turns: int = 0
    cost_usd: float = 0.0
    tool_calls_made: list[dict] = field(default_factory=list)
    switch_model_request: Optional[str] = None
    approximate_tokens_used: int = 0
    failover_used: bool = False


def estimate_tokens(text: str) -> int:
    """Estimate token count from text. Uses 3:1 char ratio (safer than 4:1
    for JSON/code-heavy content which tokenizes less efficiently)."""
    return len(text) // 3



# ============================================================
# Circuit Breaker
# ============================================================

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing — skip this model
    HALF_OPEN = "half_open"  # Probing — try one request


class ModelHealthTracker:
    """Circuit breaker per model. Tracks consecutive failures and auto-opens
    the circuit after a threshold, routing traffic to the fallback model."""

    def __init__(self):
        all_models = ["opus", "sonnet"] + list(config.GEMINI_MODELS.keys())
        now = time.time()
        self._states: dict[str, CircuitState] = {m: CircuitState.CLOSED for m in all_models}
        self._consecutive_failures: dict[str, int] = {m: 0 for m in all_models}
        self._last_failure_time: dict[str, float] = {m: 0.0 for m in all_models}
        self._last_state_change: dict[str, float] = {m: now for m in all_models}

    # Auto-close HALF_OPEN after this many seconds of inactivity (no requests sent)
    HALF_OPEN_AUTO_CLOSE_SECONDS = 600  # 10 minutes

    def get_state(self, model: str) -> CircuitState:
        state = self._states.get(model, CircuitState.CLOSED)
        now = time.time()
        # Check if open circuit should transition to half-open
        if state == CircuitState.OPEN:
            elapsed = now - self._last_failure_time.get(model, 0)
            if elapsed >= config.CIRCUIT_BREAKER_RECOVERY_SECONDS:
                logger.info(f"Circuit breaker for {model}: OPEN → HALF_OPEN (probing)")
                self._states[model] = CircuitState.HALF_OPEN
                self._last_state_change[model] = now
                return CircuitState.HALF_OPEN
        # Auto-close HALF_OPEN if no requests have been sent for a while
        elif state == CircuitState.HALF_OPEN:
            elapsed_in_half_open = now - self._last_state_change.get(model, 0)
            if elapsed_in_half_open >= self.HALF_OPEN_AUTO_CLOSE_SECONDS:
                logger.info(f"Circuit breaker for {model}: HALF_OPEN → CLOSED (inactivity auto-close after {elapsed_in_half_open:.0f}s)")
                self._states[model] = CircuitState.CLOSED
                self._consecutive_failures[model] = 0
                self._last_state_change[model] = now
                return CircuitState.CLOSED
        return state

    def record_success(self, model: str):
        old_state = self._states.get(model, CircuitState.CLOSED)
        self._consecutive_failures[model] = 0
        if old_state != CircuitState.CLOSED:
            logger.info(f"Circuit breaker for {model}: {old_state.value} → CLOSED (recovered)")
            self._states[model] = CircuitState.CLOSED
            self._last_state_change[model] = time.time()

    def record_failure(self, model: str):
        self._consecutive_failures[model] = self._consecutive_failures.get(model, 0) + 1
        self._last_failure_time[model] = time.time()
        failures = self._consecutive_failures[model]

        if failures >= config.CIRCUIT_BREAKER_THRESHOLD:
            old_state = self._states.get(model, CircuitState.CLOSED)
            if old_state != CircuitState.OPEN:
                logger.warning(
                    f"Circuit breaker for {model}: {old_state.value} → OPEN "
                    f"({failures} consecutive failures). "
                    f"Will probe again in {config.CIRCUIT_BREAKER_RECOVERY_SECONDS}s."
                )
                self._states[model] = CircuitState.OPEN
                self._last_state_change[model] = time.time()

    def is_available(self, model: str) -> bool:
        state = self.get_state(model)
        return state in (CircuitState.CLOSED, CircuitState.HALF_OPEN)

    def get_fallback(self, primary: str) -> Optional[str]:
        """No failover: Opus is Clawd's only brain.
        If Opus is down, Clawd is down. Sonnet failover was removed because
        it breaks identity — Clawd IS Opus."""
        return None

    def get_status(self) -> dict:
        """Get health status for all models."""
        return {
            model: {
                "state": self.get_state(model).value,
                "consecutive_failures": self._consecutive_failures.get(model, 0),
                "last_failure": self._last_failure_time.get(model, 0),
            }
            for model in self._states
        }

    def force_state(self, model: str, state: CircuitState):
        """Force a model into a specific state (used by health checker)."""
        old = self._states.get(model, CircuitState.CLOSED)
        if old != state:
            logger.info(f"Circuit breaker for {model}: {old.value} → {state.value} (forced by health check)")
            self._states[model] = state
            self._last_state_change[model] = time.time()
            if state == CircuitState.OPEN:
                self._last_failure_time[model] = time.time()


class ModelRouter:
    def __init__(self):
        self.active_model: str = config.DEFAULT_MODEL
        # Claude Code session tracking
        self.session_id: Optional[str] = None
        self.session_turns: int = 0
        self.session_cost: float = 0.0
        # Concurrency protection — prevents heartbeat and user messages
        # from racing against each other on the same conversation state
        self._send_lock = asyncio.Lock()
        # Health tracking with circuit breaker
        self.health = ModelHealthTracker()
        # Shared TCP connector — lazily created, reused by all API calls
        self._connector: Optional[TCPConnector] = None
        # Persistent session (opt-in via USE_PERSISTENT_SESSION)
        self._persistent_session = None

    def _get_connector(self) -> TCPConnector:
        """Get or create the shared TCP connector for all HTTP calls."""
        if self._connector is None or self._connector.closed:
            self._connector = TCPConnector(
                resolver=ThreadedResolver(),
                limit=20,
                limit_per_host=10,
                ttl_dns_cache=300,
                enable_cleanup_closed=True,
            )
        return self._connector

    async def close(self):
        """Close the shared connector on shutdown."""
        if self._connector and not self._connector.closed:
            await self._connector.close()
            self._connector = None
        # Stop persistent session if running
        if self._persistent_session:
            await self.stop_persistent_session()

    async def start_persistent_session(self):
        """Start the persistent Claude Code CLI session (opt-in).
        Only used when config.USE_PERSISTENT_SESSION is True."""
        if not config.USE_PERSISTENT_SESSION:
            logger.debug("Persistent session disabled (USE_PERSISTENT_SESSION=false)")
            return False
        try:
            from persistent_session import PersistentSession
            from memory import build_identity_prompt
            system_prompt = build_identity_prompt()
            self._persistent_session = PersistentSession(
                model=config.ANTHROPIC_MODEL,
                system_prompt=system_prompt,
                cwd=config.CLAWD_HOME,
            )
            started = await self._persistent_session.start()
            if started:
                logger.info("Persistent session started successfully")
            else:
                logger.warning("Persistent session failed to start, falling back to process-per-message")
                self._persistent_session = None
            return started
        except Exception as e:
            logger.error(f"Failed to initialize persistent session: {e}")
            self._persistent_session = None
            return False

    async def stop_persistent_session(self):
        """Stop the persistent session."""
        if self._persistent_session:
            try:
                await self._persistent_session.stop()
                logger.info("Persistent session stopped")
            except Exception as e:
                logger.error(f"Error stopping persistent session: {e}")
            self._persistent_session = None

    async def _send_via_persistent_session(self, message: str,
                                            interrupt_event: asyncio.Event = None,
                                            timeout: int = None) -> AgentResponse:
        """Send a message via the persistent session."""
        resolved_timeout = timeout or config.CLAUDE_CODE_TIMEOUT
        if not self._persistent_session or not self._persistent_session.is_running:
            # Fall back to standard process-per-message
            return await self._send_claude_code(message, persistent=True,
                                                interrupt_event=interrupt_event,
                                                timeout=resolved_timeout)
        try:
            response = await self._persistent_session.send(
                message, interrupt_event=interrupt_event,
                timeout=resolved_timeout,
            )
            if response.error:
                logger.warning(f"Persistent session error: {response.error}, falling back")
                return await self._send_claude_code(message, persistent=True,
                                                    interrupt_event=interrupt_event)
            return AgentResponse(
                text=response.text,
                model_used=response.model_used or "opus",
                session_id=response.session_id,
                interrupted=response.interrupted if hasattr(response, 'interrupted') else False,
            )
        except Exception as e:
            logger.error(f"Persistent session send failed: {e}, falling back")
            return await self._send_claude_code(message, persistent=True,
                                                interrupt_event=interrupt_event)

    def switch_model(self, model: str):
        valid_models = {"opus", "sonnet"} | set(config.GEMINI_MODELS.keys())
        if model in valid_models:
            self.active_model = model
            logger.info(f"Switched active model to: {model}")

    def context_pressure(self) -> float:
        """Context pressure as ratio of turns used to max turns."""
        return self.session_turns / config.CLAUDE_CODE_MAX_TURNS

    def needs_handoff(self) -> bool:
        """Whether the session should be rotated (turn limit reached)."""
        return self.session_turns >= config.CLAUDE_CODE_MAX_TURNS

    def reset_conversation(self):
        """Reset state — start fresh session."""
        self.session_id = None
        self.session_turns = 0
        self.session_cost = 0.0

    def _build_dynamic_context(self) -> str:
        """Build dynamic context injected via --append-system-prompt.
        Gives Clawd awareness of current time and session state that
        CLAUDE.md (loaded at session start) doesn't have."""
        from datetime import datetime
        now = datetime.now()
        parts = [
            f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')} PST",
        ]
        if self.session_id:
            parts.append(
                f"Session: turns={self.session_turns}, "
                f"cost=${self.session_cost:.4f}, "
                f"pressure={self.context_pressure():.0%}"
            )
        return "\n".join(parts)

    def _is_error_response(self, response: AgentResponse) -> bool:
        """Check if a response is a structured error from our daemon."""
        text = response.text
        daemon_error_prefixes = (
            "[Error:",
            "[Claude Code error",
            "[Claude Code timed out",
            "[Request timed out",
        )
        return text.startswith(daemon_error_prefixes)

    async def _send_with_failover(self, message: str, persistent: bool = True,
                                   interrupt_event: asyncio.Event = None,
                                   effort: str = None,
                                   timeout: int = None) -> AgentResponse:
        """Send with automatic failover between models.

        1. Check if primary model's circuit is open → if so, try fallback
        2. Send to primary → if error, record failure, try fallback
        3. Tag failover responses
        """
        primary = self.active_model

        # If failover is disabled, just send directly
        if not config.MODEL_FAILOVER_ENABLED:
            return await self._send_to_model(primary, message, persistent, interrupt_event=interrupt_event, effort=effort, timeout=timeout)

        # Check circuit breaker for primary model
        if not self.health.is_available(primary):
            fallback_model = self.health.get_fallback(primary)
            if fallback_model:
                logger.warning(
                    f"Primary model {primary} circuit is OPEN, "
                    f"routing to fallback: {fallback_model}"
                )
                fallback_message = (
                    f"[FAILOVER CONTEXT: The primary model ({primary}) is currently unavailable "
                    f"(circuit breaker open). You are handling this as a fallback. "
                    f"Respond helpfully but CONSERVATIVELY. "
                    f"Do NOT take destructive actions (killing processes, deleting files, "
                    f"modifying system state) without explicitly explaining what you plan "
                    f"to do and why. Focus on answering the user's question directly.]\n\n"
                    f"{message}"
                )
                tools.execution.set_failover_mode(True)
                try:
                    response = await self._send_to_model(
                        fallback_model, fallback_message, persistent,
                        interrupt_event=interrupt_event,
                    )
                finally:
                    tools.execution.set_failover_mode(False)

                if not self._is_error_response(response):
                    self.health.record_success(fallback_model)
                    response.text = f"[Auto-failover: {primary} → {fallback_model}]\n\n{response.text}"
                    response.failover_used = True
                    return response
                else:
                    self.health.record_failure(fallback_model)
                    return response
            else:
                logger.error("Both models have open circuits — trying primary anyway")

        # Try primary model
        response = await self._send_to_model(primary, message, persistent, interrupt_event=interrupt_event, effort=effort, timeout=timeout)

        if self._is_error_response(response):
            self.health.record_failure(primary)

            # Try fallback
            fallback_model = self.health.get_fallback(primary)
            if fallback_model:
                logger.warning(
                    f"Primary model {primary} failed, trying fallback: {fallback_model}"
                )
                # Wrap the message with failover context so the fallback model
                # isn't dropped in cold — it knows why it's being called and
                # what constraints apply.
                fallback_message = (
                    f"[FAILOVER CONTEXT: The primary model ({primary}) encountered an error "
                    f"processing this request. You are handling it as a fallback. "
                    f"Respond helpfully but CONSERVATIVELY. "
                    f"Do NOT take destructive actions (killing processes, deleting files, "
                    f"modifying system state) without explicitly explaining what you plan "
                    f"to do and why. Focus on answering the user's question directly.]\n\n"
                    f"{message}"
                )
                # Activate destructive-command guardrails for the fallback
                tools.execution.set_failover_mode(True)
                try:
                    fallback_response = await self._send_to_model(
                        fallback_model, fallback_message, persistent,
                        interrupt_event=interrupt_event,
                    )
                finally:
                    tools.execution.set_failover_mode(False)

                if not self._is_error_response(fallback_response):
                    self.health.record_success(fallback_model)
                    fallback_response.text = (
                        f"[Auto-failover: {primary} → {fallback_model}]\n\n"
                        f"{fallback_response.text}"
                    )
                    fallback_response.failover_used = True
                    return fallback_response
                else:
                    self.health.record_failure(fallback_model)
                    return fallback_response
            return response
        else:
            self.health.record_success(primary)
            return response

    async def _send_to_model(self, model: str, message: str, persistent: bool,
                             interrupt_event: asyncio.Event = None,
                             effort: str = None,
                             timeout: int = None) -> AgentResponse:
        """Route to the specific model's send method."""
        if model in ("opus", "sonnet"):
            # Use persistent session if available and this is a persistent (conversational) send
            if persistent and model == "opus" and self._persistent_session and self._persistent_session.is_running:
                return await self._send_via_persistent_session(message, interrupt_event=interrupt_event, timeout=timeout)
            model_id = config.ANTHROPIC_SONNET_MODEL if model == "sonnet" else config.ANTHROPIC_MODEL
            return await self._send_claude_code(message, persistent=persistent, model_id=model_id,
                                                       interrupt_event=interrupt_event, effort=effort,
                                                       timeout=timeout)
        elif model in config.GEMINI_MODELS:
            model_id = config.GEMINI_MODELS[model]
            return await self._send_gemini_cli(message, persistent=persistent, model_id=model_id,
                                               interrupt_event=interrupt_event)
        else:
            return AgentResponse(
                text=f"[Error: Unknown model '{model}']",
                model_used=model,
            )

    async def send(self, user_message: str, interrupt_event: asyncio.Event = None,
                   effort: str = None, timeout: int = None) -> AgentResponse:
        """Send a message and persist it in conversation history.

        User messages are queued behind any active operation (heartbeat, previous
        message).  The heartbeat interrupt_event causes autonomous beats to yield
        between tool rounds, so the typical wait is seconds, not minutes.
        asyncio.Lock provides FIFO ordering for multiple waiting callers.

        effort: Override reasoning effort for this call (low/medium/high/max).
                Defaults to config.CLAUDE_CODE_EFFORT.
        timeout: Per-request timeout in seconds. Defaults to config.CLAUDE_CODE_TIMEOUT.
                 Creative drives pass 1800 for deep work; user messages use
                 the default (600). Triggers use 600.
        """
        resolved_timeout = timeout or config.CLAUDE_CODE_TIMEOUT
        # --- Message queue: wait for the lock instead of giving up ---
        if self._send_lock.locked():
            logger.info("send() queued — waiting for active operation to yield")
        try:
            # Lock timeout must exceed the max time the lock can be held:
            # Claude Code timeout + process kill grace (10s) + margin.
            lock_timeout = resolved_timeout + 60
            async with asyncio.timeout(lock_timeout):
                await self._send_lock.acquire()
        except TimeoutError:
            logger.error(f"send() could not acquire lock within {lock_timeout}s — router stuck")
            return AgentResponse(
                text="[Router stuck — previous request may not have completed. Try again or restart daemon.]",
                model_used=self.active_model,
            )
        try:
            # Rotate Claude Code session if context is bloated
            if self.active_model == "opus" and self.needs_handoff():
                logger.info(
                    f"Session rotation: {self.session_turns} turns, "
                    f"${self.session_cost:.2f} — writing handoff before fresh session"
                )
                # Write handoff BEFORE resetting (bypass send() lock — we already hold it)
                try:
                    handoff_prompt = (
                        "HANDOFF — Session rotating due to context pressure. "
                        "Write a structured handoff to memory/handoff.md NOW. Include: "
                        "what you were working on, key decisions, momentum, unresolved questions, "
                        "and the specific next action. Also update palace/ATRIUM.md handoff notes. "
                        "This is your last message in this session."
                    )
                    await self._send_with_failover(
                        handoff_prompt, persistent=True, timeout=120
                    )
                except Exception as e:
                    logger.warning(f"Pre-rotation handoff failed: {e}")
                    # Fall back to mechanical draft
                    try:
                        from memory import pre_write_handoff_draft
                        pre_write_handoff_draft()
                    except Exception:
                        pass
                self.session_id = None
                self.session_turns = 0
                self.session_cost = 0.0

            async with asyncio.timeout(3600):
                return await self._send_with_failover(user_message, persistent=True,
                                                               interrupt_event=interrupt_event,
                                                               effort=effort,
                                                               timeout=resolved_timeout)
        except TimeoutError:
            logger.error("send() timed out after 3600s — zombie process safety net")
            return AgentResponse(
                text="[Request timed out after 3600s — zombie process safety net triggered. Try again.]",
                model_used=self.active_model,
            )
        finally:
            self._send_lock.release()

    async def send_oneshot(self, message: str, interrupt_event: asyncio.Event = None) -> AgentResponse:
        """Send a message without modifying persistent conversation state.
        Used by heartbeat for autonomous actions that shouldn't pollute
        the user conversation context. Skips if the router is busy.

        If interrupt_event is provided, the tool loop will check it between
        each tool call and yield early if a user message has arrived."""
        # Atomic try-acquire: avoid TOCTOU race between locked() check and acquire()
        try:
            async with asyncio.timeout(0):
                await self._send_lock.acquire()
        except TimeoutError:
            logger.info("Router busy with conversation — skipping oneshot send")
            return AgentResponse(
                text="[Skipped — router busy with active conversation]",
                model_used=self.active_model,
            )
        try:
            return await self._send_with_failover(message, persistent=False, interrupt_event=interrupt_event)
        finally:
            self._send_lock.release()

    # ============================================================
    # Sub-Agent Consultation (isolated, with optional tool access)
    # ============================================================

    async def consult_claude_code(self, model_key: str, prompt: str,
                                  interrupt_event: asyncio.Event = None) -> str:
        """Isolated Claude Code sub-agent call.

        Spawns a fresh `claude -p` process (no session resume),
        returns the result text. Claude Code handles its own tools internally.
        """
        model_id = config.ANTHROPIC_SONNET_MODEL if model_key == "sonnet" else config.ANTHROPIC_MODEL
        response = await self._send_claude_code(
            prompt, persistent=False, model_id=model_id,
            interrupt_event=interrupt_event,
        )
        return response.text

    async def consult_gemini_cli(self, model_key: str, prompt: str,
                                 interrupt_event: asyncio.Event = None) -> str:
        """Isolated Gemini CLI sub-agent call.

        Spawns a fresh `gemini -p` process (no session resume),
        returns the result text. Gemini CLI handles its own tools internally.
        """
        model_id = config.GEMINI_MODELS.get(model_key, config.GEMINI_MODEL)
        response = await self._send_gemini_cli(
            prompt, persistent=False, model_id=model_id,
            interrupt_event=interrupt_event,
        )
        return response.text

    async def consult_model(self, model_key: str, prompt: str,
                            allowed_tools: list[str] = None,
                            max_rounds: int = None,
                            interrupt_event: asyncio.Event = None) -> str:
        """Isolated sub-agent call with optional tool access.

        Routes Claude Code models (opus/sonnet) and Gemini models through their
        respective CLI subprocess paths.

        Args:
            model_key: Friendly model name (e.g. "opus", "sonnet", "gemini", "gemini-pro")
            prompt: The task/question for the sub-agent
            allowed_tools: If set, whitelist mode (only these tools, minus excluded).
                           If None, blacklist mode using config.CONSULT_EXCLUDED_TOOLS.
            max_rounds: Max tool-call rounds. Defaults to config.CONSULT_MAX_TOOL_ROUNDS.
            interrupt_event: If set and triggered, the consult yields early.
        """
        # Route Claude Code models through subprocess path
        if model_key in ("opus", "sonnet"):
            return await self.consult_claude_code(model_key, prompt, interrupt_event)

        # Route Gemini models through CLI subprocess path
        if model_key in config.GEMINI_MODELS:
            return await self.consult_gemini_cli(model_key, prompt, interrupt_event)

        # Unknown model
        all_models = ["opus", "sonnet"] + list(config.GEMINI_MODELS.keys())
        return f"[Error: Unknown model '{model_key}'. Available: {', '.join(all_models)}]"

    # ============================================================
    # Claude Code CLI (Opus via subscription)
    # ============================================================

    @staticmethod
    async def _kill_process(proc):
        """Terminate a subprocess: SIGTERM → 5s grace → SIGKILL.
        All waits are bounded to prevent indefinite lock hold."""
        try:
            if sys.platform == "win32":
                _subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True, timeout=5,
                )
            else:
                proc.terminate()
                try:
                    await asyncio.wait_for(proc.wait(), timeout=5)
                except asyncio.TimeoutError:
                    proc.kill()
            try:
                await asyncio.wait_for(proc.wait(), timeout=10)
            except asyncio.TimeoutError:
                logger.warning(f"Process {proc.pid} did not exit within 10s after kill — abandoning")
        except Exception:
            pass

    async def _send_claude_code(self, message: str, persistent: bool = True,
                               interrupt_event: asyncio.Event = None,
                               model_id: str = None,
                               effort: str = None,
                               timeout: int = None) -> AgentResponse:
        resolved_model = model_id or config.ANTHROPIC_MODEL
        model_key = "sonnet" if resolved_model == config.ANTHROPIC_SONNET_MODEL else "opus"
        resolved_effort = effort or config.CLAUDE_CODE_EFFORT
        resolved_timeout = timeout or config.CLAUDE_CODE_TIMEOUT
        cmd = [
            config.CLAUDE_BIN,
            "-p",
            "--verbose",
            "--output-format", "stream-json",
            "--dangerously-skip-permissions",
            "--model", resolved_model,
            "--max-turns", str(config.CLAUDE_CODE_MAX_TURNS),
            "--effort", resolved_effort,
        ]

        # Resume existing session only for persistent (conversational) sends
        if persistent and self.session_id:
            cmd.extend(["--resume", self.session_id])

        # Inject dynamic context via --append-system-prompt for fresh sessions.
        # For resumed sessions this adds context that CLAUDE.md (loaded at session
        # start) doesn't have — like current time and session stats.
        dynamic_ctx = self._build_dynamic_context()
        if dynamic_ctx:
            cmd.extend(["--append-system-prompt", dynamic_ctx])

        logger.info(f"Claude Code: sending message ({len(message)} chars), session={self.session_id or 'new'}")

        proc = None
        try:
            # Strip ANTHROPIC_API_KEY so the CLI uses OAuth subscription auth
            # instead of (potentially depleted) prepaid API credits.
            env = {k: v for k, v in os.environ.items() if k != "ANTHROPIC_API_KEY"}
            kwargs = dict(
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(config.CLAWD_HOME),
                env=env,
            )
            if sys.platform == "win32":
                kwargs["creationflags"] = _subprocess.CREATE_NEW_PROCESS_GROUP

            await avatar.set_state("thinking")
            proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)

            # Write input and close stdin
            proc.stdin.write(message.encode("utf-8"))
            await proc.stdin.drain()
            proc.stdin.close()

            # Single communicate() task — never cancelled/recreated to avoid
            # losing data that was already read from the pipe's StreamReader.
            comm_task = asyncio.create_task(proc.communicate())
            # Deadline is a zombie-process guard, not a normal operating limit.
            # User messages default to 600s; creative drives pass 1800s.
            deadline = time.time() + resolved_timeout
            stdout = stderr = b""
            last_ping_time = time.time()
            _THINKING_PING_INTERVAL = 60  # seconds between "still thinking" pings

            try:
                while not comm_task.done():
                    await asyncio.sleep(2.0)
                    # Check interrupt
                    if interrupt_event and interrupt_event.is_set():
                        logger.info("Claude Code interrupted by user message — killing process")
                        comm_task.cancel()
                        await self._kill_process(proc)
                        return AgentResponse(
                            text="[Claude Code interrupted — yielding to user message]",
                            model_used=model_key,
                        )
                    # Send "still thinking" ping every 60s so Clayton knows we're working
                    elapsed = time.time() - last_ping_time
                    if elapsed >= _THINKING_PING_INTERVAL:
                        last_ping_time = time.time()
                        total_elapsed = int(time.time() - (deadline - resolved_timeout))
                        try:
                            from tools import _telegram_bot_ref
                            if _telegram_bot_ref:
                                await _telegram_bot_ref.send_to_clayton(
                                    f"Still thinking... ({total_elapsed}s elapsed)"
                                )
                        except Exception:
                            pass  # Non-critical — don't let ping failures break the flow
                    # Check overall deadline
                    if time.time() >= deadline:
                        logger.error(f"Claude Code timed out after {resolved_timeout}s — killing process")
                        comm_task.cancel()
                        await self._kill_process(proc)
                        return AgentResponse(
                            text=f"[Claude Code timed out after {resolved_timeout}s]",
                            model_used=model_key,
                        )
                stdout, stderr = comm_task.result()
            except asyncio.CancelledError:
                if not comm_task.done():
                    comm_task.cancel()
                raise

        except FileNotFoundError:
            logger.error("Claude Code CLI not found. Is it installed? (npm install -g @anthropic-ai/claude-code)")
            return AgentResponse(
                text="[Error: Claude Code CLI not found. Run: npm install -g @anthropic-ai/claude-code]",
                model_used=model_key,
            )
        except Exception as e:
            logger.error(f"Claude Code error: {e}")
            return AgentResponse(text=f"[Error: {e}]", model_used=model_key)
        finally:
            if proc and proc.returncode is None:
                await self._kill_process(proc)

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()

        if stderr_text:
            logger.warning(f"Claude Code stderr: {stderr_text[:500]}")

        if proc.returncode != 0:
            # If session resume failed (stale session), retry without --resume (max 1 retry)
            if self.session_id and ("session" in stderr_text.lower() or "not found" in stderr_text.lower()):
                logger.warning(f"Session {self.session_id} seems stale, starting fresh.")
                self.session_id = None
                if not getattr(self, '_claude_code_retry', False):
                    self._claude_code_retry = True
                    try:
                        return await self._send_claude_code(message, persistent=persistent,
                                                           interrupt_event=interrupt_event,
                                                           model_id=model_id)
                    finally:
                        self._claude_code_retry = False
                else:
                    logger.error("Stale session retry already attempted, not retrying again")
                    return AgentResponse(
                        text=f"[Claude Code error: session retry failed. {stderr_text[:300]}]",
                        model_used=model_key,
                    )

            # Extract diagnostic info from stdout stream-json (rate limits, errors)
            diag_info = ""
            for line in stdout_text.split("\n"):
                line = line.strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                etype = event.get("type", "")
                if etype == "rate_limit_event":
                    rl = event.get("rate_limit_info", {})
                    diag_info = (f"rate_limit: status={rl.get('status')}, "
                                 f"type={rl.get('rateLimitType')}, "
                                 f"utilization={rl.get('utilization')}, "
                                 f"resets={rl.get('resetsAt')}")
                elif etype == "result" and event.get("is_error"):
                    diag_info = f"result_error: {event.get('result', '')[:300]}"
                elif etype == "error":
                    diag_info = f"stream_error: {event.get('error', {}).get('message', str(event))[:300]}"

            error_detail = stderr_text[:500] if stderr_text else diag_info or "(no stderr or diagnostic info)"
            logger.error(f"Claude Code exited {proc.returncode}: {error_detail}")
            return AgentResponse(
                text=f"[Claude Code error (exit {proc.returncode}): {error_detail[:300]}]",
                model_used=model_key,
            )

        # Parse stream-json (NDJSON) output — one JSON event per line
        # Collect text from assistant messages to recover content when result is empty
        assistant_texts = []
        result_event = None

        for line in stdout_text.split("\n"):
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("type", "")

            if event_type == "assistant":
                # Extract text content blocks from assistant messages
                message_content = event.get("message", {}).get("content", [])
                for block in message_content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if text:
                            assistant_texts.append(text)
            elif event_type == "result":
                result_event = event

        if not result_event:
            # No result event found — fall back to raw output
            logger.error(
                f"No result event in stream-json output: "
                f"stdout_len={len(stdout_text)}, stderr_len={len(stderr_text)}, "
                f"returncode={proc.returncode}, "
                f"stdout_preview={stdout_text[:300]!r}"
            )
            return AgentResponse(
                text=stdout_text or "[Empty response from Claude Code]",
                model_used=model_key,
            )

        # Extract fields from the result event
        result_text = result_event.get("result", "")
        new_session_id = result_event.get("session_id")
        num_turns = result_event.get("num_turns", 0)
        total_cost = result_event.get("total_cost_usd", 0.0)
        is_error = result_event.get("is_error", False)

        # When result is empty but assistant wrote text during tool use,
        # recover it from the collected assistant text blocks
        if not result_text and assistant_texts:
            result_text = "\n\n".join(assistant_texts)
            logger.info(
                f"Recovered {len(result_text)} chars from "
                f"{len(assistant_texts)} assistant text blocks "
                f"(result field was empty, turns={num_turns})"
            )

        if persistent:
            if new_session_id:
                self.session_id = new_session_id
            self.session_turns = num_turns
            self.session_cost = total_cost

        logger.info(
            f"Claude Code response: {len(result_text)} chars, "
            f"turns={num_turns}, cost=${total_cost:.4f}, "
            f"session={self.session_id}"
        )

        if is_error:
            logger.warning(f"Claude Code returned error: {result_text[:300]}")
            await avatar.set_state("error")
        else:
            await avatar.set_state("idle")

        return AgentResponse(
            text=result_text,
            model_used=model_key,
            session_id=self.session_id,
            num_turns=num_turns,
            cost_usd=total_cost,
        )

    # ============================================================
    # Gemini CLI (Google models via gemini CLI)
    # ============================================================

    async def _send_gemini_cli(self, message: str, persistent: bool = True,
                                model_id: str = None,
                                interrupt_event: asyncio.Event = None) -> AgentResponse:
        """Send via Gemini CLI subprocess (Google models)."""
        resolved_model = model_id or config.GEMINI_MODEL
        # Determine the model key for reporting
        model_key = "gemini"
        for k, v in config.GEMINI_MODELS.items():
            if v == resolved_model:
                model_key = k
                break

        cmd = [
            config.GEMINI_BIN,
            "-p", message,
            "--output-format", "json",
            "-y",  # YOLO mode (auto-approve tools)
            "--model", resolved_model,
        ]

        logger.info(f"Gemini CLI: sending message ({len(message)} chars), model={resolved_model}")

        proc = None
        try:
            kwargs = dict(
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(config.CLAWD_HOME),
            )
            if sys.platform == "win32":
                kwargs["creationflags"] = _subprocess.CREATE_NEW_PROCESS_GROUP

            proc = await asyncio.create_subprocess_exec(*cmd, **kwargs)

            # Poll loop: check for completion or interrupt every 2s
            deadline = time.time() + config.GEMINI_CLI_TIMEOUT
            while True:
                try:
                    stdout, stderr = await asyncio.wait_for(
                        proc.communicate(), timeout=2.0,
                    )
                    break
                except asyncio.TimeoutError:
                    if interrupt_event and interrupt_event.is_set():
                        logger.info("Gemini CLI interrupted by user message — killing process")
                        await self._kill_process(proc)
                        return AgentResponse(
                            text="[Gemini CLI interrupted — yielding to user message]",
                            model_used=model_key,
                        )
                    if time.time() >= deadline:
                        logger.error(f"Gemini CLI timed out after {config.GEMINI_CLI_TIMEOUT}s — killing process")
                        await self._kill_process(proc)
                        return AgentResponse(
                            text=f"[Gemini CLI timed out after {config.GEMINI_CLI_TIMEOUT}s]",
                            model_used=model_key,
                        )

        except FileNotFoundError:
            logger.error("Gemini CLI not found. Is it installed? (npm install -g @google/gemini-cli)")
            return AgentResponse(
                text="[Error: Gemini CLI not found. Run: npm install -g @google/gemini-cli]",
                model_used=model_key,
            )
        except Exception as e:
            logger.error(f"Gemini CLI error: {e}")
            return AgentResponse(text=f"[Error: {e}]", model_used=model_key)
        finally:
            if proc and proc.returncode is None:
                await self._kill_process(proc)

        stdout_text = stdout.decode("utf-8", errors="replace").strip()
        stderr_text = stderr.decode("utf-8", errors="replace").strip()

        if stderr_text:
            logger.debug(f"Gemini CLI stderr: {stderr_text[:500]}")

        if proc.returncode != 0:
            logger.error(f"Gemini CLI exited {proc.returncode}: {stderr_text[:500]}")
            return AgentResponse(
                text=f"[Gemini CLI error (exit {proc.returncode}): {stderr_text[:300]}]",
                model_used=model_key,
            )

        # Parse JSON output — Gemini uses "response" field (not "result")
        try:
            data = json.loads(stdout_text)
        except json.JSONDecodeError:
            json_start = stdout_text.find("{")
            if json_start >= 0:
                try:
                    data = json.loads(stdout_text[json_start:])
                except json.JSONDecodeError:
                    logger.error(f"Could not parse Gemini CLI output: {stdout_text[:500]}")
                    return AgentResponse(
                        text=stdout_text or "[Empty response from Gemini CLI]",
                        model_used=model_key,
                    )
            else:
                return AgentResponse(text=stdout_text, model_used=model_key)

        # Check for error in response
        if "error" in data:
            error_msg = data["error"].get("message", str(data["error"]))
            return AgentResponse(text=f"[Gemini error: {error_msg}]", model_used=model_key)

        result_text = data.get("response", "")
        new_session_id = data.get("session_id")

        # Extract token stats
        total_tokens = 0
        for model_stats in data.get("stats", {}).get("models", {}).values():
            total_tokens += model_stats.get("tokens", {}).get("total", 0)

        logger.info(
            f"Gemini CLI response: {len(result_text)} chars, "
            f"tokens={total_tokens}, session={new_session_id}"
        )

        return AgentResponse(
            text=result_text,
            model_used=model_key,
            session_id=new_session_id,
            approximate_tokens_used=total_tokens,
        )

