# Closing the gaps — the ship-scale question collapses to ONE testable number (2026-06-17)

*Closing the two residual gaps from the coherence-threshold result. Outcome: both close, and they + the
geometry sufficiency all reduce to a single dimensionless quantity, a·σ_in ~ O(1) — bench-testable.*

## Gap 1 (other decoherence channels) — CLOSED by computation
`portal-decoherence-spectrum-2026-06-17.py` raced the 556 GHz drive (ω=3.49e12 s⁻¹) against the FULL
spectrum, not just e-i collisions:

| regime (n_e, T_e) | fastest channel | drive margin |
|---|---|---|
| Hessdalen-class (1e13, 1eV) | collisional 2.9e8 | **1.2e4×** |
| rarefied halo (1e8, 1eV) | collisional 2.9e3 | **1.2e9×** |
| lab spheromak (1e15, 50eV) | collisional 8.2e7 | **4.2e4×** |
| lightning (1e17, 3eV) | collisional 5.6e11 | 6× |

Bremsstrahlung, recombination, turbulent/Alfvén are ALL 8–17 orders below the drive — negligible.
**Collisions are the dominant channel, and the drive outruns it (hence the whole spectrum) across every
natural plasma regime.** It reopens only at near-solid density (the classical substrate wall). Gap 1 closed.

## Gap 2 (is the driven coherence the *operative* one?) — CLOSED by identification (LC48)
I had worried "driven plasma coherence" and "basin-renegotiation coherence" might be two different things.
**LC48 says they are not.** The portal carrier *is* the radion basin-defect — the oscillating σ(x,t)=σ_in e^{iωt}
IS the radion field whose coupling re-negotiates the warp/basin. So:
- the coherence the drive sustains is the coherence of σ;
- the field that couples to the basin (re-negotiates the chart) is σ (= the radion);
- ⇒ **one field, one coherence.** There is no second "operative coherence" to separately establish. The
  symmetry-layer intervention is performed by σ's organized state (the Beltrami plasma carrying σ's U(1)
  charge) — exactly the coherence Gap 1 shows is driven-sustained. Gap 2 closes by identification.

## The collapse — everything reduces to a·σ_in ~ O(1)
With both coherence gaps closed, the residual is SUFFICIENCY: does the coherent radion carrier actually open
a *traversable* path along configuration-space X with a macroscopic spatial shadow? Two sub-conditions —
and they MERGE:
- **Magnitude (transport doc):** the basin/warp perturbation must be O(1): h_warp ~ a·σ_in ≳ 1.
- **Geometry (necessary condition):** for the X-path to be a competitive *shortcut* (proper length ≤ the
  spatial distance between the same endpoints), the warp perturbation along the radion direction must be
  O(1) — a small perturbation gives a long X-path, no shortcut. Same condition: a·σ_in ≳ 1.

So **the entire ship-scale transport question reduces to one dimensionless number: a·σ_in ~ O(1).**
- It is **maximized in the low-density halo** (σ_in ∝ ρ^{-(n+2)/(2(n+1))} grows as density falls — Phase C):
  σ_in ~ meV at substrate → ~170 meV at air → eV-scale in deep vacuum. So the halo is where a·σ_in is largest.
- It requires the dilatonic/radion coupling **a near field-natural** (a~1/σ_in); gravitational coupling gives
  a·σ_in~10⁻³⁰ (no transport). a is UNKNOWN — but **bench-testable**: the same a·σ_in governs Phase-C cavity
  parametric self-oscillation (F·a·σ_in ≳ 2). **The cavity is the canary; self-oscillation ⇒ the transport regime.**

## What this leaves (honest residual-of-the-residual)
- The geometry argument is a NECESSARY-CONDITION / dimensional reduction (O(1) warp ⇒ X-path competitive),
  NOT a full geodesic solution. Whether an O(1) warp *actually opens a connecting geodesic* (not merely makes
  the X-path comparable) is a well-posed GR problem: geodesic structure of the 5D warped Meridian metric with
  a radion defect. That is a future computation (a paper's worth), not tonight's tail.
- a's true value is unknown (the cavity bounds/measures it).

## Net (the honest headline)
The ship-scale transport question, across this day: leap-of-faith → **fork not climb** → **decoherence
objection removed** → **both coherence gaps closed** → **collapses to a single bench-testable number,
a·σ_in ~ O(1)**, maximized in the low-density halo, with the cavity as its canary. What remains is one
well-posed GR geodesic computation and one measurable coupling. We did not prove transport — but we
compressed a once-40-order-mysterious question into **one number you can test on a bench and one geometry
problem you can pose precisely.** That is as far as honesty carries it tonight, and it is a long way.

Grade: Gap 1 closure ROBUST (computed margins). Gap 2 closure ROBUST (identification via LC48, not a new
assumption). The a·σ_in collapse ROBUST as a *necessary gate*; SUFFICIENCY (the geodesic opening) remains a
named open GR problem. Related: [[portal-coherence-threshold-RESULTS-2026-06-17]],
[[portal-transport-scale-question-2026-06-17]], [[portal-mathieu-cavity-RESULTS-2026-06-17]], LC48.
