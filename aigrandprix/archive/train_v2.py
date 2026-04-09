"""Continue training from v1 checkpoint with more exploration."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from drone_env import DroneRacingEnv

env = make_vec_env(DroneRacingEnv, n_envs=4, env_kwargs={"max_steps": 500})

# Load previous model and continue training with higher entropy
model = PPO.load("drone_ppo_v1", env=env)
model.ent_coef = 0.02  # More exploration

print("Continuing training from 200K checkpoint...")
print("Entropy coef increased to 0.02 for more exploration")
print("Training 300K more steps (500K total)...")
model.learn(total_timesteps=300_000)
model.save("drone_ppo_v2")
print("Saved drone_ppo_v2")

# Test
print("\nTesting v2 agent:")
test_env = DroneRacingEnv(max_steps=1000)
for ep in range(5):
    obs, _ = test_env.reset()
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = test_env.step(action)
        done = terminated or truncated
    stats = test_env.get_stats()
    g = stats["gates_passed"]
    s = stats["steps"]
    r = stats["total_reward"]
    print(f"  Ep {ep+1}: Gates {g}/5 | Steps {s} | Reward {r:.1f}")
