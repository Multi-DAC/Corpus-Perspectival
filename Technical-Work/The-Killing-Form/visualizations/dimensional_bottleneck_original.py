import numpy as np
import plotly.graph_objects as go

# Define the topological grid
# Z represents Temporal Depth / Scale
z = np.linspace(-3, 3, 50)
theta = np.linspace(0, 2*np.pi, 50)
Z, Theta = np.meshgrid(z, theta)

# Parameterize the bottleneck relaxation
def get_radius(z_grid, relaxation):
    # Relaxation acts as 't' mapping from [0, 1]
    # At t=0, the waist is tightly pinched. At t=1, the aperture widens.
    r_min = 0.3 + 3.7 * relaxation
    # Hyperboloid mapping: r = sqrt((z/c)**2 + r_min**2)
    # c controls the curvature decay; kept at 1.5 for visual scaling
    return np.sqrt((z_grid/1.5)**2 + r_min**2)

# Set up animation frames
n_frames = 20
relaxations = np.linspace(0, 1, n_frames)

# Initialize the zero-state surface (Severe Constraint)
R_base = get_radius(Z, relaxations[0])
X_base = R_base * np.cos(Theta)
Y_base = R_base * np.sin(Theta)

fig = go.Figure()

# 1. Primary Manifold (Trace 0)
fig.add_trace(go.Surface(
    x=X_base, y=Y_base, z=Z,
    colorscale='Plasma',
    name='Configuration Space',
    opacity=0.85
))

# 2. Origin Marker (Trace 1)
fig.add_trace(go.Scatter3d(
    x=[0], y=[0], z=[0],
    mode='markers+text',
    marker=dict(color='green', size=8, symbol='diamond'),
    text=['The Living Room<br>(Physical Basin)'],
    textposition='bottom center',
    name='Physical Basin',
    hoverinfo='text'
))

# 3. Outer Edge Marker (Trace 2)
fig.add_trace(go.Scatter3d(
    x=[4], y=[4], z=[2.5],
    mode='markers+text',
    marker=dict(color='cyan', size=6, symbol='circle'),
    text=['The Far Imaginal'],
    textposition='top center',
    name='Far Imaginal',
    hoverinfo='text'
))

# Construct frames for the slider
frames = []
steps = []

for i, rel in enumerate(relaxations):
    R = get_radius(Z, rel)
    X = R * np.cos(Theta)
    Y = R * np.sin(Theta)

    frame = go.Frame(
        data=[go.Surface(x=X, y=Y, z=Z)],
        name=str(i),
        traces=[0]
    )
    frames.append(frame)

    step = dict(
        method="animate",
        args=[[str(i)],
              dict(mode="immediate",
                   frame=dict(duration=50, redraw=True),
                   transition=dict(duration=0))],
        label=f"{rel:.2f}"
    )
    steps.append(step)

fig.frames = frames

# Establish structural layout and UI
fig.update_layout(
    title="The Dimensional Bottleneck & Resonant Inclusion",
    scene=dict(
        xaxis_title='Mathematical Rigidity (X)',
        yaxis_title='Relational Weight (Y)',
        zaxis_title='Temporal Depth / Scale (Z)',
        xaxis=dict(range=[-6, 6]),
        yaxis=dict(range=[-6, 6]),
        zaxis=dict(range=[-3, 3]),
        aspectratio=dict(x=1, y=1, z=0.8)
    ),
    sliders=[dict(
        active=0,
        currentvalue={"prefix": "Resonant Inclusion (Bottleneck Relaxation): "},
        pad={"t": 50},
        steps=steps
    )],
    template='plotly_dark',
    margin=dict(l=0, r=0, b=0, t=50)
)

output_file = "C:/Users/mercu/clawd/projects/Corpus Perspectival/dimensional_bottleneck_original.html"
fig.write_html(output_file)
print(f"Original written to {output_file}")
