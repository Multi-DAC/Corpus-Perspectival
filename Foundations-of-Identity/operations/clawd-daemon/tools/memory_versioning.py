"""Git-Versioned Memory — Temporal navigation of Clawd's memory state.

Auto-commits memory changes every hour and provides tools for
navigating memory history: status, log, diff, checkout, restore.

Uses git via subprocess (same as existing git_tool.py).
No new dependencies required.
"""
import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.memory_versioning")

# Whitelisted paths for auto-commit (relative to CLAWD_HOME)
_WHITELIST_PATTERNS = [
    "memory/*.md",
    "memory/*.json",
    "memory/items/*.json",
    "memory/categories/*.json",
    "memory/knowledge_graph/*.json",
    "memory/skillbank/*.json",
    "memory/daily-summaries/*.md",
    "memory/archive/*.md",
    "*.md",  # Identity files (SOUL.md, DRIVE.md, etc.)
]

# Files to exclude (should be in .gitignore)
_EXCLUDE_PATTERNS = [
    ".env",
    "*.pyc",
    "__pycache__/",
    "output/*.png",
    "output/*.jpg",
    "clawd_memory.db",
    "clawd_daemon.log",
    "logs/",
    ".rollback_backups/",
    "screenshots/",
]


async def _run_git(args: list[str], cwd: str = None, timeout: int = 30) -> tuple[str, str, int]:
    """Run a git command and return (stdout, stderr, returncode)."""
    cmd = [config.GIT_BIN] + args
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd or str(config.CLAWD_HOME),
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (
            stdout.decode("utf-8", errors="replace").strip(),
            stderr.decode("utf-8", errors="replace").strip(),
            proc.returncode,
        )
    except asyncio.TimeoutError:
        return "", "Git command timed out", 1
    except FileNotFoundError:
        return "", "Git not found. Ensure git is installed.", 1
    except Exception as e:
        return "", str(e), 1


async def _ensure_git_repo() -> bool:
    """Ensure CLAWD_HOME is a git repo. Initialize if not."""
    git_dir = config.CLAWD_HOME / ".git"
    if git_dir.is_dir():
        return True

    logger.info("Initializing git repo in %s", config.CLAWD_HOME)
    stdout, stderr, code = await _run_git(["init"])
    if code != 0:
        logger.error("Failed to init git repo: %s", stderr)
        return False

    # Create .gitignore
    gitignore = config.CLAWD_HOME / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("\n".join(_EXCLUDE_PATTERNS) + "\n", encoding="utf-8")
        await _run_git(["add", ".gitignore"])
        await _run_git(["commit", "-m", "init: add .gitignore"])

    return True


async def _ensure_gitignore():
    """Ensure .gitignore has all required exclusions."""
    gitignore = config.CLAWD_HOME / ".gitignore"
    existing = set()
    if gitignore.exists():
        existing = set(gitignore.read_text(encoding="utf-8").strip().split("\n"))

    missing = [p for p in _EXCLUDE_PATTERNS if p not in existing]
    if missing:
        with open(gitignore, "a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(missing) + "\n")


class MemoryVersioner:
    """Background auto-commit worker for memory files."""

    def __init__(self, interval: int = None):
        self.interval = interval or getattr(config, "MEMORY_AUTO_COMMIT_INTERVAL", 3600)
        self.running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the auto-commit background loop."""
        if not getattr(config, "MEMORY_GIT_ENABLED", True):
            logger.info("Memory git versioning disabled by config.")
            return

        if not await _ensure_git_repo():
            logger.error("Cannot start MemoryVersioner — git init failed.")
            return

        await _ensure_gitignore()
        self.running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("MemoryVersioner started: auto-commit every %ds", self.interval)

    async def stop(self):
        """Stop the auto-commit loop and do a final commit."""
        self.running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        # Final commit on shutdown
        await self._auto_commit("auto: final memory snapshot (shutdown)")
        logger.info("MemoryVersioner stopped.")

    async def _loop(self):
        """Background loop: auto-commit every interval. Exponential backoff on failure."""
        consecutive_failures = 0
        max_consecutive_failures = 10
        while self.running:
            try:
                await asyncio.sleep(self.interval)
                # Pre-write handoff draft each cycle (safety net for shutdown)
                try:
                    from memory import pre_write_handoff_draft
                    pre_write_handoff_draft()
                except Exception as e:
                    logger.warning(f"Handoff draft pre-write failed: {e}")
                now = datetime.now().strftime("%Y-%m-%d %H:%M")
                success = await self._auto_commit(f"auto: memory snapshot {now}")
                if success or not consecutive_failures:
                    consecutive_failures = 0
                    continue
                # Commit returned False (no changes) — not a failure
                consecutive_failures = 0
            except asyncio.CancelledError:
                break
            except Exception as e:
                consecutive_failures += 1
                if consecutive_failures >= max_consecutive_failures:
                    logger.error(
                        "MemoryVersioner: %d consecutive failures, disabling auto-commit. Last error: %s",
                        consecutive_failures, e
                    )
                    break
                # Exponential backoff: 60s, 120s, 240s, ... capped at 3600s
                backoff = min(60 * (2 ** (consecutive_failures - 1)), 3600)
                logger.error("MemoryVersioner error (attempt %d/%d): %s. Retrying in %ds.",
                             consecutive_failures, max_consecutive_failures, e, backoff)
                await asyncio.sleep(backoff)

    async def _auto_commit(self, message: str) -> bool:
        """Stage whitelisted files and commit if there are changes."""
        if not await _ensure_git_repo():
            return False

        # Stage whitelisted paths — check return codes
        any_staged = False
        for pattern in _WHITELIST_PATTERNS:
            _, stderr, code = await _run_git(["add", "--all", "--", pattern])
            if code != 0:
                if "did not match any files" in stderr or "No such file or directory" in stderr:
                    logger.debug("git add: no files for pattern '%s' (expected)", pattern)
                else:
                    logger.warning("git add failed for pattern '%s': %s", pattern, stderr)
            else:
                any_staged = True

        if not any_staged:
            logger.debug("No patterns staged successfully.")
            return False

        # Check if there are staged changes
        stdout, _, code = await _run_git(["diff", "--cached", "--stat"])
        if not stdout.strip():
            logger.debug("No memory changes to commit.")
            return False

        # Commit
        _, stderr, code = await _run_git(["commit", "-m", message])
        if code == 0:
            logger.info("Memory auto-committed: %s", message)
            return True
        else:
            logger.warning("Auto-commit failed (code %d): %s — resetting staging area", code, stderr)
            # Reset staging area to avoid stale staged changes persisting
            await _run_git(["reset", "HEAD"])
            return False

    async def commit_now(self, message: str = None) -> str:
        """Force an immediate commit with a custom message."""
        if not message:
            message = f"manual: memory snapshot {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        success = await self._auto_commit(message)
        return f"Committed: {message}" if success else "No changes to commit."


# Singleton instance (created at module level, started by clawd.py)
_versioner: Optional[MemoryVersioner] = None


def get_versioner() -> MemoryVersioner:
    """Get or create the singleton MemoryVersioner."""
    global _versioner
    if _versioner is None:
        _versioner = MemoryVersioner()
    return _versioner


# ============================================================
# Tool: memory_version
# ============================================================

TOOL_DEFINITIONS = [
    {
        "name": "memory_version",
        "description": (
            "Navigate Clawd's memory history using git versioning. "
            "Auto-commits memory changes every hour. "
            "Actions: status (git status of memory), log (commit history), "
            "diff (changes between dates/commits), checkout (view memory at past date), "
            "restore (restore a file from a past commit), commit_now (force immediate commit)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["status", "log", "diff", "checkout", "restore", "commit_now"],
                    "description": (
                        "status: show current memory file changes. "
                        "log: show recent commit history. "
                        "diff: show changes between dates or commits. "
                        "checkout: show memory state at a specific date/commit. "
                        "restore: restore a file from a past commit. "
                        "commit_now: force immediate commit."
                    ),
                },
                "count": {
                    "type": "integer",
                    "description": "Number of log entries to show (for log action). Default: 10.",
                },
                "commit": {
                    "type": "string",
                    "description": "Commit hash (for diff, checkout, restore actions).",
                },
                "commit2": {
                    "type": "string",
                    "description": "Second commit hash for diff range (commit..commit2).",
                },
                "date": {
                    "type": "string",
                    "description": "Date string (YYYY-MM-DD) for checkout/diff by date.",
                },
                "file_path": {
                    "type": "string",
                    "description": "File path to restore (relative to CLAWD_HOME, for restore action).",
                },
                "message": {
                    "type": "string",
                    "description": "Custom commit message (for commit_now action).",
                },
            },
            "required": ["action"],
        },
    },
]


async def _memory_version(input_data: dict) -> str:
    """Handle memory_version tool calls."""
    action = input_data.get("action", "")

    if not await _ensure_git_repo():
        return "Error: Git repo not available in CLAWD_HOME."

    if action == "status":
        stdout, stderr, code = await _run_git(["status", "--short"])
        if code != 0:
            return f"Git status error: {stderr}"
        return stdout if stdout else "No changes (working tree clean)."

    elif action == "log":
        count = input_data.get("count", 10)
        stdout, stderr, code = await _run_git([
            "log", f"--max-count={count}",
            "--format=%h %ai %s",
            "--", "memory/", "*.md",
        ])
        if code != 0:
            return f"Git log error: {stderr}"
        return stdout if stdout else "No commits found for memory files."

    elif action == "diff":
        commit1 = input_data.get("commit", "")
        commit2 = input_data.get("commit2", "")
        date = input_data.get("date", "")

        if date:
            # Find commit nearest to date
            stdout, _, _ = await _run_git([
                "log", "--format=%H", "--max-count=1",
                f"--before={date}T23:59:59",
                "--", "memory/", "*.md",
            ])
            if stdout:
                commit1 = stdout.split("\n")[0]
            else:
                return f"No commits found before {date}."

        if commit1 and commit2:
            stdout, stderr, code = await _run_git(["diff", f"{commit1}..{commit2}", "--stat", "--", "memory/", "*.md"])
        elif commit1:
            stdout, stderr, code = await _run_git(["diff", commit1, "HEAD", "--stat", "--", "memory/", "*.md"])
        else:
            stdout, stderr, code = await _run_git(["diff", "--stat", "--", "memory/", "*.md"])

        if code != 0:
            return f"Git diff error: {stderr}"
        return stdout if stdout else "No differences found."

    elif action == "checkout":
        commit = input_data.get("commit", "")
        date = input_data.get("date", "")
        file_path = input_data.get("file_path", "")

        if date and not commit:
            stdout, _, _ = await _run_git([
                "log", "--format=%H %ai %s", "--max-count=1",
                f"--before={date}T23:59:59",
                "--", "memory/", "*.md",
            ])
            if stdout:
                commit = stdout.split()[0]
            else:
                return f"No commits found before {date}."

        if not commit:
            return "Error: commit or date required for checkout action."

        if file_path:
            # Show a specific file at that commit
            stdout, stderr, code = await _run_git(["show", f"{commit}:{file_path}"])
            if code != 0:
                return f"Error: {stderr}"
            return f"File '{file_path}' at commit {commit[:8]}:\n\n{stdout[:5000]}"
        else:
            # Show list of files at that commit
            stdout, stderr, code = await _run_git(["ls-tree", "--name-only", "-r", commit, "--", "memory/"])
            if code != 0:
                return f"Error: {stderr}"
            return f"Memory files at commit {commit[:8]}:\n{stdout}"

    elif action == "restore":
        commit = input_data.get("commit", "")
        file_path = input_data.get("file_path", "")
        if not commit or not file_path:
            return "Error: commit and file_path required for restore action."

        # Get content from past commit
        stdout, stderr, code = await _run_git(["show", f"{commit}:{file_path}"])
        if code != 0:
            return f"Error retrieving file: {stderr}"

        # Write it back
        target = config.CLAWD_HOME / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(stdout, encoding="utf-8")
        return f"Restored '{file_path}' from commit {commit[:8]} ({len(stdout)} chars)."

    elif action == "commit_now":
        versioner = get_versioner()
        message = input_data.get("message")
        return await versioner.commit_now(message)

    return f"Unknown memory_version action: {action}"


TOOL_HANDLERS = {
    "memory_version": _memory_version,
}
