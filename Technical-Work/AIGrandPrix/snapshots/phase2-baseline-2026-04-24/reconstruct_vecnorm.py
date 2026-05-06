"""
reconstruct_vecnorm.py — Recover VecNormalize obs/reward statistics for the
v3 7.5M retrain checkpoint, which was killed before train_envs.save() ran.

Method: load the policy, wrap a fresh InfiniteGateEnv stack in VecNormalize
with training=True, roll the policy for N steps to populate the running
mean/variance, save the reconstructed pkl.

Approximation caveat: the gamma-discounted reward running mean cannot be
recovered exactly from a short rollout (it depends on full training-time
trajectory), but obs normalization (the part the policy depends on at eval
time) converges within a few tens of thousands of steps and is what we need
for proper eval.

Usage:
    python reconstruct_vecnorm.py --policy <ckpt.zip> --out <vec_normalize.pkl>
                                    --n-envs 8 --steps 100000
"""

import os
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402
from stable_baselines3.common.monitor import Monitor  # noqa: E402


def make_env(seed):
    def _init():
        env = InfiniteGateEnv(
            gate_radius=0.75,
            max_steps=30000,
            dt=0.002,
            substeps=1,
            domain_rand=True,
            domain_rand_scale=0.15,
            adaptive_curriculum=True,
            seed=seed,
        )
        return Monitor(env)
    return _init


def reconstruct(policy_path: str, out_path: str, n_envs: int, total_steps: int,
                base_seed: int = 17):
    print('=' * 72)
    print('VecNormalize reconstruction')
    print('=' * 72)
    print(f'  Policy:      {policy_path}')
    print(f'  Output:      {out_path}')
    print(f'  Parallel envs: {n_envs}')
    print(f'  Target steps:  {total_steps:,}')

    raw = DummyVecEnv([make_env(base_seed + i * 42) for i in range(n_envs)])
    env = VecNormalize(
        raw,
        norm_obs=True,
        norm_reward=True,
        clip_obs=10.0,
        clip_reward=10.0,
        gamma=0.999,
        training=True,
    )

    model = PPO.load(policy_path, device='cpu')
    print(f'  Model loaded — params: '
          f'{sum(p.numel() for p in model.policy.parameters()):,}')

    obs = env.reset()
    t0 = time.time()
    steps_done = 0
    while steps_done < total_steps:
        act, _ = model.predict(obs, deterministic=False)  # stochastic — explore obs space
        obs, rew, done, info = env.step(act)
        steps_done += n_envs
        if steps_done % (n_envs * 1000) == 0 or steps_done >= total_steps:
            elapsed = time.time() - t0
            sps = steps_done / elapsed if elapsed > 0 else 0
            obs_mean_norm = float(((env.obs_rms.mean) ** 2).sum() ** 0.5)
            obs_var_mean = float(env.obs_rms.var.mean())
            print(f'  step {steps_done:>8,} / {total_steps:,}  '
                  f'({sps:.0f} sps)  '
                  f'obs_mean|={obs_mean_norm:.3f}  obs_var_mean={obs_var_mean:.3f}')

    elapsed = time.time() - t0
    env.save(out_path)
    print(f'\nDone in {elapsed/60:.1f} min ({steps_done/elapsed:.0f} steps/sec)')
    print(f'Saved: {out_path}')
    print(f'  obs_rms.mean.shape: {env.obs_rms.mean.shape}')
    print(f'  obs_rms.var.shape:  {env.obs_rms.var.shape}')
    print(f'  ret_rms.mean: {float(env.ret_rms.mean):.3f}')
    print(f'  ret_rms.var:  {float(env.ret_rms.var):.3f}')
    env.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--policy', required=True,
                   help='Path to PPO checkpoint .zip')
    p.add_argument('--out', required=True,
                   help='Output path for vec_normalize.pkl')
    p.add_argument('--n-envs', type=int, default=8)
    p.add_argument('--steps', type=int, default=100_000)
    p.add_argument('--base-seed', type=int, default=17)
    args = p.parse_args()
    reconstruct(args.policy, args.out, args.n_envs, args.steps, args.base_seed)


if __name__ == '__main__':
    main()
