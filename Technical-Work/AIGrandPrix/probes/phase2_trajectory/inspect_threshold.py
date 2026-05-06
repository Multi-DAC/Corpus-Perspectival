"""Inspect threshold-probe checkpoints as they land. Prints per-maneuver
gates + aggregate for any eval_step_*.json file present in the threshold
range."""
import json
from pathlib import Path

OUT = Path('/mnt/c/Users/mercu/clawd/projects/aigrandprix/probes/phase2_trajectory')
if not OUT.exists():
    OUT = Path(r'C:\Users\mercu\clawd\projects\aigrandprix\probes\phase2_trajectory')

THRESHOLD_STEPS = [10000016, 12500016, 15000016, 17500016, 20000016, 22500016]

print(f"{'step':>10s}  {'agg':>8s}  {'crash':>6s}  per-maneuver gates_mean")
for s in THRESHOLD_STEPS:
    p = OUT / f'eval_step_{s}.json'
    if not p.exists():
        print(f'{s/1e6:>9.1f}M  pending')
        continue
    with open(p) as f:
        d = json.load(f)
    a = d['aggregate']['mean_gates_across_maneuvers']
    c = d['aggregate']['mean_crash_rate'] * 100
    pm = ' '.join(f"{m[:4]}={d['per_maneuver'][m]['gates_mean']:.1f}"
                  for m in d['per_maneuver'])
    print(f'{s/1e6:>9.1f}M  {a:>8.2f}  {c:>5.0f}%  {pm}')
