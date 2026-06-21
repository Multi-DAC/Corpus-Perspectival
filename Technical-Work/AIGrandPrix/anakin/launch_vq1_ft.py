"""DETACHED launch: VQ1 reward fine-tune (chain-reliably-FIRST) — Day 141, w/ Clayton.

WHY. The Day-141 rehearsal (`integration/SCALEUP_REHEARSAL_RESULTS.md`) found the real bottleneck:
gate-COUNT is stuck ~1.3 across every checkpoint (seed +23 AND scale-up +65), while RETURN climbs.
Scaling improved flight *speed/quality* through 1-2 gates, NOT chaining. Root cause = the reward:
the Day-124 minimum-TIME mandate trains a VQ2 (speed) policy — speed-scaled gate bonus + speed bonus
reward flying fast, and CRASH_PENALTY(15) << GATE_BONUS(100) makes crashing-after-a-gate nearly free
→ fly-fast-and-crash. **But VQ1 scores GATE-COUNT; speed is VQ2 (Clayton).** We were optimizing the
wrong stage's objective.

FIX (env-var ANAKIN_VQ1=1, wired into sim/vec_env.py + sim/maneuver_env.py, reversible):
  flat gate bonus (pass it, don't race it) + CRASH=100 (= one gate: cross-then-crash ≈ 0, so the policy
  must CHAIN to net positive) + no speed bonus + minimal time penalty. Acquire-then-harden on the
  *reward*: master chaining now; speed (VQ2) is a later fine-tune.

SEED: maneuver_appearance_ft/best.pt — the VALIDATED gate-passer (official appearance gate 0.413 PASS;
adapter-path flight +70.94). Chosen over the scale-up best.pt because the rehearsal showed identical
transfer (~1.3 gates) and the scale-up is MORE speed-over-fit (longer on the speed reward) = more
fly-fast-crash habit to unlearn. We want the cleanest flier, not the fastest.

STACK (keep all robustness; only the REWARD objective changes):
  ANAKIN_VQ1=1            -> chain-first reward (NEW — the fix)
  ANAKIN_APPEARANCE_DR=1  -> keep appearance invariance (official-domain transfer)
  ANAKIN_RATE_RANDOM=1    -> keep control-rate robustness   ANAKIN_PRIV=1 -> keep geometry head

SUCCESS CRITERION (NOT the eval-return — it's now a different scale): run the rehearsal and check
whether GATE-COUNT climbs above 1.3. That is the only metric that matters for VQ1.
  .venv/Scripts/python.exe integration/translation_rehearsal.py --checkpoint <vq1_ft/best.pt> --episodes 10 --env-device cpu

BUDGET: 8 x 500k = 4M. best.pt protected (now protects the best CHAINER). carry_state resume. --smoke.
Run: .venv/Scripts/python.exe launch_vq1_ft.py     (detached)   |   --smoke for foreground verify
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_appearance_ft", "best.pt")  # validated gate-passer
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_vq1_ft")
LOG = os.path.join(DREAMER, "logdir", "vq1_ft_orchestrator.log")
NUM_BATCHES = "8"
SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_appearance_ft/best.pt (validated gate-passer)")
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
env["ANAKIN_VQ1"] = "1"             # chain-first reward (the fix)
env["ANAKIN_APPEARANCE_DR"] = "1"   # keep appearance invariance
env["ANAKIN_DR_WIDTH"] = "1.0"
env["ANAKIN_RATE_RANDOM"] = "1"     # keep rate robustness
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # keep geometry head
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    print("SMOKE: 2000 steps foreground (verify VQ1 reward active + warm-start loads)...")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
                     creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True)
print(f"launched DETACHED VQ1 fine-tune orchestrator pid {p.pid} -> {LOG}")
print("ANAKIN_VQ1=1 (chain-first) + DR + RATE_RANDOM + PRIV; 8x500k off appearance-ft/best.pt. "
      "best.pt protects the best CHAINER. Validate via translation_rehearsal gate-count (>1.3?).")
