"""Debug: why are gates not being passed with 0.8m radius?"""
import sys
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\tracks")
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\sim")

from drone_env_v2 import DroneRacingEnvV2
from course_corkscrew import COURSE
from stable_baselines3 import PPO
import numpy as np

gates = [g["pos"] for g in COURSE["gates"]]
env = DroneRacingEnvV2(gates=gates, max_steps=2000, gate_radius=0.8)
obs, _ = env.reset()
print(f"gate_radius: {env.gate_radius}")
print(f"n_gates: {env.n_gates}")
print(f"First gate: {env.gates[0]}")
print(f"Start pos: {env.state[:3]}")
print(f"Dist to gate 0: {env._dist_to_gate(0):.2f}")

# Load the model being trained
import glob
runs = sorted(glob.glob("sim/runs/multicourse_177078*"))
if runs:
    latest = runs[-1]
    best = f"{latest}/best/best_model.zip"
    print(f"\nLoading model: {best}")
    model = PPO.load(best, device="cpu")
    
    obs, _ = env.reset()
    min_dist = 999
    for i in range(2000):
        action, _ = model.predict(obs, deterministic=True)
        obs, r, term, trunc, info = env.step(action)
        if env.current_gate < env.n_gates:
            d = env._dist_to_gate(env.current_gate)
            if d < min_dist:
                min_dist = d
        if i % 100 == 0:
            cg = env.current_gate
            d = env._dist_to_gate(cg) if cg < env.n_gates else -1
            print(f"Step {i}: pos={env.state[:3].round(2)}, gate={cg}, dist={d:.2f}, min_dist_ever={min_dist:.2f}")
        if term or trunc:
            print(f"Ended at step {i}, gates_passed={env.current_gate}, min_dist={min_dist:.2f}")
            break
else:
    print("No model found yet")
