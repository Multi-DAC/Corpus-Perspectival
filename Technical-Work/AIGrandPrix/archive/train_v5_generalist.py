"""
v5: Train a GENERALIST agent on randomized courses.
Each episode = random course + random physics.
This is how you build robustness.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from drone_env import DroneRacingEnv
from drone_env_random import RandomCourseEnv, COURSES

print("=" * 60)
print("v5: Generalist agent — randomized courses + physics")
print(f"Course library: {len(COURSES)} courses")
print("=" * 60)

# Bigger network for more capacity
policy_kwargs = dict(
    net_arch=dict(pi=[128, 128], vf=[128, 128])  # Bigger than default 64,64
)

env = make_vec_env(RandomCourseEnv, n_envs=4, env_kwargs={"max_steps": 500})

model = PPO(
    "MlpPolicy", env,
    learning_rate=3e-4,
    n_steps=2048,
    batch_size=128,
    n_epochs=10,
    gamma=0.99,
    ent_coef=0.015,  # Slightly more exploration for diverse courses
    verbose=0,
    policy_kwargs=policy_kwargs,
)

print(f"Network: pi=[128,128], vf=[128,128]")
print(f"Training 1M steps...")
t0 = time.time()
model.learn(total_timesteps=1_000_000)
elapsed = time.time() - t0
print(f"Done in {elapsed:.0f}s ({1_000_000/elapsed:.0f} steps/sec)")
model.save("drone_ppo_v5_generalist")

# Test on each course individually
print("\nTesting on all courses:")
total_completions = 0
total_gates = 0
for i, course in enumerate(COURSES):
    test_env = DroneRacingEnv(gates=course, max_steps=1000)
    results = []
    for ep in range(5):
        obs, _ = test_env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = test_env.step(action)
            done = terminated or truncated
        stats = test_env.get_stats()
        results.append(stats)
    
    avg_g = sum(r["gates_passed"] for r in results) / 5
    comps = sum(1 for r in results if r["gates_passed"] == len(course))
    avg_r = sum(r["total_reward"] for r in results) / 5
    total_completions += comps
    total_gates += sum(r["gates_passed"] for r in results)
    name = ["easy", "zigzag", "climb", "tight", "s-curve", "descend", "wide", "sprint"][i]
    print(f"  {name:>8s}: Gates {avg_g:.1f}/5 | Complete {comps}/5 | Reward {avg_r:.1f}")

print(f"\nOverall: {total_completions}/{len(COURSES)*5} completions, {total_gates}/{len(COURSES)*25} gates")
