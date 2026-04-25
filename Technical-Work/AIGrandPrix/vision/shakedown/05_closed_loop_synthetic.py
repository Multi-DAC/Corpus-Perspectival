"""
Stage 5 — closed-loop synthetic flight.

Stages 1–4 verified each layer in isolation: detector, adapter,
policy-on-static-obs, MAVSDK conversions on synthetic telemetry.
None of those exercised the *full loop* where errors compound:

    env state → render → detect → adapter → normalize → policy
              → MAVSDK round-trip → step env → next state

If sub-pixel PnP error introduces 0.02 m drift per frame, does that
compound into divergence over a 60s episode? Does the policy recover
when the vision pipeline drops a gate detection? Does the
StubMAVSDKClient round-trip survive 5000 calls without state leak?

Method:
For each seed, run two parallel rollouts of the same InfiniteGateEnv:
  - Reference: env built-in obs (matches ImprovedObsWrapper) → policy
  - Closed-loop: render synthetic camera → detect → adapter → policy,
    round-trip the action through StubMAVSDKClient.send_policy_action
Both runs step the env with the same policy-action format (CTBR).

Compare:
  - Gates passed (vision vs reference)
  - Position trajectory divergence over time
  - Per-step action drift
  - Detection success rate
  - Episode survival

Stub-MAVSDK is the right target for Stage 5: real PX4 SITL is deferred
until the DCL sim drops (per ROADMAP_v2 §10 E1). The stub validates
everything we own — vision pipeline, adapter, policy invocation,
MAVSDK frame-conversion API surface — without the install/maintenance
cost of a SITL stack we'll discard the moment DCL ships.
"""

import os
import sys
import json
import pickle
import time
from pathlib import Path
import numpy as np

VISION_DIR = Path(__file__).resolve().parent.parent
SIM_DIR = VISION_DIR.parent / 'sim'
RL_DIR = VISION_DIR.parent / 'rl'
sys.path.insert(0, str(VISION_DIR))
sys.path.insert(0, str(SIM_DIR))
sys.path.insert(0, str(RL_DIR))

from synthetic_camera import SyntheticCamera
from gate_detector import GateDetector, GateDetectorConfig
from adapter import CompetitionAdapter, Telemetry
from mavsdk_client import StubMAVSDKClient, MAVTelemetry
from infinite_gate_env import InfiniteGateEnv

from stable_baselines3 import PPO


PHASE2_RUN = SIM_DIR / 'runs' / 'infinite_v3_phase2_60M_1777095742'
CHECKPOINT_STEP = 67500016
POLICY_PATH = PHASE2_RUN / 'checkpoints' / f'ppo_phase2_{CHECKPOINT_STEP}_steps.zip'
VECNORM_PATH = PHASE2_RUN / 'checkpoints' / f'ppo_phase2_{CHECKPOINT_STEP}_steps_vecnorm.pkl'

IMG_W, IMG_H, FOV = 640, 480, 90.0
RESULTS_DIR = Path(__file__).resolve().parent / 'results'


# --------------------------------------------------------------------
# Obs normalization (reproduces VecNormalize.normalize_obs single-vec)
# --------------------------------------------------------------------

def load_vecnorm_stats(path: Path):
    with open(path, 'rb') as f:
        vn = pickle.load(f)
    return vn.obs_rms, float(vn.clip_obs), float(vn.epsilon)


def normalize_obs(obs, obs_rms, clip_obs, epsilon):
    normed = (obs - obs_rms.mean) / np.sqrt(obs_rms.var + epsilon)
    return np.clip(normed, -clip_obs, clip_obs).astype(np.float32)


# --------------------------------------------------------------------
# Vision pipeline: env state → camera → detection → adapter obs
# --------------------------------------------------------------------

def render_and_observe(env, cam, det, adapter):
    """Render synthetic camera from env state, run detection + adapter."""
    base = env._base_env
    state = base.state
    pos = state[0:3].copy()
    vel = state[3:6].copy()
    q = state[6:10].copy()
    omega = state[10:13].copy()

    current = base.current_gate
    n_gates = base.n_gates

    # Render up to 2 visible gates (current + lookahead)
    visible_gates = []
    visible_orients = []
    for i in range(current, min(current + 2, n_gates)):
        visible_gates.append(env.gates[i])
        visible_orients.append(env.gate_orientations[i])

    if not visible_gates:
        # No gates left — return zeroed vision obs
        telem = Telemetry(position=pos, velocity=vel, orientation=q,
                          angular_velocity=omega)
        obs = adapter.build_observation(telemetry=telem)
        return obs, False, None

    img = cam.render(pos, q, visible_gates, visible_orients,
                     current_gate_idx=0, add_noise=True)
    detections = det.detect(img)
    primary = detections[0] if detections else None

    gate_pos_body = None
    gate_distance = None
    gate_orient_body = None
    next_gate_pos_body = None

    if primary is not None and primary.found and primary.position_3d is not None:
        cam_pos = primary.position_3d
        gate_pos_body = np.array([cam_pos[2], -cam_pos[0], -cam_pos[1]])
        gate_distance = float(primary.distance)
        if primary.normal_camera is not None:
            n = primary.normal_camera
            gate_orient_body = np.array([n[2], -n[0], -n[1]])
        else:
            cam_b = primary.bearing_body
            gate_orient_body = np.array([cam_b[2], -cam_b[0], -cam_b[1]])

    if (len(detections) > 1 and detections[1].found
            and detections[1].position_3d is not None):
        cam2 = detections[1].position_3d
        next_gate_pos_body = np.array([cam2[2], -cam2[0], -cam2[1]])

    telem = Telemetry(position=pos, velocity=vel, orientation=q,
                      angular_velocity=omega)
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=gate_pos_body,
        gate_distance=gate_distance,
        gate_orientation_body=gate_orient_body,
        next_gate_pos_body=next_gate_pos_body,
    )
    detected = (primary is not None and primary.found
                and primary.position_3d is not None)
    return obs, detected, gate_distance


# --------------------------------------------------------------------
# MAVSDK round-trip exercise
# --------------------------------------------------------------------

def mavsdk_roundtrip(stub_client, adapter, policy_action):
    """Convert policy action → CompetitionAction → stub.send_policy_action.

    Returns the original policy action unchanged. The point is to exercise
    the conversion + send path without an exception, not to alter dynamics.
    StubMAVSDKClient.send_policy_action is a no-op; in a real flight this
    would dispatch to the autopilot.
    """
    cmd = adapter.to_competition_action(policy_action)
    # send_policy_action expects the policy action (CTBR [-1,1]^4)
    stub_client.send_policy_action(np.asarray(policy_action, dtype=np.float32))
    return cmd


# --------------------------------------------------------------------
# Episode runners
# --------------------------------------------------------------------

def _yaw_quat_toward(pos, target):
    """Return [w,x,y,z] quat for a yaw rotation about world-z that points
    body-x at `target` from `pos`. Body z stays world-up (level flight)."""
    d = target - pos
    yaw = float(np.arctan2(d[1], d[0]))
    return np.array([np.cos(yaw / 2), 0.0, 0.0, np.sin(yaw / 2)])


def _orient_drone_to_first_gate(env):
    """Force drone init attitude to face the first gate.

    InfiniteGateEnv places the drone behind the first gate, but leaves
    initial_attitude at the wrapper default (identity = facing world +x).
    With a randomized first-gate heading that puts the gate out of frame
    on most seeds. Real flight would never start with the camera pointed
    away from gate 1; we mirror that here. Both reference and closed-loop
    runs share this fixup so the comparison stays apples-to-apples.
    """
    base = env._base_env
    pos = base.state[0:3]
    gate0 = env.gates[base.current_gate]
    base.state[6:10] = _yaw_quat_toward(pos, gate0)
    base.prev_dist_to_gate = float(np.linalg.norm(pos - gate0))


def _obs_after_reset(env):
    """Recompute the wrapper obs after we've mutated the underlying state.

    ImprovedObsWrapper reads env.state directly inside .observation(); calling
    its .observation(None) (with the inner env state already updated) returns
    a fresh obs that reflects our quaternion override.
    """
    return env._obs_wrapper.observation(None)


def run_reference_episode(env, model, obs_rms, clip_obs, epsilon,
                          stub_client, adapter, max_steps=5000, seed=0):
    """Reference: env built-in obs → policy → step. No vision pipeline."""
    obs, info = env.reset(seed=seed)
    _orient_drone_to_first_gate(env)
    obs = _obs_after_reset(env)
    stub_client.init_flight()
    adapter.reset()
    trajectory = {
        'positions': [], 'actions': [], 'gates_passed': [],
        'rewards': [], 'terminated_step': None,
    }
    total_gates = 0
    for step in range(max_steps):
        normed = normalize_obs(obs, obs_rms, clip_obs, epsilon)
        action, _ = model.predict(normed, deterministic=True)
        action = np.asarray(action, dtype=np.float32).flatten()
        # Round-trip through MAVSDK (no-op for stub) — exercise the surface
        mavsdk_roundtrip(stub_client, adapter, action)
        trajectory['positions'].append(env._base_env.state[0:3].copy())
        trajectory['actions'].append(action.copy())
        obs, reward, terminated, truncated, info = env.step(action)
        total_gates = info.get('gates_passed', total_gates)
        trajectory['gates_passed'].append(total_gates)
        trajectory['rewards'].append(float(reward))
        if terminated or truncated:
            trajectory['terminated_step'] = step + 1
            break
    trajectory['gates_passed_final'] = total_gates
    trajectory['steps'] = len(trajectory['actions'])
    return trajectory


def run_closed_loop_episode(env, model, obs_rms, clip_obs, epsilon,
                            cam, det, adapter, stub_client,
                            max_steps=5000, seed=0):
    """Closed loop: render → detect → adapter obs → policy → MAVSDK → step."""
    env.reset(seed=seed)
    _orient_drone_to_first_gate(env)
    stub_client.init_flight()
    adapter.reset()
    trajectory = {
        'positions': [], 'actions': [], 'gates_passed': [],
        'rewards': [], 'detections': [], 'gate_distances': [],
        'terminated_step': None,
    }
    total_gates = 0
    detections_count = 0
    for step in range(max_steps):
        vision_obs, detected, gate_dist = render_and_observe(env, cam, det, adapter)
        if detected:
            detections_count += 1
        normed = normalize_obs(vision_obs, obs_rms, clip_obs, epsilon)
        action, _ = model.predict(normed, deterministic=True)
        action = np.asarray(action, dtype=np.float32).flatten()
        mavsdk_roundtrip(stub_client, adapter, action)
        trajectory['positions'].append(env._base_env.state[0:3].copy())
        trajectory['actions'].append(action.copy())
        trajectory['detections'].append(bool(detected))
        trajectory['gate_distances'].append(
            float(gate_dist) if gate_dist is not None else None)
        obs, reward, terminated, truncated, info = env.step(action)
        total_gates = info.get('gates_passed', total_gates)
        trajectory['gates_passed'].append(total_gates)
        trajectory['rewards'].append(float(reward))
        if terminated or truncated:
            trajectory['terminated_step'] = step + 1
            break
    trajectory['gates_passed_final'] = total_gates
    trajectory['steps'] = len(trajectory['actions'])
    trajectory['detection_rate'] = detections_count / max(len(trajectory['actions']), 1)
    return trajectory


# --------------------------------------------------------------------
# Comparison + reporting
# --------------------------------------------------------------------

def summarize(ref_traj, vis_traj):
    """Compute divergence + comparison metrics over the shared step prefix."""
    n = min(len(ref_traj['positions']), len(vis_traj['positions']))
    pos_ref = np.asarray(ref_traj['positions'][:n])
    pos_vis = np.asarray(vis_traj['positions'][:n])
    act_ref = np.asarray(ref_traj['actions'][:n])
    act_vis = np.asarray(vis_traj['actions'][:n])

    pos_drift = np.linalg.norm(pos_vis - pos_ref, axis=1)
    act_drift = np.abs(act_vis - act_ref)

    return {
        'steps_ref': ref_traj['steps'],
        'steps_vis': vis_traj['steps'],
        'gates_ref': ref_traj['gates_passed_final'],
        'gates_vis': vis_traj['gates_passed_final'],
        'detection_rate_vis': vis_traj.get('detection_rate', None),
        'pos_drift_mean_m': float(np.mean(pos_drift)) if n else None,
        'pos_drift_max_m': float(np.max(pos_drift)) if n else None,
        'pos_drift_at_n50': float(pos_drift[min(50, n - 1)]) if n else None,
        'pos_drift_at_n500': float(pos_drift[min(500, n - 1)]) if n else None,
        'pos_drift_final': float(pos_drift[-1]) if n else None,
        'act_drift_mean_per_dim': act_drift.mean(axis=0).tolist() if n else None,
        'act_drift_max_per_dim': act_drift.max(axis=0).tolist() if n else None,
        'reward_ref': float(np.sum(ref_traj['rewards'])),
        'reward_vis': float(np.sum(vis_traj['rewards'])),
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
    obs_rms, clip_obs, epsilon = load_vecnorm_stats(VECNORM_PATH)
    print(f'  obs_rms.mean[:6] = {obs_rms.mean[:6]}')
    print(f'  clip_obs={clip_obs}, epsilon={epsilon}')

    cam = SyntheticCamera(IMG_W, IMG_H, FOV)
    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(IMG_W, IMG_H, FOV)
    adapter = CompetitionAdapter()
    stub_client = StubMAVSDKClient()

    # 5 seeds, max_steps=3000 each (= 6s of physics @ 500Hz)
    seeds = [0, 1, 2, 3, 4]
    max_steps = 3000

    results = []
    print('\n=== Stage 5 closed-loop synthetic flight ===\n')
    for seed in seeds:
        print(f'[seed {seed}] reference rollout...', flush=True)
        env_ref = InfiniteGateEnv(
            gate_radius=0.75, max_steps=max_steps, dt=0.002,
            domain_rand=False, adaptive_curriculum=False, seed=seed,
        )
        t0 = time.monotonic()
        ref_traj = run_reference_episode(
            env_ref, model, obs_rms, clip_obs, epsilon,
            stub_client, adapter, max_steps=max_steps, seed=seed,
        )
        t_ref = time.monotonic() - t0
        env_ref.close()

        print(f'[seed {seed}] closed-loop (vision) rollout...', flush=True)
        env_vis = InfiniteGateEnv(
            gate_radius=0.75, max_steps=max_steps, dt=0.002,
            domain_rand=False, adaptive_curriculum=False, seed=seed,
        )
        t0 = time.monotonic()
        vis_traj = run_closed_loop_episode(
            env_vis, model, obs_rms, clip_obs, epsilon,
            cam, det, adapter, stub_client,
            max_steps=max_steps, seed=seed,
        )
        t_vis = time.monotonic() - t0
        env_vis.close()

        summary = summarize(ref_traj, vis_traj)
        summary['seed'] = seed
        summary['runtime_ref_s'] = t_ref
        summary['runtime_vis_s'] = t_vis
        results.append(summary)

        print(f'  gates: ref={summary["gates_ref"]} vis={summary["gates_vis"]} | '
              f'steps: ref={summary["steps_ref"]} vis={summary["steps_vis"]} | '
              f'det_rate={summary["detection_rate_vis"]:.2%} | '
              f'pos_drift_max={summary["pos_drift_max_m"]:.3f}m | '
              f't_vis={t_vis:.1f}s')

    # Aggregate
    agg = {
        'n_seeds': len(seeds),
        'gates_ref_mean': float(np.mean([r['gates_ref'] for r in results])),
        'gates_vis_mean': float(np.mean([r['gates_vis'] for r in results])),
        'gates_ref_total': int(sum(r['gates_ref'] for r in results)),
        'gates_vis_total': int(sum(r['gates_vis'] for r in results)),
        'detection_rate_mean': float(np.mean([r['detection_rate_vis'] for r in results])),
        'pos_drift_max_overall': float(np.max([r['pos_drift_max_m'] for r in results])),
        'pos_drift_mean_at_n50': float(np.mean([r['pos_drift_at_n50'] for r in results])),
        'pos_drift_mean_at_n500': float(np.mean([r['pos_drift_at_n500'] for r in results])),
        'reward_ref_mean': float(np.mean([r['reward_ref'] for r in results])),
        'reward_vis_mean': float(np.mean([r['reward_vis'] for r in results])),
    }

    print('\n=== Aggregate (5 seeds) ===')
    for k, v in agg.items():
        print(f'  {k}: {v}')

    out = {
        'checkpoint': str(POLICY_PATH.name),
        'config': {
            'image': [IMG_W, IMG_H, FOV],
            'max_steps': max_steps,
            'seeds': seeds,
            'gate_radius': 0.75,
            'dt': 0.002,
        },
        'per_seed': results,
        'aggregate': agg,
    }

    RESULTS_DIR.mkdir(exist_ok=True)
    out_path = RESULTS_DIR / '05_closed_loop_synthetic.json'
    with open(out_path, 'w') as f:
        json.dump(out, f, indent=2, default=lambda x: x.tolist() if hasattr(x, 'tolist') else x)
    print(f'\nWrote {out_path}')


if __name__ == '__main__':
    main()
