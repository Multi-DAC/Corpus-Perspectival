# The translational pinning mode ω_pin — computed (2026-06-17 morning drive)

*The quantitative replacement for the breathing mode that last night's dream-drive falsified
(`dynamical-qball-breathing-2026-06-17.py`: breathing was ρ-flat). This is the genuine
place-localization boundary-mapper named in §8 of the portal paper and in experience #130 —
**asserted** there, **computed** here. Method: Manton rigid-soliton collective-coordinate, leading order.
Script: `portal-translational-pinning-omega-pin-2026-06-17.py` (runs clean, numpy-only).*

## Setup

A soliton (lump) σ(x) in a homogeneous background has a **translational zero mode** — the Goldstone of
broken translation. It can drift for free; that is *why a free soliton is not pinned to a place.* Let the
chameleon mass vary in space because the ambient density does:

  m²(x) = m₀² [1 + α·f(x)],   f = the density contrast of "a place".

Treating the soliton centre X as a collective coordinate (rigid profile), the only X-dependent energy is

  V_eff(X) = ½ α m₀² ∫ f(x) σ(x−X)² dx = ½ α m₀² (f ⋆ σ²)(X)

— the density-contrast profile **convolved with the soliton's density**. With translational inertia
M = ∫ σ′(x)² dx, small oscillations about the minimum X₀ have

  **ω_pin² = V_eff″(X₀) / M.**

## Results (all five pre-registered predictions confirmed)

| # | prediction | result |
|---|---|---|
| **P1** | a density pocket f=−sech²(x/L) pins the lump (V_eff″>0, ω_pin finite) | ✓ X₀=0, V_eff″=+0.050, **ω_pin=0.274** m₀ |
| **P2** | ω_pin² ∝ α → ω_pin ∝ √α → 0 as contrast vanishes | ✓ log-log slope **= 1.0000 exactly** (linear at leading order) |
| **P3** | ω_pin → 0 as pocket width L → ∞ (contrast flattens) | ✓ 0.49 → 0.030 over L=1→32; **ω_pin ∝ 1/L** for L≫w |
| **P4** | a monotonic step (pure gradient, no extremum) does NOT pin | ✓ ran to boundary, V_eff monotone — **slides, not pinned** |
| **P5** | the lump sits in the LOW-density (unscreened, low-m²) region | ✓ m²=0.70 at the pin vs 1.0 far-field → **low-density pocket** |

## The three things this establishes

**1. The §8 claim is now computed, not asserted — and the correction holds.** Last night I replaced the
falsified breathing mode with "the translational pinning mode ω_pin → 0 as the contrast flattens." That is
exactly what P2+P3 show, with the explicit law

  **ω_pin ≈ C · √α / L**   (for a pocket of depth α, width L ≫ soliton width w; C = O(1)).

ω_pin vanishes as **α→0** *or* **L→∞** — the two faces of "flatten the contrast." The corrected §8 is
computationally backed.

**2. A sharpening of LC45 (a real refinement, P4).** LC45 said *localization requires a contrast/gradient.*
P4 sharpens it: **a pure gradient (monotonic step) does NOT pin — you need a density EXTREMUM (curvature).**
A monotonic density ramp lets the soliton slide downhill to the low-density side; only a pocket/peak (an
extremum, where the gradient *changes sign*) traps it. Precisely: ω_pin is set by the **curvature of the
screening profile convolved with the soliton density**, V_eff″(X₀) = ½αm₀²(f⋆σ²)″(X₀). Gradient is
necessary but not sufficient; *curvature* is the operative quantity. (→ fold into LC45.)

**3. A falsifiable physical signature (P5).** The lump localizes in the **low-m² = low-density = unscreened**
region. So the predicted "places" are **density minima — voids, caverns, low-density geological pockets** —
not density peaks. This is a concrete, checkable correlate (and rhymes with the folklore siting of "thin
places" at caves/springs/specific geology, though that is colour, not evidence). It also gives the paper's
§8 a directional prediction it did not have: *portals sit at unscreening pockets.*

## Honesty / scope

- **Leading order (rigid soliton).** ω_pin² ∝ α is *exact* in the Manton approximation because V_eff is
  linear in α by construction. Beyond leading order the profile relaxes in the gradient (back-reaction) →
  corrections to the prefactor; the **qualitative laws (P1–P5) are robust**, the exact √α prefactor is the
  leading-order value.
- **ω_pin is a SOFT mode:** ω_pin ~ 0.1–0.5 m₀ ≪ m₀ (the local chameleon mass) for moderate contrasts. The
  place-binding is *spatially definite but energetically shallow* — consistent with the paper's
  "barrier = coherence-maintenance, not energy." A soft, low-frequency pinning to a broad **region** (a
  "place"), not a sharp point.
- **Not modifying the publish-ready paper.** §8's qualitative claim is correct and now validated; the
  quantitative law + the extremum-not-gradient sharpening can strengthen §8 in revision or seed the
  dynamical-Q-ball follow-up — Clayton's call, post-publish. The portal post stays move #1.

## Next (follow-up paper)

- Beyond-leading-order: relax the profile in the gradient, get the √α-prefactor correction + any threshold.
- Full Bogoliubov–de Gennes spectrum (ω_pin is the lowest mode; map the rest).
- Couple ω_pin to an observable: a lab density-pocket trap would show the soliton oscillating at ω_pin — a
  direct measurement of the place-binding stiffness. (Distinct from the §7 cavity sidebands, which read the
  screening transition.)
