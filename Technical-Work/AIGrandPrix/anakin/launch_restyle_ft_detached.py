"""DETACHED launch: VQ1-appearance fine-tune off band-ft best.pt (+421.91).

Two Day-129 camera-truth fixes trained in together:
  1. VFoV band: the competition feed's ~59deg vertical FoV costs the 90deg-trained
     pilot -68% return (translation_rehearsal). anakin_band overlay grays rows outside
     [14:50] (lockstep with integration/dreamer_pilot.to_training_frame).
  2. Tilt sign: vq1_spec.txt:325 says the camera tilts UP 20deg; render.py had trained
     DOWN 20deg (40deg total error, found in Day-129 recon, fixed in sim/render.py).
     The fine-tune relearns the official view direction off best.pt's warm dynamics.

Seeds a FRESH logdir (maneuver_restyle_ft) with best.pt as latest.pt — the scale-2 run's
artifacts are never touched; carry-forward's best-protection then guards the fine-tune
itself. 4 x 500k = 2M steps; per-batch eval through the SAME masked obs, so the
carry_state returns measure exam-condition performance directly.

Run: .venv/Scripts/python.exe launch_band_ft_detached.py   (returns immediately)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_band_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_restyle_ft")
LOG = os.path.join(DREAMER, "logdir", "restyle_ft_orchestrator.log")

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_band_ft/best.pt (+421.91)")
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

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED band-ft orchestrator pid {p.pid} -> {LOG}")
