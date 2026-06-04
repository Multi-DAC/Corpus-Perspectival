"""
sweep_noise.py — Perception-quality sensitivity sweep for the Anakin (80M) teacher.

Reverse-engineers the perception SPEC: how many gates/ep does Anakin fly as gate-derived
perception degrades from privileged (clean) toward the W3-calibrated detector error and beyond?
Anakin drives directly from the (scaled-noise) perception obs — NO retraining. This gives a
lower-bound performance-vs-perception-quality curve and locates the cliff: if it stays high
until ~W3 then falls, we are obs-limited and know the detector spec; if it degrades smoothly
from clean, temporal filtering is mandatory.

scale = 0.0 -> perfect perception (== privileged);  1.0 == W3-calibrated;  >1 == worse.

Usage:  python sweep_noise.py --episodes 12 --max-steps 15000
"""
import os, sys, argparse, time
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
TAKEOFF_ALT = 2.0
# W3-calibrated point targets (scale=1.0). scale interpolates each from its clean value.
W3 = dict(bearing=0.018, range=0.19, dropout=0.05, fov=0.785, maxr=28.0, latency=2)


def error_model_at(scale):
    """Interpolate the detector error model from clean (s=0) toward W3 (s=1), extrapolate past 1."""
    return {
        "bearing_sigma_rad": scale * W3["bearing"],
        "range_sigma_frac":  scale * W3["range"],
        "dropout_prob":      scale * W3["dropout"],
        # FoV opens fully at s=0 (pi) and closes toward the W3 cone; range limit huge at s=0.
        "fov_halfangle_rad": np.pi - min(scale, 1.0) * (np.pi - W3["fov"]),
        "max_range_m":       1e9 - min(scale, 1.0) * (1e9 - W3["maxr"]),
        "latency_steps":     int(round(scale * W3["latency"])),
        "next_gate_extra_dropout": 0.5,
    }


def run_scale(teacher, scale, episodes, max_steps, seed):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    w = env._obs_wrapper                          # the internal PerceptionObsWrapper
    w.error_model.update(error_model_at(scale))
    w.randomize = False                            # use our point values, not sampled ranges
    base = env._base_env
    gates, took = [], 0
    for ep in range(episodes):
        obs, _ = env.reset(); done = False; L = 0; max_h = -1e9; g = 0
        while not done and L < max_steps:
            act, _ = teacher.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act)
            L += 1; max_h = max(max_h, float(base.state[2]))
            g = max(g, int(info.get("gates_passed", 0)))
            done = term or trunc
        gates.append(g); took += (max_h >= TAKEOFF_ALT)
    env.close()
    a = np.array(gates)
    return dict(scale=scale, mean=float(a.mean()), median=float(np.median(a)),
                mx=int(a.max()), ge1=float((a >= 1).mean() * 100),
                takeoff=took, eps=episodes)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=15000)
    ap.add_argument("--scales", default="0.0,0.25,0.5,1.0,1.5")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    scales = [float(s) for s in args.scales.split(",")]
    teacher = PPO.load(TEACHER, device="cpu")
    print(f"Anakin perception-noise sweep  (n={args.episodes}/scale, max_steps={args.max_steps})")
    print(f"  scale 0.0 = privileged-clean | 1.0 = W3-calibrated detector | >1 = worse\n")
    print(f"  {'scale':>6} {'gates/ep':>9} {'median':>7} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    rows = []
    t0 = time.time()
    for s in scales:
        r = run_scale(teacher, s, args.episodes, args.max_steps, args.seed)
        rows.append(r)
        print(f"  {r['scale']:>6.2f} {r['mean']:>9.2f} {r['median']:>7.0f} {r['mx']:>4d} "
              f"{r['ge1']:>6.0f} {r['takeoff']:>4d}/{r['eps']:<3d}")
    print(f"\n  swept {len(scales)} levels in {(time.time()-t0)/60:.1f} min")
    # crude cliff read
    clean = rows[0]['mean']
    for r in rows:
        if clean > 0 and r['mean'] < 0.5 * clean:
            print(f"  --> performance halves by scale ~{r['scale']:.2f} "
                  f"({r['mean']:.2f} vs clean {clean:.2f})")
            break


if __name__ == "__main__":
    main()
