"""
Persistent Claude Code CLI Session Manager

Maintains a single long-running Claude Code CLI process and routes all
communication through it. This avoids spawning new processes for every message.

Key insight: We use an interactive REPL-style session where:
1. Process starts once at daemon boot
2. We send messages via stdin with special delimiters
3. Process stays alive between messages
4. Conversation history is maintained in the process

For shutdown: we send a special exit command and wait for graceful termination.

OPT-IN ONLY: Clawd's current --resume approach with structured NDJSON output
is more reliable than heuristic text-based response completion detection.
Set USE_PERSISTENT_SESSION=true to enable.
"""
import asyncio
import json
import logging
import os
import shutil
import sys
import subprocess as _subprocess
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Callable
import tempfile

import config

logger = logging.getLogger("clawd.persistent_session")

# Session ID persisted across daemon restarts
SESSION_ID_FILE = config.CLAWD_HOME / ".claude_session_id"


def get_or_create_session_id() -> str:
    """Get persistent session ID from file or create new one."""
    try:
        if SESSION_ID_FILE.exists():
            session_id = SESSION_ID_FILE.read_text().strip()
            if session_id and len(session_id) == 36:  # UUID format
                return session_id
    except Exception as e:
        logger.debug(f"Failed to read session ID file: {e}")

    session_id = str(uuid.uuid4())
    try:
        SESSION_ID_FILE.write_text(session_id)
        logger.info(f"Created new persistent session ID: {session_id[:8]}...{session_id[-4:]}")
    except Exception as e:
        logger.warning(f"Failed to persist session ID: {e}")

    return session_id


@dataclass
class SessionResponse:
    """Response from the persistent session."""
    text: str = ""
    tool_calls: list[dict] = field(default_factory=list)
    model_used: str = ""
    session_id: Optional[str] = None
    error: Optional[str] = None
    exit_code: Optional[int] = None
    interrupted: bool = False


class PersistentSession:
    """
    Maintains a single persistent Claude Code CLI process.

    The process runs in interactive mode. Messages are sent via stdin,
    responses are read from stdout. The process stays alive between messages,
    maintaining full conversation context in memory.

    Architecture:
    - _start(): Launch process, start _read_loop task
    - _read_loop: Continuously reads stdout, parses responses
    - send(): Writes message to stdin, waits for response via Future
    - _stop(): Sends exit, waits for process termination

    Thread safety:
    - _send_lock ensures only one message is sent at a time
    - _response_future tracks the pending response
    """

    # Special marker to indicate end of response
    RESPONSE_END_MARKER = "\n__CLAUDE_RESPONSE_END__\n"

    def __init__(
        self,
        model: str = None,
        system_prompt: str = None,
        cwd: Path = None,
    ):
        self.model = model or config.ANTHROPIC_MODEL
        self.system_prompt = system_prompt
        self.cwd = cwd or config.CLAWD_HOME
        self._session_id: str = get_or_create_session_id()

        # Process state
        self._process: Optional[asyncio.subprocess.Process] = None
        self._running = False
        self._started = False

        # Communication
        self._response_future: Optional[asyncio.Future] = None
        self._send_lock = asyncio.Lock()
        self._output_buffer = asyncio.Queue(maxsize=100)
        self._read_task: Optional[asyncio.Task] = None

        # Response accumulation
        self._current_response_parts: list[str] = []
        self._current_tool_calls: list[dict] = []

    async def start(self) -> bool:
        """Start the persistent Claude Code CLI process."""
        if self._started:
            logger.warning("Session already started")
            return True

        cmd = [
            config.CLAUDE_BIN,
            "--output-format", "text",
            "--dangerously-skip-permissions",
            "--session-id", self._session_id,
        ]

        # Add system prompt if provided
        if self.system_prompt:
            sys_prompt = self.system_prompt[:50000]
            cmd.extend(["--system-prompt", sys_prompt])

        logger.info(f"Starting persistent session {self._session_id[:8]} with model {self.model}")

        try:
            env = os.environ.copy()
            env.pop("CLAUDECODE", None)

            kwargs = dict(
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.cwd),
            )
            if sys.platform == "win32":
                kwargs["creationflags"] = _subprocess.CREATE_NEW_PROCESS_GROUP

            self._process = await asyncio.create_subprocess_exec(*cmd, **kwargs)
            self._running = True
            self._started = True

            # Start the output reader
            self._read_task = asyncio.create_task(self._read_loop(), name="session_read")

            logger.info(f"Persistent session started (PID {self._process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start persistent session: {e}")
            return False

    async def _read_loop(self):
        """Continuously read stdout and queue output."""
        try:
            while self._running and self._process and self._process.stdout:
                try:
                    chunk = await asyncio.wait_for(
                        self._process.stdout.read(4096),
                        timeout=1.0
                    )
                    if not chunk:
                        logger.info("Session process exited (EOF)")
                        self._running = False
                        if self._response_future is not None and not self._response_future.done():
                            self._response_future.cancel()
                        break

                    text = chunk.decode("utf-8", errors="replace")
                    await self._output_buffer.put(text)

                except asyncio.TimeoutError:
                    continue

        except asyncio.CancelledError:
            logger.debug("Read loop cancelled")
        except Exception as e:
            logger.error(f"Read loop error: {e}")
            self._running = False
            if self._response_future is not None and not self._response_future.done():
                self._response_future.cancel()

    async def send(
        self,
        message: str,
        interrupt_event: Optional[asyncio.Event] = None,
        timeout: float = None,
    ) -> SessionResponse:
        """Send a message and wait for response."""
        if not self._running or self._process is None or self._process.returncode is not None:
            logger.warning(f"Session not available: running={self._running}, returncode={self._process.returncode if self._process else 'N/A'}")
            return SessionResponse(error="Session not running", model_used=self.model)

        async with self._send_lock:
            self._current_response_parts = []
            self._current_tool_calls = []
            self._response_future = None
            self._response_future = asyncio.Future()

            try:
                input_text = message + "\n"
                self._process.stdin.write(input_text.encode("utf-8"))
                await self._process.stdin.drain()

                logger.debug(f"Sent message to session ({len(message)} chars)")

            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                if self._response_future and not self._response_future.done():
                    self._response_future.set_exception(e)
                return SessionResponse(error=str(e), model_used=self.model)

            timeout = timeout or config.CLAUDE_CODE_TIMEOUT
            start_time = asyncio.get_event_loop().time()

            try:
                while True:
                    if interrupt_event and interrupt_event.is_set():
                        if not self._response_future.done():
                            self._response_future.set_result(
                                SessionResponse(
                                    text="[Interrupted]",
                                    model_used=self.model,
                                    interrupted=True,
                                )
                            )
                        break

                    elapsed = asyncio.get_event_loop().time() - start_time
                    if elapsed > timeout:
                        if not self._response_future.done():
                            self._response_future.set_result(
                                SessionResponse(error="Timeout", model_used=self.model)
                            )
                        break

                    if self._process.returncode is not None:
                        if not self._response_future.done():
                            self._response_future.set_result(
                                SessionResponse(
                                    error=f"Process exited with code {self._process.returncode}",
                                    model_used=self.model,
                                    exit_code=self._process.returncode,
                                )
                            )
                        break

                    if self._response_future.done():
                        break

                    await asyncio.sleep(0.1)

            except asyncio.CancelledError:
                if not self._response_future.done():
                    self._response_future.set_result(
                        SessionResponse(text="[Cancelled]", model_used=self.model, interrupted=True)
                    )

            try:
                response = await self._response_future
            except Exception as e:
                response = SessionResponse(error=str(e), model_used=self.model)

            if not response.text and not response.error and not response.interrupted:
                response.text = "".join(self._current_response_parts) or "[No response]"

            response.model_used = self.model
            response.session_id = self._session_id
            return response

    def _process_output(self, text: str):
        """Process output from the read loop."""
        self._current_response_parts.append(text)

        if self._response_future is not None and not self._response_future.done():
            full_text = "".join(self._current_response_parts)
            if self._is_response_complete(full_text):
                response = SessionResponse(
                    text=full_text.strip(),
                    tool_calls=self._current_tool_calls.copy(),
                    model_used=self.model,
                )
                try:
                    self._response_future.set_result(response)
                except asyncio.InvalidStateError:
                    logger.warning("Attempted to set_result on already-completed future")
                self._current_response_parts = []

    def _is_response_complete(self, text: str) -> bool:
        """Heuristic to detect if response is complete."""
        if not text.strip():
            return False

        text_lower = text.lower()

        end_patterns = [
            "\n\n",
            ".",
            "!",
            "?",
            "```",
        ]

        for pattern in end_patterns:
            if text.rstrip().endswith(pattern):
                if len(text.strip()) > 50:
                    return True

        if len(text.strip()) > 2000:
            return True

        return False

    async def _handle_tool_call(self, tool_data: dict):
        """Handle a tool call from the stream."""
        self._current_tool_calls.append(tool_data)

    async def stop(self):
        """Stop the persistent session gracefully."""
        logger.info("Stopping persistent session...")
        self._running = False

        if self._read_task and not self._read_task.done():
            self._read_task.cancel()
            try:
                await self._read_task
            except asyncio.CancelledError:
                pass

        if self._process and self._process.stdin:
            try:
                self._process.stdin.close()
            except Exception:
                pass

        if self._process:
            try:
                await asyncio.wait_for(self._process.wait(), timeout=5)
                logger.info(f"Session process exited cleanly (code {self._process.returncode})")
            except asyncio.TimeoutError:
                await self._kill_process()

        self._started = False
        logger.info("Persistent session stopped")

    async def _kill_process(self):
        """Force kill the process."""
        if not self._process:
            return

        try:
            if sys.platform == "win32":
                _subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(self._process.pid)],
                    capture_output=True,
                    timeout=5
                )
            else:
                self._process.kill()
                await asyncio.wait_for(self._process.wait(), timeout=5)
        except Exception as e:
            logger.debug(f"Force kill error: {e}")

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def is_running(self) -> bool:
        return self._running
