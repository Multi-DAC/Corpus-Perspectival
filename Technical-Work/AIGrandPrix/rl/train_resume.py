"""
Anakin Training - Resume from checkpoint with stability fixes
- Linear LR decay (3e-4 -> 3e-5) prevents gradient explosion at high step counts
- Explicit max_grad_norm=1.0 (less aggressive than default 0.5)
- Resumes from best available checkpoint
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
from stable_baselines3.common.monitor import Monitor

import importlib.util
spec = importlib.util.spec_from_file_location("train_ppo_local",
    Path(__file__).parent / "train_ppo.py")
train_ppo_local = importlib.util.module_from_spec(spec)
spec.loader.exec_module(train_ppo_local)

make_env = train_ppo_local.make_env
RUNS_DIR = Path(__file__).parent / "runs"


def linear_schedule(initial_lr: float, final_lr: float = 3e-5):
    """Linear LR decay from initial to final over training."""
    def schedule(progress_remaining: float) -> float:
        return final_lr + (initial_lr - final_lr) * progress_remaining
    return schedule


class StabilityCallback(BaseCallback):
    """
    Combined stability callback:
    1. Clamps log_std to [-2, 2] every step to prevent action distribution explosion
    2. Checks for NaN in parameters periodically
    """
    def __init__(self, log_std_min=-2.0, log_std_max=2.0, check_freq=500, verbose=1):
        super().__init__(verbose)
        self.log_std_min = log_std_min
        self.log_std_max = log_std_max
        self.check_freq = check_freq
        self.clamp_count = 0

    def _on_step(self) -> bool:
        # Clamp log_std every step
        for name, param in self.model.policy.named_parameters():
            if 'log_std' in name:
                with __import__('torch').no_grad():
                    old = param.data.clone()
                    param.data.clamp_(self.log_std_min, self.log_std_max)
                    if not (old == param.data).all():
                        self.clamp_count += 1
                        if self.clamp_count <= 5 or self.clamp_count % 1000 == 0:
                            print(f"  [StabilityCallback] log_std clamped at step {self.num_timesteps} "
                                  f"(total clamps: {self.clamp_count})")

        # Check for NaN periodically
        if self.n_calls % self.check_freq == 0:
            for name, param in self.model.policy.named_parameters():
                if param.data.isnan().any():
                    print(f"\n!!! NaN detected in {name} at step {self.num_timesteps} !!!")
                    print("Stopping training to prevent checkpoint corruption.")
                    return False
        return True


def find_best_checkpoint():
    """Find the latest valid checkpoint across all runs."""
    best_steps = 0
    best_path = None

    for run_dir in RUNS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        for f in run_dir.glob("anakin_*_steps.zip"):
            steps = int(f.stem.split('_')[1])
            if steps > best_steps:
                best_steps = steps
                best_path = f

    return best_path, best_steps


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--resume', type=str, default=None, help='Checkpoint path to resume from')
    parser.add_argument('--fresh', action='store_true', help='Train from scratch (ignore checkpoints)')
    parser.add_argument('--total-steps', type=int, default=40_000_000, help='Total training steps')
    args = parser.parse_args()

    print("=" * 60)
    print("Anakin Training - Stability-Enhanced")
    print("=" * 60)

    env = DummyVecEnv([lambda: Monitor(make_env('gauntlet', domain_rand=False))])

    print(f"Observation space: {env.observation_space}")
    print(f"Action space: {env.action_space}")

    checkpoint_dir = RUNS_DIR / f"fresh_{int(datetime.now().timestamp())}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    lr_schedule = linear_schedule(initial_lr=3e-4, final_lr=3e-5)

    if args.fresh or args.resume is None:
        # Check for existing checkpoint to resume from
        if not args.fresh:
            best_path, best_steps = find_best_checkpoint()
            if best_path:
                print(f"\nFound checkpoint: {best_path} ({best_steps:,} steps)")
                print("Use --fresh to train from scratch instead")
                args.resume = str(best_path)

    if args.resume:
        print(f"\nResuming from: {args.resume}")
        model = PPO.load(args.resume, env=env, device='cpu')
        # Override LR with decaying schedule
        model.learning_rate = lr_schedule
        # Override gradient clipping (less aggressive)
        model.max_grad_norm = 1.0
        reset_timesteps = False
        remaining = args.total_steps  # SB3 handles the offset internally
    else:
        print("\nTraining from scratch")
        model = PPO(
            "MlpPolicy",
            env,
            learning_rate=lr_schedule,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            max_grad_norm=1.0,
            verbose=1,
            device='cpu',
        )
        reset_timesteps = True
        remaining = args.total_steps

    params = sum(p.numel() for p in model.policy.parameters())
    print(f"  Model params: {params:,}")
    print(f"  LR: decaying 3e-4 -> 3e-5")
    print(f"  Max grad norm: {model.max_grad_norm}")
    print(f"  Target: {args.total_steps:,} total steps")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save training config for reproducibility
    with open(checkpoint_dir / "training_config.txt", "w") as f:
        f.write(f"resume: {args.resume}\n")
        f.write(f"total_steps: {args.total_steps}\n")
        f.write(f"lr: 3e-4 -> 3e-5 (linear decay)\n")
        f.write(f"max_grad_norm: 1.0\n")
        f.write(f"params: {params}\n")
        f.write(f"started: {datetime.now().isoformat()}\n")

    checkpoint_cb = CheckpointCallback(
        save_freq=500_000,
        save_path=str(checkpoint_dir),
        name_prefix="anakin"
    )

    stability_cb = StabilityCallback(log_std_min=-2.0, log_std_max=2.0, check_freq=500)

    model.learn(
        total_timesteps=remaining,
        reset_num_timesteps=reset_timesteps,
        callback=[checkpoint_cb, stability_cb],
        progress_bar=True,
        log_interval=10,
    )

    save_path = checkpoint_dir / "final_model.zip"
    model.save(save_path)
    print(f"\nTraining complete! Saved to: {save_path}")

    env.close()

if __name__ == "__main__":
    main()
