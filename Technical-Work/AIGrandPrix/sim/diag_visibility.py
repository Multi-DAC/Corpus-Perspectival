"""
diag_visibility.py — Confirm the cliff is signal ACQUISITION (geometry), not persistence.

Fly frozen Anakin on its IDEAL privileged line (perception_obs=False -> ~10.9 gates) and, at every
step, measure whether the CURRENT gate would be in frame for the deploy camera (FoV cone + range
limit), purely geometrically (no stochastic dropout). If the current gate is out of frame a large
fraction of the time even on the ideal line, the racing line is not gaze-compatible and the fix is
FoV-aware flight, not a better estimator.

Reports: % steps current gate detectable; per-gate time-to-first-detectable (and 'never' rate).
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
FOV_HALF = 0.785     # 90 deg VFoV
MAX_RANGE = 28.0


def detectable(pos, q, gate):
    rel = gate - pos
    d = float(np.linalg.norm(rel))
    if d < 1e-6 or d > MAX_RANGE:
        return False, d
    fwd = quat_rotate_np(q, np.array([0.0, 0.0, 1.0]))
    fwd = fwd / (np.linalg.norm(fwd) + 1e-9)
    cos_ang = float(np.dot(fwd, rel / d))
    return (cos_ang >= np.cos(FOV_HALF)), d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--episodes", type=int, default=8)
    ap.add_argument("--max-steps", type=int, default=15000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    teacher = PPO.load(TEACHER, device="cpu")
    env = InfiniteGateEnv(perception_obs=False, ground_start_prob=0.5,
                          domain_rand=True, adaptive_curriculum=True, seed=args.seed)
    base = env._base_env

    steps_total = steps_vis = 0
    gate_seen_lag = []     # steps from a gate becoming current to first detectable
    gates_never = 0
    gates_counted = 0
    dist_when_first_seen = []

    for _ in range(args.episodes):
        obs, _ = env.reset(); done = False; L = 0
        cur = base.current_gate
        cur_start = 0
        first_seen_this_gate = None
        while not done and L < args.max_steps:
            pos, q = base.state[0:3], base.state[6:10]
            if base.current_gate != cur:
                # previous gate resolved -> record acquisition lag
                gates_counted += 1
                if first_seen_this_gate is None:
                    gates_never += 1
                else:
                    gate_seen_lag.append(first_seen_this_gate - cur_start)
                cur = base.current_gate; cur_start = L; first_seen_this_gate = None
            if base.current_gate < base.n_gates:
                vis, d = detectable(pos, q, np.array(base.gates[base.current_gate], dtype=float))
                steps_total += 1
                if vis:
                    steps_vis += 1
                    if first_seen_this_gate is None:
                        first_seen_this_gate = L
                        dist_when_first_seen.append(d)
            act, _ = teacher.predict(obs, deterministic=True)
            obs, _r, term, trunc, info = env.step(act); L += 1
            done = term or trunc
    env.close()

    print(f"Visibility diagnostic — frozen Anakin on the IDEAL privileged line "
          f"(n={args.episodes}, FoV 90deg, range {MAX_RANGE:.0f}m)\n")
    print(f"  current gate IN FRAME : {steps_vis/max(steps_total,1)*100:.1f}% of steps "
          f"({steps_vis:,}/{steps_total:,})")
    print(f"  gates resolved        : {gates_counted}")
    if gates_counted:
        print(f"  gates NEVER seen      : {gates_never}/{gates_counted} "
              f"= {gates_never/gates_counted*100:.0f}%  (cannot dead-reckon these)")
    if gate_seen_lag:
        gl = np.array(gate_seen_lag)
        print(f"  acquisition lag       : median {np.median(gl):.0f} steps "
              f"({np.median(gl)*base.dt*1000:.0f} ms)  mean {gl.mean():.0f}")
    if dist_when_first_seen:
        dd = np.array(dist_when_first_seen)
        print(f"  range at first sight  : median {np.median(dd):.1f}m  min {dd.min():.1f}m")
    print(f"\n  read: high in-frame% + low never-seen => persistence problem (dead-reckon should help)")
    print(f"        low in-frame%  + high never-seen => ACQUISITION problem (need FoV-aware flight)")


if __name__ == "__main__":
    main()
