"""
Anakin Competition Training — 120Hz + Aggressive Domain Randomization

Trains at the VQ1 competition's physics rate (120Hz) with heavy parameter
randomization to build a sim-transfer-robust policy. Resumes from the
existing 21M-step checkpoint trained at 500Hz.

Key differences from standard training:
    - dt = 1/120 (was 0.002 = 500Hz)
    - domain_rand_scale = 0.3 (was 0.1, giving ±30% mass/inertia)
    - max_steps = 7200 (~60s at 120Hz, was 30000 at 500Hz)
    - gate_radius = 0.75 (keep forgiving while adapting to new rate)

Usage:
    python train_competition.py                     # Resume from best checkpoint
    python train_competition.py --fresh             # Train from scratch at 120Hz
    python train_competition.py --total-steps 20000000  # Custom step count
"""

import os
import sys
import argparse
import numpy as np
from pathlib import Path
from datetime import datetime
from functools import partial

sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

import gymnasium as gym
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import CheckpointCallback, BaseCallback
from stable_baselines3.common.monitor import Monitor

import importlib.util
_spec = importlib.util.spec_from_file_location("train_ppo_local",
    Path(__file__).parent / "train_ppo.py")
train_ppo_local = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(train_ppo_local)

make_env = train_ppo_local.make_env
RUNS_DIR = Path(__file__).parent / "runs"

# ============================================================
# Competition physics parameters
# ============================================================
COMPETITION_DT = 1.0 / 120.0       # 120 Hz (VQ1 spec: 120Hz physics)
COMPETITION_MAX_STEPS = 7200        # ~60s at 120Hz
COMPETITION_GATE_RADIUS = 0.75      # Keep forgiving while adapting
COMPETITION_DR_SCALE = 0.3          # Aggressive: ±30% mass/inertia, ±15% thrust


def linear_schedule(initial_lr: float, final_lr: float = 3e-5):
    """Linear LR decay from initial to final over training."""
    def schedule(progress_remaining: float) -> float:
        return final_lr + (initial_lr - final_lr) * progress_remaining
    return schedule


class StabilityCallback(BaseCallback):
    """Clamps log_std and checks for NaN."""
    def __init__(self, log_std_min=-2.0, log_std_max=2.0, check_freq=500, verbose=1):
        super().__init__(verbose)
        self.log_std_min = log_std_min
        self.log_std_max = log_std_max
        self.check_freq = check_freq
        self.clamp_count = 0

    def _on_step(self) -> bool:
        import torch
        for name, param in self.model.policy.named_parameters():
            if 'log_std' in name:
                with torch.no_grad():
                    old = param.data.clone()
                    param.data.clamp_(self.log_std_min, self.log_std_max)
                    if not (old == param.data).all():
                        self.clamp_count += 1
                        if self.clamp_count <= 5 or self.clamp_count % 1000 == 0:
                            print(f"  [Stability] log_std clamped at step {self.num_timesteps} "
                                  f"(total: {self.clamp_count})")
        if self.n_calls % self.check_freq == 0:
            for name, param in self.model.policy.named_parameters():
                if param.data.isnan().any():
                    print(f"\n!!! NaN in {name} at step {self.num_timesteps} !!!")
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


def make_competition_env(track_name='gauntlet', domain_rand=True):
    """Create environment with competition physics parameters."""
    return make_env(
        track_name=track_name,
        domain_rand=domain_rand,
        dt=COMPETITION_DT,
        gate_radius=COMPETITION_GATE_RADIUS,
        max_steps=COMPETITION_MAX_STEPS,
        domain_rand_scale=COMPETITION_DR_SCALE,
    )


def main():
    parser = argparse.ArgumentParser(description='Anakin Competition Training (120Hz)')
    parser.add_argument('--resume', type=str, default=None, help='Specific checkpoint to resume from')
    parser.add_argument('--fresh', action='store_true', help='Train from scratch (ignore checkpoints)')
    parser.add_argument('--total-steps', type=int, default=20_000_000, help='Total training steps')
    parser.add_argument('--n-envs', type=int, default=4, help='Parallel environments')
    parser.add_argument('--lr', type=float, default=1e-4, help='Initial learning rate (lower for fine-tuning)')
    args = parser.parse_args()

    print("=" * 60)
    print("Anakin Competition Training — 120Hz + Aggressive DR")
    print("=" * 60)
    print(f"  Physics dt:     {COMPETITION_DT*1000:.2f} ms ({1/COMPETITION_DT:.0f} Hz)")
    print(f"  Max steps:      {COMPETITION_MAX_STEPS} (~{COMPETITION_MAX_STEPS * COMPETITION_DT:.0f}s)")
    print(f"  Gate radius:    {COMPETITION_GATE_RADIUS} m")
    print(f"  DR scale:       {COMPETITION_DR_SCALE} (±{COMPETITION_DR_SCALE*100:.0f}% mass/inertia)")
    print(f"  Envs:           {args.n_envs}")
    print(f"  Total steps:    {args.total_steps:,}")
    print(f"  Learning rate:  {args.lr} -> 3e-5")

    # Create vectorized environments with competition physics
    def make_train_env():
        def _init():
            env = make_competition_env('gauntlet', domain_rand=True)
            env = Monitor(env)
            return env
        return _init

    train_envs = DummyVecEnv([make_train_env() for _ in range(args.n_envs)])

    print(f"\nObservation space: {train_envs.observation_space}")
    print(f"Action space: {train_envs.action_space}")

    # Output directory
    checkpoint_dir = RUNS_DIR / f"competition_{int(datetime.now().timestamp())}"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    lr_schedule = linear_schedule(initial_lr=args.lr, final_lr=3e-5)

    # Find checkpoint
    if not args.fresh and args.resume is None:
        best_path, best_steps = find_best_checkpoint()
        if best_path:
            print(f"\nFound checkpoint: {best_path} ({best_steps:,} steps)")
            args.resume = str(best_path)

    if args.resume:
        print(f"Resuming from: {args.resume}")
        model = PPO.load(args.resume, env=train_envs, device='cpu')
        model.learning_rate = lr_schedule
        model.max_grad_norm = 1.0
        reset_timesteps = True  # Reset step counter for this training phase
    else:
        print("Training from scratch at 120Hz")
        model = PPO(
            "MlpPolicy",
            train_envs,
            learning_rate=lr_schedule,
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            max_grad_norm=1.0,
            verbose=1,
            device='cpu',
            policy_kwargs=dict(
                net_arch=dict(pi=[256, 256], vf=[256, 256]),
                activation_fn=__import__('torch').nn.Tanh,
            ),
            tensorboard_log=str(checkpoint_dir / 'tb'),
        )
        reset_timesteps = True

    params = sum(p.numel() for p in model.policy.parameters())
    print(f"  Params: {params:,}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Save config
    with open(checkpoint_dir / "training_config.txt", "w") as f:
        f.write(f"mode: competition_120hz\n")
        f.write(f"resume: {args.resume}\n")
        f.write(f"dt: {COMPETITION_DT}\n")
        f.write(f"max_steps: {COMPETITION_MAX_STEPS}\n")
        f.write(f"gate_radius: {COMPETITION_GATE_RADIUS}\n")
        f.write(f"dr_scale: {COMPETITION_DR_SCALE}\n")
        f.write(f"total_steps: {args.total_steps}\n")
        f.write(f"lr: {args.lr} -> 3e-5\n")
        f.write(f"n_envs: {args.n_envs}\n")
        f.write(f"params: {params}\n")
        f.write(f"started: {datetime.now().isoformat()}\n")

    checkpoint_cb = CheckpointCallback(
        save_freq=500_000,
        save_path=str(checkpoint_dir),
        name_prefix="anakin_comp"
    )
    stability_cb = StabilityCallback()

    model.learn(
        total_timesteps=args.total_steps,
        reset_num_timesteps=reset_timesteps,
        callback=[checkpoint_cb, stability_cb],
        progress_bar=True,
        log_interval=10,
    )

    save_path = checkpoint_dir / "final_model.zip"
    model.save(save_path)
    print(f"\nTraining complete! Saved to: {save_path}")

    train_envs.close()


if __name__ == "__main__":
    main()
