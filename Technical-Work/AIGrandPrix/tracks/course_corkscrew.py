"""
The Corkscrew — 15-Gate Tight Hairpin Course
Designed by Clayton (Feb 10, 2026)

Emphasis: Aggressive deceleration + banking
Tight turns, 120°+ direction changes, helix sections.
"""

import numpy as np

COURSE = {
    "name": "The Corkscrew",
    "description": "15-gate tight hairpin course — aggressive deceleration + banking",
    "gate_radius": 1.5,
    "gates": [
        {"pos": [0, 0, 1.5], "orient": [1, 0, 0], "label": "G1: Entry"},
        {"pos": [4, 1, 1.5], "orient": [0.8, 0.6, 0], "label": "G2: Tightening Radius"},
        {"pos": [6, 4, 1.5], "orient": [-0.5, 0.86, 0], "label": "G3: 120° Hairpin"},
        {"pos": [4, 6, 2.0], "orient": [-1, 0, 0.2], "label": "G4: Climbing Bank"},
        {"pos": [1, 5, 2.5], "orient": [0.5, -0.86, 0.2], "label": "G5: Helix Ascent"},
        {"pos": [0, 2, 3.0], "orient": [1, 0, 0], "label": "G6: Peak Apex"},
        {"pos": [2, 0, 2.5], "orient": [0.8, -0.6, -0.2], "label": "G7: Descent Bank"},
        {"pos": [5, 1, 2.0], "orient": [-0.2, 0.98, -0.2], "label": "G8: Pivot"},
        {"pos": [7, 4, 1.5], "orient": [-1, 0, 0], "label": "G9: Cross-over"},
        {"pos": [5, 6, 1.5], "orient": [0, -1, 0], "label": "G10: Reverse Hairpin"},
        {"pos": [2, 5, 2.0], "orient": [1, 0, 0.1], "label": "G11: Minor Climb"},
        {"pos": [1, 3, 2.5], "orient": [0, -1, 0], "label": "G12: High-speed Pivot"},
        {"pos": [3, 1, 2.0], "orient": [1, 0, -0.1], "label": "G13: Sharp Descent"},
        {"pos": [6, 2, 1.5], "orient": [0, 1, 0], "label": "G14: Final Hook"},
        {"pos": [8, 5, 1.5], "orient": [1, 0, 0], "label": "G15: Exit"},
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
    print(f"The Corkscrew: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for i, (pos, label) in enumerate(zip(gates, get_gate_labels())):
        print(f"  {label}: ({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})")
