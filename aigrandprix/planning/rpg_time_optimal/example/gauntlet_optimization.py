"""
Optimize time-optimal trajectory through Clayton's 45-Gate Gauntlet.
Expected to run for 2-4 hours due to course complexity.
"""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from planner import Planner
from quad import Quad
from track import Track
from integrator import RungeKutta4
from trajectory import Trajectory

# Load quad and track
quad_path = os.path.join(os.path.dirname(__file__), '..', 'quads', 'quad.yaml')
track_path = os.path.join(os.path.dirname(__file__), '..', 'tracks', 'gauntlet.yaml')

quad = Quad(quad_path)
track = Track(track_path)

print(f"Track: {len(track.gates)} gates")
print(f"Quad: mass={quad.m}kg, T_max={quad.T_max:.2f}N/motor")

# Compute total course distance for initial guesses
import numpy as np
gates = np.array(track.gates)
total_dist = np.linalg.norm(gates[0] - np.array(track.init_pos))
for i in range(len(gates) - 1):
    total_dist += np.linalg.norm(gates[i+1] - gates[i])
print(f"Approximate course distance: {total_dist:.1f}m")

# Conservative estimate: avg 8 m/s (course has lots of verticals and tight turns)
t_guess = total_dist / 8.0
print(f"Time guess: {t_guess:.1f}s (at 8 m/s avg)")

# Options — more nodes per gate for the complex course
options = {
    'nodes_per_gate': 40,  # More nodes for tighter tolerance on 45 gates
    'tolerance': 0.3,
    'vel_guess': 8.0,
    't_guess': t_guess,
    'solver_options': {
        'ipopt': {
            'max_iter': 10000,
            'tol': 1e-3,
            'acceptable_tol': 1e-2,
            'acceptable_iter': 100,
            'print_level': 5,
            'linear_solver': 'mumps',
        }
    }
}

print(f"\nSetting up optimizer...")
print(f"  Nodes per gate: {options['nodes_per_gate']}")
print(f"  Total nodes: {options['nodes_per_gate'] * (len(track.gates) + 1)}")
print(f"  Tolerance: {options['tolerance']}m")

t0 = time.time()
planner = Planner(quad, track, RungeKutta4, options)
planner.setup()
setup_time = time.time() - t0
print(f"Setup complete in {setup_time:.1f}s")

print(f"\nSolving... (this will take a while)")
print(f"Wall time started: {time.strftime('%H:%M:%S')}")

t0 = time.time()
x_sol = planner.solve()
solve_time = time.time() - t0

print(f"\nSolver finished in {solve_time:.1f}s ({solve_time/60:.1f} min)")
print(f"Wall time ended: {time.strftime('%H:%M:%S')}")

# Extract trajectory
traj = Trajectory(x_sol, NPW=planner.NPW, wp=planner.wp)
optimal_time = traj.t_total
print(f"\nOPTIMAL TIME: {optimal_time:.2f}s")
print(f"Average speed: {total_dist / optimal_time:.2f} m/s")

# Save
result_path = os.path.join(os.path.dirname(__file__), 'gauntlet_result.csv')
traj.save(result_path, True)
result_path2 = os.path.join(os.path.dirname(__file__), 'gauntlet_result_raw.csv')
traj.save(result_path2, False)
print(f"Trajectory saved to {result_path}")
