#!/usr/bin/env python
"""
Fixed-Q carrier curve ω(ρ) — the PHYSICAL bleed (2026-06-17, Clayton-collaborative).

canonical-qball-existence-2026-06-17.py proved the existence band slides rigidly (width g²/2λ
const, no closure) — but it sampled ω at a FIXED FRACTION inside the band, so σ(0) came out
ρ-invariant by construction. That is not the physical experiment. A gauged soliton conserves its
Noether charge Q (charge cannot leak); the band slides up with ρ, so to hold Q the carrier must
ride to a new ω(ρ) — the carrier BLUESHIFTS.

Why it matters: ω_pin (place-localization) needs a SPATIAL GRADIENT; the breathing mode came up
FLAT. But the carrier-frequency blueshift is readable on a plain UNIFORM-density bench (the 556 GHz
line moving). So this tests whether the parked self-calibrating densitometer (Phase D) is
resurrectable in a gradient-free form: read ρ off the carrier blueshift at fixed Q.

Model identical to the canonical script: complex scalar, U=½m²(ρ)σ²−gσ³+λσ⁴, chameleon mass
m²(ρ)=m0²(1+ρ/ρ*), self-interaction (g,λ) ρ-independent. Q-ball ODE σ''+(2/r)σ'=U'(σ)−ω²σ.
Band ω₋²=m²−g²/2λ, ω₊²=m². Carrier scale: ω=m0 ↔ f=mc²/h=556 GHz.

OUTPUT: ω(ρ) at fixed Q; carrier f(ρ); densitometer sensitivity S=(dω/ω)/(dρ/ρ); does the
fixed-Q soliton persist at every ρ.
"""
import numpy as np
from scipy.integrate import solve_ivp, simpson

m0, g, lam, rho_star = 1.0, 1.0, 0.7, 1.0
F0_GHZ = 556.0   # carrier f at ω=m0 (R16: mc²/h)


def m2(rho):
    return m0**2 * (1 + rho / rho_star)


def Up(s, rho):
    return m2(rho) * s - 3 * g * s**2 + 4 * lam * s**3


def band(rho):
    M2 = m2(rho)
    return M2 - g**2 / (2 * lam), M2          # ω₋², ω₊²


def _shoot(s0, omega, rho, Rmax=60.0):
    w2 = omega**2

    def ode(r, y):
        s, sp = y
        rr = max(r, 1e-7)
        return [sp, -(2.0 / rr) * sp + Up(s, rho) - w2 * s]
    ev_zero = lambda r, y: y[0]
    ev_zero.terminal = True
    ev_zero.direction = -1
    ev_turn = lambda r, y: y[1] if r > 0.5 else 1.0
    ev_turn.terminal = True
    ev_turn.direction = 1
    sol = solve_ivp(ode, [1e-4, Rmax], [s0, 0.0], events=[ev_zero, ev_turn],
                    rtol=1e-8, atol=1e-10, max_step=0.05, dense_output=True)
    if sol.t_events[0].size > 0 and (sol.t_events[1].size == 0 or sol.t_events[0][0] < sol.t_events[1][0]):
        return 'over', sol
    return 'under', sol


def qball_profile(omega, rho):
    mw = m2(rho) - omega**2
    disc = g**2 - 2 * lam * mw
    if disc <= 0:
        return None
    s_out = (g + np.sqrt(disc)) / (2 * lam)
    grid = np.linspace(0.25 * s_out, 1.05 * s_out, 50)
    kinds = [_shoot(s, omega, rho)[0] for s in grid]
    flip = None
    for i in range(len(grid) - 1):
        if kinds[i] == 'under' and kinds[i + 1] == 'over':
            flip = (grid[i], grid[i + 1])
            break
    if flip is None:
        return None
    lo, hi = flip
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if _shoot(mid, omega, rho)[0] == 'over':
            hi = mid
        else:
            lo = mid
    s0 = 0.5 * (lo + hi)
    _, sol = _shoot(s0, omega, rho)
    r = np.linspace(1e-4, sol.t[-1], 3000)
    s = np.clip(sol.sol(r)[0], 0, None)
    if np.max(s) < 1e-3:
        return None
    return r, s


def charge(omega, rho):
    p = qball_profile(omega, rho)
    if p is None:
        return None
    r, s = p
    return omega * simpson(s**2 * 4 * np.pi * r**2, r)


def omega_at_fixed_Q(Q_target, rho, n_grid=22):
    """Find ω in (ω₋,ω₊) with charge(ω,ρ)=Q_target. Q(ω) is monotone-decreasing across the band
    (large near ω₋, →0 near ω₊), so grid-sample then linear-interpolate the crossing (robust to
    edge profile-solve failures)."""
    wlo2, whi2 = band(rho)
    wlo, whi = np.sqrt(max(wlo2, 1e-6)), np.sqrt(whi2)
    ws = np.linspace(wlo + 0.02 * (whi - wlo), whi - 0.02 * (whi - wlo), n_grid)
    Qs = [charge(w, rho) for w in ws]
    pts = [(w, q) for w, q in zip(ws, Qs) if q is not None]
    if len(pts) < 2:
        return None
    wv = np.array([p[0] for p in pts])
    qv = np.array([p[1] for p in pts])
    # need Q_target bracketed by the achievable charge range at this ρ
    if Q_target > qv.max() or Q_target < qv.min():
        return None
    # interpolate ω as a function of Q (qv is descending in w; sort by Q ascending for interp)
    order = np.argsort(qv)
    return float(np.interp(Q_target, qv[order], wv[order]))


if __name__ == "__main__":
    rhos = [0.0, 0.5, 1.0, 2.0, 4.0, 8.0, 15.0]
    print("Fixed-Q carrier curve ω(ρ) — the physical bleed (charge conserved, band slides up)")
    print("=" * 78)
    for Q_target in [80.0, 150.0, 300.0]:
        print(f"\n[Q = {Q_target:.0f}]  {'ρ/ρ*':>5} {'ω':>7} {'ω₊=m':>7} {'in-band?':>9} "
              f"{'f (GHz)':>9} {'Δf vs ρ0':>10}")
        f0 = None
        curve = []
        for rho in rhos:
            w = omega_at_fixed_Q(Q_target, rho)
            if w is None:
                print(f"        {rho:5.1f} {'--':>7} {np.sqrt(band(rho)[1]):7.3f}  "
                      f"{'NO SOLN':>9}")
                continue
            mphys = np.sqrt(band(rho)[1])
            f = w * F0_GHZ
            if f0 is None:
                f0 = f
            curve.append((rho, w))
            print(f"        {rho:5.1f} {w:7.4f} {mphys:7.3f} {'yes':>9} "
                  f"{f:9.1f} {f - f0:+10.1f}")
        # densitometer sensitivity S = (dω/ω)/(dρ/ρ), central differences on the interior points
        if len(curve) >= 3:
            rr = np.array([c[0] for c in curve])
            ww = np.array([c[1] for c in curve])
            # use a representative interior point (ρ≈1) for S
            ints = []
            for i in range(1, len(rr) - 1):
                if rr[i] <= 0:
                    continue
                dwdrho = (ww[i + 1] - ww[i - 1]) / (rr[i + 1] - rr[i - 1])
                S = (rr[i] / ww[i]) * dwdrho
                ints.append((rr[i], S))
            if ints:
                s_str = "  ".join(f"ρ={r:.0f}:S={s:.2f}" for r, s in ints)
                print(f"        sensitivity S=(dω/ω)/(dρ/ρ): {s_str}")

    print("\n" + "=" * 78)
    print("READ: if ω(ρ) rises smoothly (carrier blueshifts) AND the soliton persists at every ρ,")
    print("the carrier frequency is a UNIFORM-BENCH densitometer (no gradient, no breathing mode).")
    print("S~O(1) => fractional freq shift ≈ fractional density change = comfortably resolvable.")
    print("S<<1 => carrier too stiff to read ρ; S>>1 => exquisitely sensitive (and band-edge risk).")
