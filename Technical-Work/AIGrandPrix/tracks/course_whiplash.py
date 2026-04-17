"""
Whiplash — 20-Gate Speed Management Course
Designed by Clayton (Feb 10, 2026)

Emphasis: Long straights into sudden turns
Tests speed management — don't approach a 90° turn at max velocity.
"""

import numpy as np

# Expand ranges like "1-4: (0,0,1) to (40,0,1)" into individual gates
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


# Build the full course
_gates = []

# Gates 1-4: Super-Straight (0,0,1) to (40,0,1)
_gates += _linspace_gates([0, 0, 1], [40, 0, 1], 4, [1, 0, 0], "G1-4: Super-Straight")

# Gate 5: Emergency Deceleration
_gates.append({"pos": [45, 2, 1.5], "orient": [0, 1, 0], "label": "G5: Emergency Deceleration"})

# Gate 6: 180° Return Leg
_gates.append({"pos": [43, 6, 1.5], "orient": [-1, 0, 0], "label": "G6: 180° Return Leg"})

# Gate 7: High Speed Acceleration
_gates.append({"pos": [30, 6, 1.5], "orient": [-1, 0, 0], "label": "G7: High Speed Acceleration"})

# Gate 8: Sustain Velocity
_gates.append({"pos": [15, 6, 1.5], "orient": [-1, 0, 0], "label": "G8: Sustain Velocity"})

# Gate 9: Hard 90° Left
_gates.append({"pos": [10, 8, 2.0], "orient": [0, 1, 0], "label": "G9: Hard 90° Left"})

# Gate 10: Hard 90° Right
_gates.append({"pos": [12, 15, 2.0], "orient": [1, 0, 0], "label": "G10: Hard 90° Right"})

# Gates 11-14: Secondary Burner Section (20,15,1.5) to (60,15,1.5)
_gates += _linspace_gates([20, 15, 1.5], [60, 15, 1.5], 4, [1, 0, 0], "G11-14: Burner")

# Gate 15: Sudden Drop/Yaw Pivot
_gates.append({"pos": [65, 13, 2.0], "orient": [0, -1, 0], "label": "G15: Sudden Drop/Yaw Pivot"})

# Gate 16: Ground-effect Strafe
_gates.append({"pos": [63, 8, 1.0], "orient": [-1, 0, 0], "label": "G16: Ground-effect Strafe"})

# Gate 17: Constant Throttle
_gates.append({"pos": [40, 8, 1.0], "orient": [-1, 0, 0], "label": "G17: Constant Throttle"})

# Gate 18: Constant Throttle
_gates.append({"pos": [20, 8, 1.0], "orient": [-1, 0, 0], "label": "G18: Constant Throttle"})

# Gate 19: Chicane Hook
_gates.append({"pos": [5, 5, 1.5], "orient": [0.7, -0.7, 0], "label": "G19: Chicane Hook"})

# Gate 20: Termination
_gates.append({"pos": [0, 0, 1.5], "orient": [1, 0, 0], "label": "G20: Termination"})


COURSE = {
    "name": "Whiplash",
    "description": "20-gate speed management course — long straights into sudden turns",
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
    print(f"Whiplash: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
