"""DETACHED launch: INFORMED-Dreamer (route 3) fine-tune off restyle-ft best.pt (Day 136).

The cheapest test of the privileged-information route (SkyDreamer / informed Dreamer 2510.14783),
chosen from first principles after mask (color-keyed) and edge (texture-amplifying) both FALSIFIED,
both pinning the residual to background texture. Informed Dreamer attacks the diagnosed ROOT directly:
the world-model latent is keyed to APPEARANCE because nothing ever forced it toward GEOMETRY. Here a
decoder-only head (ANAKIN_PRIV=1) reconstructs a privileged 9-d body-frame geometric vector
(vec-to-gate + gate-normal + velocity) the ENCODER never sees -> gradients flow back through the RSSM
into the encoder, pressuring the latent to encode geometry instead of pixels. priv_state is needed
ONLY in training; the deployed policy maps image->latent->motor exactly as before.

Wiring smoke-verified Day 136: Decoder MLP shapes {'priv_state': (9,)}, encoder blind, priv_state_loss
finite (~6.5 symlog), strict=False seed load + optim-restore skip clean, gate loads the priv superset.

SHORT budget: 2 x 500k = 1M steps (the cheapest-first-step; the edge run was 2M). If the holdout gate's
mean-term improves vs the band-ft baseline (pre-registered pass: ratio < 0.5), grounding the latent in
geometry closes the official-domain gap -> commit the longer run + curriculum. If not, route 3 is
weakened and route 1 (renderer appearance-DR: illumination + bg-texture) is next. One variable.

Run: .venv/Scripts/python.exe launch_informed_ft.py   (returns immediately; gate via the watcher)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_restyle_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_informed_ft")
LOG = os.path.join(DREAMER, "logdir", "informed_ft_orchestrator.log")

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
    "--config", "anakin_maneuver anakin_band anakin_informed",
    "--envs", "256",
    "--batch-steps", "500000",
    "--num-batches", "2",
    "--train-ratio", "64",
    "--eval-every", "5000",
]

env = dict(os.environ)
env["ANAKIN_PRIV"] = "1"           # informed-Dreamer: env emits priv_state; non-strict seed load
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED informed-ft orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_PRIV=1; 1M steps (2x500k). Launch launch_postrun_informed_watcher.py to auto-gate.")
