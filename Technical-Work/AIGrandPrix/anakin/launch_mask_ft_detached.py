"""DETACHED launch: SEGMENTATION-FRONT-END fine-tune off band-ft best.pt (+2142.53).

The Day-134 route change (integration/SEG_ROUTE_DECISION_2026-06-14.md): holdout_gate_v2 at
robust n=400 showed the official<->training gap is BACKGROUND TEXTURE, not gate color (palette
already matched). Every real-race winner decouples perception from control; SkyDreamer = our
DreamerV3 fed gate MASKS instead of RGB. We keep the world model + maneuver curriculum and isolate
the gate (sim/gate_mask.py, RGB-ratio rule, env-var ANAKIN_GATE_MASK=1) in BOTH obs paths
(sim/render.py output for training; integration/dreamer_pilot.to_training_frame for inference).

Pre-check (integration/mask_precheck.py): pixel-space Fréchet mean-term collapsed 4x under masking
(34.6 -> 8.6). Both VFoV band (anakin_band) and the Day-129 tilt fix stay in — geometry is still
official. Fine-tune (not from scratch): the dynamics/policy transfer; only the encoder must re-adapt
to gate-on-black input. carry_forward best-protection guards against a bad early step.

Seeds a FRESH logdir (maneuver_mask_ft) with band-ft best.pt as latest.pt. 4 x 500k = 2M steps;
per-batch eval runs through the SAME masked obs (env var set on this subprocess), so reported
best_return is exam-condition (masked) performance directly.

Run: .venv/Scripts/python.exe launch_mask_ft_detached.py   (returns immediately)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_band_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_mask_ft")
LOG = os.path.join(DREAMER, "logdir", "mask_ft_orchestrator.log")

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_band_ft/best.pt (+2142.53)")
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
env["ANAKIN_GATE_MASK"] = "1"   # gate-isolate obs in BOTH render (train) and eval

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED mask-ft orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_GATE_MASK=1 set on subprocess; training + eval both on gate-isolated obs.")
