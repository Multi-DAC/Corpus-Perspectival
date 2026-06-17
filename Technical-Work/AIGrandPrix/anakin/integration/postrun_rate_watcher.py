"""postrun_rate_watcher.py — relay for the RATE-RANDOMIZED fine-tune (Day 137, control-rate-cliff fix).

Polls the rate-ft orchestrator log for "[carry] complete:", then runs the DECISIVE instrument and
writes integration/RATE_RESULTS.md:

  control_rate_rehearsal.py --checkpoint maneuver_rate_ft/best.pt
    The appearance-free control-rate sweep (50/40/33/30/24 Hz, validated harness). The pre-rate policy
    flew at 50 Hz (+1154/6.5 gates) and DIED at the 30 Hz deploy clock (-14/1 gate). PASS = the cliff
    FLATTENS: the 30 Hz row recovers toward the 50 Hz anchor (gates/ep at 30 Hz climbs back toward the
    50 Hz value). That means the policy is now rate-robust and a real 30 Hz flight is worth running.

If training DIED (stale log, no complete line): no sweep; seed (informed-ft) protected; writes a STATUS
block telling next-session to relaunch launch_rate_ft.py first (resumes safe).

Launch detached:  .venv/Scripts/python.exe launch_postrun_rate_watcher.py
Dry-run:          .venv/Scripts/python.exe integration/postrun_rate_watcher.py --dry-run
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
ORCH_LOG = os.path.join(LOGDIR, "rate_ft_orchestrator.log")
RUNDIR = os.path.join(LOGDIR, "maneuver_rate_ft")
RATE_BEST = os.path.join(RUNDIR, "best.pt")
RESULTS = os.path.join(_HERE, "RATE_RESULTS.md")

POLL_S = 120
STALE_S = 30 * 60
MAX_WAIT_S = int(float(os.environ.get("ANAKIN_WATCHER_MAX_H", "10")) * 3600)


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
    env["ANAKIN_PRIV"] = "0"          # eval = image-only model (priv head is train-only, dropped on load)
    env["ANAKIN_EDGE"] = "0"
    env["ANAKIN_GATE_MASK"] = "0"
    env["ANAKIN_RATE_RANDOM"] = "0"   # the rehearsal sets dt itself per-row; env must NOT randomize
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
        f.write(f"\n# Rate-randomized fine-tune — results — {now()}\n\n"
                f"**Outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Sweep NOT run** (no completion signal). Seed best.pt (informed-ft) intact. "
                    "Next: relaunch `launch_rate_ft.py` (resumes safe), gate after.\n")
        log(f"exiting without sweep: {state} — {detail}")
        return

    time.sleep(60)

    run_step(
        "control_rate_rehearsal.py (RATE-FT) — appearance-free 50/40/33/30/24 Hz sweep on the new best.pt",
        [PY, "-u", os.path.join("integration", "control_rate_rehearsal.py"),
         "--checkpoint", RATE_BEST],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. PASS = the cliff FLATTENS: the 30 Hz row's "
                f"return + gates/ep recover toward the 50 Hz anchor. If it flattens, the policy is "
                f"rate-robust -> run a real 30 Hz official flight (only then is any residual appearance "
                f"gap testable). If the 30 Hz row is still dead, widen dt range / lengthen the run / "
                f"check the world model can infer rate. Decision = waking stream + Clayton.*\n")
    log("sweep done; results written")


if __name__ == "__main__":
    main()
