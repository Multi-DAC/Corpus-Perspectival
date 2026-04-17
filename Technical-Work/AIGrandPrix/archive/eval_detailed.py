import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'sim'))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'rl'))
from train_ppo import make_env
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

# Best model from latest training run
model_path = 'rl/runs/gauntlet_1770766522/best/best_model.zip'
print(f"Evaluating: {model_path}\n")

model = PPO.load(model_path, device='cpu')

# Evaluate on gauntlet track
env = Monitor(make_env('gauntlet'))

print("=== Gauntlet Track Evaluation ===")
for ep in range(5):
    obs, info = env.reset()
    done = False
    steps = 0
    
    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        steps += 1
        done = terminated or truncated
    
    # Get stats
    base = env.unwrapped
    while hasattr(base, 'env'):
        base = base.env
    
    gates_passed = base.current_gate if hasattr(base, 'current_gate') else 0
    total_gates = base.n_gates if hasattr(base, 'n_gates') else '?'
    time_s = steps * base.dt if hasattr(base, 'dt') else steps * 0.02
    
    print(f"Ep {ep+1}: gates={gates_passed}/{total_gates}, time={time_s:.1f}s, reward={info['episode']['r']:.1f}")

env.close()

# Also test on individual tracks
print("\n=== Individual Track Evaluation ===")
tracks = ['gauntlet', '19gate']

for track_name in tracks:
    try:
        env = Monitor(make_env(track_name))
        obs, info = env.reset()
        done = False
        steps = 0
        
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, reward, terminated, truncated, info = env.step(action)
            steps += 1
            done = terminated or truncated
        
        base = env.unwrapped
        while hasattr(base, 'env'):
            base = base.env
        
        gates_passed = base.current_gate if hasattr(base, 'current_gate') else 0
        total_gates = base.n_gates if hasattr(base, 'n_gates') else '?'
        time_s = steps * base.dt if hasattr(base, 'dt') else steps * 0.02
        
        print(f"{track_name}: {gates_passed}/{total_gates} gates in {time_s:.1f}s (reward: {info['episode']['r']:.1f})")
        env.close()
    except Exception as e:
        print(f"{track_name}: Error - {e}")
