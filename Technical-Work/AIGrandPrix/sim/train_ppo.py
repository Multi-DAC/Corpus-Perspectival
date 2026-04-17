"""
First PPO training run — teach a drone to fly through gates.

This is our "hello world" of drone RL. The goal isn't perfection,
it's proving the loop works: environment → training → improvement.

Uses Stable Baselines3 PPO with our custom DroneRacingEnv.
"""

import time
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import BaseCallback
from drone_env import DroneRacingEnv


class ProgressCallback(BaseCallback):
    """Print training progress every N steps."""
    
    def __init__(self, print_freq=5000, verbose=0):
        super().__init__(verbose)
        self.print_freq = print_freq
        self.episode_rewards = []
        self.episode_gates = []
    
    def _on_step(self) -> bool:
        # Collect episode info
        for info in self.locals.get("infos", []):
            if "episode" in info:
                self.episode_rewards.append(info["episode"]["r"])
            if "gate_passed" in info:
                self.episode_gates.append(info["gate_passed"])
        
        if self.num_timesteps % self.print_freq == 0:
            # Get recent stats from the environment
            mean_reward = 0
            if len(self.episode_rewards) > 0:
                recent = self.episode_rewards[-20:]
                mean_reward = sum(recent) / len(recent)
                
            gates_info = ""
            if len(self.episode_gates) > 0:
                max_gate = max(self.episode_gates[-50:]) if self.episode_gates else 0
                gates_info = f" | Best gate: {max_gate}"
            
            print(f"  Step {self.num_timesteps:>7d} | "
                  f"Mean reward (last 20): {mean_reward:>8.1f}{gates_info}")
        
        return True


def train(total_timesteps=100_000, save_path="drone_ppo_v1"):
    """Train a PPO agent on the drone racing environment."""
    
    print("=" * 60)
    print("PPO Training — Drone Racing")
    print("=" * 60)
    
    # Create vectorized environment (4 parallel envs for faster training)
    env = make_vec_env(
        DroneRacingEnv,
        n_envs=4,
        env_kwargs={
            "max_steps": 500,  # Shorter episodes for faster learning
        }
    )
    
    print(f"Environment: DroneRacingEnv (4 parallel)")
    print(f"Total timesteps: {total_timesteps:,}")
    print()
    
    # PPO with standard hyperparameters
    # These are reasonable defaults — we'll tune later
    model = PPO(
        "MlpPolicy",
        env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        ent_coef=0.01,      # Entropy bonus for exploration
        vf_coef=0.5,
        max_grad_norm=0.5,
        verbose=0,
        device="auto",       # Will use CUDA if available
        # tensorboard_log="./tb_logs/",  # Enable when tensorboard is installed
    )
    
    print(f"Policy network: {model.policy.__class__.__name__}")
    print(f"Device: {model.device}")
    print()
    print("Training...")
    print("-" * 60)
    
    start_time = time.time()
    
    callback = ProgressCallback(print_freq=10_000)
    model.learn(
        total_timesteps=total_timesteps,
        callback=callback,
        progress_bar=False,
    )
    
    elapsed = time.time() - start_time
    print("-" * 60)
    print(f"Training complete! {elapsed:.1f}s ({total_timesteps/elapsed:.0f} steps/sec)")
    
    # Save model
    model.save(save_path)
    print(f"Model saved: {save_path}")
    
    # Test the trained agent
    print()
    print("=" * 60)
    print("Testing trained agent...")
    print("=" * 60)
    
    test_env = DroneRacingEnv(max_steps=1000)
    
    results = []
    for ep in range(10):
        obs, _ = test_env.reset()
        total_reward = 0
        done = False
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = test_env.step(action)
            total_reward += reward
            done = terminated or truncated
        
        stats = test_env.get_stats()
        results.append(stats)
        gates = stats["gates_passed"]
        steps = stats["steps"]
        print(f"  Episode {ep+1:>2d}: Gates {gates}/{stats['total_gates']} | "
              f"Steps {steps:>4d} | Reward {total_reward:>8.1f} | "
              f"Speed {stats['velocity']:.1f} m/s")
    
    # Summary
    avg_gates = sum(r["gates_passed"] for r in results) / len(results)
    max_gates = max(r["gates_passed"] for r in results)
    completions = sum(1 for r in results if r["gates_passed"] == results[0]["total_gates"])
    
    print()
    print(f"Results over 10 episodes:")
    print(f"  Average gates passed: {avg_gates:.1f}/5")
    print(f"  Best gates passed: {max_gates}/5")
    print(f"  Course completions: {completions}/10")
    print()
    
    if avg_gates > 0:
        print("The agent is learning! It's passing gates!")
    else:
        print("Agent hasn't learned to pass gates yet. Need more training or reward tuning.")
    
    return model


if __name__ == "__main__":
    import sys
    
    steps = 100_000  # Default
    if len(sys.argv) > 1:
        steps = int(sys.argv[1])
    
    train(total_timesteps=steps)
