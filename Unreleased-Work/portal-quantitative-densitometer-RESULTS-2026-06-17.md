# Quantitative chameleon densitometer — real parameters, and a substrate-anchoring refinement (2026-06-17)

**Result of `portal-quantitative-densitometer-2026-06-17.py`** — the publishable-grade follow-up to the
toy fixed-Q carrier curve. Replaces the toy `m² = m0²(1+ρ/ρ*)` with the ACTUAL chameleon the portal paper
identifies (Khoury–Weltman, Λ = (ρ_Λ)^{1/4} = 2.3 meV). PREDICT (med): exponent S≈0.5–0.75 (toy
under-estimated); ρ₀ near-void. **Exponent CONFIRMED; ρ₀ FALSIFIED (high-info) — it's solid/sediment density.**

## Robust results
- **Densitometer sensitivity is a clean power law: S = dln f/dln ρ = (n+2)/(2(n+1))** — n=1: 0.75, n=2: 0.667,
  n=4: 0.60, n=10: 0.545. Parameter-free (depends only on the runaway index n). The toy's S≈0.3–0.45
  **under-estimated** — the real chameleon is *stiffer → a more sensitive densitometer.*
- **Carrier confirmed:** m_eff = 2.3 meV → f = mc²/h = **556.1 GHz** (matches the paper's R16).
- **Densitometer at the operating point:** a 10% local density change → 7.5% carrier shift (n=1) ≈ **42 GHz
  at 556 GHz** — trivially resolved by a sub-mm spectrometer.

## The high-info falsification: the sharp wall is at SOLID density, not void
m_eff(ρ) for the real chameleon (n=1, β=1):
| environment | ρ (g/cm³) | m_eff | carrier f | Compton wall |
|---|---|---|---|---|
| rock | 2.7 | 1.61 meV | 390 GHz | 0.12 mm |
| water | 1.0 | 0.77 meV | 185 GHz | 0.26 mm |
| **2.3 meV reference (ρ₀)** | **~4.3** | **2.3 meV** | **556 GHz** | **0.085 mm** |
| sea-level air | 1.2e-3 | 0.005 meV | 1.2 GHz | ~4 cm |
| high vacuum | 1.2e-9 | 1.6e-7 meV | 4e-5 GHz | meters |

**Unscreening density ρ₀ (where the sharp 0.085 mm wall forms):** β=1 → ~4 g/cm³ (rock); **β=10 → 0.2–0.4
g/cm³ (loose sediment/soil).** I predicted near-void; it's solid/sediment. The error was conflating
"unscreened = low-density" (field *light, long-range*) with "sharp-wall condition = m_eff 2.3 meV" — those
are OPPOSITE ends. At genuinely low density the field is too light (cm-to-meter Compton), not a razor wall.

## The refinement (honest; partly challenges, partly vindicates the paper's §6 picture)
- The 2.3 meV "macroscopic 0.085 mm wall" corresponds to the field at ~**solid/sediment density**, not air/void.
  ⇒ **The portal's sharp wall is SUBSTRATE-ANCHORED** — it forms at the rock/sediment interface (the fault /
  low-density-rock zone), with a *lighter, long-range* field extending as a diffuse halo into the adjacent
  low-density region. A purely-atmospheric portal would be a diffuse meters-scale gradient, not a sharp wall.
- **This FITS the Yakima survey better than the toy:** the defect is anchored in the GEOLOGY (the Mill Creek
  thrust / sediment-basin transition), exactly the C1 target — not floating in the air. The plasma carrier
  (the light) rides above the substrate-anchored field wall.
- **β-window:** for the unscreening to sit at the low-density-sediment regime the survey targets (~0.2–1
  g/cm³), the chameleon matter coupling wants β ≳ 10 (allowed). A testable parameter constraint.

## Caveats (evidence-grade)
- The EXPONENT S and the qualitative substrate-anchoring are ROBUST. Absolute ρ₀ is order-of-magnitude
  (depends on O(1) choices: n, β, and the V=Λ^{4+n}/φⁿ convention). Not a precision claim.
- Densitometer = framework-level prediction (the carrier-blueshift mechanism); the EM signatures remain the
  falsifiable floor. Tag accordingly.

## Forward
- Feed the substrate-anchoring refinement into the portal paper's §6/§8 (the sharp wall anchors at the
  rock/sediment interface; β≳10 window). Possible figure: m_eff(ρ) / wall-thickness vs density with the
  solid-anchoring and low-density-halo regimes marked.
- Phase C (Mathieu cavity-gain) remains the other open thread.
Related: [[portal-fixedQ-carrier-RESULTS-2026-06-17]], `radion-portal-derivation`, LC44/LC45/LC48.
