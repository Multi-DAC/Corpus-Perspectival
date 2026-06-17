"""
Portal gauged-soliton existence — v2 (proper thin-wall gauged DILATONIC Q-ball).
Day 136 creative drive. v1 (free static charge) FALSIFIED: the soliton dispersed (R->inf, E->0)
because free charge has no binding. The fix is the Q-ball mechanism: the charge is carried by a
massive complex scalar phi, whose charge-kinetic energy omega^2 f^2 -> Q^2/Volume DIVERGES as the
carrier spreads, binding it. That term was missing. Add it -> the soliton should exist.

Thin-wall energy at fixed Noether charge Q (carrier amplitude f0=v fixed; V=(4/3)pi R^3):
  E_surface = 4 pi R^2 * S1                      (carrier-field wall tension)
  E_volume  = V * U0                             (carrier potential energy density inside, >0)
  E_charge  = Q^2 / (2 V f0^2)                   (charge-kinetic: the Q-ball binding term; ~Q^2/R^3)
  E_EM      = c_em * Q^2 / (R * exp(a*sig_in))   (electrostatic self-energy, dilatonically modified)
  E_radion  = V * 0.5 m^2 sig_in^2  +  4 pi R^2 * k_sig * sig_in^2   (radion potential + wall)
Minimize over (R, sig_in) at fixed Q, a. Finite interior minimum => EXHIBITED soliton.
Units: m=1, f0=v=1, choose S1,U0,c_em,k_sig ~ O(1).
"""
import numpy as np
from scipy.optimize import minimize_scalar, minimize

m = 1.0; f0 = 1.0
S1 = 0.5      # wall tension
U0 = 0.3      # interior potential energy density (Q-ball requires >0)
c_em = 1.0/(8*np.pi)   # EM self-energy constant
k_sig = 0.1   # radion wall stiffness

def vol(R): return (4.0/3.0)*np.pi*R**3

def Eparts(R, sig_in, Q, a):
    V = vol(R)
    E_surf = 4*np.pi*R**2 * S1
    E_vol  = V * U0
    E_chg  = Q**2 / (2*V*f0**2)
    E_em   = c_em * Q**2 / (R * np.exp(a*sig_in))
    E_rad  = V * 0.5*m**2*sig_in**2 + 4*np.pi*R**2 * k_sig * sig_in**2
    return E_surf, E_vol, E_chg, E_em, E_rad

def Etot(x, Q, a):
    R, sig_in = x
    if R <= 1e-3: return 1e12
    return sum(Eparts(R, sig_in, Q, a))

def soliton(Q, a, x0=(2.0, 0.2)):
    res = minimize(Etot, x0, args=(Q, a), method="Nelder-Mead",
                   options=dict(xatol=1e-6, fatol=1e-9, maxiter=8000))
    R, sig = res.x
    parts = Eparts(R, sig, Q, a)
    return dict(R=R, sig=sig, E=sum(parts), parts=parts, ok=res.success)

if __name__ == "__main__":
    print("Gauged DILATONIC Q-ball — v2 (with the binding charge-kinetic term)")
    print("="*72)

    print("\n[1] E(R) at sig_in=0.2, Q=10, a=0.5 (both ends should diverge -> interior min):")
    for R in [0.3,0.5,0.8,1.0,1.5,2,3,5,8]:
        Es,Ev,Ec,Eem,Er = Eparts(R,0.2,10.0,0.5)
        print(f"   R={R:4.1f}  surf={Es:6.2f} vol={Ev:7.2f} chg={Ec:7.2f} em={Eem:6.2f} rad={Er:6.2f}"
              f"  Etot={Es+Ev+Ec+Eem+Er:8.2f}")

    print("\n[2] EXHIBITED soliton vs charge Q (a=0.5):")
    print(f"   {'Q':>5} {'R*':>7} {'sig_in':>8} {'E*':>9} {'E/Q':>7}  (E_surf E_vol E_chg E_em E_rad)")
    Qs=[5,10,20,40,80,160]; Rs=[]; Es=[]
    for Q in Qs:
        d=soliton(Q,0.5); Rs.append(d['R']); Es.append(d['E'])
        p=d['parts']
        print(f"   {Q:5.0f} {d['R']:7.3f} {d['sig']:8.4f} {d['E']:9.2f} {d['E']/Q:7.3f}  "
              f"({p[0]:.1f} {p[1]:.1f} {p[2]:.1f} {p[3]:.1f} {p[4]:.2f})")
    pR=np.polyfit(np.log(Qs),np.log(Rs),1)[0]
    pE=np.polyfit(np.log(Qs),np.log(Es),1)[0]
    print(f"\n   size   R* ~ Q^{pR:.3f}   (thin-wall expectation ~Q^(1/3)=0.333)")
    print(f"   energy E* ~ Q^{pE:.3f}   (Q-ball expectation ~Q^1 linear)")

    print("\n[3] Dilatonic coupling: does sigma sag to lower energy? (Q=40)")
    print(f"   {'a':>5} {'R*':>7} {'sig_in':>8} {'E*':>9}  dilaton effect")
    E_a0=None
    for a in [0.0,0.5,1.0,2.0,3.0]:
        d=soliton(40.0,a)
        if a==0.0: E_a0=d['E']
        dE = 100*(d['E']-E_a0)/E_a0 if E_a0 else 0.0
        print(f"   {a:5.1f} {d['R']:7.3f} {d['sig']:8.4f} {d['E']:9.2f}  {dE:+6.2f}% vs a=0")

    print("\n[4] Robustness: does a finite soliton persist as U0 -> 0 (flat carrier potential)?")
    for U0v in [0.5,0.3,0.1,0.03,0.0]:
        U0=U0v
        d=soliton(40.0,0.5)
        print(f"   U0={U0v:4.2f}  R*={d['R']:7.3f}  E*={d['E']:8.2f}  sig={d['sig']:7.4f}")
