"""
DAgger Warm-Start + PPO Fine-Tuning for Speed Optimization

Strategy:
1. Parse optimal trajectory CSV -> state-action pairs
2. Convert raw motor thrusts -> CTBR format (what the policy outputs)
3. Pre-train SB3 PPO policy via behavior cloning on expert data
4. Fine-tune with PPO using speed-focused reward shaping

The gauntlet specialist already gets 45/45 gates at 41.1s.
Optimal is 34.8s. This pipeline aims to close that 18% gap.

Usage:
    python train_v9_dagger_warmstart.py                    # Full pipeline
    python train_v9_dagger_warmstart.py --skip-bc          # Skip BC, just PPO
    python train_v9_dagger_warmstart.py --eval model.zip   # Evaluate
"""

import os
import sys
import time
import argparse
import csv
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from pathlib import Path
from scipy.spatial import KDTree

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from drone_env_v2 import (
    DroneRacingEnvV2, QuadParams, rk4_step,
    quat_rotate_np, quat_normalize
)
from train_ppo import CTBRActionWrapper, ImprovedObsWrapper, load_track, make_env


# ============================================================
# Expert Trajectory Parsing
# ============================================================

def parse_optimal_trajectory(csv_path):
    """
    Parse the RPG optimizer's output CSV into state and action arrays.
    
    CSV columns: t, p_x, p_y, p_z, q_w, q_x, q_y, q_z, v_x, v_y, v_z,
                 w_x, w_y, w_z, a_lin_x, ..., u_1, u_2, u_3, u_4, ...
    
    Returns:
        times: (N,) timestamps
        states: (N, 13) [pos(3), vel(3), quat(4), bodyrate(3)]
        motor_thrusts: (N, 4) raw motor thrusts in Newtons
    """
    times = []
    states = []
    thrusts = []
    
    with open(csv_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # Find column indices
        col = {name: i for i, name in enumerate(header)}
        
        for row in reader:
            if not row or len(row) < 20:
                continue  # Skip empty rows
            t = float(row[col['t']])
            
            # State: [px, py, pz, vx, vy, vz, qw, qx, qy, qz, wx, wy, wz]
            state = np.array([
                float(row[col['p_x']]),
                float(row[col['p_y']]),
                float(row[col['p_z']]),
                float(row[col['v_x']]),
                float(row[col['v_y']]),
                float(row[col['v_z']]),
                float(row[col['q_w']]),
                float(row[col['q_x']]),
                float(row[col['q_y']]),
                float(row[col['q_z']]),
                float(row[col['w_x']]),
                float(row[col['w_y']]),
                float(row[col['w_z']]),
            ])
            
            # Motor thrusts
            u = np.array([
                float(row[col['u_1']]),
                float(row[col['u_2']]),
                float(row[col['u_3']]),
                float(row[col['u_4']]),
            ])
            
            times.append(t)
            states.append(state)
            thrusts.append(u)
    
    return np.array(times), np.array(states), np.array(thrusts)


def motor_thrusts_to_ctbr(thrusts, params=None):
    """
    Convert raw motor thrusts [T1,T2,T3,T4] to CTBR actions [-1,1].
    
    CTBR = [collective_thrust_norm, omega_x_norm, omega_y_norm, omega_z_norm]
    
    The CTBR wrapper maps:
        collective: [-1,1] -> [0, 4*T_max]
        omega_xy:   [-1,1] -> [-omega_max_xy, omega_max_xy]  
        omega_z:    [-1,1] -> [-omega_max_z, omega_max_z]
    
    But the wrapper also has a P-controller that converts CTBR commands to thrusts.
    So we can't simply invert the mixer — we need to figure out what CTBR command
    the P-controller would need to produce these thrusts.
    
    Instead, we'll compute the CTBR representation directly from the state:
    - Collective = sum of thrusts, normalized
    - Body rates = actual body rates from the state (the controller target)
    """
    if params is None:
        params = QuadParams()
    
    T_max = params.T_max
    
    ctbr_actions = []
    for thrust in thrusts:
        # Collective thrust normalized to [-1, 1]
        # collective in [0, 4*T_max] maps to [-1, 1]
        collective = np.sum(thrust)
        collective_norm = (collective / (4.0 * T_max)) * 2.0 - 1.0
        
        ctbr_actions.append(np.array([collective_norm, 0.0, 0.0, 0.0]))  # placeholder
    
    return np.array(ctbr_actions)


def expert_to_ctbr_from_states(states, thrusts, params=None):
    """
    Build CTBR expert actions from trajectory states.
    
    Since the CTBR wrapper implements a P-controller on body rates,
    and the expert trajectory has the actual body rates at each timestep,
    the expert CTBR command is simply:
    - collective_norm from total thrust
    - body_rate targets = the actual body rates (since the expert is tracking them)
    """
    if params is None:
        params = QuadParams()
    
    T_max = params.T_max
    
    ctbr_actions = []
    for i in range(len(states)):
        # Collective from thrust sum
        collective = np.sum(thrusts[i])
        collective_norm = np.clip((collective / (4.0 * T_max)) * 2.0 - 1.0, -1.0, 1.0)
        
        # Body rates from state, normalized to [-1, 1]
        wx = states[i, 10]  # body rate x
        wy = states[i, 11]  # body rate y  
        wz = states[i, 12]  # body rate z
        
        wx_norm = np.clip(wx / params.omega_max_xy, -1.0, 1.0)
        wy_norm = np.clip(wy / params.omega_max_xy, -1.0, 1.0)
        wz_norm = np.clip(wz / params.omega_max_z, -1.0, 1.0)
        
        ctbr_actions.append(np.array([collective_norm, wx_norm, wy_norm, wz_norm]))
    
    return np.array(ctbr_actions, dtype=np.float32)


def build_improved_obs(states, gates, gate_radius=0.75):
    """
    Build ImprovedObsWrapper-compatible observations from expert trajectory states.
    
    Matches the 26-dim observation format:
    [vel_body(3), omega(3), g_body(3), rel_gate_body(3), dist(1),
     rel_next_body(3), speed(1), progress(1), rel_gate_world(3),
     forward_world(3), time_since_gate(1), speed_toward(1)]
    """
    n_gates = len(gates)
    observations = []
    
    current_gate = 0
    last_gate_time = 0.0
    dt_traj = 0.0  # Will be set from time differences
    
    for i in range(len(states)):
        state = states[i]
        pos = state[0:3]
        vel = state[3:6]
        q = state[6:10]
        omega = state[10:13]
        
        # Check gate passage
        if current_gate < n_gates:
            dist_to_current = np.linalg.norm(pos - gates[current_gate])
            if dist_to_current < gate_radius:
                current_gate += 1
                last_gate_time = i * 0.01  # approximate
        
        # Rotation helpers
        q_conj = np.array([q[0], -q[1], -q[2], -q[3]])
        
        # Body-frame velocity
        vel_body = quat_rotate_np(q_conj, vel)
        
        # Gravity in body frame
        g_world = np.array([0.0, 0.0, -9.81])
        g_body = quat_rotate_np(q_conj, g_world)
        
        # Forward direction (body z-axis in world)
        forward_body = np.array([0.0, 0.0, 1.0])
        forward_world = quat_rotate_np(q, forward_body)
        
        # Gate info
        if current_gate < n_gates:
            gate_pos = gates[current_gate]
            rel_gate_world = gate_pos - pos
            rel_gate_body = quat_rotate_np(q_conj, rel_gate_world)
            dist_to_gate = np.linalg.norm(rel_gate_world)
            speed_toward = -np.dot(vel, rel_gate_world / (dist_to_gate + 1e-6))
        else:
            rel_gate_world = np.zeros(3)
            rel_gate_body = np.zeros(3)
            dist_to_gate = 0.0
            speed_toward = 0.0
        
        # Lookahead gate
        if current_gate + 1 < n_gates:
            next_gate = gates[current_gate + 1]
            rel_next_body = quat_rotate_np(q_conj, next_gate - pos)
        elif current_gate < n_gates:
            rel_next_body = rel_gate_body
        else:
            rel_next_body = np.zeros(3)
        
        speed = np.linalg.norm(vel)
        progress = current_gate / max(n_gates, 1)
        time_since_gate = i * 0.01 - last_gate_time
        
        obs = np.array([
            *vel_body,           # 3
            *omega,              # 3
            *g_body,             # 3
            *rel_gate_body,      # 3
            dist_to_gate,        # 1
            *rel_next_body,      # 3
            speed,               # 1
            progress,            # 1
            *rel_gate_world,     # 3
            *forward_world,      # 3
            time_since_gate,     # 1
            speed_toward,        # 1
        ], dtype=np.float32)
        
        observations.append(obs)
    
    return np.array(observations, dtype=np.float32)


# ============================================================
# Behavior Cloning into SB3 PPO Policy
# ============================================================

def pretrain_ppo_bc(model, observations, actions, epochs=100, batch_size=256, 
                    lr=1e-3, device='cpu'):
    """
    Pre-train SB3 PPO policy network via supervised learning on expert data.
    
    This directly modifies the PPO model's actor network weights.
    """
    policy = model.policy
    actor = policy.action_net  # The final layer mapping features -> actions
    features_extractor = policy.mlp_extractor  # The shared MLP
    
    # We need to train the full pipeline: obs -> features_extractor -> actor
    # Set up the forward pass through SB3's architecture
    
    X = torch.FloatTensor(observations).to(device)
    Y = torch.FloatTensor(actions).to(device)
    
    dataset = TensorDataset(X, Y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    # Only optimize actor parameters (not critic)
    actor_params = (
        list(features_extractor.policy_net.parameters()) + 
        list(actor.parameters())
    )
    optimizer = optim.Adam(actor_params, lr=lr)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    print(f"\nPre-training PPO actor via Behavior Cloning...")
    print(f"  Samples: {len(observations)}, Epochs: {epochs}, Batch: {batch_size}")
    
    best_loss = float('inf')
    
    for epoch in range(epochs):
        policy.train()
        total_loss = 0
        n_batches = 0
        
        for obs_batch, act_batch in loader:
            # Forward through SB3 policy architecture
            features = features_extractor.forward_actor(
                policy.extract_features(obs_batch, policy.pi_features_extractor)
            )
            pred_actions = actor(features)
            
            # MSE loss on actions
            loss = nn.MSELoss()(pred_actions, act_batch)
            
            # Also add a small loss to keep actions bounded
            bound_loss = 0.01 * torch.mean(torch.relu(pred_actions.abs() - 1.0))
            total = loss + bound_loss
            
            optimizer.zero_grad()
            total.backward()
            torch.nn.utils.clip_grad_norm_(actor_params, 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            n_batches += 1
        
        scheduler.step()
        avg_loss = total_loss / n_batches
        
        if avg_loss < best_loss:
            best_loss = avg_loss
        
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1:4d}/{epochs}: loss={avg_loss:.6f} (best={best_loss:.6f})")
    
    policy.eval()
    print(f"  BC pre-training complete. Best loss: {best_loss:.6f}")
    
    return model


def augment_expert_data(observations, actions, n_augment=5, noise_scale=0.15):
    """
    Data augmentation: add noise to observations to improve robustness.
    Key insight: near the expert trajectory, the same action is approximately correct.
    """
    aug_obs = [observations]
    aug_act = [actions]
    
    for i in range(n_augment):
        noisy = observations.copy()
        
        # Add noise to body-frame velocity (dims 0-2)
        noisy[:, 0:3] += np.random.normal(0, noise_scale * 2, size=(len(observations), 3)).astype(np.float32)
        
        # Add noise to angular velocity (dims 3-5)
        noisy[:, 3:6] += np.random.normal(0, noise_scale, size=(len(observations), 3)).astype(np.float32)
        
        # Small noise to gravity-in-body (dims 6-8) — attitude perturbation
        noisy[:, 6:9] += np.random.normal(0, noise_scale * 0.5, size=(len(observations), 3)).astype(np.float32)
        
        # Noise to relative gate positions (dims 9-11, 13-15, 19-21)
        for dims in [(9, 12), (13, 16), (19, 22)]:
            noisy[:, dims[0]:dims[1]] += np.random.normal(
                0, noise_scale * 3, size=(len(observations), 3)
            ).astype(np.float32)
        
        aug_obs.append(noisy)
        aug_act.append(actions.copy())
    
    result_obs = np.concatenate(aug_obs)
    result_act = np.concatenate(aug_act)
    
    print(f"  Augmented: {len(observations)} -> {len(result_obs)} samples ({n_augment}x noise)")
    return result_obs, result_act


# ============================================================
# DAgger with SB3 PPO
# ============================================================

def dagger_collect(model, env, expert_states, expert_actions, 
                   n_episodes=20, max_steps=3000):
    """
    Run current policy, collect (obs, expert_action) pairs via nearest-neighbor.
    """
    # KD-tree on expert positions + velocities for state matching
    expert_pv = expert_states[:, 0:6]  # pos + vel
    kdtree = KDTree(expert_pv)
    
    all_obs = []
    all_expert_act = []
    episode_stats = []
    
    for ep in range(n_episodes):
        obs, _ = env.reset()
        
        for step in range(max_steps):
            # Get policy action
            action, _ = model.predict(obs, deterministic=False)  # Stochastic for exploration
            
            # Get expert action via nearest neighbor
            inner = env
            while hasattr(inner, 'env'):
                inner = inner.env
            state_query = inner.state[0:6]
            _, idx = kdtree.query(state_query)
            expert_act = expert_actions[min(idx, len(expert_actions) - 1)]
            
            # Record
            all_obs.append(obs.copy())
            all_expert_act.append(expert_act.copy())
            
            # Step with policy action
            obs, reward, terminated, truncated, info = env.step(action)
            
            if terminated or truncated:
                break
        
        # Get gate count
        inner = env
        while hasattr(inner, 'env'):
            inner = inner.env
        episode_stats.append({
            'gates': inner.current_gate,
            'time': inner.steps * inner.dt,
        })
    
    avg_gates = np.mean([s['gates'] for s in episode_stats])
    avg_time = np.mean([s['time'] for s in episode_stats])
    
    return (np.array(all_obs, dtype=np.float32), 
            np.array(all_expert_act, dtype=np.float32),
            avg_gates, avg_time)


# ============================================================
# Main Pipeline
# ============================================================

def main(args):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.callbacks import (
        EvalCallback, CheckpointCallback, BaseCallback
    )
    from stable_baselines3.common.monitor import Monitor
    
    base_dir = Path(__file__).parent.parent
    output_dir = Path(__file__).parent / 'runs' / f'dagger_v9_{int(time.time())}'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 60)
    print("DAgger Warm-Start + PPO Speed Optimization")
    print("=" * 60)
    
    # --------------------------------------------------------
    # Step 1: Parse expert trajectory
    # --------------------------------------------------------
    csv_path = base_dir / 'rpg_time_optimal' / 'example' / 'gauntlet_result.csv'
    print(f"\n[1/4] Parsing expert trajectory: {csv_path}")
    
    times, states, thrusts = parse_optimal_trajectory(str(csv_path))
    print(f"  Loaded {len(times)} timesteps, {times[-1]:.2f}s total")
    print(f"  Position range: x=[{states[:,0].min():.1f}, {states[:,0].max():.1f}], "
          f"z=[{states[:,2].min():.1f}, {states[:,2].max():.1f}]")
    print(f"  Speed range: [{np.linalg.norm(states[:,3:6], axis=1).min():.1f}, "
          f"{np.linalg.norm(states[:,3:6], axis=1).max():.1f}] m/s")
    
    # Load gauntlet gates
    gates_list, init_pos = load_track('gauntlet')
    gates = [np.array(g, dtype=np.float64) for g in gates_list]
    
    # Convert to CTBR actions
    print("\n  Converting motor thrusts -> CTBR actions...")
    ctbr_actions = expert_to_ctbr_from_states(states, thrusts)
    print(f"  CTBR collective range: [{ctbr_actions[:,0].min():.3f}, {ctbr_actions[:,0].max():.3f}]")
    print(f"  CTBR wx range: [{ctbr_actions[:,1].min():.3f}, {ctbr_actions[:,1].max():.3f}]")
    print(f"  CTBR wy range: [{ctbr_actions[:,2].min():.3f}, {ctbr_actions[:,2].max():.3f}]")
    print(f"  CTBR wz range: [{ctbr_actions[:,3].min():.3f}, {ctbr_actions[:,3].max():.3f}]")
    
    # Build improved observations
    print("\n  Building 26-dim observations from trajectory...")
    expert_obs = build_improved_obs(states, gates, gate_radius=0.75)
    print(f"  Observations shape: {expert_obs.shape}")
    
    # Augment
    expert_obs_aug, ctbr_actions_aug = augment_expert_data(
        expert_obs, ctbr_actions, n_augment=args.augment_factor
    )
    
    # --------------------------------------------------------
    # Step 2: Create PPO model and pre-train via BC
    # --------------------------------------------------------
    print(f"\n[2/4] Creating PPO model and pre-training via BC...")
    
    # Speed-focused reward for fine-tuning
    speed_reward = {
        'gate_bonus': 100.0,
        'course_complete_bonus': 500.0,
        'progress_scale': 1.0,
        'time_penalty': 0.1,          # Stronger time pressure for speed
        'crash_penalty': 10.0,
        'bodyrate_penalty_scale': 0.005,
        'speed_bonus_scale': 0.15,    # More speed reward
        'attitude_penalty_scale': 0.0,
    }
    
    def make_train_env():
        def _init():
            env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
            return Monitor(env)
        return _init
    
    n_envs = args.n_envs
    train_envs = DummyVecEnv([make_train_env() for _ in range(n_envs)])
    eval_env = DummyVecEnv([lambda: Monitor(make_env('gauntlet', domain_rand=False, 
                                                       reward_config=speed_reward))])
    
    # Initialize PPO
    model = PPO(
        "MlpPolicy",
        train_envs,
        verbose=1,
        device='cpu',
        learning_rate=1e-4,          # Lower LR for fine-tuning (don't destroy BC weights)
        n_steps=2048,
        batch_size=256,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.15,             # Tighter clip for fine-tuning
        ent_coef=0.005,              # Less exploration (BC gives good init)
        vf_coef=0.5,
        max_grad_norm=0.5,
        policy_kwargs=dict(
            net_arch=dict(
                pi=[256, 256],
                vf=[256, 256],
            ),
            activation_fn=torch.nn.Tanh,
        ),
        tensorboard_log=str(output_dir / 'tb'),
        seed=args.seed,
    )
    
    param_count = sum(p.numel() for p in model.policy.parameters())
    print(f"  Model params: {param_count:,}")
    
    if not args.skip_bc:
        # Pre-train actor with BC
        model = pretrain_ppo_bc(
            model, expert_obs_aug, ctbr_actions_aug,
            epochs=args.bc_epochs, batch_size=256, lr=args.bc_lr
        )
        
        # Quick eval after BC
        print("\n  Evaluating BC-initialized policy...")
        single_env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
        bc_results = []
        for ep in range(5):
            obs, _ = single_env.reset()
            for step in range(3000):
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = single_env.step(action)
                if terminated or truncated:
                    break
            inner = single_env
            while hasattr(inner, 'env'):
                inner = inner.env
            gates = inner.current_gate
            t = inner.steps * inner.dt
            print(f"    BC ep {ep+1}: {gates}/45 gates, {t:.1f}s")
            bc_results.append({'gates': gates, 'time': t})
        
        avg_bc_gates = np.mean([r['gates'] for r in bc_results])
        print(f"  BC average: {avg_bc_gates:.1f}/45 gates")
        
        # Save BC model
        model.save(str(output_dir / 'bc_model'))
        print(f"  Saved BC model to {output_dir / 'bc_model'}")
    
    # --------------------------------------------------------
    # Step 3: DAgger rounds (optional)
    # --------------------------------------------------------
    if args.dagger_rounds > 0:
        print(f"\n[3/4] Running {args.dagger_rounds} DAgger rounds...")
        
        dagger_env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
        
        all_obs = expert_obs_aug.copy()
        all_act = ctbr_actions_aug.copy()
        
        for round_i in range(args.dagger_rounds):
            new_obs, new_act, avg_gates, avg_time = dagger_collect(
                model, dagger_env, states, ctbr_actions,
                n_episodes=args.dagger_episodes
            )
            
            all_obs = np.concatenate([all_obs, new_obs])
            all_act = np.concatenate([all_act, new_act])
            
            print(f"  Round {round_i+1}/{args.dagger_rounds}: "
                  f"{len(new_obs)} samples, avg gates={avg_gates:.1f}, "
                  f"avg time={avg_time:.1f}s, total dataset={len(all_obs)}")
            
            # Retrain BC on aggregated dataset
            model = pretrain_ppo_bc(
                model, all_obs, all_act,
                epochs=30, batch_size=512, lr=5e-4
            )
        
        model.save(str(output_dir / 'dagger_model'))
        print(f"  Saved DAgger model to {output_dir / 'dagger_model'}")
    
    # --------------------------------------------------------
    # Step 4: PPO Fine-tuning
    # --------------------------------------------------------
    print(f"\n[4/4] PPO fine-tuning for {args.ppo_steps:,} steps...")
    
    class SpeedProgressCallback(BaseCallback):
        def __init__(self):
            super().__init__()
            self.best_gates = 0
            self.best_time = float('inf')
            self.episode_count = 0
            self.recent_times = []
            
        def _on_step(self):
            for info in self.locals.get('infos', []):
                if 'episode' in info:
                    self.episode_count += 1
                    ep_reward = info['episode']['r']
                    
                    gates = info.get('gates_passed', 0)
                    completion_time = info.get('completion_time', None)
                    
                    if gates > self.best_gates:
                        self.best_gates = gates
                        print(f"\n*** New gate record: {gates} gates! "
                              f"(ep {self.episode_count}) ***")
                    
                    if completion_time and completion_time < self.best_time:
                        self.best_time = completion_time
                        self.recent_times.append(completion_time)
                        print(f"\n*** New speed record: {completion_time:.2f}s! "
                              f"(ep {self.episode_count}) ***")
                    
                    if self.episode_count % 50 == 0:
                        avg_t = np.mean(self.recent_times[-10:]) if self.recent_times else 0
                        print(f"  Ep {self.episode_count}: gates={gates}, "
                              f"reward={ep_reward:.1f}, "
                              f"best_time={self.best_time:.2f}s, "
                              f"recent_avg_time={avg_t:.2f}s")
            return True
    
    callbacks = [
        SpeedProgressCallback(),
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
    
    model.learn(
        total_timesteps=args.ppo_steps,
        callback=callbacks,
        progress_bar=False,
    )
    
    # Save final
    model.save(str(output_dir / 'final_model'))
    print(f"\nFinal model saved to {output_dir / 'final_model'}")
    
    # --------------------------------------------------------
    # Final evaluation
    # --------------------------------------------------------
    print(f"\n{'=' * 60}")
    print("FINAL EVALUATION")
    print(f"{'=' * 60}")
    
    final_env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
    
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
        complete = '✅' if info.get('course_complete') else ''
        print(f"  Episode {ep+1:2d}: {gates:2d}/45 gates | "
              f"{t:6.2f}s | reward={total_reward:8.1f} | "
              f"{'crash=' + crash if crash else ''} {complete}")
    
    train_envs.close()
    eval_env.close()
    
    print(f"\nAll outputs in: {output_dir}")
    print(f"Optimal time: 34.79s | Previous best: 41.1s")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='DAgger + PPO Speed Training')
    parser.add_argument('--skip-bc', action='store_true', help='Skip behavior cloning')
    parser.add_argument('--bc-epochs', type=int, default=150, help='BC training epochs')
    parser.add_argument('--bc-lr', type=float, default=1e-3, help='BC learning rate')
    parser.add_argument('--augment-factor', type=int, default=5, help='Data augmentation multiplier')
    parser.add_argument('--dagger-rounds', type=int, default=5, help='DAgger rounds (0 to skip)')
    parser.add_argument('--dagger-episodes', type=int, default=15, help='Episodes per DAgger round')
    parser.add_argument('--ppo-steps', type=int, default=4_000_000, help='PPO fine-tuning steps')
    parser.add_argument('--n-envs', type=int, default=8, help='Parallel environments')
    parser.add_argument('--seed', type=int, default=42, help='Random seed')
    parser.add_argument('--eval', type=str, default=None, help='Evaluate model path')
    
    args = parser.parse_args()
    
    if args.eval:
        from stable_baselines3 import PPO
        model = PPO.load(args.eval)
        speed_reward = {
            'gate_bonus': 100.0, 'course_complete_bonus': 500.0,
            'progress_scale': 1.0, 'time_penalty': 0.1,
            'crash_penalty': 10.0, 'speed_bonus_scale': 0.15,
        }
        env = make_env('gauntlet', domain_rand=False, reward_config=speed_reward)
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
            print(f"  Ep {ep+1}: {inner.current_gate}/45 gates, "
                  f"{inner.steps * inner.dt:.2f}s")
    else:
        main(args)
