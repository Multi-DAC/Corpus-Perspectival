"""Diagnose why the agent gets stuck after gate 2."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from stable_baselines3 import PPO
from drone_env import DroneRacingEnv

model = PPO.load("drone_ppo_v2")
env = DroneRacingEnv(max_steps=1000)

obs, _ = env.reset()
done = False
step = 0

print("Gate positions:")
for i, g in enumerate(env.gates):
    print(f"  Gate {i+1}: [{g[0]:.0f}, {g[1]:.0f}, {g[2]:.0f}]")
print()

print("Step-by-step flight log:")
print(f"{'Step':>5} | {'X':>6} {'Y':>6} {'Z':>6} | {'Vx':>6} {'Vy':>6} {'Vz':>6} | {'Gate':>4} | {'Reward':>7} | Notes")
print("-" * 90)

while not done:
    action, _ = model.predict(obs, deterministic=True)
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    step += 1
    
    x, y, z = env.state[0:3]
    vx, vy, vz = env.state[3:6]
    
    notes = ""
    if "gate_passed" in info:
        notes = f"** GATE {info['gate_passed']} PASSED **"
    if "crash" in info:
        notes = f"CRASH: {info['crash']}"
    if "course_complete" in info:
        notes = "COURSE COMPLETE!"
    
    # Print every 10 steps, plus gate events and final
    if step % 10 == 0 or notes or done:
        print(f"{step:>5} | {x:>6.1f} {y:>6.1f} {z:>6.1f} | {vx:>6.1f} {vy:>6.1f} {vz:>6.1f} | {env.current_gate:>4} | {reward:>7.2f} | {notes}")

print()
print(f"Final: gate {env.current_gate}/5, step {step}, terminated={terminated}, truncated={truncated}")
stats = env.get_stats()
print(f"Speed: {stats['velocity']:.1f} m/s, Total reward: {stats['total_reward']:.1f}")
