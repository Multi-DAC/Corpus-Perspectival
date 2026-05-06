"""
PPO Training Pipeline for AI Grand Prix

Architecture based on:
- Swift (Nature 2023): 2-layer MLP, PPO, state-based
- Dream to Fly (Jan 2025): Progress + gate bonus reward
- E2E RL (ICRA 2024): Direct motor commands

Phase 1: Behavior Cloning warm-start from optimal trajectory
Phase 2: PPO fine-tuning with progress reward

Usage:
    python train_ppo.py --track 19gate     # Train on 19-gate track
    python train_ppo.py --track gauntlet   # Train on gauntlet
    python train_ppo.py --eval model.zip   # Evaluate a trained model
"""

import os
import sys
import yaml
import argparse
import time
import numpy as np
from pathlib import Path

# Add parent paths
sys.path.insert(0, str(Path(__file__).parent.parent / 'sim'))

import gymnasium as gym
from gymnasium import spaces
from drone_env_v2 import (
    DroneRacingEnvV2, QuadParams, rk4_step, 
    quat_rotate_np, quat_normalize
)

# ============================================================
# CTBR Action Wrapper — Convert thrust+bodyrates to motor thrusts
# ============================================================

class CTBRActionWrapper(gym.ActionWrapper):
    """
    Wraps the motor-thrust environment to accept CTBR commands.
    
    Action: [collective_thrust_normalized, omega_x, omega_y, omega_z]
    All in [-1, 1], mapped to physical limits.
    
    This matches the control interface used by:
    - Swift: collective thrust + body rates
    - Dream to Fly: CTBR format
    - Human pilots: same control sticks
    
    Internally converts to individual motor thrusts via mixer.
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(4,), dtype=np.float32
        )
        self.params = env.params if hasattr(env, 'params') else QuadParams()
        
    def action(self, action):
        """Convert CTBR to motor thrusts."""
        action = np.clip(action, -1.0, 1.0)
        
        # Decode CTBR
        # collective thrust: [-1, 1] -> [0, 4*T_max] (sum of all motors)
        T_max = self.env.params.T_max
        collective = (action[0] + 1.0) * 0.5 * 4.0 * T_max  # [0, 4*T_max]
        
        # Body rates: [-1, 1] -> [-omega_max, omega_max]
        wx_cmd = action[1] * self.env.params.omega_max_xy
        wy_cmd = action[2] * self.env.params.omega_max_xy
        wz_cmd = action[3] * self.env.params.omega_max_z
        
        # Simple rate controller: compute torques needed, then solve for motor thrusts
        # This is a P-controller on body rates (inner loop)
        w = self.env.state[10:13]
        
        # PD gains (tuned for stability)
        Kp_xy = 0.08   # body rate P gain roll/pitch
        Kp_z = 0.02    # body rate P gain yaw
        Kd_xy = 0.002  # small D term for damping
        
        # Desired torques (simplified — P control on rate error)
        tau_x = Kp_xy * (wx_cmd - w[0])
        tau_y = Kp_xy * (wy_cmd - w[1])
        tau_z = Kp_z * (wz_cmd - w[2])
        
        # Motor mixing (X-configuration, from dynamics equations):
        # T_total = T0 + T1 + T2 + T3
        # tau_x = l * (T0 - T1 - T2 + T3)
        # tau_y = l * (-T0 - T1 + T2 + T3)
        # tau_z = ctau * (T0 - T1 + T2 - T3)
        #
        # Invert:
        l = self.env.params.arm_length
        ctau = self.env.params.ctau
        
        T0 = collective/4 + tau_x/(4*l) - tau_y/(4*l) + tau_z/(4*ctau)
        T1 = collective/4 - tau_x/(4*l) - tau_y/(4*l) - tau_z/(4*ctau)
        T2 = collective/4 - tau_x/(4*l) + tau_y/(4*l) + tau_z/(4*ctau)
        T3 = collective/4 + tau_x/(4*l) + tau_y/(4*l) - tau_z/(4*ctau)
        
        thrusts = np.array([T0, T1, T2, T3])
        thrusts = np.clip(thrusts, self.env.params.T_min, self.env.params.T_max)
        
        # Normalize to [-1, 1] for the base environment
        T_min = self.env.params.T_min
        normalized = 2.0 * (thrusts - T_min) / (T_max - T_min + 1e-8) - 1.0
        return normalized.astype(np.float32)


# ============================================================
# Improved Observation Wrapper
# ============================================================

class ImprovedObsWrapper(gym.ObservationWrapper):
    """
    Improved observation space following Swift/E2E RL papers.
    
    Observation (30-dim):
        Body frame velocity (3) — more informative than world-frame
        Angular velocity (3)
        Gravity in body frame (3) — encodes attitude without quaternion ambiguity
        Relative position to next gate in body frame (3)
        Distance to next gate (1)
        Relative position to next-next gate in body frame (3)
        Velocity magnitude (1)
        Gate progress normalized (1)
        Relative position to next gate in world frame (3) — for spatial reasoning
        Body frame forward direction (3) — heading info
        Time since last gate (1)
        Speed toward gate (1) — closing speed
        Gate orientation in body frame (3) — direction to fly through gate
        Gate alignment (1) — dot product of velocity with gate orientation [-1, 1]
    """
    
    def __init__(self, env):
        super().__init__(env)
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(30,), dtype=np.float32
        )
        self.last_gate_time = 0.0
        self.last_gate_idx = 0
    
    def observation(self, obs):
        env = self.env
        while hasattr(env, 'env'):
            env = env.env
        
        state = env.state
        pos = state[0:3]
        vel = state[3:6]
        q = state[6:10]
        omega = state[10:13]
        
        # Rotation helpers
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
        
        # Body-frame velocity
        vel_body = quat_rotate_np(q_conj, vel)
        
        # Gravity in body frame (encodes attitude without quaternion singularities)
        g_world = np.array([0.0, 0.0, -9.81])
        g_body = quat_rotate_np(q_conj, g_world)
        
        # Forward direction in world frame (body z-axis rotated to world)
        forward_body = np.array([0.0, 0.0, 1.0])
        forward_world = quat_rotate_np(q, forward_body)
        
        # Gate info
        n_gates = env.n_gates
        current = env.current_gate
        
        if current < n_gates:
            gate_pos = env.gates[current]
            rel_gate_world = gate_pos - pos
            rel_gate_body = quat_rotate_np(q_conj, rel_gate_world)
            dist_to_gate = np.linalg.norm(rel_gate_world)
            
            # Closing speed (rate of distance decrease — positive means approaching)
            speed_toward = -np.dot(vel, rel_gate_world / (dist_to_gate + 1e-6))
            
            # Gate orientation — direction to fly through
            gate_orient_world = env.gate_orientations[current]
            gate_orient_body = quat_rotate_np(q_conj, gate_orient_world)
            
            # Alignment: how well velocity aligns with gate direction (1.0 = perfect)
            speed_mag = np.linalg.norm(vel)
            if speed_mag > 0.1:
                gate_alignment = np.dot(vel / speed_mag, gate_orient_world)
            else:
                gate_alignment = 0.0
        else:
            rel_gate_world = np.zeros(3)
            rel_gate_body = np.zeros(3)
            dist_to_gate = 0.0
            speed_toward = 0.0
            gate_orient_body = np.zeros(3)
            gate_alignment = 0.0
        
        # Lookahead gate
        if current + 1 < n_gates:
            next_gate = env.gates[current + 1]
            rel_next_body = quat_rotate_np(q_conj, next_gate - pos)
        elif current < n_gates:
            rel_next_body = rel_gate_body
        else:
            rel_next_body = np.zeros(3)
        
        # Track gate changes for timing
        if current > self.last_gate_idx:
            self.last_gate_time = env.steps * env.dt
            self.last_gate_idx = current
        time_since_gate = env.steps * env.dt - self.last_gate_time
        
        speed = np.linalg.norm(vel)
        progress = current / max(n_gates, 1)
        
        return np.array([
            *vel_body,           # 3: body-frame velocity
            *omega,              # 3: angular velocity
            *g_body,             # 3: gravity in body frame (attitude encoding)
            *rel_gate_body,      # 3: next gate in body frame
            dist_to_gate,        # 1: distance to next gate
            *rel_next_body,      # 3: next-next gate in body frame
            speed,               # 1: scalar speed
            progress,            # 1: course progress
            *rel_gate_world,     # 3: next gate in world frame
            *forward_world,      # 3: forward direction
            time_since_gate,     # 1: time since last gate pass
            speed_toward,        # 1: closing speed on gate
            *gate_orient_body,   # 3: gate orientation in body frame
            gate_alignment,      # 1: velocity alignment with gate direction
        ], dtype=np.float32)
    
    def reset(self, **kwargs):
        self.last_gate_time = 0.0
        self.last_gate_idx = 0
        return super().reset(**kwargs)


# ============================================================
# Track loading
# ============================================================

def load_track(track_name):
    """Load track gates from YAML."""
    base = Path(__file__).parent.parent / 'rpg_time_optimal' / 'tracks'
    
    if track_name == '19gate':
        path = base / 'track.yaml'
    elif track_name == 'gauntlet':
        path = base / 'gauntlet.yaml'
    else:
        path = base / f'{track_name}.yaml'
    
    with open(path) as f:
        data = yaml.safe_load(f)
    
    gates = data['gates']
    init_pos = data['initial']['position']
    
    return gates, init_pos


def make_env(track_name='gauntlet', domain_rand=False, reward_config=None,
             dt=0.002, gate_radius=0.75, max_steps=30000, substeps=1,
             domain_rand_scale=0.1):
    """Create wrapped environment.

    Args:
        dt: Control/physics timestep. 0.002=500Hz (training default), 1/120=120Hz (VQ1 competition).
        gate_radius: Gate radius in meters. 0.75 (forgiving) or 0.5 (tight).
        max_steps: Max episode length. Scale with dt to maintain duration.
        substeps: Physics substeps per control step.
        domain_rand_scale: Scale for domain randomization (0.1=mild, 0.3=aggressive).
    """
    gates, init_pos = load_track(track_name)

    # Reward v2 — Gates are non-negotiable
    rc = {
        'gate_bonus': 100.0,         # Massive gate bonus — this is the POINT
        'course_complete_bonus': 500.0,  # Huge completion bonus
        'progress_scale': 1.0,       # Still reward approach but gate bonus dominates
        'time_penalty': 0.05,        # Stronger time pressure — don't dawdle
        'crash_penalty': 10.0,       # Moderate crash penalty
        'bodyrate_penalty_scale': 0.01,
        'speed_bonus_scale': 0.0,
        'attitude_penalty_scale': 0.0,
    }
    if reward_config:
        rc.update(reward_config)

    env = DroneRacingEnvV2(
        gates=gates,
        gate_radius=gate_radius,
        max_steps=max_steps,
        dt=dt,
        substeps=substeps,
        domain_randomization=domain_rand,
        domain_rand_scale=domain_rand_scale,
        reward_config=rc,
    )
    env.initial_position = np.array(init_pos, dtype=np.float64)
    
    # Wrap with CTBR actions and improved observations
    env = CTBRActionWrapper(env)
    env = ImprovedObsWrapper(env)
    
    return env


# ============================================================
# Training
# ============================================================

def train(args):
    """Train PPO agent."""
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
        from stable_baselines3.common.callbacks import (
            EvalCallback, CheckpointCallback, BaseCallback
        )
        from stable_baselines3.common.monitor import Monitor
    except ImportError:
        print("stable-baselines3 not installed. Installing...")
        os.system(f"{sys.executable} -m pip install stable-baselines3[extra]")
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import SubprocVecEnv, DummyVecEnv
        from stable_baselines3.common.callbacks import (
            EvalCallback, CheckpointCallback, BaseCallback
        )
        from stable_baselines3.common.monitor import Monitor
    
    output_dir = Path(__file__).parent / 'runs' / f'{args.track}_{int(time.time())}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Training PPO on {args.track}")
    print(f"Output: {output_dir}")
    print(f"Num envs: {args.n_envs}")
    print(f"Total timesteps: {args.total_steps:,}")
    
    # Create vectorized environments
    def make_train_env():
        def _init():
            env = make_env(args.track, domain_rand=args.domain_rand)
            env = Monitor(env)
            return env
        return _init
    
    # DummyVecEnv is more stable on Windows (SubprocVecEnv has pickling issues)
    train_envs = DummyVecEnv([make_train_env() for _ in range(args.n_envs)])
    
    # Eval environment (no domain randomization)
    eval_env = DummyVecEnv([lambda: Monitor(make_env(args.track, domain_rand=False))])
    
    # PPO hyperparameters (informed by Swift + standard PPO)
    model = PPO(
        "MlpPolicy",
        train_envs,
        verbose=1,
        device='cpu',  # CPU is faster for MLP (309 vs 286 FPS) and avoids GPU display artifacts
        learning_rate=3e-4,
        n_steps=2048,           # Steps per env per update
        batch_size=256,         # Mini-batch size
        n_epochs=10,            # Optimization epochs per update  
        gamma=0.99,             # Discount factor
        gae_lambda=0.95,        # GAE parameter
        clip_range=0.2,         # PPO clip range
        ent_coef=0.01,          # Entropy coefficient (exploration)
        vf_coef=0.5,            # Value function coefficient
        max_grad_norm=0.5,      # Gradient clipping
        policy_kwargs=dict(
            net_arch=dict(
                pi=[256, 256],   # Actor: 2 hidden layers (Swift-style)
                vf=[256, 256],   # Critic: 2 hidden layers
            ),
            activation_fn=__import__('torch').nn.Tanh,  # Tanh like Swift
        ),
        tensorboard_log=str(output_dir / 'tb'),
        seed=args.seed,
    )
    
    print(f"\nModel architecture:")
    print(f"  Policy: MLP [obs -> 256 -> 256 -> action]")
    print(f"  Value:  MLP [obs -> 256 -> 256 -> 1]")
    print(f"  Activation: Tanh")
    print(f"  Params: {sum(p.numel() for p in model.policy.parameters()):,}")
    
    # Callbacks
    class ProgressCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.best_gates = 0
            self.episode_count = 0
            
        def _on_step(self):
            # Check for completed episodes
            for info in self.locals.get('infos', []):
                if 'episode' in info:
                    self.episode_count += 1
                    ep_reward = info['episode']['r']
                    ep_len = info['episode']['l']
                    
                    gates = info.get('gates_passed', 0)
                    if gates > self.best_gates:
                        self.best_gates = gates
                        print(f"\n*** New best: {gates} gates! (ep {self.episode_count}, reward={ep_reward:.1f}) ***")
                    
                    if self.episode_count % 100 == 0:
                        print(f"  Ep {self.episode_count}: reward={ep_reward:.1f}, len={ep_len}, gates={gates}")
            
            return True
    
    callbacks = [
        ProgressCallback(),
        CheckpointCallback(
            save_freq=25000,  # ~200K total steps with 8 envs
            save_path=str(output_dir / 'checkpoints'),
            name_prefix='ppo_drone'
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
    
    # Train!
    print(f"\nStarting training...")
    model.learn(
        total_timesteps=args.total_steps,
        callback=callbacks,
        progress_bar=False,
    )
    
    # Save final model
    final_path = str(output_dir / 'final_model')
    model.save(final_path)
    print(f"\nTraining complete! Model saved to {final_path}")
    
    train_envs.close()
    eval_env.close()
    
    return str(output_dir)


# ============================================================
# Evaluation
# ============================================================

def evaluate(model_path, track_name='gauntlet', n_episodes=5, render=False):
    """Evaluate a trained model."""
    from stable_baselines3 import PPO
    
    env = make_env(track_name, domain_rand=False)
    model = PPO.load(model_path)
    
    print(f"\nEvaluating {model_path} on {track_name}")
    print(f"Episodes: {n_episodes}")
    
    results = []
    for ep in range(n_episodes):
        obs, info = env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if terminated or truncated:
                break
        
        stats = env.get_stats() if hasattr(env, 'get_stats') else {}
        inner = env
        while hasattr(inner, 'env'):
            inner = inner.env
            if hasattr(inner, 'get_stats'):
                stats = inner.get_stats()
                break
        
        gates = stats.get('gates_passed', 0)
        total = stats.get('total_gates', '?')
        t = stats.get('time', steps * 0.02)
        
        print(f"  Episode {ep+1}: gates={gates}/{total}, time={t:.1f}s, reward={total_reward:.1f}")
        results.append({
            'gates': gates,
            'total_gates': total,
            'time': t,
            'reward': total_reward,
            'steps': steps,
        })
    
    avg_gates = np.mean([r['gates'] for r in results])
    avg_reward = np.mean([r['reward'] for r in results])
    print(f"\nAverage: gates={avg_gates:.1f}, reward={avg_reward:.1f}")
    
    return results


# ============================================================
# Main
# ============================================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='PPO Drone Racing')
    parser.add_argument('--track', type=str, default='gauntlet', 
                       choices=['19gate', 'gauntlet'])
    parser.add_argument('--total-steps', type=int, default=2_000_000)
    parser.add_argument('--n-envs', type=int, default=8)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--domain-rand', action='store_true')
    parser.add_argument('--eval', type=str, default=None,
                       help='Path to model for evaluation')
    
    args = parser.parse_args()
    
    if args.eval:
        evaluate(args.eval, args.track)
    else:
        train(args)
