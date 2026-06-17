"""postrun_dr_watcher.py — relay for the APPEARANCE-DR (route 1) fine-tune (Day 136).

Polls the dr-ft orchestrator log for "[carry] complete:", then runs the two pre-flight
instruments and writes integration/DR_RESULTS.md:

  1. holdout_gate_v2.py --official-raw on the manual harvest, --ckpt-new = dr-ft best vs the
     default band-ft baseline. PRIMARY signal = MEAN-TERM ratio (dr-ft / band-ft); pre-registered
     PASS < 0.5 (appearance-invariance training at least halves the official-domain gap — the official
     look becomes one more sample inside the trained manifold). The harvest is a BIASED instrument
     (human flew around/above gates) so the gate is indicative; the rehearsal is the fly-test.
  2. translation_rehearsal.py off maneuver_dr_ft/best.pt — does it still FLY through the adapter path?

★ The gate + rehearsal run with ANAKIN_APPEARANCE_DR=0 (CANONICAL render) so the "rendered" reference
is the same one the band-ft baseline was gated against — apples-to-apples. The test is whether the
DR-trained policy maps the official harvest CLOSER to the canonical rendered look (because it learned
geometry-keyed, appearance-invariant latents), not whether we re-randomize the reference.

If training DIED (stale log, no complete line): no gate; seed (restyle-ft) protected; writes a STATUS
block telling next-session to relaunch launch_dr_ft.py first.

Launch detached:  .venv/Scripts/python.exe launch_postrun_dr_watcher.py
Dry-run:          .venv/Scripts/python.exe integration/postrun_dr_watcher.py --dry-run
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
ORCH_LOG = os.path.join(LOGDIR, "dr_ft_orchestrator.log")
RUNDIR = os.path.join(LOGDIR, "maneuver_dr_ft")
DR_BEST = os.path.join(RUNDIR, "best.pt")
RESULTS = os.path.join(_HERE, "DR_RESULTS.md")
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
    env["ANAKIN_APPEARANCE_DR"] = "0"   # canonical render for the gate (apples-to-apples vs band-ft)
    env["ANAKIN_PRIV"] = "0"
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
        f.write(f"\n# Appearance-DR (route 1) fine-tune — results — {now()}\n\n"
                f"**Outcome:** `{state}` — {detail}\n")

    if state != "complete":
        with open(RESULTS, "a") as f:
            f.write("\n**Gate NOT run** (no completion signal). Seed best.pt (restyle-ft) intact. "
                    "Next: relaunch `launch_dr_ft.py` (resumes safe), gate after.\n")
        log(f"exiting without gate: {state} — {detail}")
        return

    time.sleep(60)

    run_step(
        "holdout_gate_v2.py (DR) — official-harvest vs rendered, baseline vs dr-ft",
        [PY, "-u", os.path.join("integration", "holdout_gate_v2.py"),
         "--official-dir", HARVEST, "--official-raw", "--ckpt-new", DR_BEST],
    )
    run_step(
        "translation_rehearsal.py (DR) — 10 eps off maneuver_dr_ft/best.pt",
        [PY, "-u", os.path.join("integration", "translation_rehearsal.py"),
         "--checkpoint", DR_BEST, "--episodes", "10"],
    )

    with open(RESULTS, "a") as f:
        f.write(f"\n---\n*Watcher finished {now()}. PRIMARY = the holdout-gate MEAN-TERM ratio "
                f"(dr-ft/band-ft; pass < 0.5 means appearance-invariance training closed the "
                f"official-domain gap). This is the CHEAPEST-FIRST-STEP (1M, moderate width 0.5). "
                f"If the gate moves the needle -> commit the multi-M run WITH a widening curriculum + "
                f"held-out-slice eval (Clayton-gated, VQ1 path). If not -> route 1 weakened, the heavy "
                f"PencilNet decoupled-pose front-end (route c) is next. Decision = waking stream + Clayton.*\n")
    log("all steps done; results written")


if __name__ == "__main__":
    main()
