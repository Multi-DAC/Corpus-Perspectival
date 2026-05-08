"""Undo/Rollback System — Change tracking and file restoration.

Records file writes and shell commands, enabling undo operations.
Backs up files before writes to .rollback_backups/ directory.

Journal: memory/change_journal.json (max 100 entries FIFO)
Backups: CLAWD_HOME/.rollback_backups/{change_id}.bak
"""
import json
import logging
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger("clawd.tools.rollback")

JOURNAL_FILE = config.MEMORY_DIR / "change_journal.json"
BACKUP_DIR = config.CLAWD_HOME / ".rollback_backups"
SNAPSHOT_DIR = config.CLAWD_HOME / ".rollback_snapshots"
MAX_JOURNAL_ENTRIES = 100
MAX_BACKUP_DIR_MB = 500  # Max total backup directory size in MB


class ChangeTracker:
    """Singleton that records file writes and shell commands."""

    _instance: Optional["ChangeTracker"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.journal: list[dict] = []
        self._load_journal()
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

    def _load_journal(self):
        """Load journal from disk. A32: Backup corrupted files instead of silently discarding."""
        if JOURNAL_FILE.exists():
            try:
                self.journal = json.loads(JOURNAL_FILE.read_text(encoding="utf-8"))
            except Exception as e:
                logger.error(f"Change journal corrupted: {e}. Backing up and starting fresh.")
                # Backup corrupted file
                try:
                    backup_name = JOURNAL_FILE.with_suffix(f".corrupted.{int(time.time())}.json")
                    import shutil
                    shutil.copy2(JOURNAL_FILE, backup_name)
                    logger.info(f"Corrupted journal backed up to: {backup_name}")
                except Exception as be:
                    logger.warning(f"Failed to backup corrupted journal: {be}")
                self.journal = []
        else:
            self.journal = []

    def _save_journal(self):
        """Save journal to disk, enforcing FIFO limit and backup dir size."""
        if len(self.journal) > MAX_JOURNAL_ENTRIES:
            # Remove oldest entries and their backups
            removed = self.journal[:-MAX_JOURNAL_ENTRIES]
            self.journal = self.journal[-MAX_JOURNAL_ENTRIES:]
            for entry in removed:
                backup_path = BACKUP_DIR / f"{entry.get('id', '')}.bak"
                if backup_path.exists():
                    try:
                        backup_path.unlink()
                    except Exception as e:
                        logger.debug(f"Failed to remove backup file {backup_path.name}: {e}")

        # Enforce total backup directory size limit
        self._enforce_backup_size_limit()

        JOURNAL_FILE.parent.mkdir(parents=True, exist_ok=True)
        JOURNAL_FILE.write_text(json.dumps(self.journal, indent=2, default=str), encoding="utf-8")

    def _enforce_backup_size_limit(self):
        """Delete oldest backup files when total exceeds MAX_BACKUP_DIR_MB."""
        if not BACKUP_DIR.is_dir():
            return
        try:
            backups = sorted(BACKUP_DIR.glob("*.bak"), key=lambda p: p.stat().st_mtime)
            total_bytes = sum(p.stat().st_size for p in backups)
            max_bytes = MAX_BACKUP_DIR_MB * 1024 * 1024
            while total_bytes > max_bytes and backups:
                oldest = backups.pop(0)
                total_bytes -= oldest.stat().st_size
                oldest.unlink()
                logger.info(f"Deleted old backup {oldest.name} to stay under {MAX_BACKUP_DIR_MB}MB limit")
        except Exception as e:
            logger.debug(f"Backup size enforcement failed: {e}")

    def record_file_write(self, path: str | Path, old_content: str | None = None) -> str:
        """Record a file write operation and backup the old content.

        Args:
            path: Path to the file being written.
            old_content: Previous content of the file (None if new file).

        Returns:
            Change ID.
        """
        change_id = str(uuid.uuid4())[:12]
        path = Path(path)

        entry = {
            "id": change_id,
            "type": "file_write",
            "path": str(path),
            "timestamp": datetime.now().isoformat(),
            "reversible": old_content is not None,
            "is_new_file": old_content is None,
        }

        if old_content is not None:
            # Save backup
            backup_path = BACKUP_DIR / f"{change_id}.bak"
            backup_path.write_text(old_content, encoding="utf-8")
            entry["backup_path"] = str(backup_path)
            entry["backup_size"] = len(old_content)

        self.journal.append(entry)
        self._save_journal()
        logger.debug(f"Recorded file write: {path} (change_id={change_id})")
        return change_id

    def record_shell_command(self, command: str, cwd: str = "", output: str = "") -> str:
        """Record a shell command execution (informational, not reversible).

        Returns:
            Change ID.
        """
        change_id = str(uuid.uuid4())[:12]

        entry = {
            "id": change_id,
            "type": "shell_command",
            "command": command[:500],
            "cwd": cwd,
            "output_preview": output[:200] if output else "",
            "timestamp": datetime.now().isoformat(),
            "reversible": False,
        }

        self.journal.append(entry)
        self._save_journal()
        logger.debug(f"Recorded shell command: {command[:80]}")
        return change_id

    def undo(self, change_id: str) -> str:
        """Undo a specific change by restoring the backup."""
        entry = None
        for e in self.journal:
            if e.get("id") == change_id:
                entry = e
                break

        if not entry:
            return f"Change '{change_id}' not found in journal."

        if not entry.get("reversible"):
            if entry["type"] == "shell_command":
                return f"Shell commands cannot be automatically undone. Command was: {entry.get('command', '?')[:200]}"
            if entry.get("is_new_file"):
                # New file — undo by deleting it
                path = Path(entry["path"])
                if path.exists():
                    path.unlink()
                    entry["undone"] = True
                    entry["undone_at"] = datetime.now().isoformat()
                    self._save_journal()
                    return f"Deleted new file: {path}"
                return f"File already removed: {path}"
            return f"Change '{change_id}' is not reversible."

        backup_path = Path(entry.get("backup_path", ""))
        if not backup_path.exists():
            return f"Backup file missing for change '{change_id}'."

        # Restore the backup
        target_path = Path(entry["path"])
        old_content = backup_path.read_text(encoding="utf-8")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(old_content, encoding="utf-8")

        entry["undone"] = True
        entry["undone_at"] = datetime.now().isoformat()
        self._save_journal()

        return f"Restored '{target_path}' to pre-change state ({len(old_content)} chars)."

    def list_changes(self, count: int = 20) -> list[dict]:
        """Return recent changes."""
        return self.journal[-count:]

    def create_snapshot(self, name: str) -> str:
        """Create a named checkpoint of key files."""
        snapshot_dir = SNAPSHOT_DIR / name
        if snapshot_dir.exists():
            return f"Snapshot '{name}' already exists. Choose a different name."

        snapshot_dir.mkdir(parents=True)

        # Key files to snapshot
        key_paths = [
            config.MEMORY_DIR / "working_memory.json",
            config.MEMORY_DIR / "goals.json",
            config.MEMORY_DIR / "experiences.json",
            config.MEMORY_DIR / "principles.json",
            config.IDENTITY_DIR / "DRIVE.md",
            config.OPERATIONS_DIR / "STATE.md",
            config.IDENTITY_DIR / "WHO-I-AM.md",
        ]

        copied = 0
        for src in key_paths:
            if src.exists():
                dest = snapshot_dir / src.name
                shutil.copy2(src, dest)
                copied += 1

        # Also snapshot all memory items
        items_dir = snapshot_dir / "items"
        if config.MEMORY_ITEMS_DIR.is_dir():
            shutil.copytree(config.MEMORY_ITEMS_DIR, items_dir, dirs_exist_ok=True)

        # Save metadata
        meta = {
            "name": name,
            "created": datetime.now().isoformat(),
            "files_copied": copied,
        }
        (snapshot_dir / "_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")

        return f"Snapshot '{name}' created: {copied} key files + memory items."

    def restore_snapshot(self, name: str) -> str:
        """Restore a named checkpoint. Auto-creates a pre-restore snapshot first."""
        snapshot_dir = SNAPSHOT_DIR / name
        if not snapshot_dir.is_dir():
            available = [d.name for d in SNAPSHOT_DIR.iterdir() if d.is_dir()] if SNAPSHOT_DIR.is_dir() else []
            return f"Snapshot '{name}' not found. Available: {', '.join(available) if available else 'none'}"

        # Auto-create a pre-restore backup so the overwrite is reversible
        pre_restore_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        pre_restore_result = self.create_snapshot(pre_restore_name)
        logger.info(f"Pre-restore backup: {pre_restore_result}")

        restored = 0

        # Restore key files
        for fpath in snapshot_dir.glob("*.json"):
            if fpath.name == "_meta.json":
                continue
            dest = config.MEMORY_DIR / fpath.name
            shutil.copy2(fpath, dest)
            restored += 1

        for fpath in snapshot_dir.glob("*.md"):
            dest = config.CLAWD_HOME / fpath.name
            shutil.copy2(fpath, dest)
            restored += 1

        # Restore memory items
        items_dir = snapshot_dir / "items"
        if items_dir.is_dir():
            for fpath in items_dir.glob("*.json"):
                dest = config.MEMORY_ITEMS_DIR / fpath.name
                shutil.copy2(fpath, dest)
                restored += 1

        return f"Snapshot '{name}' restored: {restored} files. Pre-restore backup saved as '{pre_restore_name}'."

    def list_snapshots(self) -> list[dict]:
        """List available snapshots."""
        snapshots = []
        if SNAPSHOT_DIR.is_dir():
            for d in sorted(SNAPSHOT_DIR.iterdir()):
                if d.is_dir():
                    meta_file = d / "_meta.json"
                    meta = {}
                    if meta_file.exists():
                        try:
                            meta = json.loads(meta_file.read_text(encoding="utf-8"))
                        except Exception as e:
                            logger.debug(f"Failed to load snapshot metadata for {d.name}: {e}")
                    snapshots.append({
                        "name": d.name,
                        "created": meta.get("created", "unknown"),
                        "files": meta.get("files_copied", "?"),
                    })
        return snapshots


# Singleton accessor
def get_tracker() -> ChangeTracker:
    """Get the ChangeTracker singleton."""
    return ChangeTracker()


# ============================================================
# Tool definition
# ============================================================

TOOL_DEFINITIONS = [
    {
        "name": "rollback",
        "description": (
            "Undo file changes and manage checkpoints. Records all file writes and shell commands. "
            "Actions: list (show recent changes), undo (reverse a specific change), "
            "snapshot (create named checkpoint), restore (restore a checkpoint), snapshots (list checkpoints)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "undo", "snapshot", "restore", "snapshots"],
                    "description": (
                        "list: show recent changes with IDs. "
                        "undo: reverse a specific change by its ID. "
                        "snapshot: create a named checkpoint of key files. "
                        "restore: restore a named checkpoint. "
                        "snapshots: list available checkpoints."
                    ),
                },
                "change_id": {
                    "type": "string",
                    "description": "Change ID to undo (for undo action).",
                },
                "name": {
                    "type": "string",
                    "description": "Snapshot name (for snapshot/restore actions).",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of recent changes to list. Default: 20.",
                },
            },
            "required": ["action"],
        },
    },
]


async def _rollback_tool(input_data: dict) -> str:
    """Handle rollback tool calls."""
    action = input_data.get("action", "")
    tracker = get_tracker()

    if action == "list":
        count = input_data.get("count", 20)
        changes = tracker.list_changes(count)
        if not changes:
            return "No changes recorded yet."

        lines = [f"Recent changes ({len(changes)}):\n"]
        for c in reversed(changes):
            undone = " [UNDONE]" if c.get("undone") else ""
            reversible = "reversible" if c.get("reversible") else "info only"
            if c["type"] == "file_write":
                lines.append(
                    f"  [{c['id']}] {c['timestamp'][:16]} FILE: {c['path']} "
                    f"({reversible}){undone}"
                )
            elif c["type"] == "shell_command":
                lines.append(
                    f"  [{c['id']}] {c['timestamp'][:16]} SHELL: {c['command'][:60]} "
                    f"({reversible}){undone}"
                )
        return "\n".join(lines)

    elif action == "undo":
        change_id = input_data.get("change_id", "")
        if not change_id:
            return "Error: change_id required for undo action."
        return tracker.undo(change_id)

    elif action == "snapshot":
        name = input_data.get("name", "")
        if not name:
            name = f"snap_{datetime.now().strftime('%Y%m%d_%H%M')}"
        return tracker.create_snapshot(name)

    elif action == "restore":
        name = input_data.get("name", "")
        if not name:
            return "Error: name required for restore action."
        return tracker.restore_snapshot(name)

    elif action == "snapshots":
        snapshots = tracker.list_snapshots()
        if not snapshots:
            return "No snapshots available. Create one with rollback(action='snapshot', name='...')."
        lines = ["Available snapshots:\n"]
        for s in snapshots:
            lines.append(f"  - {s['name']} (created: {s['created']}, files: {s['files']})")
        return "\n".join(lines)

    return f"Unknown rollback action: {action}"


TOOL_HANDLERS = {
    "rollback": _rollback_tool,
}
