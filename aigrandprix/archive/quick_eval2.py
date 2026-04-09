"""Fast evaluation — maneuver stats (30 eps) + Lobster's Revenge (5 eps)."""
import sys, os, numpy as np
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, str(Path(__file__).parent.parent / 'rl'))

from infinite_gate_env import InfiniteGateEnv, ManeuverLibrary
from stable_baselines3 import PPO

# Find latest best model
best_dirs = sorted(Path('runs').glob('infinite_*/best/best_model.zip'), key=lambda p: p.stat().st_mtime)
model_path = str(best_dirs[-1].with_suffix('')) if best_dirs else None
if not model_path:
    cps = sorted(Path('runs').glob('infinite_*/checkpoints/*.zip'), key=lambda p: p.stat().st_mtime)
    model_path = str(cps[-1].with_suffix(''))

print(f"Loading: {model_path}")
model = PPO.load(model_path, device='cpu')

# Infinite gate eval — 30 episodes
print("\n=== Infinite Gate (30 episodes) ===")
env = InfiniteGateEnv(gate_radius=0.75, max_steps=30000, dt=0.002, substeps=1,
                       domain_rand=False, adaptive_curriculum=False)
gates_list = []
gate_times = []
for ep in range(30):
    obs, _ = env.reset()
    ep_gates = 0
    last_gate_step = 0
    for step in range(30000):
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        if info.get('gates_passed', 0) > ep_gates:
            gate_times.append((step - last_gate_step) * 0.002)
            ep_gates = info['gates_passed']
            last_gate_step = step
        if terminated or truncated:
            break
    gates_list.append(ep_gates)
    if (ep+1) % 10 == 0:
        print(f"  {ep+1}/30 done, avg gates={np.mean(gates_list):.1f}")

print(f"\nGates/episode: avg={np.mean(gates_list):.1f}, max={max(gates_list)}, min={min(gates_list)}")
if gate_times:
    print(f"Gate-to-gate: avg={np.mean(gate_times):.2f}s, median={np.median(gate_times):.2f}s, fastest={min(gate_times):.2f}s")

print("\n=== Per-Maneuver Success ===")
stats = env.get_maneuver_stats()
for m in sorted(stats, key=lambda x: stats[x]['rate'], reverse=True):
    s = stats[m]
    if s['attempts'] > 0:
        bar = '#' * int(s['rate'] * 20)
        print(f"  {m:15s}: {s['rate']:5.1%} [{bar:20s}] ({s['successes']}/{s['attempts']})")

# Lobster's Revenge — 5 episodes  
print("\n=== Lobster's Revenge (5 runs) ===")
# Remove sim/ from path to get rl/train_ppo
sim_dir = os.path.dirname(__file__)
if sim_dir in sys.path:
    sys.path.remove(sim_dir)
from train_ppo import make_env
sys.path.insert(0, sim_dir)

rc = {'gate_bonus': 100.0, 'progress_scale': 1.5, 'time_penalty': 5.0,
      'crash_penalty': 15.0, 'speed_bonus_scale': 0.15}
lr_env = make_env('gauntlet', domain_rand=False, reward_config=rc)
for ep in range(5):
    obs, _ = lr_env.reset()
    total_r = 0
    gates = 0
    for step in range(30000):
        action, _ = model.predict(obs, deterministic=True)
        obs, r, d, t, info = lr_env.step(action)
        total_r += r
        if info.get('gate_passed'):
            gates = info['gate_passed']
        if d or t:
            break
    print(f"  Run {ep+1}: {gates}/45 gates, reward={total_r:.0f}, time={(step+1)*0.002:.1f}s")
