"""Summarize Phase 2 trajectory: load all eval_step_*.json files, print
table + per-maneuver progression, write a markdown summary.
"""

import json
from pathlib import Path

OUT_DIR = Path('/mnt/c/Users/mercu/clawd/projects/aigrandprix/probes/phase2_trajectory')
if not OUT_DIR.exists():
    import os
    OUT_DIR = Path(r'C:\Users\mercu\clawd\projects\aigrandprix\probes\phase2_trajectory')

files = sorted(OUT_DIR.glob('eval_step_*.json'),
               key=lambda p: int(p.stem.split('_')[-1]))

if not files:
    print('no eval files yet')
    exit(0)

print(f'Found {len(files)} checkpoint eval files\n')

# Load all
results = []
for f in files:
    with open(f) as fp:
        d = json.load(fp)
    results.append(d)

# Trajectory table — curriculum + aggregate
print('=' * 100)
print(f"{'step':>10s}  {'cur_gates':>10s}  {'cur_max':>8s}  {'cur_crash':>10s}  {'agg_gates':>10s}  {'agg_crash':>10s}")
print('-' * 100)
for r in results:
    step = r['step']
    cur = r['curriculum']
    agg = r['aggregate']
    print(f"{step:>10,d}  {cur['gates_mean']:>10.2f}  {cur['gates_max']:>8d}  {cur['crash_rate']*100:>9.0f}%  "
          f"{agg['mean_gates_across_maneuvers']:>10.2f}  {agg['mean_crash_rate']*100:>9.0f}%")
print()

# Per-maneuver progression — gates over time
maneuvers = list(results[0]['per_maneuver'].keys())
print('=' * 100)
print('Per-maneuver gate progression (mean gates per episode, 8 episodes/maneuver):')
print('-' * 100)
header = f"{'maneuver':<14s}"
for r in results:
    header += f"  {r['step']/1e6:>5.1f}M"
print(header)
for m in maneuvers:
    row = f"{m:<14s}"
    for r in results:
        g = r['per_maneuver'][m]['gates_mean']
        row += f"  {g:>5.2f} "
    print(row)
print()

# Per-maneuver crash rate progression
print('=' * 100)
print('Per-maneuver crash rate progression (% of episodes ending in crash):')
print('-' * 100)
header = f"{'maneuver':<14s}"
for r in results:
    header += f"  {r['step']/1e6:>5.1f}M"
print(header)
for m in maneuvers:
    row = f"{m:<14s}"
    for r in results:
        c = r['per_maneuver'][m]['crash_rate'] * 100
        row += f"  {c:>4.0f}% "
    print(row)
print()

# Trajectory shape diagnosis
print('=' * 100)
print('Trajectory shape diagnosis:')
print('-' * 100)
agg_gates = [r['aggregate']['mean_gates_across_maneuvers'] for r in results]
first, last = agg_gates[0], agg_gates[-1]
peak = max(agg_gates)
peak_step = results[agg_gates.index(peak)]['step']
print(f"  First (22.5M): {first:.2f}")
print(f"  Last  ({results[-1]['step']/1e6:.1f}M): {last:.2f}")
print(f"  Peak: {peak:.2f} at step {peak_step:,}")
delta = last - first
trend = 'CLIMBING' if delta > 1.0 else 'PLATEAU' if abs(delta) < 1.0 else 'REGRESSING'
print(f"  Trend (last - first): {delta:+.2f}  →  {trend}")

# Convergence pattern: how do laggards (lowest at first) move vs leaders?
first_pm = results[0]['per_maneuver']
last_pm = results[-1]['per_maneuver']
print()
print('  Per-maneuver shift (last - first), sorted by first-gate-count:')
shifts = []
for m in maneuvers:
    f0 = first_pm[m]['gates_mean']
    fl = last_pm[m]['gates_mean']
    shifts.append((f0, m, f0, fl, fl - f0))
shifts.sort()
for _, m, f0, fl, dlt in shifts:
    arrow = '↑' if dlt > 1.0 else '↓' if dlt < -1.0 else '·'
    print(f"    {m:<14s}  {f0:>6.2f} → {fl:>6.2f}  ({dlt:+6.2f})  {arrow}")
