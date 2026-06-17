# Fixed-Q carrier curve — the densitometer jewel resurrected, gradient-free (2026-06-17, Clayton-collaborative)

**Result of `portal-fixedQ-carrier-2026-06-17.py`** — the physically-correct follow-up to the canonical
existence check. The canonical script (`canonical-qball-existence-2026-06-17.py`) sampled ω at a fixed
fraction *inside* the band, so σ(0) came out ρ-invariant by construction. The physical experiment fixes
the conserved **Noether charge Q** (charge cannot leak from a gauged soliton) and lets the carrier ride
the sliding band: ω(ρ) is found by root-finding charge(ω,ρ)=Q.

## Numbers (toy potential m0=1, g=1, λ=0.7, chameleon m²=m0²(1+ρ/ρ*); carrier f: ω=m0 ↔ 556 GHz)

| Q | f(ρ/ρ*=0) | f(ρ/ρ*=15) | in-band every ρ? |
|---|---|---|---|
| 80  | 383 GHz | 2202 GHz | yes |
| 150 | 365 GHz | 2195 GHz | yes |
| 300 | no soln @ρ0 (band can't hold Q) | 2190 GHz | yes for ρ≥0.5 |

Sensitivity S=(dω/ω)/(dρ/ρ) ≈ 0.27→0.46 (rises with ρ).

## Three findings
1. **Fixed-Q soliton PERSISTS at every ρ** — no fixed-Q dissolution. Confirms the no-closure verdict in
   the physically-correct frame (conserved charge), agreeing with the band-relative canonical result.
2. **Carrier blueshifts smoothly + monotonically** — hundreds of GHz per unit ρ/ρ*. A UNIFORM-bench
   observable: the line moves as you bleed. No spatial gradient (unlike ω_pin), no breathing mode (flat).
3. **S≈0.3–0.45 is the sweet spot** — sub-unity ⇒ stiff/stable (no band-edge runaway), yet absolute
   shifts are tens–hundreds of GHz ⇒ trivially resolved by a sub-mm spectrometer. A stable, monotonic,
   easily-read densitometer.

**Phase D (the parked self-calibrating bleed-valve densitometer) is resurrected in the gradient-free form
the breathing mode couldn't provide:** read ρ off the carrier blueshift at fixed Q, on a uniform-density
bench. Candidate 4th lab channel + the cheapest experimental handle on the whole portal-carrier picture.

## Discipline wall
Toy potential — the MECHANISM is verified (persistence; smooth monotone blueshift; workable sub-unity
sensitivity), NOT the literal GHz, which rescale with the real dark-energy-scale (a, ρ*) parameters.
Next if pursued: redo with the screened-scalar parameters from the paper (R12/R16) for quantitative f(ρ),
and fold into the Phase C cavity-gain (Mathieu) calc for an SNR/finesse map. Related:
[[portal-dynamical-qball-FOLLOWUP-SEED-2026-06-17]], `canonical-qball-existence-2026-06-17.py`.
