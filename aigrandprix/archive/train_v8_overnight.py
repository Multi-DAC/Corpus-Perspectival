"""
v8: Overnight Extended Training — Continue from checkpoint

Load the best multi-course model and train another 8M steps.
Bias course selection toward courses with fewer gates passed.
"""
import sys
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\tracks")
sys.path.insert(0, r"C:\Users\Wasch\clawd\projects\aigrandprix\sim")
sys.stdout.reconfigure(encoding='utf-8')

import os
import time
import numpy as np
import torch

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.common.callbacks import EvalCallback, BaseCallback
from drone_env_v2 import DroneRacingEnvV2

from course_corkscrew import COURSE as CORKSCREW
from course_whiplash import COURSE as WHIPLASH
from course_elevator_shaft import COURSE as ELEVATOR
from course_claustrophobia import COURSE as CLAUSTRO
from course_autobahn import COURSE as AUTOBAHN
from course_gauntlet_jr import COURSE as GAUNTLET_JR
from course_final_exam import COURSE as FINAL_EXAM
from clayton_master_course import MASTER_COURSE

ALL_COURSES = [
    CORKSCREW, WHIPLASH, ELEVATOR, CLAUSTRO,
    AUTOBAHN, GAUNTLET_JR, FINAL_EXAM, MASTER_COURSE,
]

# Curriculum weights — higher = picked more often
# Based on eval results: mastered courses get less time, weak ones get more
COURSE_WEIGHTS = [
    1,   # Corkscrew: 100% — maintenance reps only
    3,   # Whiplash: 55% — needs work
    1,   # Elevator Shaft: 100% — maintenance
    1,   # Claustrophobia: 100% — maintenance
    4,   # Autobahn: 16% — needs heavy work
    4,   # Gauntlet Jr: 25% — needs heavy work
    3,   # Final Exam: 48% — needs work
    5,   # Clayton's Gauntlet: 0% — needs the most work
]

GATE_RADIUS = 0.8

device = "cpu"  # MLP policy runs better on CPU
print(f"Device: {device}")
print(f"Courses: {len(ALL_COURSES)}")
for i, c in enumerate(ALL_COURSES):
    name = c.get("name", "Unknown")
    n = len(c["gates"])
    w = COURSE_WEIGHTS[i]
    print(f"  {name}: {n} gates (weight: {w})")


class WeightedMultiCourseEnv(DroneRacingEnvV2):
    """Random course selection with curriculum weighting."""
    
    def __init__(self, courses, weights, max_steps=3000, **kwargs):
        self.courses = courses
        self.weights = np.array(weights, dtype=np.float64)
        self.weights /= self.weights.sum()  # normalize to probabilities
        
        self._course_gates = []
        for c in courses:
            gates = [g["pos"] for g in c["gates"]]
            self._course_gates.append(gates)
        
        self._rng = np.random.default_rng()
        self._initialized = False
        
        largest = max(self._course_gates, key=len)
        super().__init__(gates=largest, max_steps=max_steps, **kwargs)
        self._initialized = True
    
    def reset(self, seed=None, options=None):
        if not self._initialized:
            return super().reset(seed=seed, options=options)
        
        # Weighted random course selection
        idx = self._rng.choice(len(self.courses), p=self.weights)
        selected_gates = self._course_gates[idx]
        
        self.gates = [np.array(g, dtype=np.float64) for g in selected_gates]
        self.n_gates = len(self.gates)
        self.max_steps = max(1500, len(self.gates) * 80)  # More time for longer courses
        
        return super().reset(seed=seed, options=options)


class PerCourseEvalCallback(BaseCallback):
    """Log per-course performance with FIXED gate counting."""
    
    def __init__(self, courses, eval_freq=200000, n_eval_episodes=3, 
                 gate_radius=0.8, verbose=1):
        super().__init__(verbose)
        self.courses = courses
        self.eval_freq = eval_freq
        self.n_eval_episodes = n_eval_episodes
        self.gate_radius = gate_radius
    
    def _on_step(self) -> bool:
        if self.num_timesteps % self.eval_freq == 0 and self.num_timesteps > 0:
            print(f"\n{'='*60}")
            print(f"Per-Course Evaluation at step {self.num_timesteps}")
            print(f"{'='*60}")
            
            for course in self.courses:
                name = course.get("name", "Unknown")
                gates = [g["pos"] for g in course["gates"]]
                max_steps = max(1500, len(gates) * 80)
                
                env = DroneRacingEnvV2(gates=gates, max_steps=max_steps, 
                                       gate_radius=self.gate_radius)
                rewards = []
                gates_passed = []
                
                for ep in range(self.n_eval_episodes):
                    obs, _ = env.reset()
                    total_reward = 0
                    done = False
                    while not done:
                        action, _ = self.model.predict(obs, deterministic=True)
                        obs, reward, terminated, truncated, info = env.step(action)
                        total_reward += reward
                        done = terminated or truncated
                    rewards.append(total_reward)
                    gates_passed.append(env.current_gate)  # FIXED: use env.current_gate
                
                avg_r = np.mean(rewards)
                avg_g = np.mean(gates_passed)
                total_g = len(gates)
                pct = (avg_g / total_g) * 100 if total_g > 0 else 0
                print(f"  {name:25s} | reward: {avg_r:8.1f} | gates: {avg_g:.1f}/{total_g} ({pct:.0f}%)")
            
            print(f"{'='*60}\n")
        return True


def make_env(courses, weights, max_steps=3000, gate_radius=0.8):
    def _init():
        return WeightedMultiCourseEnv(
            courses=courses,
            weights=weights,
            max_steps=max_steps,
            gate_radius=gate_radius,
        )
    return _init


def main():
    run_name = f"overnight_{int(time.time())}"
    run_dir = os.path.join("runs", run_name)
    os.makedirs(run_dir, exist_ok=True)
    
    total_timesteps = 8_000_000
    n_envs = 4
    
    # Load checkpoint
    checkpoint = r"C:\Users\Wasch\clawd\projects\aigrandprix\sim\runs\multicourse_1770781551\best\best_model.zip"
    
    print(f"\n=== Overnight Extended Training ===")
    print(f"Run: {run_name}")
    print(f"Checkpoint: {checkpoint}")
    print(f"Total NEW steps: {total_timesteps:,}")
    print(f"Parallel envs: {n_envs}")
    print(f"Gate radius: {GATE_RADIUS}")
    print(f"Course weighting: curriculum (weak courses favored)")
    print()
    
    # Create environments
    env = DummyVecEnv([make_env(ALL_COURSES, COURSE_WEIGHTS, gate_radius=GATE_RADIUS) 
                       for _ in range(n_envs)])
    eval_env = DummyVecEnv([make_env(ALL_COURSES, COURSE_WEIGHTS, gate_radius=GATE_RADIUS)])
    
    # Load model with new env
    model = PPO.load(checkpoint, env=env, device=device)
    model.tensorboard_log = os.path.join(run_dir, "tb")
    
    print(f"Model loaded from checkpoint. Continuing training...")
    
    # Callbacks
    eval_callback = EvalCallback(
        eval_env,
        best_model_save_path=os.path.join(run_dir, "best"),
        log_path=os.path.join(run_dir, "eval_logs"),
        eval_freq=max(50000 // n_envs, 1),
        n_eval_episodes=5,
        deterministic=True,
    )
    
    per_course_callback = PerCourseEvalCallback(
        ALL_COURSES,
        eval_freq=500000,  # Every 500K steps
        n_eval_episodes=3,
        gate_radius=GATE_RADIUS,
    )
    
    # Train
    print(f"\nStarting overnight training...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[eval_callback, per_course_callback],
        progress_bar=True,
        reset_num_timesteps=True,
    )
    
    # Save final model
    final_path = os.path.join(run_dir, "final_model")
    model.save(final_path)
    print(f"\nFinal model saved: {final_path}")
    
    # Final per-course evaluation (10 episodes each)
    print("\n=== FINAL OVERNIGHT EVALUATION ===")
    for course in ALL_COURSES:
        name = course.get("name", "Unknown")
        gates = [g["pos"] for g in course["gates"]]
        max_steps = max(1500, len(gates) * 80)
        
        env_eval = DroneRacingEnvV2(gates=gates, max_steps=max_steps, gate_radius=GATE_RADIUS)
        rewards = []
        gates_passed_list = []
        
        for ep in range(10):
            obs, _ = env_eval.reset()
            total_reward = 0
            done = False
            while not done:
                action, _ = model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = env_eval.step(action)
                total_reward += reward
                done = terminated or truncated
            rewards.append(total_reward)
            gates_passed_list.append(env_eval.current_gate)  # FIXED
        
        avg_r = np.mean(rewards)
        avg_g = np.mean(gates_passed_list)
        best_g = max(gates_passed_list)
        total_g = len(gates)
        pct = (avg_g / total_g) * 100 if total_g > 0 else 0
        print(f"  {name:25s} | gates: {avg_g:.1f}/{total_g} ({pct:.0f}%) best={best_g} | reward: {avg_r:.1f}")


if __name__ == "__main__":
    main()
