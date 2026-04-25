"""
Stage 2 — detector × adapter integration smoke test.

Compares the 30-dim observation produced by the full vision pipeline
(synthetic_camera → gate_detector → CompetitionAdapter.build_observation)
against the ground-truth observation that ImprovedObsWrapper.observation
would produce for the same drone state + gate configuration. The trained
policy was fit to ImprovedObsWrapper's output, so any per-dim divergence
between the two streams is a wiring bug or a precision tax.

For each scenario (drone state + gate position/orientation), we:
  1. Compute the state-based obs matching ImprovedObsWrapper exactly.
  2. Render synthetic camera, detect, build vision-based obs via adapter.
  3. Diff per-dim.

The 30 dims, with their slice index, are:
  [0:3]    body-frame velocity
  [3:6]    angular velocity
  [6:9]    gravity in body frame (attitude)
  [9:12]   next gate in body frame
  [12]     distance to next gate
  [13:16]  next-next gate in body frame
  [16]     scalar speed
  [17]     course progress
  [18:21]  next gate in world frame
  [21:24]  forward direction
  [24]     time since last gate
  [25]     closing speed (signed; +approach in training, sign matters)
  [26:29]  gate orientation in body frame
  [29]     gate alignment (vel·gate_orient_world)
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

from synthetic_camera import SyntheticCamera
from gate_detector import GateDetector, GateDetectorConfig
from adapter import CompetitionAdapter, Telemetry
from drone_env_v2 import quat_rotate_np


IMG_W, IMG_H, FOV = 640, 480, 90.0

DIM_LABELS = [
    *['vel_body_x', 'vel_body_y', 'vel_body_z'],
    *['omega_x', 'omega_y', 'omega_z'],
    *['g_body_x', 'g_body_y', 'g_body_z'],
    *['rel_gate_body_x', 'rel_gate_body_y', 'rel_gate_body_z'],
    'dist_to_gate',
    *['rel_next_body_x', 'rel_next_body_y', 'rel_next_body_z'],
    'speed', 'progress',
    *['rel_gate_world_x', 'rel_gate_world_y', 'rel_gate_world_z'],
    *['forward_world_x', 'forward_world_y', 'forward_world_z'],
    'time_since_gate', 'speed_toward',
    *['gate_orient_body_x', 'gate_orient_body_y', 'gate_orient_body_z'],
    'gate_alignment',
]
assert len(DIM_LABELS) == 30


def state_based_obs(pos, vel, q, omega, gate_pos, gate_orient_world,
                    next_gate_pos=None,
                    last_gate_time=0.0, current_time=0.0,
                    progress=0.0):
    """Reproduces ImprovedObsWrapper.observation exactly for a single timestep."""
    q_conj = np.array([q[0], -q[1], -q[2], -q[3]])

    vel_body = quat_rotate_np(q_conj, vel)
    g_world = np.array([0.0, 0.0, -9.81])
    g_body = quat_rotate_np(q_conj, g_world)
    forward_body = np.array([0.0, 0.0, 1.0])
    forward_world = quat_rotate_np(q, forward_body)

    rel_gate_world = gate_pos - pos
    rel_gate_body = quat_rotate_np(q_conj, rel_gate_world)
    dist_to_gate = float(np.linalg.norm(rel_gate_world))
    speed_toward = float(-np.dot(vel, rel_gate_world / (dist_to_gate + 1e-6)))
    gate_orient_body = quat_rotate_np(q_conj, gate_orient_world)

    speed = float(np.linalg.norm(vel))
    if speed > 0.1:
        gate_alignment = float(np.dot(vel / speed, gate_orient_world))
    else:
        gate_alignment = 0.0

    if next_gate_pos is not None:
        rel_next_body = quat_rotate_np(q_conj, next_gate_pos - pos)
    else:
        rel_next_body = rel_gate_body

    time_since_gate = current_time - last_gate_time

    return np.array([
        *vel_body, *omega, *g_body,
        *rel_gate_body, dist_to_gate,
        *rel_next_body,
        speed, progress,
        *rel_gate_world, *forward_world,
        time_since_gate, speed_toward,
        *gate_orient_body, gate_alignment,
    ], dtype=np.float32)


def vision_based_obs(scenario, cam, det, adapter):
    """Run synthetic_camera → detector → adapter; return 30-dim obs and metadata."""
    pos, vel, q, omega = scenario['pos'], scenario['vel'], scenario['q'], scenario['omega']
    gate_pos = scenario['gate_pos']
    gate_orient_world = scenario['gate_orient_world']

    # Position the camera at the drone's pose, render gate(s) in world.
    img = cam.render(
        pos, q,
        [gate_pos] + ([scenario['next_gate_pos']] if scenario.get('next_gate_pos') is not None else []),
        [gate_orient_world] + ([scenario.get('next_gate_orient_world', gate_orient_world)] if scenario.get('next_gate_pos') is not None else []),
        current_gate_idx=0, add_noise=True,
    )
    detections = det.detect(img)
    primary = detections[0]

    gate_pos_body = None
    gate_distance = None
    gate_orient_body = None
    next_gate_pos_body = None
    if primary.found and primary.position_3d is not None:
        cam_pos = primary.position_3d
        # Camera frame (x=right, y=down, z=forward) → body frame (x=fwd, y=left, z=up)
        gate_pos_body = np.array([cam_pos[2], -cam_pos[0], -cam_pos[1]])
        gate_distance = float(primary.distance)
        # Gate normal (facing direction) in body frame — what the policy expects
        if primary.normal_camera is not None:
            n = primary.normal_camera
            gate_orient_body = np.array([n[2], -n[0], -n[1]])
        else:
            cam_b = primary.bearing_body
            gate_orient_body = np.array([cam_b[2], -cam_b[0], -cam_b[1]])
    if len(detections) > 1 and detections[1].found and detections[1].position_3d is not None:
        cam2 = detections[1].position_3d
        next_gate_pos_body = np.array([cam2[2], -cam2[0], -cam2[1]])

    telem = Telemetry(position=pos, velocity=vel, orientation=q, angular_velocity=omega)
    obs = adapter.build_observation(
        telemetry=telem,
        gate_pos_body=gate_pos_body,
        gate_distance=gate_distance,
        gate_orientation_body=gate_orient_body,
        next_gate_pos_body=next_gate_pos_body,
    )
    return obs, primary.found, gate_distance


def make_scenarios():
    """Mix of scenarios that exercise all 30 dims with non-trivial values."""
    scenarios = []
    rng = np.random.default_rng(0)
    # Hand-crafted edge cases
    scenarios.append(dict(
        name='hover_5m_ahead',
        pos=np.zeros(3), vel=np.zeros(3),
        q=np.array([1., 0, 0, 0]), omega=np.zeros(3),
        gate_pos=np.array([5., 0, 0]),
        gate_orient_world=np.array([1., 0, 0]),
    ))
    scenarios.append(dict(
        name='approach_8m_5mps',
        pos=np.zeros(3), vel=np.array([5., 0, 0]),
        q=np.array([1., 0, 0, 0]), omega=np.zeros(3),
        gate_pos=np.array([8., 0, 0]),
        gate_orient_world=np.array([1., 0, 0]),
    ))
    scenarios.append(dict(
        name='retreat_6m_-3mps',
        pos=np.zeros(3), vel=np.array([-3., 0, 0]),
        q=np.array([1., 0, 0, 0]), omega=np.zeros(3),
        gate_pos=np.array([6., 0, 0]),
        gate_orient_world=np.array([1., 0, 0]),
    ))
    scenarios.append(dict(
        name='offaxis_6m_yaw15',
        pos=np.zeros(3), vel=np.array([4., 1., 0.]),
        q=np.array([1., 0, 0, 0]), omega=np.zeros(3),
        gate_pos=6 * np.array([np.cos(np.radians(15)), np.sin(np.radians(15)), 0]),
        gate_orient_world=np.array([np.cos(np.radians(15)), np.sin(np.radians(15)), 0]),
    ))
    scenarios.append(dict(
        name='climbing_8m',
        pos=np.zeros(3), vel=np.array([3., 0., 1.5]),
        q=np.array([1., 0, 0, 0]), omega=np.array([0.1, 0.0, 0.0]),
        gate_pos=np.array([8., 0., 1.5]),
        gate_orient_world=np.array([1., 0, 0]),
    ))
    return scenarios


def diff_obs(state_obs, vision_obs):
    diffs = vision_obs - state_obs
    return [
        {
            'dim': i, 'label': DIM_LABELS[i],
            'state': float(state_obs[i]),
            'vision': float(vision_obs[i]),
            'diff': float(diffs[i]),
            'rel': float(diffs[i] / abs(state_obs[i])) if abs(state_obs[i]) > 1e-3 else None,
        }
        for i in range(30)
    ]


def main():
    cam = SyntheticCamera(IMG_W, IMG_H, FOV)
    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(IMG_W, IMG_H, FOV)
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
        per_dim = diff_obs(state_obs, vision_obs)
        big_diffs = [d for d in per_dim if abs(d['diff']) > 0.05]
        report.append({
            'scenario': s['name'],
            'detection_found': bool(found),
            'pnp_distance_m': est_dist,
            'true_distance_m': float(np.linalg.norm(s['gate_pos'] - s['pos'])),
            'max_abs_diff': float(np.max(np.abs(state_obs - vision_obs))),
            'big_diffs': big_diffs,
            'per_dim': per_dim,
        })

    out_dir = Path(__file__).parent / 'results'
    out_dir.mkdir(exist_ok=True)
    with open(out_dir / 'stage2_adapter_integration.json', 'w') as f:
        json.dump(report, f, indent=2)

    # Console summary: per-scenario, list dims with |diff| > 0.05
    print(f"\n{'Scenario':<25} {'found':>6} {'maxDiff':>9} {'BIG dims (>0.05)'}")
    for r in report:
        big = ', '.join(f"{d['label']}({d['diff']:+.2f})" for d in r['big_diffs'])
        print(f"{r['scenario']:<25} {str(r['detection_found']):>6} {r['max_abs_diff']:>8.3f}  {big}")


if __name__ == '__main__':
    main()
