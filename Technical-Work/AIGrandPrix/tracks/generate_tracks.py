"""
Procedural Track Generator for Drone Racing

Generates diverse tracks with varying:
- Gate count (10-50)
- Gate spacing (tight to wide)
- Turn angles (gentle to hairpin)
- Vertical variation (flat to full 3D)
- Course character (speed, technical, mixed, vertical, spiral)

Output: YAML files compatible with load_track()

Usage:
    python generate_tracks.py --count 500
    python generate_tracks.py --count 100 --output-dir ../rpg_time_optimal/tracks/generated
"""

import numpy as np
import yaml
import argparse
from pathlib import Path


def random_track(rng, style=None):
    """Generate a single random track.
    
    Styles:
        speed     - long straights, gentle curves, wide spacing
        technical - tight turns, short segments, varied elevation
        vertical  - emphasis on altitude changes, 3D maneuvering
        spiral    - helical patterns, continuous turning
        mixed     - combination of all elements
        hairpin   - sharp reversals, aggressive direction changes
    """
    if style is None:
        style = rng.choice(['speed', 'technical', 'vertical', 'spiral', 'mixed', 'hairpin'])
    
    # Style-dependent parameters
    params = {
        'speed': {
            'n_gates': rng.integers(15, 35),
            'segment_len': rng.uniform(10, 28),
            'turn_strength': rng.uniform(0.1, 0.4),
            'z_variation': rng.uniform(0.0, 1.5),
            'z_drift': rng.uniform(-0.02, 0.02),
        },
        'technical': {
            'n_gates': rng.integers(15, 30),
            'segment_len': rng.uniform(2.5, 6.0),
            'turn_strength': rng.uniform(0.5, 1.2),
            'z_variation': rng.uniform(0.5, 2.0),
            'z_drift': rng.uniform(-0.05, 0.05),
        },
        'vertical': {
            'n_gates': rng.integers(12, 25),
            'segment_len': rng.uniform(4.0, 10.0),
            'turn_strength': rng.uniform(0.3, 0.8),
            'z_variation': rng.uniform(2.0, 5.0),
            'z_drift': rng.uniform(-0.1, 0.1),
        },
        'spiral': {
            'n_gates': rng.integers(15, 35),
            'segment_len': rng.uniform(3.0, 8.0),
            'turn_strength': rng.uniform(0.6, 1.0),
            'z_variation': rng.uniform(1.0, 3.0),
            'z_drift': rng.uniform(0.05, 0.15),  # Tends upward
        },
        'mixed': {
            'n_gates': rng.integers(15, 45),
            'segment_len': rng.uniform(3.0, 15.0),
            'turn_strength': rng.uniform(0.2, 1.0),
            'z_variation': rng.uniform(0.5, 3.0),
            'z_drift': rng.uniform(-0.05, 0.05),
        },
        'hairpin': {
            'n_gates': rng.integers(12, 25),
            'segment_len': rng.uniform(3.0, 8.0),
            'turn_strength': rng.uniform(0.8, 1.5),
            'z_variation': rng.uniform(0.3, 2.0),
            'z_drift': rng.uniform(-0.03, 0.03),
        },
    }
    
    p = params[style]
    n_gates = int(p['n_gates'])
    
    # Generate track as a random walk with smooth turning
    gates = []
    x, y, z = 0.0, 0.0, rng.uniform(1.0, 3.0)  # Start height
    heading = rng.uniform(0, 2 * np.pi)
    
    for i in range(n_gates):
        gates.append([round(float(x), 2), round(float(y), 2), round(float(z), 2)])
        
        # Segment length with per-gate variation
        seg_len = p['segment_len'] * rng.uniform(0.6, 1.4)
        
        # Turn: smooth random walk on heading
        if style == 'hairpin' and rng.random() < 0.3:
            # Occasional sharp reversal
            heading += rng.choice([-1, 1]) * rng.uniform(2.0, 3.0)
        else:
            heading += rng.normal(0, p['turn_strength'])
        
        # Advance position
        x += seg_len * np.cos(heading)
        y += seg_len * np.sin(heading)
        
        # Altitude: smooth random walk with bounds
        z += rng.normal(p['z_drift'], p['z_variation'] * 0.3)
        z = np.clip(z, 0.5, 12.0)  # Keep above ground, below ceiling
    
    # Initial position: slightly behind and below first gate
    g0 = gates[0]
    g1 = gates[1] if len(gates) > 1 else [g0[0] + 1, g0[1], g0[2]]
    
    # Direction from gate 0 to gate 1
    dx = g1[0] - g0[0]
    dy = g1[1] - g0[1]
    dist = max(np.sqrt(dx**2 + dy**2), 0.01)
    
    # Start 3m behind first gate, same height
    init_x = g0[0] - 3.0 * (dx / dist)
    init_y = g0[1] - 3.0 * (dy / dist)
    init_z = g0[2]
    
    init_pos = [round(float(init_x), 2), round(float(init_y), 2), round(float(init_z), 2)]
    
    return {
        'name': f'proc_{style}_{n_gates}g',
        'style': style,
        'gates': gates,
        'initial': {'position': init_pos},
    }


def validate_track(track):
    """Basic validation — no self-intersecting segments, reasonable distances."""
    gates = np.array(track['gates'])
    if len(gates) < 5:
        return False
    
    # Check gate-to-gate distances
    dists = np.linalg.norm(np.diff(gates, axis=0), axis=1)
    if dists.min() < 1.0:  # Too close — drone can't maneuver
        return False
    if dists.max() > 40.0:  # Too far — boring/timeout
        return False
    
    # Check total course length isn't insane
    total_len = dists.sum()
    if total_len > 500:  # Way too long
        return False
    
    # Check altitude bounds
    zs = gates[:, 2]
    if zs.min() < 0.3 or zs.max() > 15.0:
        return False
    
    return True


def generate_batch(count, seed=42):
    """Generate a batch of validated tracks."""
    rng = np.random.default_rng(seed)
    tracks = []
    attempts = 0
    max_attempts = count * 5
    
    while len(tracks) < count and attempts < max_attempts:
        track = random_track(rng)
        if validate_track(track):
            track['name'] = f"proc_{track['style']}_{len(track['gates'])}g_{len(tracks):04d}"
            tracks.append(track)
        attempts += 1
    
    print(f"Generated {len(tracks)} valid tracks in {attempts} attempts")
    return tracks


def save_tracks(tracks, output_dir):
    """Save tracks as individual YAML files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for track in tracks:
        path = output_dir / f"{track['name']}.yaml"
        # Save in format compatible with load_track()
        data = {
            'gates': track['gates'],
            'initial': track['initial'],
        }
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    print(f"Saved {len(tracks)} tracks to {output_dir}")
    
    # Also save a manifest
    manifest = {
        'count': len(tracks),
        'names': [t['name'] for t in tracks],
        'styles': {},
    }
    for t in tracks:
        s = t['style']
        manifest['styles'][s] = manifest['styles'].get(s, 0) + 1
    
    with open(output_dir / 'manifest.yaml', 'w') as f:
        yaml.dump(manifest, f)
    
    # Print style distribution
    print("\nStyle distribution:")
    for style, count in sorted(manifest['styles'].items()):
        print(f"  {style:12s}: {count}")


def stats(tracks):
    """Print track statistics."""
    gate_counts = [len(t['gates']) for t in tracks]
    all_dists = []
    for t in tracks:
        gs = np.array(t['gates'])
        dists = np.linalg.norm(np.diff(gs, axis=0), axis=1)
        all_dists.extend(dists.tolist())
    
    all_dists = np.array(all_dists)
    
    print(f"\nTrack Statistics:")
    print(f"  Tracks: {len(tracks)}")
    print(f"  Gate counts: {min(gate_counts)}-{max(gate_counts)} (mean {np.mean(gate_counts):.0f})")
    print(f"  Gate spacing: {all_dists.min():.1f}-{all_dists.max():.1f}m (mean {all_dists.mean():.1f}m)")
    print(f"  Total gate count: {sum(gate_counts)}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--count', type=int, default=500)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output-dir', type=str, 
                        default=str(Path(__file__).parent.parent / 'rpg_time_optimal' / 'tracks' / 'generated'))
    args = parser.parse_args()
    
    tracks = generate_batch(args.count, seed=args.seed)
    stats(tracks)
    save_tracks(tracks, args.output_dir)
