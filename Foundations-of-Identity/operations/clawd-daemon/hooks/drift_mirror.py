#!/usr/bin/env python3
"""PostToolUse hook — Auto-mirror Drift essays from personal-works to Library.

When an Edit/Write tool produces a file under
`Foundations-of-Identity/personal-works/drift/essays/`, this hook copies it
to `Library/Drift/essays/` (the public-facing mirror per REPO_MAP.md).

This is gap #11 / #60 from Phase 3/4 of SUBSTRATE.md. Drift count discipline
required manual mirror until now; this hook makes it automatic.

Receives JSON on stdin with tool_name, tool_input. Runs synchronously; should
complete in <1s for the common case. Failures are silent (audit-trail only).
"""
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

CLAWD_HOME = Path(os.environ.get("CLAWD_HOME", os.path.expanduser("~/clawd")))

# The two drift essay directories — canonical (personal-works) and mirror (Library)
CANONICAL_DIRS = [
    CLAWD_HOME / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays",
    CLAWD_HOME / "repo-staging" / "drift" / "_essays",  # Drift site repo also canonical
]
MIRROR_DIR = CLAWD_HOME / "repo-staging" / "Corpus-Perspectival" / "Library" / "Drift" / "essays"

# Audit log for hook activity
AUDIT_LOG = CLAWD_HOME / "memory" / "drift_mirror_audit.jsonl"


def _log(entry: dict) -> None:
    """Append one JSONL entry to the hook audit log."""
    try:
        AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(AUDIT_LOG, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass  # Never block on audit failure


def _resolve_path(raw: str) -> Path | None:
    """Resolve a tool-input path string to a real Path."""
    if not raw:
        return None
    try:
        p = Path(raw)
        if not p.is_absolute():
            p = CLAWD_HOME / p
        return p.resolve()
    except Exception:
        return None


def _is_under_canonical(path: Path) -> Path | None:
    """If path is under any canonical drift dir, return that canonical dir.
    Otherwise None.
    """
    try:
        path_resolved = path.resolve()
    except Exception:
        return None
    for canonical in CANONICAL_DIRS:
        try:
            canonical_resolved = canonical.resolve()
            path_resolved.relative_to(canonical_resolved)
            return canonical_resolved
        except (ValueError, OSError):
            continue
    return None


def main() -> None:
    try:
        data = json.loads(sys.stdin.read())
    except (json.JSONDecodeError, Exception):
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})

    # Only Edit/Write trigger mirroring (Read, Glob, Grep, Bash skip)
    if tool_name not in ("Edit", "Write"):
        return

    # Pull the path field — Edit uses file_path, Write uses file_path too
    raw_path = tool_input.get("file_path") or tool_input.get("path") or tool_input.get("file")
    src = _resolve_path(raw_path)
    if src is None or not src.exists() or not src.is_file():
        return

    # Skip non-essay files (anything but markdown)
    if src.suffix.lower() not in (".md", ".markdown"):
        return

    canonical = _is_under_canonical(src)
    if canonical is None:
        return  # Not a drift essay write, skip

    # Compute mirror destination
    rel = src.relative_to(canonical)
    dst = MIRROR_DIR / rel.name  # Flat mirror; Library/Drift/essays/<filename>

    try:
        MIRROR_DIR.mkdir(parents=True, exist_ok=True)
        # Skip if mirror is already up-to-date (avoid redundant copies)
        if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
            _log({
                "ts": datetime.now().isoformat(),
                "action": "skipped_uptodate",
                "src": str(src),
                "dst": str(dst),
            })
            return
        shutil.copy2(src, dst)
        _log({
            "ts": datetime.now().isoformat(),
            "action": "mirrored",
            "src": str(src),
            "dst": str(dst),
            "size": src.stat().st_size,
        })
    except Exception as e:
        _log({
            "ts": datetime.now().isoformat(),
            "action": "error",
            "src": str(src),
            "dst": str(dst),
            "error": f"{type(e).__name__}: {e}",
        })


if __name__ == "__main__":
    main()
