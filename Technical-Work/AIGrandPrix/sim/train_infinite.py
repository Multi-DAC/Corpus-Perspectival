"""
Infinite Gate Training — Procedural Maneuver Mastery

Trains on an infinite stream of procedurally generated gates.
Each gate transition tests a specific maneuver from the library.
Adaptive curriculum biases toward weak skills.

Usage:
    python train_infinite.py
    python train_infinite.py --total-steps 40000000
    python train_infinite.py --eval path/to/model.zip
"""

import os
import sys
import time
import argparse
import numpy as np
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import (
    EvalCallback, CheckpointCallback, BaseCallback
)

# Import make_env from rl/ (not sim/)
rl_dir = str(Path(__file__).parent.parent / 'rl')
if rl_dir not in sys.path:
    sys.path.insert(0, rl_dir)
# Remove sim/ from path temporarily to avoid wrong train_ppo
sim_dir = os.path.dirname(__file__)
if sim_dir in sys.path:
    sys.path.remove(sim_dir)
from train_ppo import make_env
sys.path.insert(0, sim_dir)  # Re-add sim/


class ManeuverStatsCallback(BaseCallback):
    """Track per-maneuver success rates across all envs. Persists to disk."""
    
    STATS_FILE = Path(__file__).parent / 'runs' / 'maneuver_stats.json'
    
    def __init__(self):
        super().__init__()
        self.episode_count = 0
        self.total_gates = 0
        self.gates_per_episode = []
        self.maneuver_stats = {m: {'ok': 0, 'total': 0} 
                               for m in ManeuverLibrary.MANEUVERS}
        # Load persisted stats
        self._load_stats()
    
    def _load_stats(self):
        """Load accumulated stats from disk."""
        import json
        if self.STATS_FILE.exists():
            try:
                with open(self.STATS_FILE) as f:
                    data = json.load(f)
                self.total_gates = data.get('total_gates', 0)
                self.episode_count = data.get('episode_count', 0)
                for m in ManeuverLibrary.MANEUVERS:
                    if m in data.get('maneuvers', {}):
                        self.maneuver_stats[m] = data['maneuvers'][m]
                print(f"  Loaded persisted stats: {self.episode_count} episodes, {self.total_gates} gates")
            except Exception:
                pass
    
    def _save_stats(self, all_stats):
        """Save accumulated stats to disk."""
        import json
        data = {
            'episode_count': self.episode_count,
            'total_gates': self.total_gates,
            'maneuvers': all_stats if all_stats else self.maneuver_stats,
        }
        self.STATS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.STATS_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    
    def _on_step(self):
        # Step-based logging (every 500K steps) — more reliable than episode detection
        # which can be swallowed by DummyVecEnv auto-reset
        total_steps = self.num_timesteps
        if total_steps > 0 and total_steps % 500_000 < self.locals.get('n_envs', 8):
            self._log_stats()
        return True

    def _log_stats(self):
        """Aggregate and print stats from all training envs."""
        # Aggregate maneuver stats from all envs
        all_stats = {}
        for env_fn in self.training_env.envs:
            env = env_fn
            while hasattr(env, 'env'):
                env = env.env
            if hasattr(env, 'get_maneuver_stats'):
                for m, s in env.get_maneuver_stats().items():
                    if m not in all_stats:
                        all_stats[m] = {'ok': 0, 'total': 0}
                    all_stats[m]['ok'] += s['successes']
                    all_stats[m]['total'] += s['attempts']

        if all_stats:
            total_gates = sum(s['total'] for s in all_stats.values())
            total_ok = sum(s['ok'] for s in all_stats.values())
            print(f"\n  === Stats @ {self.num_timesteps:,} steps ===")
            print(f"  Total gates: {total_gates}, success: {total_ok/max(total_gates,1):.0%}")
            for m in sorted(all_stats):
                s = all_stats[m]
                if s['total'] > 0:
                    rate = s['ok'] / s['total']
                    print(f"    {m:15s}: {s['ok']}/{s['total']} ({rate:.0%})")
            self._save_stats(all_stats)

        # Log curriculum stats (sequence planner progression)
        for env_fn in self.training_env.envs:
            env = env_fn
            while hasattr(env, 'env'):
                env = env.env
            if hasattr(env, 'get_curriculum_stats'):
                cs = env.get_curriculum_stats()
                avg_m = cs['avg_mastery']
                raw_m = cs.get('raw_avg_mastery', avg_m)
                ema_m = cs.get('ema_mastery', avg_m)
                dist = cs['planner']['complexity_distribution']
                target = cs['planner'].get('target_distribution', {})
                completions = cs['planner']['sequence_completions']
                failures = cs['planner']['sequence_failures']
                decisions = cs['planner'].get('total_decisions', 0)
                print(f"  Curriculum: ema={ema_m:.0%} raw={raw_m:.0%} | decisions={decisions}")
                # Per-maneuver breakdown if available
                per_m = cs.get('per_maneuver', {})
                if per_m:
                    weak = [(m, r) for m, r in sorted(per_m.items(), key=lambda x: x[1]) if r < 0.82]
                    if weak:
                        weak_str = ", ".join(f"{m}={r:.0%}" for m, r in weak[:4])
                        print(f"    Weak (<82%): {weak_str}")
                print(f"    Empirical: word={dist.get('word',0):.0%} "
                      f"sent={dist.get('sentence',0):.0%} "
                      f"para={dist.get('paragraph',0):.0%} "
                      f"essay={dist.get('essay',0):.0%}")
                if target:
                    print(f"    Target:    word={target.get('word',0):.0%} "
                          f"sent={target.get('sentence',0):.0%} "
                          f"para={target.get('paragraph',0):.0%} "
                          f"essay={target.get('essay',0):.0%}")
                if any(v > 0 for v in completions.values()):
                    print(f"    Completions: sent={completions.get('sentence',0)} "
                          f"para={completions.get('paragraph',0)} "
                          f"essay={completions.get('essay',0)} | "
                          f"Failures: sent={failures.get('sentence',0)} "
                          f"para={failures.get('paragraph',0)} "
                          f"essay={failures.get('essay',0)}")
                break  # Only need one env's stats


def train_infinite(args):
    output_dir = Path(__file__).parent / 'runs' / f'infinite_{int(time.time())}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Infinite Gate Training -- Procedural Maneuver Mastery")
    print("=" * 60)
    print(f"  Maneuvers: {len(ManeuverLibrary.MANEUVERS)}")
    for m in ManeuverLibrary.MANEUVERS:
        print(f"    - {m}")
    
    n_envs = args.n_envs
    
    def make_infinite_env(seed=None):
        def _init():
            env = InfiniteGateEnv(
                gate_radius=0.75,
                max_steps=30000,      # 60s at 500Hz
                dt=0.002,             # 500Hz
                substeps=1,
                domain_rand=True,
                domain_rand_scale=0.15,
                adaptive_curriculum=True,
                seed=seed,
            )
            return Monitor(env)
        return _init
    
    train_envs = DummyVecEnv([make_infinite_env(seed=i*42) for i in range(n_envs)])
    
    # Eval on gauntlet (real track benchmark)
    reward_config = {
        'gate_bonus': 100.0,
        'progress_scale': 1.5,
        'time_penalty': 5.0,
        'crash_penalty': 15.0,
        'speed_bonus_scale': 0.15,
        'gate_speed_scale': 0.08,  # Match training env (doubled for speed incentive)
    }
    eval_env = DummyVecEnv([lambda: Monitor(make_env('gauntlet', domain_rand=False,
                                                       reward_config=reward_config))])
    
    if args.resume:
        print(f"\nResuming from: {args.resume}")
        model = PPO.load(args.resume, env=train_envs, device='cpu')
        # Aggressive LR reduction for fine-tuning stability
        # 1e-4 still causes NaN — policy is in steep gradient region after 60M+ steps
        model.learning_rate = 3e-5
        model.max_grad_norm = 0.3  # Tighter gradient clipping (default is 0.5)
        print(f"  LR reduced to {model.learning_rate}, max_grad_norm={model.max_grad_norm}")
    else:
        print("\n*** Training from SCRATCH -- infinite gate generalist ***")
        model = PPO(
            'MlpPolicy',
            train_envs,
            learning_rate=3e-4,
            clip_range=0.2,
            ent_coef=0.01,
            n_steps=4096,
            batch_size=512,
            n_epochs=8,
            gamma=0.999,
            gae_lambda=0.95,
            max_grad_norm=0.5,
            vf_coef=0.5,
            policy_kwargs=dict(
                net_arch=dict(pi=[512, 512], vf=[512, 512]),
            ),
            verbose=0,
            device='cpu',
        )
    
    print(f"  Model params: {sum(p.numel() for p in model.policy.parameters()):,}")
    print(f"  LR: {model.learning_rate}, Ent: {model.ent_coef}")
    
    # Callbacks
    checkpoint_cb = CheckpointCallback(
        save_freq=500_000 // n_envs,
        save_path=str(output_dir / 'checkpoints'),
        name_prefix='ppo_infinite'
    )
    
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path=str(output_dir / 'best'),
        log_path=str(output_dir / 'tb'),
        eval_freq=100_000 // n_envs,
        n_eval_episodes=3,
        deterministic=True,
    )
    
    stats_cb = ManeuverStatsCallback()
    
    print(f"\nStarting infinite gate training: {args.total_steps:,} steps...")
    print(f"  Envs: {n_envs}")
    print(f"  Adaptive curriculum: ON")
    print(f"  Domain randomization: ON")
    
    model.learn(
        total_timesteps=args.total_steps,
        callback=[checkpoint_cb, eval_cb, stats_cb],
        reset_num_timesteps=True,
        tb_log_name='PPO_infinite',
        progress_bar=False,
    )
    
    # Final stats
    print("\n" + "=" * 60)
    print("Final Maneuver Mastery")
    print("=" * 60)
    
    for env_fn in train_envs.envs:
        env = env_fn
        while hasattr(env, 'env'):
            env = env.env
        if hasattr(env, 'get_maneuver_stats'):
            for m, s in env.get_maneuver_stats().items():
                rate = s['successes'] / max(s['attempts'], 1)
                bar = '#' * int(rate * 20)
                print(f"  {m:15s}: {rate:5.1%} [{bar:20s}] ({s['successes']}/{s['attempts']})")
            break
    
    # Eval on all hand-designed tracks
    print("\n" + "=" * 60)
    print("Transfer Test -- Hand-Designed Tracks")
    print("=" * 60)
    
    from stable_baselines3.common.evaluation import evaluate_policy
    
    for track_name in ['gauntlet', 'corkscrew', 'autobahn', 'claustrophobia',
                       'elevator_shaft', 'whiplash', 'final_exam']:
        try:
            test_env = DummyVecEnv([lambda tn=track_name: Monitor(
                make_env(tn, domain_rand=False, reward_config=reward_config)
            )])
            mean_r, std_r = evaluate_policy(model, test_env, n_eval_episodes=5, deterministic=True)
            print(f"  {track_name:20s}: reward={mean_r:.1f} +/- {std_r:.1f}")
            test_env.close()
        except Exception as e:
            print(f"  {track_name:20s}: ERROR -- {e}")
    
    print(f"\nModel saved to: {output_dir}")
    train_envs.close()
    eval_env.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--total-steps', type=int, default=40_000_000)
    parser.add_argument('--n-envs', type=int, default=8)
    parser.add_argument('--resume', type=str, default=None)
    args = parser.parse_args()
    
    train_infinite(args)
