#
# Takeoff eval: does the retrained policy actually lift off the pad and navigate?
# Forces ground_start_prob=1.0 (every episode starts at ground rest) and reports
# takeoff success + gates passed. Reads a saved checkpoint — does NOT touch the live run.
#
import os, sys, argparse
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
SIM  = os.path.join(HERE, "..", "..", "sim")
sys.path.insert(0, SIM)
sys.path.insert(0, os.path.join(HERE, "..", "..", "rl"))
from infinite_gate_env import InfiniteGateEnv
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize

CKPT = os.path.join(SIM, "runs", "infinite_v3_takeoff_twr385_1780305737", "checkpoints")
TAKEOFF_ALT = 1.0  # m above start; clearing this from z=0.2 = a real liftoff


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--step", type=int, default=75000032)
    ap.add_argument("--episodes", type=int, default=20)
    args = ap.parse_args()

    zip_path = os.path.join(CKPT, f"ppo_phase2_{args.step}_steps.zip")
    pkl_path = os.path.join(CKPT, f"ppo_phase2_{args.step}_steps_vecnorm.pkl")
    print(f"checkpoint: {os.path.basename(zip_path)}")

    raw = DummyVecEnv([lambda: InfiniteGateEnv(ground_start_prob=1.0, seed=999)])
    venv = VecNormalize.load(pkl_path, raw)
    venv.training = False
    venv.norm_reward = False
    model = PPO.load(zip_path, device="cpu")

    base = venv.venv.envs[0]  # Monitor? no — DummyVecEnv -> InfiniteGateEnv directly
    inner = base.unwrapped if hasattr(base, "unwrapped") else base

    took_off, gates_list, maxz_list, crashes = 0, [], [], {}
    for ep in range(args.episodes):
        obs = venv.reset()
        z0 = float(inner._base_env.state[2])
        max_z = z0
        gates = 0
        crash = None
        for _ in range(8000):
            act, _ = model.predict(obs, deterministic=True)
            obs, _, done, infos = venv.step(act)
            z = float(inner._base_env.state[2])
            max_z = max(max_z, z)
            info = infos[0]
            gates = inner.episode_gates
            if done[0]:
                crash = info.get("crash", "done")
                break
        climbed = max_z - z0
        if climbed >= TAKEOFF_ALT:
            took_off += 1
        gates_list.append(gates)
        maxz_list.append(max_z)
        crashes[crash] = crashes.get(crash, 0) + 1

    n = args.episodes
    print(f"\n=== TAKEOFF EVAL (ground start x{n}, step {args.step:,}) ===")
    print(f"  takeoff success (climbed >= {TAKEOFF_ALT}m): {took_off}/{n} = {took_off/n*100:.0f}%")
    print(f"  mean gates passed: {np.mean(gates_list):.2f}  (max {max(gates_list)})")
    print(f"  mean max altitude: {np.mean(maxz_list):.2f} m")
    print(f"  episode endings: {crashes}")


if __name__ == "__main__":
    main()
