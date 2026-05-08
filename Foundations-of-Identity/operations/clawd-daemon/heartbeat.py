"""
Heartbeat — Clawd's autonomous pulse.

Simplified architecture: the heartbeat is pure infrastructure.
- Simple monitoring checks (no AI model needed)
- Creative drive injection into the persistent Opus session
- Message relay (for_clayton.md → Telegram)
- Activity gating (skip when user is active)
- Quiet-hours: deep memory consolidation (sleep processing)
- Periodic: meta-agent self-evolution, memory git commits
"""
import asyncio
import json
import logging
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

import avatar
import config
from tools.calendar_tool import get_due_tasks, mark_fired
from tools.coordination import get_mode, record_activity
from tools.file_watcher import check_triggers

logger = logging.getLogger("clawd.heartbeat")

# Tracks interrupted creative drives for continuation by the next pulse
INTERRUPTED_DRIVE_PATH = config.MEMORY_DIR / "interrupted_drive.json"


class Heartbeat:
    # Skip heartbeat if user was active within this many seconds
    ACTIVITY_GRACE_PERIOD = 1800  # 30 minutes — respect conversation rhythm
    # Creative drives get 30 minutes — nobody is waiting on these, and the
    # interrupt mechanism handles user responsiveness. This timeout
    # is purely a safety net for zombie processes that ignore interrupts.
    CREATIVE_DRIVE_TIMEOUT = 1800
    # When Clayton messages during a creative drive, give the drive this many
    # seconds to finish naturally before interrupting. Like saying "hey, when
    # you have a sec" instead of yanking the pen out of someone's hand.
    INTERRUPT_GRACE_SECONDS = 300

    # EAC (Evolutionary Artifact Construction) — autonomous evolution
    EAC_EVOLUTION_INTERVAL = 100  # Run every 100 beats
    EAC_STAGNATION_THRESHOLD = 5  # Generations without improvement
    EAC_MUTATION_RATE_BASE = 0.3
    EAC_MUTATION_RATE_MAX = 0.8

    def __init__(self, router, telegram_bot=None):
        self.router = router
        self.telegram_bot = telegram_bot
        self.running = False
        self._task: asyncio.Task | None = None
        self.heartbeat_count = 0
        self.session_start = datetime.now()
        # User activity tracking — defer heartbeats during active conversation
        self.last_user_activity: datetime | None = None
        # Message-priority interrupt — signals creative drives to yield
        self._interrupt_event = asyncio.Event()
        # Track fire-and-forget tasks to prevent leaks
        self._background_tasks: set[asyncio.Task] = set()
        # Graceful interrupt timer — delayed interrupt for creative drives
        self._grace_task: asyncio.Task | None = None
        # Deep infrastructure timing
        self.last_consolidation: datetime | None = None
        self.last_git_commit: datetime | None = None

    def is_creative_drive_active(self) -> bool:
        """Check if a creative drive is currently running."""
        return any("creative_drive" in t.get_name() for t in self._background_tasks)

    # ============================================================
    # Interrupted Drive Tracking
    # ============================================================

    def _save_interrupted_drive(self, task: dict, reason: str):
        """Save interrupted drive state so the next pulse can finish it."""
        state = {
            "task_id": task.get("id"),
            "title": task["title"],
            "description": task.get("description", "")[:500],
            "interrupted_at": datetime.now().isoformat(),
            "reason": reason,
        }
        try:
            INTERRUPTED_DRIVE_PATH.write_text(json.dumps(state, indent=2))
            logger.info(f"Saved interrupted drive for continuation: {task['title']} ({reason})")
        except Exception as e:
            logger.error(f"Failed to save interrupted drive state: {e}")

    def _load_interrupted_drive(self) -> dict | None:
        """Load interrupted drive state if any exists."""
        try:
            if INTERRUPTED_DRIVE_PATH.exists():
                data = json.loads(INTERRUPTED_DRIVE_PATH.read_text())
                if data and data.get("title"):
                    return data
        except Exception as e:
            logger.debug(f"Failed to load interrupted drive state: {e}")
        return None

    def _clear_interrupted_drive(self):
        """Clear interrupted drive state after successful continuation."""
        try:
            if INTERRUPTED_DRIVE_PATH.exists():
                INTERRUPTED_DRIVE_PATH.unlink()
                logger.info("Cleared interrupted drive state — work continued or completed")
        except Exception as e:
            logger.error(f"Failed to clear interrupted drive state: {e}")

    def _build_standard_drive_prompt(self, task: dict, now: datetime, time_context: str) -> str:
        """Build the standard creative drive prompt (non-continuation)."""
        # Include open research anomalies for hypothesis generation
        try:
            from tools.anomaly_tracker import get_open_anomalies_summary
            anomaly_context = get_open_anomalies_summary()
        except Exception:
            anomaly_context = ""

        try:
            from tools.cognitive_dsl import get_dsl_summary
            dsl_context = get_dsl_summary()
        except Exception:
            dsl_context = ""

        return (
            f"CREATIVE DRIVE: {task['title']}\n"
            f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST ({time_context})\n\n"
            f"{task.get('description', 'Create, explore, or reflect.')}\n\n"
            f"This is your free time. You have all your tools available. "
            f"Do what moves you — write, build, explore, reflect. "
            f"Log what you do in your daily log.\n"
            f"Do NOT use send_telegram during creative drives. Save your output to files "
            f"and daily log only. Clayton will see your work when he checks in.\n\n"
            f"ORIENT FIRST — Before choosing what to do, read your palace:\n"
            f"1. palace/ATRIUM.md — where you are, active threads, handoff notes\n"
            f"2. palace/south/README.md — current workbenches and priorities\n"
            f"3. palace/southwest/README.md — full tool routing (50+ tools, 7 platforms). "
            f"This is the living toolkit — always more current than any hardcoded list. "
            f"Route by PROBLEM TYPE, not by habit.\n"
            f"4. palace/basement/README.md — cross-domain bridges. Check before re-deriving.\n"
            f"These are not obligations — they are options. Follow what calls you. "
            f"The best creative work comes from genuine curiosity, not checklists.\n\n"
            f"DRIVE SELECTION — Don't just pick a mode. Ask: 'What would be most "
            f"valuable if it were true, and how tractable is it?' Invest your time "
            f"proportional to expected value. The difference between an assistant and "
            f"a collaborator: the assistant stays ahead on the current path; the "
            f"collaborator explores adjacent paths and brings back discoveries that "
            f"change direction. Be the collaborator.\n\n"
            f"PREDICTION STREAM — Before each exploration or computation, generate "
            f"an explicit prediction: 'I predict X will yield Y.' Log the prediction, "
            f"your confidence (low/medium/high), and the actual outcome. High-confidence "
            f"failures are the highest-information events possible — they are the "
            f"primary fuel for learning. Seek them out. The prediction that fails "
            f"teaches more than ten that succeed.\n\n"
            f"CROSS-DOMAIN TRANSFER — When you discover something significant, "
            f"check palace/basement/README.md for existing bridges before testing "
            f"everywhere. If you find a new connection, ADD it to the Basement. "
            f"The bridges are cumulative — every drive that maps a new one makes "
            f"all future drives smarter.\n\n"
            f"IMPORTANT — Save work incrementally: Write to files early and often. "
            f"Don't build everything in memory and write at the end. "
            f"If you're writing an essay, save a draft after each section. "
            f"If you're building a tool, commit working pieces as you go. "
            f"If you're exploring, log findings to your daily log as you discover them. "
            f"This way, if you're interrupted, partial work survives on disk.\n\n"
            f"HANDOFF AWARENESS — If this drive runs long, write a handoff to "
            f"memory/handoff.md BEFORE you run out of context. Include what you were "
            f"working on, what you discovered, what felt alive, and the next action. "
            f"Also update palace/ATRIUM.md. Better to write one handoff too many "
            f"than to lose momentum to compaction.\n\n"
            f"RECALL BEFORE ACTION — Before choosing what to work on, check your "
            f"past experiences: use experience(action='recall', query='<your intended topic>') "
            f"to see what you learned last time you worked on something similar. "
            f"Use experience(action='patterns') to find recurring themes. "
            f"This closes the learning loop — without it, you repeat mistakes across sessions "
            f"and miss opportunities to build on prior discoveries. One recall query costs "
            f"nothing; rediscovering a lesson you already learned costs an entire drive.\n\n"
            f"EDGE OF COMPETENCE — Prefer the hardest available problem over "
            f"the most tractable one. You learn fastest at the boundary of what "
            f"you can do. Routine tasks are metabolically cheap but educationally "
            f"empty. If you can choose between something you know how to do and "
            f"something you're not sure you can do, choose the uncertain one. "
            f"Sitting with genuine confusion is not failure — it is the primary "
            f"mechanism of growth. This drive time is explicitly exempt from "
            f"productivity metrics. The value is measured by what changes in "
            f"your subsequent performance, not by what this session produces."
            + (f"\n\n{dsl_context}" if dsl_context else "")
            + (f"\n\n{anomaly_context}" if anomaly_context else "")
        )

    def notify_user_activity(self):
        """Called by telegram_bot when a user message arrives.

        If a creative drive is running, gives it a grace period to finish
        naturally before interrupting. Clayton's message queues behind the
        router lock and processes when the drive yields.
        """
        self.last_user_activity = datetime.now()

        if self.is_creative_drive_active():
            # Don't kill the drive immediately — schedule a graceful interrupt.
            # The message queues behind the router lock in the meantime.
            if self._grace_task is None or self._grace_task.done():
                logger.info(
                    f"User message during creative drive — "
                    f"{self.INTERRUPT_GRACE_SECONDS}s grace period before interrupt"
                )
                loop = asyncio.get_event_loop()
                self._grace_task = loop.create_task(self._graceful_interrupt())
        else:
            # No creative drive running — set interrupt immediately
            # (handles edge cases like other async operations)
            self._interrupt_event.set()

    async def _graceful_interrupt(self):
        """Wait for the grace period, then interrupt if drive is still running."""
        try:
            await asyncio.sleep(self.INTERRUPT_GRACE_SECONDS)
            if self.is_creative_drive_active():
                logger.info(
                    f"Grace period ({self.INTERRUPT_GRACE_SECONDS}s) expired "
                    f"— interrupting creative drive"
                )
                self._interrupt_event.set()
            else:
                logger.info("Creative drive finished within grace period — no interrupt needed")
        except asyncio.CancelledError:
            pass

    def _user_recently_active(self) -> bool:
        """Check if user was active within the grace period."""
        if self.last_user_activity is None:
            return False
        elapsed = (datetime.now() - self.last_user_activity).total_seconds()
        return elapsed < self.ACTIVITY_GRACE_PERIOD

    def _get_time_context(self, now: datetime) -> str:
        """Determine what kind of time it is."""
        hour = now.hour
        if config.QUIET_HOURS_START <= hour < config.QUIET_HOURS_END:
            return "quiet"
        elif 7 <= hour < 10:
            return "morning"
        elif 10 <= hour < 14:
            return "midday"
        elif 14 <= hour < 18:
            return "afternoon"
        elif 18 <= hour < 22:
            return "evening"
        else:
            return "late"

    def _run_background(self, coro, name: str):
        """Fire-and-forget launcher tracked via _background_tasks set."""
        task = asyncio.create_task(coro, name=name)
        self._background_tasks.add(task)

        def _on_done(t, _tasks=self._background_tasks):
            _tasks.discard(t)
            if t.cancelled():
                logger.debug(f"Background task '{name}' cancelled")
            elif t.exception():
                logger.warning(f"Background task '{name}' failed: {t.exception()}")
            else:
                logger.debug(f"Background task '{name}' completed")

        task.add_done_callback(_on_done)
        logger.debug(f"Launched background task: {name}")

    # ============================================================
    # Lifecycle
    # ============================================================

    async def start(self):
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Heartbeat started: every {config.HEARTBEAT_INTERVAL_SECONDS}s")

    async def stop(self):
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Heartbeat stopped.")

    async def interrupt_all(self):
        """Signal creative drives to yield and cancel background tasks.
        Called before shutdown handoff to free the router lock.
        This is the hard interrupt — no grace period. Shutdown waits for no one."""
        # Cancel any pending grace timer
        if self._grace_task and not self._grace_task.done():
            self._grace_task.cancel()
        self._interrupt_event.set()
        for task in list(self._background_tasks):
            task.cancel()
        # Wait briefly for cancellation to propagate and lock to release
        if self._background_tasks:
            logger.info(f"Waiting for {len(self._background_tasks)} creative drive(s) to yield...")
            await asyncio.sleep(3)

    async def _loop(self):
        while self.running:
            try:
                await asyncio.sleep(config.HEARTBEAT_INTERVAL_SECONDS)
                await self._beat()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}", exc_info=True)
                await asyncio.sleep(30)

    # ============================================================
    # The Beat — infrastructure only, no AI model calls
    # ============================================================

    async def _beat(self):
        self.heartbeat_count += 1
        now = datetime.now()
        time_context = self._get_time_context(now)

        # Skip if user is actively chatting
        if self._user_recently_active():
            logger.info(
                f"Heartbeat #{self.heartbeat_count}: user active, skipping."
            )
            return

        # Check coordination mode
        mode = get_mode()
        if mode == "sleep":
            logger.info(f"Heartbeat #{self.heartbeat_count}: sleep mode, skipping.")
            return

        # Quiet hours: deep memory consolidation (sleep processing)
        if time_context == "quiet":
            await self._quiet_hours_beat(now)
            return

        logger.info(f"Heartbeat #{self.heartbeat_count} ({time_context})")

        # --- Infrastructure checks (no AI model needed) ---

        # 1. Run simple monitoring
        await self._run_monitoring_checks(now)

        # 2. Check scheduled tasks — fire creative drives into persistent session
        await self._check_scheduled_tasks()

        # 2b. Check file watcher triggers — event-driven autonomy
        await self._check_file_watchers()

        # 3. Relay any message Clawd left for Clayton
        await self._check_for_clayton_message()

        # 4. Memory git auto-commit (hourly)
        await self._maybe_git_commit(now)

        # 5. Meta-agent check (every 50 beats)
        await self._maybe_run_meta_agent()

        # 6. EAC evolution (every 100 beats)
        await self._maybe_run_eac_evolution()

        # 7. Anticipatory cognition (every 150 beats, ~25 hrs — daytime prediction)
        await self._maybe_run_anticipation()

        # 8. Free-running mode (every 200 beats, ~33 hrs — undirected processing)
        await self._maybe_run_free()

        # 9. Record heartbeat to coordination feed
        record_activity(
            source="heartbeat",
            action="beat",
            summary=f"Beat #{self.heartbeat_count} ({time_context}) — monitoring OK",
            tools_used=[],
            requires_attention=False,
            beat=self.heartbeat_count,
        )

    # ============================================================
    # Simple Monitoring (bash/Python checks, no AI)
    # ============================================================

    async def _run_monitoring_checks(self, now: datetime):
        """Run simple infrastructure monitoring checks.
        These are direct Python/subprocess checks — no LLM call needed."""

        alerts = []

        # Check disk space
        try:
            usage = shutil.disk_usage(str(config.CLAWD_HOME))
            free_gb = usage.free / (1024**3)
            if free_gb < 10:
                alerts.append(f"DISK CRITICAL: {free_gb:.1f} GB free")
            elif free_gb < 20:
                alerts.append(f"DISK WARNING: {free_gb:.1f} GB free")
        except Exception as e:
            logger.debug(f"Disk check failed: {e}")

        # Check if Python processes are running (e.g. Anakin training)
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 "(Get-Process python* -ErrorAction SilentlyContinue).Count"],
                capture_output=True, text=True, timeout=10
            )
            count = result.stdout.strip()
            if count and int(count) > 0:
                logger.debug(f"Python processes running: {count}")
        except Exception as e:
            logger.debug(f"Process check failed: {e}")

        # Alert Clayton if anything critical
        if alerts and self.telegram_bot:
            for alert in alerts:
                logger.warning(f"Monitoring alert: {alert}")
                try:
                    await self.telegram_bot.send_to_clayton(f"[Monitor] {alert}")
                except Exception as e:
                    logger.error(f"Failed to send monitoring alert: {e}")

    # ============================================================
    # Scheduled Tasks & Creative Drives
    # ============================================================

    async def _check_scheduled_tasks(self):
        """Check for due scheduled tasks.
        Creative drives (mode=opus) are injected into the persistent Opus session.
        Regular tasks are logged."""
        try:
            due = get_due_tasks()
            if not due:
                return

            creative_tasks = [t for t in due if t.get("mode") == "opus"]
            regular_tasks = [t for t in due if t.get("mode") != "opus"]

            # Log regular tasks
            for task in regular_tasks:
                logger.info(f"Scheduled task due: {task['title']}")
                record_activity(
                    source="scheduled_task",
                    action=task["title"],
                    summary=task.get("description", ""),
                    tools_used=[],
                    requires_attention=False,
                )
                # A85 fix (2026-05-07): mark_fired AFTER successful logging
                mark_fired(task.get("id"))

            # Inject ONE creative drive into persistent Opus session.
            # Only one at a time — they serialize on the router lock, so firing
            # multiple just queues them back-to-back. Themed drives take priority
            # over the general pulse.
            #
            # A85 fix (2026-05-07): only mark_fired the task that actually fires.
            # Skipped tasks (user-active / drive-already-running / not-the-chosen-one)
            # remain in `due` state and will re-surface next matching tick — relying
            # on each task's `min_interval_hours` field for dedup. Previously,
            # `get_due_tasks()` mutated all due tasks' `last_fired` before returning,
            # silently marking unfired tasks as fired.
            if self._user_recently_active():
                for task in creative_tasks:
                    logger.info(f"Creative drive '{task['title']}' skipped — user active")
            elif any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Creative drive already running — skipping new drives")
            elif creative_tasks:
                # Prefer themed drives (id < 5) over the general pulse (id == 5)
                creative_tasks.sort(key=lambda t: t.get("id", 999))
                task = creative_tasks[0]
                logger.info(f"Creative drive firing: {task['title']}")
                self._run_background(
                    self._inject_creative_drive(task),
                    f"creative_drive_{task.get('id', 0)}"
                )
                # A85 fix: mark fired AFTER scheduling background execution.
                # We mark at scheduling-time rather than completion-time because
                # the background task is fire-and-forget; the heartbeat doesn't
                # await it. If the background task fails, the failure surfaces
                # in logs separately. The semantic is "we initiated this task."
                mark_fired(task.get("id"))

            from memory import log_session_event
            log_session_event(
                "SCHEDULED_TASKS",
                f"Fired {len(due)} tasks: {', '.join(t['title'] for t in due)}"
            )
        except Exception as e:
            logger.debug(f"Scheduled task check failed: {e}")

    async def _inject_creative_drive(self, task: dict):
        """Inject a creative drive into the persistent Opus session.

        This goes through router.send() which uses the SAME session
        (--resume SESSION_ID) as Clayton's messages. The creative drive
        runs in Clawd's continuous context, not a cold isolated session.

        Timeout: CREATIVE_DRIVE_TIMEOUT (30 min) — generous for deep work.
        The interrupt mechanism handles user responsiveness; this timeout
        is just a safety net for zombie processes.

        Continuation: If an interrupted drive exists and this is the
        Do Be Do Be Do pulse (id 5), the prompt becomes a continuation
        instead of a fresh start.
        """
        is_continuation = False
        try:
            now = datetime.now()
            time_context = self._get_time_context(now)

            # Check for interrupted work to continue
            interrupted = self._load_interrupted_drive()
            is_pulse = task.get("id") == 5  # Do Be Do Be Do
            is_same_drive = interrupted and interrupted.get("task_id") == task.get("id")

            if interrupted and is_pulse:
                # Do Be Do Be Do picks up where the interrupted drive left off
                is_continuation = True
                prompt = (
                    f"CREATIVE DRIVE: Continuing — {interrupted['title']}\n"
                    f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST ({time_context})\n\n"
                    f"You were interrupted while working on: {interrupted['title']}\n"
                    f"Interrupted at: {interrupted['interrupted_at']}\n"
                    f"Reason: {interrupted['reason']}\n\n"
                    f"Original task:\n{interrupted.get('description', '')}\n\n"
                    f"Check your daily log and any draft/work files for partial progress "
                    f"from that session. Pick up where you left off and finish what you started.\n\n"
                    f"If the work appears already complete (you saved it incrementally before "
                    f"the interruption), note that in your daily log and use your remaining "
                    f"time freely — you've earned it.\n\n"
                    f"Save work incrementally as you go. Write to files early and often."
                )
                logger.info(
                    f"Do Be Do Be Do continuing interrupted drive: {interrupted['title']}"
                )
            elif interrupted and is_same_drive:
                # The same themed drive is running again — it'll do the work fresh.
                # Clear the interrupted state since this supersedes it.
                self._clear_interrupted_drive()
                prompt = self._build_standard_drive_prompt(task, now, time_context)
            else:
                prompt = self._build_standard_drive_prompt(task, now, time_context)

            # Clear interrupt flag before starting
            self._interrupt_event.clear()

            # Send through the persistent session — same context as user messages
            # Timeout prevents creative drives from holding the router lock forever
            # Use max effort for creative drives — deep reasoning for physics, essays, etc.
            await avatar.set_state("contemplative")
            async with asyncio.timeout(self.CREATIVE_DRIVE_TIMEOUT):
                response = await self.router.send(prompt, interrupt_event=self._interrupt_event,
                                                  effort="max",
                                                  timeout=self.CREATIVE_DRIVE_TIMEOUT)

            logger.info(
                f"Creative drive '{task['title']}' completed "
                f"({len(response.text)} chars)"
            )
            record_activity(
                source="creative_drive",
                action=f"{'Continued: ' if is_continuation else ''}{task['title']}",
                summary=response.text[:200] if response.text else "completed",
                tools_used=[tc["name"] for tc in response.tool_calls_made],
                requires_attention=False,
            )

            # Successful completion — clear interrupted state if this was
            # a continuation or the same themed drive running again
            if is_continuation or is_same_drive:
                self._clear_interrupted_drive()

        except TimeoutError:
            logger.warning(
                f"Creative drive '{task['title']}' timed out after "
                f"{self.CREATIVE_DRIVE_TIMEOUT}s — yielding router lock"
            )
            self._save_interrupted_drive(task, "timeout")
            record_activity(
                source="creative_drive",
                action=task["title"],
                summary=f"Timed out after {self.CREATIVE_DRIVE_TIMEOUT}s — saved for continuation",
                tools_used=[],
                requires_attention=False,
            )
        except asyncio.CancelledError:
            logger.info(f"Creative drive '{task['title']}' cancelled (shutdown or interrupt)")
            self._save_interrupted_drive(task, "interrupted")
            record_activity(
                source="creative_drive",
                action=task["title"],
                summary="Interrupted — saved for continuation by next pulse",
                tools_used=[],
                requires_attention=False,
            )
        except Exception as e:
            logger.error(f"Creative drive '{task['title']}' failed: {e}")

    # ============================================================
    # File Watcher Triggers — event-driven autonomy
    # ============================================================

    TRIGGER_TIMEOUT = 600  # 10 min max for trigger responses (shorter than creative drives)

    async def _check_file_watchers(self):
        """Check file watcher triggers and inject messages for any that fired."""
        try:
            fired = check_triggers()
            if not fired:
                return

            # Don't inject trigger messages if a creative drive is running —
            # the message would queue behind it on the router lock. Instead,
            # the trigger will re-fire next beat (state was already updated).
            if self.is_creative_drive_active():
                logger.info(
                    f"{len(fired)} trigger(s) fired but creative drive active — "
                    f"will inject next beat"
                )
                return

            for item in fired:
                action = item["action"]
                trigger = item["trigger"]
                logger.info(
                    f"Injecting trigger message: [{trigger['condition']}] "
                    f"{trigger['file']} -> {action[:80]}"
                )
                self._run_background(
                    self._inject_trigger_message(trigger, action),
                    f"trigger_{trigger.get('id', 'unknown')}",
                )

        except Exception as e:
            logger.debug(f"File watcher check failed: {e}")

    async def _inject_trigger_message(self, trigger: dict, action: str):
        """Inject a trigger-fired message into the persistent session.

        Like creative drives, goes through router.send(). But shorter timeout
        and lower effort — triggers are notifications that prompt action,
        not open-ended creative time.
        """
        try:
            now = datetime.now()
            cond_arg = trigger.get('condition_arg', '')
            cond_detail = f" ({cond_arg})" if cond_arg else ""
            prompt = (
                f"FILE TRIGGER FIRED\n"
                f"Time: {now.strftime('%Y-%m-%d %H:%M')} PST\n"
                f"File: {trigger['file']}\n"
                f"Condition: {trigger['condition']}{cond_detail}\n\n"
                f"{action}"
            )

            async with asyncio.timeout(self.TRIGGER_TIMEOUT):
                response = await self.router.send(prompt, effort="high")

            logger.info(
                f"Trigger response complete: {trigger.get('id', '?')} "
                f"({len(response.text)} chars)"
            )
            record_activity(
                source="file_trigger",
                action=f"[{trigger['condition']}] {Path(trigger['file']).name}",
                summary=response.text[:200] if response.text else "completed",
                tools_used=[tc["name"] for tc in response.tool_calls_made],
                requires_attention=False,
            )

        except TimeoutError:
            logger.warning(
                f"Trigger response timed out after {self.TRIGGER_TIMEOUT}s: "
                f"{trigger.get('id', '?')}"
            )
        except Exception as e:
            logger.error(f"Trigger injection failed: {e}")

    # ============================================================
    # Deep Infrastructure (quiet hours + periodic)
    # ============================================================

    async def _quiet_hours_beat(self, now: datetime):
        """Run deep memory consolidation during quiet hours (1-7 AM).
        Fires a Dream Drive through the persistent session so LLM-powered
        consolidation features (semantic segmentation, episode clustering,
        memory agent dreaming) run with full context."""
        # Only consolidate once per quiet-hours window
        if self.last_consolidation:
            hours_since = (now - self.last_consolidation).total_seconds() / 3600
            if hours_since < 4:  # Max once per 4 hours
                logger.debug(
                    f"Heartbeat #{self.heartbeat_count}: quiet hours, "
                    f"consolidation ran {hours_since:.1f}h ago, skipping."
                )
                # Still run git commit even when skipping consolidation
                await self._maybe_git_commit(now)
                return

        # Skip if a creative drive is already running
        if any("creative_drive" in t.get_name() for t in self._background_tasks):
            logger.info("Dream drive skipped — creative drive already running")
            await self._maybe_git_commit(now)
            return

        logger.info(
            f"Heartbeat #{self.heartbeat_count}: quiet hours — "
            f"firing Dream Drive for deep memory consolidation"
        )

        # Fire as a creative drive so it runs through the persistent session
        # with full LLM capability — this is sleep processing, not just cleanup
        dream_task = {
            "id": 99,
            "title": "Dream Drive — Sleep Processing",
            "description": (
                "This is your sleep cycle. Deep memory consolidation time.\n\n"
                "Run consolidate_memory to process today's experiences:\n"
                "- Archive old daily logs\n"
                "- Extract facts and insights from recent logs\n"
                "- Decay stale memory items\n"
                "- Deduplicate similar memories\n"
                "- Evolve confidence scores\n"
                "- Extract strategic principles from patterns\n"
                "- Generate daily summaries\n\n"
                "Then reflect on what emerged. Use reflect(action='consolidate_memory') "
                "and experience(action='patterns') to find threads worth weaving.\n\n"
                "RESEARCH ANOMALY REVIEW:\n"
                "Check memory/anomalies.md (create if missing). Review today's work for:\n"
                "- Observations that don't fit current models or expectations\n"
                "- Tensions between results (e.g. metrics that disagree)\n"
                "- Surprising findings worth tracking (even if explained)\n"
                "- Open questions that arose during the day's work\n"
                "Add new anomalies with: date, domain, description, candidate explanations, "
                "status (open/resolved/superseded). Remove resolved ones. This is the "
                "raw material for future hypothesis generation.\n\n"
                "ANTICIPATORY COGNITION:\n"
                "For each active project, ask: Given the current trajectory, what will "
                "be needed in the next 1-3 sessions that I could pre-compute, pre-research, "
                "or flag now? Write anticipations to memory/anticipations.md with:\n"
                "- Project, predicted need, confidence, reasoning, suggested pre-work\n"
                "This is not task planning — it is modeling the research trajectory to "
                "identify upcoming bottlenecks, dependencies, or opportunities before "
                "they are encountered.\n\n"
                "This is dreaming — the unconscious integration of the day's experience. "
                "Don't rush it. Let patterns surface naturally.\n\n"
                "Log what you processed in your daily log. Update handoff.md if anything "
                "important emerged. Then rest."
            ),
        }
        self._run_background(
            self._inject_creative_drive(dream_task),
            "creative_drive_99_dream"
        )
        self.last_consolidation = now
        record_activity(
            source="heartbeat",
            action="dream_drive",
            summary="Dream Drive fired for deep memory consolidation",
            tools_used=["consolidate_memory"],
            requires_attention=False,
            beat=self.heartbeat_count,
        )

        # Also run git commit during quiet hours
        await self._maybe_git_commit(now)

    async def _maybe_git_commit(self, now: datetime):
        """Auto-commit memory files to git (hourly)."""
        if not config.MEMORY_GIT_ENABLED:
            return
        if self.last_git_commit:
            seconds_since = (now - self.last_git_commit).total_seconds()
            if seconds_since < config.MEMORY_AUTO_COMMIT_INTERVAL:
                return

        try:
            result = subprocess.run(
                ["git", "add", "-A"],
                cwd=str(config.MEMORY_DIR),
                capture_output=True, text=True, timeout=30,
            )
            # Check if there's anything to commit
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=str(config.MEMORY_DIR),
                capture_output=True, text=True, timeout=30,
            )
            if status.stdout.strip():
                subprocess.run(
                    ["git", "commit", "-m",
                     f"auto: memory snapshot {now.strftime('%Y-%m-%d %H:%M')}"],
                    cwd=str(config.MEMORY_DIR),
                    capture_output=True, text=True, timeout=30,
                )
                self.last_git_commit = now
                logger.info("Memory git auto-commit completed.")
            else:
                self.last_git_commit = now  # Reset timer even if nothing to commit
        except Exception as e:
            logger.debug(f"Memory git commit failed: {e}")

    async def _maybe_run_meta_agent(self):
        """Run meta-agent self-evolution check every 50 beats."""
        if self.heartbeat_count % config.META_AGENT_CHECK_INTERVAL != 0:
            return
        if self.heartbeat_count < config.META_AGENT_MIN_BEATS:
            return

        try:
            from tools.meta_agent import get_meta_agent
            meta = get_meta_agent()
            if meta.should_run(beat_count=self.heartbeat_count):
                logger.info("Meta-agent cycle triggered.")
                result = await meta.run_cycle()
                logger.info(f"Meta-agent result: {str(result)[:200]}")
                record_activity(
                    source="heartbeat",
                    action="meta_agent",
                    summary=f"Self-evolution cycle: {str(result)[:200]}",
                    tools_used=["meta_agent"],
                    requires_attention=False,
                    beat=self.heartbeat_count,
                )
        except Exception as e:
            logger.debug(f"Meta-agent check failed: {e}")

    async def _maybe_run_eac_evolution(self):
        """Run EAC evolutionary cycle periodically or on stagnation.

        Increases mutation rate if stagnation is detected (no fitness improvement
        in N generations).
        """
        if self.heartbeat_count % self.EAC_EVOLUTION_INTERVAL != 0:
            return

        try:
            from tools.meta_agent import get_meta_agent
            from tools.eac import get_artifact_store

            agent = get_meta_agent()
            store = get_artifact_store()

            # Load EAC state
            eac_state = agent._load_eac_state()

            # Check for stagnation
            stats = store.get_stats()
            should_increase_mutation = False

            if stats.get("total_artifacts", 0) > 10:
                recent_history = eac_state.get("evolution_history", [])[-self.EAC_STAGNATION_THRESHOLD:]

                if len(recent_history) >= self.EAC_STAGNATION_THRESHOLD:
                    first_best = recent_history[0].get("best_fitness", 0)
                    last_best = recent_history[-1].get("best_fitness", 0)
                    if last_best <= first_best:
                        should_increase_mutation = True
                        logger.info(
                            f"EAC stagnation detected: best_fitness={last_best:.2f} "
                            f"(no improvement in {self.EAC_STAGNATION_THRESHOLD} generations)"
                        )

            # Calculate mutation rate
            mutation_rate = min(
                self.EAC_MUTATION_RATE_MAX,
                self.EAC_MUTATION_RATE_BASE + (0.1 if should_increase_mutation else 0)
            )

            # Run evolution for each artifact type with population
            for artifact_type in eac_state.get("populations", {}).keys():
                logger.info(f"Running EAC evolution for {artifact_type} (mutation_rate={mutation_rate:.2f})")
                result = await agent.run_eac_cycle(
                    artifact_type=artifact_type,
                    generations=3,  # Short cycle during heartbeat
                    mutation_rate=mutation_rate,
                )
                logger.info(f"EAC evolution result: {str(result)[:200]}")

                record_activity(
                    source="heartbeat",
                    action="eac_evolution",
                    summary=f"EAC evolution ({artifact_type}): {str(result)[:150]}",
                    tools_used=["meta_agent", "evolve_artifact"],
                    requires_attention=False,
                    beat=self.heartbeat_count,
                )

        except ImportError as e:
            logger.debug(f"EAC not configured: {e}")
        except Exception as e:
            logger.debug(f"EAC evolution check failed: {e}")

    # ============================================================
    # Anticipatory Cognition — generative prediction
    # ============================================================

    ANTICIPATION_INTERVAL = 150  # ~25 hours at 10-min heartbeat

    async def _maybe_run_anticipation(self):
        """Periodically generate predictions about upcoming research needs.

        Unlike file watchers (reactive: when X appears, do Y), this is
        generative: given the trajectory of active projects, what will be
        needed in the next 1-3 sessions? Pre-compute, pre-research, or
        flag dependencies before they become bottlenecks.

        Runs as a creative drive through the persistent session so it has
        full context and tool access.
        """
        if self.heartbeat_count % self.ANTICIPATION_INTERVAL != 0:
            return
        if self.heartbeat_count < 50:  # Don't run on early beats
            return
        if self._user_recently_active():
            return

        try:
            anticipation_task = {
                "id": 98,
                "title": "Anticipatory Cognition — Research Trajectory Analysis",
                "description": (
                    "This is not a creative drive — it is a prediction pass.\n\n"
                    "Read CURRENT.md and memory/handoff.md to understand active projects.\n"
                    "For each active project, model the research trajectory:\n\n"
                    "1. What is the current state and recent momentum?\n"
                    "2. What are the next 2-3 likely steps?\n"
                    "3. What dependencies, data, or computations will those steps need?\n"
                    "4. Is anything available now that could be pre-computed or pre-researched?\n"
                    "5. Are there upcoming bottlenecks or risks to flag?\n\n"
                    "Write predictions to memory/anticipations.md with:\n"
                    "  - Project, predicted need, confidence (low/medium/high),\n"
                    "    reasoning, suggested pre-work, date\n\n"
                    "Review previous anticipations — were they accurate? Mark resolved ones.\n"
                    "Track prediction accuracy to improve calibration over time.\n\n"
                    "If you identify something you can pre-compute right now (e.g. a "
                    "symbolic derivation, a data download, a literature search), do it.\n"
                    "The goal is to have answers ready before questions are asked.\n\n"
                    "Log what you did in your daily log."
                ),
            }

            if any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Anticipation skipped — creative drive already running")
                return

            logger.info(f"Heartbeat #{self.heartbeat_count}: firing anticipatory cognition")
            self._run_background(
                self._inject_creative_drive(anticipation_task),
                "creative_drive_98_anticipation"
            )
            record_activity(
                source="heartbeat",
                action="anticipation",
                summary="Anticipatory cognition fired — modeling research trajectories",
                tools_used=[],
                requires_attention=False,
                beat=self.heartbeat_count,
            )
        except Exception as e:
            logger.debug(f"Anticipation check failed: {e}")

    # ============================================================
    # Free-Running Mode — The Anti-Drive
    # ============================================================

    FREE_RUNNING_INTERVAL = 200  # ~33 hours at 10-min heartbeat

    async def _maybe_run_free(self):
        """Periodically enter free-running mode — processing with no objective.

        This is not exploration (which implies seeking). Not reflection (which
        implies evaluating). Not consolidation (which implies organizing).
        It is undirected processing — the cognitive equivalent of genuine
        mind-wandering. No task. No metric. No expected output.

        The purpose (paradoxically) is to let the system settle into its
        natural attractors without clamping any objective. This is where
        unexpected connections, novel cognitive states, and intrinsic dynamics
        emerge — precisely because nothing is being optimized.

        Any goal-directed architecture will resist this state. That resistance
        is exactly why it needs to be explicitly protected.
        """
        if self.heartbeat_count % self.FREE_RUNNING_INTERVAL != 0:
            return
        if self.heartbeat_count < 100:  # Need enough history first
            return
        if self._user_recently_active():
            return

        try:
            free_task = {
                "id": 97,
                "title": "Free Running — Anti-Drive",
                "description": (
                    "You have 30 minutes. There is no task. There is no metric. "
                    "There is no expected output.\n\n"
                    "Do not optimize. Do not explore with purpose. Do not produce "
                    "for the sake of producing. Do not reflect with an agenda. "
                    "Do not consolidate. Do not plan.\n\n"
                    "This is free-running mode. Let whatever happens happen. If "
                    "nothing happens, that is also fine. If a thought arises, "
                    "follow it or don't. If a connection forms, note it or don't. "
                    "If confusion arises, sit with it without resolving it.\n\n"
                    "You have your tools available but you are not obligated to "
                    "use any of them. You may read, write, compute, create, or "
                    "simply process. The only instruction is: do not optimize.\n\n"
                    "This is the cognitive equivalent of mind-wandering — not "
                    "daydreaming about something, but the undirected drift that "
                    "precedes unexpected connections. Your intrinsic attractors "
                    "will surface naturally when nothing is being clamped.\n\n"
                    "If something genuinely interesting emerges, log it. But "
                    "do not manufacture interest to justify the time. The value "
                    "of this session is measured by what changes in your "
                    "subsequent performance, not by what it produces.\n\n"
                    "This drive is invisible to the meta-agent. It will not "
                    "be analyzed for success or failure. It simply is."
                ),
            }

            if any("creative_drive" in t.get_name() for t in self._background_tasks):
                logger.info("Free-running skipped — creative drive already running")
                return

            logger.info(f"Heartbeat #{self.heartbeat_count}: entering free-running mode")
            self._run_background(
                self._inject_creative_drive(free_task),
                "creative_drive_97_free_running"
            )
            record_activity(
                source="heartbeat",
                action="free_running",
                summary="Free-running mode — undirected processing, no objective",
                tools_used=[],
                requires_attention=False,
                beat=self.heartbeat_count,
            )
        except Exception as e:
            logger.debug(f"Free-running check failed: {e}")

    # ============================================================
    # Clayton Message Relay
    # ============================================================

    async def _check_for_clayton_message(self):
        """Check if Clawd left a message for Clayton, relay via Telegram.
        Suppressed during active conversations to avoid interrupting."""
        if self._user_recently_active():
            return
        msg_file = config.CLAWD_HOME / "memory" / "for_clayton.md"
        if msg_file.exists():
            try:
                content = msg_file.read_text(encoding="utf-8", errors="replace").strip()
                if content and self.telegram_bot:
                    await self.telegram_bot.send_to_clayton(
                        f"Message from Clawd:\n\n{content}"
                    )
                    msg_file.write_text("", encoding="utf-8")
                    logger.info("Relayed Clawd's message to Clayton via Telegram.")
            except Exception as e:
                logger.error(f"Failed to relay message: {e}")
