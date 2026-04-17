"""
v7: Multi-Course Training — Phase 2

Train on all 8 courses with random course selection per episode.
This prevents overfitting to any single track layout and builds
a generalist racing agent.

Courses:
1. The Corkscrew (15 gates) — tight hairpins
2. Whiplash (20 gates) — speed management
3. Elevator Shaft (15 gates) — vertical variation
4. Claustrophobia (20 gates) — tight spacing
5. The Autobahn (25 gates) — speed course
6. The Gauntlet Jr. (20 gates) — general sampler
7. Final Exam (25 gates) — integration test
8. Clayton's Gauntlet (45 gates) — original master course
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
from stable_baselines3.common.vec_env import DummyVecEnv, SubprocVecEnv
from stable_baselines3.common.callbacks import EvalCallback, BaseCallback
from drone_env_v2 import DroneRacingEnvV2

# Import all courses
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

# Check device
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Device: {device}")
if device == "cuda":
    print(f"GPU: {torch.cuda.get_device_name(0)}")
print(f"Courses: {len(ALL_COURSES)}")
for c in ALL_COURSES:
    name = c.get("name", "Unknown")
    n = len(c["gates"])
    print(f"  {name}: {n} gates")


class MultiCourseEnv(DroneRacingEnvV2):
    """
    Wrapper that randomly selects a course on each reset.
    This forces the agent to generalize across track geometries.
    """
    
    def __init__(self, courses, max_steps=3000, **kwargs):
        self.courses = courses
        self._course_gates = []
        for c in courses:
            gates = [g["pos"] for g in c["gates"]]
            self._course_gates.append(gates)
        
        self._rng = np.random.default_rng()
        self._initialized = False
        
        # Initialize with the largest course to set up observation space
        largest = max(self._course_gates, key=len)
        super().__init__(gates=largest, max_steps=max_steps, **kwargs)
        self._initialized = True
    
    def reset(self, seed=None, options=None):
        # Randomly select a course (skip if not yet initialized)
        if not self._initialized:
            return super().reset(seed=seed, options=options)
        idx = self._rng.integers(0, len(self.courses))
        selected_gates = self._course_gates[idx]
        
        # Update gates
        self.gates = [np.array(g, dtype=np.float64) for g in selected_gates]
        self.n_gates = len(self.gates)
        
        # Adjust max_steps based on course size
        # More gates = more time needed
        self.max_steps = max(1500, len(self.gates) * 60)
        
        return super().reset(seed=seed, options=options)


class PerCourseEvalCallback(BaseCallback):
    """Log per-course performance during training."""
    
    def __init__(self, courses, eval_freq=50000, n_eval_episodes=3, verbose=1, gate_radius=0.8):
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
                max_steps = max(1500, len(gates) * 60)
                
                env = DroneRacingEnvV2(gates=gates, max_steps=max_steps, gate_radius=self.gate_radius)
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
                    gates_passed.append(env.current_gate)
                
                avg_r = np.mean(rewards)
                avg_g = np.mean(gates_passed)
                total_g = len(gates)
                pct = (avg_g / total_g) * 100 if total_g > 0 else 0
                print(f"  {name:25s} | reward: {avg_r:8.1f} | gates: {avg_g:.1f}/{total_g} ({pct:.0f}%)")
            
            print(f"{'='*60}\n")
        return True


def make_env(courses, max_steps=3000, domain_randomization=False, gate_radius=0.8):
    def _init():
        return MultiCourseEnv(
            courses=courses, 
            max_steps=max_steps,
            domain_randomization=domain_randomization,
            gate_radius=gate_radius,
        )
    return _init


def main():
    run_name = f"multicourse_{int(time.time())}"
    run_dir = os.path.join("runs", run_name)
    os.makedirs(run_dir, exist_ok=True)
    
    total_timesteps = 4_000_000  # More steps needed for multi-course generalization
    n_envs = 4
    
    print(f"\n=== Multi-Course Training ===")
    print(f"Run: {run_name}")
    print(f"Total steps: {total_timesteps:,}")
    print(f"Parallel envs: {n_envs}")
    print(f"Courses: {len(ALL_COURSES)}")
    print()
    
    # Create parallel training environments
    env = DummyVecEnv([make_env(ALL_COURSES) for _ in range(n_envs)])
    
    # Eval environment (tests on all courses via MultiCourseEnv)
    eval_env = DummyVecEnv([make_env(ALL_COURSES)])
    
    # Note: gauntlet model used different obs space (26-dim DroneRacingEnv v1)
    # vs our 20-dim DroneRacingEnvV2. Training from scratch with real physics.
    print("Training Anakin from scratch on real quadrotor dynamics")
    model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=256,
            n_epochs=10,
            gamma=0.99,
            gae_lambda=0.95,
            clip_range=0.2,
            ent_coef=0.01,
            policy_kwargs=dict(
                net_arch=dict(pi=[256, 256], vf=[256, 256]),
            ),
            tensorboard_log=os.path.join(run_dir, "tb"),
            device=device,
        )
    
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
        eval_freq=200000,  # Every 200K steps, test each course individually
        n_eval_episodes=3,
    )
    
    # Train
    print(f"\nStarting training...")
    model.learn(
        total_timesteps=total_timesteps,
        callback=[eval_callback, per_course_callback],
        progress_bar=True,
    )
    
    # Save final model
    final_path = os.path.join(run_dir, "final_model")
    model.save(final_path)
    print(f"\nFinal model saved: {final_path}")
    
    # Final per-course evaluation
    print("\n=== FINAL EVALUATION ===")
    for course in ALL_COURSES:
        name = course.get("name", "Unknown")
        gates = [g["pos"] for g in course["gates"]]
        max_steps = max(1500, len(gates) * 60)
        
        env_eval = DroneRacingEnvV2(gates=gates, max_steps=max_steps, gate_radius=0.8)
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
            gates_passed_list.append(env_eval.current_gate)
        
        avg_r = np.mean(rewards)
        avg_g = np.mean(gates_passed_list)
        total_g = len(gates)
        pct = (avg_g / total_g) * 100 if total_g > 0 else 0
        print(f"  {name:25s} | reward: {avg_r:8.1f} | gates: {avg_g:.1f}/{total_g} ({pct:.0f}%)")


if __name__ == "__main__":
    main()
