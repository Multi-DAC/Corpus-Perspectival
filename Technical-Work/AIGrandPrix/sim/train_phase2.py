"""
train_phase2.py — Anakin Phase 2: extended retrain from a healthy v3 checkpoint.

Continues training from v3 7.5M (or any specified checkpoint) under F1+F2+F3
with V2 curriculum unchanged. Designed for the Day-83 ROADMAP Phase 2 launch
(post-Reading-A-falsification). Differences from train_infinite_v3.py:

  1. RESUME from a checkpoint (loads policy + VecNormalize stats; preserves
     num_timesteps so checkpoint filenames continue from where v3 left off).
  2. CPU device by default. Pre-launch benchmark (2026-04-24, WSL Ubuntu, 16
     envs DummyVecEnv): CPU ~2400 sps vs CUDA ~1900 sps. SB3 explicitly warns
     about this case — for MLP policies the GPU dispatch overhead exceeds
     compute benefit. RTX 5080 is reserved for vision-pipeline work where the
     CNN forward pass actually pays for the GPU trip. Override with --device
     cuda only if you've benchmarked the specific config.
  3. CheckpointWithVecNormalize callback saves vec_normalize.pkl at every
     checkpoint — fixes the bug that contaminated Phase 1 eval (vec stats
     only saved at training end; if killed mid-run, lost forever).
  4. lr=3e-4 throughout (policy at 100% crash is not fine-tuning territory).

Curriculum settings unchanged from V2 (asymmetric EMA, soft boundaries,
per-maneuver filtering, gate_speed_scale=0.08). Domain randomization 15%.

Usage:
    python train_phase2.py \\
        --resume-policy ".../ppo_v3_7500000_steps.zip" \\
        --resume-vecnorm ".../vec_normalize_reconstructed.pkl" \\
        --total-steps 60000000 \\
        --n-envs 16 \\
        --tag phase2_60M
"""

import os
import sys
import time
import argparse
import json
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(__file__))

from infinite_gate_env import InfiniteGateEnv  # noqa: E402
from stable_baselines3 import PPO  # noqa: E402
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize  # noqa: E402
from stable_baselines3.common.monitor import Monitor  # noqa: E402
from stable_baselines3.common.callbacks import BaseCallback  # noqa: E402

# Re-import the v3 callbacks rather than redefining them
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from train_infinite_v3 import LogStdClampCallback, GradNormLoggerCallback  # noqa: E402


class CheckpointWithVecNormalize(BaseCallback):
    """Saves both PPO policy and VecNormalize stats at every checkpoint.

    Fix for the bug that contaminated Phase 1 eval: stable_baselines3's stock
    CheckpointCallback saves only the policy zip, so VecNormalize stats are
    lost if the run is killed before training-end's manual env.save() runs.

    Per-checkpoint stats also let us evaluate any checkpoint accurately, not
    just the final one.
    """
    def __init__(self, save_freq: int, save_path: str, name_prefix: str,
                 vec_env, verbose: int = 0):
        super().__init__(verbose)
        self.save_freq = save_freq
        self.save_path = Path(save_path)
        self.name_prefix = name_prefix
        self.vec_env = vec_env
        self.save_path.mkdir(parents=True, exist_ok=True)
        self._last_save = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_save < self.save_freq:
            return True
        self._last_save = self.num_timesteps
        ckpt_name = f'{self.name_prefix}_{self.num_timesteps}_steps'
        self.model.save(str(self.save_path / ckpt_name))
        self.vec_env.save(str(self.save_path / f'{ckpt_name}_vecnorm.pkl'))
        if self.verbose:
            print(f'    [ckpt] saved {ckpt_name} + vecnorm at step '
                  f'{self.num_timesteps:,}')
        return True


class PerManeuverMasteryLogger(BaseCallback):
    """Periodically writes per-maneuver mastery EMA from each env's curriculum.

    InfiniteGateEnv's curriculum tracks per-maneuver mastery internally; this
    logger pulls those readings from each parallel env and aggregates them so
    we can see which maneuvers are strengthening / weakening as training goes.
    """
    def __init__(self, log_path: str, log_freq: int = 100_000, verbose: int = 0):
        super().__init__(verbose)
        self.log_path = str(log_path)
        self.log_freq = log_freq
        self.history = []
        self._last_log = 0

    def _on_step(self) -> bool:
        if self.num_timesteps - self._last_log < self.log_freq:
            return True
        self._last_log = self.num_timesteps

        # Pull per-maneuver mastery from each underlying env via vec_env.env_method
        try:
            envs_unwrapped = self.training_env.venv.envs  # VecNormalize -> DummyVecEnv -> [Monitor(InfiniteGateEnv)]
        except AttributeError:
            envs_unwrapped = self.training_env.envs

        per_env_raw = []
        per_env_ema_scalar = []
        for monitor in envs_unwrapped:
            inner = monitor.env if hasattr(monitor, 'env') else monitor
            try:
                rates = inner._get_per_maneuver_masteries()
            except AttributeError:
                rates = {}
            per_env_raw.append(dict(rates))
            ema_scalar = getattr(inner, '_ema_mastery', None)
            if ema_scalar is not None:
                per_env_ema_scalar.append(float(ema_scalar))

        all_maneuvers = set()
        for e in per_env_raw:
            all_maneuvers.update(e.keys())
        agg_raw = {}
        for m in all_maneuvers:
            vals = [e.get(m) for e in per_env_raw if e.get(m) is not None]
            if vals:
                agg_raw[m] = float(np.mean(vals))

        entry = {
            'step': int(self.num_timesteps),
            'ema_overall': float(np.mean(per_env_ema_scalar)) if per_env_ema_scalar else None,
            'raw': agg_raw,
        }
        self.history.append(entry)
        with open(self.log_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        return True


def make_infinite_env(seed: int, ground_start_prob: float = 0.0):
    def _init():
        env = InfiniteGateEnv(
            gate_radius=0.75,
            max_steps=30000,
            dt=0.002,
            substeps=1,
            domain_rand=True,
            domain_rand_scale=0.15,
            adaptive_curriculum=True,
            ground_start_prob=ground_start_prob,
            seed=seed,
        )
        return Monitor(env)
    return _init


def train(args):
    out_dir = Path(__file__).parent / 'runs' / f'infinite_v3_{args.tag}_{int(time.time())}'
    out_dir.mkdir(parents=True, exist_ok=True)

    print('=' * 72)
    print(f'Anakin Phase 2 — extended retrain from healthy v3 ({args.tag})')
    print('=' * 72)
    print(f'  Output:       {out_dir}')
    print(f'  Resume from:  {args.resume_policy}')
    print(f'  Resume vec:   {args.resume_vecnorm}')
    print(f'  Total steps:  {args.total_steps:,}  (continues, not from zero)')
    print(f'  Parallel envs: {args.n_envs}')
    print(f'  Device:       {args.device}')
    print(f'  Save every:   {args.save_every:,}')
    print(f'  Mastery log:  every {args.mastery_log_freq:,} steps')

    # Build env stack
    raw_envs = DummyVecEnv([
        make_infinite_env(seed=i * 42 + args.base_seed,
                          ground_start_prob=args.ground_start_prob)
        for i in range(args.n_envs)
    ])

    # Load VecNormalize from resume path — preserves running mean/var
    train_envs = VecNormalize.load(args.resume_vecnorm, raw_envs)
    train_envs.training = True
    train_envs.norm_reward = True

    # Load PPO model with custom env (must rebind because n_envs may differ from saved)
    model = PPO.load(
        args.resume_policy,
        env=train_envs,
        device=args.device,
        # Override learning rate explicitly — saved schedule may be wrong
        custom_objects={'learning_rate': 3e-4, 'lr_schedule': lambda _: 3e-4},
    )
    print(f'  Model loaded — params: '
          f'{sum(p.numel() for p in model.policy.parameters()):,}')
    print(f'  Resumed at step: {model.num_timesteps:,}')

    # Callbacks
    ckpt_cb = CheckpointWithVecNormalize(
        save_freq=args.save_every,
        save_path=str(out_dir / 'checkpoints'),
        name_prefix='ppo_phase2',
        vec_env=train_envs,
        verbose=1,
    )
    logstd_cb = LogStdClampCallback(min_std=0.1, max_std=1.0, verbose=0)
    grad_cb = GradNormLoggerCallback(
        log_path=out_dir / 'grad_norms.json',
        log_freq=args.grad_log_freq,
    )
    mastery_cb = PerManeuverMasteryLogger(
        log_path=out_dir / 'mastery.json',
        log_freq=args.mastery_log_freq,
    )

    t0 = time.time()
    model.learn(
        total_timesteps=args.total_steps,
        callback=[ckpt_cb, logstd_cb, grad_cb, mastery_cb],
        reset_num_timesteps=False,  # CRITICAL: continue from resume_policy's step count
        tb_log_name='ppo_phase2',
        progress_bar=False,
    )
    dt = time.time() - t0

    # Final save (also saved per checkpoint, but belt-and-suspenders)
    model.save(str(out_dir / 'final_model'))
    train_envs.save(str(out_dir / 'vec_normalize.pkl'))

    print(f'\nTraining done: {args.total_steps:,} steps in {dt/60:.1f} min '
          f'({args.total_steps/dt:.0f} steps/sec)')
    print(f'Final num_timesteps: {model.num_timesteps:,}')
    print(f'log_std clamp fires: {logstd_cb.n_clamps}')
    print(f'Final log_std: {model.policy.log_std.detach().tolist()}')
    print(f'Saved: {out_dir}')


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--resume-policy', required=True,
                   help='Path to PPO checkpoint .zip to resume from')
    p.add_argument('--resume-vecnorm', required=True,
                   help='Path to vec_normalize.pkl matching the checkpoint')
    p.add_argument('--total-steps', type=int, default=60_000_000,
                   help='Additional steps to train (continues, not from zero)')
    p.add_argument('--n-envs', type=int, default=16)
    p.add_argument('--base-seed', type=int, default=17)
    p.add_argument('--tag', type=str, default='phase2')
    p.add_argument('--device', type=str, default='cpu')
    p.add_argument('--save-every', type=int, default=2_500_000,
                   help='Save (policy + vecnorm) every N env steps')
    p.add_argument('--ground-start-prob', type=float, default=0.0,
                   help='Fraction of episodes starting at ground rest (TAKEOFF curriculum)')
    p.add_argument('--grad-log-freq', type=int, default=100_000)
    p.add_argument('--mastery-log-freq', type=int, default=100_000)
    args = p.parse_args()
    train(args)


if __name__ == '__main__':
    main()
