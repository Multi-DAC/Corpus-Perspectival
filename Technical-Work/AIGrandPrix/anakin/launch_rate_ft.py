"""DETACHED launch: RATE-RANDOMIZED fine-tune off maneuver_informed_ft best.pt (Day 137).

THE control-rate-cliff fix (CONTROL_RATE_FINDING_2026-06-17.md). The primary transfer killer is NOT
appearance — it's a control clock mismatch: trained at dt=0.02 (50 Hz), deployed once per 30 Hz vision
frame (run_dreamer.py). A 50 Hz policy run at 30 Hz holds each body-rate command 1.67x too long ->
over-rotation -> spin-out (flight #1 DQ). control_rate_rehearsal.py measured the cliff (appearance-free,
instrument-validated): the informed flier scores +1154/6.5 gates at 50 Hz and DIES at 30 Hz (-14/1 gate).

FIX: randomize the control dt per-episode during training (vec_env ANAKIN_RATE_RANDOM=1, dt in
[0.020,0.040] = 50..25 Hz) so the policy becomes invariant to the decision clock. Seeded off the
informed checkpoint so it KEEPS the geometry-grounded latent (priv_state head, ANAKIN_PRIV=1) and
ADDS rate-robustness. Same KIND of intervention as the band/DR knobs, on the axis that actually gates
transfer; also buys real-hardware variable-latency robustness for the later VQs (fixed build).

BUDGET: 3 x 500k = 1.5M steps (rate adaptation is a dynamics change, a touch heavier than appearance;
still cheapest-bounded). Gate via launch_postrun_rate_watcher.py -> control_rate_rehearsal at the full
sweep on the new best.pt: PASS = the cliff flattens (30 Hz return recovers toward the 50 Hz anchor).

Run: .venv/Scripts/python.exe launch_rate_ft.py   (returns immediately; gate via the watcher)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_informed_ft", "best.pt")  # the strong flier
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_rate_ft")
LOG = os.path.join(DREAMER, "logdir", "rate_ft_orchestrator.log")

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_informed_ft/best.pt")
else:
    print(f"resuming existing {latest} (carry_state continues)")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band anakin_informed",
    "--envs", "256",
    "--batch-steps", "500000",
    "--num-batches", "3",
    "--train-ratio", "64",
    "--eval-every", "5000",
]

env = dict(os.environ)
env["ANAKIN_RATE_RANDOM"] = "1"     # vec_env: per-episode control dt in [DT_MIN, DT_MAX]
env["ANAKIN_DT_MIN"] = "0.020"      # 50 Hz (training clock)
env["ANAKIN_DT_MAX"] = "0.040"      # 25 Hz — covers the 30 Hz deploy clock with margin both sides
env["ANAKIN_PRIV"] = "1"           # keep informed-Dreamer geometry grounding (seed has the priv head)
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED rate-randomized ft orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_RATE_RANDOM=1 dt[0.020,0.040]; 1.5M steps (3x500k). "
      "Launch launch_postrun_rate_watcher.py to auto-gate via the control-rate sweep.")
