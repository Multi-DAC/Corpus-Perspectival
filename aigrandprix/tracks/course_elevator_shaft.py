"""
Elevator Shaft — 15-Gate Vertical Variation Course
Designed by Clayton (Feb 10, 2026)

Emphasis: Climbs, dives, gates at different altitudes
Tests 3D spatial awareness and vertical maneuvering.
"""

import numpy as np

COURSE = {
    "name": "Elevator Shaft",
    "description": "15-gate vertical variation course — climbs, dives, altitude changes",
    "gate_radius": 1.5,
    "gates": [
        {"pos": [0, 0, 1], "orient": [1, 0, 0], "label": "G1: Start"},
        {"pos": [5, 0, 5], "orient": [0.7, 0, 0.7], "label": "G2: 45° Climb Angle"},
        {"pos": [5, 0, 10], "orient": [0, 0, 1], "label": "G3: Pure Vertical Pass"},
        {"pos": [5, 3, 10], "orient": [0, 1, 0], "label": "G4: High-altitude Pivot"},
        {"pos": [5, 6, 8], "orient": [0, 0, -1], "label": "G5: Power Loop Descent"},
        {"pos": [5, 6, 3], "orient": [0, 0, -1], "label": "G6: Sustained Dive"},
        {"pos": [8, 6, 1], "orient": [1, 0, 0], "label": "G7: Floor Level Leveling"},
        {"pos": [15, 6, 1], "orient": [1, 0, 0], "label": "G8: Sprint Stage"},
        {"pos": [18, 6, 6], "orient": [0.3, 0, 0.95], "label": "G9: Extreme Pitch-up"},
        {"pos": [18, 10, 10], "orient": [0, 1, 0], "label": "G10: Top Shelf Leveling"},
        {"pos": [15, 10, 10], "orient": [-1, 0, 0], "label": "G11: Negative Direction"},
        {"pos": [10, 10, 5], "orient": [-0.7, 0, -0.7], "label": "G12: High-speed Glide"},
        {"pos": [5, 10, 1], "orient": [0, 0, -1], "label": "G13: Vertical Finishing Dive"},
        {"pos": [0, 5, 1], "orient": [-1, 0, 0], "label": "G14: Ground Sweep"},
        {"pos": [-5, 0, 1.5], "orient": [-1, 0, 0], "label": "G15: Exit"},
    ]
}


def get_gates():
    return np.array([g["pos"] for g in COURSE["gates"]], dtype=np.float32)

def get_orientations():
    return np.array([g["orient"] for g in COURSE["gates"]], dtype=np.float32)

def get_gate_labels():
    return [g["label"] for g in COURSE["gates"]]


if __name__ == "__main__":
    gates = get_gates()
    print(f"Elevator Shaft: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
