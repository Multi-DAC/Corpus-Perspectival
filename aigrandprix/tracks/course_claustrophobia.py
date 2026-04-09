"""
Claustrophobia — 20-Gate Tight Spacing Course
Designed by Clayton (Feb 10, 2026)

Emphasis: Tight gate spacing, minimal recovery distance
Tests precision at lower speed. Gates packed close.
"""

import numpy as np

def _linspace_gates(start, end, n, orient, label_prefix):
    """Generate n evenly spaced gates between start and end."""
    gates = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        pos = [
            start[0] + t * (end[0] - start[0]),
            start[1] + t * (end[1] - start[1]),
            start[2] + t * (end[2] - start[2]),
        ]
        gates.append({
            "pos": pos,
            "orient": orient,
            "label": f"{label_prefix} {i+1}"
        })
    return gates


_gates = [
    {"pos": [0, 0, 1.5], "orient": [1, 0, 0], "label": "G1: Entry"},
    {"pos": [3, 0.5, 1.4], "orient": [0.98, 0.1, -0.03], "label": "G2: Narrowing Corridor"},
    {"pos": [6, 0, 1.5], "orient": [1, -0.1, 0], "label": "G3: Slalom Initiation"},
    {"pos": [9, -1, 1.6], "orient": [0.9, -0.4, 0], "label": "G4: Precision Offset"},
    {"pos": [11, 1, 1.4], "orient": [0.8, 0.6, 0], "label": "G5: Precision Offset"},
    {"pos": [13, -0.5, 1.5], "orient": [1, 0, 0], "label": "G6: Leveling Pulse"},
    {"pos": [15, 0, 1.2], "orient": [1, 0, -0.1], "label": "G7: Decreasing Z-Clearance"},
    {"pos": [17, 0, 0.9], "orient": [1, 0, -0.1], "label": "G8: Minimum Altitude"},
    {"pos": [20, 2, 1.2], "orient": [0.6, 0.8, 0.1], "label": "G9: Blind Hook Transition"},
    {"pos": [19, 5, 1.5], "orient": [-0.5, 0.8, 0.1], "label": "G10: Tight Orbit"},
    {"pos": [16, 6, 1.5], "orient": [-1, 0, 0], "label": "G11: Return Leg"},
]

# Gates 12-15: 3.0m separation interval (13,6,1.5) to (4,6,1.5)
_gates += _linspace_gates([13, 6, 1.5], [4, 6, 1.5], 4, [-1, 0, 0], "G12-15: 3m Interval")

_gates += [
    {"pos": [2, 8, 1.8], "orient": [0, 1, 0], "label": "G16: Upward Pitch-Hook"},
    {"pos": [4, 10, 1.5], "orient": [1, 0, -0.1], "label": "G17: High-Precision S-Turn"},
    {"pos": [7, 9, 1.3], "orient": [0.8, -0.6, -0.1], "label": "G18: High-Precision S-Turn"},
    {"pos": [10, 10, 1.5], "orient": [1, 0, 0], "label": "G19: Stabilization"},
    {"pos": [13, 10, 1.5], "orient": [1, 0, 0], "label": "G20: Finish"},
]


COURSE = {
    "name": "Claustrophobia",
    "description": "20-gate tight spacing course — precision at low speed",
    "gate_radius": 1.5,
    "gates": _gates,
}


def get_gates():
    return np.array([g["pos"] for g in COURSE["gates"]], dtype=np.float32)

def get_orientations():
    return np.array([g["orient"] for g in COURSE["gates"]], dtype=np.float32)

def get_gate_labels():
    return [g["label"] for g in COURSE["gates"]]


if __name__ == "__main__":
    gates = get_gates()
    print(f"Claustrophobia: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
