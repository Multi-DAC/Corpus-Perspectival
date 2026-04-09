"""
Final Exam — 25-Gate Integration Test
Designed by Clayton (Feb 10, 2026)

The hardest course. Deliberately combines: velocity, vertical ascent,
spatial pivots, ballistic dives, micro-slalom, blind displacement,
centripetal orbits, dropdown transitions, irregular strafes, snap-backs.
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


def _circle_gates(center, radius, n, z, label_prefix, start_deg=0, end_deg=360):
    """Generate gates around a circle with tangential orientations."""
    gates = []
    for i in range(n):
        t = i / n  # Don't close the circle (would duplicate start)
        angle = np.radians(start_deg + t * (end_deg - start_deg))
        x = center[0] + radius * np.cos(angle)
        y = center[1] + radius * np.sin(angle)
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

# Gates 1-3: Pure Velocity (0,0,1) to (30,0,1)
_gates += _linspace_gates([0, 0, 1], [30, 0, 1], 3, [1, 0, 0], "G1-3: Pure Velocity")

# Gate 4: Vertical Ascent
_gates.append({"pos": [35, 2, 5], "orient": [0.1, 0.1, 0.98], "label": "G4: Vertical Ascent"})

# Gate 5: Spatial Pivot
_gates.append({"pos": [35, 8, 8], "orient": [0, 1, 0], "label": "G5: Spatial Pivot"})

# Gate 6: Ballistic Dive
_gates.append({"pos": [30, 12, 1], "orient": [-0.1, 0.1, -0.98], "label": "G6: Ballistic Dive"})

# Gates 7-10: Micro-Slalom (25,12,1.2) to (10,12,0.8)
_gates += _linspace_gates([25, 12, 1.2], [10, 12, 0.8], 4, [-1, 0, 0], "G7-10: Micro-Slalom")

# Gate 11: Climbing Lateral Hook
_gates.append({"pos": [5, 15, 2], "orient": [0, 1, 0.2], "label": "G11: Climbing Lateral Hook"})

# Gate 12: Blind Displacement
_gates.append({"pos": [8, 20, 4], "orient": [0.6, 0.8, 0.1], "label": "G12: Blind Displacement"})

# Gate 13: Stabilization
_gates.append({"pos": [15, 22, 5], "orient": [1, 0, 0], "label": "G13: Stabilization"})

# Gates 14-18: Centripetal Orbit (circle R=10m at Z=5, centered at (15, 22))
_gates += _circle_gates(
    center=[15, 22], radius=10, n=5, z=5,
    label_prefix="G14-18: Centripetal Orbit",
    start_deg=0, end_deg=300  # ~300° arc (almost full circle)
)

# Gate 19: Dropdown Transition
_gates.append({"pos": [15, 10, 3], "orient": [0, -1, -0.5], "label": "G19: Dropdown Transition"})

# Gates 20-23: Irregular Strafe (15,0,1.5) to (40,-10,1.5)
_gates += _linspace_gates([15, 0, 1.5], [40, -10, 1.5], 4, [0.9, -0.4, 0], "G20-23: Irregular Strafe")

# Gate 24: Snap-back Pivot
_gates.append({"pos": [45, -5, 2], "orient": [0, 1, 0], "label": "G24: Snap-back Pivot"})

# Gate 25: Termination
_gates.append({"pos": [40, 0, 1.5], "orient": [-1, 0, 0], "label": "G25: Termination"})


COURSE = {
    "name": "Final Exam",
    "description": "25-gate integration test — every challenge type combined",
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
    print(f"Final Exam: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
