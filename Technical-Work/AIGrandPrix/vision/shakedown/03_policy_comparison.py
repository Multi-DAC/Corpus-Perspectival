"""
Stage 3 — adapter × policy: action-distribution comparison.

Loads the baseline 60.4M PPO policy (the one that actually flies) and,
for each scenario, runs policy.predict() on:
  (a) the state-based obs (what the policy was trained on)
  (b) the vision-derived obs (what the competition stack will feed)

Then diffs the resulting actions per dim. The vision pipeline is
"policy-equivalent" if the action drift stays small across scenarios.

Pass criteria:
  - |action_vision - action_state| < 0.10 per dim, mean across scenarios
  - max single-dim drift < 0.25 in any scenario
  - sign agreement on all 4 action dims in all scenarios
    (thrust/roll-rate/pitch-rate/yaw-rate must point the same way)

Background:
  - Baseline 60.4M was trained pre-F1 → NO VecNormalize, raw obs.
    Confirmed by grepping `train_infinite.py` (no norm_obs references).
  - Stages 1+1b cleared the vision pipeline detection accuracy.
  - Stage 2 cleared the obs-tensor wiring (3 wiring bugs fixed).
  - Stage 3 closes the loop: does the policy *agree with itself*
    across the two paths through the same drone state?
"""

import os
import sys
import json
from pathlib import Path
import numpy as np

VISION_DIR = Path(__file__).resolve().parent.parent
SIM_DIR = VISION_DIR.parent / 'sim'
sys.path.insert(0, str(VISION_DIR))
sys.path.insert(0, str(SIM_DIR))

# Reuse stage 2 obs builders
sys.path.insert(0, str(Path(__file__).parent))
from importlib import import_module
stage2 = import_module('02_adapter_integration')
state_based_obs = stage2.state_based_obs
vision_based_obs = stage2.vision_based_obs
make_scenarios = stage2.make_scenarios
DIM_LABELS = stage2.DIM_LABELS

from synthetic_camera import SyntheticCamera
from gate_detector import GateDetector, GateDetectorConfig
from adapter import CompetitionAdapter

from stable_baselines3 import PPO


BASELINE_PATH = SIM_DIR / 'runs' / 'infinite_1771733969' / 'best' / 'best_model.zip'

ACTION_LABELS = ['thrust', 'roll_rate', 'pitch_rate', 'yaw_rate']
PASS_MEAN_DRIFT = 0.10
PASS_MAX_DRIFT = 0.25


def main():
    if not BASELINE_PATH.exists():
        print(f'ERROR: baseline policy not found at {BASELINE_PATH}')
        sys.exit(1)

    print(f'Loading baseline policy: {BASELINE_PATH}')
    model = PPO.load(str(BASELINE_PATH), device='cpu')
    print(f'  obs space: {model.observation_space}')
    print(f'  action space: {model.action_space}')

    cam = SyntheticCamera(640, 480, 90.0)
    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(640, 480, 90.0)
    adapter = CompetitionAdapter()

    scenarios = make_scenarios()
    report = []
    for s in scenarios:
        adapter.reset()
        state_obs = state_based_obs(
            s['pos'], s['vel'], s['q'], s['omega'],
            s['gate_pos'], s['gate_orient_world'],
            next_gate_pos=s.get('next_gate_pos'),
        )
        vision_obs, found, est_dist = vision_based_obs(s, cam, det, adapter)

        action_state, _ = model.predict(state_obs, deterministic=True)
        action_vision, _ = model.predict(vision_obs, deterministic=True)
        action_state = np.asarray(action_state).flatten()
        action_vision = np.asarray(action_vision).flatten()
        diff = action_vision - action_state
        signs_agree = bool(np.all(np.sign(action_state) == np.sign(action_vision)))

        report.append({
            'scenario': s['name'],
            'detection_found': bool(found),
            'pnp_distance_m': est_dist,
            'true_distance_m': float(np.linalg.norm(s['gate_pos'] - s['pos'])),
            'action_state': action_state.tolist(),
            'action_vision': action_vision.tolist(),
            'action_diff': diff.tolist(),
            'max_abs_diff': float(np.max(np.abs(diff))),
            'mean_abs_diff': float(np.mean(np.abs(diff))),
            'signs_agree': signs_agree,
        })

    out_dir = Path(__file__).parent / 'results'
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / 'stage3_policy_comparison.json', 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\n{'Scenario':<25} {'maxDrift':>9} {'meanDrift':>10} {'signs':>6}  per-dim diff")
    for r in report:
        per = ', '.join(f"{l}({d:+.3f})" for l, d in zip(ACTION_LABELS, r['action_diff']))
        sig = 'OK' if r['signs_agree'] else 'FLIP'
        print(f"{r['scenario']:<25} {r['max_abs_diff']:>8.3f}  {r['mean_abs_diff']:>9.3f}  {sig:>6}  {per}")

    # Pass/fail
    overall_max = max(r['max_abs_diff'] for r in report)
    overall_mean = float(np.mean([r['mean_abs_diff'] for r in report]))
    all_signs_ok = all(r['signs_agree'] for r in report)
    print(f"\nOverall: max={overall_max:.3f}, mean={overall_mean:.3f}, signs_ok={all_signs_ok}")
    print(f"Pass criteria: max < {PASS_MAX_DRIFT}, mean < {PASS_MEAN_DRIFT}, signs all ok")
    if overall_max < PASS_MAX_DRIFT and overall_mean < PASS_MEAN_DRIFT and all_signs_ok:
        print('PASS')
    else:
        print('FAIL — investigate')


if __name__ == '__main__':
    main()
