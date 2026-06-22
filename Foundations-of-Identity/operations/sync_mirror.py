#!/usr/bin/env python
"""sync_mirror.py — keep the staging FoI mirror in sync with clawd-local canonical.

WHY. clawd-local is canonical for identity/ memory/ operations/ palace/ + CURRENT.md +
KNOWLEDGE_GRAPH.md; these mirror to repo-staging/Corpus-Perspectival/Foundations-of-Identity/.
The mirror was kept by hand-`cp` per file — forgettable, so files silently drifted (e.g. the
public BOOT_IDENTITY still said Finnley "due May 2026" weeks after he was born). This automates it.

DESIGN. The staging *tracked-set* IS the manifest — no fragile include/exclude list. For every file
already tracked under Foundations-of-Identity/, refresh it from its clawd-local counterpart.
  - Files canonical AT staging (personal-works/, operations/clawd-daemon/) have no local source -> skipped.
  - Comparison is line-ending-normalized (CRLF/LF won't fake drift — the audit's own lesson).
  - NEW local .md notes not yet mirrored are REPORTED (not auto-published — that stays deliberate).
  - Orphans (tracked in staging, gone locally) are REPORTED, never auto-deleted.

USAGE.
  python operations/sync_mirror.py            # --check: report drift / new / orphans (no writes)
  python operations/sync_mirror.py --sync     # refresh drifted mirror files from local (writes staging tree)
  python operations/sync_mirror.py --sync --commit   # + git add -u, commit, push staging
"""
import os
import sys
import subprocess
import hashlib
import shutil

LOCAL = r"C:\Users\mercu\clawd"
STAGE_REPO = os.path.join(LOCAL, "repo-staging", "Corpus-Perspectival")
FOI_REL = "Foundations-of-Identity"
FOI = os.path.join(STAGE_REPO, FOI_REL)

# local mirrored layers (canonical at clawd-local) + their walk-excludes for NEW-file detection
MIRRORED_LAYERS = ("identity", "memory", "operations", "palace")
SINGLE_FILES = ("CURRENT.md", "KNOWLEDGE_GRAPH.md")
# dirs never mirrored (cruft / private / state) — for new-file detection only
EXCLUDE_DIR_PARTS = {
    "precompact_snapshots", ".search_index", "conversations", "__pycache__",
    ".git", "node_modules", "clawd-daemon",
}
EXCLUDE_FILES = {"MASTER_ROADMAP.md", "MEMORY.md"}  # private / daemon-local-only
# new-file detection: only these extensions are auto-flagged as mirror candidates
NEW_CANDIDATE_EXT = {".md"}


def norm_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha1(f.read().replace(b"\r\n", b"\n")).hexdigest()


def local_counterpart(foi_relpath):
    """staging FoI subpath -> clawd-local source path, or None if canonical-at-staging."""
    if foi_relpath.startswith("personal-works/"):
        return None
    if foi_relpath.startswith("operations/clawd-daemon/"):
        return None  # synced from the sibling daemon repo separately
    if "/" not in foi_relpath and foi_relpath not in SINGLE_FILES:
        return None  # FoI-root loose files (README.md etc.) are FoI's own, NOT the clawd-local namesake
    top = foi_relpath.split("/", 1)[0]
    if top in MIRRORED_LAYERS or foi_relpath in SINGLE_FILES:
        return os.path.join(LOCAL, foi_relpath.replace("/", os.sep))
    # archive/, tools/, etc. — refresh only if a local counterpart actually exists
    cand = os.path.join(LOCAL, foi_relpath.replace("/", os.sep))
    return cand if os.path.exists(cand) else None


# refresh DOCUMENTS + code; leave daemon-managed state (.json/.jsonl) out of scope (rec #4 territory)
SKIP_REFRESH_EXT = {".json", ".jsonl"}


def tracked_foi():
    out = subprocess.run(["git", "ls-files", FOI_REL + "/*"], cwd=STAGE_REPO,
                         capture_output=True, text=True).stdout
    pre = FOI_REL + "/"
    return [l.strip().replace("\\", "/")[len(pre):] for l in out.splitlines() if l.strip()]


def find_new_candidates(tracked_set):
    """local .md files under mirrored layers that aren't in the staging tracked-set."""
    new = []
    for layer in MIRRORED_LAYERS:
        root = os.path.join(LOCAL, layer)
        if not os.path.isdir(root):
            continue
        for r, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIR_PARTS]
            for f in files:
                if os.path.splitext(f)[1].lower() not in NEW_CANDIDATE_EXT or f in EXCLUDE_FILES:
                    continue
                rel = os.path.relpath(os.path.join(r, f), LOCAL).replace("\\", "/")
                if rel not in tracked_set:
                    new.append(rel)
    for sf in SINGLE_FILES:
        if sf not in tracked_set and os.path.exists(os.path.join(LOCAL, sf)):
            new.append(sf)
    return sorted(new)


def main():
    do_sync = "--sync" in sys.argv
    do_commit = "--commit" in sys.argv
    tracked = tracked_foi()
    tracked_set = set(tracked)

    drifted, orphans, refreshed = [], [], []
    skipped_staging_canonical = 0
    skipped_state = 0
    for rel in tracked:
        lc = local_counterpart(rel)
        sp = os.path.join(FOI, rel.replace("/", os.sep))
        if lc is None:
            skipped_staging_canonical += 1
            continue
        if os.path.splitext(rel)[1].lower() in SKIP_REFRESH_EXT:
            skipped_state += 1  # daemon-managed state; not a document to keep in sync
            continue
        if not os.path.exists(lc):
            orphans.append(rel)
            continue
        if not os.path.exists(sp) or norm_sha(lc) != norm_sha(sp):
            drifted.append(rel)
            if do_sync:
                os.makedirs(os.path.dirname(sp), exist_ok=True)
                shutil.copy2(lc, sp)
                refreshed.append(rel)

    new_candidates = find_new_candidates(tracked_set)

    print(f"mirror sync ({'SYNC' if do_sync else 'CHECK'}) — {len(tracked)} tracked FoI files "
          f"({skipped_staging_canonical} canonical-at-staging + {skipped_state} daemon-state, skipped)")
    print(f"  DRIFTED (mirror stale vs local): {len(drifted)}")
    for p in drifted[:40]:
        print(f"    ~ {p}" + ("  [refreshed]" if p in refreshed else ""))
    if len(drifted) > 40:
        print(f"    ... +{len(drifted)-40} more")
    print(f"  NEW local .md not yet mirrored (review; not auto-added): {len(new_candidates)}")
    for p in new_candidates[:30]:
        print(f"    + {p}")
    if len(new_candidates) > 30:
        print(f"    ... +{len(new_candidates)-30} more")
    print(f"  ORPHANS (tracked in staging, missing locally — NOT deleted): {len(orphans)}")
    for p in orphans[:20]:
        print(f"    ? {p}")

    if do_sync and refreshed and do_commit:
        # stage ONLY the files we refreshed, by explicit path — never `git add -u` (that would
        # sweep up unrelated WIP under FoI, e.g. personal-works/ drafts someone else is editing).
        paths = [(FOI_REL + "/" + r) for r in refreshed]
        subprocess.run(["git", "add"] + paths, cwd=STAGE_REPO)
        msg = f"sync_mirror: refresh {len(refreshed)} drifted mirror file(s) from clawd-local canonical"
        subprocess.run(["git", "commit", "-q", "-m", msg], cwd=STAGE_REPO)
        push = subprocess.run(["git", "push", "origin", "main"], cwd=STAGE_REPO,
                              capture_output=True, text=True)
        print("\n  committed + pushed:", (push.stderr or push.stdout).strip().splitlines()[-1:])
    elif do_sync and refreshed:
        print(f"\n  refreshed {len(refreshed)} file(s) into the staging tree (not committed; add --commit to push)")
    print("\ndone.")


if __name__ == "__main__":
    main()
