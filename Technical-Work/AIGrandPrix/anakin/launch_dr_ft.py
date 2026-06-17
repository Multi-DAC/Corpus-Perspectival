"""DETACHED launch: APPEARANCE-DR fine-tune off restyle-ft best.pt (Day 136).

THE SURVIVING ROUTE. mask (color-keyed), edge (texture-amplifying), and informed-Dreamer
(geometry head) all FALSIFIED the official-appearance holdout gate — each improved rendered/
rehearsal metrics but left the official harvest OOD, all pinning the residual to BACKGROUND
TEXTURE. Spec: integration/APPEARANCE_RANDOMIZATION_SPEC_2026-06-15.md. Clayton's call (Day 136
night): commit to appearance-DR.

The move (per the spec's one-line summary): stop matching the official gate; train Anakin to not
care what the gate/background/lighting looks like. The backbone is the wrong color (color-lineage
problem) and the harvest is a biased ruler — invariance routes around both. DR is implemented in
sim/render.py, env-var gated (ANAKIN_APPEARANCE_DR=1, ANAKIN_DR_WIDTH in [0,1]); render-level only,
no new model wiring (contrast: informed needed a priv_state head). Smoke-verified Day 136: DR off ==
byte-identical; DR on == per-env hue/sat/val + illumination (#1 lit. knob) + structured bg-texture
(the confirmed gap) + bloom, no NaN, real cross-env variation.

CHEAPEST-FIRST-STEP (Mirror discipline: measure the small version first): 2 x 500k = 1M steps at a
MODERATE width (0.5) off restyle_ft/best.pt. Pre-registered pass: the holdout gate's mean-term ratio
(adapted/band-ft) improves toward < 0.5 (DR closes the official-domain gap). If it moves the needle
-> commit the multi-M run WITH a widening curriculum + held-out-slice eval (Clayton-gated, VQ1 path).
If not -> route 1 is weakened and the heavy PencilNet decoupled pose front-end (route c) is next.

Run: .venv/Scripts/python.exe launch_dr_ft.py   (returns immediately; gate via the watcher)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_restyle_ft", "best.pt")
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_dr_ft")
LOG = os.path.join(DREAMER, "logdir", "dr_ft_orchestrator.log")

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
    "--config", "anakin_maneuver anakin_band",   # band-ft baseline config; DR is render-level (no config)
    "--envs", "256",
    "--batch-steps", "500000",
    "--num-batches", "2",
    "--train-ratio", "64",
    "--eval-every", "5000",
]

env = dict(os.environ)
env["ANAKIN_APPEARANCE_DR"] = "1"   # the route
env["ANAKIN_DR_WIDTH"] = "0.5"      # moderate width for the cheapest-first-step (curriculum widens later)
env["ANAKIN_PRIV"] = "0"
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200

logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED appearance-DR orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_APPEARANCE_DR=1 DR_WIDTH=0.5; 1M steps (2x500k). Launch the postrun DR watcher to auto-gate.")
