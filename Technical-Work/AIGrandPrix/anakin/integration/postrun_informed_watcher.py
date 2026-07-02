"""postrun_informed_watcher.py — relay for the INFORMED-Dreamer (route 3) fine-tune (Day 136).

Polls the informed-ft orchestrator log for "[carry] complete:", then runs the two pre-flight
instruments and writes integration/INFORMED_RESULTS.md:

  1. holdout_gate_v2.py --official-raw on the manual harvest, --ckpt-new = informed-ft best vs the
     default band-ft baseline. PRIMARY signal = MEAN-TERM ratio (informed / band-ft); pre-registered
     PASS < 0.5 (grounding the latent in geometry at least halves the official-domain gap). The gate
     loads image-only (DreamerPilot drops the informed priv_state head non-strict) — priv_state is a
     TRAIN-time signal only, so the deployed/eval encoder is unchanged. The harvest is a BIASED
     instrument (human flew around/above gates) so the gate is indicative; the rehearsal is the fly-test.
  2. translation_rehearsal.py off maneuver_informed_ft/best.pt — does it FLY in our sim through the
     adapter path? Good roundtrip returns => the geometry-grounded encoder survives the official obs path.

Gate/rehearsal run with ANAKIN_PRIV=0 (image-only model; the priv head is training-only and dropped on
load), ANAKIN_EDGE=0, ANAKIN_GATE_MASK=0.

If training DIED (stale log, no complete line): no gate; seed (restyle-ft) protected; writes a STATUS
block telling next-session to relaunch launch_informed_ft.py first.

Launch detached:  .venv/Scripts/python.exe launch_postrun_informed_watcher.py
Dry-run:          .venv/Scripts/python.exe integration/postrun_informed_watcher.py --dry-run
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
ORCH_LOG = os.path.join(LOGDIR, "informed_ft_orchestrator.log")
RUNDIR = os.path.join(LOGDIR, "maneuver_informed_ft")
INFORMED_BEST = os.path.join(RUNDIR, "best.pt")
RESULTS = os.path.join(_HERE, "INFORMED_RESULTS.md")
HARVEST = (r"C:\Users\Wasch\OneDrive\Desktop\AI-GP Simulator v1.0.3364"
           r"\PyAIPilotExample\official_frames\manual_20260614_114130")

POLL_S = 120
STALE_S = 30 * 60
MAX_WAIT_S = int(float(os.environ.get("ANAKIN_WATCHER_MAX_H", "8")) * 3600)


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
    env["ANAKIN_PRIV"] = "0"        # gate/rehearsal = image-only model (priv head is train-only)
    env["ANAKIN_EDGE"] = "0"
    env["ANAKIN_GATE_MASK"] = "0"
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
        f.write(f"\n## {title}\n\n*{now()} — {status}, {dt/60:.1f} min*\n\n```\n{out.strip()}\n```\n")
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
        f.write(f"\n# Informed-Dreamer (route 3) fine-tune — results — {now()}\n\n"
                f"**Outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Gate NOT run** (no completion signal). Seed best.pt (restyle-ft) intact. "
                    "Next: relaunch `launch_informed_ft.py` (resumes safe), gate after.\n")
        log(f"exiting without gate: {state} — {detail}")
        return

    time.sleep(60)

    ok_gate = run_step(
        "holdout_gate_v2.py (INFORMED) — official-harvest vs rendered, baseline vs informed-ft",
        [PY, "-u", os.path.join("integration", "holdout_gate_v2.py"),
         "--official-dir", HARVEST, "--official-raw", "--ckpt-new", INFORMED_BEST],
    )
    run_step(
        "translation_rehearsal.py (INFORMED) — 10 eps off maneuver_informed_ft/best.pt",
        [PY, "-u", os.path.join("integration", "translation_rehearsal.py"),
         "--checkpoint", INFORMED_BEST, "--episodes", "10"],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. PRIMARY = the holdout-gate MEAN-TERM ratio "
                f"(informed/band-ft; pass < 0.5 means grounding the latent in geometry closed the "
                f"official-domain gap). The rehearsal roundtrip RETURN is the fly go/no-go for flight #4. "
                f"If the gate moves but doesn't pass, route 3 helps partially -> stack route 1 "
                f"(renderer appearance-DR: illumination + bg-texture). Decision = waking stream + Clayton.*\n")
    log("all steps done; results written")


if __name__ == "__main__":
    main()
