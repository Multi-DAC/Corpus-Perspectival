"""
Convert Python track definitions to YAML format for the training pipeline.
"""

import sys
import yaml
import importlib.util
import numpy as np
from pathlib import Path


def load_python_track(py_path):
    """Load a Python track module and extract its COURSE dict."""
    spec = importlib.util.spec_from_file_location("track_mod", py_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    if hasattr(mod, 'COURSE'):
        return mod.COURSE
    elif hasattr(mod, 'get_course'):
        return mod.get_course()
    else:
        raise ValueError(f"No COURSE dict or get_course() in {py_path}")


def to_float(x):
    """Force conversion to Python float (not numpy scalar)."""
    return round(float(x), 6)


def course_to_yaml(course):
    """Convert a Python COURSE dict to YAML-compatible format.
    
    Gates are stored as simple [x, y, z] arrays matching gauntlet.yaml format.
    The env only uses position, not orientation.
    """
    # Gates as simple [x, y, z] lists (matching gauntlet.yaml format)
    gates = []
    for g in course['gates']:
        pos = [to_float(x) for x in g['pos']]
        gates.append(pos)
    
    # Initial position: before first gate, offset back along its orientation
    first_gate = course['gates'][0]
    pos0 = [float(x) for x in first_gate['pos']]
    orient0 = [float(x) for x in first_gate['orient']]
    norm0 = np.sqrt(sum(x**2 for x in orient0))
    if norm0 > 0:
        orient0 = [x / norm0 for x in orient0]
    
    # Start 3m behind first gate
    init_pos = [
        to_float(pos0[0] - 3.0 * orient0[0]),
        to_float(pos0[1] - 3.0 * orient0[1]),
        to_float(pos0[2]),
    ]
    
    return {
        'gates': gates,
        'initial': {
            'position': init_pos,
        }
    }


def main():
    tracks_dir = Path(__file__).parent.parent / 'tracks'
    output_dir = Path(__file__).parent.parent / 'rpg_time_optimal' / 'tracks'
    
    py_files = sorted(tracks_dir.glob('course_*.py'))
    
    for py_file in py_files:
        print(f"Converting {py_file.name}...")
        try:
            course = load_python_track(py_file)
            yaml_data = course_to_yaml(course)
            
            # Output filename: course_gauntlet_jr.py -> gauntlet_jr.yaml
            stem = py_file.stem.replace('course_', '')
            out_path = output_dir / f'{stem}.yaml'
            
            with open(out_path, 'w') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
            
            n_gates = len(yaml_data['gates'])
            print(f"  -> {out_path.name}: {n_gates} gates")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Also handle clayton_master_course.py
    master = tracks_dir / 'clayton_master_course.py'
    if master.exists():
        print(f"Converting {master.name}...")
        try:
            course = load_python_track(master)
            yaml_data = course_to_yaml(course)
            out_path = output_dir / 'master_course.yaml'
            with open(out_path, 'w') as f:
                yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
            print(f"  -> {out_path.name}: {len(yaml_data['gates'])} gates")
        except Exception as e:
            print(f"  ERROR: {e}")


if __name__ == '__main__':
    main()
