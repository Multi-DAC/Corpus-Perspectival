"""v5b: Continue v5 generalist training for 2M more steps (3M total)."""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from drone_env import DroneRacingEnv
from drone_env_random import RandomCourseEnv, COURSES

env = make_vec_env(RandomCourseEnv, n_envs=4, env_kwargs={"max_steps": 500})
model = PPO.load("drone_ppo_v5_generalist", env=env)

print("Continuing v5 generalist: +2M steps (3M total)...")
t0 = time.time()
model.learn(total_timesteps=2_000_000)
elapsed = time.time() - t0
print(f"Done in {elapsed:.0f}s")
model.save("drone_ppo_v5b_generalist")

# Test
print("\nTesting v5b on all courses:")
total_comp = 0
total_gates = 0
names = ["easy", "zigzag", "climb", "tight", "s-curve", "descend", "wide", "sprint"]
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
    total_comp += comps
    total_gates += sum(r["gates_passed"] for r in results)
    print(f"  {names[i]:>8s}: Gates {avg_g:.1f}/5 | Complete {comps}/5 | Reward {avg_r:.1f}")

print(f"\nOverall: {total_comp}/{len(COURSES)*5} completions, {total_gates}/{len(COURSES)*25} gates")
pct = total_gates / (len(COURSES)*25) * 100
print(f"Gate pass rate: {pct:.0f}%")
