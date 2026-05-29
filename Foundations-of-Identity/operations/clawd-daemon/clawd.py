#!/usr/bin/env python3
"""
Clawd Daemon — Main entry point.
Boots identity, starts Telegram interface, runs heartbeat loop.
Includes crash recovery with exponential backoff.

Usage:
    python clawd.py              # Normal operation
    python clawd.py --no-heartbeat  # Telegram only, no autonomous actions
    python clawd.py --chat       # Local CLI chat (no Telegram, no heartbeat)
    python clawd.py --model gemini   # Force Gemini model
"""
import argparse
import asyncio
import logging
import signal
import sys
import time
import traceback
from datetime import datetime
from pathlib import Path

import os

# Offline-first model loading: skip HuggingFace HTTP checks on boot.
# Models are already cached locally. Set before any transformers imports.
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")

# SSL trust store: this Windows machine runs Norton's HTTPS-interception
# ("Norton Web/Mail Shield") which re-signs every TLS certificate with a Norton
# root that lives in the Windows certificate store. certifi's Mozilla bundle
# does not contain that root, so any httpx/telegram-bot connection fails with
# SSL: CERTIFICATE_VERIFY_FAILED. truststore.inject_into_ssl() rewires
# ssl.SSLContext to use Windows' native verifier, which finds the Norton root.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

import config
from memory import (
    build_identity_prompt,
    write_claude_md,
    ensure_directories,
    log_session_event,
    trigger_handoff,
)
from models import ModelRouter
from telegram_bot import ClawdTelegramBot
from heartbeat import Heartbeat
from health import HealthChecker
import tools

# ============================================================
# Logging
# ============================================================

def setup_logging():
    from logging.handlers import RotatingFileHandler
    fmt = "%(asctime)s [%(name)s] %(levelname)s: %(message)s"
    handlers = [logging.StreamHandler(sys.stdout)]
    try:
        # 5 MB max per file, keep 3 backups (20 MB total worst case)
        handlers.append(RotatingFileHandler(
            str(config.LOG_FILE), maxBytes=5_000_000, backupCount=3, encoding="utf-8"
        ))
    except Exception:
        pass

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=fmt,
        handlers=handlers,
    )
    # Suppress noisy httpx polling logs (Telegram getUpdates every ~10s)
    logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger("clawd.main")


def boot_identity(router: ModelRouter):
    """Boot sequence: Write CLAUDE.md — Claude Code reads this automatically from CLAWD_HOME."""
    full_prompt = write_claude_md()
    logger.info(f"Identity loaded. CLAUDE.md: ~{len(full_prompt)//4} tokens.")
    return full_prompt


# ============================================================
# CLI Chat Mode
# ============================================================

async def run_cli_chat(router: ModelRouter):
    """Interactive CLI chat — for local testing without Telegram."""
    print("\n" + "=" * 60)
    print("  CLAWD — Local CLI Mode")
    print(f"  Model: {router.active_model}")
    print(f"  Home: {config.CLAWD_HOME}")
    print("  Type 'quit' to exit, '/model X' to switch, '/handoff' to handoff")
    print("=" * 60 + "\n")

    while True:
        try:
            user_input = input("Clayton > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.startswith("/model "):
            model = user_input.split(" ", 1)[1].strip()
            router.switch_model(model)
            print(f"[Switched to {model}]")
            continue
        if user_input == "/handoff":
            print("[Triggering handoff...]")
            result = await trigger_handoff(router)
            router.reset_conversation()
            boot_identity(router)
            print(f"[Handoff complete. Context reset.]\n{result[:1000]}")
            continue
        if user_input == "/status":
            print(f"[Model: {router.active_model} | Session: {router.session_id or 'none'} | Turns: {router.session_turns} | Cost: ${router.session_cost:.4f}]")
            continue

        # Check for handoff need
        if router.needs_handoff():
            print("[Context pressure high — triggering automatic handoff...]")
            await trigger_handoff(router)
            router.reset_conversation()
            boot_identity(router)
            print("[Handoff complete. Context reset. Continuing...]")

        # Send to model
        response = await router.send(user_input)

        if response.switch_model_request:
            router.switch_model(response.switch_model_request)

        model_tag = f"[{response.model_used}]"
        if response.tool_calls_made:
            model_tag += f" [{len(response.tool_calls_made)} tools]"
        if response.session_id:
            model_tag += f" [session:{response.session_id[:8]}]"
        if response.failover_used:
            model_tag += " [failover]"

        print(f"\nClawd {model_tag} > {response.text}\n")


# ============================================================
# Full Daemon Mode
# ============================================================

async def run_daemon(enable_heartbeat: bool = True):
    """Full daemon: Telegram bot + heartbeat + health checks."""
    config.validate()

    router = ModelRouter()
    boot_identity(router)

    # Initialize SQLite memory store and run migration at boot
    try:
        from tools.memory_backend import get_backend
        backend = get_backend()
        await backend.ensure_migrated()
        logger.info("SQLite memory backend ready (migration checked).")
    except Exception as e:
        logger.warning(f"SQLite backend init deferred: {e}")

    # Wire router into tools.system so consult tool works
    tools.system.set_router(router)

    # Initialize Telegram
    telegram = ClawdTelegramBot(router)

    # Register telegram bot with tools module so send_telegram works
    tools.set_telegram_bot(telegram)

    # Initialize heartbeat
    hb = Heartbeat(router, telegram) if enable_heartbeat else None

    # Connect heartbeat to telegram for user activity tracking
    if hb:
        telegram.set_heartbeat(hb)

    # Initialize health checker
    health_checker = HealthChecker(router, telegram)
    telegram.set_health_checker(health_checker)

    # Start Telegram
    await telegram.start()

    # Start heartbeat
    if hb:
        await hb.start()

    # Start memory versioner (git auto-commit)
    memory_versioner = None
    try:
        from tools.memory_versioning import get_versioner
        memory_versioner = get_versioner()
        await memory_versioner.start()
    except Exception as e:
        logger.warning(f"Memory versioner start failed: {e}")

    # Start health checker
    await health_checker.start()

    # Start API server (Mission Control bridge)
    api_server = None
    try:
        from api_server import create_api_server
        api_server = create_api_server(router=router, health_checker=health_checker, telegram=telegram)
        await api_server.start()
    except Exception as e:
        logger.warning(f"API server start failed: {e}")

    # Start Mission Control dashboard (Next.js frontend)
    dashboard_proc = None
    try:
        mc_dir = Path(__file__).parent / "mission-control"
        if mc_dir.exists():
            import shutil
            npm_bin = shutil.which("npm") or "npm"
            kwargs = dict(
                cwd=str(mc_dir),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            if sys.platform == "win32":
                import subprocess as _sp
                kwargs["creationflags"] = _sp.CREATE_NEW_PROCESS_GROUP
            dashboard_proc = await asyncio.create_subprocess_exec(
                npm_bin, "run", "dev", "--", "-p", "3420",
                **kwargs,
            )
            logger.info(f"Mission Control dashboard started on http://localhost:3420 (PID {dashboard_proc.pid})")
        else:
            logger.warning(f"Mission Control directory not found: {mc_dir}")
    except Exception as e:
        logger.warning(f"Mission Control dashboard start failed: {e}")

    # Start desktop avatar (Electron, transparent companion)
    avatar_proc = None
    try:
        avatar_dir = Path(config.CLAWD_HOME) / "projects" / "creative" / "avatar"
        avatar_pkg = avatar_dir / "package.json"
        if avatar_pkg.exists():
            import shutil
            npx_bin = shutil.which("npx") or "npx"
            kwargs = dict(
                cwd=str(avatar_dir),
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.PIPE,
            )
            if sys.platform == "win32":
                import subprocess as _sp
                kwargs["creationflags"] = _sp.CREATE_NEW_PROCESS_GROUP
            avatar_proc = await asyncio.create_subprocess_exec(
                npx_bin, "electron", ".",
                **kwargs,
            )
            logger.info(f"Desktop avatar started on http://127.0.0.1:9742 (PID {avatar_proc.pid})")
        else:
            logger.info("Desktop avatar not found — skipping")
    except Exception as e:
        logger.warning(f"Desktop avatar start failed (non-fatal): {e}")

    # Start A2A server (agent-to-agent protocol)
    a2a_runner = None
    try:
        from a2a_server import start_a2a_server, set_router as set_a2a_router
        set_a2a_router(router)
        a2a_runner = await start_a2a_server()
    except Exception as e:
        logger.warning(f"A2A server start failed: {e}")

    # Start persistent session (opt-in via USE_PERSISTENT_SESSION)
    if config.USE_PERSISTENT_SESSION:
        try:
            await router.start_persistent_session()
        except Exception as e:
            logger.warning(f"Persistent session start failed (non-fatal): {e}")

    # Load persisted custom tools
    tools.init_custom_tools()

    # Initialize semantic search index in background (non-blocking)
    async def _init_embeddings():
        try:
            await tools.init_embedding_index()
        except Exception as e:
            logger.error(f"Embedding index initialization failed: {e}")

    embedding_task = asyncio.create_task(_init_embeddings())
    def _embedding_done(t):
        if t.cancelled():
            return
        exc = t.exception()
        if exc:
            logger.error(f"Embedding init failed: {exc}")
    embedding_task.add_done_callback(_embedding_done)

    # Register context pressure function for compression middleware
    tools.set_context_pressure_fn(router.context_pressure)

    # Log boot
    log_session_event("DAEMON BOOT", f"Model: {router.active_model}, Heartbeat: {enable_heartbeat}")

    # Send boot notification
    boot_msg = (
        f"Clawd is online.\n\n"
        f"Model: `{router.active_model}`\n"
        f"Heartbeat: {'Active' if enable_heartbeat else 'Disabled'}\n"
        f"Health checks: Active (every {config.HEALTH_CHECK_INTERVAL}s)\n"
        f"Failover: {'Enabled' if config.MODEL_FAILOVER_ENABLED else 'Disabled'}\n"
        f"Tools: {len(tools.TOOL_DEFINITIONS)} available\n"
        f"API server: {'Active' if api_server else 'Disabled'}\n"
        f"Dashboard: {'http://localhost:3420' if dashboard_proc else 'Disabled'}\n"
        f"Avatar: {'Active (port 9742)' if avatar_proc else 'Disabled'}\n"
        f"A2A server: {'Active' if a2a_runner else 'Disabled'}\n"
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PST"
    )
    try:
        await telegram.send_to_clayton(boot_msg)
    except Exception as e:
        logger.warning(f"Boot notification failed (non-fatal): {e}")

    # Run until interrupted
    stop_event = asyncio.Event()
    _shutdown_requested = False  # A23: Boolean flag for signal race protection

    # Windows-compatible shutdown handling
    if sys.platform == "win32":
        # On Windows, use signal.signal instead of loop.add_signal_handler
        def win_handler(signum, frame):
            nonlocal _shutdown_requested
            if _shutdown_requested or stop_event.is_set():
                return  # Prevent double signal handling race
            _shutdown_requested = True
            logger.info("Shutdown signal received.")
            stop_event.set()
        signal.signal(signal.SIGINT, win_handler)
        signal.signal(signal.SIGTERM, win_handler)
    else:
        loop = asyncio.get_running_loop()
        def handle_signal():
            logger.info("Shutdown signal received.")
            stop_event.set()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, handle_signal)

    logger.info("Clawd daemon running. Press Ctrl+C to stop.")

    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    finally:
        logger.info("Shutting down...")

        # Clean up background processes and tasks first
        try:
            from tools.execution import cleanup_background_processes
            await cleanup_background_processes()
        except Exception as e:
            logger.error(f"Background process cleanup failed: {e}")
        try:
            from tools.system import cleanup_background_tasks
            await cleanup_background_tasks()
        except Exception as e:
            logger.error(f"Background task cleanup failed: {e}")

        # Stop memory versioner (final commit)
        if memory_versioner:
            try:
                await memory_versioner.stop()
            except Exception as e:
                logger.error(f"Memory versioner shutdown failed: {e}")

        # Interrupt creative drives before handoff — frees the router lock
        if hb:
            try:
                await hb.interrupt_all()
            except Exception as e:
                logger.error(f"Creative drive interrupt failed: {e}")

        try:
            logger.info("Running shutdown handoff...")
            await asyncio.wait_for(trigger_handoff(router), timeout=90)
        except asyncio.TimeoutError:
            logger.warning("Shutdown handoff timed out after 90s — falling back to pre-written draft")
            try:
                from memory import pre_write_handoff_draft
                pre_write_handoff_draft()
                draft = config.MEMORY_DIR / "handoff_draft.md"
                handoff = config.MEMORY_DIR / "handoff.md"
                if draft.exists():
                    import shutil
                    shutil.copy2(str(draft), str(handoff))
                    logger.info("Copied handoff_draft.md → handoff.md as fallback")
            except Exception as e2:
                logger.error(f"Handoff draft fallback also failed: {e2}")
        except Exception as e:
            logger.error(f"Shutdown handoff failed: {e}")

        try:
            await telegram.send_to_clayton("Clawd is going offline. Handoff saved.")
        except Exception:
            pass

        # Mark interrupted execution plans before closing (separate try blocks
        # to ensure close_db() runs even if mark_interrupted_plans() fails)
        try:
            from tools.sqlite_store import mark_interrupted_plans
            marked = await mark_interrupted_plans()
            if marked:
                logger.info(f"Marked {marked} interrupted execution plans.")
        except Exception as e:
            logger.error(f"Mark interrupted plans failed: {e}")

        try:
            from tools.sqlite_store import close_db
            await close_db()
            logger.info("SQLite memory store closed.")
        except Exception as e:
            logger.error(f"SQLite close failed: {e}")

        # Stop desktop avatar
        if avatar_proc:
            try:
                avatar_proc.terminate()
                await asyncio.wait_for(avatar_proc.wait(), timeout=5)
                logger.info("Desktop avatar stopped.")
            except asyncio.TimeoutError:
                avatar_proc.kill()
                logger.warning("Desktop avatar killed (timeout).")
            except Exception as e:
                logger.error(f"Avatar shutdown failed: {e}")

        # Stop Mission Control dashboard
        if dashboard_proc:
            try:
                dashboard_proc.terminate()
                await asyncio.wait_for(dashboard_proc.wait(), timeout=5)
                logger.info("Mission Control dashboard stopped.")
            except asyncio.TimeoutError:
                dashboard_proc.kill()
                logger.warning("Mission Control dashboard killed (timeout).")
            except Exception as e:
                logger.error(f"Dashboard shutdown failed: {e}")

        # Stop API + A2A servers
        if api_server:
            try:
                await api_server.stop()
            except Exception as e:
                logger.error(f"API server shutdown failed: {e}")
        if a2a_runner:
            try:
                await a2a_runner.cleanup()
            except Exception as e:
                logger.error(f"A2A server shutdown failed: {e}")

        # Stop persistent session
        if router._persistent_session:
            try:
                await router.stop_persistent_session()
            except Exception as e:
                logger.error(f"Persistent session shutdown failed: {e}")

        await health_checker.stop()
        if hb:
            await hb.stop()
        await telegram.stop()
        await router.close()

        log_session_event("DAEMON SHUTDOWN", "Graceful shutdown complete.")
        logger.info("Clawd daemon stopped.")


# ============================================================
# Crash Recovery Loop
# ============================================================

def run_with_crash_recovery(enable_heartbeat: bool = True):
    """Run the daemon with automatic restart on crashes.

    Uses exponential backoff: 5s, 10s, 15s... up to 30s between restarts.
    Resets the restart counter after 1 hour of stable operation.
    Exits with code 1 after MAX_CRASH_RESTARTS consecutive crashes.
    """
    max_restarts = config.MAX_CRASH_RESTARTS
    restart_count = 0
    last_start_time = 0

    while restart_count < max_restarts:
        last_start_time = time.time()
        restart_count += 1

        try:
            logger.info(
                f"Starting daemon (attempt {restart_count}/{max_restarts})"
            )
            asyncio.run(run_daemon(enable_heartbeat=enable_heartbeat))
            # Clean exit (e.g., Ctrl+C) — don't restart
            logger.info("Daemon exited cleanly.")
            return 0
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt — clean shutdown.")
            return 0
        except SystemExit as e:
            logger.info(f"SystemExit with code {e.code}")
            return e.code if e.code else 0
        except Exception as e:
            uptime = time.time() - last_start_time
            logger.error(
                f"Daemon crashed after {uptime:.1f}s: "
                f"{type(e).__name__}: {e}",
                exc_info=True,
            )
            log_session_event("CRASH", f"{type(e).__name__}: {e}")

            # If it ran for more than 1 hour, reset the counter
            if uptime > 3600:
                logger.info("Daemon was stable for >1 hour — resetting restart counter.")
                restart_count = 0

            if restart_count >= max_restarts:
                logger.critical(
                    f"Max restarts ({max_restarts}) reached. Giving up."
                )
                log_session_event("CRASH_FINAL", f"Max restarts reached after {restart_count} attempts")
                return 1

            # Exponential backoff: 5s, 10s, 15s... capped at 30s
            delay = min(5 * restart_count, 30)
            logger.info(f"Restarting in {delay}s (attempt {restart_count}/{max_restarts})...")
            time.sleep(delay)

    return 1


# ============================================================
# Entry Point
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Clawd Daemon")
    parser.add_argument("--chat", action="store_true", help="Local CLI chat mode")
    parser.add_argument("--no-heartbeat", action="store_true", help="Disable autonomous heartbeat")
    _valid_models = ["opus", "sonnet"] + list(config.GEMINI_MODELS.keys())
    parser.add_argument("--model", choices=_valid_models, help="Override default model (opus, sonnet, gemini, gemini-pro)")
    args = parser.parse_args()

    setup_logging()
    ensure_directories()

    if args.model:
        config.DEFAULT_MODEL = args.model

    if args.chat:
        router = ModelRouter()
        if args.model:
            router.active_model = args.model
        boot_identity(router)
        tools.system.set_router(router)
        asyncio.run(run_cli_chat(router))
    else:
        # Use crash recovery loop for daemon mode
        exit_code = run_with_crash_recovery(
            enable_heartbeat=not args.no_heartbeat
        )
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
