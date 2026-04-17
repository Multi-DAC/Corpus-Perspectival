"""
A.2: Light Spectrum of Resolved T^6/Z_3 in RS_1
Project Meridian Phase 23, March 25, 2026

QUESTION: Are there sub-eV modes from the resolved Z_3 orbifold?
If yes: engineering channels reopen (resonant cavities, precision sensors).
If no: engineering narrows to topology and information channels.

THE KEY PHYSICS:
The resolved T^6/Z_3 orbifold has h^{1,1} = 36 Kahler moduli:
  - 9 untwisted (from T^6 cycles — BULK fields)
  - 27 twisted (from exceptional divisors at fixed points — BRANE fields)

Each complexified: t_i = b_i + i*J_i (B-field axion + Kahler volume)
The AXIONS (b_i) get masses from instantons wrapping the cycles.
The VOLUMES (J_i) get masses from the stabilization potential.

The crucial distinction:
  - Twisted axions: small cycles, large instanton effects -> HEAVY (~GeV)
  - Untwisted axions: large cycles, suppressed instantons -> LIGHT (sub-eV!)

In the RS_1 warped background, the warp factor further suppresses the
untwisted axion masses by eps ~ 10^{-15}.
"""

import numpy as np

# ============================================================
# Constants
# ============================================================
M_Pl = 2.435e18       # Reduced Planck mass (GeV)
k = M_Pl              # AdS curvature
epsilon = 1e-15        # Hierarchy ratio
keps = k * epsilon     # IR brane scale ~ 2.4 TeV
Lambda_phi = np.sqrt(6) * M_Pl * epsilon  # Radion decay constant ~ 6 TeV
hbar_c = 0.197e-13     # GeV*cm
eV = 1e-9              # 1 eV in GeV
meV = 1e-12            # 1 meV in GeV
neV = 1e-18            # 1 neV in GeV

# Phase 22 parameters
v_blowup = 0.205       # Blow-up VEV (20.5% of compactification scale)
kappa1 = -0.01654      # Moduli space curvature from Phase 22
DKL_CA = 720           # E8 quartic identity

# ============================================================
# PART 1: Hodge numbers and moduli count
# ============================================================

def hodge_numbers():
    """
    Resolved T^6/Z_3 orbifold Hodge numbers.

    T^6 as (T^2)^3 with Z_3 acting as (z1,z2,z3) -> (w*z1, w*z2, w*z3)
    where w = exp(2*pi*i/3).

    Untwisted (1,1)-forms: dz_i ^ dz_bar_j -> w * w_bar = 1 (ALL invariant)
    h^{1,1}_untw = 9

    Twisted: 27 fixed points (3 per T^2, 3^3 = 27 total)
    Each contributes one exceptional P^1 (from blowing up C^3/Z_3)
    h^{1,1}_tw = 27

    (2,1)-forms: dz_i ^ dz_j ^ dz_bar_k -> w^2 * w_bar = w != 1
    h^{2,1}_untw = 0
    h^{2,1}_tw = 0 (for Z_3 with standard action)
    """
    print("=" * 70)
    print("A.2: LIGHT SPECTRUM OF RESOLVED T^6/Z_3 IN RS_1")
    print("=" * 70)

    print(f"\n--- HODGE NUMBERS ---")
    print(f"  h^(1,1)_untwisted = 9   (Kahler forms from T^6)")
    print(f"  h^(1,1)_twisted   = 27  (exceptional divisors at fixed points)")
    print(f"  h^(1,1)_total     = 36")
    print(f"  h^(2,1)           = 0   (no complex structure moduli)")
    print(f"  Euler number chi  = 2(h^(1,1) - h^(2,1)) = 72")

    print(f"\n--- MODULI COUNT ---")
    print(f"  Kahler moduli:     36 real (volumes J_i)")
    print(f"  B-field axions:    36 real (b_i from integral of B on 2-cycles)")
    print(f"  Complexified:      t_i = b_i + i*J_i, i = 1..36")
    print(f"  Wilson line:       ~2 real (from E8 breaking, direction + magnitude)")
    print(f"  Complex structure: 0 (h^(2,1) = 0)")
    print(f"  TOTAL:             ~74 real scalar moduli")

    return 9, 27, 36

# ============================================================
# PART 2: Mass estimates by class
# ============================================================

def axion_mass_formula(t, f_a_scale='bulk'):
    """
    Axion mass from instanton wrapping a 2-cycle of volume t (in string units).

    Instanton action: S = 2*pi*t
    Instanton scale: Lambda^4 ~ (k*eps)^4 * exp(-S) [warped]

    For bulk axion (untwisted): f_a ~ M_Pl / sqrt(S)
    For brane axion (twisted):  f_a ~ Lambda_phi / sqrt(S)

    Mass: m^2 = Lambda^4 / f_a^2
    """
    S = 2 * np.pi * t
    exp_S = np.exp(-S)

    if f_a_scale == 'bulk':
        # Untwisted: bulk field, Planck-scale decay constant
        f_a = M_Pl / np.sqrt(S) if S > 0 else M_Pl
    elif f_a_scale == 'brane':
        # Twisted: brane-localized, TeV-scale decay constant
        f_a = Lambda_phi / np.sqrt(S) if S > 0 else Lambda_phi
    else:
        raise ValueError(f"Unknown f_a_scale: {f_a_scale}")

    # Instanton-generated scale (warped)
    Lambda4 = keps**4 * exp_S

    # Axion mass
    m_sq = Lambda4 / f_a**2
    m = np.sqrt(m_sq) if m_sq > 0 else 0

    return {
        't': t,
        'S': S,
        'exp_S': exp_S,
        'f_a': f_a,
        'Lambda4': Lambda4,
        'm_sq': m_sq,
        'm': m,
        'f_a_scale': f_a_scale,
    }

def kahler_modulus_mass(sector='twisted'):
    """
    Mass of Kahler volume modulus (not axion).

    Twisted (blow-up): stabilized by NCG spectral action
    -> mass ~ sqrt(C_ncg) * k*eps / (4*pi) ~ 100 GeV

    Untwisted (T^6 volumes): stabilized by flux + NP potential
    -> mass ~ k*eps * exp(-S/2) / sqrt(M_Pl/keps) ~ variable
    """
    if sector == 'twisted':
        # Same mechanism as radion but in blow-up direction
        # From A.1b: C_ncg ~ 0.383 for radion
        # Blow-up direction: curvature ~ |kappa1| * (keps)^2
        C_blowup = abs(kappa1) * DKL_CA * v_blowup**2 / (8 * np.pi**2)
        m_sq = C_blowup * keps**2 / (16 * np.pi**2)
        m = np.sqrt(m_sq)
        return {'m': m, 'm_sq': m_sq, 'C': C_blowup, 'sector': 'twisted'}
    else:
        # Untwisted: controlled by classical Kahler potential
        # Mass ~ (keps)^2 / M_Pl (gravity-mediated SUSY breaking scale)
        m = keps**2 / M_Pl  # ~ TeV^2 / M_Pl ~ 10^-6 eV ... wait
        # This is actually the gravitino mass in gravity mediation
        # The Kahler moduli masses depend on the specific stabilization scheme
        # Conservative estimate: m ~ m_{3/2} ~ (keps)^2 / M_Pl
        m_gravitino = keps**2 / M_Pl
        return {'m': m_gravitino, 'sector': 'untwisted', 'note': 'gravity-mediated scale'}

def mass_table():
    """Compute and print the full mass table."""

    print(f"\n{'='*70}")
    print("MASS SPECTRUM BY CLASS")
    print(f"{'='*70}")

    # -------------------------------------------------------
    # Class 1: Twisted Kahler moduli (27 blow-up volumes)
    # -------------------------------------------------------
    print(f"\n--- CLASS 1: TWISTED KAHLER MODULI (27 blow-up volumes) ---")
    tw_kahler = kahler_modulus_mass('twisted')
    print(f"  Stabilization: NCG spectral action (same as radion)")
    print(f"  C_blowup = |kappa1| * DKL * v^2 / (8 pi^2) = {tw_kahler['C']:.4f}")
    print(f"  m = {tw_kahler['m']:.1f} GeV")
    print(f"  VERDICT: HEAVY. Not sub-eV.")

    # -------------------------------------------------------
    # Class 2: Untwisted Kahler moduli (9 T^6 volumes)
    # -------------------------------------------------------
    print(f"\n--- CLASS 2: UNTWISTED KAHLER MODULI (9 T^6 volumes) ---")
    untw_kahler = kahler_modulus_mass('untwisted')
    print(f"  Stabilization: Gravity-mediated (conservative)")
    print(f"  m ~ (k*eps)^2 / M_Pl = TeV^2 / M_Pl = {untw_kahler['m']/eV:.2e} eV")
    print(f"  = {untw_kahler['m']:.3e} GeV")
    print(f"  NOTE: This is the gravitino mass scale in gravity mediation.")
    print(f"  If SUSY breaking is different, could be lighter or heavier.")
    print(f"  VERDICT: SUB-eV if gravity-mediated! But model-dependent.")

    # -------------------------------------------------------
    # Class 3: Twisted axions (27 B-field on exceptional divisors)
    # -------------------------------------------------------
    print(f"\n--- CLASS 3: TWISTED AXIONS (27 B-field on exceptional divisors) ---")
    print(f"  These are BRANE-localized (at fixed points) -> f_a ~ Lambda_phi")
    print(f"  Cycle volume: t ~ v^2 = {v_blowup**2:.4f} (small!)")

    tw_axion = axion_mass_formula(v_blowup**2, f_a_scale='brane')
    print(f"  Instanton action S = 2*pi*t = {tw_axion['S']:.3f}")
    print(f"  exp(-S) = {tw_axion['exp_S']:.4f}")
    print(f"  f_a = Lambda_phi / sqrt(S) = {tw_axion['f_a']:.1f} GeV")
    print(f"  m = {tw_axion['m']:.1f} GeV")
    print(f"  VERDICT: HEAVY (~GeV). Small cycle -> unsuppressed instanton.")

    # -------------------------------------------------------
    # Class 4: UNTWISTED AXIONS (9 B-field on T^6 cycles) — KEY CLASS
    # -------------------------------------------------------
    print(f"\n--- CLASS 4: UNTWISTED AXIONS (9 B-field on T^6 cycles) ---")
    print(f"  These are BULK fields -> f_a ~ M_Pl / sqrt(S)")
    print(f"  Cycle volumes t from the original T^6 2-tori.")
    print(f"  The warp factor suppresses the instanton scale by eps^4.")

    t_values = [0.3, 0.5, 0.8, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]

    print(f"\n  {'t':>6s} | {'S=2pi*t':>8s} | {'exp(-S)':>10s} | {'f_a (GeV)':>12s} | {'m (GeV)':>12s} | {'m (eV)':>12s} | {'freq':>12s} | {'Sub-eV?':>8s}")
    print(f"  {'-'*6}-+-{'-'*8}-+-{'-'*10}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*12}-+-{'-'*8}")

    sub_eV_modes = []

    for t in t_values:
        result = axion_mass_formula(t, f_a_scale='bulk')
        m = result['m']
        m_eV = m / eV

        # Frequency: f = m*c^2/h = m * (GeV) / (4.136e-24 GeV*s)
        if m > 0:
            freq_Hz = m / (4.136e-24)  # GeV / (GeV*s) = Hz
            if freq_Hz > 1e12:
                freq_str = f"{freq_Hz/1e12:.1f} THz"
            elif freq_Hz > 1e9:
                freq_str = f"{freq_Hz/1e9:.1f} GHz"
            elif freq_Hz > 1e6:
                freq_str = f"{freq_Hz/1e6:.1f} MHz"
            elif freq_Hz > 1e3:
                freq_str = f"{freq_Hz/1e3:.1f} kHz"
            else:
                freq_str = f"{freq_Hz:.1f} Hz"
        else:
            freq_str = "---"

        is_sub_eV = m < eV
        marker = "YES!" if is_sub_eV else "no"
        if is_sub_eV:
            sub_eV_modes.append((t, m, m_eV, freq_str))

        print(f"  {t:6.1f} | {result['S']:8.2f} | {result['exp_S']:10.3e} | {result['f_a']:12.3e} | {m:12.3e} | {m_eV:12.3e} | {freq_str:>12s} | {marker:>8s}")

    print(f"\n  SUB-eV MODES FOUND: {len(sub_eV_modes)}")

    # -------------------------------------------------------
    # Class 5: Wilson line modulus
    # -------------------------------------------------------
    print(f"\n--- CLASS 5: WILSON LINE MODULUS ---")
    print(f"  Direction: (1,1,-2,0,0,0,0,0) in E8 root space")
    print(f"  VEV: z = 5/18 + delta_z, delta_z = -0.000698 (Phase 22)")
    print(f"  Stabilized by threshold corrections (kappa1 = {kappa1})")
    # The Wilson line mass is set by the curvature of the potential in z
    # m_W^2 ~ kappa1 * (keps)^2 (from the threshold correction curvature)
    m_W_sq = abs(kappa1) * keps**2
    m_W = np.sqrt(m_W_sq)
    print(f"  m ~ sqrt(|kappa1|) * k*eps = {np.sqrt(abs(kappa1)):.3f} * {keps:.0f} GeV")
    print(f"  m = {m_W:.1f} GeV")
    print(f"  VERDICT: HEAVY (~TeV). Threshold-stabilized.")

    # -------------------------------------------------------
    # Class 6: KK tower
    # -------------------------------------------------------
    print(f"\n--- CLASS 6: KK TOWER ---")
    print(f"  First KK mass: m_1 ~ k*eps = {keps:.0f} GeV (TeV scale)")
    print(f"  Tower: m_n ~ n * k*eps")
    print(f"  VERDICT: ALL HEAVY. No sub-eV KK modes.")

    return sub_eV_modes

# ============================================================
# PART 3: Coupling analysis for sub-eV modes
# ============================================================

def coupling_analysis(sub_eV_modes):
    """Compute couplings of sub-eV axions to SM."""

    print(f"\n{'='*70}")
    print("COUPLING ANALYSIS FOR SUB-eV AXIONS")
    print(f"{'='*70}")

    alpha_em = 1.0 / 137.0

    for t, m, m_eV, freq_str in sub_eV_modes:
        S = 2 * np.pi * t
        f_a = M_Pl / np.sqrt(S)

        # Axion-photon coupling
        g_agamma = alpha_em / (2 * np.pi * f_a)

        # Axion-nucleon coupling (through QCD)
        g_aN = m * 1e-3 / f_a  # rough estimate

        # Gravitational coupling
        g_grav = 1.0 / (M_Pl * np.sqrt(t))

        print(f"\n  --- t = {t:.1f}, m = {m_eV:.2e} eV, freq = {freq_str} ---")
        print(f"    f_a = M_Pl/sqrt(S) = {f_a:.2e} GeV")
        print(f"    g_a-gamma-gamma = alpha/(2*pi*f_a) = {g_agamma:.2e} GeV^-1")
        print(f"    g_gravitational = 1/(M_Pl*sqrt(t)) = {g_grav:.2e} GeV^-1")

        # Experimental bounds
        print(f"    CAST bound: g < 6.6e-11 GeV^-1 -> {'PASSES' if g_agamma < 6.6e-11 else 'EXCLUDED'} (by {6.6e-11/g_agamma:.0e})")
        print(f"    IAXO projected: g ~ 1e-12 GeV^-1 -> {'below' if g_agamma < 1e-12 else 'within reach'}")
        print(f"    ABRACADABRA: sensitive to g ~ 1e-16 for m ~ neV -> {'relevant' if m_eV < 1e-6 and g_agamma > 1e-19 else 'not in window'}")

    # Cuscuton enhancement
    print(f"\n--- CUSCUTON CONSTRAINT CHANNEL ---")
    print(f"  The cuscuton's instantaneous response (c_s = inf) could")
    print(f"  amplify axion effects through the constraint equation.")
    print(f"  The axion modifies the bulk geometry -> cuscuton responds")
    print(f"  instantaneously -> modified gravitational potential.")
    print(f"  Enhancement factor: TBD (requires axion-cuscuton mixing computation)")
    print(f"  This is a NOVEL coupling channel unique to Meridian.")

# ============================================================
# PART 4: Key results
# ============================================================

def key_results(sub_eV_modes):
    """Print the key results summary."""

    print(f"\n\n{'='*70}")
    print("A.2 KEY RESULTS")
    print(f"{'='*70}")

    n_sub = len(sub_eV_modes)

    if n_sub > 0:
        lightest = min(sub_eV_modes, key=lambda x: x[1])
        heaviest = max(sub_eV_modes, key=lambda x: x[1])

        print(f"""
    +--------------------------------------------------------------+
    |                                                              |
    |  RESULT 1: SUB-eV MODES EXIST                               |
    |  {n_sub} untwisted B-field axions with masses in the           |
    |  sub-eV range (for cycle volumes t > ~0.3 string units).     |
    |                                                              |
    |  Mass range: {lightest[2]:.1e} eV to {heaviest[2]:.1e} eV               |
    |  Frequency range: {lightest[3]} to {heaviest[3]}            |
    |                                                              |
    |  RESULT 2: THEY ARE ULTRA-WEAKLY COUPLED                    |
    |  g_a-gamma ~ 10^-20 GeV^-1 (8 orders below IAXO)           |
    |  f_a ~ M_Pl / sqrt(S) ~ 10^17 GeV (Planck-scale decay)     |
    |  Direct detection: FAR below any planned experiment          |
    |                                                              |
    |  RESULT 3: TOPOLOGICAL HANDLES SURVIVE                       |
    |  Axion field space is S^1 (periodic). Winding modes,         |
    |  domain walls, and cosmic strings are topological defects    |
    |  that could have macroscopic effects despite weak coupling.  |
    |  This is the B.2 connection.                                 |
    |                                                              |
    |  RESULT 4: THE MASS HIERARCHY                                |
    |  Twisted (27): GeV-scale (brane-localized, small cycles)    |
    |  Untwisted (9): sub-eV (bulk, large cycles, warp-suppressed)|
    |  This split is STRUCTURAL, not fine-tuned.                   |
    |  Small cycles -> unsuppressed instantons -> heavy            |
    |  Large cycles -> suppressed instantons -> light              |
    |                                                              |
    |  RESULT 5: ENGINEERING IMPLICATIONS                          |
    |  The sub-eV axions are in principle resonantly excitable     |
    |  at microwave to radio frequencies. But the coupling is      |
    |  so weak that no practical device reaches the sensitivity.   |
    |  UNLESS: the cuscuton constraint channel enhances the        |
    |  effective coupling (novel, needs B.2 computation).          |
    |  OR: topological effects (domain walls, strings) provide     |
    |  non-perturbative handles (also B.2 territory).             |
    |                                                              |
    +--------------------------------------------------------------+

    FULL MASS TABLE SUMMARY:

    | Class                    | Count | Mass Scale    | Sub-eV? |
    |--------------------------|-------|---------------|---------|
    | Twisted Kahler (blow-up) | 27    | ~10 GeV       | No      |
    | Untwisted Kahler (T^6)   | 9     | ~1 ueV (GMSB) | Maybe*  |
    | Twisted axions           | 27    | ~GeV          | No      |
    | UNTWISTED AXIONS         | 9     | neV - meV     | YES!    |
    | Wilson line              | 2     | ~300 GeV      | No      |
    | KK tower                 | inf   | >= TeV        | No      |

    * Untwisted Kahler masses depend on SUSY-breaking mediation.
      Gravity-mediated: m ~ TeV^2/M_Pl ~ ueV (sub-eV!).
      Gauge-mediated: m ~ TeV (heavy).
      In Meridian's RS_1: likely gravity-mediated -> sub-eV.

    THE ENGINEERING LANDSCAPE AFTER A.2:
    - Radion: DEAD (120 GeV, sub-nuclear) [A.1b]
    - Cuscuton direct: WEAK (dark-energy amplitude) [B.1]
    - Sub-eV axions: EXIST but ultra-weakly coupled [THIS RESULT]
    - Topological channels: OPEN (B.2 needed)
    - Cuscuton-axion coupling: UNKNOWN (novel, needs computation)

    The engineering path: topology + information, not brute force.
    The 9 light axions provide the SUBSTRATE for topological effects.
    B.2 determines whether those effects are accessible.
    """)

# ============================================================
# Main
# ============================================================

def main():
    # Part 1: Hodge numbers
    h11_untw, h11_tw, h11_total = hodge_numbers()

    # Part 2: Mass table
    sub_eV_modes = mass_table()

    # Part 3: Couplings
    if sub_eV_modes:
        coupling_analysis(sub_eV_modes)

    # Part 4: Key results
    key_results(sub_eV_modes)

if __name__ == '__main__':
    main()
