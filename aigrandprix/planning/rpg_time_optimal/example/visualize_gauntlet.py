"""
Visualize the 45-Gate Gauntlet — Time-Optimal Trajectory
34.79 seconds of optimized aggression through 338.8m of chaos.
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from mpl_toolkits.mplot3d.art3d import Line3DCollection
import matplotlib.gridspec as gridspec
import yaml
import os

# Load data
script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, 'gauntlet_result.csv'))
track_path = os.path.join(script_dir, '..', 'tracks', 'gauntlet.yaml')

with open(track_path, 'r') as f:
    track = yaml.safe_load(f)

gates = np.array(track['gates'])
init_pos = np.array(track['initial']['position'])

# Extract trajectory data
t = df['t'].values
x = df['p_x'].values
y = df['p_y'].values
z = df['p_z'].values
vx = df['v_x'].values
vy = df['v_y'].values
vz = df['v_z'].values
speed = np.sqrt(vx**2 + vy**2 + vz**2)

# Motor thrusts
u1 = df['u_1'].values
u2 = df['u_2'].values
u3 = df['u_3'].values
u4 = df['u_4'].values
total_thrust = u1 + u2 + u3 + u4

print(f"Total time: {t[-1]:.2f}s")
print(f"Peak speed: {speed.max():.2f} m/s ({speed.max()*3.6:.1f} km/h)")
print(f"Average speed: {speed.mean():.2f} m/s ({speed.mean()*3.6:.1f} km/h)")
print(f"Course distance: {np.sum(np.sqrt(np.diff(x)**2 + np.diff(y)**2 + np.diff(z)**2)):.1f}m")
print(f"Altitude range: {z.min():.1f}m to {z.max():.1f}m")
print(f"Peak total thrust: {total_thrust.max():.1f}N")

# Color map based on speed
norm = plt.Normalize(speed.min(), speed.max())
cmap = plt.cm.plasma

# ============================================================
# Figure 1: 4-panel overview
# ============================================================
fig = plt.figure(figsize=(18, 14))
fig.suptitle("THE GAUNTLET — 45 Gates in 34.79s", fontsize=20, fontweight='bold', y=0.98)
fig.text(0.5, 0.955, "338.8m • Peak: {:.0f} km/h • Avg: {:.0f} km/h • Vertical loops to z=20m".format(
    speed.max()*3.6, speed.mean()*3.6), ha='center', fontsize=12, color='gray')

gs = gridspec.GridSpec(2, 2, hspace=0.3, wspace=0.3)

# --- Panel 1: 3D Trajectory ---
ax1 = fig.add_subplot(gs[0, 0], projection='3d')

# Plot trajectory as colored segments
points = np.array([x, y, z]).T.reshape(-1, 1, 3)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc3d = Line3DCollection(segments, cmap=cmap, norm=norm, linewidth=1.5, alpha=0.9)
lc3d.set_array(speed[:-1])
ax1.add_collection3d(lc3d)

# Plot gates
ax1.scatter(gates[:, 0], gates[:, 1], gates[:, 2], c='red', s=25, marker='s', alpha=0.7, zorder=5, label='Gates')
ax1.scatter([init_pos[0]], [init_pos[1]], [init_pos[2]], c='lime', s=80, marker='*', zorder=10, label='Start')

# Labels
ax1.set_xlabel('X (m)', fontsize=9)
ax1.set_ylabel('Y (m)', fontsize=9)
ax1.set_zlabel('Z (m)', fontsize=9)
ax1.set_title('3D Trajectory', fontsize=13, fontweight='bold')
ax1.legend(fontsize=8, loc='upper left')

# Set limits with padding
pad = 3
ax1.set_xlim(min(x.min(), gates[:,0].min()) - pad, max(x.max(), gates[:,0].max()) + pad)
ax1.set_ylim(min(y.min(), gates[:,1].min()) - pad, max(y.max(), gates[:,1].max()) + pad)
ax1.set_zlim(min(z.min(), gates[:,2].min()) - pad, max(z.max(), gates[:,2].max()) + pad)
ax1.view_init(elev=25, azim=-60)

# --- Panel 2: Top-down (XY) view ---
ax2 = fig.add_subplot(gs[0, 1])

points_xy = np.array([x, y]).T.reshape(-1, 1, 2)
segments_xy = np.concatenate([points_xy[:-1], points_xy[1:]], axis=1)
lc_xy = LineCollection(segments_xy, cmap=cmap, norm=norm, linewidth=2)
lc_xy.set_array(speed[:-1])
ax2.add_collection(lc_xy)

# Gate markers with numbers
for i, g in enumerate(gates):
    ax2.plot(g[0], g[1], 's', color='red', markersize=4, alpha=0.6)
    if i % 5 == 0:  # Label every 5th gate
        ax2.annotate(f'{i+1}', (g[0], g[1]), fontsize=6, color='darkred',
                    ha='center', va='bottom', xytext=(0, 3), textcoords='offset points')

ax2.plot(init_pos[0], init_pos[1], '*', color='lime', markersize=12, zorder=10)
ax2.set_xlabel('X (m)', fontsize=10)
ax2.set_ylabel('Y (m)', fontsize=10)
ax2.set_title('Top-Down View (XY)', fontsize=13, fontweight='bold')
ax2.set_aspect('equal')
ax2.grid(True, alpha=0.3)
ax2.autoscale()
cb = plt.colorbar(lc_xy, ax=ax2, shrink=0.8, label='Speed (m/s)')

# --- Panel 3: Speed Profile ---
ax3 = fig.add_subplot(gs[1, 0])

# Color the speed line by value
points_speed = np.array([t, speed]).T.reshape(-1, 1, 2)
segments_speed = np.concatenate([points_speed[:-1], points_speed[1:]], axis=1)
lc_speed = LineCollection(segments_speed, cmap=cmap, norm=norm, linewidth=2)
lc_speed.set_array(speed[:-1])
ax3.add_collection(lc_speed)

ax3.set_xlim(t.min(), t.max())
ax3.set_ylim(0, speed.max() * 1.1)
ax3.axhline(y=speed.mean(), color='white', alpha=0.5, linestyle='--', linewidth=1)
ax3.text(t.max()*0.98, speed.mean()+0.5, f'avg {speed.mean():.1f} m/s', ha='right', fontsize=8, color='gray')

# Mark gate passages (approximate — find closest trajectory point to each gate)
for i, g in enumerate(gates):
    dists = np.sqrt((x - g[0])**2 + (y - g[1])**2 + (z - g[2])**2)
    gate_idx = np.argmin(dists)
    if i % 5 == 0:
        ax3.axvline(x=t[gate_idx], color='red', alpha=0.15, linewidth=0.5)

ax3.set_xlabel('Time (s)', fontsize=10)
ax3.set_ylabel('Speed (m/s)', fontsize=10)
ax3.set_title('Speed Profile', fontsize=13, fontweight='bold')
ax3.grid(True, alpha=0.3)

# --- Panel 4: Altitude Profile ---
ax4 = fig.add_subplot(gs[1, 1])

points_alt = np.array([t, z]).T.reshape(-1, 1, 2)
segments_alt = np.concatenate([points_alt[:-1], points_alt[1:]], axis=1)
lc_alt = LineCollection(segments_alt, cmap=cmap, norm=norm, linewidth=2)
lc_alt.set_array(speed[:-1])
ax4.add_collection(lc_alt)

ax4.set_xlim(t.min(), t.max())
ax4.set_ylim(z.min() - 1, z.max() + 1)

# Mark gate altitudes
for i, g in enumerate(gates):
    dists = np.sqrt((x - g[0])**2 + (y - g[1])**2 + (z - g[2])**2)
    gate_idx = np.argmin(dists)
    ax4.plot(t[gate_idx], g[2], 's', color='red', markersize=3, alpha=0.4)

ax4.set_xlabel('Time (s)', fontsize=10)
ax4.set_ylabel('Altitude (m)', fontsize=10)
ax4.set_title('Altitude Profile', fontsize=13, fontweight='bold')
ax4.grid(True, alpha=0.3)

# Style
for ax in [ax3, ax4]:
    ax.set_facecolor('#1a1a2e')
fig.patch.set_facecolor('#0d0d1a')
for ax in [ax2]:
    ax.set_facecolor('#1a1a2e')
ax1.set_facecolor('#1a1a2e')
ax1.xaxis.pane.fill = False
ax1.yaxis.pane.fill = False
ax1.zaxis.pane.fill = False

# Text colors
for ax in [ax1, ax2, ax3, ax4]:
    ax.title.set_color('white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(colors='white')
    if hasattr(ax, 'zaxis'):
        ax.zaxis.label.set_color('white')
        ax.tick_params(axis='z', colors='white')
fig.suptitle("THE GAUNTLET — 45 Gates in 34.79s", fontsize=20, fontweight='bold', y=0.98, color='white')
fig.texts[1].set_color('#aaaaaa')

output_path = os.path.join(script_dir, 'gauntlet_visualization.png')
fig.savefig(output_path, dpi=150, bbox_inches='tight', facecolor=fig.get_facecolor())
print(f"\nSaved to {output_path}")

# ============================================================
# Figure 2: Side view (XZ) — shows the vertical drama
# ============================================================
fig2, ax_xz = plt.subplots(figsize=(16, 6))
fig2.patch.set_facecolor('#0d0d1a')
ax_xz.set_facecolor('#1a1a2e')

points_xz = np.array([x, z]).T.reshape(-1, 1, 2)
segments_xz = np.concatenate([points_xz[:-1], points_xz[1:]], axis=1)
lc_xz = LineCollection(segments_xz, cmap=cmap, norm=norm, linewidth=2.5)
lc_xz.set_array(speed[:-1])
ax_xz.add_collection(lc_xz)

for i, g in enumerate(gates):
    ax_xz.plot(g[0], g[2], 's', color='red', markersize=6, alpha=0.7)
    ax_xz.annotate(f'{i+1}', (g[0], g[2]), fontsize=7, color='#ff6666',
                  ha='center', va='bottom', xytext=(0, 4), textcoords='offset points')

ax_xz.plot(init_pos[0], init_pos[2], '*', color='lime', markersize=15, zorder=10)
ax_xz.set_xlabel('X (m)', fontsize=12, color='white')
ax_xz.set_ylabel('Z / Altitude (m)', fontsize=12, color='white')
ax_xz.set_title('THE GAUNTLET — Side View (XZ): Vertical Loops & Dives', fontsize=16, fontweight='bold', color='white')
ax_xz.tick_params(colors='white')
ax_xz.grid(True, alpha=0.2)
ax_xz.set_aspect('equal')
ax_xz.autoscale()
cb2 = plt.colorbar(lc_xz, ax=ax_xz, shrink=0.8, label='Speed (m/s)')
cb2.ax.yaxis.label.set_color('white')
cb2.ax.tick_params(colors='white')

output2 = os.path.join(script_dir, 'gauntlet_sideview.png')
fig2.savefig(output2, dpi=150, bbox_inches='tight', facecolor=fig2.get_facecolor())
print(f"Saved side view to {output2}")

plt.close('all')
print("\nDone! 🦞")
