"""
diag_camera_axis.py — Is the detection cliff a CAMERA-AXIS artifact?

drone_env_v2 line 128: thrust is along body-z, so body-z is the UP/thrust axis. But the perception
FoV cone (perception_obs.py) is built around forward_world = quat_rotate(q, [0,0,1]) = body-z = UP.
So the virtual camera points up the thrust axis, not forward like a real FPV cam (which looks forward
+ ~20 deg up-tilt, per VADR / adapter.py _cam_to_body_with_tilt).

This flies frozen Anakin on its ideal privileged line and measures current-gate visibility (90 deg
cone, 28 m) under SEVERAL candidate body-fixed camera axes. The axis that actually sees the gates is
the correct camera model — and tells us whether fixing the camera geometry alone unblocks perception.
"""
import os, sys, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from drone_env_v2 import quat_rotate_np
from stable_baselines3 import PPO

TEACHER = os.path.join(HERE, "runs", "infinite_1771556763", "checkpoints",
                       "ppo_infinite_80000000_steps.zip")
FOV_HALF = 0.785
MAX_RANGE = 28.0
c20, s20 = np.cos(np.radians(20)), np.sin(np.radians(20))

# Candidate body-frame camera look-axes (unit vectors).
AXES = {
    "z_up (current)": np.array([0, 0, 1.0]),
    "x_fwd":          np.array([1.0, 0, 0]),
    "y_fwd":          np.array([0, 1.0, 0]),
    "neg_x_fwd":      np.array([-1.0, 0, 0]),
    "neg_y_fwd":      np.array([0, -1.0, 0]),
    "x_tilt20up":     np.array([c20, 0, s20]),
    "y_tilt20up":     np.array([0, c20, s20]),
    "neg_x_tilt20":   np.array([-c20, 0, s20]),
    "neg_y_tilt20":   np.array([0, -c20, s20]),
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=6)
    ap.add_argument("--max-steps", type=int, default=12000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    teacher = PPO.load(TEACHER, device="cpu")
    env = InfiniteGateEnv(perception_obs=False, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=args.seed)
    base = env._base_env

    vis = {k: 0 for k in AXES}          # steps current gate in-cone
    seen_gate = {k: set() for k in AXES}  # which (episode,gate) seen at least once
    total = 0
    gates_resolved = 0
    # also: alignment of body-z and body-x with velocity, to identify "forward"
    align_z, align_x, align_y, nvel = 0.0, 0.0, 0.0, 0

    for ep in range(args.episodes):
        obs, _ = env.reset(); done = False; L = 0
        prev_gate = base.current_gate
        while not done and L < args.max_steps:
            pos, q, vel = base.state[0:3], base.state[6:10], base.state[3:6]
            cur = base.current_gate
            if cur != prev_gate:
                gates_resolved += 1; prev_gate = cur
            if cur < base.n_gates:
                rel = np.array(base.gates[cur], dtype=float) - pos
                d = float(np.linalg.norm(rel))
                total += 1
                if 1e-6 < d <= MAX_RANGE:
                    rel_u = rel / d
                    for name, ax_b in AXES.items():
                        ax_w = quat_rotate_np(q, ax_b); ax_w /= (np.linalg.norm(ax_w) + 1e-9)
                        if float(np.dot(ax_w, rel_u)) >= np.cos(FOV_HALF):
                            vis[name] += 1
                            seen_gate[name].add((ep, cur))
            sp = np.linalg.norm(vel)
            if sp > 0.5:
                vu = vel / sp
                align_z += abs(float(np.dot(quat_rotate_np(q, [0, 0, 1.0]), vu)))
                align_x += abs(float(np.dot(quat_rotate_np(q, [1.0, 0, 0]), vu)))
                align_y += abs(float(np.dot(quat_rotate_np(q, [0, 1.0, 0]), vu)))
                nvel += 1
            act, _ = teacher.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act); L += 1
            done = term or trunc
    env.close()

    print(f"Camera-axis visibility test — frozen Anakin, ideal line "
          f"(n={args.episodes}, FoV 90deg, range {MAX_RANGE:.0f}m)\n")
    print(f"  body-axis | velocity alignment (1=aligned w/ flight dir):")
    print(f"    body-z {align_z/max(nvel,1):.2f}   body-x {align_x/max(nvel,1):.2f}   "
          f"body-y {align_y/max(nvel,1):.2f}   (higher => that axis is 'forward')\n")
    print(f"  {'camera axis':>16} {'in-frame %':>11} {'gates seen >=1x':>16}")
    ng = gates_resolved if gates_resolved else 1
    for name in AXES:
        print(f"  {name:>16} {vis[name]/max(total,1)*100:>10.1f}% "
              f"{len(seen_gate[name]):>6d} ({len(seen_gate[name])/ng*100:>3.0f}% of {ng})")
    print(f"\n  total steps {total:,}, gates resolved {gates_resolved}")
    print(f"  -> the high-visibility axis is the correct FPV camera model.")


if __name__ == "__main__":
    main()
