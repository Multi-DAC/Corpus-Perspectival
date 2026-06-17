"""control_rate_rehearsal.py — does the policy survive the DEPLOY control rate? (appearance-free)

THE PATTERN (2026-06-17): every transfer attempt and every instrument we built operates on a
single axis — the static APPEARANCE of a single frame (restyle, mask, edge, informed, DR, the
resolution probe; the holdout gate is a single-frame embedding distance; the translation rehearsal
runs inside our own sim). None of them has a TIME axis.

THE FIND: training decides at dt=0.02 (50 Hz; sim/env.py + dynamics.step). The official deploy
decides ONCE PER 30 Hz vision frame (run_dreamer.py:297, frame-driven; comment line 24). The policy
emits body-RATE commands (rad/s) HELD until the next decision — so at deploy every maneuver command
is applied ~1.67x longer than trained, and the world-model's forward prediction (calibrated to 20 ms
of inter-frame motion) sees 33 ms -> over-rotation + latent drift -> spin-out. "The maneuvers train
fine; it's how they're INVOKED that's the problem." Invisible to the gate (no time) and the rehearsal
(runs at 50 Hz).

THIS TEST isolates CONTROL RATE with appearance held perfectly constant (our own clean renderer):
sweep the control dt, same checkpoint, same tracks (fixed seeds), same PHYSICAL horizon (so returns
are comparable). High at 0.02 and collapsing toward 0.0333 => rate mismatch is a real, appearance-
independent failure mode -> fix = rate-matched / rate-randomized fine-tune (cheap; build/controls/
vision unchanged). Flat => policy is rate-robust and the killer is elsewhere.

Run (anakin .venv):
  .venv/Scripts/python.exe integration/control_rate_rehearsal.py
"""
import os
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
ANAKIN = os.path.dirname(_HERE)
sys.path.insert(0, _HERE)
sys.path.insert(0, os.path.join(ANAKIN, "sim"))

from holdout_gate_v2 import LOGDIR  # noqa: E402

# maneuver_informed_ft is the validated strong flier in THIS rehearsal harness (direct +600.8;
# translation_rehearsal). band-ft's +2142 was a training-batch metric, NOT a rehearsal flight —
# it scores ~-20 here, so it cannot anchor a rate test. Use the checkpoint that actually flies.
CKPT = os.path.join(LOGDIR, "maneuver_informed_ft", "best.pt")
# 1200 steps @ dt=0.02 = 24 physical seconds — the exact horizon translation_rehearsal validates
# the direct anchor at. Held CONSTANT across dt so returns are comparable AND the 50 Hz row must
# reproduce the known-good direct baseline or the instrument is still broken.
HORIZON_S = 24.0
N_EPS = 12

# (label, control dt). 0.0200 = 50 Hz training clock; 0.0333 = 30 Hz official deploy clock.
RATES = [
    ("50 Hz (TRAIN)",   0.0200),
    ("40 Hz",           0.0250),
    ("33 Hz",           0.0303),
    ("30 Hz (DEPLOY)",  0.0333),
    ("24 Hz",           0.0417),
]


def run_rate(pilot, dt, n_eps=N_EPS, device="cuda"):
    sys.path.insert(0, os.path.join(ANAKIN, "sim"))
    from maneuver_env import AnakinManeuverEnv   # the env the policy trained on (validated harness)
    max_steps = max(1, round(HORIZON_S / dt))    # constant physical horizon
    seeds = list(range(1000, 1000 + n_eps))      # same seeds translation_rehearsal uses
    rets, gates = [], []
    for seed in seeds:
        env = AnakinManeuverEnv(max_steps=max_steps, dt=dt, device=device, seed=seed)
        obs, _ = env.reset(seed=seed)
        pilot.reset()
        ep_ret = 0.0
        info = {}
        for _ in range(max_steps):
            a = pilot.act_training_frame(obs)    # 'direct' interface — the validated +600 anchor
            obs, r, term, trunc, info = env.step(a)
            ep_ret += float(r)
            if term or trunc:
                break
        rets.append(ep_ret)
        gates.append(int(info.get("gates_passed", env._cur)))
    return np.array(rets), np.array(gates)


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint", default=CKPT)
    ap.add_argument("--episodes", type=int, default=N_EPS)
    args = ap.parse_args()
    n_eps = args.episodes

    from dreamer_pilot import DreamerPilot
    ckpt = args.checkpoint
    assert os.path.exists(ckpt), f"checkpoint missing: {ckpt}"
    pilot = DreamerPilot(ckpt)
    print(f"\ncheckpoint: {ckpt}")
    print(f"horizon {HORIZON_S:.0f}s, {n_eps} eps/rate, same seeds+tracks across rates, "
          f"appearance identical (clean renderer)\n")
    print(f"{'rate':>16} {'dt':>7} {'mean_ret':>9} {'std':>7} {'gates/ep':>9} {'vs TRAIN':>9}")
    print("  " + "-" * 64)
    base = None
    rows = []
    for name, dt in RATES:
        rets, gates = run_rate(pilot, dt, n_eps)
        m = float(rets.mean())
        if base is None:
            base = m
        rel = (m / base) if base not in (0, None) else float("nan")
        rows.append((name, dt, m, gates.mean(), rel))
        print(f"{name:>16} {dt:7.4f} {m:9.1f} {rets.std():7.1f} {gates.mean():9.2f} {rel:8.0%}")
    print("  " + "-" * 64)

    train_m = rows[0][2]
    deploy_m = next(r[2] for r in rows if "DEPLOY" in r[0])
    train_g = rows[0][3]
    deploy_g = next(r[3] for r in rows if "DEPLOY" in r[0])
    drop = 1.0 - (deploy_m / train_m) if train_m else float("nan")
    print(f"\n50Hz->30Hz return change: {deploy_m:.1f} vs {train_m:.1f}  ({drop:+.0%})")
    print(f"50Hz->30Hz gates/ep:      {deploy_g:.2f} vs {train_g:.2f}")
    if drop > 0.30 or (train_g - deploy_g) > 0.5:
        print("\nVERDICT: CONTROL-RATE MISMATCH CONFIRMED as an appearance-independent failure mode.")
        print("         The policy degrades at the deploy clock with PERFECT appearance. The killer")
        print("         (or a killer) is the 50Hz-train/30Hz-deploy gap, not (only) appearance.")
        print("         Fix: rate-matched or rate-RANDOMIZED fine-tune (cheap; build/controls/vision")
        print("         unchanged) — and it transfers to real courses (variable latency) for free.")
    else:
        print("\nVERDICT: policy is RATE-ROBUST across 50->30 Hz. The rate mismatch is NOT the killer;")
        print("         the failure is elsewhere (back to appearance / closed-loop instrumentation).")


if __name__ == "__main__":
    main()
