"""
Figure-8 coil winding diagram + parameter computation for Phase 1 EM platform.
Wire: 24 AWG enamelled magnet wire (EMTEL).
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# ============ Physical parameters ============
WIRE_AWG = 24
WIRE_DIAMETER_MM = 0.511
WIRE_DCR_OHM_PER_M = 0.0842
WIRE_AMPACITY_A = 3.5

# ============ DESIGN POINT ============
N_TURNS_PER_LOOP = 50
LOOP_RADIUS_MM = 35
SUPPLY_V = 12.0
SERIES_R_OHM = 6.0

# ============ Derived ============
loop_radius_m = LOOP_RADIUS_MM / 1000.0
length_per_turn_m = (np.pi + 2) * loop_radius_m
total_wire_length_m = 2 * N_TURNS_PER_LOOP * length_per_turn_m
coil_dcr = total_wire_length_m * WIRE_DCR_OHM_PER_M
total_circuit_R = coil_dcr + SERIES_R_OHM
peak_current_A = SUPPLY_V / total_circuit_R

mu0 = 4 * np.pi * 1e-7
a_wire_m = WIRE_DIAMETER_MM / 2 / 1000
L_single_H = mu0 * N_TURNS_PER_LOOP**2 * loop_radius_m * (np.log(8 * loop_radius_m / a_wire_m) - 2)
L_total_H = 2 * L_single_H
B_center_single_T = mu0 * N_TURNS_PER_LOOP * peak_current_A / (2 * loop_radius_m)
B_center_figure8_T = 2 * B_center_single_T

def Xl(f_Hz, L_H):
    return 2 * np.pi * f_Hz * L_H

# ============ DIAGRAM ============
fig = plt.figure(figsize=(15, 9))
gs = fig.add_gridspec(2, 2, height_ratios=[1.5, 1])

# --- TOP: WINDING SCHEMATIC ---
ax1 = fig.add_subplot(gs[0, :])
ax1.set_xlim(-10, 10)
ax1.set_ylim(-5.5, 5.5)
ax1.set_aspect('equal')
ax1.set_title('Figure-8 Coil — Top View Showing Single-Wire Winding Path\n' +
              '(Both D-loops wound from the same continuous wire; opposite rotation directions)',
              fontsize=12, fontweight='bold')

def draw_d_spiral(ax, center_x, n_turns_visible, opens_right, color):
    R_outer = 3.0
    R_inner = 0.5
    for i in range(n_turns_visible):
        r = R_inner + (R_outer - R_inner) * i / n_turns_visible
        if opens_right:
            theta = np.linspace(np.pi/2, 3*np.pi/2, 80)
        else:
            theta = np.linspace(-np.pi/2, np.pi/2, 80)
        x = center_x + r * np.cos(theta)
        y = r * np.sin(theta)
        ax.plot(x, y, color=color, lw=1.2, alpha=0.7)
        ax.plot([center_x, center_x], [-r, r], color=color, lw=1.2, alpha=0.7)

draw_d_spiral(ax1, -3.5, 8, opens_right=True,  color='#1f77b4')
draw_d_spiral(ax1, 3.5,  8, opens_right=False, color='#d62728')

# Current direction labels with arrows
ax1.annotate('', xy=(-5.5, 2.5), xytext=(-3, 2.5),
             arrowprops=dict(arrowstyle='->', color='#1f77b4', lw=3))
ax1.text(-4.5, 3.2, 'CCW', fontsize=12, color='#1f77b4', fontweight='bold', ha='center')
ax1.annotate('', xy=(-3, -2.5), xytext=(-5.5, -2.5),
             arrowprops=dict(arrowstyle='->', color='#1f77b4', lw=3))

ax1.annotate('', xy=(5.5, 2.5), xytext=(3, 2.5),
             arrowprops=dict(arrowstyle='->', color='#d62728', lw=3))
ax1.text(4.5, 3.2, 'CW', fontsize=12, color='#d62728', fontweight='bold', ha='center')
ax1.annotate('', xy=(3, -2.5), xytext=(5.5, -2.5),
             arrowprops=dict(arrowstyle='->', color='#d62728', lw=3))

# Crossover indicator
ax1.plot([0, 0], [0, 4.2], color='black', lw=2, linestyle='--', alpha=0.6)
ax1.annotate('CROSSOVER\n(wire jumps from inner-left\nto inner-right for opposite winding)',
             xy=(0, 4.0), xytext=(0, 4.7),
             ha='center', fontsize=9, color='black',
             arrowprops=dict(arrowstyle='-', color='black', lw=0.8))

# Start and End leads
ax1.plot([-3.5, -3.5], [-3.2, -4.7], color='#1f77b4', lw=2)
ax1.text(-3.5, -5.0, 'START', ha='center', fontsize=10, color='#1f77b4', fontweight='bold')
ax1.plot([3.5, 3.5], [-3.2, -4.7], color='#d62728', lw=2)
ax1.text(3.5, -5.0, 'END', ha='center', fontsize=10, color='#d62728', fontweight='bold')

# Focal point
ax1.plot(0, 0, marker='*', color='black', markersize=22)
ax1.text(0, -1.0, 'FOCAL POINT\n(peak B-field)', ha='center', fontsize=9, fontweight='bold')

ax1.axis('off')

# --- BOTTOM-LEFT: SIDE VIEW ---
ax2 = fig.add_subplot(gs[1, 0])
ax2.set_xlim(-6, 6)
ax2.set_ylim(-3, 4)
ax2.set_aspect('equal')
ax2.set_title('Side View — Field Lines\n(opposing currents -> focal field at center)', fontsize=10)

ax2.add_patch(Rectangle((-3.5, -0.3), 0.6, 0.6, facecolor='#1f77b4', edgecolor='black'))
ax2.text(-3.2, 0, 'OUT', fontsize=8, ha='center', va='center', color='white', fontweight='bold')
ax2.add_patch(Rectangle((2.9, -0.3), 0.6, 0.6, facecolor='#d62728', edgecolor='black'))
ax2.text(3.2, 0, 'IN', fontsize=8, ha='center', va='center', color='white', fontweight='bold')

theta = np.linspace(0, 2*np.pi, 100)
for r in [1.0, 1.8, 2.5]:
    x = -3.2 + r * np.cos(theta); y = r * np.sin(theta)
    ax2.plot(x, y, color='#1f77b4', lw=0.8, alpha=0.4)
    x = 3.2 + r * np.cos(theta); y = r * np.sin(theta)
    ax2.plot(x, y, color='#d62728', lw=0.8, alpha=0.4)

ax2.annotate('', xy=(0, 1.5), xytext=(0, -0.5),
             arrowprops=dict(arrowstyle='->', color='black', lw=4))
ax2.text(0.4, 0.6, 'B_net', fontsize=11, fontweight='bold')
ax2.text(0, -2.4, 'Fields ADD at center -> focal peak\nFields OPPOSE at periphery -> cancellation',
         ha='center', fontsize=9, style='italic')
ax2.axis('off')

# --- BOTTOM-RIGHT: PARAMETERS ---
ax3 = fig.add_subplot(gs[1, 1])
ax3.axis('off')
ax3.set_title('Computed Parameters (24 AWG, this design point)', fontsize=10, fontweight='bold')

text = (
    "WIRE:        24 AWG, dia {:.3f} mm bare copper\n".format(WIRE_DIAMETER_MM) +
    "GEOMETRY:    {} turns per D-loop, R = {} mm\n".format(N_TURNS_PER_LOOP, LOOP_RADIUS_MM) +
    "TOTAL WIRE:  {:.1f} m\n\n".format(total_wire_length_m) +
    "ELECTRICAL\n" +
    "  Coil DCR:        {:.2f} ohm\n".format(coil_dcr) +
    "  Series limiter:  {:.1f} ohm  (50W power resistor)\n".format(SERIES_R_OHM) +
    "  Total R:         {:.2f} ohm\n".format(total_circuit_R) +
    "  Peak current:    {:.2f} A   (at {}V supply)\n".format(peak_current_A, SUPPLY_V) +
    "  Coil power:      {:.2f} W\n".format(peak_current_A**2 * coil_dcr) +
    "  Resistor power:  {:.2f} W (well under 50W rating)\n\n".format(peak_current_A**2 * SERIES_R_OHM) +
    "INDUCTANCE & REACTANCE\n" +
    "  L (figure-8):    {:.0f} uH\n".format(L_total_H*1e6) +
    "  XL @   4 Hz:     {:.2f} mohm  (negligible)\n".format(Xl(4, L_total_H)*1000) +
    "  XL @ 100 Hz:     {:.1f} mohm\n".format(Xl(100, L_total_H)*1000) +
    "  XL @  1 kHz:     {:.2f} ohm\n".format(Xl(1000, L_total_H)) +
    "  XL @ 10 kHz:     {:.1f} ohm   (coil dominates)\n\n".format(Xl(10000, L_total_H)) +
    "FIELD STRENGTH (rough estimate, focal point)\n" +
    "  Peak B-field:    {:.2f} mT  ({:.0f} uT)\n".format(B_center_figure8_T*1e3, B_center_figure8_T*1e6) +
    "  vs Earth field:  {:.0f}x geomagnetic\n".format(B_center_figure8_T/50e-6) +
    "  vs clinical TMS: {:.2f}% (TMS ~ 1.5 T)\n".format(B_center_figure8_T/1.5*100) +
    "  -> well within published bioactive PEMF range\n\n" +
    "WIRE TEMPERATURE: within ampacity ({:.1f}A vs {}A safe)".format(peak_current_A, WIRE_AMPACITY_A)
)
ax3.text(0.02, 0.98, text, transform=ax3.transAxes, fontfamily='monospace',
         fontsize=8, va='top', ha='left')

plt.tight_layout()
output_path = "figure8_coil_winding.png"
plt.savefig(output_path, dpi=120, bbox_inches='tight', facecolor='white')
print("Saved diagram to {}".format(output_path))
print()
print("=" * 60)
print("WINDING PROCEDURE")
print("=" * 60)
print("Cut length: ~{:.1f} m (calculated + 0.5m for leads)".format(total_wire_length_m + 0.5))
print("Each D-loop: {} turns at {}mm radius".format(N_TURNS_PER_LOOP, LOOP_RADIUS_MM))
print("Channel depth required: ~{:.0f}mm (single-row stack)".format(N_TURNS_PER_LOOP * WIRE_DIAMETER_MM))
print("Expected DCR: {:.2f} ohm".format(coil_dcr))
print("Peak field at focus: {:.2f} mT".format(B_center_figure8_T*1e3))
