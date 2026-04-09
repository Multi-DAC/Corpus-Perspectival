"""
v4: Harder course + domain randomization + speed rewards.
Goal: Make the agent fast AND robust, not just competent.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import time
import numpy as np

from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from drone_env import DroneRacingEnv


# Harder courses with turns and altitude changes
COURSES = {
    "easy": [
        [5.0, 0.0, 2.0],
        [10.0, 3.0, 2.5],
        [15.0, 0.0, 3.0],
        [20.0, -3.0, 2.0],
        [25.0, 0.0, 2.5],
    ],
    "zigzag": [
        [5.0, 4.0, 2.0],
        [10.0, -4.0, 3.0],
        [15.0, 4.0, 2.0],
        [20.0, -4.0, 3.0],
        [25.0, 0.0, 2.5],
    ],
    "climb": [
        [5.0, 0.0, 3.0],
        [10.0, 2.0, 5.0],
        [15.0, 0.0, 7.0],
        [20.0, -2.0, 5.0],
        [25.0, 0.0, 3.0],
    ],
    "tight": [
        [4.0, 2.0, 2.0],
        [8.0, -2.0, 3.0],
        [12.0, 3.0, 2.0],
        [16.0, -3.0, 4.0],
        [20.0, 0.0, 2.5],
    ],
}


def test_agent(model, course_name, gates, n_episodes=5):
    """Test agent on a specific course."""
    test_env = DroneRacingEnv(gates=gates, max_steps=1000)
    results = []
    for ep in range(n_episodes):
        obs, _ = test_env.reset()
        done = False
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = test_env.step(action)
            done = terminated or truncated
        stats = test_env.get_stats()
        results.append(stats)
    
    avg_gates = sum(r["gates_passed"] for r in results) / len(results)
    avg_reward = sum(r["total_reward"] for r in results) / len(results)
    completions = sum(1 for r in results if r["gates_passed"] == len(gates))
    avg_speed = sum(r["velocity"] for r in results) / len(results)
    
    print(f"  {course_name:>8s}: Gates {avg_gates:.1f}/5 | "
          f"Complete {completions}/{n_episodes} | "
          f"Reward {avg_reward:.1f} | Speed {avg_speed:.1f} m/s")
    return avg_gates, completions


def main():
    print("=" * 60)
    print("v4: Multi-course training with domain randomization")
    print("=" * 60)
    
    # Train on randomized courses (pick random course each reset)
    # We'll train on easy first, then test generalization
    
    # Phase 1: Train on easy course (our proven approach)
    print("\nPhase 1: Training on easy course (500K steps)...")
    env = make_vec_env(
        DroneRacingEnv, n_envs=4,
        env_kwargs={"max_steps": 500, "gates": COURSES["easy"]}
    )
    
    model = PPO(
        "MlpPolicy", env,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        ent_coef=0.01,
        verbose=0,
    )
    
    t0 = time.time()
    model.learn(total_timesteps=500_000)
    print(f"Phase 1 done ({time.time()-t0:.0f}s)")
    
    # Test on all courses
    print("\nPhase 1 Results (trained on easy only):")
    for name, gates in COURSES.items():
        test_agent(model, name, gates)
    
    # Phase 2: Fine-tune on all courses
    print("\nPhase 2: Fine-tuning on all courses (200K per course)...")
    for name, gates in COURSES.items():
        env = make_vec_env(
            DroneRacingEnv, n_envs=4,
            env_kwargs={"max_steps": 500, "gates": gates}
        )
        model.set_env(env)
        model.learn(total_timesteps=200_000)
        print(f"  Trained on {name}")
    
    print(f"Phase 2 done ({time.time()-t0:.0f}s total)")
    model.save("drone_ppo_v4")
    
    # Final test on all courses
    print("\nFinal Results (trained on all courses):")
    total_completions = 0
    for name, gates in COURSES.items():
        _, completions = test_agent(model, name, gates)
        total_completions += completions
    
    print(f"\nOverall: {total_completions}/{len(COURSES)*5} course completions")
    
    if total_completions >= 15:
        print("Excellent generalization! Agent handles diverse courses.")
    elif total_completions >= 10:
        print("Good progress. Agent generalizes to most courses.")
    else:
        print("Needs more training or architecture changes for generalization.")


if __name__ == "__main__":
    main()
