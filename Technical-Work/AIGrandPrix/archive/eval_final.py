import sys, numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent / 'sim'))
sys.path.insert(0, str(Path(__file__).resolve().parent / 'rl'))
from train_ppo import make_env
from stable_baselines3 import PPO
from stable_baselines3.common.monitor import Monitor

# Try best model first, then final
run_dir = Path('rl/runs/gauntlet_1770766522')
if (run_dir / 'best' / 'best_model.zip').exists():
    model_path = run_dir / 'best' / 'best_model'
    print(f"Loading BEST model")
else:
    model_path = run_dir / 'final_model'
    print(f"Loading FINAL model")

env = Monitor(make_env('gauntlet'))
model = PPO.load(str(model_path), device='cpu')

print(f"\n{'='*50}")
print(f"ANAKIN EVALUATION — Lobster's Revenge (45 gates)")
print(f"{'='*50}\n")

best_gates = 0
best_reward = 0

for ep in range(5):
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
    n_passed = sum(1 for t in base.gates_passed_times if t > 0)
    time_s = steps * base.dt
    pos = np.array(positions)
    crash = info.get('crash', 'none')
    ep_reward = info['episode']['r']
    
    if n_passed > best_gates:
        best_gates = n_passed
        best_reward = ep_reward

    print(f"Run {ep+1}: {n_passed}/{base.n_gates} gates | {time_s:.1f}s | reward {ep_reward:.0f} | {crash}")
    
    # Print gate times
    times = [t for t in base.gates_passed_times if t > 0]
    if times:
        print(f"  Gate times: {', '.join(f'{t:.1f}s' for t in times[:10])}")
        if len(times) > 10:
            print(f"  ... {', '.join(f'{t:.1f}s' for t in times[10:])}")
    
    print(f"  Position: x=[{pos[:,0].min():.1f},{pos[:,0].max():.1f}] y=[{pos[:,1].min():.1f},{pos[:,1].max():.1f}] z=[{pos[:,2].min():.1f},{pos[:,2].max():.1f}]")
    print()

print(f"{'='*50}")
print(f"BEST: {best_gates}/45 gates | reward {best_reward:.0f}")
print(f"{'='*50}")
