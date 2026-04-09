import sys
import os
BASEPATH = os.path.abspath(__file__).split('rpg_time_optimal', 1)[0]+'rpg_time_optimal/'
sys.path += [BASEPATH + 'src']
from track import Track
from quad import Quad
from integrator import RungeKutta4
from planner import Planner
from trajectory import Trajectory

track = Track(BASEPATH + "/tracks/track.yaml")
quad = Quad(BASEPATH + "/quads/quad.yaml")

# No plotting callback — headless solve for speed
solver_options = {
    'ipopt': {
        'max_iter': 5000,
        'max_wall_time': 5400.0,  # 90 minutes
        'tol': 1e-4,              # slightly relaxed tolerance for faster convergence
        'acceptable_tol': 1e-3,
        'acceptable_iter': 50,    # accept if 50 iterations meet acceptable_tol
        'print_level': 5,
        'linear_solver': 'mumps',
    }
}

planner = Planner(quad, track, RungeKutta4, {
    'tolerance': 0.3,
    'nodes_per_gate': 40,
    'vel_guess': 3.0,
    'solver_options': solver_options,
})
planner.setup()
x = planner.solve()

traj = Trajectory(x, NPW=planner.NPW, wp=planner.wp)
traj.save(BASEPATH + '/example/result_cpc_format.csv', False)
traj.save(BASEPATH + '/example/result.csv', True)

print(f'\n=== RESULT ===')
print(f'Total time: {traj.time[-1]:.2f}s')
print(f'Trajectory saved to result.csv and result_cpc_format.csv')
