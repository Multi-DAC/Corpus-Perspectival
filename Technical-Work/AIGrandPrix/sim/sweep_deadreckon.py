"""
sweep_deadreckon.py — Does ego-motion dead-reckoning of out-of-frame gates recover Anakin?

The cliff is the DETECTION channel (FoV + range limit): the drone goes blind when the gate
leaves the cone. This compares the stock perception wrapper (holds the STALE last-known vector)
against DeadReckonPerceptionObsWrapper (propagates the lost gate by velocity*dt) under:
  - clean       (sanity: both should match ~4.75; dead-reckon branch never fires)
  - detection   (FoV 90deg + 28m range limit, else clean — the isolated cliff)
  - all_W3      (the realistic VQ1 detector: detection limits + range/bearing/dropout/latency)

Frozen Anakin throughout. Any recovery is attributable purely to persistence-through-blindness.
"""
import os, sys, argparse, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from perception_deadreckon import DeadReckonPerceptionObsWrapper
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
TAKEOFF_ALT = 2.0
CLEAN = dict(bearing_sigma_rad=0.0, range_sigma_frac=0.0, dropout_prob=0.0,
             fov_halfangle_rad=np.pi, max_range_m=1e9, latency_steps=0,
             next_gate_extra_dropout=0.5)
DETECTION = dict(fov_halfangle_rad=0.785, max_range_m=28.0)
ALL_W3 = dict(range_sigma_frac=0.19, bearing_sigma_rad=0.018, dropout_prob=0.05,
              fov_halfangle_rad=0.785, max_range_m=28.0, latency_steps=2)
CONFIGS = {"clean": {}, "detection": DETECTION, "all_W3": ALL_W3}


def make_env(deadreckon, seed):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    if deadreckon:
        env._obs_wrapper = DeadReckonPerceptionObsWrapper(env._ctbr, randomize=False, seed=seed + 5)
        env.observation_space = env._obs_wrapper.observation_space
    return env


def run(teacher, deadreckon, overrides, episodes, max_steps, seed):
    env = make_env(deadreckon, seed)
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
    return float(a.mean()), int(a.max()), float((a >= 1).mean() * 100), took


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=12)
    ap.add_argument("--max-steps", type=int, default=15000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    teacher = PPO.load(TEACHER, device="cpu")
    print(f"Dead-reckoning recovery test (n={args.episodes}, max_steps={args.max_steps})")
    print(f"  frozen Anakin; stock=hold-stale vs dead-reckon=propagate-by-ego-motion\n")
    print(f"  {'config':>10} {'wrapper':>11} {'gates/ep':>9} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    t0 = time.time()
    results = {}
    for cfg_name, ov in CONFIGS.items():
        for dr in (False, True):
            m, mx, ge1, took = run(teacher, dr, ov, args.episodes, args.max_steps, args.seed)
            tag = "dead-reckon" if dr else "stock"
            results[(cfg_name, dr)] = m
            print(f"  {cfg_name:>10} {tag:>11} {m:>9.2f} {mx:>4d} {ge1:>6.0f} {took:>4d}/{args.episodes:<3d}")
        print()
    print(f"  done in {(time.time()-t0)/60:.1f} min\n")
    # headline deltas
    for cfg in ("detection", "all_W3"):
        s, d = results[(cfg, False)], results[(cfg, True)]
        clean = results[("clean", False)]
        rec = (d - s) / max(clean - s, 1e-9) * 100 if clean > s else 0.0
        print(f"  {cfg:>10}: stock {s:.2f} -> dead-reckon {d:.2f}  "
              f"(recovers {rec:.0f}% of the gap to clean {clean:.2f})")


if __name__ == "__main__":
    main()
