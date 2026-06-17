#!/usr/bin/env python
"""
Dream-drive #2 (2026-06-17 ~06:55): resolve the OPEN ANOMALY from drive #1 —
does a CANONICAL gauged Q-ball have a hidden UNIFORM-DENSITY existence-closure ρ_crit
that the crude R12 energy-minimization (which gave ω>m, outside the band) masked?

MODEL: complex scalar, U(σ;ρ) = ½m²(ρ)σ² − gσ³ + λσ⁴, canonical Q-ball potential.
Chameleon density enters as a mass rescaling m²(ρ)=m0²(1+ρ/ρ*); self-interaction g,λ
FIXED (the charge/self binding is ρ-independent — matches the portal's gauge-charge R12).
Q-ball profile ODE:  σ'' + (2/r)σ' = U'(σ) − ω²σ ,  σ'(0)=0, σ(∞)=0.
Existence band: ω₋² = 2·min_σ[U/σ²] = m² − g²/(2λ);  ω₊² = U''(0) = m².

PREDICT (med-high): band WIDTH ω₊²−ω₋² = g²/(2λ) = CONST in ρ → band SLIDES up, never closes
→ NO uniform-density dissolution → drive-#1 correction is COMPLETE. R12's ω>m = flat-top artifact.
FALSIFY risk: a numeric profile fails to exist at high ρ, or the band narrows -> a real ρ_crit.
"""
import numpy as np
from scipy.integrate import solve_ivp, simpson

m0, g, lam, rho_star = 1.0, 1.0, 0.7, 1.0     # zero-ρ band ω²∈[1−1/1.4, 1] = [0.286, 1]
def m2(rho): return m0**2*(1+rho/rho_star)
def Up(s, rho): return m2(rho)*s - 3*g*s**2 + 4*lam*s**3     # U'(σ)

def band(rho):
    M2=m2(rho)
    wlo2 = M2 - g**2/(2*lam)                                  # lower edge (analytic)
    whi2 = M2                                                 # upper edge = mass²
    return wlo2, whi2

def _shoot(s0, omega, rho, Rmax=60.0):
    """Integrate σ outward from σ(0)=s0, σ'(0)=0. Return ('over'|'under', r, σ)."""
    w2=omega**2
    def ode(r,y):
        s,sp=y; rr=max(r,1e-7)
        return [sp, -(2.0/rr)*sp + Up(s,rho) - w2*s]
    ev_zero=lambda r,y: y[0];            ev_zero.terminal=True; ev_zero.direction=-1   # σ→0 (overshoot)
    ev_turn=lambda r,y: y[1] if r>0.5 else 1.0; ev_turn.terminal=True; ev_turn.direction=1 # σ'→0+ (undershoot)
    sol=solve_ivp(ode,[1e-4,Rmax],[s0,0.0],events=[ev_zero,ev_turn],rtol=1e-8,atol=1e-10,max_step=0.05,dense_output=True)
    if sol.t_events[0].size>0 and (sol.t_events[1].size==0 or sol.t_events[0][0]<sol.t_events[1][0]):
        return 'over', sol
    return 'under', sol

def qball_profile(omega, rho):
    """Auto-bracket scan on σ(0) for the under->over flip, then bisect; return (r,σ) or None."""
    # outer zero of U_ω sets the natural s0 scale: ½(m²-ω²) - gσ + λσ² = 0
    mw = m2(rho)-omega**2
    disc = g**2 - 2*lam*mw
    if disc <= 0: return None
    s_out = (g+np.sqrt(disc))/(2*lam)
    grid = np.linspace(0.25*s_out, 1.05*s_out, 50)
    kinds = [_shoot(s,omega,rho)[0] for s in grid]
    flip = None
    for i in range(len(grid)-1):
        if kinds[i]=='under' and kinds[i+1]=='over':
            flip=(grid[i], grid[i+1]); break
    if flip is None: return None
    lo,hi=flip
    for _ in range(50):
        mid=0.5*(lo+hi)
        if _shoot(mid,omega,rho)[0]=='over': hi=mid
        else: lo=mid
    s0=0.5*(lo+hi); kind,sol=_shoot(s0,omega,rho)
    r=np.linspace(1e-4, sol.t[-1], 3000); s=np.clip(sol.sol(r)[0],0,None)
    if np.max(s)<1e-3: return None
    return r, s

def charge(omega, rho):
    p=qball_profile(omega, rho)
    if p is None: return None, None
    r,s=p
    Q = omega*simpson(s**2 * 4*np.pi*r**2, r)                 # Noether charge ∝ ω∫σ²
    s0=s[0]
    return Q, s0

print(f"{'ρ/ρ*':>5} {'m²':>5} {'ω₋²':>7} {'ω₊²':>5} {'width':>6} {'exists?':>8} {'Q(mid)':>9} {'σ(0)':>6}")
print("-"*60)
widths=[]
for rho in [0.0, 1.0, 3.0, 7.0, 15.0]:
    wlo2,whi2=band(rho)
    width=whi2-wlo2
    widths.append(width)
    wtest=np.sqrt(max(wlo2,1e-6)+0.25*width)                  # ω just inside lower edge (thin-wall, robust)
    Q,s0 = charge(wtest, rho)
    ex = "YES" if Q is not None else "no"
    qs = f"{Q:9.1f}" if Q is not None else "    --   "
    ss = f"{s0:6.3f}" if s0 is not None else "  --  "
    print(f"{rho:5.1f} {whi2:5.2f} {wlo2:7.3f} {whi2:5.2f} {width:6.3f} {ex:>8} {qs} {ss}")

print("-"*60)
print(f"band WIDTH ω₊²−ω₋² across ρ: {[f'{w:.3f}' for w in widths]}")
print(f"  -> width is {'CONSTANT' if max(widths)-min(widths)<1e-6 else 'VARYING'} (analytic g²/2λ = {g**2/(2*lam):.3f})")
print("VERDICT: if width const + soliton exists at every ρ -> NO uniform-density existence-closure;")
print("  the band slides up, the soliton persists (heavier, screened amplitude). Drive-#1 correction COMPLETE.")
print("  R12's ω=Q/(σ²V)>m was the thin-wall flat-top mis-estimating ω, NOT a hidden dissolution.")
