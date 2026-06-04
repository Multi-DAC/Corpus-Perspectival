"""
distill_collect.py — Dual-view distillation data collection (Anakin teacher -> vision student).

Runs the 80M privileged teacher RAW (perception_obs=False, NO VecNormalize — that run never
used it) in InfiniteGateEnv, and at each sim step records TWO views of the SAME physics state:
  • privileged  (ImprovedObsWrapper)   -> the teacher decides from this
  • perception  (PerceptionObsWrapper) -> the student will learn to act from this

Because both observation builders are pure functions of the unwrapped base env state
(env.state + gate attrs), a single env stepped by the teacher gives perfectly aligned
(perception_obs, teacher_action) pairs with no lockstep-seeding fragility. We point a
standalone PerceptionObsWrapper at the SAME base env and call .observation() once per step
(keeping its latency buffers in sync with the sim rate).

Output: an .npz with obs (N,30) float32, act (N,4) float32, plus episode boundaries + meta.

Usage:
    python distill_collect.py --episodes 3 --out runs/distill/smoke.npz        # smoke test
    python distill_collect.py --pairs 500000 --out runs/distill/dataset.npz     # full collect
"""
import os, sys, time, argparse
import numpy as np
from pathlib import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "rl"))

from infinite_gate_env import InfiniteGateEnv
from perception_obs import PerceptionObsWrapper
from stable_baselines3 import PPO

TEACHER_DEFAULT = os.path.join(
    HERE, "runs", "infinite_1771556763", "checkpoints", "ppo_infinite_80000000_steps.zip"
)
TAKEOFF_ALT = 2.0


def _reset_perception(perc):
    """Re-init the perception view's internal state WITHOUT driving the env reset
    (the teacher env owns the env lifecycle; the perception wrapper only observes)."""
    perc._reset_perception_state()
    perc._sample_episode_params()
    perc.last_gate_idx = 0
    perc.last_gate_time = 0.0


def collect(args):
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    print(f"teacher: {os.path.relpath(args.ckpt, HERE)}")
    teacher = PPO.load(args.ckpt, device="cpu")

    # Privileged env — exactly the obs/dynamics the 80M teacher was trained on. RAW, no VecNormalize.
    env = InfiniteGateEnv(
        perception_obs=False,
        ground_start_prob=args.ground_prob,
        domain_rand=True,
        adaptive_curriculum=True,
        seed=args.seed,
    )
    base = env._base_env

    # Perception view over the SAME base env (reads the same state, applies detector noise).
    perc = PerceptionObsWrapper(env._ctbr, randomize=True, seed=args.seed + 1)

    obs_buf, act_buf = [], []
    ep_lengths, ep_gates = [], []
    took = 0
    n_pairs_target = args.pairs
    n_eps_target = args.episodes

    priv_obs, _ = env.reset()
    _reset_perception(perc)
    L = 0
    max_h = -1e9
    t0 = time.time()
    ep = 0

    while True:
        # Both views at the SAME pre-step state.
        perc_obs = perc.observation(None)              # student input (noisy)
        action, _ = teacher.predict(priv_obs, deterministic=True)  # teacher from privileged

        obs_buf.append(np.asarray(perc_obs, dtype=np.float32))
        act_buf.append(np.asarray(action, dtype=np.float32))

        priv_obs, _r, term, trunc, info = env.step(action)
        L += 1
        max_h = max(max_h, float(base.state[2]))

        done = term or trunc or L >= args.max_steps
        if done:
            g = int(info.get("gates_passed", 0))
            ep_lengths.append(L); ep_gates.append(g)
            took += (max_h >= TAKEOFF_ALT)
            ep += 1
            if ep % 5 == 0 or ep <= 3:
                print(f"  ep {ep:4d}: gates={g:3d} len={L:5d} pairs={len(obs_buf):,}")
            # stop conditions
            if n_pairs_target and len(obs_buf) >= n_pairs_target:
                break
            if n_eps_target and ep >= n_eps_target:
                break
            priv_obs, _ = env.reset()
            _reset_perception(perc)
            L = 0; max_h = -1e9

    obs_arr = np.stack(obs_buf)
    act_arr = np.stack(act_buf)
    ep_g = np.array(ep_gates)
    dt = time.time() - t0

    np.savez_compressed(
        out,
        obs=obs_arr, act=act_arr,
        ep_lengths=np.array(ep_lengths), ep_gates=ep_g,
        meta=np.array([args.ckpt, str(args.ground_prob), str(args.seed)], dtype=object),
    )

    print("\n=== collection summary ===")
    print(f"  pairs collected : {len(obs_arr):,}  (obs {obs_arr.shape}, act {act_arr.shape})")
    print(f"  episodes        : {ep}")
    print(f"  gates/episode   : mean {ep_g.mean():.2f}  median {np.median(ep_g):.0f}  "
          f"max {ep_g.max()}  (>=1: {(ep_g>=1).mean()*100:.0f}%)")
    print(f"  takeoff%        : {took}/{ep} = {took/max(ep,1)*100:.0f}%")
    print(f"  obs range       : [{obs_arr.min():.2f}, {obs_arr.max():.2f}]  "
          f"act range [{act_arr.min():.2f}, {act_arr.max():.2f}]")
    print(f"  wall            : {dt/60:.1f} min ({len(obs_arr)/max(dt,1e-9):.0f} pairs/s)")
    print(f"  saved           : {os.path.relpath(out, HERE)}")
    env.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=TEACHER_DEFAULT)
    ap.add_argument("--out", default=os.path.join("runs", "distill", "dataset.npz"))
    ap.add_argument("--episodes", type=int, default=0, help="stop after N episodes (0 = ignore)")
    ap.add_argument("--pairs", type=int, default=0, help="stop after N (obs,act) pairs (0 = ignore)")
    ap.add_argument("--ground-prob", dest="ground_prob", type=float, default=0.5)
    ap.add_argument("--max-steps", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    if not args.episodes and not args.pairs:
        args.episodes = 3  # default to a smoke test rather than running forever
    collect(args)
