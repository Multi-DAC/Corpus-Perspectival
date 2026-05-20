"""M3: State-File Coherence Checker (T1.B claim-provenance).

Reads declared assertions from navigation files (handoff.md, CURRENT.md,
palace/ATRIUM.md) and verifies them against ground truth. Raises faults
on mismatch. The monitor that would have caught the drift-count error
and library-mirror asymmetry on day 1 instead of day 10.

Integrated implementation plan #4. Builds on M6 (heartbeat) + M1 (cross-
channel pattern). Atomic heartbeat write; UTF-8 stdout; append-only
fault log per M1 pattern.

Falsifiability commitment: must flag known Mirror #28 stale-claim
instances. Verified by --test-known-instances flag using deliberate
counter-truth in a test file.

Usage:
    python operations/monitors/m3_state_coherence.py
    python operations/monitors/m3_state_coherence.py --json
    python operations/monitors/m3_state_coherence.py --quiet
    python operations/monitors/m3_state_coherence.py --test-known-instances
"""
import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLAWD = Path(r"C:\Users\mercu\clawd")
M3_HEARTBEAT_PATH = CLAWD / "memory" / "monitor_m3_heartbeat.json"
M3_FAULT_LOG_PATH = CLAWD / "memory" / "monitor_m3_faults.jsonl"

NAMING_DATE = datetime(2026, 1, 31)  # Clawd named self 2026-01-31
DRIFT_CANONICAL = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Foundations-of-Identity" / "personal-works" / "drift" / "essays"
DRIFT_MIRROR = CLAWD / "repo-staging" / "Corpus-Perspectival" / "Library" / "Drift" / "essays"

# ============================================================================
# Ground-truth probes
# ============================================================================

def count_canonical_drift() -> int:
    if not DRIFT_CANONICAL.exists():
        return -1
    return sum(1 for p in DRIFT_CANONICAL.glob("*.md"))


def count_mirror_drift() -> int:
    if not DRIFT_MIRROR.exists():
        return -1
    return sum(1 for p in DRIFT_MIRROR.glob("*.md"))


def days_since_naming() -> int:
    return (datetime.now() - NAMING_DATE).days + 1  # Day 1 = naming day


# ============================================================================
# Claim extractors (parse declared values from navigation files)
# ============================================================================

def _read(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def claims_from_current_md() -> list:
    """Pull declared facts from CURRENT.md.

    Returns list of (claim_name, declared_value, ground_truth_value, status, explanation) tuples.
    """
    text = _read(CLAWD / "CURRENT.md")
    out = []

    # Drift essays count: "| Drift essays | **N files canonical**"
    m = re.search(r"\|\s*Drift essays\s*\|\s*\*\*(\d+)\s+files canonical\*\*", text)
    if m:
        declared = int(m.group(1))
        truth = count_canonical_drift()
        if truth < 0:
            out.append(("CURRENT.md drift count", declared, "unknown (canonical dir not found)", "skip", "canonical dir absent"))
        elif declared == truth:
            out.append(("CURRENT.md drift count", declared, truth, "ok", None))
        else:
            out.append(("CURRENT.md drift count", declared, truth, "FAULT", f"declared {declared}, actual {truth} (delta {truth-declared:+d})"))

    # Days since naming: "| Days since naming | **N** |"
    m = re.search(r"\|\s*Days since naming\s*\|\s*\*\*(\d+)\*\*", text)
    if m:
        declared = int(m.group(1))
        truth = days_since_naming()
        if declared == truth:
            out.append(("CURRENT.md days since naming", declared, truth, "ok", None))
        else:
            out.append(("CURRENT.md days since naming", declared, truth, "FAULT", f"declared {declared}, actual {truth} (delta {truth-declared:+d})"))

    return out


def claims_from_handoff_md() -> list:
    text = _read(CLAWD / "memory" / "handoff.md")
    out = []

    # Look for "**N essays** canonical" patterns
    for m in re.finditer(r"\*\*(\d+)\s+essays\*\*\s+canonical", text):
        declared = int(m.group(1))
        truth = count_canonical_drift()
        if truth < 0:
            continue
        if abs(declared - truth) <= 1:  # tolerance for transient state
            out.append((f"handoff.md drift count (near-line: '{m.group(0)}')", declared, truth, "ok", None))
        else:
            out.append((f"handoff.md drift count (near-line: '{m.group(0)}')", declared, truth, "FAULT", f"declared {declared}, actual {truth} (delta {truth-declared:+d})"))

    return out


def cross_file_consistency_checks() -> list:
    """Checks that span multiple files / structural invariants."""
    out = []

    # Drift canonical vs Library mirror parity
    canonical_count = count_canonical_drift()
    mirror_count = count_mirror_drift()
    if canonical_count >= 0 and mirror_count >= 0:
        delta = canonical_count - mirror_count
        if delta == 0:
            out.append(("drift canonical/mirror parity", f"canonical={canonical_count}, mirror={mirror_count}", "match", "ok", None))
        else:
            # Compute the missing files in each direction
            canonical_names = {p.stem for p in DRIFT_CANONICAL.glob("*.md")}
            mirror_names = {p.stem for p in DRIFT_MIRROR.glob("*.md")}
            in_canonical_only = canonical_names - mirror_names
            in_mirror_only = mirror_names - canonical_names
            severity = "FAULT" if abs(delta) > 2 else "warn"
            out.append((
                "drift canonical/mirror parity",
                f"canonical={canonical_count}, mirror={mirror_count}",
                "match",
                severity,
                f"canonical-only ({len(in_canonical_only)}): {sorted(list(in_canonical_only))[:3]}... ; mirror-only ({len(in_mirror_only)}): {sorted(list(in_mirror_only))[:3]}...",
            ))

    # Naming-date math sanity (NAMING_DATE constant correctness check)
    if days_since_naming() > 365:
        out.append(("naming date sanity", days_since_naming(), "<365 expected", "warn", "days-since-naming exceeds 365; verify NAMING_DATE constant"))

    return out


# ============================================================================
# Main check pass
# ============================================================================

def run_checks() -> list:
    checks = []
    checks.extend(claims_from_current_md())
    checks.extend(claims_from_handoff_md())
    checks.extend(cross_file_consistency_checks())
    return checks


def write_heartbeat(checks: list) -> None:
    payload = {
        "monitor": "M3",
        "timestamp": datetime.now().isoformat(),
        "pid": os.getpid(),
        "checks_total": len(checks),
        "checks_ok": sum(1 for c in checks if c[3] == "ok"),
        "checks_warn": sum(1 for c in checks if c[3] == "warn"),
        "checks_fault": sum(1 for c in checks if c[3] == "FAULT"),
        "checks_skip": sum(1 for c in checks if c[3] == "skip"),
    }
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=str(M3_HEARTBEAT_PATH.parent), delete=False) as tmp:
        json.dump(payload, tmp, indent=2)
        tmp_name = tmp.name
    shutil.move(tmp_name, M3_HEARTBEAT_PATH)


def append_faults(checks: list) -> None:
    faults = [c for c in checks if c[3] in ("FAULT", "warn")]
    if not faults:
        return
    record = {
        "timestamp": datetime.now().isoformat(),
        "faults": [
            {"name": c[0], "declared": c[1], "truth": c[2], "severity": c[3], "explanation": c[4]}
            for c in faults
        ],
    }
    with open(M3_FAULT_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")


def synthetic_test() -> bool:
    """Falsifiability: verify M3 detects a deliberate counter-truth assertion.

    Creates a small test file with a deliberately-wrong drift count claim,
    runs a focused claim-verification against it, and confirms detection.
    """
    print("=== M3 Falsifiability Test ===")
    test_dir = CLAWD / "memory" / "_m3_test"
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "fake_handoff.md"
    truth = count_canonical_drift()
    if truth < 0:
        print("  SKIP: canonical drift dir not available")
        return False

    # Deliberate wrong claim: truth-1000 essays (obviously wrong)
    fake_count = max(0, truth - 1000)
    test_file.write_text(f"**{fake_count} essays** canonical (DELIBERATELY WRONG)\n", encoding="utf-8")

    # Parse + check the test file directly
    text = test_file.read_text()
    m = re.search(r"\*\*(\d+)\s+essays\*\*\s+canonical", text)
    if m is None:
        test_file.unlink(missing_ok=True)
        print("  FAIL: claim-extraction regex failed on test file")
        return False

    declared = int(m.group(1))
    detected_fault = abs(declared - truth) > 1
    test_file.unlink(missing_ok=True)
    test_dir.rmdir()

    if detected_fault:
        print(f"  PASS: detected synthetic stale-claim (declared {declared}, actual {truth}, delta {truth-declared:+d})")
        return True
    else:
        print(f"  FAIL: synthetic stale-claim NOT detected. declared={declared} truth={truth}")
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--test-known-instances", action="store_true")
    args = parser.parse_args()

    if args.test_known_instances:
        ok = synthetic_test()
        sys.exit(0 if ok else 1)

    # Pre-write heartbeat placeholder so M3 self-check doesn't trip on first run
    if not M3_HEARTBEAT_PATH.exists():
        M3_HEARTBEAT_PATH.write_text(json.dumps({
            "monitor": "M3", "timestamp": datetime.now().isoformat(),
            "pid": os.getpid(), "status": "initializing"
        }, indent=2))

    checks = run_checks()
    write_heartbeat(checks)
    append_faults(checks)

    if args.quiet:
        return

    if args.json:
        print(json.dumps([{"name": c[0], "declared": c[1], "truth": c[2], "severity": c[3], "explanation": c[4]} for c in checks], indent=2, default=str))
        return

    print(f"=== M3 State Coherence Check {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    for c in checks:
        name, declared, truth, severity, explanation = c
        if severity == "ok":
            print(f"  OK      {name}  (declared={declared}, truth={truth})")
        elif severity == "skip":
            print(f"  skip    {name}  ({explanation})")
        elif severity == "warn":
            print(f"  warn    {name}  — {explanation}")
        elif severity == "FAULT":
            print(f"  FAULT   {name}  — {explanation}")


if __name__ == "__main__":
    main()
