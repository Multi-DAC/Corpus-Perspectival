"""
nose_axis_test.py — honesty check: deploy mounts the camera on the NOSE (+x, adapter convention).
Anakin CRABS (flies -x/+y). So how does frozen Anakin do with the REALISTIC +x nose camera vs the
-x camera I happened to test? If +x is near-zero, the retrain must flip Anakin's flight orientation
(fly nose-forward), not just polish.
"""
import os, sys, time
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from perception_deadreckon import DeadReckonPerceptionObsWrapper
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
TAKEOFF = 2.0
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))
ALL_W3 = dict(range_sigma_frac=0.19, bearing_sigma_rad=0.018, dropout_prob=0.05,
              fov_halfangle_rad=0.785, max_range_m=28.0, latency_steps=2, next_gate_extra_dropout=0.5)
ROWS = [
    ("+x_fwd  / reckon (deploy nose)", [1.0, 0, 0]),
    ("+x+tilt / reckon (deploy nose)", [c20, 0, s20]),
    ("-x+tilt / reckon (where it flies)", [-c20, 0, s20]),
]


def run(teacher, cam, episodes=12, max_steps=15000, seed=2026):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    env._obs_wrapper = DeadReckonPerceptionObsWrapper(
        env._ctbr, cam_axis_body=cam, deadreckon=True, randomize=False, seed=seed + 5)
    env.observation_space = env._obs_wrapper.observation_space
    env._obs_wrapper.error_model.update(ALL_W3); env._obs_wrapper.randomize = False
    base = env._base_env
    gates, took = [], 0
    for _ in range(episodes):
        obs, _ = env.reset(); done = False; L = 0; mh = -1e9; g = 0
        while not done and L < max_steps:
            act, _ = teacher.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act)
            L += 1; mh = max(mh, float(base.state[2])); g = max(g, int(info.get("gates_passed", 0)))
            done = term or trunc
        gates.append(g); took += (mh >= TAKEOFF)
    env.close()
    a = np.array(gates)
    return a.mean(), int(a.max()), (a >= 1).mean()*100, took, episodes


def main():
    teacher = PPO.load(TEACHER, device="cpu")
    print("Nose-axis honesty check (frozen Anakin, all-W3 detector, dead-reckon)\n")
    print(f"  {'camera mount':>34} {'gates/ep':>9} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    t0 = time.time()
    for label, cam in ROWS:
        m, mx, ge1, took, ep = run(teacher, cam)
        print(f"  {label:>34} {m:>9.2f} {mx:>4d} {ge1:>6.0f} {took:>4d}/{ep:<3d}")
    print(f"\n  done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
