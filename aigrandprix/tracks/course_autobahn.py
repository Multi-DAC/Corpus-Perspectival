"""
The Autobahn — 25-Gate Speed Course
Designed by Clayton (Feb 10, 2026)

Emphasis: Long sweeping curves, wide gate spacing, full throttle
Teaches the agent that sometimes maximum speed IS the answer.

Gates 1-10: Spiral arc, R=50m (generated mathematically)
Gates 11-25: Explicit coordinates from Clayton
"""

import numpy as np


def _generate_spiral_arc(n_gates, radius, start_angle=0, arc_degrees=180, z_start=2, z_end=3):
    """Generate gates along a spiral arc with tangential orientations."""
    gates = []
    for i in range(n_gates):
        t = i / (n_gates - 1)
        angle = np.radians(start_angle + t * arc_degrees)
        # Spiral center at (0, radius, z_start) — arc sweeps forward and to the right
        x = radius * np.sin(angle)
        y = radius * (1 - np.cos(angle))
        z = z_start + t * (z_end - z_start)
        
        # Tangential orientation (derivative of position)
        dx = np.cos(angle)
        dy = np.sin(angle)
        dz = (z_end - z_start) / (n_gates - 1) if n_gates > 1 else 0
        norm = np.sqrt(dx**2 + dy**2 + dz**2)
        orient = [dx / norm, dy / norm, dz / norm]
        
        gates.append({
            "pos": [round(x, 2), round(y, 2), round(z, 2)],
            "orient": [round(o, 3) for o in orient],
            "label": f"G{i+1}: Great Sweeper {i+1}"
        })
    return gates


# Build full course
_gates = []

# Gates 1-10: The Great Sweeper (spiral arc, R=50m)
_gates += _generate_spiral_arc(10, radius=50, start_angle=0, arc_degrees=120, z_start=2, z_end=3)

# Gates 11-15: Terminal Velocity Section (50,50,3) to (150,50,3)
for i in range(5):
    t = i / 4
    x = 50 + t * 100
    _gates.append({
        "pos": [x, 50, 3],
        "orient": [1, 0, 0],
        "label": f"G{11+i}: Terminal Velocity {i+1}"
    })

# Gate 16: Kinetic Retention Curve
_gates.append({"pos": [165, 60, 4], "orient": [0.8, 0.6, 0], "label": "G16: Kinetic Retention Curve"})

# Gate 17: Climbing Apex
_gates.append({"pos": [175, 85, 5], "orient": [0.4, 0.9, 0], "label": "G17: Climbing Apex"})

# Gate 18: Gravity-assisted Descent
_gates.append({"pos": [170, 110, 4], "orient": [-0.2, 0.98, 0], "label": "G18: Gravity-assisted Descent"})

# Gates 19-25: Main Straightaway (150,130,2) to (0,130,2)
for i in range(7):
    t = i / 6
    x = 150 - t * 150
    _gates.append({
        "pos": [x, 130, 2],
        "orient": [-1, 0, 0],
        "label": f"G{19+i}: Main Straightaway {i+1}"
    })


COURSE = {
    "name": "The Autobahn",
    "description": "25-gate speed course — sweeping curves, full throttle sections",
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
    print(f"The Autobahn: {len(gates)} gates")
    print(f"Bounds: X[{gates[:,0].min():.1f}-{gates[:,0].max():.1f}] "
          f"Y[{gates[:,1].min():.1f}-{gates[:,1].max():.1f}] "
          f"Z[{gates[:,2].min():.1f}-{gates[:,2].max():.1f}]")
    for g in COURSE["gates"]:
        print(f"  {g['label']}: ({g['pos'][0]:.1f}, {g['pos'][1]:.1f}, {g['pos'][2]:.1f})")
