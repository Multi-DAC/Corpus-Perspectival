"""SMOKE TEST: informed-Dreamer (route 3) wiring check — tiny budget, NOT a real fine-tune.

Purpose: before spending a real continue-train, verify the whole informed path runs end-to-end:
  1. strict=False load of the seed (new priv_state decoder head absent from restyle_ft/best.pt),
  2. the env emits a 9-d priv_state and it flows into the replay/batch,
  3. the decoder builds the priv_state MLP head (encoder stays blind) and computes a FINITE loss,
  4. training reaches a latest.pt with no traceback.

Tiny: 16 envs, prefill 2000, 6000 steps, 1 batch -> a couple minutes on the 5080. The number that
matters here is "did it run", not the return. The real short fine-tune is launch_informed_ft.py.

Run: .venv/Scripts/python.exe launch_informed_smoke.py   (returns immediately; poll the log)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_restyle_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_informed_smoke")
LOG = os.path.join(DREAMER, "logdir", "informed_smoke_orchestrator.log")

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_restyle_ft/best.pt")
else:
    print(f"resuming existing {latest}")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band anakin_informed",
    "--envs", "16",
    "--batch-steps", "6000",
    "--num-batches", "1",
    "--train-ratio", "64",
    "--eval-every", "2000",
    "--prefill", "2000",
]

env = dict(os.environ)
env["ANAKIN_PRIV"] = "1"           # informed-Dreamer: env emits priv_state; non-strict load
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED informed-smoke pid {p.pid} -> {LOG}")
print("ANAKIN_PRIV=1; verify: strict=False load, priv_state loss finite, latest.pt written.")
