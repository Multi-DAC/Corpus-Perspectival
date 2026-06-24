"""DETACHED launch: VQ1 BUDGET RUN w/ gate-spacing calibration — Day 144 (post first official flight).

WHY. vq1_v2 FLIES the official sim (Day 144 first flight): takes off, navigates to a gate, commits —
calibration (tilt/handedness/thrust) is SOUND. Failures = (1) bobbing/vertical instability,
(2) overshoots the gate, (3) loses control downrange. Per A154, many-gate chaining is BUDGET-governed
(capability emerges ~10-20M steps), and vq1_v2 was only a ~500k-step fine-tune. So: more budget.

PLUS the geometry calibration. Captured official_track shows gates 24-39 m apart (mean 27); our default
grammar is mostly 3-14 m (0% of gaps in the official band — the overshoot's cleanest explanation). This
run sets ANAKIN_WIDEGAP=1 (sim/maneuvers.py): stretches the gentle/straight/vertical maneuver family's
inter-gate distance into the official band (smoke: 0% -> 13% in [24,39], p90 16 -> 32 m), tight precision
turns untouched. Distribution-calibration ONLY — still pixels-only, no geometry fed to the agent, NOT a
fixed-layout overfit. "Generalize first"; a course-tight fine-tune is held for the final VQ1 stretch.

SEED: maneuver_vq1_v2_ft/best.pt (the validated official-sim flier). Continue improving THAT policy.
SEPARATE LOGDIR maneuver_vq1_v3_widegap (does not touch vq1_v2). Same robustness stack (VQ1=2 reward +
DR + RATE_RANDOM + PRIV) + WIDEGAP. best.pt protected per batch -> rehearse intermediate checkpoints.

ASSESS (don't tune blind): after batch ~1-2, rehearse gate-count vs vq1_v2's 1.9:
  .venv/Scripts/python.exe integration/translation_rehearsal.py --checkpoint <vq1_v3_widegap/best.pt> --episodes 10 --env-device cpu
If overshoot persists, escalate calibration (bias maneuver SELECTION toward the long family, or raise _GAP_K).

Run: .venv/Scripts/python.exe launch_vq1_v3_widegap.py   (detached)  |  --smoke for foreground verify
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_vq1_v2_ft", "best.pt")   # the official-sim flier
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_vq1_v3_widegap")
LOG = os.path.join(DREAMER, "logdir", "vq1_v3_widegap_orchestrator.log")
NUM_BATCHES = "24"            # ~12M steps; stoppable anytime, best.pt protected per batch
SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_vq1_v2_ft/best.pt (the official-sim flier)")
else:
    print(f"resuming existing {latest} (carry_state continues)")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band anakin_informed",
    "--envs", "256",
    "--batch-steps", "2000" if SMOKE else "500000",
    "--num-batches", "1" if SMOKE else NUM_BATCHES,
    "--train-ratio", "64",
    "--eval-every", "5000",
]
env = dict(os.environ)
env["ANAKIN_VQ1"] = "2"             # keep the timidity-trap fix (CRASH=40 < GATE=100)
env["ANAKIN_WIDEGAP"] = "1"         # ★ gate-spacing calibration to the official course (this run)
env["ANAKIN_APPEARANCE_DR"] = "1"   # keep appearance invariance
env["ANAKIN_DR_WIDTH"] = "1.0"
env["ANAKIN_RATE_RANDOM"] = "1"     # keep rate robustness
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # keep geometry head
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    print("SMOKE: 2000 steps foreground (verify warm-start from vq1_v2 loads + WIDEGAP active + trains)...")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
                     creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
print(f"launched DETACHED VQ1-v3 widegap budget run orchestrator pid {p.pid} -> {LOG}")
print("VQ1=2 + WIDEGAP=1 + DR + RATE_RANDOM + PRIV; 24x500k (~12M steps) off vq1_v2/best.pt. "
      "logdir maneuver_vq1_v3_widegap. Rehearse intermediate best.pt vs vq1_v2's 1.9 gates.")
