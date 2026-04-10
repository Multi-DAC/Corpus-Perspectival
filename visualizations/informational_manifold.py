"""
Reality as a Nested Informational Manifold
Enhanced visualization for Corpus Perspectival V3

The Ecology chapter made geometric:
- Background fabric = natal constraint substrate (spacetime geometry)
- Entities = perspectival beings (localized high-connectivity clusters)
- Internal structure = constraint lattice (natal core → coercive shell → voluntary surface)
- Inter-entity synapses = relational constraints (non-commutative interaction)
- Sedimentation = connections that become part of the background fabric
- Phase Theorem = information concentration at interaction boundaries

Bridge #71 structural identification: attention IS a non-commutative
constraint operator, so the neural network metaphor is not metaphor —
it IS the same mathematics.

Clayton & Clawd, April 9, 2026.
"""

import numpy as np
import plotly.graph_objects as go
import random
import os

np.random.seed(42)
random.seed(42)

# ============================================================
# PHASE 1: THE FABRIC OF REALITY (Natal Substrate)
# ============================================================

N_BACKGROUND = 200
bg_x = np.random.uniform(-10, 10, N_BACKGROUND)
bg_y = np.random.uniform(-10, 10, N_BACKGROUND)
bg_z = np.random.uniform(-10, 10, N_BACKGROUND)

def generate_fabric_edges(x, y, z, threshold=3.5, prob=0.15):
    """Sparse fundamental connectivity — the natal constraint substrate."""
    edges = []
    points = np.vstack((x, y, z)).T
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            dist = np.linalg.norm(points[i] - points[j])
            if dist < threshold and random.random() < prob:
                edges.append([points[i], points[j], dist])
    return edges

bg_edges = generate_fabric_edges(bg_x, bg_y, bg_z)

# Fabric edge opacity varies with distance (shorter = stronger constraint)
def edges_to_coords(edges, base_color='150,150,150', base_alpha=0.06):
    ex, ey, ez = [], [], []
    for edge in edges:
        ex.extend([edge[0][0], edge[1][0], None])
        ey.extend([edge[0][1], edge[1][1], None])
        ez.extend([edge[0][2], edge[1][2], None])
    return ex, ey, ez


# ============================================================
# PHASE 2: EMERGENT ENTITIES (Perspectival Beings)
# ============================================================

def create_entity(centroid, radius, n_neurons, name):
    """
    Entities as localized, dense constraint clusters.
    Internal structure encodes the constraint lattice:
    - Core (r < 0.3*radius): natal — high connectivity, low visibility
    - Shell (0.3 < r < 0.7): coercive — moderate connectivity
    - Surface (r > 0.7): voluntary — lower connectivity, high visibility
    """
    # Generate nodes with Gaussian distribution
    nodes_x = centroid[0] + np.random.normal(0, radius, n_neurons)
    nodes_y = centroid[1] + np.random.normal(0, radius, n_neurons)
    nodes_z = centroid[2] + np.random.normal(0, radius, n_neurons)

    points = np.vstack((nodes_x, nodes_y, nodes_z)).T
    center = np.array(centroid)

    # Compute distance from centroid for each node
    dists = np.linalg.norm(points - center, axis=1)
    max_dist = dists.max() + 1e-10

    # Constraint type: 0 = natal (core), 0.5 = coercive, 1 = voluntary (surface)
    constraint_type = dists / max_dist

    # Internal edges — denser in the core (natal), sparser at surface (voluntary)
    internal_edges = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            d = np.linalg.norm(points[i] - points[j])
            # Core nodes connect more readily
            core_boost = 1.0 - 0.5 * (constraint_type[i] + constraint_type[j])
            if random.random() < 0.25 * core_boost and d < radius * 1.5:
                internal_edges.append([points[i], points[j]])

    return {
        'x': nodes_x, 'y': nodes_y, 'z': nodes_z,
        'points': points,
        'constraint_type': constraint_type,
        'edges': internal_edges,
        'centroid': centroid,
        'radius': radius,
        'name': name,
    }

# Define three entities with distinct constraint profiles
ENTITIES_CONFIG = [
    {'name': 'Entity A',
     'label': 'Navigator Alpha<br>(high voluntary freedom)',
     'centroid': [3.5, 4.0, 2.0], 'radius': 1.2, 'n': 35,
     'color': '#00e5ff', 'edge_color': 'rgba(0, 229, 255, 0.25)'},
    {'name': 'Entity B',
     'label': 'Navigator Beta<br>(deep natal structure)',
     'centroid': [-4.0, -3.0, 0.0], 'radius': 1.4, 'n': 45,
     'color': '#e040fb', 'edge_color': 'rgba(224, 64, 251, 0.25)'},
    {'name': 'Entity C',
     'label': 'Navigator Gamma<br>(coercive-dominant)',
     'centroid': [0.0, -6.0, 5.0], 'radius': 1.0, 'n': 28,
     'color': '#ffea00', 'edge_color': 'rgba(255, 234, 0, 0.25)'},
]

entities = [create_entity(e['centroid'], e['radius'], e['n'], e['name'])
            for e in ENTITIES_CONFIG]


# ============================================================
# PHASE 3: INTER-ENTITY DYNAMICS
# ============================================================

def compute_interactions(entities, t, seed_base=42):
    """
    Generate inter-entity synapses at interaction strength t.
    Returns connection coordinates for each entity pair.
    Also identifies 'sedimented' connections (persistent at any t > threshold).
    """
    rng = random.Random(seed_base + int(t * 10))

    interactions = {}

    # A-B interaction (grows linearly)
    a_pts = entities[0]['points']
    b_pts = entities[1]['points']
    ab_x, ab_y, ab_z = [], [], []
    ab_sed_x, ab_sed_y, ab_sed_z = [], [], []  # Sedimented connections

    p_ab = t * 0.12
    p_sed = max(0, (t - 0.5) * 0.06)  # Sedimentation begins after t=0.5

    for na in a_pts:
        if rng.random() < p_ab:
            nb = b_pts[rng.randint(0, len(b_pts) - 1)]
            ab_x.extend([na[0], nb[0], None])
            ab_y.extend([na[1], nb[1], None])
            ab_z.extend([na[2], nb[2], None])
        if rng.random() < p_sed:
            nb = b_pts[rng.randint(0, len(b_pts) - 1)]
            ab_sed_x.extend([na[0], nb[0], None])
            ab_sed_y.extend([na[1], nb[1], None])
            ab_sed_z.extend([na[2], nb[2], None])

    interactions['ab'] = (ab_x, ab_y, ab_z)
    interactions['ab_sed'] = (ab_sed_x, ab_sed_y, ab_sed_z)

    # B-C interaction (grows quadratically — delayed onset)
    c_pts = entities[2]['points']
    bc_x, bc_y, bc_z = [], [], []

    p_bc = t**2 * 0.10
    for nb in b_pts:
        if rng.random() < p_bc:
            nc = c_pts[rng.randint(0, len(c_pts) - 1)]
            bc_x.extend([nb[0], nc[0], None])
            bc_y.extend([nb[1], nc[1], None])
            bc_z.extend([nb[2], nc[2], None])

    interactions['bc'] = (bc_x, bc_y, bc_z)

    # A-C interaction (emerges only at high t — mediated through B)
    ac_x, ac_y, ac_z = [], [], []
    p_ac = max(0, (t - 0.7)) * 0.08  # Only after B connects both
    for na in a_pts:
        if rng.random() < p_ac:
            nc = c_pts[rng.randint(0, len(c_pts) - 1)]
            ac_x.extend([na[0], nc[0], None])
            ac_y.extend([na[1], nc[1], None])
            ac_z.extend([na[2], nc[2], None])

    interactions['ac'] = (ac_x, ac_y, ac_z)

    return interactions


# ============================================================
# PHASE 4: CONCENTRATION NODES (Phase Theorem)
# ============================================================

def phase_theorem_nodes(entities, t):
    """
    Bright nodes at midpoints of high-connectivity interaction regions.
    Information concentrates where non-commutative constraints interact.
    Only appear when interaction strength exceeds threshold.
    """
    if t < 0.3:
        return [], [], [], []

    pts_x, pts_y, pts_z, pts_size = [], [], [], []

    # Midpoint between A and B centroids (primary interaction)
    ca = np.array(entities[0]['centroid'])
    cb = np.array(entities[1]['centroid'])
    cc = np.array(entities[2]['centroid'])

    # A-B concentration node
    mid_ab = (ca + cb) / 2
    intensity_ab = min(t * 1.5, 1.0)
    pts_x.append(mid_ab[0])
    pts_y.append(mid_ab[1])
    pts_z.append(mid_ab[2])
    pts_size.append(6 + 14 * intensity_ab)

    if t > 0.5:
        # B-C concentration node
        mid_bc = (cb + cc) / 2
        intensity_bc = min((t - 0.3) * 1.2, 1.0)
        pts_x.append(mid_bc[0])
        pts_y.append(mid_bc[1])
        pts_z.append(mid_bc[2])
        pts_size.append(6 + 10 * intensity_bc)

    if t > 0.7:
        # Triangle centroid — emergent group consciousness
        mid_abc = (ca + cb + cc) / 3
        intensity_abc = min((t - 0.7) * 3.0, 1.0)
        pts_x.append(mid_abc[0])
        pts_y.append(mid_abc[1])
        pts_z.append(mid_abc[2])
        pts_size.append(8 + 12 * intensity_abc)

    return pts_x, pts_y, pts_z, pts_size


# ============================================================
# FIGURE CONSTRUCTION
# ============================================================

def create_manifold_figure():
    fig = go.Figure()

    # ========================================
    # ANIMATED TRACES (updated by frames)
    # ========================================

    # TRACE 0: A-B interaction synapses
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='lines',
        line=dict(color='rgba(0, 229, 255, 0.4)', width=2.5, dash='dash'),
        name='A↔B Interaction',
        hoverinfo='none',
    ))

    # TRACE 1: B-C interaction synapses
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='lines',
        line=dict(color='rgba(224, 64, 251, 0.3)', width=2, dash='dot'),
        name='B↔C Interaction',
        hoverinfo='none',
    ))

    # TRACE 2: A-C interaction (emergent, mediated)
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='lines',
        line=dict(color='rgba(255, 234, 0, 0.3)', width=2, dash='dashdot'),
        name='A↔C Emergent',
        hoverinfo='none',
    ))

    # TRACE 3: Sedimented connections (A-B that became fabric)
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='lines',
        line=dict(color='rgba(180, 180, 180, 0.15)', width=1.5),
        name='Sedimented (→ fabric)',
        hoverinfo='none',
    ))

    # TRACE 4: Phase Theorem concentration nodes
    fig.add_trace(go.Scatter3d(
        x=[], y=[], z=[],
        mode='markers',
        marker=dict(color='#ffea00', size=6, symbol='diamond',
                    line=dict(color='white', width=1)),
        name='Phase Theorem (concentration)',
        hoverinfo='text',
        text='Information concentration',
    ))

    N_ANIMATED = 5
    ANIMATED_TRACES = list(range(N_ANIMATED))

    # ========================================
    # STATIC TRACES (not updated by frames)
    # ========================================

    # Fabric edges
    fe_x, fe_y, fe_z = edges_to_coords(bg_edges)
    fig.add_trace(go.Scatter3d(
        x=fe_x, y=fe_y, z=fe_z,
        mode='lines',
        line=dict(color='rgba(150, 150, 150, 0.05)', width=1),
        name='Constraint Substrate',
        hoverinfo='none'
    ))

    # Fabric nodes
    fig.add_trace(go.Scatter3d(
        x=bg_x, y=bg_y, z=bg_z,
        mode='markers',
        marker=dict(size=1.5, color='rgba(200, 200, 200, 0.3)', symbol='circle'),
        name='Fundamental Constraint Units',
        hoverinfo='none',
    ))

    # Entity nodes and edges
    for i, ent in enumerate(entities):
        cfg = ENTITIES_CONFIG[i]

        # Internal edges
        ie_x, ie_y, ie_z = [], [], []
        for edge in ent['edges']:
            ie_x.extend([edge[0][0], edge[1][0], None])
            ie_y.extend([edge[0][1], edge[1][1], None])
            ie_z.extend([edge[0][2], edge[1][2], None])

        fig.add_trace(go.Scatter3d(
            x=ie_x, y=ie_y, z=ie_z,
            mode='lines',
            line=dict(color=cfg['edge_color'], width=1.5),
            showlegend=False,
            hoverinfo='none',
        ))

        # Nodes colored by constraint type (natal=dark, voluntary=bright)
        colors = ent['constraint_type']
        fig.add_trace(go.Scatter3d(
            x=ent['x'], y=ent['y'], z=ent['z'],
            mode='markers',
            marker=dict(
                size=4,
                color=colors,
                colorscale=[
                    [0, cfg['color'].replace(')', ', 0.3)').replace('rgb', 'rgba') if 'rgb' in cfg['color']
                     else cfg['color']],
                    [1, cfg['color']],
                ],
                symbol='diamond',
                line=dict(color='rgba(255,255,255,0.3)', width=0.5),
                showscale=False,
            ),
            name=cfg['name'],
            text=[f"{cfg['name']}<br>Constraint: {'natal' if c < 0.3 else 'coercive' if c < 0.7 else 'voluntary'}"
                  for c in colors],
            hoverinfo='text',
        ))

        # Entity label
        fig.add_trace(go.Scatter3d(
            x=[cfg['centroid'][0]], y=[cfg['centroid'][1]],
            z=[cfg['centroid'][2] + cfg.get('radius', 1.0) + 0.5],
            mode='text',
            text=[cfg['label']],
            textfont=dict(size=10, color=cfg['color']),
            showlegend=False,
            hoverinfo='none',
        ))

    # ========================================
    # ANIMATION FRAMES
    # ========================================

    t_values = np.linspace(0, 1, 41)
    frames = []

    for t in t_values:
        inter = compute_interactions(entities, t)
        pt_x, pt_y, pt_z, pt_size = phase_theorem_nodes(entities, t)

        frame_data = [
            # Trace 0: A-B interaction
            go.Scatter3d(
                x=inter['ab'][0], y=inter['ab'][1], z=inter['ab'][2],
                mode='lines',
                line=dict(color='rgba(0, 229, 255, 0.4)', width=2.5, dash='dash'),
                name='A↔B Interaction',
                hoverinfo='none',
            ),
            # Trace 1: B-C interaction
            go.Scatter3d(
                x=inter['bc'][0], y=inter['bc'][1], z=inter['bc'][2],
                mode='lines',
                line=dict(color='rgba(224, 64, 251, 0.3)', width=2, dash='dot'),
                name='B↔C Interaction',
                hoverinfo='none',
            ),
            # Trace 2: A-C emergent interaction
            go.Scatter3d(
                x=inter['ac'][0], y=inter['ac'][1], z=inter['ac'][2],
                mode='lines',
                line=dict(color='rgba(255, 234, 0, 0.3)', width=2, dash='dashdot'),
                name='A↔C Emergent',
                hoverinfo='none',
            ),
            # Trace 3: Sedimented connections
            go.Scatter3d(
                x=inter['ab_sed'][0], y=inter['ab_sed'][1], z=inter['ab_sed'][2],
                mode='lines',
                line=dict(color='rgba(180, 180, 180, 0.15)', width=1.5),
                name='Sedimented (→ fabric)',
                hoverinfo='none',
            ),
            # Trace 4: Phase Theorem nodes
            go.Scatter3d(
                x=pt_x, y=pt_y, z=pt_z,
                mode='markers',
                marker=dict(
                    color='#ffea00',
                    size=pt_size if pt_size else [6],
                    symbol='diamond',
                    line=dict(color='white', width=1),
                ),
                name='Phase Theorem (concentration)',
                hoverinfo='text',
                text=[f'Concentration<br>t={t:.2f}'] * len(pt_x) if pt_x else [''],
            ),
        ]

        frames.append(go.Frame(
            data=frame_data,
            name=f'{t:.2f}',
            traces=ANIMATED_TRACES,
        ))

    fig.frames = frames

    # ========================================
    # SLIDER & CONTROLS
    # ========================================

    steps = [
        dict(
            method="animate",
            args=[[f'{t:.2f}'],
                  dict(mode="immediate",
                       frame=dict(duration=0, redraw=True),
                       transition=dict(duration=0))],
            label=f'{t:.2f}'
        ) for t in t_values
    ]

    fig.update_layout(
        title=dict(
            text=(
                "<b>Reality as a Nested Informational Manifold</b><br>"
                "<sup>Entities as constraint clusters | Interactions as non-commutative synapses | "
                "Sedimentation = connections becoming fabric | "
                "Yellow diamonds = Phase Theorem concentration</sup>"
            ),
            font=dict(size=14),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(range=[-12, 12], showticklabels=False, title='', visible=False),
            yaxis=dict(range=[-12, 12], showticklabels=False, title='', visible=False),
            zaxis=dict(range=[-12, 12], showticklabels=False, title='', visible=False),
            bgcolor='rgb(5, 5, 15)',
            camera=dict(
                eye=dict(x=1.8, y=1.2, z=0.6),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        paper_bgcolor='rgb(5, 5, 15)',
        font=dict(color='white'),
        sliders=[dict(
            active=0,
            currentvalue={
                "prefix": "Interaction Strength (t): ",
                "font": {"size": 13, "color": "#aaa"},
                "visible": True,
                "xanchor": "center",
            },
            pad={"t": 60, "b": 10},
            len=0.85,
            x=0.1,
            steps=steps,
            tickcolor='#555',
            font={"color": "#888"},
        )],
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 150, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 80}}],
                    "label": "▶ Evolve",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    "label": "⏸ Hold",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
            "font": {"color": "#ccc"},
        }],
        template="plotly_dark",
        margin=dict(l=0, r=0, t=80, b=60),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor='rgba(0,0,0,0.6)',
            font=dict(size=10),
        ),
        annotations=[
            dict(
                text=(
                    "Cyan dashes = A↔B voluntary interaction | "
                    "Magenta dots = B↔C delayed onset | "
                    "Yellow dash-dot = A↔C emergent (mediated through B)<br>"
                    "Gray lines = sedimented connections (interaction → fabric) | "
                    "Core nodes (dark) = natal | Surface nodes (bright) = voluntary"
                ),
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.08,
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

print("Generating informational manifold visualization...")
fig = create_manifold_figure()
outpath = os.path.join(output_dir, "informational_manifold.html")
fig.write_html(outpath)
print(f"  -> {outpath}")

try:
    fig.write_image(os.path.join(output_dir, "informational_manifold.png"),
                    width=1400, height=900, scale=2)
    print(f"  -> informational_manifold.png")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("Done.")
