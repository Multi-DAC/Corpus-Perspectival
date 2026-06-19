"""DETACHED launch: APPEARANCE-DR fine-tune off maneuver_rate_ft best.pt (Day 139).

THE perception fix. Flight #3 (rate-ft) confirmed the control-rate cliff is solved but the policy
spins out on the OFFICIAL sim because it is APPEARANCE-OOD: trained on a bare red gate over flat
noise, it cannot parse the official world (structured wireframe + blue guide-tube + small distant
gates) and saturates roll/throttle. Proven offline: integration/offline_official_check.py shows the
rate-ft checkpoint pins roll mean -12.87, 63% saturated, throttle 0.97 on the captured official
start frames. (Diagnosis: 2026-06-19 daily log; appearance-DR was BUILT in render.py but never
enabled in any training run.)

FIX (the spec's ACTIVE route, now strengthened): enable appearance domain-randomization so the
official look is one sample inside a wide trained manifold. render.py DR (env-var ANAKIN_APPEARANCE_DR=1):
gate hue/sat/val jitter (breaks color-lineage), bloom, brightness/illumination, smooth bg texture,
the ribbon as a randomized DISTRACTOR (never a cue), and NEW _bg_clutter (sharp structured blocks =
the confirmed dominant gap the smooth texture couldn't make). Don't MATCH the official appearance —
be INVARIANT to it.

STACK ALL THREE on this run (seeded off rate_ft which already carries them):
  ANAKIN_APPEARANCE_DR=1  -> appearance invariance (NEW)
  ANAKIN_RATE_RANDOM=1    -> KEEP control-rate robustness (don't regress the rate-ft win)
  ANAKIN_PRIV=1           -> KEEP geometry-grounded latent (priv_state head — the anti-crutch ground)
Course-layout variety (maneuver lib) and off-screen-target acquisition (random heading vs fixed +x
facing => gate 0 at a random bearing incl. behind) are ALREADY in the env — no change needed.

BUDGET: 4 x 500k = 2M steps (full-strength appearance DR is a wider distribution than the original
light spec; give it room). DR_WIDTH=1.0 (max robustness, Clayton's "as robustly as possible"; the
priv geometry head grounds it). If it destabilizes early, fall back to a curriculum: relaunch at
DR_WIDTH 0.5 then resume at 1.0 (carry_state continues from latest.pt).

GATE (offline, no flight): after best.pt updates, run
  .venv python integration/offline_official_check.py --ckpt <appearance_ft/best.pt> --tag 112512
  PASS = roll-saturation falls from 63% toward ~0 and throttle normalizes off 0.97.

Run: .venv/Scripts/python.exe launch_appearance_ft.py   (returns immediately; gate offline)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_rate_ft", "best.pt")   # rate+geometry seed
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_appearance_ft")
LOG = os.path.join(DREAMER, "logdir", "appearance_ft_orchestrator.log")

SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_rate_ft/best.pt")
else:
    print(f"resuming existing {latest} (carry_state continues)")

cmd = [
    PY, "-u", os.path.join(ANAKIN, "carry_forward_train.py"),
    "--logdir", LOGDIR,
    "--config", "anakin_maneuver anakin_band anakin_informed",
    "--envs", "256",
    "--batch-steps", "2000" if SMOKE else "500000",
    "--num-batches", "1" if SMOKE else "4",
    "--train-ratio", "64",
    "--eval-every", "5000",
]

env = dict(os.environ)
env["ANAKIN_APPEARANCE_DR"] = "1"   # render.py: full appearance domain randomization (NEW — the fix)
env["ANAKIN_DR_WIDTH"] = "1.0"      # max robustness; priv head grounds it. Curriculum = 0.5 then 1.0.
env["ANAKIN_RATE_RANDOM"] = "1"     # KEEP rate robustness (don't regress the rate-ft win)
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # KEEP geometry-grounded latent (priv_state head)
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    # foreground, tiny, so we can see it run + confirm DR active before committing the 2M run
    print("SMOKE: 2000 steps foreground (verifying launch + appearance DR active)...")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED appearance-DR ft orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_APPEARANCE_DR=1 width=1.0 + RATE_RANDOM + PRIV; 2M steps (4x500k). "
      "Gate offline via integration/offline_official_check.py on the new best.pt (tag 112512).")
