# §9 correction — NUMERICALLY CONFIRMED. The grounded resolution (for Clayton's ratification)

*Morning Do-Be-Talk-Be-Do drive, 2026-06-02 ~07:00. Pre-derives the joint §9 resolution that A144 +
P218 called for, so we settle it with numbers, not argument. Toy model + runs:
`2026-06-02-phi-vs-mk-toy.py`, `2026-06-02-phi-vs-mk-test4refine.py` (same folder).*

## The verdict

The dream-drive self-FALSIFY (A144) is **correct, and now numerically confirmed.** The midnight §9
("Φ_S repelling at 0 → Morse dichotomy on σ_struct") was backwards. The corrected picture — a
**Φ_S-vs-M_k competition** — is verified in the ℤ/2-swap model the Companion itself uses (§3.4.2,
§7.4.3), and it comes with a **clean closed-form threshold** the numerics hit to the digit.

This also rules out A144's own hedge (candidate #3, "I'm over-eager to self-FALSIFY"): the correction
is not motivated reasoning — it survives computation. *FALSIFY-of-the-FALSIFY: negative.*

## The model (ℤ/2-swap, parametrized by d = p₀ − p₁ ∈ [−1,1])

- d = 0 → uniform / symmetric / **superposed** ("neutral 0"); d = ±1 → **definite** pointer states.
- **Φ_S** (push_struct = C-average over the swap, strength a∈[0,1]): `d → (1−a)d`. Companion's
  `push_struct(δ₀)=uniform` is the a=1 case. Fixed point d=0; contraction rate (1−a).
- **M_k** (measurement / sharpening, inverse-temperature β≥1): `pᵢ ∝ pᵢ^β`; near d=0, `d → βd`.

## Results (each a logged prediction)

| Test | Prediction (conf) | Result | Verdict |
|---|---|---|---|
| **1. Φ_S alone** | uniform ATTRACTS (high) | f'(0)=1−a ∈ {0.7,0.4,0.0}<1; definite→uniform | **CONFIRM** — Φ_S attracts toward neutral |
| **2. M_k alone** | uniform REPELS (med-high) | f'(0)=β ∈ {1.5,2,3}>1; uniform→±1 | **CONFIRM** — measurement is the repeller |
| **3. Competition Φ_S∘M_k** | threshold β(1−a)=1 (not predicted: exact form) | a=0.5 → β\*=2.000 exact; β<2 DFS, β>2 einselection | **CONFIRM + bonus closed form** |
| **4. N_sign vs N_struct** | coincide if symmetric, separate if broken (med) | t=0: both 0 (coincide); t=0.05: N_struct=+0.05, N_sign=−0.274 (separate 0.324) | **CONFIRM** — coincidence is a symmetry artifact |

## The corrected §9, stated cleanly (proposal)

> **Neutral-0 is repelling ⟺ measurement dominates coherence-restoration: β(1−a) > 1.**
> - **Φ_S** (structural coherence / C-averaging) **attracts** toward the symmetric-neutral state (the
>   σ_struct *maximum*). It is *not* the repeller; the midnight attribution was inverted.
> - **M_k** (measurement, T4) drives 0 → ± (the symmetry-breaking / "to be is to fall off the neutral").
> - **Einselection** = M_k wins, β(1−a) > 1 → pointer states stable, superposition repelled.
> - **Decoherence-free / metastable superposition** = Φ_S wins, β(1−a) < 1 → superposition stable.
>   (The §9 "edge case" survives — but its mechanism is *weak measurement*, **not** a degenerate Hessian.)
> - The dichotomy is a **competition on coupling strengths (β vs a)**, **not** a Morse condition on
>   σ_struct (0 is a σ_struct *maximum*, not a saddle).
> - **N_sign (Bias sign=0) ≠ N_struct (Φ_S-harmonic)** in general; they coincide only under enough
>   symmetry. §9's argument borrowed Φ_S's N_struct dynamics to claim N_sign repelling — valid only in
>   the symmetric case, which is exactly the toy the intuition was built on.

## Why this is better than the midnight version (not just a patch)

1. **Tighter physics.** β(1−a)=1 is literally the decoherence-vs-coherent-dynamics competition that
   *is* einselection (Zurek): pointer states win when environmental measurement outpaces unitary
   coherence-restoration. The midnight Morse-on-σ_struct picture couldn't express "how strong is the
   measurement?" — the corrected one makes it the control parameter.
2. **The DFS edge case gets the right cause.** Decoherence-free subspaces are *weak-measurement*
   regions (β(1−a)<1), not degenerate-Hessian curiosities.
3. **It is the dynamical face of the bulk-vs-binding architecture** (`orthogonal-coupling...2026-05-31`):
   Φ_S = coherence-restoration through the rich bulk; M_k = the thin binding/measurement gate that
   *commits* (consolidates). β(1−a)>1 = "isometry → consolidate"; β(1−a)<1 = "dissonance → don't
   consolidate." The corrected §9 and the coupling architecture are one structure, dynamic vs structural.

## Unaffected (re-confirmed)
§10 (gluing / Lawvere-escape) and §11 (Chater witness) never depended on Φ_S's direction. They stand.

## Next (for the joint session)
1. **Ratify** the corrected §9 prose above; replace the struck-through midnight claim in the draft.
2. Optional rigor: lift β(1−a)=1 from the ℤ/2 toy to the general statement (measurement-rate vs the
   curvature of the σ_struct well — a Lyapunov/linear-stability argument on the combined operator).
3. Check the §7.3 / Anchor App. B §B.1 sign convention to confirm the N_sign≠N_struct reading at the
   formal (not just toy) level — the last open premise.

*Cognitive trace: PREDICT×3 (logged, with confidence) → TEST (toy) → CONFIRM×3 + bonus closed form →
FALSIFY-the-self-FALSIFY-hedge (A144 #3 ruled out) → EXTRACT (β(1−a)=1 competition) → TRANSFER (one
structure with the coupling architecture). No high-confidence prediction failed — but the
self-FALSIFY it was testing was itself the high-info event from the prior drive; this drive *grounds* it.*
