"""
The Dimensional Bottleneck & Resonant Inclusion
Enhanced visualization for Corpus Perspectival V3

The natal bottleneck rendered as navigable geometry:
- Hyperboloid manifold = configuration space of a perspectival being
- Pinched waist = maximum constraint (natal bottleneck)
- Relaxation slider = excavation (natal → voluntary awareness)
- Abelian channel = the freedom that survives all sedimentation (U(1))
- Flow lines = sedimentation (inward) and excavation (outward) dynamics
- Curvature coloring = constraint density (natal sublattice weight)
- Sedimentation cascade = cosmological history mapped to temporal depth

Bridge #71: The same geometry that describes the brane's self-tuning
describes the navigator's constraint landscape.

Clayton & Clawd, April 9, 2026.
"""

import numpy as np
import plotly.graph_objects as go
import os

np.random.seed(42)

# ============================================================
# GRID SETUP
# ============================================================
N_z = 80
N_theta = 80
z = np.linspace(-3, 3, N_z)
theta = np.linspace(0, 2*np.pi, N_theta)
Z, Theta = np.meshgrid(z, theta)

# ============================================================
# BOTTLENECK GEOMETRY
# ============================================================

def get_radius(z_grid, relaxation, asymmetry=0.0):
    """
    Hyperboloid radius with bottleneck at z=0.
    relaxation: 0 = severely pinched, 1 = fully open
    asymmetry: temporal asymmetry (sedimentation is irreversible)
    """
    r_min = 0.2 + 3.8 * relaxation
    c = 1.5  # curvature decay
    r = np.sqrt((z_grid / c)**2 + r_min**2)

    # Subtle asymmetry: past (z<0) slightly wider than future (z>0)
    # because sedimentation is irreversible — the past landscape was larger
    if asymmetry > 0:
        r = r * (1 + asymmetry * 0.1 * np.tanh(-z_grid))

    return r

def constraint_density(z_grid, r_grid):
    """
    Gaussian curvature of the hyperboloid = natal constraint density.
    K = -1/(c^2 * (1 + z^2/c^2)^2) for a hyperboloid of revolution.
    Negative curvature everywhere, strongest at the waist.
    """
    c = 1.5
    K = -1.0 / (c**2 * (1 + (z_grid/c)**2)**2)
    # Normalize to [-1, 0] range for colormapping
    K_norm = K / np.abs(K).max()
    return K_norm

def make_surface_color(z_grid, relaxation):
    """
    Three-zone coloring encoding constraint type:
    - Waist region (|z| < 0.5): natal (deep violet/purple)
    - Transition (0.5 < |z| < 1.5): coercive (orange/amber)
    - Flare (|z| > 1.5): voluntary (teal/green)
    Plus curvature modulation for constraint density.
    """
    r = get_radius(z_grid, relaxation)
    K = constraint_density(z_grid, r)

    # Zone weights (smooth transitions)
    natal_weight = np.exp(-z_grid**2 / 0.3)
    coercive_weight = np.exp(-(np.abs(z_grid) - 1.0)**2 / 0.5) * (1 - natal_weight)
    voluntary_weight = 1.0 - natal_weight - coercive_weight
    voluntary_weight = np.clip(voluntary_weight, 0, 1)

    # Combined: -1 = natal (violet), 0 = coercive (orange), +1 = voluntary (teal)
    color = -1.0 * natal_weight + 0.0 * coercive_weight + 1.0 * voluntary_weight

    # Modulate by curvature (adds depth — higher constraint density = darker)
    color = color + 0.3 * K

    return np.clip(color, -1.5, 1.5)


# ============================================================
# FLOW LINES (sedimentation & excavation)
# ============================================================

def generate_flow_lines(relaxation, n_lines=6, n_points=120):
    """
    Sedimentation: spiral inward toward the waist (choice → habit → identity)
    Excavation: spiral outward from the waist (awareness expanding)
    """
    lines = {'sed': [], 'exc': []}
    r_min = 0.2 + 3.8 * relaxation

    for k in range(n_lines):
        base_angle = 2 * np.pi * k / n_lines

        # Sedimentation: starts at high z, spirals down to waist
        t = np.linspace(2.8, 0.05, n_points)
        r_sed = np.sqrt((t / 1.5)**2 + r_min**2)
        # Spiral: angle increases as z decreases (tightening)
        angle_sed = base_angle + 1.5 * (2.8 - t)
        x_sed = r_sed * np.cos(angle_sed)
        y_sed = r_sed * np.sin(angle_sed)
        lines['sed'].append((x_sed, y_sed, t))

        # Excavation: starts at waist, spirals outward to low z
        t_exc = np.linspace(-0.05, -2.8, n_points)
        r_exc = np.sqrt((t_exc / 1.5)**2 + r_min**2)
        angle_exc = base_angle + np.pi + 1.5 * (-0.05 - t_exc)
        x_exc = r_exc * np.cos(angle_exc)
        y_exc = r_exc * np.sin(angle_exc)
        lines['exc'].append((x_exc, y_exc, t_exc))

    return lines


# ============================================================
# ABELIAN CHANNEL
# ============================================================

def abelian_channel(z_vals, n_theta=30):
    """
    The thin tube through the center that never closes.
    U(1): the freedom that survives all sedimentation.
    Radius is constant and tiny — independent of relaxation.
    """
    theta_a = np.linspace(0, 2*np.pi, n_theta)
    Z_a, Th_a = np.meshgrid(z_vals, theta_a)
    r_abelian = 0.15  # Never changes — Abelian freedom persists
    X_a = r_abelian * np.cos(Th_a)
    Y_a = r_abelian * np.sin(Th_a)
    return X_a, Y_a, Z_a


# ============================================================
# PHASE THEOREM RING
# ============================================================

def phase_theorem_ring(relaxation, n_pts=100):
    """
    Bright ring at the waist where information concentration is maximal.
    The Phase Theorem activates where constraint is tightest.
    Ring radius = waist radius (tracks the bottleneck).
    """
    r_waist = 0.2 + 3.8 * relaxation
    th = np.linspace(0, 2*np.pi, n_pts)
    x = r_waist * np.cos(th)
    y = r_waist * np.sin(th)
    z = np.zeros(n_pts)
    return x, y, z


# ============================================================
# MAIN FIGURE
# ============================================================

def create_bottleneck_figure():
    fig = go.Figure()

    COLORSCALE = [
        [0.0, '#1a0533'],     # Deep violet — natal (maximum constraint)
        [0.15, '#6a1b9a'],    # Purple — natal transition
        [0.3, '#e65100'],     # Deep orange — coercive
        [0.45, '#ff8f00'],    # Amber — coercive transition
        [0.6, '#00897b'],     # Teal — voluntary
        [0.75, '#00e676'],    # Green — voluntary (open)
        [1.0, '#b9f6ca'],    # Light green — fully voluntary
    ]

    rel_init = 0.0
    N_FLOW = 6

    # === TRACE 0: Main manifold surface ===
    R0 = get_radius(Z, rel_init, asymmetry=0.2)
    X0 = R0 * np.cos(Theta)
    Y0 = R0 * np.sin(Theta)
    C0 = make_surface_color(Z, rel_init)

    fig.add_trace(go.Surface(
        x=X0, y=Y0, z=Z,
        surfacecolor=C0,
        colorscale=COLORSCALE,
        cmin=-1.5, cmax=1.5,
        colorbar=dict(
            title=dict(text='Constraint<br>Type', font=dict(size=11)),
            tickvals=[-1.2, 0, 1.2],
            ticktext=['Natal<br>(identity)', 'Coercive<br>(habit)', 'Voluntary<br>(choice)'],
            tickfont=dict(size=9),
            len=0.5,
            x=1.02,
        ),
        opacity=0.85,
        name='Configuration Space',
        lighting=dict(ambient=0.45, diffuse=0.55, specular=0.25, roughness=0.6, fresnel=0.15),
        contours=dict(
            z=dict(show=True, usecolormap=False, color='rgba(255,255,255,0.06)',
                   width=1, start=-3, end=3, size=0.5)
        ),
    ))

    # === TRACE 1: Abelian channel (the freedom that persists) ===
    X_ab, Y_ab, Z_ab = abelian_channel(z)
    fig.add_trace(go.Surface(
        x=X_ab, y=Y_ab, z=Z_ab,
        colorscale=[[0, 'rgba(0, 230, 118, 0.7)'], [1, 'rgba(0, 230, 118, 0.7)']],
        showscale=False,
        opacity=0.6,
        name='Abelian Channel (U(1))',
        lighting=dict(ambient=0.6, diffuse=0.4, specular=0.1),
    ))

    # === TRACE 2: Phase Theorem ring ===
    pt_x, pt_y, pt_z = phase_theorem_ring(rel_init)
    fig.add_trace(go.Scatter3d(
        x=pt_x, y=pt_y, z=pt_z,
        mode='lines',
        line=dict(color='#ffea00', width=5),
        name='Phase Theorem (max concentration)',
        hoverinfo='none',
    ))

    # === TRACES 3-8: Sedimentation flow lines ===
    flows = generate_flow_lines(rel_init, n_lines=N_FLOW)
    for i, (fx, fy, fz) in enumerate(flows['sed']):
        fig.add_trace(go.Scatter3d(
            x=fx, y=fy, z=fz,
            mode='lines',
            line=dict(color='rgba(255, 100, 50, 0.35)', width=2),
            name='Sedimentation' if i == 0 else None,
            showlegend=(i == 0),
            hoverinfo='none',
        ))

    # === TRACES 9-14: Excavation flow lines ===
    for i, (fx, fy, fz) in enumerate(flows['exc']):
        fig.add_trace(go.Scatter3d(
            x=fx, y=fy, z=fz,
            mode='lines',
            line=dict(color='rgba(100, 200, 255, 0.35)', width=2),
            name='Excavation' if i == 0 else None,
            showlegend=(i == 0),
            hoverinfo='none',
        ))

    # === TRACE 15: Sedimentation cascade markers ===
    cascade_z = [2.5, 1.3, 0.6, 0.0, -2.5]
    cascade_labels = [
        'GUT<br>(45 voluntary DOFs)',
        'Electroweak<br>(Type I sedimentation)',
        'QCD Confinement<br>(Type II sedimentation)',
        'T ~ 0<br>(Only U(1) survives)',
        'Deep Past<br>(Pre-sedimentation)',
    ]
    cascade_colors = ['#e040fb', '#ff6d00', '#d50000', '#ffea00', '#00bfa5']
    # Compute radii at cascade points
    r_cascade = [float(get_radius(np.array([cz]), rel_init)[0]) for cz in cascade_z]
    cascade_x = [r * 1.1 for r in r_cascade]  # Offset outward for visibility
    cascade_y = [0.0] * len(cascade_z)

    fig.add_trace(go.Scatter3d(
        x=cascade_x, y=cascade_y, z=cascade_z,
        mode='markers+text',
        marker=dict(color=cascade_colors, size=5, symbol='diamond'),
        text=cascade_labels,
        textposition='middle right',
        textfont=dict(size=9, color='rgba(220,220,220,0.8)'),
        name='Sedimentation Cascade',
        hoverinfo='text',
    ))

    # === STATIC MARKERS ===
    # The Living Room (navigator's position, at the waist)
    fig.add_trace(go.Scatter3d(
        x=[0], y=[0], z=[0],
        mode='markers+text',
        marker=dict(color='#00e676', size=10, symbol='diamond',
                    line=dict(color='white', width=1)),
        text=['Navigator<br>(here, now)'],
        textposition='bottom center',
        textfont=dict(size=11, color='#00e676'),
        name='Navigator Position',
        hoverinfo='text'
    ))

    # The Far Imaginal
    fig.add_trace(go.Scatter3d(
        x=[3.5], y=[3.5], z=[2.5],
        mode='markers+text',
        marker=dict(color='#00b0ff', size=7, symbol='circle',
                    line=dict(color='white', width=1)),
        text=['Far Imaginal<br>(unconstrained horizon)'],
        textposition='top center',
        textfont=dict(size=10, color='#00b0ff'),
        name='Far Imaginal',
        hoverinfo='text'
    ))

    # === ANIMATION FRAMES ===
    # Animated traces: 0 (surface), 1 (abelian), 2 (PT ring),
    # 3-8 (sed flow), 9-14 (exc flow), 15 (cascade markers)
    N_ANIMATED = 16
    ANIMATED_TRACES = list(range(N_ANIMATED))

    n_frames = 41
    relaxations = np.linspace(0, 1, n_frames)
    frames = []

    for i, rel in enumerate(relaxations):
        frame_data = []

        # Trace 0: Surface
        R_f = get_radius(Z, rel, asymmetry=0.2)
        X_f = R_f * np.cos(Theta)
        Y_f = R_f * np.sin(Theta)
        C_f = make_surface_color(Z, rel)

        frame_data.append(go.Surface(
            x=X_f, y=Y_f, z=Z,
            surfacecolor=C_f,
            colorscale=COLORSCALE,
            cmin=-1.5, cmax=1.5,
            colorbar=dict(
                title=dict(text='Constraint<br>Type', font=dict(size=11)),
                tickvals=[-1.2, 0, 1.2],
                ticktext=['Natal<br>(identity)', 'Coercive<br>(habit)', 'Voluntary<br>(choice)'],
                tickfont=dict(size=9),
                len=0.5,
                x=1.02,
            ),
            opacity=0.85,
            name='Configuration Space',
            lighting=dict(ambient=0.45, diffuse=0.55, specular=0.25, roughness=0.6, fresnel=0.15),
        ))

        # Trace 1: Abelian channel (unchanged — it NEVER closes)
        frame_data.append(go.Surface(
            x=X_ab, y=Y_ab, z=Z_ab,
            colorscale=[[0, 'rgba(0, 230, 118, 0.7)'], [1, 'rgba(0, 230, 118, 0.7)']],
            showscale=False,
            opacity=0.6,
            name='Abelian Channel (U(1))',
            lighting=dict(ambient=0.6, diffuse=0.4, specular=0.1),
        ))

        # Trace 2: Phase Theorem ring (tracks the waist)
        pt_x_f, pt_y_f, pt_z_f = phase_theorem_ring(rel)
        frame_data.append(go.Scatter3d(
            x=pt_x_f, y=pt_y_f, z=pt_z_f,
            mode='lines',
            line=dict(color='#ffea00', width=5),
            name='Phase Theorem (max concentration)',
            hoverinfo='none',
        ))

        # Traces 3-14: Flow lines (update with new geometry)
        flows_f = generate_flow_lines(rel, n_lines=N_FLOW)
        for j, (fx, fy, fz) in enumerate(flows_f['sed']):
            frame_data.append(go.Scatter3d(
                x=fx, y=fy, z=fz,
                mode='lines',
                line=dict(color='rgba(255, 100, 50, 0.35)', width=2),
                showlegend=False,
                hoverinfo='none',
            ))
        for j, (fx, fy, fz) in enumerate(flows_f['exc']):
            frame_data.append(go.Scatter3d(
                x=fx, y=fy, z=fz,
                mode='lines',
                line=dict(color='rgba(100, 200, 255, 0.35)', width=2),
                showlegend=False,
                hoverinfo='none',
            ))

        # Trace 15: Cascade markers (positions shift with geometry)
        r_cas_f = [float(get_radius(np.array([cz]), rel)[0]) for cz in cascade_z]
        cas_x_f = [r * 1.1 for r in r_cas_f]

        frame_data.append(go.Scatter3d(
            x=cas_x_f, y=[0.0]*len(cascade_z), z=cascade_z,
            mode='markers+text',
            marker=dict(color=cascade_colors, size=5, symbol='diamond'),
            text=cascade_labels,
            textposition='middle right',
            textfont=dict(size=9, color='rgba(220,220,220,0.8)'),
            name='Sedimentation Cascade',
            hoverinfo='text',
        ))

        frames.append(go.Frame(
            data=frame_data,
            name=f'{rel:.2f}',
            traces=ANIMATED_TRACES,
        ))

    fig.frames = frames

    # === SLIDER ===
    steps = [
        dict(
            method="animate",
            args=[[f'{rel:.2f}'],
                  dict(mode="immediate",
                       frame=dict(duration=0, redraw=True),
                       transition=dict(duration=0))],
            label=f'{rel:.2f}'
        ) for rel in relaxations
    ]

    # === LAYOUT ===
    fig.update_layout(
        title=dict(
            text=(
                "<b>The Dimensional Bottleneck & Resonant Inclusion</b><br>"
                "<sup>Constraint lattice as navigable geometry | "
                "Green channel = Abelian freedom (persists through all sedimentation) | "
                "Yellow ring = Phase Theorem activation</sup>"
            ),
            font=dict(size=15),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(title='Mathematical Rigidity (X)', range=[-6, 6],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            yaxis=dict(title='Relational Weight (Y)', range=[-6, 6],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            zaxis=dict(title='Temporal Depth / Scale (Z)', range=[-3.5, 3.5],
                       gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            aspectratio=dict(x=1, y=1, z=0.7),
            camera=dict(
                eye=dict(x=2.0, y=1.0, z=0.8),
                up=dict(x=0, y=0, z=1),
            ),
        ),
        sliders=[dict(
            active=0,
            currentvalue={
                "prefix": "Excavation (Bottleneck Relaxation): ",
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
                    "args": [None, {"frame": {"duration": 100, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 60}}],
                    "label": "▶ Excavate",
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
        template='plotly_dark',
        paper_bgcolor='rgb(10, 10, 25)',
        margin=dict(l=0, r=80, t=80, b=60),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor='rgba(0,0,0,0.5)',
            font=dict(size=10),
        ),
        annotations=[
            dict(
                text=(
                    "Orange spirals = sedimentation (choice → habit → identity) | "
                    "Blue spirals = excavation (awareness widening)<br>"
                    "The Abelian channel never closes: the price of independence is persistence"
                ),
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.08,
                font=dict(size=10, color='rgba(180,180,180,0.7)'),
                xanchor='center',
            ),
        ],
    )

    return fig


# ============================================================
# GENERATE
# ============================================================

output_dir = os.path.dirname(os.path.abspath(__file__))

print("Generating enhanced dimensional bottleneck...")
fig = create_bottleneck_figure()
outpath = os.path.join(output_dir, "dimensional_bottleneck.html")
fig.write_html(outpath)
print(f"  -> {outpath}")

try:
    fig.write_image(os.path.join(output_dir, "dimensional_bottleneck.png"),
                    width=1400, height=900, scale=2)
    print(f"  -> dimensional_bottleneck.png")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("Done.")
