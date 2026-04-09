"""Quick eval of Anakin model"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from stable_baselines3 import PPO
from stable_baselines3.common.evaluation import evaluate_policy
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.monitor import Monitor
from infinite_gate_env import InfiniteGateEnv

# Load model
ckpt = r"runs\infinite_1771139042\checkpoints\ppo_infinite_14000000_steps.zip"
print(f"Loading: {ckpt}")
model = PPO.load(ckpt)

# Eval on InfiniteGateEnv
print("\nEvaluating on Infinite Gate Environment...")
env = DummyVecEnv([lambda: Monitor(InfiniteGateEnv())])
mean_r, std_r = evaluate_policy(model, env, n_eval_episodes=10, deterministic=True)
print(f"Infinite Gate: {mean_r:.1f} +/- {std_r:.1f}")

# Check maneuver stats
print("\nManeuver Stats from recent episodes:")
test_env = InfiniteGateEnv()
obs, _ = test_env.reset()

for episode in range(20):
    done = False
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, truncated, info = test_env.step(action)
        done = done or truncated

stats = test_env.get_maneuver_stats()
for m, s in sorted(stats.items()):
    if s['attempts'] > 0:
        rate = s['successes'] / s['attempts']
        bar = '#' * int(rate * 20)
        print(f"  {m:15s}: {rate:5.1%} [{bar:20s}] ({s['successes']}/{s['attempts']})")

env.close()