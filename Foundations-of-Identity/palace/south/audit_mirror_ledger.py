#!/usr/bin/env python
"""Repo-health audit Step 2 — redundancy/desync ledger.
Compares each clawd-local mirrored layer against its Foundations-of-Identity staging
mirror (per REPO_MAP.md): counts, only-local, only-staging, and CONTENT DRIFT
(same relative path, different hash = the mirror fell out of sync).

Right instruments only (os.walk + hashlib), no find/awk/git-bash temp.
"""
import os, hashlib, sys

LOCAL = r"C:\Users\mercu\clawd"
STAGE = r"C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\Foundations-of-Identity"
DAEMON = r"C:\Users\mercu\clawd-daemon"

# (label, local_root, staging_root)
PAIRS = [
    ("identity",   os.path.join(LOCAL, "identity"),   os.path.join(STAGE, "identity")),
    ("memory",     os.path.join(LOCAL, "memory"),     os.path.join(STAGE, "memory")),
    ("operations", os.path.join(LOCAL, "operations"), os.path.join(STAGE, "operations")),
    ("palace",     os.path.join(LOCAL, "palace"),     os.path.join(STAGE, "palace")),
    ("clawd-daemon", DAEMON, os.path.join(STAGE, "operations", "clawd-daemon")),
]

SKIP_DIRS = {".git", "__pycache__", "node_modules", ".pytest_cache", ".venv", "venv"}
SKIP_EXT  = {".pyc", ".pyo"}

def walk_rel(root):
    """relpath -> sha1 for every file under root (skipping noise)."""
    out = {}
    if not os.path.isdir(root):
        return out
    for r, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in SKIP_EXT:
                continue
            full = os.path.join(r, f)
            rel = os.path.relpath(full, root).replace("\\", "/")
            try:
                with open(full, "rb") as fh:
                    out[rel] = hashlib.sha1(fh.read()).hexdigest()
            except Exception as e:
                out[rel] = f"<ERR {e.__class__.__name__}>"
    return out

# Paths that are CORRECTLY local-only per REPO_MAP (not desync, expected)
EXPECTED_LOCAL_ONLY = {
    "palace": {"MASTER_ROADMAP.md"},                 # private, local-only
    "memory": None,   # precompact_snapshots/, archive/ — flagged separately, treated as expected
}

def is_expected_local_only(label, rel):
    if label == "palace" and rel == "MASTER_ROADMAP.md":
        return True
    if label == "memory" and (rel.startswith("precompact_snapshots/") or rel.startswith("conversations/")
                              or rel == "telegram-history.json"):
        return True
    if label == "clawd-daemon" and (rel.startswith("tests/") or rel.endswith(".env")
                              or ".bak" in rel or rel.startswith("logs/")):
        return True
    return False

print("# Redundancy / Desync Ledger — clawd-local ↔ staging mirror")
print(f"# LOCAL={LOCAL}\n# STAGE={STAGE}\n")
total_drift = 0
for label, lroot, sroot in PAIRS:
    L = walk_rel(lroot)
    S = walk_rel(sroot)
    lset, sset = set(L), set(S)
    common = lset & sset
    drift = sorted(p for p in common if L[p] != S[p])
    only_l = sorted(p for p in (lset - sset) if not is_expected_local_only(label, p))
    only_l_expected = sorted(p for p in (lset - sset) if is_expected_local_only(label, p))
    only_s = sorted(sset - lset)
    total_drift += len(drift)
    print(f"## {label}: local={len(L)} staging={len(S)} common={len(common)}")
    print(f"   CONTENT DRIFT (edited one side only): {len(drift)}")
    for p in drift[:25]:
        print(f"      ~ {p}")
    if len(drift) > 25:
        print(f"      ... +{len(drift)-25} more")
    print(f"   only-local (unmirrored, NOT expected): {len(only_l)}")
    for p in only_l[:20]:
        print(f"      L {p}")
    if len(only_l) > 20:
        print(f"      ... +{len(only_l)-20} more")
    print(f"   only-local (expected per REPO_MAP): {len(only_l_expected)}")
    print(f"   only-staging (stale or staging-canonical): {len(only_s)}")
    for p in only_s[:20]:
        print(f"      S {p}")
    if len(only_s) > 20:
        print(f"      ... +{len(only_s)-20} more")
    print()
print(f"# TOTAL CONTENT-DRIFT FILES ACROSS ALL MIRRORS: {total_drift}")
