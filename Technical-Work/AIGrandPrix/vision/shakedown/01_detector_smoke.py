"""
Stage 1 — synthetic_camera × gate_detector smoke test.

Sweeps a single gate across (distance × yaw_angle × height_offset) and
measures, per cell:
  - detection rate (was a gate found?)
  - PnP distance error (|estimated - true|)
  - PnP lateral error (|estimated_xy - true_xy|)
  - bearing error (degrees between estimated and true bearing)

Drone is at origin looking along world +x. Gate is placed at
(d*cos(yaw), d*sin(yaw), h_offset) facing back toward the drone.
N samples per cell to average over the synthetic-camera background noise.

Per shakedown success criteria (vision/shakedown/README.md):
  - detection rate >= 95% for d <= 8m
  - PnP error <= 0.3m at 5m, <= 0.8m at 10m

Writes JSON results to results/stage1_detector_smoke.json and a
summary to STATUS.md.
"""

import os
import sys
import json
from pathlib import Path
import numpy as np

VISION_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(VISION_DIR))

from synthetic_camera import SyntheticCamera
from gate_detector import GateDetector, GateDetectorConfig


DISTANCES = [2.0, 4.0, 6.0, 8.0, 10.0, 15.0]
YAWS_DEG = [-30.0, -15.0, 0.0, 15.0, 30.0]
HEIGHT_OFFSETS = [-1.0, 0.0, 1.0]
SAMPLES_PER_CELL = 8
IMG_W, IMG_H, FOV = 640, 480, 90.0


def make_pipeline():
    cam = SyntheticCamera(width=IMG_W, height=IMG_H, fov_deg=FOV)
    det = GateDetector(GateDetectorConfig())
    det.set_camera_from_fov(IMG_W, IMG_H, FOV)
    return cam, det


def true_bearing_camera_frame(gate_world):
    # drone at origin, body x = world x, so gate body = gate world
    body = gate_world
    # camera convention: cam_x = -body_y, cam_y = -body_z, cam_z = body_x
    cam = np.array([-body[1], -body[2], body[0]])
    return cam / (np.linalg.norm(cam) + 1e-9)


def run_cell(cam, det, distance, yaw_deg, h_offset, n):
    yaw = np.radians(yaw_deg)
    gate_world = np.array([distance * np.cos(yaw), distance * np.sin(yaw), h_offset])
    # Gate faces back toward the drone
    facing = -gate_world / (np.linalg.norm(gate_world) + 1e-9)
    drone_pos = np.array([0.0, 0.0, 0.0])
    drone_quat = np.array([1.0, 0.0, 0.0, 0.0])

    true_dist = float(np.linalg.norm(gate_world))
    true_bear_cam = true_bearing_camera_frame(gate_world)

    n_found = 0
    dist_errs, lat_errs, bear_errs = [], [], []

    for k in range(n):
        np.random.seed(1000 + k)
        img = cam.render(
            drone_pos, drone_quat, [gate_world], [facing],
            current_gate_idx=0, add_noise=True,
        )
        d = det.detect_primary(img)
        if not d.found or d.position_3d is None:
            continue
        n_found += 1
        est_pos_cam = d.position_3d
        est_dist = float(np.linalg.norm(est_pos_cam))
        dist_errs.append(abs(est_dist - true_dist))
        # lateral error in camera-plane (x_cam, y_cam) — true vs estimated
        true_pos_cam = true_dist * true_bear_cam
        lat_errs.append(float(np.linalg.norm(
            est_pos_cam[:2] - true_pos_cam[:2]
        )))
        cos = float(np.clip(np.dot(d.bearing_body, true_bear_cam), -1.0, 1.0))
        bear_errs.append(float(np.degrees(np.arccos(cos))))

    return {
        'distance_m': distance,
        'yaw_deg': yaw_deg,
        'height_offset_m': h_offset,
        'true_dist_m': true_dist,
        'n_samples': n,
        'detection_rate': n_found / n,
        'mean_dist_err_m': float(np.mean(dist_errs)) if dist_errs else None,
        'p95_dist_err_m': float(np.percentile(dist_errs, 95)) if dist_errs else None,
        'mean_lateral_err_m': float(np.mean(lat_errs)) if lat_errs else None,
        'mean_bearing_err_deg': float(np.mean(bear_errs)) if bear_errs else None,
    }


def main():
    cam, det = make_pipeline()
    cells = []
    for d in DISTANCES:
        for y in YAWS_DEG:
            for h in HEIGHT_OFFSETS:
                cells.append(run_cell(cam, det, d, y, h, SAMPLES_PER_CELL))

    out_dir = Path(__file__).parent / 'results'
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / 'stage1_detector_smoke.json'

    # Summaries by distance band
    by_dist = {}
    for c in cells:
        by_dist.setdefault(c['distance_m'], []).append(c)

    summary = {}
    for d, group in sorted(by_dist.items()):
        det_rate = float(np.mean([g['detection_rate'] for g in group]))
        ds = [g['mean_dist_err_m'] for g in group if g['mean_dist_err_m'] is not None]
        ls = [g['mean_lateral_err_m'] for g in group if g['mean_lateral_err_m'] is not None]
        bs = [g['mean_bearing_err_deg'] for g in group if g['mean_bearing_err_deg'] is not None]
        summary[d] = {
            'detection_rate': det_rate,
            'mean_dist_err_m': float(np.mean(ds)) if ds else None,
            'mean_lateral_err_m': float(np.mean(ls)) if ls else None,
            'mean_bearing_err_deg': float(np.mean(bs)) if bs else None,
            'n_cells': len(group),
        }

    payload = {
        'config': {
            'image': [IMG_W, IMG_H], 'fov_deg': FOV,
            'distances': DISTANCES, 'yaws_deg': YAWS_DEG,
            'height_offsets': HEIGHT_OFFSETS,
            'samples_per_cell': SAMPLES_PER_CELL,
        },
        'by_distance': summary,
        'cells': cells,
    }
    with open(out_path, 'w') as f:
        json.dump(payload, f, indent=2)

    print(f'\nWrote {out_path}\n')
    print(f"{'dist':>6} {'det%':>6} {'distErr':>8} {'latErr':>8} {'bearErr':>8}")
    for d, s in sorted(summary.items()):
        print(f"{d:>6.1f} {100*s['detection_rate']:>5.1f}% "
              f"{(s['mean_dist_err_m'] or float('nan')):>7.3f}m "
              f"{(s['mean_lateral_err_m'] or float('nan')):>7.3f}m "
              f"{(s['mean_bearing_err_deg'] or float('nan')):>7.2f}°")


if __name__ == '__main__':
    main()
