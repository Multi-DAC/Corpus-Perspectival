"""postrun_gate_watcher.py — overnight measurement relay (built Day 131, 22:10).

The restyle fine-tune's batch 3 completes after the stream sleeps. This watcher
converts that dead time into measurement: it polls the orchestrator log for
"[carry] complete:", then runs the two pre-flight instruments in sequence and
writes everything into ONE morning-letter file:

    integration/OVERNIGHT_RESULTS.md

  1. holdout_gate.py            — P224 appearance gate (pre-registered PASS:
                                  restyle-ft FD < 0.5 x band-ft FD on the 20
                                  SEALED official frames)
  2. translation_rehearsal.py   — 10 episodes off maneuver_restyle_ft/best.pt
                                  (--checkpoint flag is mandatory; default
                                  points at the OLD scale_2 run)

If training DIED instead of completing (log mtime stale >30 min, no complete
line): the watcher does NOT run the gate — best.pt is valid (+2142.53 protected)
but resume takes priority; it writes a STATUS block telling morning-me to
relaunch launch_restyle_ft_detached.py first. Decision authority stays with the
waking stream; the watcher only acts on the unambiguous signal.

Launch detached:  .venv/Scripts/python.exe launch_postrun_watcher.py
Dry-run check:    .venv/Scripts/python.exe integration/postrun_gate_watcher.py --dry-run
"""
import argparse
import datetime
import os
import subprocess
import sys
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(_HERE)
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
ORCH_LOG = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir",
                        "restyle_ft_orchestrator.log")
RESTYLE_BEST = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir",
                            "maneuver_restyle_ft", "best.pt")
RESULTS = os.path.join(_HERE, "OVERNIGHT_RESULTS.md")

POLL_S = 120          # poll cadence
STALE_S = 30 * 60     # log silent this long with no complete-line => training died
MAX_WAIT_S = 6 * 3600 # absolute ceiling; past this, write status and exit


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    line = f"[{now()}] {msg}"
    print(line, flush=True)


def orch_state():
    """-> ('complete'|'running'|'dead'|'missing', detail)"""
    if not os.path.exists(ORCH_LOG):
        return "missing", f"orchestrator log not found: {ORCH_LOG}"
    with open(ORCH_LOG, "r", errors="replace") as f:
        text = f.read()
    for line in reversed(text.splitlines()):
        if "[carry] complete:" in line:
            return "complete", line.strip()
    age = time.time() - os.path.getmtime(ORCH_LOG)
    # the orchestrator log is quiet between batches; the BATCH log carries the pulse
    batch_logs = sorted(
        f for f in os.listdir(os.path.dirname(ORCH_LOG) + "/maneuver_restyle_ft")
        if f.startswith("carry_batch_") and f.endswith(".log")
    ) if os.path.isdir(os.path.dirname(ORCH_LOG) + "/maneuver_restyle_ft") else []
    if batch_logs:
        latest = os.path.join(os.path.dirname(ORCH_LOG), "maneuver_restyle_ft", batch_logs[-1])
        age = min(age, time.time() - os.path.getmtime(latest))
    if age > STALE_S:
        return "dead", f"no progress for {age/60:.0f} min (no complete line)"
    return "running", f"last activity {age/60:.1f} min ago"


def run_step(title, cmd):
    """Run a subprocess from ANAKIN root, capture everything, append to RESULTS."""
    log(f"running: {title}")
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=ANAKIN, capture_output=True, text=True,
                           timeout=45 * 60)
        out = (r.stdout or "") + (("\n--- stderr ---\n" + r.stderr) if r.stderr.strip() else "")
        status = f"exit {r.returncode}"
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        status = "TIMEOUT (45 min)"
    dt = time.time() - t0
    with open(RESULTS, "a") as f:
        f.write(f"\n## {title}\n\n*{now()} — {status}, {dt/60:.1f} min*\n\n"
                f"```\n{out.strip()}\n```\n")
    log(f"done: {title} ({status}, {dt/60:.1f} min)")
    return status == "exit 0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="report current orchestrator state and exit")
    args = ap.parse_args()

    state, detail = orch_state()
    log(f"orchestrator state: {state} — {detail}")
    if args.dry_run:
        return

    t_start = time.time()
    while state == "running":
        if time.time() - t_start > MAX_WAIT_S:
            state, detail = "dead", f"watcher ceiling {MAX_WAIT_S/3600:.0f}h reached"
            break
        time.sleep(POLL_S)
        state, detail = orch_state()

    with open(RESULTS, "a") as f:
        f.write(f"\n# Overnight results — {now()}\n\n"
                f"**Fine-tune outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Gate NOT run** (training did not signal completion). "
                    "best.pt remains the protected +2142.53. Morning sequence: "
                    "relaunch `launch_restyle_ft_detached.py` (resumes safe), "
                    "then run the gate after completion.\n")
        log(f"exiting without gate: {state} — {detail}")
        return

    time.sleep(60)  # let file handles settle, GPU drain

    ok_gate = run_step(
        "holdout_gate.py — P224 appearance gate "
        "(pre-registered PASS: restyle-ft FD < 0.5 x band-ft FD)",
        [PY, "-u", os.path.join("integration", "holdout_gate.py")],
    )
    run_step(
        "translation_rehearsal.py — 10 episodes off maneuver_restyle_ft/best.pt",
        [PY, "-u", os.path.join("integration", "translation_rehearsal.py"),
         "--checkpoint", RESTYLE_BEST, "--episodes", "10"],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. Gate step "
                f"{'succeeded' if ok_gate else 'FAILED — read its block above'}; "
                f"flight #2 decision belongs to the waking stream + Clayton.*\n")
    log("all steps done; morning letter written")


if __name__ == "__main__":
    main()
