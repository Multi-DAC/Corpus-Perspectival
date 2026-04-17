"""
Curriculum Training — Multi-Track Generalist

Trains Anakin on all available tracks simultaneously.
Each episode randomly selects a track, building general racing skills.

Architecture:
- Loads from best single-track specialist (run 7: 34.64s on Gauntlet)
- Random track selection per episode reset
- Domain randomization for robustness
- Progressive difficulty: start with easier tracks, add harder ones

Track Roster:
- gauntlet (45 gates) — our mastered track
- autobahn (25 gates) — sweeping speed curves  
- whiplash (20 gates) — straights into sudden turns
- claustrophobia (20 gates) — tight spacing precision
- gauntlet_jr (20 gates) — smaller gauntlet variant
- corkscrew (15 gates) — tight hairpins
- elevator_shaft (15 gates) — vertical/3D maneuvering
- final_exam (25 gates) — everything combined

Usage:
    python train_curriculum.py
    python train_curriculum.py --total-steps 8000000
    python train_curriculum.py --eval path/to/model.zip
"""

import os
import sys
import time
import argparse
import numpy as np
import yaml
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from train_ppo import make_env, load_track, CTBRActionWrapper, ImprovedObsWrapper

import gymnasium as gym
from gymnasium import spaces

# Add parent paths for drone env
sys.path.insert(0, str(Path(__file__).parent))
from drone_env_v2 import DroneRacingEnvV2, QuadParams
from stable_baselines3.common.monitor import Monitor


# ============================================================
# Multi-Track Environment — Randomly selects track on reset
# ============================================================

class MultiTrackEnv(gym.Env):
    """
    Wraps multiple tracks into a single environment.
    On each reset(), randomly selects a new track.
    
    Pre-creates all track environments for speed (no reconstruction on reset).
    Swaps the active gate list and initial position in the base env directly.
    """
    
    def __init__(self, track_names, domain_rand=False, reward_config=None,
                 max_steps=30000, gate_radius=0.75):
        super().__init__()
        
        self.track_names = track_names
        self.domain_rand = domain_rand
        self.max_steps = max_steps
        self.gate_radius = gate_radius
        
        # Load all track data upfront
        self.tracks = {}
        for name in track_names:
            gates, init_pos = load_track(name)
            self.tracks[name] = {
                'gates': [np.array(g, dtype=np.float64) for g in gates],
                'init_pos': np.array(init_pos, dtype=np.float64),
            }
        
        # Build reward config (time_penalty and speed_bonus auto-scale with dt)
        self.rc = {
            'gate_bonus': 100.0,
            'course_complete_bonus': 500.0,
            'progress_scale': 1.5,
            'time_penalty': 5.0,            # Multiplied by dt in env (5.0 * 0.002 = 0.01/step)
            'crash_penalty': 15.0,
            'bodyrate_penalty_scale': 0.005,
            'speed_bonus_scale': 0.15,      # Already multiplied by dt in env
            'attitude_penalty_scale': 0.0,
        }
        if reward_config:
            self.rc.update(reward_config)
        
        # Create ONE wrapped env (using first track)
        self.current_track = track_names[0]
        first_data = self.tracks[self.current_track]
        
        self._base_env = DroneRacingEnvV2(
            gates=first_data['gates'],
            gate_radius=gate_radius,
            max_steps=max_steps,
            dt=0.002,           # 500 Hz control
            substeps=1,         # 500 Hz physics (= control rate)
            domain_randomization=domain_rand,
            domain_rand_scale=0.15,
            reward_config=self.rc,
        )
        self._base_env.initial_position = first_data['init_pos'].copy()
        
        self._env = CTBRActionWrapper(self._base_env)
        self._env = ImprovedObsWrapper(self._env)
        
        self.observation_space = self._env.observation_space
        self.action_space = self._env.action_space
        
        # Track statistics
        self.track_completions = {name: 0 for name in track_names}
        self.track_attempts = {name: 0 for name in track_names}
        self.episode_count = 0
    
    def _swap_track(self, track_name):
        """Hot-swap the gate layout in the base env (no reconstruction)."""
        data = self.tracks[track_name]
        self._base_env.gates = data['gates']
        self._base_env.n_gates = len(data['gates'])
        self._base_env.initial_position = data['init_pos'].copy()
        # Update gate-dependent precomputed data
        if hasattr(self._base_env, 'num_gates'):
            self._base_env.num_gates = len(data['gates'])
        # Recompute gate orientations for new track
        orients = []
        for i in range(len(data['gates'])):
            if i == 0:
                direction = data['gates'][0] - data['init_pos']
            else:
                direction = data['gates'][i] - data['gates'][i - 1]
            norm = np.linalg.norm(direction)
            if norm > 1e-6:
                direction = direction / norm
            else:
                direction = np.array([1.0, 0.0, 0.0])
            orients.append(direction)
        self._base_env.gate_orientations = orients
    
    def reset(self, **kwargs):
        """Reset with a randomly selected track."""
        self.current_track = np.random.choice(self.track_names)
        self.track_attempts[self.current_track] += 1
        self.episode_count += 1
        
        # Hot-swap gates (fast!)
        self._swap_track(self.current_track)
        
        obs, info = self._env.reset(**kwargs)
        info['track_name'] = self.current_track
        return obs, info
    
    def step(self, action):
        obs, reward, terminated, truncated, info = self._env.step(action)
        
        if terminated or truncated:
            if hasattr(self._base_env, 'gates_hit') and hasattr(self._base_env, 'n_gates'):
                if self._base_env.gates_hit >= self._base_env.n_gates:
                    self.track_completions[self.current_track] += 1
        
        info['track_name'] = self.current_track
        return obs, reward, terminated, truncated, info
    
    def render(self):
        return self._env.render()
    
    def close(self):
        if self._env:
            self._env.close()


# ============================================================
# Training
# ============================================================

def train_curriculum(args):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.callbacks import (
        EvalCallback, CheckpointCallback, BaseCallback
    )
    
    output_dir = Path(__file__).parent / 'runs' / f'curriculum_{int(time.time())}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("Curriculum Training — Multi-Track Generalist")
    print("=" * 60)
    
    # Hand-designed tracks
    hand_tracks = [
        'gauntlet',        # 45 gates — mastered
        'autobahn',        # 25 gates — speed
        'whiplash',        # 20 gates — speed management
        'claustrophobia',  # 20 gates — precision
        'gauntlet_jr',     # 20 gates — medium
        'corkscrew',       # 15 gates — hairpins
        'elevator_shaft',  # 15 gates — vertical
        'final_exam',      # 25 gates — everything
    ]
    
    # Load generated tracks
    gen_dir = Path(__file__).parent.parent / 'rpg_time_optimal' / 'tracks' / 'generated'
    gen_tracks = []
    if gen_dir.exists():
        for yf in sorted(gen_dir.glob('proc_*.yaml')):
            gen_tracks.append(f'generated/{yf.stem}')
    
    all_tracks = hand_tracks + gen_tracks
    
    # Verify all tracks load
    tracks_ok = []
    for name in all_tracks:
        try:
            gates, init_pos = load_track(name)
            tracks_ok.append(name)
        except Exception as e:
            print(f"  FAIL {name}: {e}")
    
    n_hand = sum(1 for t in tracks_ok if not t.startswith('generated/'))
    n_gen = sum(1 for t in tracks_ok if t.startswith('generated/'))
    print(f"\n{len(tracks_ok)} tracks loaded ({n_hand} hand-designed + {n_gen} procedural)")
    
    # Reward config — balanced for generalization
    reward_config = {
        'gate_bonus': 100.0,
        'course_complete_bonus': 500.0,
        'progress_scale': 1.5,
        'time_penalty': 0.10,
        'crash_penalty': 15.0,
        'bodyrate_penalty_scale': 0.005,
        'speed_bonus_scale': 0.15,
        'attitude_penalty_scale': 0.0,
    }
    
    # Create training envs
    n_envs = args.n_envs
    
    def make_train_env():
        def _init():
            env = MultiTrackEnv(
                tracks_ok, domain_rand=True,
                reward_config=reward_config,
                max_steps=3000, gate_radius=0.75
            )
            return Monitor(env)
        return _init
    
    train_envs = DummyVecEnv([make_train_env() for _ in range(n_envs)])
    
    # Eval on gauntlet (our benchmark) — deterministic
    eval_env = DummyVecEnv([lambda: Monitor(make_env('gauntlet', domain_rand=False,
                                                       reward_config=reward_config))])
    
    # Fresh start or resume from checkpoint
    resume_path = args.resume
    
    if resume_path and Path(resume_path).with_suffix('.zip').exists():
        print(f"\nResuming from: {resume_path}")
        model = PPO.load(
            resume_path, env=train_envs,
            learning_rate=3e-4,
            clip_range=0.2,
            ent_coef=0.01,
            n_steps=2048,
            batch_size=256,
            n_epochs=8,
        )
        print(f"  Model params: {sum(p.numel() for p in model.policy.parameters()):,}")
    else:
        print("\n*** Training from SCRATCH -- fresh generalist, no specialist bias ***")
        model = PPO(
            'MlpPolicy',
            train_envs,
            learning_rate=3e-4,       # Standard PPO default
            clip_range=0.2,           # Standard PPO default
            ent_coef=0.01,            # Encourage exploration
            n_steps=4096,             # Larger rollout for 500Hz (longer episodes)
            batch_size=512,           # Larger batch for 512-width network
            n_epochs=8,
            gamma=0.999,              # Longer horizon for 500Hz (30K steps/ep)
            gae_lambda=0.95,
            max_grad_norm=0.5,
            vf_coef=0.5,
            policy_kwargs=dict(
                net_arch=dict(pi=[512, 512], vf=[512, 512]),
            ),
            verbose=0,
            device='cpu',             # MLP policy runs faster on CPU
        )
        print(f"  Model params: {sum(p.numel() for p in model.policy.parameters()):,}")
    
    print(f"  LR: {model.learning_rate}, Ent: {model.ent_coef}")
    
    # Callbacks
    class CurriculumCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.episode_count = 0
            self.completions = 0
            self.best_time = float('inf')
            self.track_stats = {t: {'complete': 0, 'total': 0} for t in tracks_ok}
        
        def _on_step(self):
            for info in self.locals.get('infos', []):
                if 'episode' in info:
                    self.episode_count += 1
                    track = info.get('track_name', 'unknown')
                    if track in self.track_stats:
                        self.track_stats[track]['total'] += 1
                    
                    # Check for completion
                    reward = info['episode']['r']
                    if reward > 4000:  # Likely completed
                        self.completions += 1
                        if track in self.track_stats:
                            self.track_stats[track]['complete'] += 1
                    
                    # Log every 100 episodes
                    if self.episode_count % 100 == 0:
                        rate = self.completions / max(self.episode_count, 1)
                        # Aggregate by category: hand-designed vs procedural styles
                        hand_c, hand_t = 0, 0
                        style_stats = {}
                        for t in tracks_ok:
                            s = self.track_stats[t]
                            if not t.startswith('generated/'):
                                hand_c += s['complete']
                                hand_t += s['total']
                            else:
                                # Extract style from name: generated/proc_STYLE_...
                                basename = t.split('/')[-1] if '/' in t else t
                                parts = basename.split('_')
                                st = parts[1] if len(parts) > 1 else 'unknown'
                                if st not in style_stats:
                                    style_stats[st] = {'complete': 0, 'total': 0}
                                style_stats[st]['complete'] += s['complete']
                                style_stats[st]['total'] += s['total']
                        
                        print(f"\n  Ep {self.episode_count}: "
                              f"completions={self.completions} ({rate:.0%})")
                        if hand_t > 0:
                            print(f"    hand-designed: {hand_c}/{hand_t} ({hand_c/max(hand_t,1):.0%})")
                        for st in sorted(style_stats):
                            ss = style_stats[st]
                            if ss['total'] > 0:
                                print(f"    proc/{st}: {ss['complete']}/{ss['total']} ({ss['complete']/max(ss['total'],1):.0%})")
            return True
    
    checkpoint_cb = CheckpointCallback(
        save_freq=200_000 // n_envs,
        save_path=str(output_dir / 'checkpoints'),
        name_prefix='ppo_curriculum'
    )
    
    eval_cb = EvalCallback(
        eval_env,
        best_model_save_path=str(output_dir / 'best'),
        log_path=str(output_dir / 'tb'),
        eval_freq=40_000 // n_envs,
        n_eval_episodes=3,
        deterministic=True,
    )
    
    curriculum_cb = CurriculumCallback()
    
    print(f"\nStarting curriculum training: {args.total_steps:,} steps...")
    print(f"  Envs: {n_envs}, LR: {model.learning_rate}, Clip: 0.15")
    print(f"  Tracks: {len(tracks_ok)}")
    print(f"  Domain randomization: ON")
    
    model.learn(
        total_timesteps=args.total_steps,
        callback=[checkpoint_cb, eval_cb, curriculum_cb],
        reset_num_timesteps=True,
        tb_log_name='PPO_curriculum',
        progress_bar=False,
    )
    
    # Final per-track evaluation
    print("\n" + "=" * 60)
    print("Final Per-Track Evaluation")
    print("=" * 60)
    
    for track_name in tracks_ok:
        try:
            test_env = DummyVecEnv([lambda tn=track_name: Monitor(
                make_env(tn, domain_rand=False, reward_config=reward_config)
            )])
            mean_r, std_r = evaluate_policy(model, test_env, n_eval_episodes=5)
            print(f"  {track_name}: reward={mean_r:.1f} ± {std_r:.1f}")
            test_env.close()
        except Exception as e:
            print(f"  {track_name}: ERROR — {e}")
    
    print(f"\nModel saved to: {output_dir}")
    train_envs.close()
    eval_env.close()


# ============================================================
# Evaluation
# ============================================================

def evaluate_all(model_path, tracks=None):
    """Evaluate a model on all tracks."""
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.evaluation import evaluate_policy
    
    all_tracks = tracks or [
        'gauntlet', 'autobahn', 'whiplash', 'claustrophobia',
        'gauntlet_jr', 'corkscrew', 'elevator_shaft', 'final_exam',
    ]
    
    reward_config = {
        'gate_bonus': 100.0,
        'course_complete_bonus': 500.0,
        'progress_scale': 1.5,
        'time_penalty': 0.10,
        'crash_penalty': 15.0,
        'bodyrate_penalty_scale': 0.005,
        'speed_bonus_scale': 0.15,
    }
    
    model = PPO.load(model_path)
    
    print(f"Evaluating {model_path} on {len(all_tracks)} tracks\n")
    
    for track_name in all_tracks:
        try:
            env = DummyVecEnv([lambda tn=track_name: Monitor(
                make_env(tn, domain_rand=False, reward_config=reward_config)
            )])
            mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=5, deterministic=True)
            print(f"  {track_name:20s}: reward={mean_r:.1f} ± {std_r:.1f}")
            env.close()
        except Exception as e:
            print(f"  {track_name:20s}: ERROR — {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--total-steps', type=int, default=8_000_000)
    parser.add_argument('--n-envs', type=int, default=8)
    parser.add_argument('--eval', type=str, default=None)
    parser.add_argument('--resume', type=str, default=None, help='Path to checkpoint to resume from')
    args = parser.parse_args()
    
    if args.eval:
        evaluate_all(args.eval)
    else:
        train_curriculum(args)
