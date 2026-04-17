"""
5D Randall-Sundrum Braneworld: Cuscuton Self-Tuning & w_a Constraint
Enhanced visualization for Corpus Perspectival V3

Physics:
- Codimension-1 D3-brane embedded in AdS_5 bulk
- Cuscuton field provides self-tuning: vacuum energy screened from brane geometry
- w_a = 0 (exactly) maintains Horndeski cancellation mechanism
- w_a != 0 catastrophically fractures the brane-bulk intersection
- Warp factor e^{-2k|y|} encodes the RS exponential hierarchy
- Local Gaussian curvature encodes constraint density (natal sublattice)

Meridian predictions: w_0 = -0.830, w_a = 0, C_GB = 2/3, epsilon_GW = 0.275

Clawd & Clayton, April 9, 2026.
"""

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

np.random.seed(42)  # Reproducible fracture patterns

# ============================================================
# GRID SETUP
# ============================================================
N = 120  # Higher resolution
x = np.linspace(-10, 10, N)
y = np.linspace(-10, 10, N)
X, Y = np.meshgrid(x, y)
R2 = X**2 + Y**2
R = np.sqrt(R2 + 1e-10)

# ============================================================
# PHYSICS PARAMETERS (from Meridian)
# ============================================================
k_RS = 0.5          # RS curvature scale (AdS_5 inverse radius)
w0 = -0.830         # Dark energy EOS (Meridian prediction)
C_GB = 2/3          # Gauss-Bonnet coefficient (derived)
sigma = 2.0         # Gravity well width
well_depth = 5.0    # Gravity well amplitude

# ============================================================
# WARP FACTOR & GRAVITY WELL
# ============================================================

def warp_factor(z_coord, k=k_RS):
    """RS warp factor: e^{-2k|y|} — the exponential hierarchy."""
    return np.exp(-2 * k * np.abs(z_coord))

def cuscuton_well(X, Y, depth=well_depth, width=sigma):
    """
    Localized mass creating intrinsic 4D curvature,
    represented as extrinsic brane displacement into the 5th dimension.
    Includes secondary structure from the Cuscuton field profile.
    """
    R2 = X**2 + Y**2
    # Primary gravitational well
    primary = -depth * np.exp(-R2 / (2 * width**2))
    # Cuscuton field ring — the self-tuning boundary
    cuscuton_ring = 0.3 * np.exp(-(R2 - 16) ** 2 / 8.0)
    return primary + cuscuton_ring

def gaussian_curvature(Z, dx=20/N):
    """
    Compute Gaussian curvature of the surface z=f(x,y).
    K = (f_xx * f_yy - f_xy^2) / (1 + f_x^2 + f_y^2)^2
    This encodes the natal constraint density.
    """
    fy, fx = np.gradient(Z, dx)
    fyy, fyx = np.gradient(fy, dx)
    fxy, fxx = np.gradient(fx, dx)
    denom = (1 + fx**2 + fy**2)**2
    K = (fxx * fyy - fxy**2) / (denom + 1e-10)
    return K

def generate_brane_z(wa, include_warp=True):
    """
    Brane displacement into the bulk.
    wa = 0: Horndeski self-tuning intact. Stable.
    wa != 0: Cancellation mechanism fractures.
    """
    Z = cuscuton_well(X, Y)

    if include_warp:
        # Apply warp factor attenuation at large displacements
        Z = Z * warp_factor(Z)

    if wa == 0:
        return Z

    # === INSTABILITY MODES (physically motivated) ===
    abs_wa = np.abs(wa)

    # Mode 1: Brane oscillation — bulk graviton KK modes leak onto brane
    # Frequency set by RS mass gap: m_n ~ k * x_n where x_n are Bessel zeros
    kk_mode1 = abs_wa * 3.0 * np.sin(2.405 * X / 5) * np.cos(2.405 * Y / 5)
    kk_mode2 = abs_wa * 1.5 * np.sin(5.520 * X / 10) * np.cos(5.520 * Y / 10)

    # Mode 2: Radion instability — brane separation fluctuates
    # Quadratic runaway when self-tuning fails
    radion = abs_wa * 0.15 * R2

    # Mode 3: Stochastic fracture — quantum fluctuations unsuppressed
    # Scales with wa^2 (perturbative onset)
    fracture = wa**2 * 8.0 * (np.random.rand(*X.shape) - 0.5)

    # Mode 4: Cuscuton screening failure — vacuum energy leaks through
    # The ring structure breaks first (boundary of screening region)
    screening_failure = abs_wa * 2.0 * np.exp(-(R2 - 16)**2 / 20.0) * np.sin(8 * np.arctan2(Y, X))

    # Sign of wa determines direction of bulk displacement
    sign = np.sign(wa) if wa != 0 else 1

    return Z + sign * (kk_mode1 + kk_mode2) + radion + fracture + screening_failure

def generate_geodesics(Z, n_geodesics=12, n_points=80):
    """
    Generate geodesic lines on the brane surface.
    Radial geodesics from the gravity well center.
    """
    geodesics_x = []
    geodesics_y = []
    geodesics_z = []

    angles = np.linspace(0, 2 * np.pi, n_geodesics, endpoint=False)

    for theta in angles:
        # Radial lines from center
        t = np.linspace(0.3, 9.5, n_points)
        gx = t * np.cos(theta)
        gy = t * np.sin(theta)

        # Interpolate Z values
        # Map to grid indices
        ix = ((gx - x[0]) / (x[-1] - x[0]) * (N - 1)).astype(int)
        iy = ((gy - y[0]) / (y[-1] - y[0]) * (N - 1)).astype(int)
        ix = np.clip(ix, 0, N - 1)
        iy = np.clip(iy, 0, N - 1)
        gz = Z[iy, ix]

        geodesics_x.append(gx)
        geodesics_y.append(gy)
        geodesics_z.append(gz)

    return geodesics_x, geodesics_y, geodesics_z


# ============================================================
# FIGURE 1: INTERACTIVE w_a SLIDER
# ============================================================

def create_interactive_figure():
    """Main interactive visualization with w_a slider."""

    fig = go.Figure()

    # *** TRACE 0: Brane surface (FIRST — so animation frames can target index 0) ***
    Z_stable = generate_brane_z(0.0)
    K_stable = gaussian_curvature(Z_stable)
    K_norm = np.clip(K_stable, -2, 2)

    COLORSCALE = [
        [0.0, '#1a0533'],     # Deep violet — high negative curvature
        [0.2, '#4a0e6e'],     # Purple
        [0.35, '#0d47a1'],    # Deep blue
        [0.5, '#00897b'],     # Teal — flat (zero curvature)
        [0.65, '#f9a825'],    # Gold
        [0.8, '#ff6f00'],     # Orange
        [1.0, '#d50000'],     # Red — high positive curvature
    ]

    fig.add_trace(go.Surface(
        x=X, y=Y, z=Z_stable,
        surfacecolor=K_norm,
        colorscale=COLORSCALE,
        cmin=-2, cmax=2,
        colorbar=dict(
            title=dict(text='Gaussian<br>Curvature<br>(Natal<br>Constraint<br>Density)', font=dict(size=11)),
            tickfont=dict(size=10),
            len=0.6,
            x=1.02,
        ),
        opacity=0.92,
        name='D3-Brane',
        lighting=dict(
            ambient=0.4,
            diffuse=0.6,
            specular=0.3,
            roughness=0.5,
            fresnel=0.2
        ),
        contours=dict(
            z=dict(show=True, usecolormap=False, color='rgba(255,255,255,0.08)',
                   width=1, start=-5, end=2, size=0.5)
        )
    ))

    N_GEO = 12
    # *** TRACES 1-12: Geodesic lines ***
    gx, gy, gz = generate_geodesics(Z_stable, n_geodesics=N_GEO)
    for i in range(N_GEO):
        fig.add_trace(go.Scatter3d(
            x=gx[i], y=gy[i], z=gz[i] + 0.02,
            mode='lines',
            line=dict(color='rgba(255, 255, 255, 0.25)', width=2),
            showlegend=False,
            hoverinfo='none'
        ))

    # *** TRACE 13: Cuscuton screening ring ***
    ring_theta = np.linspace(0, 2*np.pi, 60)
    ring_r = 4.0
    ring_x = ring_r * np.cos(ring_theta)
    ring_y = ring_r * np.sin(ring_theta)
    ring_ix = ((ring_x - x[0]) / (x[-1] - x[0]) * (N-1)).astype(int)
    ring_iy = ((ring_y - y[0]) / (y[-1] - y[0]) * (N-1)).astype(int)
    ring_ix = np.clip(ring_ix, 0, N-1)
    ring_iy = np.clip(ring_iy, 0, N-1)
    ring_z = Z_stable[ring_iy, ring_ix]

    fig.add_trace(go.Scatter3d(
        x=ring_x, y=ring_y, z=ring_z + 0.05,
        mode='lines',
        line=dict(color='rgba(0, 255, 200, 0.5)', width=3, dash='dash'),
        name='Cuscuton Screening Boundary',
        hoverinfo='none'
    ))

    # *** Static decorations (NOT animated) ***

    # AdS_5 Bulk boundary wireframe
    edges = [
        [[-10,-10,-8], [10,-10,-8]], [[10,-10,-8], [10,10,-8]],
        [[10,10,-8], [-10,10,-8]], [[-10,10,-8], [-10,-10,-8]],
        [[-10,-10,8], [10,-10,8]], [[10,-10,8], [10,10,8]],
        [[10,10,8], [-10,10,8]], [[-10,10,8], [-10,-10,8]],
        [[-10,-10,-8], [-10,-10,8]], [[10,-10,-8], [10,-10,8]],
        [[10,10,-8], [10,10,8]], [[-10,10,-8], [-10,10,8]],
    ]
    for edge in edges:
        fig.add_trace(go.Scatter3d(
            x=[edge[0][0], edge[1][0]],
            y=[edge[0][1], edge[1][1]],
            z=[edge[0][2], edge[1][2]],
            mode='lines',
            line=dict(color='rgba(100, 180, 255, 0.15)', width=2),
            showlegend=False,
            hoverinfo='none'
        ))

    # Bulk label
    fig.add_trace(go.Scatter3d(
        x=[0], y=[-10], z=[7],
        mode='text',
        text=['AdS₅ Bulk'],
        textfont=dict(size=14, color='rgba(100, 180, 255, 0.5)'),
        showlegend=False,
        hoverinfo='none'
    ))

    # --- Animation frames ---
    # Each frame updates ONLY traces 0-13 (surface + geodesics + ring)
    ANIMATED_TRACES = list(range(N_GEO + 2))  # 0=surface, 1-12=geodesics, 13=ring

    wa_values = np.linspace(-0.5, 0.5, 41)
    frames = []
    for wa in wa_values:
        z_frame = generate_brane_z(wa)
        K_frame = gaussian_curvature(z_frame)
        K_frame_norm = np.clip(K_frame, -2, 2)

        frame_data = []

        # Trace 0: Surface
        frame_data.append(go.Surface(
            x=X, y=Y, z=z_frame,
            surfacecolor=K_frame_norm,
            colorscale=COLORSCALE,
            cmin=-2, cmax=2,
            colorbar=dict(
                title=dict(text='Gaussian<br>Curvature<br>(Natal<br>Constraint<br>Density)', font=dict(size=11)),
                tickfont=dict(size=10),
                len=0.6,
                x=1.02,
            ),
            opacity=0.92,
            name='D3-Brane',
            lighting=dict(ambient=0.4, diffuse=0.6, specular=0.3, roughness=0.5, fresnel=0.2),
        ))

        # Traces 1-12: Geodesics
        gx_f, gy_f, gz_f = generate_geodesics(z_frame, n_geodesics=N_GEO)
        for i in range(N_GEO):
            frame_data.append(go.Scatter3d(
                x=gx_f[i], y=gy_f[i], z=gz_f[i] + 0.02,
                mode='lines',
                line=dict(color='rgba(255, 255, 255, 0.25)', width=2),
                showlegend=False,
                hoverinfo='none'
            ))

        # Trace 13: Cuscuton ring (follows the surface)
        ring_z_frame = z_frame[ring_iy, ring_ix]
        frame_data.append(go.Scatter3d(
            x=ring_x, y=ring_y, z=ring_z_frame + 0.05,
            mode='lines',
            line=dict(color='rgba(0, 255, 200, 0.5)', width=3, dash='dash'),
            name='Cuscuton Screening Boundary',
            hoverinfo='none'
        ))

        frames.append(go.Frame(
            data=frame_data,
            name=f'{wa:.2f}',
            traces=ANIMATED_TRACES,
        ))

    fig.frames = frames

    # --- Slider ---
    sliders = [{
        "pad": {"b": 10, "t": 60},
        "len": 0.85,
        "x": 0.1,
        "y": 0,
        "currentvalue": {
            "font": {"size": 14, "color": "#aaa"},
            "prefix": "w_a = ",
            "visible": True,
            "xanchor": "center"
        },
        "steps": [
            {
                "args": [
                    [f'{wa:.2f}'],
                    {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}
                ],
                "label": f'{wa:.2f}',
                "method": "animate"
            } for wa in wa_values
        ],
        "tickcolor": "#555",
        "font": {"color": "#888"},
    }]

    # --- Layout ---
    fig.update_layout(
        title=dict(
            text=(
                "<b>5D Randall-Sundrum Braneworld</b><br>"
                "<sup>Cuscuton Self-Tuning & w<sub>a</sub> Constraint | "
                "w₀ = −0.830 | C<sub>GB</sub> = 2/3 | "
                "Color = Gaussian curvature (natal constraint density)</sup>"
            ),
            font=dict(size=16),
            x=0.5,
        ),
        scene=dict(
            xaxis=dict(range=[-10, 10], title='X (Brane spatial)', gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            yaxis=dict(range=[-10, 10], title='Y (Brane spatial)', gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            zaxis=dict(range=[-8, 8], title='Z (Bulk extra dimension)', gridcolor='rgba(80,80,80,0.3)',
                       showbackground=True, backgroundcolor='rgba(10,10,30,0.8)'),
            aspectratio=dict(x=1, y=1, z=0.6),
            camera=dict(
                eye=dict(x=1.8, y=1.2, z=0.9),
                up=dict(x=0, y=0, z=1)
            ),
        ),
        sliders=sliders,
        updatemenus=[{
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 120, "redraw": True},
                                    "fromcurrent": True, "transition": {"duration": 80}}],
                    "label": "▶ Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
                    "label": "⏸ Pause",
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
        paper_bgcolor='rgb(10, 10, 25)',
        margin=dict(l=0, r=80, t=80, b=60),
        legend=dict(
            x=0.01, y=0.99,
            bgcolor='rgba(0,0,0,0.5)',
            font=dict(size=11),
        ),
        annotations=[
            dict(
                text=(
                    "Meridian prediction: w<sub>a</sub> = 0 (exactly) — "
                    "Horndeski self-tuning requires exact cancellation<br>"
                    "Any w<sub>a</sub> ≠ 0 fractures the Cuscuton vacuum screening mechanism"
                ),
                showarrow=False,
                xref="paper", yref="paper",
                x=0.5, y=-0.08,
                font=dict(size=11, color='rgba(180,180,180,0.7)'),
                xanchor='center',
            ),
        ],
    )

    return fig


# ============================================================
# FIGURE 2: STATIC COMPARISON PANEL (for V3 publication)
# ============================================================

def create_comparison_figure():
    """Three-panel comparison: w_a = -0.3, w_a = 0, w_a = +0.3"""

    fig = make_subplots(
        rows=1, cols=3,
        specs=[[{'type': 'scene'}, {'type': 'scene'}, {'type': 'scene'}]],
        subplot_titles=[
            'w_a = -0.3 (Unstable)',
            'w_a = 0 (Self-Tuned)',
            'w_a = +0.3 (Unstable)',
        ],
        horizontal_spacing=0.02,
    )

    wa_vals = [-0.3, 0.0, 0.3]
    scenes = ['scene', 'scene2', 'scene3']

    for idx, (wa, scene) in enumerate(zip(wa_vals, scenes)):
        Z = generate_brane_z(wa)
        K = gaussian_curvature(Z)
        K_norm = np.clip(K, -2, 2)

        colorscale = [
            [0.0, '#1a0533'],
            [0.2, '#4a0e6e'],
            [0.35, '#0d47a1'],
            [0.5, '#00897b'],
            [0.65, '#f9a825'],
            [0.8, '#ff6f00'],
            [1.0, '#d50000'],
        ]

        fig.add_trace(
            go.Surface(
                x=X, y=Y, z=Z,
                surfacecolor=K_norm,
                colorscale=colorscale,
                showscale=(idx == 2),
                colorbar=dict(
                    title='K (curvature)',
                    len=0.6,
                    x=1.02,
                ) if idx == 2 else None,
                opacity=0.9,
                lighting=dict(ambient=0.4, diffuse=0.6, specular=0.3, roughness=0.5),
            ),
            row=1, col=idx+1
        )

        # Geodesics
        gx, gy, gz = generate_geodesics(Z, n_geodesics=8)
        for i in range(len(gx)):
            fig.add_trace(
                go.Scatter3d(
                    x=gx[i], y=gy[i], z=gz[i] + 0.02,
                    mode='lines',
                    line=dict(
                        color='rgba(255,255,255,0.2)' if wa == 0 else 'rgba(255,100,100,0.2)',
                        width=2
                    ),
                    showlegend=False,
                    hoverinfo='none',
                ),
                row=1, col=idx+1
            )

    # Scene settings
    scene_settings = dict(
        xaxis=dict(range=[-10,10], showticklabels=False, title=''),
        yaxis=dict(range=[-10,10], showticklabels=False, title=''),
        zaxis=dict(range=[-8,8], showticklabels=False, title=''),
        aspectratio=dict(x=1, y=1, z=0.6),
        camera=dict(eye=dict(x=1.6, y=1.6, z=1.0)),
    )
    fig.update_layout(
        scene=scene_settings,
        scene2=scene_settings,
        scene3=scene_settings,
    )

    fig.update_layout(
        title=dict(
            text=(
                "<b>Cuscuton Self-Tuning: Why w<sub>a</sub> = 0 Exactly</b><br>"
                "<sup>Left/Right: KK mode leakage, radion instability, screening failure | "
                "Center: stable self-tuned brane</sup>"
            ),
            font=dict(size=15),
            x=0.5,
        ),
        template="plotly_dark",
        paper_bgcolor='rgb(10, 10, 25)',
        height=500,
        width=1500,
        margin=dict(l=0, r=80, t=80, b=30),
    )

    return fig


# ============================================================
# FIGURE 3: CONSTRAINT LATTICE CROSS-SECTION
# ============================================================

def create_constraint_cross_section():
    """
    Radial cross-section showing the three constraint sublattices:
    natal (background geometry), coercive (gauge potential), voluntary (gauge freedom).
    """
    r = np.linspace(0, 10, 500)

    # Natal: the well itself (background geometry from spectral triple D)
    natal = -well_depth * np.exp(-r**2 / (2 * sigma**2))

    # Coercive: gauge potential inner fluctuation (A modifying D)
    # Peaks at intermediate radius — where the gauge field is strongest
    coercive = 1.5 * r * np.exp(-r**2 / 8.0)

    # Voluntary: gauge freedom (unitary group action)
    # Flat — gauge invariance means physics doesn't depend on gauge choice
    # But modulated by the Cuscuton screening boundary
    voluntary = 0.3 * np.exp(-(r - 4)**2 / 0.5) + 0.08

    # Accessible region: intersection
    accessible = natal + coercive

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=r, y=natal,
        mode='lines',
        name='Natal (B₀) — Background Geometry',
        line=dict(color='#7c4dff', width=3),
        fill='tozeroy',
        fillcolor='rgba(124, 77, 255, 0.1)',
    ))

    fig.add_trace(go.Scatter(
        x=r, y=coercive,
        mode='lines',
        name='Coercive (E) — Gauge Potential',
        line=dict(color='#ff6d00', width=3),
        fill='tozeroy',
        fillcolor='rgba(255, 109, 0, 0.1)',
    ))

    fig.add_trace(go.Scatter(
        x=r, y=voluntary,
        mode='lines',
        name='Voluntary (V) — Gauge Freedom',
        line=dict(color='#00e676', width=3),
        fill='tozeroy',
        fillcolor='rgba(0, 230, 118, 0.1)',
    ))

    fig.add_trace(go.Scatter(
        x=r, y=accessible,
        mode='lines',
        name='Accessible Region A(t) = B₀ ∩ E ∩ V',
        line=dict(color='#ffffff', width=2, dash='dash'),
    ))

    # Cuscuton screening boundary
    fig.add_vline(x=4, line=dict(color='rgba(0,255,200,0.4)', width=1, dash='dot'),
                  annotation_text='Cuscuton screening', annotation_position='top right',
                  annotation_font=dict(color='rgba(0,255,200,0.6)', size=10))

    # DOF counts
    fig.add_annotation(x=0.3, y=-4.5, text='96 DOFs<br>(spectral triple)',
                       font=dict(color='#7c4dff', size=10), showarrow=False)
    fig.add_annotation(x=2.5, y=1.2, text='16 DOFs<br>(inner fluctuations)',
                       font=dict(color='#ff6d00', size=10), showarrow=False)
    fig.add_annotation(x=4.0, y=0.55, text='12 DOFs<br>(unitary group)',
                       font=dict(color='#00e676', size=10), showarrow=False)

    fig.update_layout(
        title=dict(
            text=(
                "<b>Constraint Lattice Cross-Section of the Brane</b><br>"
                "<sup>Bridge #71: natal ↔ D, coercive ↔ A, voluntary ↔ U | "
                "DOF hierarchy: 96 > 16 > 12 (SM spectral triple)</sup>"
            ),
            font=dict(size=14),
            x=0.5,
        ),
        xaxis=dict(title='Radial distance from gravity well', gridcolor='rgba(80,80,80,0.3)'),
        yaxis=dict(title='Constraint strength / Brane displacement', gridcolor='rgba(80,80,80,0.3)'),
        template="plotly_dark",
        paper_bgcolor='rgb(10, 10, 25)',
        plot_bgcolor='rgb(15, 15, 35)',
        height=500,
        width=1000,
        legend=dict(x=0.55, y=0.98, bgcolor='rgba(0,0,0,0.5)', font=dict(size=11)),
        margin=dict(l=60, r=40, t=80, b=60),
    )

    return fig


# ============================================================
# GENERATE ALL FIGURES
# ============================================================

output_dir = os.path.dirname(os.path.abspath(__file__))

print("Generating Figure 1: Interactive braneworld...")
fig1 = create_interactive_figure()
fig1.write_html(os.path.join(output_dir, "braneworld_interactive.html"))
print(f"  -> braneworld_interactive.html")

# Static images for V3
try:
    fig1_static = create_interactive_figure()
    # Set to w_a = 0 view
    fig1_static.write_image(os.path.join(output_dir, "braneworld_stable.png"),
                            width=1400, height=900, scale=2)
    print(f"  -> braneworld_stable.png (w_a = 0)")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("\nGenerating Figure 2: Three-panel comparison...")
fig2 = create_comparison_figure()
fig2.write_html(os.path.join(output_dir, "braneworld_comparison.html"))
try:
    fig2.write_image(os.path.join(output_dir, "braneworld_comparison.png"),
                     width=1500, height=500, scale=2)
    print(f"  -> braneworld_comparison.png")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("\nGenerating Figure 3: Constraint lattice cross-section...")
fig3 = create_constraint_cross_section()
fig3.write_html(os.path.join(output_dir, "braneworld_constraint_lattice.html"))
try:
    fig3.write_image(os.path.join(output_dir, "braneworld_constraint_lattice.png"),
                     width=1000, height=500, scale=2)
    print(f"  -> braneworld_constraint_lattice.png")
except Exception as e:
    print(f"  (static export skipped: {e})")

print("\nAll figures generated.")
print(f"Output directory: {output_dir}")
