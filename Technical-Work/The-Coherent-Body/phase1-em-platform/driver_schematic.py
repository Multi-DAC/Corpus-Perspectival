"""
Phase 1 EM Platform — Driver Circuit Schematics

Generates three reference diagrams (pure matplotlib for portability):
  1. driver_circuit_schematic.png  — full electrical schematic (block + connection style)
  2. component_pinouts.png         — TO-220 / diode / BNC pinout reference + test points
  3. physical_layout.png           — physical wiring / breadboard layout

Topology: low-side N-channel MOSFET switch driving a figure-8 coil load,
with flyback diode for inductive kickback recovery, series resistor for
current limiting, optional gate resistor + pulldown for clean drive,
decoupling cap on supply.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D


# ============================================================
# Helper drawing functions for schematic symbols
# ============================================================

def draw_resistor(ax, x, y, w=0.8, h=0.3, label='', label_offset=(0, 0.4), color='black'):
    """Draw a resistor box at center (x,y)."""
    ax.add_patch(Rectangle((x - w/2, y - h/2), w, h, facecolor='lightyellow',
                           edgecolor=color, lw=1.5))
    if label:
        ax.text(x + label_offset[0], y + label_offset[1], label, ha='center',
                fontsize=9, fontweight='bold')


def draw_capacitor(ax, x, y, label=''):
    """Draw capacitor symbol (two parallel plates) at (x,y), vertical orientation."""
    ax.plot([x - 0.3, x + 0.3], [y + 0.1, y + 0.1], color='black', lw=2)
    ax.plot([x - 0.3, x + 0.3], [y - 0.1, y - 0.1], color='black', lw=2)
    if label:
        ax.text(x + 0.5, y, label, fontsize=8, va='center')


def draw_diode(ax, x, y, vertical=True, anode_first=True, label=''):
    """
    Draw diode symbol. If vertical and anode_first: anode at bottom, cathode at top.
    Cathode is the line; anode is the triangle pointing toward it.
    """
    if vertical:
        if anode_first:  # anode bottom, cathode (band) top
            tri = plt.Polygon([(x - 0.25, y - 0.3), (x + 0.25, y - 0.3), (x, y + 0.05)],
                              facecolor='black', edgecolor='black')
            ax.add_patch(tri)
            ax.plot([x - 0.3, x + 0.3], [y + 0.05, y + 0.05], color='black', lw=3)  # cathode bar
        else:  # anode top, cathode bottom
            tri = plt.Polygon([(x - 0.25, y + 0.3), (x + 0.25, y + 0.3), (x, y - 0.05)],
                              facecolor='black', edgecolor='black')
            ax.add_patch(tri)
            ax.plot([x - 0.3, x + 0.3], [y - 0.05, y - 0.05], color='black', lw=3)
    if label:
        ax.text(x + 0.5, y, label, fontsize=8, va='center')


def draw_inductor(ax, x, y, w=1.2, label=''):
    """Draw inductor symbol (humps) at (x,y), horizontal orientation."""
    n_humps = 4
    hump_w = w / n_humps
    theta = np.linspace(0, np.pi, 30)
    for i in range(n_humps):
        cx = x - w/2 + hump_w * (i + 0.5)
        hx = cx + (hump_w / 2) * np.cos(np.pi - theta)
        hy = y + (hump_w / 2) * np.sin(theta)
        ax.plot(hx, hy, color='black', lw=2)
    if label:
        ax.text(x, y - 0.5, label, ha='center', fontsize=9, fontweight='bold')


def draw_mosfet_n(ax, x, y, label='IRLZ44N'):
    """Draw N-channel MOSFET symbol at center (x,y).
    Drain at top, Source at bottom, Gate at left."""
    # Channel line (vertical)
    ax.plot([x, x], [y - 0.7, y + 0.7], color='black', lw=2.5)
    # Gate line (horizontal, separated from channel)
    ax.plot([x - 0.7, x - 0.2], [y, y], color='black', lw=2)
    # Gate vertical bar (the actual gate)
    ax.plot([x - 0.2, x - 0.2], [y - 0.5, y + 0.5], color='black', lw=2)
    # Arrow on source (N-channel: arrow points INTO channel)
    arrow = plt.Polygon([(x - 0.05, y - 0.3), (x - 0.05, y - 0.5), (x + 0.1, y - 0.4)],
                        facecolor='black', edgecolor='black')
    ax.add_patch(arrow)
    # Drain/Source/Gate labels
    ax.text(x + 0.15, y + 0.6, 'D', fontsize=9, fontweight='bold', color='red')
    ax.text(x + 0.15, y - 0.6, 'S', fontsize=9, fontweight='bold', color='black')
    ax.text(x - 0.85, y, 'G', fontsize=9, fontweight='bold', color='blue')
    # Component label
    ax.text(x + 0.6, y, label, fontsize=9, fontweight='bold', va='center')


def draw_ground(ax, x, y):
    """Draw ground symbol at (x,y)."""
    ax.plot([x, x], [y, y - 0.15], color='black', lw=2)
    for i, w in enumerate([0.4, 0.25, 0.1]):
        ax.plot([x - w/2, x + w/2], [y - 0.15 - i*0.08, y - 0.15 - i*0.08],
                color='black', lw=2)


def draw_voltage_source(ax, x, y, label='+12V'):
    """Draw a voltage source as a circle with + sign."""
    ax.add_patch(Circle((x, y), 0.35, facecolor='white', edgecolor='black', lw=2))
    ax.text(x, y + 0.05, '+', ha='center', va='center', fontsize=14, fontweight='bold')
    ax.text(x, y - 0.55, label, ha='center', fontsize=10, fontweight='bold', color='red')


# ============================================================
# DIAGRAM 1 — DRIVER CIRCUIT SCHEMATIC
# ============================================================

fig, ax = plt.subplots(1, 1, figsize=(13, 9))
ax.set_xlim(-1, 14); ax.set_ylim(-2, 10)
ax.set_aspect('equal')
ax.set_title('Phase 1 EM Platform — Driver Circuit Schematic\n' +
             'Low-side N-channel MOSFET switch + flyback diode + series limiter + figure-8 coil',
             fontsize=12, fontweight='bold')

# === POWER SUPPLY (top-left) ===
draw_voltage_source(ax, 1, 8, label='+12V (ALITOVE)')
ax.plot([1, 1], [8.4, 9], color='red', lw=2)
ax.plot([1, 11], [9, 9], color='red', lw=2)  # +12V rail across the top

# Decoupling cap from rail to ground
ax.plot([2.5, 2.5], [9, 7], color='red', lw=1.5)
draw_capacitor(ax, 2.5, 6.7, label='100nF\ndecoupling')
ax.plot([2.5, 2.5], [6.4, 1], color='black', lw=1.5)

# === FLYBACK DIODE branch (drops from +12V rail to MOSFET drain) ===
ax.plot([7, 7], [9, 7], color='red', lw=2)  # from rail down
draw_diode(ax, 7, 6.5, vertical=True, anode_first=True, label='1N5408\nflyback')
# label its terminals
ax.text(7.7, 6.95, 'K (cathode\n= banded end)', fontsize=8, va='center', color='#1f77b4')
ax.text(7.7, 6.0, 'A (anode)', fontsize=8, va='center', color='#d62728')
ax.plot([7, 7], [6.15, 4], color='red', lw=2)  # diode anode down to drain node

# === SERIES RESISTOR + COIL branch (drops from +12V rail to MOSFET drain) ===
ax.plot([10, 10], [9, 8], color='red', lw=2)
draw_resistor(ax, 10, 7.7, label='R_series\n6Ω 50W', label_offset=(1.5, 0))
ax.plot([10, 10], [7.4, 6.5], color='red', lw=2)
draw_inductor(ax, 10, 6, label='Figure-8 COIL\n~280µH, ~1.5Ω DCR\n(load — under test)')
ax.plot([10, 10], [5.5, 4], color='red', lw=2)

# === Drain rail (horizontal connecting flyback anode + coil bottom + MOSFET drain) ===
ax.plot([7, 10], [4, 4], color='red', lw=2)
ax.plot([7, 7], [4, 3.5], color='red', lw=2)  # to MOSFET drain
# Junction dots
ax.add_patch(Circle((7, 4), 0.08, color='black'))
ax.add_patch(Circle((10, 4), 0.08, color='black'))

# === MOSFET ===
draw_mosfet_n(ax, 7, 2.8, label='IRLZ44N')
ax.plot([7, 7], [2.1, 1], color='black', lw=2)  # source to ground rail
draw_ground(ax, 7, 1)

# Ground rail extends to other ground points
ax.plot([1, 7], [1, 1], color='black', lw=1.5)  # to FY6900 GND, supply GND, decouple cap
ax.plot([1, 1], [1, 7.6], color='black', lw=1.5)  # supply (-) goes down then to GND rail
draw_ground(ax, 1, 1)

# === GATE DRIVE ===
# FY6900 source (lower left)
ax.add_patch(FancyBboxPatch((0.5, 3), 2, 1, boxstyle="round,pad=0.1",
                            facecolor='#444444', edgecolor='black'))
ax.text(1.5, 3.5, 'FY6900\nCH1 OUT', ha='center', va='center',
        fontsize=10, color='white', fontweight='bold')

# BNC signal line
ax.plot([2.5, 4], [3.7, 3.7], color='blue', lw=2)
ax.text(3.25, 4.0, 'BNC center', fontsize=7, color='blue', ha='center')
# BNC shield
ax.plot([2.5, 4], [3.2, 3.2], color='black', lw=1.5)
ax.plot([4, 4], [3.2, 1], color='black', lw=1.5)
ax.text(3.25, 2.9, 'BNC shield', fontsize=7, ha='center')

# Gate resistor 22Ω
draw_resistor(ax, 4.7, 3.7, label='22Ω\nR_gate', label_offset=(0, 0.5))
ax.plot([5.1, 6.1], [3.7, 3.7], color='blue', lw=2)
ax.plot([6.1, 6.1], [3.7, 2.8], color='blue', lw=2)  # to gate

# Gate junction dot
ax.add_patch(Circle((6.1, 3.7), 0.08, color='black'))

# Pulldown resistor 10k from gate to ground
ax.plot([6.1, 6.1], [3.7, 4.5], color='blue', lw=1.5)
draw_resistor(ax, 6.1, 4.8, label='10kΩ\npulldown\n(gate to GND)', label_offset=(1.5, 0))
ax.plot([6.1, 6.1], [5.1, 5.5], color='blue', lw=1.5)
ax.plot([6.1, 5], [5.5, 5.5], color='blue', lw=1.5)
ax.plot([5, 5], [5.5, 1], color='black', lw=1.5)

# Annotations
ax.annotate('When MOSFET ON:\ncurrent flows +12V → R → coil → MOSFET → GND\nDiode reverse-biased (idle)',
            xy=(11, 6), xytext=(11.3, 7.5),
            fontsize=8, va='center', color='#2ca02c',
            arrowprops=dict(arrowstyle='->', color='#2ca02c'))

ax.annotate('When MOSFET OFF:\ncoil current commutates UP through diode\nback to +12V — recycles stored energy\n(saves the MOSFET)',
            xy=(7.3, 6.5), xytext=(11.3, 5.5),
            fontsize=8, va='center', color='#d62728',
            arrowprops=dict(arrowstyle='->', color='#d62728'))

ax.text(6.5, -0.5,
        'Flow: FY6900 square wave → 22Ω → MOSFET gate → MOSFET switches coil current at command frequency',
        ha='center', fontsize=9, style='italic',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='black'))

ax.axis('off')
plt.tight_layout()
plt.savefig('driver_circuit_schematic.png', dpi=120, bbox_inches='tight', facecolor='white')
plt.close()
print("Schematic 1 saved: driver_circuit_schematic.png")


# ============================================================
# DIAGRAM 2 — COMPONENT PINOUTS REFERENCE
# ============================================================

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Phase 1 EM Platform — Component Pinouts & Test Points',
             fontsize=14, fontweight='bold')

# --- TOP-LEFT: IRLZ44N TO-220 pinout ---
ax = axes[0, 0]
ax.set_xlim(-3, 3); ax.set_ylim(-4, 4); ax.set_aspect('equal')
ax.set_title('IRLZ44N (TO-220) — pinout (front view)', fontsize=11, fontweight='bold')
ax.add_patch(Rectangle((-1.5, -1.5), 3, 2.5, facecolor='#222222', edgecolor='black'))
ax.add_patch(Rectangle((-1.5, 1.0), 3, 0.6, facecolor='#888888', edgecolor='black'))
ax.add_patch(Circle((0, 1.3), 0.18, facecolor='white', edgecolor='black'))
ax.text(0, 2.0, 'Heatsink tab\n(internally connected to Drain)', ha='center', fontsize=8)
for x, label in zip([-1.0, 0, 1.0], ['G', 'D', 'S']):
    ax.plot([x, x], [-1.5, -3.5], 'k-', lw=2)
    ax.text(x, -3.8, label, ha='center', fontsize=12, fontweight='bold')
ax.text(-2.5, -2.5, 'Pin 1\nGATE\n(from FY6900\nvia 22Ω)', ha='center', fontsize=8, color='#1f77b4')
ax.text(0, -2.5, 'Pin 2\nDRAIN\n(to coil)', ha='center', fontsize=8, color='#d62728')
ax.text(2.5, -2.5, 'Pin 3\nSOURCE\n(to GND)', ha='center', fontsize=8, color='#2ca02c')
ax.text(0, -0.25, 'IRLZ44N', ha='center', fontsize=10, color='white', fontweight='bold')
ax.text(0, 3.5, 'View FROM the FRONT (writing visible)\nLeads point DOWN', ha='center', fontsize=8, style='italic')
ax.axis('off')

# --- TOP-RIGHT: 1N5408 diode polarity ---
ax = axes[0, 1]
ax.set_xlim(-4, 4); ax.set_ylim(-2, 2); ax.set_aspect('equal')
ax.set_title('1N5408 Diode — polarity (cathode = banded end)', fontsize=11, fontweight='bold')
ax.add_patch(Rectangle((-1.5, -0.5), 3, 1.0, facecolor='#444444', edgecolor='black'))
ax.add_patch(Rectangle((1.0, -0.5), 0.3, 1.0, facecolor='white', edgecolor='black'))
ax.plot([-3, -1.5], [0, 0], 'k-', lw=2)
ax.plot([1.5, 3], [0, 0], 'k-', lw=2)
ax.text(-3, 0.4, 'ANODE (A)', ha='center', fontsize=10, color='#d62728', fontweight='bold')
ax.text(-3, -0.6, 'connects to:\nMOSFET DRAIN\n(=bottom of coil)', ha='center', fontsize=8)
ax.text(3, 0.4, 'CATHODE (K)', ha='center', fontsize=10, color='#1f77b4', fontweight='bold')
ax.text(3, -0.6, 'connects to:\n+12V RAIL\n(top of coil)', ha='center', fontsize=8)
ax.text(0, 1.3, 'CURRENT FLOWS A → K when forward biased\nWhite band marks cathode',
        ha='center', fontsize=8, style='italic')
ax.axis('off')

# --- BOTTOM-LEFT: BNC connector wiring ---
ax = axes[1, 0]
ax.set_xlim(-3, 3); ax.set_ylim(-3, 3); ax.set_aspect('equal')
ax.set_title('BNC Connector (FY6900 output) — wiring', fontsize=11, fontweight='bold')
ax.add_patch(Circle((0, 0), 1.8, facecolor='#888888', edgecolor='black', lw=2))
ax.add_patch(Circle((0, 0), 1.0, facecolor='white', edgecolor='black', lw=1))
ax.add_patch(Circle((0, 0), 0.4, facecolor='gold', edgecolor='black', lw=2))
ax.annotate('CENTER PIN\n= SIGNAL\n(to MOSFET\ngate via 22Ω)',
            xy=(0.4, 0), xytext=(2.5, 1.5),
            fontsize=9, color='#d62728', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#d62728'))
ax.annotate('OUTER SHELL\n= GROUND\n(to MOSFET\nsource / GND)',
            xy=(-1.5, 0), xytext=(-2.8, -1.8),
            fontsize=9, color='#1f77b4', fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='#1f77b4'))
ax.text(0, -2.7, 'Use BNC-to-banana or BNC-to-alligator\nadapter cable for breadboard testing',
        ha='center', fontsize=8, style='italic')
ax.axis('off')

# --- BOTTOM-RIGHT: TEST POINTS table ---
ax = axes[1, 1]
ax.axis('off')
ax.set_title('Multimeter Test Points — Verification', fontsize=11, fontweight='bold')
table_text = """
TEST POINT                    EXPECTED            METER MODE
-----------------------------------------------------------------
1. ALITOVE OUTPUT (no load)   12.0V ±0.5V         DC Volts (20V)
2. ALITOVE OUTPUT (loaded)    11.5V minimum       DC Volts (20V)
3. Coil DC resistance         1.52 ohm ±5%        ohm (200)
4. Series resistor R          6.0 ohm ±5%         ohm (20)
5. MOSFET gate quiescent      0V (FY6900 off)     DC Volts (20V)
6. MOSFET gate active         2.5V avg            DC Volts (20V)
   (50% duty 0/5V square)
7. MOSFET drain quiescent     12V (off)           DC Volts (20V)
8. MOSFET drain active        ~6V avg             DC Volts (20V)
   (50% duty)
9. Coil current (in series)   ~1.6A peak          DC Amps (10A)
10. MOSFET temp after 5min    cool-warm           touch
11. Resistor temp after 5min  warm (NOT hot)      touch
12. Coil temp after 5min      cool-warm           touch
-----------------------------------------------------------------

CONTINUITY CHECKS (with circuit OFF, multimeter beep mode)
- BNC center to MOSFET gate (via R_gate):  should beep
- BNC shell to GND rail:                   should beep
- +12V rail to MOSFET drain (no power):    SHOULD NOT beep
  (if beeps -> MOSFET shorted or wire fault)
- All solder joints individually:          beep when probed
"""
ax.text(0.0, 0.95, table_text, transform=ax.transAxes,
        fontfamily='monospace', fontsize=8, va='top', ha='left')

plt.tight_layout()
plt.savefig('component_pinouts.png', dpi=120, bbox_inches='tight', facecolor='white')
plt.close()
print("Schematic 2 saved: component_pinouts.png")


# ============================================================
# DIAGRAM 3 — PHYSICAL BREADBOARD LAYOUT
# ============================================================

fig, ax = plt.subplots(1, 1, figsize=(14, 9))
ax.set_xlim(-1, 25); ax.set_ylim(-2, 16); ax.set_aspect('equal')
ax.set_title('Phase 1 EM Platform — Physical Wiring / Breadboard Layout',
             fontsize=14, fontweight='bold')

ax.plot([0, 24], [14, 14], color='red', lw=3)
ax.text(-0.5, 14, '+12V', ha='right', va='center', fontsize=11, color='red', fontweight='bold')
ax.plot([0, 24], [0, 0], color='black', lw=3)
ax.text(-0.5, 0, 'GND', ha='right', va='center', fontsize=11, color='black', fontweight='bold')

ax.add_patch(FancyBboxPatch((1, 5), 3, 4, boxstyle="round,pad=0.1",
                            facecolor='#222222', edgecolor='black'))
ax.text(2.5, 7, 'ALITOVE\n12V 5A', ha='center', va='center',
        fontsize=10, color='white', fontweight='bold')
ax.plot([2.5, 2.5], [9, 14], color='red', lw=2)
ax.plot([2.5, 2.5], [5, 0], color='black', lw=2)

ax.plot([4, 4], [14, 11], color='red', lw=1.5)
ax.add_patch(Rectangle((3.7, 10.5), 0.6, 0.5, facecolor='lightyellow', edgecolor='black'))
ax.text(4.6, 10.75, '100nF', fontsize=8, va='center')
ax.plot([4, 4], [10.5, 0], color='black', lw=1.5)

ax.add_patch(FancyBboxPatch((1, 1.5), 3, 2.5, boxstyle="round,pad=0.1",
                            facecolor='#444444', edgecolor='black'))
ax.text(2.5, 2.75, 'FY6900\nCH1 OUT', ha='center', va='center',
        fontsize=10, color='white', fontweight='bold')

ax.plot([4, 6], [3.5, 3.5], color='blue', lw=2)
ax.plot([4, 6], [2, 2], color='black', lw=1.5)
ax.text(5, 3.9, 'BNC: signal', fontsize=7, color='blue')
ax.text(5, 1.6, 'BNC: shield to GND', fontsize=7)

ax.add_patch(Rectangle((6, 3.2), 1.5, 0.6, facecolor='lightyellow', edgecolor='black'))
ax.text(6.75, 3.5, '22 ohm', ha='center', va='center', fontsize=9, fontweight='bold')
ax.plot([7.5, 9], [3.5, 3.5], color='blue', lw=2)

ax.plot([9, 9], [3.5, 5.5], color='blue', lw=2)
ax.add_patch(Rectangle((8.7, 5.5), 0.6, 1.0, facecolor='lightyellow', edgecolor='black'))
ax.text(9.7, 6, '10k ohm\npulldown', fontsize=7, va='center')
ax.plot([9, 9], [3.5, 1], color='blue', lw=2)
ax.plot([9, 9], [1, 0], color='black', lw=1.5)

ax.add_patch(FancyBboxPatch((10, 2), 3, 4, boxstyle="round,pad=0.1",
                            facecolor='#222222', edgecolor='black'))
ax.text(11.5, 4, 'IRLZ44N\nMOSFET', ha='center', va='center',
        fontsize=10, color='white', fontweight='bold')
ax.text(11.5, 6.3, 'Drain', ha='center', fontsize=8, color='red')
ax.text(11.5, 1.7, 'Source', ha='center', fontsize=8, color='black')
ax.text(9.7, 4, 'Gate', ha='right', fontsize=8, color='blue')

ax.plot([11.5, 11.5], [2, 0], color='black', lw=1.5)
ax.plot([11.5, 11.5], [6, 8], color='red', lw=2)

ax.add_patch(FancyBboxPatch((10, 8), 7, 2.5, boxstyle="round,pad=0.1",
                            facecolor='#1f77b4', edgecolor='black', alpha=0.6))
ax.text(13.5, 9.25, 'FIGURE-8 COIL\n~280uH, ~1.5 ohm', ha='center', va='center',
        fontsize=10, fontweight='bold', color='white')

ax.plot([13.5, 13.5], [10.5, 11.5], color='red', lw=2)
ax.add_patch(Rectangle((12, 11.5), 3, 0.8, facecolor='#aaaaaa', edgecolor='black'))
ax.text(13.5, 11.9, '6 ohm 50W', ha='center', va='center', fontsize=10, fontweight='bold')
ax.plot([13.5, 13.5], [12.3, 14], color='red', lw=2)

ax.plot([17, 17], [14, 13], color='red', lw=2)
ax.add_patch(Rectangle((16.7, 11.5), 0.6, 1.5, facecolor='#444444', edgecolor='black'))
ax.add_patch(Rectangle((16.7, 12.7), 0.6, 0.3, facecolor='white', edgecolor='black'))
ax.text(17.8, 12.85, 'K (cathode,\nbanded end)', fontsize=7, va='center')
ax.text(17.8, 11.7, 'A (anode)', fontsize=7, va='center')
ax.text(16, 12.25, '1N5408\nflyback', ha='right', fontsize=9, color='black', fontweight='bold')
ax.plot([17, 17], [11.5, 6.5], color='blue', lw=2, linestyle='--')
ax.plot([17, 11.5], [6.5, 6.5], color='blue', lw=2, linestyle='--')

ax.annotate('FOCAL POINT\n(place on body region\nbeing stimulated)',
            xy=(13.5, 9.25), xytext=(20, 9.25),
            ha='left', fontsize=9, fontweight='bold', color='black',
            arrowprops=dict(arrowstyle='->', color='black'))

note_text = (
    'BUILD ORDER:\n'
    '1. Mount supply, lay rails\n'
    '2. Install MOSFET, gate R, pulldown\n'
    '3. Install series resistor + flyback\n'
    '4. Connect DUMMY 6 ohm resistor\n'
    '   in place of coil\n'
    '5. Power-on test: verify drain swings\n'
    '6. Replace dummy with figure-8 coil\n'
    '7. Re-verify; begin protocol\n\n'
    'WARNING:\n'
    '- Disconnect supply before\n'
    '  modifying circuit\n'
    '- Never operate without flyback diode\n'
    '- Verify diode polarity before power'
)
ax.text(20.5, 1, note_text, fontsize=8, va='bottom', ha='left',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='lightyellow', edgecolor='black'))

ax.axis('off')
plt.tight_layout()
plt.savefig('physical_layout.png', dpi=120, bbox_inches='tight', facecolor='white')
plt.close()
print("Schematic 3 saved: physical_layout.png")
print()
print("Done. Three reference diagrams generated.")
