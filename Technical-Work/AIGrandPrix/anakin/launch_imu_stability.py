"""DETACHED launch: IMU + STABILITY fine-tune — Day 147 (the holistic VQ1 fix).

WHY (HOLISTIC_DIAGNOSIS_2026-06-27.md, grounded in real flight frames + Clayton's eyes):
the real bottleneck is EARLY-FLIGHT INSTABILITY (bobbing/overshoot/spin-out-at-start), compounded by a
real-start PERCEPTION gap (small distant gate + dominant ribbon in the 64x64). The widegap run REGRESSED
because more training made it AGGRESSIVE, trading away the gentleness that let vq1_v2 drift past the weak
start-signal until the gate grows legible. Rate-cliff and frame-convention were FALSIFIED today.

THE FIX = stability, two reinforcing pushes:
  1. ANAKIN_IMU=1  — raw 6-DoF IMU (gyro+accel) the encoder SEES → proprioception: the policy can FEEL its
     attitude/rates instead of inferring from pixels, the direct cure for early-flight instability. Also the
     visual-inertial state estimation VQ2 mandates. Raw gyro+accel match HIGHRES_IMU so train==deploy.
  2. ANAKIN_SMOOTH — action-smoothing reward penalty (-s*dt*||a-a_prev||^2): anti-bobbing, and it penalises a
     violent first command = the start spin-out directly.

SEED = maneuver_vq1_v2_ft/best.pt — the GENTLE checkpoint that APPROACHED the gate, NOT the over-aggressive
widegap. Adding IMU augments the architecture (fresh IMU encoder/decoder branch); the backbone warm-starts,
the IMU branch trains from scratch (needs non-strict load — verify in --smoke).

Keeps the banked wins: VQ1=2 reward, APPEARANCE_DR (~59% gate gap closed), RATE_RANDOM (rate-robust), WIDEGAP
(official gate-spacing calibration), PRIV (geometry head). Separate logdir.

ASSESS (don't tune blind): the smoothing scale (default 3) needs A/B — too high prevents tight turns. After
batch ~1-2, rehearse early. VALIDATE ON THE REAL SIM (Training Flights), not the in-sim rehearsal (today's lesson).

Run: .venv/Scripts/python.exe launch_imu_stability.py            (detached)
     .venv/Scripts/python.exe launch_imu_stability.py --smoke    (2000-step foreground verify: IMU obs builds,
                                                                  warm-start partial-loads, training steps)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_vq1_v2_ft", "best.pt")   # GENTLE seed (approached gate)
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_imu_stability")
LOG = os.path.join(DREAMER, "logdir", "imu_stability_orchestrator.log")
NUM_BATCHES = "20"           # ~10M steps; stoppable anytime, best.pt protected per batch
SMOOTH = os.environ.get("ANAKIN_SMOOTH", "3.0")   # tunable; default 3.0 (A/B candidate)
SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_vq1_v2_ft/best.pt (the GENTLE official-sim flier)")
else:
    print(f"resuming existing {latest} (carry_state continues)")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band anakin_informed anakin_imu",
    "--envs", "256",
    "--batch-steps", "2000" if SMOKE else "500000",
    "--num-batches", "1" if SMOKE else NUM_BATCHES,
    "--train-ratio", "64",
    "--eval-every", "5000",
]
env = dict(os.environ)
env["ANAKIN_IMU"] = "1"             # ★ raw gyro+accel into obs (encoder sees it) — proprioception/stability
env["ANAKIN_IMU_NOISE"] = "0.02"    # sensor DR so gyro isn't a perfect echo of the action
env["ANAKIN_SMOOTH"] = SMOOTH       # ★ action-smoothing penalty (anti-bobbing + anti-violent-first-command)
env["ANAKIN_VQ1"] = "2"             # keep the timidity-trap fix (CRASH=40 < GATE=100)
env["ANAKIN_WIDEGAP"] = "1"         # keep official gate-spacing calibration
env["ANAKIN_APPEARANCE_DR"] = "1"   # keep appearance invariance (~59% gate gap closed)
env["ANAKIN_DR_WIDTH"] = "1.0"
env["ANAKIN_RATE_RANDOM"] = "1"     # keep rate robustness (confirmed rate-robust today)
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # keep geometry head
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    print(f"SMOKE: 2000 steps foreground. Verifies: IMU dict-obs builds, anakin_imu config routes imu->encoder,"
          f" warm-start partial-loads vq1_v2 (backbone) + fresh IMU branch, SMOOTH={SMOOTH} active, trains.")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
                     creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
print(f"launched DETACHED IMU+stability fine-tune orchestrator pid {p.pid} -> {LOG}")
print(f"IMU=1 + SMOOTH={SMOOTH} + VQ1=2 + WIDEGAP + DR + RATE_RANDOM + PRIV; 20x500k (~10M steps) off the "
      f"GENTLE vq1_v2/best.pt. logdir maneuver_imu_stability. Assess early; VALIDATE ON THE REAL SIM.")
