"""
The Gauntlet Jr. — 20-Gate General Course
Designed by Clayton (Feb 10, 2026)

A sampler platter — velocity starts, lateral slalom, high altitude,
vertical recovery, moderate-G hairpin, diagonal finish.
"""

import numpy as np


def _linspace_gates(start, end, n, orient, label_prefix):
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


def _arc_gates(center, radius, start_angle, end_angle, n, z, label_prefix):
    """Generate gates along a circular arc with tangential orientations."""
    gates = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        angle = np.radians(start_angle + t * (end_angle - start_angle))
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
        # Tangential direction
        dx = -np.sin(angle)
        dy = np.cos(angle)
        norm = np.sqrt(dx**2 + dy**2)
        gates.append({
            "pos": [round(x, 2), round(y, 2), z],
            "orient": [round(dx/norm, 3), round(dy/norm, 3), 0],
            "label": f"{label_prefix} {i+1}"
        })
    return gates


_gates = []

# Gates 1-3: Velocity Start (0,0,1.5) to (15,0,1.5)
_gates += _linspace_gates([0, 0, 1.5], [15, 0, 1.5], 3, [1, 0, 0], "G1-3: Velocity Start")

# Gates 4-6: Lateral Slalom (20,5,1.5) to (20,15,1.5)
_gates += _linspace_gates([20, 5, 1.5], [20, 15, 1.5], 3, [0, 1, 0], "G4-6: Lateral Slalom")

# Gates 7-9: High Altitude Straight (15,20,5) to (5,20,5)
_gates += _linspace_gates([15, 20, 5], [5, 20, 5], 3, [-1, 0, 0], "G7-9: High Altitude Straight")

# Gate 10: Vertical Recovery (Dive)
_gates.append({"pos": [0, 20, 2], "orient": [-0.5, 0, -0.8], "label": "G10: Vertical Recovery (Dive)"})

# Gates 11-15: Moderate-G Hairpin (arc back to (10,10,1.5))
# Arc from (0,20) curving to (10,10) — approximate as arc centered at (10,20) R=10
_gates += _arc_gates(
    center=[5, 15], radius=7, 
    start_angle=90, end_angle=-45, 
    n=5, z=1.5, 
    label_prefix="G11-15: Moderate-G Hairpin"
)

# Gates 16-20: 45° Diagonal Finish (10,10,1.5) to (0,0,1.5)
_gates += _linspace_gates([10, 10, 1.5], [0, 0, 1.5], 5, [-0.7, -0.7, 0], "G16-20: Diagonal Finish")


COURSE = {
    "name": "The Gauntlet Jr.",
    "description": "20-gate general course — a bit of everything",
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
    print(f"The Gauntlet Jr.: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
