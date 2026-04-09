"""Fixed eval — uses env.current_gate instead of broken info key."""
import sys
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\tracks")
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\sim")

from drone_env_v2 import DroneRacingEnvV2
from stable_baselines3 import PPO
import numpy as np

from course_corkscrew import COURSE as CORKSCREW
from course_whiplash import COURSE as WHIPLASH
from course_elevator_shaft import COURSE as ELEVATOR
from course_claustrophobia import COURSE as CLAUSTRO
from course_autobahn import COURSE as AUTOBAHN
from course_gauntlet_jr import COURSE as GAUNTLET_JR
from course_final_exam import COURSE as FINAL_EXAM
from clayton_master_course import MASTER_COURSE

ALL = [CORKSCREW, WHIPLASH, ELEVATOR, CLAUSTRO, AUTOBAHN, GAUNTLET_JR, FINAL_EXAM, MASTER_COURSE]

model = PPO.load("sim/runs/multicourse_1770781551/best/best_model.zip", device="cpu")
print("Model loaded. Evaluating all 8 courses (5 eps each, gate_radius=0.8):\n")

for course in ALL:
    name = course.get("name", "Unknown")
    gates_def = [g["pos"] for g in course["gates"]]
    n_gates = len(gates_def)
    max_steps = max(1500, n_gates * 60)
    
    gate_results = []
    reward_results = []
    for ep in range(5):
        env = DroneRacingEnvV2(gates=gates_def, max_steps=max_steps, gate_radius=0.8)
        obs, _ = env.reset()
        total_reward = 0
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, r, term, trunc, info = env.step(action)
            total_reward += r
            done = term or trunc
        gate_results.append(env.current_gate)
        reward_results.append(total_reward)
    
    avg_g = np.mean(gate_results)
    best_g = max(gate_results)
    avg_r = np.mean(reward_results)
    pct = (avg_g / n_gates) * 100
    print(f"  {name:25s} | gates: {avg_g:.1f}/{n_gates} ({pct:.0f}%) best={best_g} | reward: {avg_r:.1f}")
