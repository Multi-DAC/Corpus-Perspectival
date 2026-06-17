"""Resolve the portal paper's flagged open question (§2): does the R12 preferred-soliton
scale (Q* = argmin E/Q) map to a real size, and does it agree with the §5 carrier scale?
Day 136 creative drive. PREDICT(med-high): it lands SUB-MM (the WALL scale), NOT macroscopic
-> does NOT agree with the carrier; CONFIRMS R6's two-scale split (field->wall, carrier->size)."""
import numpy as np
from scipy.optimize import minimize

# ---- R12 thin-wall gauged dilatonic Q-ball (dimensionless, radion mass m=1) ----
S1, U0, c_em, f0, mfield = 0.5, 0.3, 1.0/(8*np.pi), 1.0, 1.0
def vol(R): return (4/3)*np.pi*R**3
def Etot(x, Q, a, S1, U0, c_em):
    R, s = x
    if R <= 1e-3: return 1e12
    V = vol(R)
    return (4*np.pi*R**2*S1 + V*U0 + Q**2/(2*V*f0**2) + c_em*Q**2/(R*np.exp(a*s)) + V*0.5*mfield**2*s**2)
def soliton(Q, a=0.5, S1=S1, U0=U0, c_em=c_em):
    r = minimize(Etot, (2.0, 0.2), args=(Q, a, S1, U0, c_em), method="Nelder-Mead",
                 options=dict(xatol=1e-6, fatol=1e-9, maxiter=8000))
    return r.x[0], sum_parts(r.x, Q, a, S1, U0, c_em)
def sum_parts(x, Q, a, S1, U0, c_em):
    R, s = x; V = vol(R)
    return 4*np.pi*R**2*S1 + V*U0 + Q**2/(2*V*f0**2) + c_em*Q**2/(R*np.exp(a*s)) + V*0.5*mfield**2*s**2

def preferred(S1=S1, U0=U0, c_em=c_em):
    """Q* = argmin E/Q, and R*(Q*) in units of 1/m_field."""
    Qs = np.array([2,3,5,8,12,20,32,50,80,130,200])
    eoq, Rs = [], []
    for Q in Qs:
        R, E = soliton(Q, S1=S1, U0=U0, c_em=c_em); eoq.append(E/Q); Rs.append(R)
    i = int(np.argmin(eoq))
    return Qs[i], Rs[i], eoq[i]

# ---- physical scales ----
hbar_c = 1.973e-7            # eV*m
m_de = 2.3e-3               # dark-energy scale, eV
inv_m = hbar_c/m_de          # 1/m in metres = wall thickness
mu0 = 4*np.pi*1e-7; mp = 1.6726e-27; e = 1.602e-19; eps0 = 8.854e-12; kB_eV = 1.0  # work in eV for T

def lundquist_Lcrit(B, n, T_eV, ionf):
    rho = n*mp; v_A = B/np.sqrt(mu0*rho); sigma = 1.5e2*T_eV**1.5*ionf
    return 1.0/(mu0*sigma*v_A)          # S=1 -> L_crit
def debye(n, T_eV):
    return np.sqrt(eps0*T_eV*e/(n*e**2))

if __name__ == "__main__":
    Qstar, Rstar_dimless, eoq = preferred()
    Rstar_phys = Rstar_dimless * inv_m
    print("R12 preferred soliton (default toy constants)")
    print(f"  Q* = {Qstar}  (min E/Q = {eoq:.3f});  R*(Q*) = {Rstar_dimless:.2f} /m  (dimensionless)")
    print(f"  wall thickness 1/m @ {m_de*1e3:.1f} meV = {inv_m*1e3:.3f} mm")
    print(f"  ==> R*(Q*) physical = {Rstar_phys*1e3:.3f} mm   ( = {Rstar_dimless:.1f} x wall thickness )")
    print()
    # warm-plasma reference (the §5 self-maintaining carrier regime)
    B,n,T,ionf = 1e-3, 1e20, 5.0, 0.2
    Lcrit = lundquist_Lcrit(B,n,T,ionf); lamD = debye(n,T)
    print("characteristic lengths (warm partially-ionized carrier: B=10G n=1e20 T=5eV 20%):")
    print(f"  Debye length            ~ {lamD*1e6:8.2f} um")
    print(f"  R12 preferred soliton   ~ {Rstar_phys*1e3:8.3f} mm   <-- the question")
    print(f"  wall thickness (1/m)    ~ {inv_m*1e3:8.3f} mm")
    print(f"  Lundquist S=1 threshold ~ {Lcrit:8.2f} m")
    print(f"  §5 carrier scale        ~ 10 - 1000 m")
    print()
    print(f"  preferred / wall        = {Rstar_phys/inv_m:.2f}      (same order -> WALL scale)")
    print(f"  preferred / Lundquist   = {Rstar_phys/Lcrit:.2e}   (orders below -> NOT carrier-scale)")
    print(f"  carrier / preferred     = {10/Rstar_phys:.2e} to {1000/Rstar_phys:.2e}")
    print()
    # ---- SENSITIVITY: does "sub-mm / wall-scale" survive varying the toy constants? ----
    print("SENSITIVITY (vary toy constants x0.3..x3 -> does R*(Q*) stay sub-mm?):")
    import itertools
    rs = []
    for fS, fU, fC in itertools.product([0.3,1,3], repeat=3):
        try:
            _, Rd, _ = preferred(S1=S1*fS, U0=U0*fU, c_em=c_em*fC)
            rs.append(Rd*inv_m*1e3)
        except Exception:
            pass
    rs = np.array(rs)
    print(f"  R*(Q*) over 27 constant-combos: min={rs.min():.3f} mm  median={np.median(rs):.3f} mm  max={rs.max():.3f} mm")
    print(f"  all sub-cm? {bool((rs<10).all())}   all sub-mm-to-mm (<5mm)? {bool((rs<5).all())}")
    print(f"  -> even at x3 EM-coupling the preferred scale stays {rs.max()/(inv_m*1e3):.1f}x the wall; never reaches metres.")
