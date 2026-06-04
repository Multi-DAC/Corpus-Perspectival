"""
sweep_channels.py — Which perception CHANNEL causes the cliff?

sweep_noise.py found Anakin holds ~80% of clean up to 0.5x W3 noise, then collapses to 0 at
full W3. This isolates the cause: corrupt ONE channel to its full W3 value (others kept clean)
and measure gates/ep. The channel that tanks performance alone is the binding constraint —
and that decides where perception effort goes (range/PnP -> sim-frame detector improvements;
detection/dropout -> UE5-style faint/occluded-gate curriculum).
"""
import os, sys, argparse, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
TAKEOFF_ALT = 2.0
CLEAN = dict(bearing_sigma_rad=0.0, range_sigma_frac=0.0, dropout_prob=0.0,
             fov_halfangle_rad=np.pi, max_range_m=1e9, latency_steps=0,
             next_gate_extra_dropout=0.5)
# Each channel set to its full W3 value (others stay clean).
CHANNELS = {
    "clean":     {},
    "range":     dict(range_sigma_frac=0.19),
    "bearing":   dict(bearing_sigma_rad=0.018),
    "dropout":   dict(dropout_prob=0.05),
    "detection": dict(fov_halfangle_rad=0.785, max_range_m=28.0),
    "latency":   dict(latency_steps=2),
    "all_W3":    dict(range_sigma_frac=0.19, bearing_sigma_rad=0.018, dropout_prob=0.05,
                      fov_halfangle_rad=0.785, max_range_m=28.0, latency_steps=2),
    # 2x stress on the two suspected weak axes
    "range_2x":  dict(range_sigma_frac=0.38),
    "dropout_2x":dict(dropout_prob=0.10),
}


def run(teacher, overrides, episodes, max_steps, seed):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    w = env._obs_wrapper
    em = dict(CLEAN); em.update(overrides)
    w.error_model.update(em); w.randomize = False
    base = env._base_env
    gates, took = [], 0
    for _ in range(episodes):
        obs, _ = env.reset(); done = False; L = 0; mh = -1e9; g = 0
        while not done and L < max_steps:
            act, _ = teacher.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act)
            L += 1; mh = max(mh, float(base.state[2])); g = max(g, int(info.get("gates_passed", 0)))
            done = term or trunc
        gates.append(g); took += (mh >= TAKEOFF_ALT)
    env.close()
    a = np.array(gates)
    return float(a.mean()), int(a.max()), float((a >= 1).mean()*100), took


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=15000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    teacher = PPO.load(TEACHER, device="cpu")
    print(f"Per-channel cliff isolation (n={args.episodes}, max_steps={args.max_steps})")
    print(f"  each row = ONE channel at full W3, others clean\n")
    print(f"  {'channel':>11} {'gates/ep':>9} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    t0 = time.time()
    for name, ov in CHANNELS.items():
        m, mx, ge1, took = run(teacher, ov, args.episodes, args.max_steps, args.seed)
        print(f"  {name:>11} {m:>9.2f} {mx:>4d} {ge1:>6.0f} {took:>4d}/{args.episodes:<3d}")
    print(f"\n  done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
