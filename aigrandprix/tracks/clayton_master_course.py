"""
Clayton's Master Course — 45-Gate Gauntlet
Designed by Clayton (Feb 9, 2026)
Converted to 3D coordinates by Clawd

Every maneuver type represented:
- Sprint straight, Sharp 90° turns, Chicanes, Ascending/Descending
- S-curves, Split-S, Hairpins, Power loops, Dive gates
- Progressive difficulty with recovery sprints between punishment sections

Coordinate system: X = forward, Y = lateral, Z = altitude
Gate radius: 1.5m (competition standard)
"""

import numpy as np

MASTER_COURSE = {
    "name": "Lobster's Revenge",
    "description": "45-gate master course with all maneuver types - full lap",
    "gate_radius": 1.5,
    "gates": [
        # === SECTION 1: Opening Sprint & First Turn ===
        # Gate 1: Start - sprint straight
        {"pos": [0, 0, 10], "label": "G1: Start/Sprint"},
        # Gate 2: 15m ahead - sharp 90° left
        {"pos": [15, 0, 10], "label": "G2: Sharp 90° L entry"},
        # Gate 3: 12m to the left
        {"pos": [15, -12, 10], "label": "G3: Chicane start"},

        # === SECTION 2: Chicane ===
        # Gates 3->4: Chicane (tight left-right-left zigzags)
        {"pos": [21, -12, 10], "label": "G4: Chicane exit -> sprint"},

        # === SECTION 3: Sprint Recovery ===
        # Gate 5: 12m ahead - ascending
        {"pos": [33, -12, 10], "label": "G5: Ascent entry"},


        # === SECTION 4: Vertical Challenge ===
        # Gate 6: 10m up
        {"pos": [33, -12, 20], "label": "G6: Top -> dive"},
        # Gate 7: 8m steep down
        {"pos": [33, -12, 12], "label": "G7: Dive bottom -> Split-S"},

        # === SECTION 5: Split-S & Hairpin ===
        # Gate 8: After split-s (reverse direction, climb)
        {"pos": [33, -12, 16], "label": "G8: Split-S exit -> hairpin"},
        # Gate 9: Hairpin 180° reversal, 5m back
        {"pos": [28, -12, 16], "label": "G9: Hairpin -> S-curve"},

        # === SECTION 6: S-Curve & Power Loop ===
        # Gate 10: S-curve alternating turns
        {"pos": [24, -8, 16], "label": "G10: S-curve -> power loop"},
        # Gate 11: Power loop (vertical loop through gate)
        {"pos": [20, -8, 16], "label": "G11: Power loop -> dive-hairpin"},

        # === SECTION 7: Dive-Hairpin Combo ===
        # Gate 12: 4m down, then back
        {"pos": [20, -8, 12], "label": "G12: Dive-hairpin exit"},

        # === SECTION 8: Ascending Chicane ===
        # Gate 13: Chicane + ascending, 5m up zigzags
        {"pos": [17, -5, 17], "label": "G13: Ascend chicane exit"},

        # === SECTION 9: Sharp Double Turn ===
        # Gate 14: Sharp right then sharp left, 4m side-switch
        {"pos": [17, 0, 17], "label": "G14: Sharp burst -> sprint"},

        # === SECTION 10: Recovery Sprint ===
        # Gate 15: 12m sprint straight
        {"pos": [29, 0, 17], "label": "G15: Sprint -> Split-S"},

        # === SECTION 11: Split-S Descent ===
        # Gate 16: Split-S down + reverse climb
        {"pos": [29, 0, 12], "label": "G16: Split-S -> dive weave"},

        # === SECTION 12: Dive Weave ===
        # Gate 17: Dive + S-curve, 5m down/weave
        {"pos": [25, 3, 8], "label": "G17: Dive weave -> loop"},

        # === SECTION 13: Loop-Reversal Chain ===
        # Gate 18: Power loop into hairpin reversal
        {"pos": [21, 3, 8], "label": "G18: Loop-hairpin -> sprint"},

        # === SECTION 14: Buildup Sprint ===
        # Gate 19: 10m sprint
        {"pos": [31, 3, 8], "label": "G19: Sprint -> dive"},

        # === SECTION 15: Pure Dive ===
        # Gate 20: 7m steep down
        {"pos": [38, 3, 1], "label": "G20: Dive -> ultra chicane"},

        # === SECTION 16: Ultra-Tight Chicane (punishment) ===
        # Gate 21: 3m punishing zigzags
        {"pos": [41, 0, 1], "label": "G21: Ultra chicane -> ascend"},

        # === SECTION 17: Ascend + Sharp Combo ===
        # Gate 22: Ascending + sharp 90° right
        {"pos": [41, 0, 6], "label": "G22: Ascend-sharp exit"},

        # === SECTION 18: S-Curve Reversal ===
        # Gate 23: S-curve into hairpin reversal
        {"pos": [37, -3, 6], "label": "G23: S-curve reversal -> sprint"},

        # === SECTION 19: Power Sprint ===
        # Gate 24: 14m sprint for speed
        {"pos": [51, -3, 6], "label": "G24: Sprint -> double vertical"},

        # === SECTION 20: Double Vertical ===
        # Gate 25: Power loop
        {"pos": [51, -3, 14], "label": "G25: Power loop -> split"},

        # === SECTION 21: Split Combo ===
        # Gate 26: Split-S down/reverse
        {"pos": [51, -3, 8], "label": "G26: Split -> dive chicane"},

        # === SECTION 22: Dive Chicane Chain ===
        # Gate 27: Dive through chicane, down/zigzags
        {"pos": [47, 0, 4], "label": "G27: Dive chicane -> ascend S"},

        # === SECTION 23: Ascending S-Curve ===
        # Gate 28: Ascending + S-curve weave
        {"pos": [43, 3, 10], "label": "G28: Ascend S -> sharp hairpin"},

        # === SECTION 24: Sharp Hairpin Pivot ===
        # Gate 29: Sharp 90° left into hairpin
        {"pos": [43, -3, 10], "label": "G29: Hairpin -> descent sprint"},

        # === SECTION 25: Descent Sprint ===
        # Gate 30: Sprint + descending
        {"pos": [52, -3, 4], "label": "G30: Descent sprint -> tight chain"},

        # === SECTION 26: Tight Chain (punishment section) ===
        # Gate 31: 3m chicane zigzags
        {"pos": [55, 0, 4], "label": "G31: Tight chicane -> power-split"},

        # === SECTION 27: Power-Split Vertical ===
        # Gate 32: Power loop into split-s
        {"pos": [55, 0, 12], "label": "G32: Power-split -> sharp weave"},

        # === SECTION 28: Sharp Weave ===
        # Gate 33: Sharp 90° right through S-curve
        {"pos": [55, 6, 12], "label": "G33: Sharp weave -> dive-ascend"},

        # === SECTION 29: Dive-Ascend Trap ===
        # Gate 34: Dive down then ascend up (the trap)
        {"pos": [55, 6, 5], "label": "G34: Dive-ascend -> final"},

        # === SECTION 30: Hairpin Dive ===
        # Gate 35: Hairpin reversal into dive
        {"pos": [50, 6, 1], "label": "G35: Hairpin dive -> recovery"},

        # === SECTION 31: Recovery Sprint ===
        # Gate 36: 12m sprint straight
        {"pos": [62, 6, 1], "label": "G36: Sprint -> chicane-loop"},

        # === SECTION 32: Chicane-Loop Hybrid ===
        # Gate 37: Chicane into power loop (vertical)
        {"pos": [66, 3, 8], "label": "G37: Chicane-loop -> split-sharp"},

        # === SECTION 33: Split-Sharp Descent ===
        # Gate 38: Split-S descend+reverse with sharp 90 left
        {"pos": [62, 0, 4], "label": "G38: Split-sharp -> S-sprint"},

        # === SECTION 34: S-Curve Sprint Dash ===
        # Gate 39: S-curve weave with sprint
        {"pos": [70, -3, 4], "label": "G39: S-sprint -> reversal ascent"},

        # === SECTION 35: Reversal Ascent ===
        # Gate 40: Hairpin reversal + ascending 7m up
        {"pos": [63, -3, 11], "label": "G40: Reversal ascent -> sharp chicane"},

        # === SECTION 36: Sharp Chicane Burst ===
        # Gate 41: Sharp 90 right through chicane
        {"pos": [63, 3, 11], "label": "G41: Sharp chicane -> vertical descent"},

        # === SECTION 37: Final Vertical Descent ===
        # Gate 42: Power loop + descending
        {"pos": [59, 3, 5], "label": "G42: Loop descent -> split dive"},

        # === SECTION 38: Split Dive Combo ===
        # Gate 43: Split-S into dive
        {"pos": [55, 3, 1], "label": "G43: Split dive -> S-hairpin"},

        # === SECTION 39: S-Curve Hairpin Closer ===
        # Gate 44: S-curve into hairpin reversal
        {"pos": [48, 0, 3], "label": "G44: S-hairpin -> final sprint"},

        # === SECTION 40: Ultimate Finisher ===
        # Gate 45: Sprint then dive back to start/finish
        {"pos": [36, 0, 1], "label": "G45: FINISH - dive to start"},
    ]
}


def get_gates():
    """Return gate positions as numpy array for sim consumption."""
    return np.array([g["pos"] for g in MASTER_COURSE["gates"]], dtype=np.float32)


def get_gate_labels():
    """Return gate labels for visualization."""
    return [g["label"] for g in MASTER_COURSE["gates"]]


# Also export as sub-courses for curriculum learning
SECTIONS = {
    "opening_sprint": list(range(0, 4)),      # Gates 1-4: Sprint + turn + chicane
    "vertical_challenge": list(range(4, 8)),   # Gates 5-8: Ascend/dive/split-s
    "technical_middle": list(range(8, 14)),    # Gates 9-14: S-curve/loop/hairpin
    "speed_section": list(range(14, 18)),      # Gates 15-18: Sprint/split/weave
    "punishment_zone": list(range(18, 24)),    # Gates 19-24: Dive/ultra-chicane
    "power_section": list(range(24, 29)),      # Gates 25-29: Verticals/combos
    "death_run": list(range(29, 35)),          # Gates 30-35: Everything at once
    "hybrid_combos": list(range(35, 40)),      # Gates 36-40: Multi-maneuver combos
    "final_gauntlet": list(range(40, 45)),      # Gates 41-45: Ultimate punishment -> finish
}


if __name__ == "__main__":
    gates = get_gates()
    labels = get_gate_labels()
    print(f"Clayton's Gauntlet: {len(gates)} gates")
    print(f"Course bounds: X[{gates[:,0].min():.0f}-{gates[:,0].max():.0f}] "
          f"Y[{gates[:,1].min():.0f}-{gates[:,1].max():.0f}] "
          f"Z[{gates[:,2].min():.0f}-{gates[:,2].max():.0f}]")
    print(f"\nSections for curriculum learning:")
    for name, indices in SECTIONS.items():
        section_gates = gates[indices]
        print(f"  {name}: {len(indices)} gates")
    print(f"\nFull course:")
    for i, (pos, label) in enumerate(zip(gates, labels)):
        print(f"  {label}: ({pos[0]:.0f}, {pos[1]:.0f}, {pos[2]:.0f})")
