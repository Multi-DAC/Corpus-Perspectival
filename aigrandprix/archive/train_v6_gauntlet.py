"""
v6: Train on Clayton's 45-Gate Gauntlet with curriculum learning + GPU

Strategy:
1. Train on each section individually (4-6 gates, achievable chunks)
2. Chain sections progressively (1+2, then 1+2+3, etc.)
3. Full 45-gate gauntlet as final test

Uses CUDA if available for faster training.
"""
import sys
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\tracks")
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import numpy as np
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from drone_env import DroneRacingEnv

from clayton_master_course import MASTER_COURSE, SECTIONS, get_gates

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")


# === Extended environment for the gauntlet ===
class GauntletEnv(DroneRacingEnv):
    """
    Extended drone env for the 45-gate gauntlet.
    - Expanded bounds (course goes to X=70, Y=-12..6, Z=1..20)
    - Longer episodes for more gates
    - Adaptive start position (can start at any section)
    """
    
    def __init__(self, gates=None, max_steps=2000, section_indices=None):
        all_gates = get_gates().tolist()
        
        if section_indices is not None:
            # Use specific section gates
            selected = [all_gates[i] for i in section_indices]
        elif gates is not None:
            selected = gates
        else:
            selected = all_gates
        
        super().__init__(gates=selected, max_steps=max_steps)
        
        # Expand bounds for the gauntlet
        self.x_bound = 80
        self.y_bound = 30
        self.z_ceiling = 25
    
    def reset(self, seed=None, options=None):
        obs, info = super().reset(seed=seed, options=options)
        
        # Start near first gate of this section
        if len(self.gates) > 0:
            start = self.gates[0].copy()
            # Offset slightly behind the first gate
            direction = np.zeros(3)
            if len(self.gates) > 1:
                direction = self.gates[1] - self.gates[0]
                direction = direction / (np.linalg.norm(direction) + 1e-6)
            self.state[:3] = start - direction * 3.0  # 3m behind first gate
            self.state[2] = max(self.state[2], 1.0)   # Don't start underground
            self.state[3:] = 0.0  # Zero velocity/angles
            
            self.prev_dist_to_gate = np.linalg.norm(
                self.gates[0] - self.state[:3]
            )
        
        return self._get_obs(), {}
    
    def step(self, action):
        obs, reward, terminated, truncated, info = super().step(action)
        
        # Override bounds check for expanded course
        x, y, z = self.state[:3]
        
        # Reset termination flags from parent (which used tighter bounds)
        if info.get("crash") == "out_of_bounds":
            # Re-check with expanded bounds
            if abs(x) <= self.x_bound and abs(y) <= self.y_bound:
                terminated = False
                reward += 10.0  # Undo the penalty from parent
                info.pop("crash", None)
        
        if info.get("crash") == "ceiling":
            if z <= self.z_ceiling:
                terminated = False
                reward += 10.0
                info.pop("crash", None)
        
        return obs, reward, terminated, truncated, info


class GauntletRandomEnv(GauntletEnv):
    """Gauntlet env with domain randomization."""
    
    def __init__(self, section_indices=None, max_steps=2000):
        super().__init__(section_indices=section_indices, max_steps=max_steps)
    
    def reset(self, seed=None, options=None):
        # Domain randomization
        self.mass = 0.5 * np.random.uniform(0.9, 1.1)
        self.drag_coeff = 0.1 * np.random.uniform(0.8, 1.2)
        self.max_thrust = 15.0 * np.random.uniform(0.95, 1.05)
        return super().reset(seed=seed, options=options)


def train_section(section_name, section_indices, total_steps=500_000, 
                  model=None, n_envs=8):
    """Train on a specific section of the gauntlet."""
    n_gates = len(section_indices)
    max_steps = max(500, n_gates * 150)  # Scale episode length with gates
    
    env = DummyVecEnv([
        lambda si=section_indices, ms=max_steps: GauntletRandomEnv(section_indices=si, max_steps=ms)
        for _ in range(n_envs)
    ])
    
    policy_kwargs = dict(
        net_arch=dict(pi=[256, 256], vf=[256, 256])  # Bigger network for complex course
    )
    
    if model is None:
        model = PPO(
            "MlpPolicy", env,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.99,
            ent_coef=0.01,
            verbose=1,
            policy_kwargs=policy_kwargs,
            device="cpu",  # MLP policy runs faster on CPU (no CNN)
        )
    else:
        model.set_env(env)
    
    print(f"\n{'='*60}")
    print(f"Training: {section_name} ({n_gates} gates, {total_steps//1000}K steps)")
    print(f"{'='*60}")
    
    t0 = time.time()
    model.learn(total_timesteps=total_steps)
    elapsed = time.time() - t0
    sps = total_steps / elapsed
    print(f"Done in {elapsed:.0f}s ({sps:.0f} steps/sec)")
    
    return model


def test_section(model, section_name, section_indices, n_episodes=5):
    """Test model on a section."""
    all_gates = get_gates().tolist()
    selected = [all_gates[i] for i in section_indices]
    n_gates = len(selected)
    max_steps = max(500, n_gates * 150)
    
    results = []
    for ep in range(n_episodes):
        env = GauntletEnv(gates=selected, max_steps=max_steps)
        obs, _ = env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            done = terminated or truncated
        stats = env.get_stats()
        results.append(stats)
    
    avg_g = sum(r["gates_passed"] for r in results) / n_episodes
    comps = sum(1 for r in results if r["gates_passed"] == n_gates)
    avg_r = sum(r["total_reward"] for r in results) / n_episodes
    
    print(f"  {section_name:>20s}: Gates {avg_g:.1f}/{n_gates} | "
          f"Complete {comps}/{n_episodes} | Reward {avg_r:.1f}")
    
    return {"name": section_name, "avg_gates": avg_g, "completions": comps, 
            "avg_reward": avg_r, "total_gates": n_gates}


def main():
    print("=" * 60)
    print("v6: Clayton's Gauntlet — Curriculum Training")
    print(f"45 gates | 9 sections | Device: {device}")
    print("=" * 60)
    
    all_gates = get_gates()
    print(f"\nCourse bounds: X[{all_gates[:,0].min():.0f}-{all_gates[:,0].max():.0f}] "
          f"Y[{all_gates[:,1].min():.0f}-{all_gates[:,1].max():.0f}] "
          f"Z[{all_gates[:,2].min():.0f}-{all_gates[:,2].max():.0f}]")
    
    section_order = [
        "opening_sprint",      # 4 gates — easiest
        "speed_section",       # 4 gates — sprints
        "vertical_challenge",  # 4 gates — up/down
        "technical_middle",    # 6 gates — S-curves/loops
        "punishment_zone",     # 6 gates — hard
        "power_section",       # 5 gates — verticals
        "death_run",           # 6 gates — everything
        "hybrid_combos",       # 5 gates — multi-maneuver
        "final_gauntlet",      # 5 gates — ultimate
    ]
    
    # Phase 1: Train on each section individually
    print("\n" + "=" * 60)
    print("PHASE 1: Individual Section Training")
    print("=" * 60)
    
    section_models = {}
    for name in section_order:
        indices = SECTIONS[name]
        model = train_section(name, indices, total_steps=300_000, n_envs=8)
        section_models[name] = model
        test_section(model, name, indices)
        
        save_path = f"gauntlet_{name}"
        model.save(save_path)
    
    # Phase 2: Progressive chaining
    print("\n" + "=" * 60)
    print("PHASE 2: Progressive Chaining")
    print("=" * 60)
    
    # Start from the opening_sprint model and progressively add sections
    chain_model = None
    chain_indices = []
    
    for i, name in enumerate(section_order):
        chain_indices.extend(SECTIONS[name])
        n_gates = len(chain_indices)
        
        steps = min(500_000, 200_000 + n_gates * 20_000)  # More steps for more gates
        
        chain_model = train_section(
            f"chain_{i+1}_{name}", 
            chain_indices, 
            total_steps=steps,
            model=chain_model
        )
        
        test_section(chain_model, f"chain_1-{i+1}", chain_indices)
    
    # Save final chained model
    chain_model.save("gauntlet_full_chain")
    
    # Phase 3: Full gauntlet test
    print("\n" + "=" * 60)
    print("PHASE 3: Full Gauntlet Test")
    print("=" * 60)
    
    all_indices = list(range(45))
    full_results = test_section(chain_model, "FULL GAUNTLET", all_indices, n_episodes=10)
    
    # Also test each section with the final model
    print("\nSection breakdown with final model:")
    for name in section_order:
        test_section(chain_model, name, SECTIONS[name])
    
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print(f"Full gauntlet: {full_results['avg_gates']:.1f}/45 gates, "
          f"{full_results['completions']}/10 completions")
    print("=" * 60)


if __name__ == "__main__":
    main()
