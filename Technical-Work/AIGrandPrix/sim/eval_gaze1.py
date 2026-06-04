"""
eval_gaze1.py — Deterministic eval of the gaze-aware fine-tune (train_vision_corrected.py, gaze1 run).

The training curve (stochastic rollouts) peaked ~4.2 gates/ep near 500k-800k steps then overtrained
down to ~1.9 by 3M. This evals the saved checkpoints DETERMINISTICALLY on the exact config they were
trained for (+x nose +20deg tilt, dead-reckon, all-W3 detector) to get decision-grade numbers
comparable to the references:
    frozen Anakin, +x+20tilt deploy cam  = 1.42  (nose_axis_test)
    clean ceiling (omniscient, no cam)    = 4.83
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from stable_baselines3 import PPO
from sweep_corrected_camera import run, ALL_W3, CLEAN, TEACHER, c20, s20

RUN = os.path.join(HERE, "runs", "vision_corrected_gaze1_1780465000")
NOSE_TILT = [c20, 0.0, s20]          # +x nose +20deg up — the deploy + training config
EPISODES, MAX_STEPS, SEED = 24, 15000, 2026

CKPTS = [
    ("frozen Anakin (ref)", TEACHER),
    ("gaze1  500k", os.path.join(RUN, "checkpoints", "vc_500000_steps.zip")),
    ("gaze1 1000k", os.path.join(RUN, "checkpoints", "vc_1000000_steps.zip")),
    ("gaze1 1500k", os.path.join(RUN, "checkpoints", "vc_1500000_steps.zip")),
    ("gaze1 2000k", os.path.join(RUN, "checkpoints", "vc_2000000_steps.zip")),
    ("gaze1 final", os.path.join(RUN, "final_model.zip")),
]


def main():
    print(f"Gaze-aware fine-tune deterministic eval (+x+20tilt deploy cam, reckon, all-W3, "
          f"n={EPISODES})")
    print(f"  refs: frozen +x+20tilt deploy = 1.42 | clean ceiling = 4.83\n")
    print(f"  {'checkpoint':>20} {'gates/ep':>9} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    t0 = time.time()
    for label, path in CKPTS:
        if not os.path.exists(path):
            print(f"  {label:>20}   MISSING {path}"); continue
        model = PPO.load(path, device="cpu")
        m, mx, ge1, took = run(model, NOSE_TILT, True, ALL_W3, EPISODES, MAX_STEPS, SEED)
        print(f"  {label:>20} {m:>9.2f} {mx:>4d} {ge1:>6.0f} {took:>4d}/{EPISODES:<3d}", flush=True)
    print(f"\n  done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
