"""DETACHED launch: VQ1 reward-v2 fine-tune (the TIMIDITY-TRAP fix) — Day 141.

WHY v2. v1 (`ANAKIN_VQ1=1`, CRASH=GATE=100) was rehearsed after batch 1 vs the seed baseline
(`integration/VQ1_BATCH1_VERDICT.md`): NO chaining gain (roundtrip gates 1.3→1.2, return +68→+22).
Diagnosis (basement LC56): CRASH=GATE makes cross-then-crash net ZERO ⇒ "one gate is enough" is an
ABSORBING fixed point ⇒ the policy learns timidity, not chaining. A productive cycle stays compact
iff its competing fixed point is ESCAPABLE = leaving it has positive value.

FIX v2 (`ANAKIN_VQ1=2`, wired in sim/vec_env.py + sim/maneuver_env.py): CRASH=40 < GATE=100, so
cross-then-crash nets +60 → the 2nd gate is ALWAYS worth attempting → the trap is de-absorbed.
Chaining-vs-stop threshold p* = c/(g+c) drops 0.50 (v1) → 0.29 (v2), covering the early-training band.
SINGLE-VARIABLE vs v1 — ONLY the crash penalty changes (no superlinear consecutive-gate bonus; that's
a v3 if v2 still stalls, to keep the test clean). This is the live falsifiable prediction of LC56:
v2 should chain where v1 could not, in the 29–50% gate-success window.

SEED: maneuver_appearance_ft/best.pt — the SAME validated gate-passer v1 started from (NOT the timid
v1-b1 checkpoint). We re-run the reward experiment from the clean flier with only the reward changed.

SEPARATE LOGDIR (maneuver_vq1_v2_ft) — does NOT touch the running v1 run (maneuver_vq1_ft). Safe to
launch alongside it, or after stopping v1. Same robustness stack (DR + RATE_RANDOM + PRIV).

SUCCESS CRITERION (same as v1): rehearsal GATE-COUNT, not eval-return.
  .venv/Scripts/python.exe integration/translation_rehearsal.py --checkpoint <vq1_v2_ft/best.pt> --episodes 10 --env-device cpu
  -> compare to seed 1.3 and v1-b1 1.2. v2 confirms LC56 iff gates climb above ~1.3.

Run: .venv/Scripts/python.exe launch_vq1_v2_ft.py      (detached)   |   --smoke for foreground verify
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_appearance_ft", "best.pt")  # validated gate-passer (the SEED)
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_vq1_v2_ft")  # SEPARATE from the running v1 run
LOG = os.path.join(DREAMER, "logdir", "vq1_v2_ft_orchestrator.log")
NUM_BATCHES = "8"
SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_appearance_ft/best.pt (validated gate-passer, same as v1)")
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
env["ANAKIN_VQ1"] = "2"             # reward-v2: CRASH=40 < GATE (the timidity-trap fix)
env["ANAKIN_APPEARANCE_DR"] = "1"   # keep appearance invariance
env["ANAKIN_DR_WIDTH"] = "1.0"
env["ANAKIN_RATE_RANDOM"] = "1"     # keep rate robustness
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # keep geometry head
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    print("SMOKE: 2000 steps foreground (verify ANAKIN_VQ1=2 reward active + warm-start loads)...")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
                     creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
print(f"launched DETACHED VQ1-v2 fine-tune orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_VQ1=2 (CRASH=40, trap de-absorbed) + DR + RATE_RANDOM + PRIV; 8x500k off appearance-ft/best.pt. "
      "SEPARATE logdir maneuver_vq1_v2_ft. Validate via translation_rehearsal gate-count vs seed 1.3 / v1 1.2.")
