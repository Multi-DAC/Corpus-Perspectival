"""
Imitation Learning from Optimal Trajectory — Behavioral Cloning + DAgger

The optimal trajectory gives us perfect state-action pairs, but open-loop 
replay diverges because quadrotor dynamics are chaotically unstable.

Solution: Train a neural network policy (behavioral cloning) that learns
the mapping state → action, then refine with DAgger (on-policy data 
collection using expert corrections).

Phase 1: Behavioral Cloning (BC)
  - Supervised learning: given state, predict action
  - Fast, simple, gives us a warm start

Phase 2: DAgger (Dataset Aggregation)
  - Run the BC policy in simulation
  - At each step, record what the EXPERT would do (nearest-neighbor lookup)
  - Add these to the dataset and retrain
  - This teaches the policy to recover from its own mistakes

Phase 3: PPO Fine-tuning  
  - Take the BC/DAgger policy as initialization
  - Fine-tune with RL reward (gate passage + speed)
  - This is where it learns to go FASTER than the expert
"""

import os
import sys
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from scipy.spatial import KDTree

sys.path.insert(0, os.path.dirname(__file__))
from drone_env_v2 import DroneRacingEnvV2, QuadParams

# ============================================================
# Neural Network Policy
# ============================================================

class RacingPolicy(nn.Module):
    """
    Maps observation (20-dim) → action (4-dim).
    Architecture: MLP with residual connections.
    """
    def __init__(self, obs_dim=20, act_dim=4, hidden=256):
        super().__init__()
        
        self.input_norm = nn.BatchNorm1d(obs_dim)
        
        self.fc1 = nn.Linear(obs_dim, hidden)
        self.fc2 = nn.Linear(hidden, hidden)
        self.fc3 = nn.Linear(hidden, hidden)
        self.fc4 = nn.Linear(hidden, act_dim)
        
        # Residual projection
        self.res_proj = nn.Linear(obs_dim, hidden)
        
        self.act = nn.ELU()
        self.dropout = nn.Dropout(0.1)
        
        # Initialize output near hover
        nn.init.zeros_(self.fc4.bias)
        nn.init.uniform_(self.fc4.weight, -0.01, 0.01)
    
    def forward(self, x):
        x = self.input_norm(x)
        
        residual = self.res_proj(x)
        
        h = self.act(self.fc1(x))
        h = self.dropout(h)
        h = self.act(self.fc2(h)) + residual
        h = self.dropout(h)
        h = self.act(self.fc3(h))
        
        return torch.tanh(self.fc4(h))  # Actions in [-1, 1]


# ============================================================
# Expert Data Preparation
# ============================================================

def prepare_expert_data(expert_dir, env):
    """
    Convert optimizer trajectory to (observation, action) pairs
    for the env's observation space.
    """
    states = np.load(os.path.join(expert_dir, 'states.npy'))
    actions = np.load(os.path.join(expert_dir, 'actions.npy'))
    times = np.load(os.path.join(expert_dir, 'times.npy'))
    
    params = QuadParams()
    T_min, T_max = params.T_min, params.T_max
    
    # Normalize actions to [-1, 1]
    actions_norm = 2.0 * (actions - T_min) / (T_max - T_min + 1e-8) - 1.0
    actions_norm = np.clip(actions_norm, -1.0, 1.0)
    
    # Build observations matching env format
    # Need to figure out which gate each state is targeting
    gates = [
        np.array([-1.1, -1.6, 3.6]), np.array([9.2, 6.6, 1.0]),
        np.array([9.2, -4.0, 1.2]), np.array([-4.5, -6.0, 3.5]),
        np.array([-4.5, -6.0, 0.8]), np.array([4.75, -0.9, 1.2]),
        np.array([-2.8, 6.8, 1.2]),
    ] * 3
    gates = gates[:19]
    n_gates = len(gates)
    
    # Assign gates to trajectory points by finding closest approach
    gate_assignments = []
    current_gate = 0
    for i in range(len(states)):
        pos = states[i][0:3]
        if current_gate < n_gates:
            dist = np.linalg.norm(pos - gates[current_gate])
            if dist < 0.5:  # Close enough to count as passed
                current_gate += 1
        gate_assignments.append(min(current_gate, n_gates - 1))
    
    # Build observation vectors
    observations = []
    for i in range(len(states)):
        state = states[i]
        gi = gate_assignments[i]
        
        # Relative gate position
        rel_gate = gates[gi] - state[0:3]
        
        # Lookahead gate
        if gi + 1 < n_gates:
            rel_gate_next = gates[gi + 1] - state[0:3]
        else:
            rel_gate_next = rel_gate
        
        # Progress
        progress = np.array([gi / n_gates])
        
        obs = np.concatenate([state, rel_gate, rel_gate_next, progress])
        observations.append(obs)
    
    observations = np.array(observations, dtype=np.float32)
    actions_norm = np.array(actions_norm, dtype=np.float32)
    
    print(f"Expert data: {len(observations)} samples")
    print(f"  Observations: {observations.shape}")
    print(f"  Actions: {actions_norm.shape}")
    print(f"  Gates used: {current_gate}/{n_gates}")
    
    return observations, actions_norm, states


# ============================================================
# Behavioral Cloning
# ============================================================

def train_bc(observations, actions, epochs=200, batch_size=64, lr=3e-4,
             device='cpu', augment=True):
    """Train behavioral cloning policy."""
    
    policy = RacingPolicy().to(device)
    optimizer = optim.AdamW(policy.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    # Data augmentation: add noise to create more diverse training data
    if augment:
        n_augment = 5
        aug_obs = [observations]
        aug_act = [actions]
        
        for _ in range(n_augment):
            noise_obs = observations.copy()
            # Add noise to position (dims 0-2)
            noise_obs[:, 0:3] += np.random.normal(0, 0.2, size=(len(observations), 3)).astype(np.float32)
            # Add noise to velocity (dims 3-5) 
            noise_obs[:, 3:6] += np.random.normal(0, 0.3, size=(len(observations), 3)).astype(np.float32)
            # Recompute relative gate positions (dims 13-18) based on noisy position
            noise_obs[:, 13:16] = observations[:, 13:16] - (noise_obs[:, 0:3] - observations[:, 0:3])
            noise_obs[:, 16:19] = observations[:, 16:19] - (noise_obs[:, 0:3] - observations[:, 0:3])
            
            aug_obs.append(noise_obs)
            aug_act.append(actions)  # Same actions (approximately correct for small noise)
        
        observations = np.concatenate(aug_obs)
        actions = np.concatenate(aug_act)
        print(f"Augmented: {len(observations)} samples ({n_augment}x noise)")
    
    # Create dataset
    X = torch.FloatTensor(observations).to(device)
    Y = torch.FloatTensor(actions).to(device)
    dataset = TensorDataset(X, Y)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    print(f"\nTraining Behavioral Cloning...")
    print(f"  Epochs: {epochs}, Batch size: {batch_size}, LR: {lr}")
    
    best_loss = float('inf')
    best_state = None
    
    for epoch in range(epochs):
        policy.train()
        total_loss = 0
        n_batches = 0
        
        for obs_batch, act_batch in loader:
            pred = policy(obs_batch)
            loss = nn.MSELoss()(pred, act_batch)
            
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
            optimizer.step()
            
            total_loss += loss.item()
            n_batches += 1
        
        scheduler.step()
        avg_loss = total_loss / n_batches
        
        if avg_loss < best_loss:
            best_loss = avg_loss
            best_state = {k: v.cpu().clone() for k, v in policy.state_dict().items()}
        
        if (epoch + 1) % 20 == 0 or epoch == 0:
            print(f"  Epoch {epoch+1:4d}/{epochs}: loss={avg_loss:.6f} (best={best_loss:.6f})")
    
    # Load best
    policy.load_state_dict(best_state)
    policy.eval()
    
    return policy


# ============================================================
# DAgger (Dataset Aggregation)
# ============================================================

def run_dagger(policy, expert_states, expert_actions_norm, env, 
               n_rounds=10, n_episodes=20, max_steps=1600, device='cpu'):
    """
    DAgger: Run policy, query expert for corrections, retrain.
    
    For expert queries, we use nearest-neighbor in state space
    since we can't call the optimizer in real-time.
    """
    
    # Build KD-tree on expert state positions for fast lookup
    expert_positions = expert_states[:, 0:6]  # pos + vel for matching
    kdtree = KDTree(expert_positions)
    
    # Starting dataset from expert
    all_obs = []
    all_act = []
    
    params = QuadParams()
    T_min, T_max = params.T_min, params.T_max
    
    gates = [
        np.array([-1.1, -1.6, 3.6]), np.array([9.2, 6.6, 1.0]),
        np.array([9.2, -4.0, 1.2]), np.array([-4.5, -6.0, 3.5]),
        np.array([-4.5, -6.0, 0.8]), np.array([4.75, -0.9, 1.2]),
        np.array([-2.8, 6.8, 1.2]),
    ] * 3
    gates = gates[:19]
    
    for round_i in range(n_rounds):
        round_obs = []
        round_act = []
        round_gates = []
        round_crashes = 0
        
        for ep in range(n_episodes):
            obs, _ = env.reset()
            
            for step in range(max_steps):
                # Policy predicts action
                with torch.no_grad():
                    obs_t = torch.FloatTensor(obs).unsqueeze(0).to(device)
                    action = policy(obs_t).cpu().numpy().flatten()
                
                # Expert query: what would the expert do from this state?
                state_query = env.state[0:6]  # pos + vel
                _, idx = kdtree.query(state_query)
                expert_action = expert_actions_norm[min(idx, len(expert_actions_norm)-1)]
                
                # Record (observation, expert_action) pair
                round_obs.append(obs.copy())
                round_act.append(expert_action.copy())
                
                # Step with POLICY action (not expert)
                obs, reward, terminated, truncated, info = env.step(action)
                
                if terminated or truncated:
                    if 'crash' in info:
                        round_crashes += 1
                    if 'gate_passed' in info:
                        pass
                    break
            
            if ep < n_episodes - 1:
                round_gates.append(env.current_gate)
        
        round_gates.append(env.current_gate)
        
        # Add to dataset
        all_obs.extend(round_obs)
        all_act.extend(round_act)
        
        avg_gates = np.mean(round_gates) if round_gates else 0
        
        print(f"  DAgger round {round_i+1}/{n_rounds}: "
              f"{len(round_obs)} new samples, "
              f"avg gates={avg_gates:.1f}/19, "
              f"crashes={round_crashes}/{n_episodes}")
        
        # Retrain policy on aggregated dataset
        all_obs_np = np.array(all_obs, dtype=np.float32)
        all_act_np = np.array(all_act, dtype=np.float32)
        
        # Quick retrain (fewer epochs for DAgger rounds)
        X = torch.FloatTensor(all_obs_np).to(device)
        Y = torch.FloatTensor(all_act_np).to(device)
        dataset = TensorDataset(X, Y)
        loader = DataLoader(dataset, batch_size=128, shuffle=True)
        
        optimizer = optim.AdamW(policy.parameters(), lr=1e-4, weight_decay=1e-4)
        
        policy.train()
        for epoch in range(30):
            for obs_batch, act_batch in loader:
                pred = policy(obs_batch)
                loss = nn.MSELoss()(pred, act_batch)
                optimizer.zero_grad()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(policy.parameters(), 1.0)
                optimizer.step()
        policy.eval()
    
    return policy


# ============================================================
# Evaluation
# ============================================================

def evaluate_policy(policy, env, n_episodes=10, device='cpu', verbose=True):
    """Evaluate policy in the environment."""
    results = []
    
    for ep in range(n_episodes):
        obs, _ = env.reset()
        total_reward = 0
        
        for step in range(2000):
            with torch.no_grad():
                obs_t = torch.FloatTensor(obs).unsqueeze(0).to(device)
                action = policy(obs_t).cpu().numpy().flatten()
            
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            if terminated or truncated:
                break
        
        stats = env.get_stats()
        stats['total_reward'] = total_reward
        results.append(stats)
        
        if verbose:
            crash = info.get('crash', 'none')
            complete = '✓' if info.get('course_complete') else ''
            print(f"  Ep {ep+1}: gates={stats['gates_passed']}/19, "
                  f"time={stats['time']:.1f}s, reward={total_reward:.1f}, "
                  f"crash={crash} {complete}")
    
    avg_gates = np.mean([r['gates_passed'] for r in results])
    completions = sum(1 for r in results if r['gates_passed'] == 19)
    avg_reward = np.mean([r['total_reward'] for r in results])
    
    print(f"\n  Summary: gates={avg_gates:.1f}/19, "
          f"completions={completions}/{n_episodes}, "
          f"avg_reward={avg_reward:.1f}")
    
    return results


# ============================================================
# Main Pipeline
# ============================================================

def main():
    print("=" * 60)
    print("Imitation Learning Pipeline")
    print("Optimal Trajectory -> Neural Network Policy")
    print("=" * 60)
    
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")
    if device == 'cuda':
        print(f"GPU: {torch.cuda.get_device_name(0)}")
    
    expert_dir = os.path.join(os.path.dirname(__file__), '..', 'expert_trajectory')
    save_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
    os.makedirs(save_dir, exist_ok=True)
    
    # Phase 1: Prepare expert data
    print("\n" + "=" * 60)
    print("PHASE 1: Prepare Expert Data")
    print("=" * 60)
    
    env = DroneRacingEnvV2(dt=0.02, substeps=4)
    observations, actions_norm, expert_states = prepare_expert_data(expert_dir, env)
    
    # Phase 2: Behavioral Cloning
    print("\n" + "=" * 60)
    print("PHASE 2: Behavioral Cloning")
    print("=" * 60)
    
    t0 = time.time()
    policy = train_bc(observations, actions_norm, epochs=200, batch_size=64,
                      lr=3e-4, device=device, augment=True)
    bc_time = time.time() - t0
    print(f"\nBC training: {bc_time:.1f}s")
    
    # Save BC model
    torch.save(policy.state_dict(), os.path.join(save_dir, 'policy_bc.pt'))
    
    # Evaluate BC
    print("\nEvaluating BC policy:")
    evaluate_policy(policy, env, n_episodes=5, device=device)
    
    # Phase 3: DAgger
    print("\n" + "=" * 60)
    print("PHASE 3: DAgger Refinement")
    print("=" * 60)
    
    t0 = time.time()
    policy = run_dagger(
        policy, expert_states, actions_norm, env,
        n_rounds=10, n_episodes=20, max_steps=1600, device=device,
    )
    dagger_time = time.time() - t0
    print(f"\nDAgger training: {dagger_time:.1f}s")
    
    # Save DAgger model
    torch.save(policy.state_dict(), os.path.join(save_dir, 'policy_dagger.pt'))
    
    # Evaluate DAgger
    print("\nEvaluating DAgger policy:")
    evaluate_policy(policy, env, n_episodes=10, device=device)
    
    # Phase 4: PPO Fine-tuning
    print("\n" + "=" * 60)
    print("PHASE 4: PPO Fine-tuning")
    print("=" * 60)
    
    try:
        from stable_baselines3 import PPO
        from stable_baselines3.common.vec_env import DummyVecEnv
        
        # Create vectorized env
        vec_env = DummyVecEnv([lambda: DroneRacingEnvV2(
            domain_randomization=True, domain_rand_scale=0.05
        ) for _ in range(8)])
        
        # Initialize PPO with our pretrained policy weights
        ppo = PPO(
            "MlpPolicy", vec_env,
            learning_rate=1e-4,
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.995,
            ent_coef=0.005,
            verbose=1,
            device=device,
            policy_kwargs=dict(
                net_arch=dict(pi=[256, 256], vf=[256, 256]),
            ),
        )
        
        # TODO: Transfer weights from our BC/DAgger policy to PPO's policy network
        # For now, train from scratch with the reward shaping
        
        print("Training PPO (500K steps)...")
        t0 = time.time()
        ppo.learn(total_timesteps=500_000)
        ppo_time = time.time() - t0
        print(f"PPO training: {ppo_time:.1f}s")
        
        ppo.save(os.path.join(save_dir, 'ppo_v2'))
        
        # Evaluate
        print("\nEvaluating PPO policy:")
        eval_env = DroneRacingEnvV2()
        results = []
        for ep in range(10):
            obs, _ = eval_env.reset()
            done = False
            while not done:
                action, _ = ppo.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = eval_env.step(action)
                done = terminated or truncated
            stats = eval_env.get_stats()
            results.append(stats)
            crash = info.get('crash', 'none')
            print(f"  Ep {ep+1}: gates={stats['gates_passed']}/19, "
                  f"time={stats['time']:.1f}s, crash={crash}")
        
        avg_gates = np.mean([r['gates_passed'] for r in results])
        print(f"\n  PPO avg gates: {avg_gates:.1f}/19")
        
    except ImportError:
        print("stable_baselines3 not available, skipping PPO phase")
    
    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)
    print(f"Models saved to: {save_dir}/")
    print(f"  policy_bc.pt     — Behavioral Cloning")
    print(f"  policy_dagger.pt — DAgger refined")
    if os.path.exists(os.path.join(save_dir, 'ppo_v2.zip')):
        print(f"  ppo_v2.zip       — PPO fine-tuned")


if __name__ == "__main__":
    main()
