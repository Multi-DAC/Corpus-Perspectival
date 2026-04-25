"""
Stage 3b — adapter x policy with a *Phase 2* checkpoint (graded outputs).

Stage 3 ran against baseline 60.4M (pre-F1, no VecNormalize) and got
zero action drift on every scenario — but the probe revealed the
baseline is bang-bang (40/50 saturated, 21 unique action vectors).
The clean pass was a weak signal: saturated outputs absorb small obs
deltas regardless of vision-pipeline correctness.

This script re-runs the comparison against a Phase 2 checkpoint trained
under F1 (VecNormalize). The expected outcome is:
  - non-trivial per-dim action drift between vision and state obs
  - drift magnitude small (vision pipeline is correct), traceable to
    stage-1b residual PnP precision tax (~0.02 m at 5m, ~0.04m at 10m)
  - signs agree on every dim
  - drift small enough to be acceptable in flight (TBD threshold)

Critical: Phase 2 was trained under VecNormalize, so the policy
expects normalized obs. We must load the matching vec_normalize.pkl
and normalize both state-based and vision-based obs before
predict().

Checkpoint chosen: 37.5M (peak per-maneuver aggregate 21.55 gates per
P96 trajectory data; representative of cured + capable regime).
"""

import os
import sys
import json
from pathlib import Path
import pickle
import numpy as np

VISION_DIR = Path(__file__).resolve().parent.parent
SIM_DIR = VISION_DIR.parent / 'sim'
sys.path.insert(0, str(VISION_DIR))
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(Path(__file__).parent))

from importlib import import_module
stage2 = import_module('02_adapter_integration')
state_based_obs = stage2.state_based_obs
vision_based_obs = stage2.vision_based_obs
make_scenarios = stage2.make_scenarios

from synthetic_camera import SyntheticCamera
from gate_detector import GateDetector, GateDetectorConfig
from adapter import CompetitionAdapter

from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv, VecNormalize


PHASE2_RUN = SIM_DIR / 'runs' / 'infinite_v3_phase2_60M_1777095742'
CHECKPOINT_STEP = 37500016
POLICY_PATH = PHASE2_RUN / 'checkpoints' / f'ppo_phase2_{CHECKPOINT_STEP}_steps.zip'
VECNORM_PATH = PHASE2_RUN / 'checkpoints' / f'ppo_phase2_{CHECKPOINT_STEP}_steps_vecnorm.pkl'

ACTION_LABELS = ['thrust', 'roll_rate', 'pitch_rate', 'yaw_rate']


def load_vecnorm_stats(path: Path):
    """Load VecNormalize and return its obs_rms + clip params for manual use."""
    with open(path, 'rb') as f:
        vn = pickle.load(f)
    return vn.obs_rms, float(vn.clip_obs), float(vn.epsilon)


def normalize_obs(obs, obs_rms, clip_obs, epsilon):
    """Reproduce VecNormalize.normalize_obs for a single un-batched obs."""
    normed = (obs - obs_rms.mean) / np.sqrt(obs_rms.var + epsilon)
    normed = np.clip(normed, -clip_obs, clip_obs)
    return normed.astype(np.float32)


def saturation_probe(model, obs_rms, clip_obs, epsilon, n=50, seed=42):
    """Sanity-check: is THIS policy bang-bang too? Sample random in-distribution
    obs (drawn from N(mean, var)) and count saturation."""
    rng = np.random.default_rng(seed)
    mean = obs_rms.mean
    std = np.sqrt(obs_rms.var + epsilon)
    actions = []
    for _ in range(n):
        raw_obs = mean + rng.normal(size=mean.shape) * std
        normed = normalize_obs(raw_obs.astype(np.float32), obs_rms, clip_obs, epsilon)
        a, _ = model.predict(normed, deterministic=True)
        actions.append(np.asarray(a).flatten())
    actions = np.array(actions)
    n_saturated = int(np.sum(np.all(np.abs(actions) > 0.99, axis=1)))
    n_unique = len(set(tuple(np.round(a, 3)) for a in actions))
    return {
        'n_trials': n,
        'n_fully_saturated': n_saturated,
        'pct_fully_saturated': 100.0 * n_saturated / n,
        'n_unique_action_vectors': n_unique,
        'mean_abs_action_per_dim': np.mean(np.abs(actions), axis=0).tolist(),
    }


def main():
    if not POLICY_PATH.exists():
        print(f'ERROR: policy not found at {POLICY_PATH}')
        sys.exit(1)
    if not VECNORM_PATH.exists():
        print(f'ERROR: vecnorm not found at {VECNORM_PATH}')
        sys.exit(1)

    print(f'Loading Phase 2 policy: {POLICY_PATH.name}')
    model = PPO.load(str(POLICY_PATH), device='cpu')
    print(f'  obs space: {model.observation_space}')
    print(f'  action space: {model.action_space}')

    print(f'Loading vec_normalize stats: {VECNORM_PATH.name}')
    obs_rms, clip_obs, epsilon = load_vecnorm_stats(VECNORM_PATH)
    print(f'  obs_rms.mean[:6] = {obs_rms.mean[:6]}')
    print(f'  obs_rms.var[:6]  = {obs_rms.var[:6]}')
    print(f'  clip_obs={clip_obs}, epsilon={epsilon}')

    # First: saturation probe — is this policy bang-bang too?
    sat = saturation_probe(model, obs_rms, clip_obs, epsilon, n=50)
    print(f'\nSaturation probe (50 random in-dist samples):')
    print(f'  fully-saturated: {sat["n_fully_saturated"]}/50 ({sat["pct_fully_saturated"]:.0f}%)')
    print(f'  unique action vectors: {sat["n_unique_action_vectors"]}/50')
    print(f'  mean |a| per dim: {[f"{x:.3f}" for x in sat["mean_abs_action_per_dim"]]}')

    cam = SyntheticCamera(640, 480, 90.0)
    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(640, 480, 90.0)
    adapter = CompetitionAdapter()

    scenarios = make_scenarios()
    report = []
    for s in scenarios:
        adapter.reset()
        state_obs_raw = state_based_obs(
            s['pos'], s['vel'], s['q'], s['omega'],
            s['gate_pos'], s['gate_orient_world'],
            next_gate_pos=s.get('next_gate_pos'),
        )
        vision_obs_raw, found, est_dist = vision_based_obs(s, cam, det, adapter)

        state_obs = normalize_obs(state_obs_raw, obs_rms, clip_obs, epsilon)
        vision_obs = normalize_obs(vision_obs_raw, obs_rms, clip_obs, epsilon)

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
            'state_obs_post_norm_max_abs': float(np.max(np.abs(state_obs))),
            'vision_obs_post_norm_max_abs': float(np.max(np.abs(vision_obs))),
        })

    out_dir = Path(__file__).parent / 'results'
    out_dir.mkdir(exist_ok=True)
    payload = {
        'checkpoint_step': CHECKPOINT_STEP,
        'checkpoint_path': str(POLICY_PATH.relative_to(SIM_DIR.parent)),
        'saturation_probe': sat,
        'scenarios': report,
    }
    with open(out_dir / 'stage3b_policy_comparison_phase2_37p5M.json', 'w') as f:
        json.dump(payload, f, indent=2)

    print(f"\n{'Scenario':<25} {'maxDrift':>9} {'meanDrift':>10} {'signs':>6}  per-dim diff")
    for r in report:
        per = ', '.join(f"{l}({d:+.3f})" for l, d in zip(ACTION_LABELS, r['action_diff']))
        sig = 'OK' if r['signs_agree'] else 'FLIP'
        print(f"{r['scenario']:<25} {r['max_abs_diff']:>8.3f}  {r['mean_abs_diff']:>9.3f}  {sig:>6}  {per}")

    overall_max = max(r['max_abs_diff'] for r in report)
    overall_mean = float(np.mean([r['mean_abs_diff'] for r in report]))
    all_signs_ok = all(r['signs_agree'] for r in report)
    print(f"\nOverall: max={overall_max:.3f}, mean={overall_mean:.3f}, signs_ok={all_signs_ok}")
    print(f"Saturation: {sat['n_fully_saturated']}/50 fully-saturated, {sat['n_unique_action_vectors']} unique vectors")
    if sat['n_fully_saturated'] < 25 and sat['n_unique_action_vectors'] > 25:
        print('GRADED policy confirmed — drift signal is REAL (not absorbed by saturation)')
    else:
        print('Policy still bang-bang — drift signal interpretation needs care')


if __name__ == '__main__':
    main()
