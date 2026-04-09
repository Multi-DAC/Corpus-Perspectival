import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'sim'))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'rl'))
from train_ppo import make_env
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

env = Monitor(make_env('gauntlet'))
model = PPO.load('rl/runs/gauntlet_1770758712/best/best_model', device='cpu')

for ep in range(3):
    obs, info = env.reset()
    done = False
    steps = 0
    positions = []

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        steps += 1
        done = terminated or truncated
        base = env.unwrapped
        positions.append(base.state[:3].copy())

    base = env.unwrapped
    print(f"Episode {ep+1}:")
    print(f"  current_gate: {base.current_gate}/{base.n_gates}")
    print(f"  gates_passed_times: {base.gates_passed_times[:10]}...")
    n_passed = sum(1 for t in base.gates_passed_times if t > 0)
    print(f"  gates passed: {n_passed}/{base.n_gates}")
    time_s = steps * base.dt
    print(f"  time: {time_s:.1f}s, steps: {steps}")
    print(f"  crash: {info.get('crash', '?')}")
    print(f"  reward: {info['episode']['r']:.1f}")
    pos = np.array(positions)
    print(f"  position range: x=[{pos[:,0].min():.1f},{pos[:,0].max():.1f}] y=[{pos[:,1].min():.1f},{pos[:,1].max():.1f}] z=[{pos[:,2].min():.1f},{pos[:,2].max():.1f}]")
    print()
