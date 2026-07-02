"""DETACHED launch: EDGE/PENCIL-FILTER fine-tune off restyle-ft best.pt (Day 135).

The corrected segmentation route. Mask route (color-threshold) FALSIFIED + flight #3 (2026-06-15)
confirmed appearance-OOD is the wall (flew blind, spiraled). Literature (PencilNet 2207.14131;
Loquercio TRO-2019) shows the proven sim-to-real path keys invariance on EDGES not color — edges
survive the color/illumination shift our old-color-trained backbone chokes on. So feed the world
model an edge-magnitude obs (sim/edge_filter.py, integer Sobel, env-var ANAKIN_EDGE=1) in BOTH paths
(render output for training; dreamer_pilot.to_training_frame for inference). Parity verified bit-exact
(integration/edge_precheck.py). Edge applied to the CONTENT band [14:50] only; anakin_band grays the
rest (lockstep with inference). geometry (VFoV band + Day-129 up-tilt) unchanged.

Fine-tune not from scratch: dynamics/maneuver/policy transfer; the ENCODER re-adapts hard (color
filters -> edge filters). carry_forward best-protection guards a bad early step. 4 x 500k = 2M steps;
per-batch eval runs through the SAME edge obs, so best_return is exam-condition (edge) directly.

PRE-REGISTERED (clean isolation — edge variable only, NO bg-randomization this run): if the holdout
gate's mean-term improves vs restyle-ft baseline, edges help the gate axis. If transfer is only
partial, the residual is background-texture edges (official TRON bg is edge-dense) -> NEXT add
bg-randomization (APPEARANCE_RANDOMIZATION_SPEC). One variable at a time.

Run: .venv/Scripts/python.exe launch_edge_ft_detached.py   (returns immediately)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_restyle_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_edge_ft")
LOG = os.path.join(DREAMER, "logdir", "edge_ft_orchestrator.log")

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_restyle_ft/best.pt")
else:
    print(f"resuming existing {latest} (carry_state continues)")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band",
    "--envs", "256",
    "--batch-steps", "500000",
    "--num-batches", "4",
    "--train-ratio", "64",
    "--eval-every", "5000",
]

env = dict(os.environ)
env["ANAKIN_EDGE"] = "1"          # edge obs in BOTH render (train) and eval
env["ANAKIN_GATE_MASK"] = "0"     # belt-and-suspenders: never both transforms at once

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED edge-ft orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_EDGE=1 set on subprocess; training + eval both on edge obs.")
