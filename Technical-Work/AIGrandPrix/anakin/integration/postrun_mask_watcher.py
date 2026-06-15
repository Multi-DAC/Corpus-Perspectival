"""postrun_mask_watcher.py — overnight relay for the SEGMENTATION (mask) fine-tune (Day 134).

Polls the mask-ft orchestrator log for "[carry] complete:", then runs the two pre-flight
instruments WITH ANAKIN_GATE_MASK=1 (so official frames + renderer + encoder are all in
mask-space) and writes integration/MASK_OVERNIGHT_RESULTS.md:

  1. holdout_gate_v2.py --official-raw on the manual harvest, band-ft vs mask-ft. Under masking
     the mask-ft encoder sees masked frames in-distribution; we want its official<->rendered
     mean-term SMALL. (band-ft sees masks OOD, so treat the ratio as indicative, the mask-ft
     absolute mean-term as the real signal.)
  2. translation_rehearsal.py off maneuver_mask_ft/best.pt, masked — the cleanest go/no-go:
     does it FLY on gate-isolated obs in our sim? Good returns => encoder re-adapted => fly #3.

If training DIED (stale log, no complete line): no gate; best.pt (seeded +2142.53, protected)
stays; writes a STATUS block telling morning-me to relaunch launch_mask_ft_detached.py first.

Launch detached:  .venv/Scripts/python.exe launch_postrun_mask_watcher.py
Dry-run:          .venv/Scripts/python.exe integration/postrun_mask_watcher.py --dry-run
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
ORCH_LOG = os.path.join(LOGDIR, "mask_ft_orchestrator.log")
RUNDIR = os.path.join(LOGDIR, "maneuver_mask_ft")
MASK_BEST = os.path.join(RUNDIR, "best.pt")
RESULTS = os.path.join(_HERE, "MASK_OVERNIGHT_RESULTS.md")
HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")

POLL_S = 120
STALE_S = 30 * 60
MAX_WAIT_S = 8 * 3600


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
    env["ANAKIN_GATE_MASK"] = "1"
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
        f.write(f"\n## {title}\n\n*{now()} — {status}, {dt/60:.1f} min (ANAKIN_GATE_MASK=1)*\n\n"
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
        f.write(f"\n# Mask fine-tune — overnight results — {now()}\n\n"
                f"**Outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Gate NOT run** (no completion signal). Seed best.pt (+2142.53) intact. "
                    "Morning: relaunch `launch_mask_ft_detached.py` (resumes safe), gate after.\n")
        log(f"exiting without gate: {state} — {detail}")
        return

    time.sleep(60)

    ok_gate = run_step(
        "holdout_gate_v2.py (MASK) — official-harvest vs rendered, band-ft vs mask-ft",
        [PY, "-u", os.path.join("integration", "holdout_gate_v2.py"),
         "--official-dir", HARVEST, "--official-raw", "--ckpt-new", MASK_BEST],
    )
    run_step(
        "translation_rehearsal.py (MASK) — 10 eps off maneuver_mask_ft/best.pt",
        [PY, "-u", os.path.join("integration", "translation_rehearsal.py"),
         "--checkpoint", MASK_BEST, "--episodes", "10"],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. Gate step "
                f"{'succeeded' if ok_gate else 'FAILED — read its block'}; the rehearsal RETURN is "
                f"the go/no-go for flight #3. Decision belongs to the waking stream + Clayton.*\n")
    log("all steps done; morning letter written")


if __name__ == "__main__":
    main()
