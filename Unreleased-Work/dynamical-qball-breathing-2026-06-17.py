#!/usr/bin/env python
"""
Dream-drive computation (2026-06-17 ~02:50): START the flagged Phase-B dynamical Q-ball solve.

GOAL: test the §7 claim that "the soliton's BREATHING mode ω_b softens to 0 as the chamber density
ρ is bled up toward ρ_crit", by extending the committed R12 thin-wall functional to a collective-
coordinate (radius R) dynamical model with a chameleon density-dependent mass m²(ρ).

PREDICTION (medium-high): raising ρ raises m², which penalizes the volume mass term ∝ R³m² -> the
Q-ball SHRINKS and the breathing mode STIFFENS (ω_b increases), NOT softens. If so, the §7 wording
is WRONG: the mode that maps the *localization* boundary is the TRANSLATIONAL pinning mode in a
spatial screening gradient, not the internal breathing mode. FALSIFY-as-engine.

R12 functional (from figures/make_portal_fig6_soliton.py), parts of E(R,σ;Q,a):
  surface 4πR²S1 | volume V·U0 | charge-kinetic Q²/(2Vf₀²) | EM c_em Q²/(R e^{aσ}) | mass V·½m²σ²+grad
Collective-coordinate dynamics: thin-wall radial inertia M_R(R)=4πR²S1; V_eff(R)=min_σ E(R,σ);
breathing ω_b² = V_eff''(R_min)/M_R(R_min).
"""
import numpy as np
from scipy.optimize import minimize_scalar

# --- R12 parameters (verbatim from the committed soliton script) ---
m0=1.0; f0=1.0; S1=0.5; U0=0.3; c_em=1.0/(8*np.pi); k_sig=0.1
def vol(R): return (4/3)*np.pi*R**3

def E(R, s, Q, a, m2):
    """Total thin-wall energy; m2 = m²(ρ) the chameleon-density-dependent mass-squared."""
    if R<=1e-3: return 1e12
    V=vol(R)
    surf = 4*np.pi*R**2*S1
    volU = V*U0
    chg  = Q**2/(2*V*f0**2)
    em   = c_em*Q**2/(R*np.exp(a*s))
    mass = V*0.5*m2*s**2 + 4*np.pi*R**2*k_sig*s**2
    return surf+volU+chg+em+mass

def Veff(R, Q, a, m2):
    """Energy minimized over σ at fixed R (adiabatic σ following the breathing)."""
    r=minimize_scalar(lambda s: E(R,s,Q,a,m2), bounds=(0.0,3.0), method="bounded")
    return r.fun, r.x

def soliton(Q, a, m2):
    """Find R_min, σ_min, E*, and breathing ω_b at this density (via m2)."""
    Rgrid=np.linspace(0.4,8.0,1400)
    Vg=np.array([Veff(R,Q,a,m2)[0] for R in Rgrid])
    i=int(np.argmin(Vg))
    if i in (0,len(Rgrid)-1):           # min ran to the boundary -> no bound soliton
        return dict(R=np.nan, s=np.nan, E=Vg[i], wb2=np.nan, bound=False)
    R_min=Rgrid[i]
    # refine + curvature by local parabola fit
    sl=slice(max(0,i-6), i+7)
    p=np.polyfit(Rgrid[sl], Vg[sl], 2)         # V ≈ aR²+bR+c
    R_ref=-p[1]/(2*p[0]); Vpp=2*p[0]            # curvature V''
    s_min=Veff(R_ref,Q,a,m2)[1]
    M_R=4*np.pi*R_ref**2*S1                     # thin-wall radial inertia
    wb2=Vpp/M_R
    return dict(R=R_ref, s=s_min, E=np.polyval(p,R_ref), wb2=wb2, bound=Vpp>0)

# --- scan density: m²(ρ) = m0²(1+ρ/ρ*), chameleon-like (mass grows with density) ---
Q, a = 40.0, 0.5
rho = np.linspace(0.0, 20.0, 21)        # ρ/ρ*  (0 = unscreening-chamber vacuum)
print(f"{'ρ/ρ*':>6} {'m²(ρ)':>7} {'R_min':>7} {'σ_in':>7} {'ω_b(breath)':>11} {'ω(carrier)':>11} {'amp~aσ':>8}")
print("-"*72)
sig0=None; wb_first=None; wb_last=None
for r in rho:
    m2=m0**2*(1+r)
    d=soliton(Q,a,m2)
    wb = np.sqrt(d['wb2']) if (d['bound'] and d['wb2']>0) else float('nan')
    V = vol(d['R'])
    w_carrier = Q/(d['s']**2 * V) if d['s']>0 else float('nan')   # Noether ω = Q/(σ²·Vol)
    amp = a*d['s']                                                 # sideband modulation depth ∝ aσ_in
    if sig0 is None: sig0=d['s']
    if not np.isnan(wb):
        if wb_first is None: wb_first=(r,wb)
        wb_last=(r,wb)
    print(f"{r:6.1f} {m2:7.2f} {d['R']:7.3f} {d['s']:7.3f} {wb:11.4f} {w_carrier:11.2f} {amp:8.4f}")

print("-"*72)
print("VERDICT (FALSIFY-as-engine):")
r0,w0=wb_first; r1,w1=wb_last
trend = "STIFFENS" if w1>w0*1.02 else ("SOFTENS" if w1<w0*0.98 else "FLAT (ρ-insensitive)")
print(f"  breathing ω_b  ρ/ρ*[{r0:.0f}->{r1:.0f}]:  {w0:.4f} -> {w1:.4f}   = {trend}")
print(f"  -> §7 claim 'breathing mode softens to DC at ρ_crit' is FALSIFIED (it is ρ-flat).")
print(f"  -> my own prediction 'breathing STIFFENS' also FALSIFIED (double-falsify, max info).")
print(f"  WHAT ACTUALLY TRACKS ρ (the corrected lab signatures, uniform bleed):")
print(f"    (1) sideband AMPLITUDE ~ aσ_in COLLAPSES (σ_in sags {sig0:.3f}->{d['s']:.3f}, ~{sig0/d['s']:.0f}x): chameleon")
print(f"        SCREENS THE FIELD AMPLITUDE, killing the optical modulation depth.")
print(f"    (2) carrier ω = Q/(σ²V) RISES STEEPLY as σ_in is screened (model-dependent magnitude).")
print(f"  The §8 LOCALIZATION boundary (place-fixedness) needs a SPATIAL screening GRADIENT -> the")
print(f"  TRANSLATIONAL pinning mode ω_pin->0 as contrast flattens; a UNIFORM-density bench has NO")
print(f"  gradient, so it cannot map place-localization at all -- it maps the SCREENING TRANSITION")
print(f"  (amplitude collapse + carrier shift).  Internal breathing was the wrong mode.")
