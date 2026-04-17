"""
Speed Optimization — Fine-tune the gauntlet specialist for faster completion.

The gauntlet specialist (gauntlet_1770766522) gets 45/45 gates at 41.1s.
Optimal trajectory is 34.8s. This script fine-tunes with aggressive 
speed-focused reward to close the 18% gap.

Approach:
- Load existing model (45/45 gates, knows the course)
- Increase time penalty and speed bonus dramatically
- Lower learning rate to preserve gate-completion ability  
- Tighter PPO clip to prevent catastrophic forgetting
- Run 4M more steps

Usage:
    python train_v10_speed.py
    python train_v10_speed.py --eval path/to/model.zip
"""

import os
import sys
import time
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from train_ppo import make_env


def train_speed(args):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.callbacks import (
        EvalCallback, CheckpointCallback, BaseCallback
    )
    from stable_baselines3.common.monitor import Monitor
    
    output_dir = Path(__file__).parent / 'runs' / f'speed_v10_{int(time.time())}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Speed Optimization - Fine-tuning Gauntlet Specialist")
    print("=" * 60)
    
    # Speed-focused reward: heavy time penalty, big speed bonus
    speed_reward = {
        'gate_bonus': 100.0,           # Keep gate bonus high
        'course_complete_bonus': 500.0, # Keep completion bonus
        'progress_scale': 1.5,          # Strong progress reward
        'time_penalty': 0.15,           # 3x original time pressure
        'crash_penalty': 15.0,          # Moderate crash penalty
        'bodyrate_penalty_scale': 0.005,
        'speed_bonus_scale': 0.2,       # Reward going fast
        'attitude_penalty_scale': 0.0,
    }
    
    # Additional speed reward: time bonus for completing quickly
    # We'll add this via a custom wrapper
    
    def make_train_env():
        def _init():
            env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
            return Monitor(env)
        return _init
    
    n_envs = args.n_envs
    train_envs = DummyVecEnv([make_train_env() for _ in range(n_envs)])
    eval_env = DummyVecEnv([lambda: Monitor(make_env('gauntlet', domain_rand=False,
                                                       reward_config=speed_reward))])
    
    # Load model — resume from checkpoint if available, otherwise from specialist
    resume_path = Path(__file__).parent / 'runs' / 'speed_v10_1770840737' / 'checkpoints' / 'ppo_speed_800000_steps'
    original_path = Path(__file__).parent.parent / 'rl' / 'runs' / 'gauntlet_1770766522' / 'best' / 'best_model'
    base_model_path = str(resume_path if resume_path.with_suffix('.zip').exists() else original_path)
    
    print(f"\nLoading base model: {base_model_path}")
    model = PPO.load(
        base_model_path,
        env=train_envs,
        device='cpu',
        # Override hyperparams for fine-tuning
        learning_rate=5e-5,      # 6x lower than original (preserve knowledge)
        clip_range=0.1,          # Tighter clip (conservative updates)
        ent_coef=0.003,          # Less exploration (it knows the course)
        n_steps=2048,
        batch_size=256,
        n_epochs=10,
        gamma=0.995,             # Slightly higher gamma (care more about future)
        gae_lambda=0.95,
        vf_coef=0.5,
        max_grad_norm=0.5,
        tensorboard_log=str(output_dir / 'tb'),
    )
    
    param_count = sum(p.numel() for p in model.policy.parameters())
    print(f"  Model params: {param_count:,}")
    
    # Quick eval of base model with new reward
    print("\nEvaluating base model with speed reward...")
    single_env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
    for ep in range(5):
        obs, _ = single_env.reset()
        total_reward = 0
        for step in range(3000):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = single_env.step(action)
            total_reward += reward
            if terminated or truncated:
                break
        inner = single_env
        while hasattr(inner, 'env'):
            inner = inner.env
        gates = inner.current_gate
        t = inner.steps * inner.dt
        complete = " COMPLETE" if info.get('course_complete') else ""
        print(f"  Base ep {ep+1}: {gates}/45 gates, {t:.2f}s, reward={total_reward:.1f}{complete}")
    
    # Training callbacks
    class SpeedCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.best_gates = 0
            self.best_time = 41.1  # Current record
            self.episode_count = 0
            self.completions = 0
            self.recent_times = []
            
        def _on_step(self):
            for info in self.locals.get('infos', []):
                if 'episode' in info:
                    self.episode_count += 1
                    ep_reward = info['episode']['r']
                    
                    # Try to get gate info from the env
                    gates = info.get('gates_passed', 0)
                    completion_time = info.get('completion_time', None)
                    
                    if completion_time:
                        self.completions += 1
                        self.recent_times.append(completion_time)
                        if completion_time < self.best_time:
                            self.best_time = completion_time
                            print(f"\n*** NEW SPEED RECORD: {completion_time:.2f}s! ***"
                                  f" (ep {self.episode_count}, completion #{self.completions})")
                    
                    if gates > self.best_gates:
                        self.best_gates = gates
                    
                    if self.episode_count % 100 == 0:
                        completion_rate = self.completions / self.episode_count * 100
                        avg_t = np.mean(self.recent_times[-20:]) if self.recent_times else 0
                        print(f"  Ep {self.episode_count}: gates={gates}, "
                              f"reward={ep_reward:.1f}, "
                              f"completions={self.completions} ({completion_rate:.0f}%), "
                              f"best={self.best_time:.2f}s, "
                              f"recent_avg={avg_t:.2f}s")
            return True
    
    callbacks = [
        SpeedCallback(),
        CheckpointCallback(
            save_freq=50000,
            save_path=str(output_dir / 'checkpoints'),
            name_prefix='ppo_speed'
        ),
        EvalCallback(
            eval_env,
            best_model_save_path=str(output_dir / 'best'),
            log_path=str(output_dir / 'eval_logs'),
            eval_freq=10000,
            n_eval_episodes=5,
            deterministic=True,
        ),
    ]
    
    print(f"\nStarting speed fine-tuning: {args.total_steps:,} steps...")
    print(f"  Envs: {n_envs}, LR: 5e-5, Clip: 0.1")
    print(f"  Time penalty: 0.15, Speed bonus: 0.2")
    print(f"  Target: < 34.8s (optimal)\n")
    
    model.learn(
        total_timesteps=args.total_steps,
        callback=callbacks,
        progress_bar=False,
    )
    
    # Save final
    model.save(str(output_dir / 'final_model'))
    print(f"\nFinal model saved to {output_dir / 'final_model'}")
    
    # Final evaluation
    print(f"\n{'=' * 60}")
    print("FINAL EVALUATION")
    print(f"{'=' * 60}")
    
    final_env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
    times = []
    
    for ep in range(10):
        obs, _ = final_env.reset()
        total_reward = 0
        for step in range(3000):
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = final_env.step(action)
            total_reward += reward
            if terminated or truncated:
                break
        
        inner = final_env
        while hasattr(inner, 'env'):
            inner = inner.env
        gates = inner.current_gate
        t = inner.steps * inner.dt
        crash = info.get('crash', '')
        complete = 'COMPLETE' if info.get('course_complete') else ''
        if complete:
            times.append(t)
        print(f"  Episode {ep+1:2d}: {gates:2d}/45 gates | "
              f"{t:6.2f}s | reward={total_reward:8.1f} | "
              f"{'crash=' + crash if crash else ''} {complete}")
    
    if times:
        print(f"\n  Completion times: {[f'{t:.2f}' for t in times]}")
        print(f"  Best: {min(times):.2f}s | Avg: {np.mean(times):.2f}s")
        print(f"  Optimal: 34.79s | Previous: 41.10s")
        improvement = (41.1 - min(times)) / 41.1 * 100
        gap_to_optimal = (min(times) - 34.79) / 34.79 * 100
        print(f"  Improvement from previous: {improvement:.1f}%")
        print(f"  Gap to optimal: {gap_to_optimal:.1f}%")
    
    train_envs.close()
    eval_env.close()
    print(f"\nAll outputs in: {output_dir}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Speed Optimization')
    parser.add_argument('--total-steps', type=int, default=4_000_000)
    parser.add_argument('--n-envs', type=int, default=8)
    parser.add_argument('--eval', type=str, default=None)
    
    args = parser.parse_args()
    
    if args.eval:
        from stable_baselines3 import PPO
        speed_reward = {
            'gate_bonus': 100.0, 'course_complete_bonus': 500.0,
            'progress_scale': 1.5, 'time_penalty': 0.15,
            'crash_penalty': 15.0, 'speed_bonus_scale': 0.2,
        }
        env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
        model = PPO.load(args.eval)
        for ep in range(10):
            obs, _ = env.reset()
            for step in range(3000):
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env.step(action)
                if terminated or truncated:
                    break
            inner = env
            while hasattr(inner, 'env'):
                inner = inner.env
            t = inner.steps * inner.dt
            print(f"  Ep {ep+1}: {inner.current_gate}/45 gates, {t:.2f}s")
    else:
        train_speed(args)
