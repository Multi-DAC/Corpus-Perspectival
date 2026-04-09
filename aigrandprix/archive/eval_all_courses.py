"""Evaluate current best model on all 8 courses."""
import sys
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\tracks")
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\sim")

from drone_env_v2 import DroneRacingEnvV2
from stable_baselines3 import PPO
import glob
import numpy as np

from course_corkscrew import COURSE as CORKSCREW
from course_whiplash import COURSE as WHIPLASH
from course_elevator_shaft import COURSE as ELEVATOR
from course_claustrophobia import COURSE as CLAUSTRO
from course_autobahn import COURSE as AUTOBAHN
from course_gauntlet_jr import COURSE as GAUNTLET_JR
from course_final_exam import COURSE as FINAL_EXAM
from clayton_master_course import MASTER_COURSE

ALL_COURSES = [CORKSCREW, WHIPLASH, ELEVATOR, CLAUSTRO, AUTOBAHN, GAUNTLET_JR, FINAL_EXAM, MASTER_COURSE]

runs = sorted(glob.glob("sim/runs/multicourse_177078*"))
latest = runs[-1]
best = f"{latest}/best/best_model.zip"
print(f"Model: {best}\n")
model = PPO.load(best, device="cpu")

for course in ALL_COURSES:
    name = course.get("name", "Unknown")
    gates = [g["pos"] for g in course["gates"]]
    n_gates = len(gates)
    max_steps = max(1500, n_gates * 60)
    
    results = []
    for ep in range(5):
        env = DroneRacingEnvV2(gates=gates, max_steps=max_steps, gate_radius=0.8)
        obs, _ = env.reset()
        total_reward = 0
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, r, term, trunc, info = env.step(action)
            total_reward += r
            done = term or trunc
        results.append((env.current_gate, total_reward))
    
    avg_gates = np.mean([r[0] for r in results])
    avg_reward = np.mean([r[1] for r in results])
    best_gates = max(r[0] for r in results)
    pct = (avg_gates / n_gates) * 100
    print(f"{name:25s} | gates: {avg_gates:.1f}/{n_gates} ({pct:.0f}%) best={best_gates} | reward: {avg_reward:.1f}")
