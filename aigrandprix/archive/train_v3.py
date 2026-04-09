"""Fresh training with wider gates and 500K steps."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from drone_env import DroneRacingEnv

env = make_vec_env(DroneRacingEnv, n_envs=4, env_kwargs={"max_steps": 500})

model = PPO(
    "MlpPolicy", env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=64,
    n_epochs=10,
    gamma=0.99,
    gae_lambda=0.95,
    clip_range=0.2,
    ent_coef=0.01,
    verbose=0,
    device="auto",
)

print("Training v3 from scratch — wider gates (1.5m radius)")
print("500K steps, 4 parallel envs...")
t0 = time.time()
model.learn(total_timesteps=500_000)
elapsed = time.time() - t0
print(f"Done in {elapsed:.0f}s")
model.save("drone_ppo_v3")

# Test
print("\nTesting v3:")
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
    v = stats["velocity"]
    print(f"  Ep {ep+1}: Gates {g}/5 | Steps {s} | Reward {r:.1f} | Speed {v:.1f} m/s")
