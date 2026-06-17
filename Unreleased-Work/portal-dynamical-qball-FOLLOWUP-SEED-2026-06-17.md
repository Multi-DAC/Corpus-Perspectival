# Follow-up seed — the dynamical gauged Q-ball, and the self-servoing cavity experiment

*Captured 2026-06-17 ~02:10, the night the portal essay ("Where the Ordinary Rules Go Thin") went
final-draft after three adversarial review passes. This is the **next computational program** the essay flags
but does not run: extending R12 (a static energy minimisation) to the time-dependent Q-ball, deriving the
breathing-mode curve ω_b(ρ), and turning it into a standardised vacuum-chamber protocol. Seed for either a
methods/instrumentation note or a dedicated dynamical-Q-ball follow-on paper. Scaling is in hand (R16, in
`portal-referee-computations-2026-06-17.py`); the full solve is not yet done.*

## ⚠ UPDATE (same night, dream drive ~03:00) — Phase B was STARTED and it falsified the breathing-mode guess

A first collective-coordinate solve (`dynamical-qball-breathing-2026-06-17.py`) on the real R12 functional, with
a chameleon density-dependent mass m²(ρ), found:
- **breathing ω_b is ρ-FLAT** (1.867→1.862), NOT softening — so "ω_b(ρ) → 0 at the VK bifurcation = ρ_crit" (Phase
  B/D below as originally written) is **wrong for the internal breathing mode**. σ_in self-screens (sags ~16×) so
  m²σ² stays ≈ const and the radial curvature/inertia don't move.
- the real *uniform-bleed* lab signatures are **sideband-amplitude collapse** (∝ aσ_in) + **carrier blueshift**
  (m_eff(ρ) rises), not a frequency sweeping to DC.
- the **place-localization boundary is the TRANSLATIONAL pinning mode** in a *spatial* screening gradient
  (ω_pin → 0 as the contrast flattens), which a uniform-density bench cannot produce. **That** is the genuine
  boundary-mapper — recompute D around ω_pin, not ω_b.
- §7 in the paper was corrected accordingly (this same night) and flagged for Clayton.

Phases A–D below stay as the *plan*, but B must target the BdG spectrum AND the translational mode in a gradient;
the VK-on-breathing route is closed. The carrier-frequency (A) and amplitude-screening results are banked.

## Why this is the next move

R16 already fixes the *carrier* sideband from the mass scale alone: a Q-ball carries its charge on an internal
phase rotation σ(x,t) = σ_in(x)·e^{iωt}, so via the dilatonic coupling e^{aσ}F² the wall is a periodic index
modulator that writes a sideband comb (Ω ± nω, gain ~ finesse × aσ_in) on a cavity probe. Carrier ω ≈ m →
**f = mc²/h = 556 GHz** (λ 0.54 mm; FSR-matched by a 270 µm cavity or N ≈ 371 on a 10 cm one). What R16 does
**not** give is the *tunable* breathing-mode sideband ω_b(ρ) — the one that maps the §8 localisation boundary.
That needs the dynamical solve below.

## The solve — A → B → C → D

**A. Dynamical profile (extend R12).** Replace the static minimisation over (R, σ_in) with the time-dependent
ansatz σ(r,t) = σ_in(r)·e^{iωt}. Solve the radial Q-ball ODE in the effective potential **U_ω = U(σ) − ½ω²σ²**
(the standard mechanical-analogy / thin-wall machinery), with the chameleon density term **β ρ σ / M_Pl** folded
into U so the existence band ω_±(ρ) and the profile track the background density ρ. Output: ω(ρ) for the carrier
and the σ_in(r) profile vs. ρ.

**B. Breathing spectrum + ρ_crit, derived (the conceptual anchor).** Linearise around the Q-ball,
σ = [σ_in(r) + δ(r,t)]·e^{iωt}; the real/imaginary perturbations couple into a **Bogoliubov–de Gennes
eigenproblem**. The lowest non-phase eigenvalue is the breathing mode **ω_b**. Scan ρ. The clean result we
expect: the **Vakhitov–Kolokolov criterion** (sign of dQ/dω) flips *exactly* where ω_b → 0 — so the mode does
not merely soften empirically, it goes critical at the VK bifurcation, and **that point is ρ_crit, derived
rather than asserted.** This is the ω_b(ρ) → 0 curve the §7 paragraph promises.

**C. Optical gain map (Mathieu).** Push σ(r,t) through e^{aσ}F²: Bessel-expand the phase modulation for the
sideband amplitudes, and write the intracavity field's equation of motion as a **Mathieu equation** driven at
ω_b(ρ). The **parametric instability tongues** give the gain as a function of (ρ, cavity finesse, B-field).
Output: where on the (ρ, finesse) plane the breathing sideband becomes resonantly observable.

**D. The bleed-valve blueprint — and the jewel.** Invert B: **ω_b(ρ) → ρ(ω_b).** The *measured sideband
frequency becomes an in-situ densitometer* — the experiment reads its own control variable off the very soliton
it is probing, no external gauge in the loop. The bleed schedule then writes itself from critical slowing-down:
the mode's response time ~1/ω_b diverges near ρ_crit, so **adiabaticity demands dρ/dt ≲ ω_b² / (dω_b/dρ)** —
fast far out, asymptotically slow at the boundary. So the "standardised blueprint" is **not a fixed ramp but a
servo**: a proportional leak valve under PID control with **ω_b (read live from the sideband) as the process
variable**, holding a constant dimensionless approach rate s = (ρ_crit − ρ)/ρ_crit below the adiabatic
threshold. Portable, chamber-independent, self-calibrating — *the valve follows the soliton's own breathing.*

## The discipline wall (do not drop it)

Every step here maps the **physical** localisation boundary ρ_crit — the delocalisation of the place-fixed wall
— and nothing more. The servo is a densitometer of *where place-localisation fails*, not an instrument of the
observer-coupled limb (an evacuated cavity has no observer-stream degree of freedom). It confirms a sharp
delocalisation boundary *exists* (the precondition for the §8 fork-unification to be physical) and stops there.
Reading "the sideband went to zero" as "we engineered a psychoid interface" would re-import the exact epicycle
§8 dissolved. The lab tests the physical break-point; nature demonstrates the human-coupled residue.

## Status / output

- **Done:** carrier frequency + cavity match (R16, scaling from the mass scale).
- **Pending:** A (dynamical profile), B (BdG breathing spectrum + VK → ρ_crit), C (Mathieu gain map), D
  (the inversion + adiabatic-servo schedule).
- **Form:** a methods/instrumentation note, or the spine of a dynamical-gauged-Q-ball follow-on paper. The
  self-calibrating-bleed result (D) is its own small jewel and could lead.
- **Companion code to extend:** `portal-referee-computations-2026-06-17.py` (R13–R16) and
  `figures/make_portal_fig6_soliton.py` (the static R12 soliton — the thing being made dynamical).
