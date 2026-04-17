import yaml, numpy as np
from pathlib import Path

base = Path(__file__).parent.parent / 'rpg_time_optimal' / 'tracks'
tracks = ['gauntlet', 'corkscrew', 'elevator_shaft', 'autobahn', 'whiplash', 'claustrophobia', 'gauntlet_jr', 'final_exam']

for t in tracks:
    p = base / f'{t}.yaml'
    if not p.exists():
        print(f"{t}: NOT FOUND")
        continue
    data = yaml.safe_load(open(p))
    gates = [np.array(g) for g in data['gates']]
    dists = [np.linalg.norm(gates[i+1] - gates[i]) for i in range(len(gates)-1)]
    init = np.array(data['initial']['position'])
    first_dist = np.linalg.norm(gates[0] - init)
    print(f"{t:20s}: {len(gates):2d} gates, init->g1={first_dist:5.1f}m, "
          f"avg_gap={np.mean(dists):5.1f}m, min={np.min(dists):5.1f}m, max={np.max(dists):5.1f}m")
