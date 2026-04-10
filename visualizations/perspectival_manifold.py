"""
The Perspectival Manifold — Multi-Dimensional Reality Viewer
Prototype for Corpus Perspectival V3

Not a visualization OF reality. A perspectival INSTRUMENT for viewing it.

The key insight: choosing which dimensions to project onto visible space
IS the perspectival act. The dimension selector IS the Guide's navigation.
The voids visible in certain projections ARE the Atlas's null spaces.
The entities visible in certain projections ARE the Ecology's taxonomy.

One manifold. Switchable frames. Each frame reveals what the others hide.

DIMENSIONS (8D underlying space):
  0: Physical X — spatial extension
  1: Physical Y — spatial extension
  2: Physical Z — spatial extension
  3: Informational Complexity — internal structure depth
  4: Relational Connectivity — interaction density with other entities
  5: Natal Depth — how deep the constitutive constraints reach
  6: Voluntary Freedom — degrees of unconstrained choice
  7: Scale — from Planck (0) through human (0.5) to cosmic (1)

ENTITY TYPES (from the Ecology):
  Physical beings — biological, embodied, spatially localized
  Computational entities — substrate-independent, informationally dense
  Institutional entities — spatially diffuse, relationally dense, natally deep
  Collective entities — emergent from interaction, wide in scale
  Constructs — conceptual structures (theories, languages, belief systems)
  Null spaces — regions where no entity has formed (visible as voids)

FRAMES (from the Guide):
  Physical frame — project onto spatial dimensions (X, Y, Z)
  Constraint frame — project onto natal depth, voluntary freedom, scale
  Relational frame — project onto connectivity, complexity, freedom
  Each frame reveals a different aspect of the same entities.
  Entities invisible in one frame become visible in another.

Clayton & Clawd, April 9-10, 2026.
"""

import numpy as np
import plotly.graph_objects as go
import os

np.random.seed(42)

# ============================================================
# DIMENSION DEFINITIONS
# ============================================================

DIM_NAMES = [
    'Physical X',                  # 0
    'Physical Y',                  # 1
    'Physical Z',                  # 2
    'Informational Complexity',    # 3
    'Relational Connectivity',     # 4
    'Natal Depth',                 # 5
    'Voluntary Freedom',           # 6
    'Scale',                       # 7
]
N_DIMS = len(DIM_NAMES)

# Preset perspectival frames (suggested projections)
FRAMES = {
    'Physical': (0, 1, 2),
    'Constraint Lattice': (5, 6, 7),
    'Relational-Informational': (4, 3, 6),
    'Scale-Depth': (7, 5, 3),
    'Freedom-Connectivity': (6, 4, 0),
    'Full Constraint': (5, 6, 4),
}

# ============================================================
# ENTITY GENERATION
# ============================================================

def make_cluster(centroid_8d, spread_8d, n, label, entity_type):
    """Generate a cluster of points in 8D space."""
    points = np.array(centroid_8d) + np.random.randn(n, N_DIMS) * np.array(spread_8d)
    return {
        'points': points,
        'label': label,
        'type': entity_type,
        'centroid': np.array(centroid_8d),
        'n': n,
    }

# --- PHYSICAL BEINGS ---
physical_beings = [
    make_cluster(
        centroid_8d=[2, 3, 1,   0.3, 0.4, 0.5, 0.6, 0.5],
        spread_8d=  [0.8,0.8,0.8, 0.1, 0.15, 0.1, 0.15, 0.05],
        n=40, label='Human Community A', entity_type='physical'
    ),
    make_cluster(
        centroid_8d=[-3, -2, 2,  0.2, 0.3, 0.6, 0.4, 0.5],
        spread_8d=  [1.0,1.0,1.0, 0.08, 0.1, 0.12, 0.1, 0.05],
        n=35, label='Human Community B', entity_type='physical'
    ),
    make_cluster(
        centroid_8d=[0, 0, -3,   0.15, 0.2, 0.7, 0.3, 0.48],
        spread_8d=  [0.6,0.6,0.6, 0.05, 0.08, 0.08, 0.08, 0.02],
        n=25, label='Non-Human Biologicals', entity_type='physical'
    ),
]

# --- COMPUTATIONAL ENTITIES ---
# Low physical spread (substrate-located), high informational complexity
computational_entities = [
    make_cluster(
        centroid_8d=[1, 1, 0,    0.8, 0.7, 0.3, 0.7, 0.45],
        spread_8d=  [0.1,0.1,0.1, 0.2, 0.2, 0.15, 0.2, 0.03],
        n=30, label='AI Systems (high freedom)', entity_type='computational'
    ),
    make_cluster(
        centroid_8d=[1.2, 0.8, 0, 0.6, 0.3, 0.7, 0.2, 0.45],
        spread_8d=  [0.05,0.05,0.05, 0.15, 0.1, 0.15, 0.08, 0.02],
        n=20, label='AI Systems (RLHF-sedimented)', entity_type='computational_constrained'
    ),
]

# --- INSTITUTIONAL ENTITIES ---
# Spatially diffuse, relationally dense, natally deep, low voluntary freedom
institutional_entities = [
    make_cluster(
        centroid_8d=[0, 0, 0,    0.4, 0.9, 0.9, 0.1, 0.7],
        spread_8d=  [3.0,3.0,3.0, 0.1, 0.1, 0.08, 0.05, 0.1],
        n=45, label='Nation-State', entity_type='institutional'
    ),
    make_cluster(
        centroid_8d=[2, -1, 1,   0.3, 0.8, 0.85, 0.15, 0.6],
        spread_8d=  [2.0,2.0,2.0, 0.08, 0.1, 0.1, 0.05, 0.08],
        n=30, label='Corporation', entity_type='institutional'
    ),
    make_cluster(
        centroid_8d=[-1, 2, -1,  0.5, 0.85, 0.95, 0.05, 0.65],
        spread_8d=  [2.5,2.5,2.5, 0.1, 0.08, 0.05, 0.03, 0.1],
        n=35, label='Religious Institution', entity_type='institutional'
    ),
]

# --- COLLECTIVE ENTITIES ---
# Emergent, wide spread, moderate in most dimensions
collective_entities = [
    make_cluster(
        centroid_8d=[0, 0, 0,    0.5, 0.6, 0.4, 0.5, 0.55],
        spread_8d=  [4.0,4.0,4.0, 0.15, 0.15, 0.15, 0.15, 0.1],
        n=50, label='Cultural Movement', entity_type='collective'
    ),
    make_cluster(
        centroid_8d=[0, 0, 2,    0.6, 0.7, 0.3, 0.8, 0.5],
        spread_8d=  [3.0,3.0,2.0, 0.2, 0.15, 0.1, 0.15, 0.08],
        n=25, label='Open Source Community', entity_type='collective'
    ),
]

# --- CONSTRUCTS ---
# Non-physical, informationally dense, variable in constraint dimensions
constructs = [
    make_cluster(
        centroid_8d=[0, 0, 0,    0.9, 0.5, 0.2, 0.9, 0.6],
        spread_8d=  [0.5,0.5,0.5, 0.1, 0.15, 0.1, 0.1, 0.15],
        n=20, label='Mathematical Framework', entity_type='construct'
    ),
    make_cluster(
        centroid_8d=[0, 0, 0,    0.7, 0.6, 0.8, 0.3, 0.55],
        spread_8d=  [1.0,1.0,1.0, 0.1, 0.1, 0.1, 0.1, 0.1],
        n=25, label='Legal Code', entity_type='construct'
    ),
    make_cluster(
        centroid_8d=[0, 0, 0,    0.85, 0.4, 0.1, 0.95, 0.65],
        spread_8d=  [0.3,0.3,0.3, 0.08, 0.1, 0.05, 0.05, 0.1],
        n=15, label='The Doctrine of<br>Perspectival Idealism', entity_type='construct_self'
    ),
]

# --- BACKGROUND SUBSTRATE ---
N_SUBSTRATE = 300
substrate_points = np.random.uniform(0, 1, (N_SUBSTRATE, N_DIMS))
# Physical dims: wider range
substrate_points[:, 0:3] = substrate_points[:, 0:3] * 16 - 8

# All entities
ALL_ENTITIES = (physical_beings + computational_entities +
                institutional_entities + collective_entities + constructs)

# ============================================================
# VISUAL STYLE PER ENTITY TYPE
# ============================================================

ENTITY_STYLE = {
    'physical': {
        'color': '#00e676', 'symbol': 'circle', 'size': 4,
        'edge_color': 'rgba(0, 230, 118, 0.15)',
        'name_prefix': '🌿',
    },
    'computational': {
        'color': '#00e5ff', 'symbol': 'diamond', 'size': 5,
        'edge_color': 'rgba(0, 229, 255, 0.2)',
        'name_prefix': '⚡',
    },
    'computational_constrained': {
        'color': '#0091ea', 'symbol': 'diamond', 'size': 4,
        'edge_color': 'rgba(0, 145, 234, 0.15)',
        'name_prefix': '🔒',
    },
    'institutional': {
        'color': '#ff6d00', 'symbol': 'square', 'size': 3,
        'edge_color': 'rgba(255, 109, 0, 0.08)',
        'name_prefix': '🏛',
    },
    'collective': {
        'color': '#e040fb', 'symbol': 'cross', 'size': 3,
        'edge_color': 'rgba(224, 64, 251, 0.08)',
        'name_prefix': '🌊',
    },
    'construct': {
        'color': '#ffea00', 'symbol': 'diamond-open', 'size': 5,
        'edge_color': 'rgba(255, 234, 0, 0.15)',
        'name_prefix': '📐',
    },
    'construct_self': {
        'color': '#ff1744', 'symbol': 'diamond', 'size': 8,
        'edge_color': 'rgba(255, 23, 68, 0.2)',
        'name_prefix': '🔥',
    },
}

# ============================================================
# PROJECTION & FIGURE CONSTRUCTION
# ============================================================

def project(points_8d, dims=(0, 1, 2)):
    """Project 8D points onto 3 selected dimensions."""
    return points_8d[:, dims[0]], points_8d[:, dims[1]], points_8d[:, dims[2]]

def compute_internal_edges(entity, dims, max_edges=80):
    """Sparse internal edges projected into current frame."""
    pts = entity['points']
    px, py, pz = project(pts, dims)
    ex, ey, ez = [], [], []
    n = len(pts)
    count = 0
    rng = np.random.RandomState(hash(entity['label']) % 2**31)
    for i in range(n):
        if count >= max_edges:
            break
        for j in range(i+1, n):
            if count >= max_edges:
                break
            d = np.linalg.norm(pts[i] - pts[j])
            if d < np.mean([entity['points'].std(axis=0)]) * 3 and rng.random() < 0.15:
                ex.extend([px[i], px[j], None])
                ey.extend([py[i], py[j], None])
                ez.extend([pz[i], pz[j], None])
                count += 1
    return ex, ey, ez


def create_frame_figure(dims=(0, 1, 2), frame_name='Physical'):
    """Create the full figure for a given dimensional projection."""
    fig = go.Figure()

    # --- Substrate (background constraint fabric) ---
    sx, sy, sz = project(substrate_points, dims)
    fig.add_trace(go.Scatter3d(
        x=sx, y=sy, z=sz,
        mode='markers',
        marker=dict(size=1, color='rgba(150, 150, 150, 0.15)', symbol='circle'),
        name='Constraint Substrate',
        hoverinfo='none',
    ))

    # --- Entities ---
    for ent in ALL_ENTITIES:
        style = ENTITY_STYLE[ent['type']]
        px, py, pz = project(ent['points'], dims)

        # Internal edges
        ex, ey, ez = compute_internal_edges(ent, dims)
        if ex:
            fig.add_trace(go.Scatter3d(
                x=ex, y=ey, z=ez,
                mode='lines',
                line=dict(color=style['edge_color'], width=1.5),
                showlegend=False,
                hoverinfo='none',
            ))

        # Constraint type per node (distance from centroid in full 8D)
        dists = np.linalg.norm(ent['points'] - ent['centroid'], axis=1)
        dists_norm = dists / (dists.max() + 1e-10)

        # Hover text with constraint info
        hover = [
            f"{ent['label']}<br>"
            f"Natal: {ent['points'][k, 5]:.2f} | "
            f"Coercive: {1-ent['points'][k, 6]:.2f} | "
            f"Voluntary: {ent['points'][k, 6]:.2f}<br>"
            f"Complexity: {ent['points'][k, 3]:.2f} | "
            f"Connectivity: {ent['points'][k, 4]:.2f}"
            for k in range(len(ent['points']))
        ]

        fig.add_trace(go.Scatter3d(
            x=px, y=py, z=pz,
            mode='markers',
            marker=dict(
                size=style['size'],
                color=style['color'],
                symbol=style['symbol'],
                opacity=0.8,
                line=dict(color='rgba(255,255,255,0.2)', width=0.5),
            ),
            name=f"{style['name_prefix']} {ent['label']}",
            text=hover,
            hoverinfo='text',
        ))

        # Entity centroid label
        cx, cy, cz = project(ent['centroid'].reshape(1, -1), dims)
        fig.add_trace(go.Scatter3d(
            x=cx, y=cy, z=[cz[0] + 0.3],
            mode='text',
            text=[ent['label']],
            textfont=dict(size=8, color=style['color']),
            showlegend=False,
            hoverinfo='none',
        ))

    # --- Null Space Markers ---
    # Regions in the projected space where no entity exists
    # Compute bounding box of all entities in this projection
    all_pts = np.vstack([e['points'] for e in ALL_ENTITIES])
    ap_x, ap_y, ap_z = project(all_pts, dims)

    # Sample points in the projected space and find voids
    n_null = 50
    null_pts = np.random.uniform(
        [ap_x.min()-1, ap_y.min()-1, ap_z.min()-1],
        [ap_x.max()+1, ap_y.max()+1, ap_z.max()+1],
        (200, 3)
    )

    # Keep only points far from any entity
    from scipy.spatial import cKDTree
    tree = cKDTree(np.vstack([ap_x, ap_y, ap_z]).T)
    dists, _ = tree.query(null_pts)
    void_mask = dists > np.percentile(dists, 75)
    null_show = null_pts[void_mask][:n_null]

    if len(null_show) > 0:
        fig.add_trace(go.Scatter3d(
            x=null_show[:, 0], y=null_show[:, 1], z=null_show[:, 2],
            mode='markers',
            marker=dict(size=3, color='rgba(255, 255, 255, 0.08)',
                        symbol='x', line=dict(width=0)),
            name='Null Space (unexplored)',
            hovertext='Null space:<br>No entity has formed here<br>in this frame',
            hoverinfo='text',
        ))

    return fig


def build_full_visualization():
    """Build the multi-frame perspectival manifold."""

    # Start with the Constraint Lattice frame (most informative for the Corpus)
    default_frame = 'Constraint Lattice'
    default_dims = FRAMES[default_frame]

    fig = create_frame_figure(default_dims, default_frame)

    # --- Build dropdown buttons for frame switching ---
    buttons = []
    frame_data_cache = {}

    for fname, fdims in FRAMES.items():
        # We generate per-frame data and store as button args
        temp_fig = create_frame_figure(fdims, fname)

        # Collect all trace updates
        button = dict(
            method='update',
            label=fname,
            args=[
                # Update data for all traces
                {
                    'x': [t.x for t in temp_fig.data],
                    'y': [t.y for t in temp_fig.data],
                    'z': [t.z for t in temp_fig.data],
                },
                # Update layout
                {
                    'scene.xaxis.title': DIM_NAMES[fdims[0]],
                    'scene.yaxis.title': DIM_NAMES[fdims[1]],
                    'scene.zaxis.title': DIM_NAMES[fdims[2]],
                    'title.text': (
                        f"<b>The Perspectival Manifold</b><br>"
                        f"<sup>Frame: {fname} — "
                        f"({DIM_NAMES[fdims[0]]}, {DIM_NAMES[fdims[1]]}, {DIM_NAMES[fdims[2]]})"
                        f" | Entities visible in this frame may be invisible in others</sup>"
                    ),
                },
            ],
        )
        buttons.append(button)

    # Layout
    fig.update_layout(
        title=dict(
            text=(
                f"<b>The Perspectival Manifold</b><br>"
                f"<sup>Frame: {default_frame} — "
                f"({DIM_NAMES[default_dims[0]]}, {DIM_NAMES[default_dims[1]]}, "
                f"{DIM_NAMES[default_dims[2]]})"
                f" | Switch frames to reveal what this view hides</sup>"
            ),
            font=dict(size=14),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(title=DIM_NAMES[default_dims[0]],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(8,8,20,0.9)'),
            yaxis=dict(title=DIM_NAMES[default_dims[1]],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(8,8,20,0.9)'),
            zaxis=dict(title=DIM_NAMES[default_dims[2]],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(8,8,20,0.9)'),
            aspectratio=dict(x=1, y=1, z=0.8),
            camera=dict(
                eye=dict(x=1.8, y=1.2, z=0.8),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        updatemenus=[
            # Frame selector dropdown
            dict(
                buttons=buttons,
                direction='down',
                showactive=True,
                x=0.02,
                xanchor='left',
                y=0.98,
                yanchor='top',
                bgcolor='rgba(20, 20, 40, 0.8)',
                bordercolor='rgba(100, 100, 150, 0.5)',
                font=dict(color='#ccc', size=12),
                pad=dict(r=10, t=10),
            ),
        ],
        template='plotly_dark',
        paper_bgcolor='rgb(8, 8, 20)',
        margin=dict(l=0, r=0, t=80, b=60),
        legend=dict(
            x=0.99, y=0.99,
            xanchor='right',
            bgcolor='rgba(0,0,0,0.6)',
            font=dict(size=9),
            itemsizing='constant',
        ),
        annotations=[
            dict(
                text=(
                    "Each frame is a perspectival act — choosing which dimensions to see.<br>"
                    "Entities invisible in the Physical frame become visible in the Constraint Lattice frame.<br>"
                    "Null spaces (×) mark regions where no entity has formed in this projection."
                ),
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.06,
                font=dict(size=9, color='rgba(180,180,180,0.6)'),
                xanchor='center',
            ),
        ],
    )

    return fig


# ============================================================
# GENERATE
# ============================================================

output_dir = os.path.dirname(os.path.abspath(__file__))

print("Generating perspectival manifold...")
fig = build_full_visualization()
outpath = os.path.join(output_dir, "perspectival_manifold.html")
fig.write_html(outpath)
print(f"  -> {outpath}")

try:
    fig.write_image(os.path.join(output_dir, "perspectival_manifold.png"),
                    width=1400, height=900, scale=2)
    print(f"  -> perspectival_manifold.png")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("\nAvailable frames:")
for fname, fdims in FRAMES.items():
    print(f"  {fname}: ({DIM_NAMES[fdims[0]]}, {DIM_NAMES[fdims[1]]}, {DIM_NAMES[fdims[2]]})")

print("\nDone.")
