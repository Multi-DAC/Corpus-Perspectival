"""
sweep_corrected_camera.py — Does fixing the camera axis (+ dead-reckon) let frozen Anakin fly?

The cliff was a camera-model artifact: the FoV cone was around body-z (thrust/UP axis), pointing at
the sky. diag_camera_axis.py showed a forward axis (~-body-x, optionally +20deg tilt) sees 96% of
gates vs 4%. This re-runs frozen Anakin under the realistic all-W3 detector but with the FoV cone
around a FORWARD camera axis, with hold-stale vs dead-reckon, to see if gates/ep recovers.

All rows: frozen Anakin, all_W3 gate noise, 90deg cone, 28m range.
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
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))
ALL_W3 = dict(range_sigma_frac=0.19, bearing_sigma_rad=0.018, dropout_prob=0.05,
              fov_halfangle_rad=0.785, max_range_m=28.0, latency_steps=2,
              next_gate_extra_dropout=0.5)
CLEAN = dict(bearing_sigma_rad=0.0, range_sigma_frac=0.0, dropout_prob=0.0,
             fov_halfangle_rad=np.pi, max_range_m=1e9, latency_steps=0, next_gate_extra_dropout=0.5)

# (label, cam_axis_body, deadreckon, error_model)
ROWS = [
    ("clean-ceiling (body-z)",    None,                 False, CLEAN),
    ("body-z  / hold  (W3)",      None,                 False, ALL_W3),
    ("body-z  / reckon(W3)",      None,                 True,  ALL_W3),
    ("-x+tilt / hold  (W3)",      [-c20, 0, s20],       False, ALL_W3),
    ("-x+tilt / reckon(W3)",      [-c20, 0, s20],       True,  ALL_W3),
    ("-x_fwd  / reckon(W3)",      [-1.0, 0, 0],         True,  ALL_W3),
    ("y_fwd   / reckon(W3)",      [0, 1.0, 0],          True,  ALL_W3),
]


def run(teacher, cam_axis, dr, em, episodes, max_steps, seed):
    env = InfiniteGateEnv(perception_obs=True, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=seed)
    env._obs_wrapper = DeadReckonPerceptionObsWrapper(
        env._ctbr, cam_axis_body=cam_axis, deadreckon=dr, randomize=False, seed=seed + 5)
    env.observation_space = env._obs_wrapper.observation_space
    w = env._obs_wrapper
    full = dict(CLEAN); full.update(em); w.error_model.update(full); w.randomize = False
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
    print(f"Corrected-camera recovery test (frozen Anakin, n={args.episodes}, all-W3 detector)\n")
    print(f"  {'config':>24} {'gates/ep':>9} {'max':>4} {'>=1%':>6} {'takeoff':>8}")
    t0 = time.time()
    for label, cam, dr, em in ROWS:
        m, mx, ge1, took = run(teacher, cam, dr, em, args.episodes, args.max_steps, args.seed)
        print(f"  {label:>24} {m:>9.2f} {mx:>4d} {ge1:>6.0f} {took:>4d}/{args.episodes:<3d}")
    print(f"\n  done in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    main()
