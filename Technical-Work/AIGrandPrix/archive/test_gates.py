import numpy as np, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from drone_env_v2 import DroneRacingEnvV2
from tracking_controller import TrajectoryOracle

expert_dir = os.path.join(os.path.dirname(__file__), '..', 'expert_trajectory')
states = np.load(os.path.join(expert_dir, 'states.npy'))
times = np.load(os.path.join(expert_dir, 'times.npy'))

# Use larger gate radius to see tracking quality
env = DroneRacingEnvV2(dt=0.02, substeps=4, gate_radius=0.8)
oracle = TrajectoryOracle(states, times)
obs, _ = env.reset()

min_dists = {}  # Track min distance to each gate

for step in range(2000):
    t = step * env.dt
    action_norm, _ = oracle.compute_action_normalized(env.state, t=t)
    
    # Check distance to current gate
    if env.current_gate < env.n_gates:
        gi = env.current_gate
        dist = np.linalg.norm(env.state[0:3] - env.gates[gi])
        if gi not in min_dists or dist < min_dists[gi]:
            min_dists[gi] = dist
        if dist < 2.0:
            print(f"t={t:5.2f}s gate={gi:2d} dist={dist:.3f}m")
    
    obs, reward, terminated, truncated, info = env.step(action_norm)
    
    if 'gate_passed' in info:
        g = info['gate_passed']
        print(f"  >>> GATE {g} PASSED <<<")
    
    if terminated:
        print(f"CRASH at t={t:.1f}s: {info}")
        break

print(f"\nGates passed: {env.current_gate}/{env.n_gates}")
print(f"\nMin distances to gates (tracker got this close):")
for gi in sorted(min_dists.keys()):
    status = "PASS" if min_dists[gi] < 0.8 else ("CLOSE" if min_dists[gi] < 1.5 else "MISS")
    print(f"  Gate {gi:2d}: {min_dists[gi]:.3f}m [{status}]")
