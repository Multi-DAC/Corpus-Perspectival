"""DETACHED launch: SCALE-UP run off maneuver_appearance_ft best.pt (Day 140).

WHY NOW. The appearance-DR fine-tune (Day 140 ~13:31) is the first checkpoint that both
PASSES the official appearance gate (holdout_gate_v2 mean-term ratio 0.413 < 0.5, ~59% gap
closed) AND still flies the competition adapter path (translation_rehearsal roundtrip +70.94).
It carries the full validated stack: APPEARANCE_DR + RATE_RANDOM (control-rate cliff) + PRIV
(geometry-grounded latent). That was the LAST robustness piece — "scale LAST" is now satisfied.

But appearance-ft was only a 2M-step fine-tune (4x500k) on a DELIBERATELY HARD distribution
(full-width DR + rate randomization). It transfers, but chains only ~1.3 gates in the rehearsal
vs 6.5 for the native 50 Hz informed checkpoint. The gap is NOT robustness (it passes the gate)
— it is consolidation: the policy needs more steps on the hard stack to master gate-CHAINING
under DR + rate-variation, which is exactly what the in-env acquire-then-harden curriculum
(sim/curriculum.py SequencePlanner: WORD->SENTENCE->PARAGRAPH->ESSAY, complexity gated by
MasteryTracker) ramps as mastery rises.

So this is the principled scale: warm-start from the gate-passing checkpoint, KEEP every
robustness knob on, and give the curriculum room to push gate-count up. best.pt is protected
(only overwritten on eval improvement), so a drift can't lose the known-good flier.

NOT in this run: dt-CONDITIONING (supply dt to the policy as an obs + MLP branch). That is the
clean upgrade over rate-randomization-invariance, but it changes the obs architecture and breaks
clean warm-start (needs partial state-dict load) — a dedicated build session, see
integration/DT_CONDITIONING_SPEC_2026-06-20.md. Rate-randomization already flew, so it is a
refinement, not a blocker for this scale-up.

STACK (identical to the validated appearance-ft run; do not regress any of these):
  ANAKIN_APPEARANCE_DR=1  width 1.0  -> appearance invariance (the gate-passer)
  ANAKIN_RATE_RANDOM=1    dt[0.020,0.040] -> control-rate robustness (30 Hz deploy)
  ANAKIN_PRIV=1           -> geometry-grounded latent (anti-appearance-crutch)

BUDGET: 12 x 500k = 6M steps (3x the appearance-ft fine-tune; room for the curriculum to ramp).
Adjust NUM_BATCHES below for available time — carry_forward checkpoints every batch and protects
best.pt, so stopping early loses nothing. carry_state.json resumes a relaunch from the latest batch.

GATE (offline, no flight) after best.pt updates:
  .venv/Scripts/python.exe integration/offline_official_check.py --ckpt <scaleup_ft/best.pt> --tag scaleup
  .venv/Scripts/python.exe integration/translation_rehearsal.py    (does gate-count rise above 1.3?)

Run: .venv/Scripts/python.exe launch_scaleup_ft.py            (returns immediately; orchestrator detached)
     .venv/Scripts/python.exe launch_scaleup_ft.py --smoke    (2000 steps foreground; verify warm-start + DR)
"""
import os
import shutil
import subprocess
import sys

ANAKIN = os.path.dirname(os.path.abspath(__file__))
PY = os.path.join(ANAKIN, ".venv", "Scripts", "python.exe")
DREAMER = os.path.join(ANAKIN, "third_party", "dreamerv3-torch")
SRC_BEST = os.path.join(DREAMER, "logdir", "maneuver_appearance_ft", "best.pt")  # gate-passing flier
LOGDIR = os.path.join(DREAMER, "logdir", "maneuver_scaleup_ft")
LOG = os.path.join(DREAMER, "logdir", "scaleup_ft_orchestrator.log")

NUM_BATCHES = "12"   # 12 x 500k = 6M steps; adjust for available time (best.pt protected, safe to stop)

SMOKE = "--smoke" in sys.argv

os.makedirs(LOGDIR, exist_ok=True)
latest = os.path.join(LOGDIR, "latest.pt")
if not os.path.exists(latest):
    if not os.path.exists(SRC_BEST):
        sys.exit(f"missing seed checkpoint: {SRC_BEST}")
    shutil.copy2(SRC_BEST, latest)
    print(f"seeded {latest} from maneuver_appearance_ft/best.pt (the gate-passing flier)")
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
env["ANAKIN_APPEARANCE_DR"] = "1"   # KEEP appearance invariance (the gate-passer)
env["ANAKIN_DR_WIDTH"] = "1.0"      # KEEP full width (priv head grounds it)
env["ANAKIN_RATE_RANDOM"] = "1"     # KEEP control-rate robustness
env["ANAKIN_DT_MIN"] = "0.020"
env["ANAKIN_DT_MAX"] = "0.040"
env["ANAKIN_PRIV"] = "1"            # KEEP geometry-grounded latent
env["ANAKIN_EDGE"] = "0"
env["ANAKIN_GATE_MASK"] = "0"

if SMOKE:
    # foreground, tiny: confirm the warm-start loads + DR is active before committing the 6M run
    print("SMOKE: 2000 steps foreground (verifying warm-start from appearance-ft + appearance DR active)...")
    sys.exit(subprocess.call(cmd, cwd=DREAMER, env=env))

DETACHED_PROCESS = 0x00000008
CREATE_NEW_PROCESS_GROUP = 0x00000200
logf = open(LOG, "a")
p = subprocess.Popen(
    cmd, stdout=logf, stderr=subprocess.STDOUT, cwd=DREAMER, env=env,
    creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP, close_fds=True,
)
print(f"launched DETACHED scale-up orchestrator pid {p.pid} -> {LOG}")
print(f"APPEARANCE_DR=1 width=1.0 + RATE_RANDOM + PRIV; {NUM_BATCHES}x500k steps, "
      "warm-started from the gate-passing appearance-ft/best.pt. best.pt protected. "
      "Gate offline via integration/offline_official_check.py + translation_rehearsal.py.")
