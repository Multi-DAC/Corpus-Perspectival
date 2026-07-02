"""postrun_edge_watcher.py — overnight relay for the EDGE/PENCIL fine-tune (Day 135).

Polls the edge-ft orchestrator log for "[carry] complete:", then runs the two pre-flight instruments
WITH ANAKIN_EDGE=1 (official frames + renderer + encoder all in edge-space) and writes
integration/EDGE_OVERNIGHT_RESULTS.md:

  1. holdout_gate_v2.py --official-raw on the manual harvest, --ckpt-new = edge-ft best. Under edge obs
     the edge-ft encoder sees edge frames in-distribution; we want its official<->rendered mean-term
     SMALL. (The default --ckpt-old baseline sees edges OOD, so treat the ratio as indicative, the
     edge-ft absolute mean-term as the real signal.) NOTE: the harvest is a BIASED instrument (human
     pilot flew around/above gates) — the gate here is indicative; the rehearsal + a real flight #4
     are the true tests.
  2. translation_rehearsal.py off maneuver_edge_ft/best.pt, edge obs — the cleaner go/no-go: does it
     FLY on edge obs in our sim? Good returns => encoder re-adapted to edges => worth flight #4.

If training DIED (stale log, no complete line): no gate; seed (restyle-ft) protected; writes a STATUS
block telling next-session to relaunch launch_edge_ft_detached.py first.

Launch detached:  .venv/Scripts/python.exe launch_postrun_edge_watcher.py
Dry-run:          .venv/Scripts/python.exe integration/postrun_edge_watcher.py --dry-run
"""
import argparse
import datetime
import os
import subprocess
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(_HERE)
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
LOGDIR = os.path.join(ANAKIN, "third_party", "dreamerv3-torch", "logdir")
ORCH_LOG = os.path.join(LOGDIR, "edge_ft_orchestrator.log")
RUNDIR = os.path.join(LOGDIR, "maneuver_edge_ft")
EDGE_BEST = os.path.join(RUNDIR, "best.pt")
RESULTS = os.path.join(_HERE, "EDGE_OVERNIGHT_RESULTS.md")
HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")

POLL_S = 120
STALE_S = 30 * 60
# Ceiling = wall-clock budget to wait for completion (the Day-134 mask run was mislabeled "dead" at an
# 8h ceiling while still healthily training a 2M-step run that takes >12h). Generous + env-overridable;
# real death still caught by STALE_S (30-min no-progress).
MAX_WAIT_S = int(float(os.environ.get("ANAKIN_WATCHER_MAX_H", "16")) * 3600)


def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def log(msg):
    print(f"[{now()}] {msg}", flush=True)


def orch_state():
    if not os.path.exists(ORCH_LOG):
        return "missing", f"orchestrator log not found: {ORCH_LOG}"
    with open(ORCH_LOG, "r", errors="replace") as f:
        text = f.read()
    for line in reversed(text.splitlines()):
        if "[carry] complete:" in line:
            return "complete", line.strip()
    age = time.time() - os.path.getmtime(ORCH_LOG)
    if os.path.isdir(RUNDIR):
        blogs = sorted(f for f in os.listdir(RUNDIR)
                       if f.startswith("carry_batch_") and f.endswith(".log"))
        if blogs:
            age = min(age, time.time() - os.path.getmtime(os.path.join(RUNDIR, blogs[-1])))
    if age > STALE_S:
        return "dead", f"no progress for {age/60:.0f} min (no complete line)"
    return "running", f"last activity {age/60:.1f} min ago"


def run_step(title, cmd):
    log(f"running: {title}")
    env = dict(os.environ)
    env["ANAKIN_EDGE"] = "1"
    env["ANAKIN_GATE_MASK"] = "0"   # never both transforms at once
    t0 = time.time()
    try:
        r = subprocess.run(cmd, cwd=ANAKIN, capture_output=True, text=True,
                           timeout=45 * 60, env=env)
        out = (r.stdout or "") + (("\n--- stderr ---\n" + r.stderr) if r.stderr.strip() else "")
        status = f"exit {r.returncode}"
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") if isinstance(e.stdout, str) else ""
        status = "TIMEOUT (45 min)"
    dt = time.time() - t0
    with open(RESULTS, "a") as f:
        f.write(f"\n## {title}\n\n*{now()} — {status}, {dt/60:.1f} min (ANAKIN_EDGE=1)*\n\n"
                f"```\n{out.strip()}\n```\n")
    log(f"done: {title} ({status}, {dt/60:.1f} min)")
    return status == "exit 0"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
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
        f.write(f"\n# Edge fine-tune — overnight results — {now()}\n\n"
                f"**Outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Gate NOT run** (no completion signal). Seed best.pt (restyle-ft) intact. "
                    "Next: relaunch `launch_edge_ft_detached.py` (resumes safe), gate after.\n")
        log(f"exiting without gate: {state} — {detail}")
        return

    time.sleep(60)

    ok_gate = run_step(
        "holdout_gate_v2.py (EDGE) — official-harvest vs rendered, baseline vs edge-ft",
        [PY, "-u", os.path.join("integration", "holdout_gate_v2.py"),
         "--official-dir", HARVEST, "--official-raw", "--ckpt-new", EDGE_BEST],
    )
    run_step(
        "translation_rehearsal.py (EDGE) — 10 eps off maneuver_edge_ft/best.pt",
        [PY, "-u", os.path.join("integration", "translation_rehearsal.py"),
         "--checkpoint", EDGE_BEST, "--episodes", "10"],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. Gate step "
                f"{'succeeded' if ok_gate else 'FAILED — read its block'}; the rehearsal RETURN is the "
                f"go/no-go for flight #4. Edges fix the gate-appearance axis; if rehearsal is weak the "
                f"residual is background-texture edges -> add bg-randomization next. Decision = waking "
                f"stream + Clayton.*\n")
    log("all steps done; results written")


if __name__ == "__main__":
    main()
