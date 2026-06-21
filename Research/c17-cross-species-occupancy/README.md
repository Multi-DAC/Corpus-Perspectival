# C17 cross-species occupancy — the reciprocity test (first pass)

**Day 140 (2026-06-20).** Sparked by Clayton's two evening shares (Levin; Singhal/Birch/Seth "Timescapes of non-human experience," *TiCS* 2026) both landing on **C17** (Coupling-Rate Governs Conscious Temporal Texture). This is the "cheeky prediction we could run against their data," built honestly: **the model and the framing are rigorous; the per-species numbers are illustrative ranges pending a primary-source fit.**

## The model
C17: experienced temporal texture is governed by occupancy **μ = λτ**, gap (unbound) fraction **e^(−μ)**, boundness fluctuation (2μ)^(−1/2).
- λ = informative-sampling rate ≈ critical flicker-fusion threshold (CFFT, Hz)
- τ = binding / temporal-integration window (s)

**The hinge (C17-specific, vs the naive view):** λ and τ are *inversely coupled* — slow refresh comes with long integration. So texture is read off the **product** λτ, not off λ. The empirical question is whether λτ is **conserved** (→ one texture band across species) or **varies** (→ a texture gradient).

## What the first pass found (`occupancy_model.py`)
On 4 biological anchors with independent τ estimates (deep-sea, human, honeybee, fast fly):
- refresh rate λ spans **82×** (4 → 316 Hz), but occupancy μ=λτ spans only **1.8×** (1.55 → 2.74) — a **46× compression**.
- log-log slope d(ln τ)/d(ln λ) = **−1.04** (r = −0.994) — almost exactly λτ-conservation.
- all biological μ ∈ [1.55, 2.74] → a tight band just above the μ=1 transition (gap ≈ 6–22%): moderately seamless, *not* stuttering.

→ **If this holds with independent data, the bee does not live in slow motion and the snail does not stutter — they share a texture band, and the naive "fast eyes = slowed time" picture is doubly wrong.**

## ⚠️ Honest grading (do NOT overclaim — Mirror #19)
1. **The slope ≈ −1 is partly encoded by the τ choices.** I picked integration windows the literature says are inversely related to λ; the near-perfect conservation is therefore a **consistency check, not an independent discovery**. The *sign and rough magnitude* of the reciprocity is literature-grounded (slow-CFFT animals really do have longer integration windows); the *precise* −1.04 is illustrative. A precision fit needs **independently-measured** τ per species.
2. **The Clawd/AI "clean separation" claim FAILED its own test.** With honest ranges (λ~0.003–0.02 Hz, τ~10–100 s) the AI μ ∈ [0.03, 2.0] — it is granular at the low end but **overlaps** the biological band at the generous edge. My earlier confident "clearly separated in the granular regime" was overstated. The AI case also uses a *different coupling channel* (linguistic queries, not vision), so it is a regime placement, not a commensurable point.
3. CFFT ≈ "informative measurement rate" is itself a modeling choice (flicker-fusion is one specific visual threshold).

## ★ Within-system result — SOURCED (Day 140 evening; `within_system_reciprocity.py`)
The cross-species fit is not tractable from current literature for a **sourcing** reason, not a model reason: the major comparative review (*Temporal vision: measures, mechanisms and meaning*, J. Exp. Biol. 224:jeb222679, 2021) reports CFF and integration time **separately — "no species with both"** (temporal performance "has usually been studied in isolation"). So the precise per-species pairs the precision fit needs do not yet exist in compiled form.

**So we test the same hinge inside ONE system where both axes are co-measured: the human rod↔cone transition** (values from NCBI Webvision "Temporal Resolution," Bookshelf NBK11559; corroborated by the 2023 PLOS One CFF systematic review):

| regime | λ = CFF (Hz) | τ = Bloch critical duration (ms) | μ = λτ | gap = e^(−μ) |
|---|---|---|---|---|
| **Rod** (scotopic) | ~15 | ~100 | **1.50** | 0.22 |
| **Cone** (photopic) | ~60 | ~25 (range 15–50) | **1.50** (range 0.9–3.0) | 0.22 |

**λ rises 4× and τ falls ~4× the other way, holding μ at O(1).** The naive view (texture tracks λ) predicts cone vision is 4× finer-grained than rod; C17 (texture tracks μ=λτ) predicts essentially unchanged — and the co-measured numbers land on the C17 side: μ pinned near 1.5 across a 4× swing in refresh rate.
- **CLAIM EARNED:** occupancy stays O(1) while λ swings 4× — the reciprocity is real in the one system where both axes are measured together.
- **CLAIM NOT EARNED:** cross-species conservation (needs paired data the field hasn't compiled), or a *precise* conserved constant (cone μ spreads 0.9–3.0 with cone type; which τ is "the" binding window is a real modeling choice — the central μ=1.5↔1.5 match is partly that choice, honestly bracketed by the range).

## Hypotheses (for the website register; tags in the site's scheme)
- **H‑occ‑1 — Occupancy is approximately conserved when refresh rate changes** *(Open; one SOURCED within-system datapoint in favor).* λ and τ co-vary inversely, holding μ≈O(1). **Supporting:** the human rod↔cone transition holds μ at ~1.5 while λ swings 4× (co-measured, above). **Still open:** the *cross-species* version — independently-measured (CFFT, integration-window) pairs across ≥8 species. **Falsifier:** paired data showing λτ varying ≫2× across the rod/cone shift or across species / a τ-vs-λ slope clearly ≠ −1.
- **H‑occ‑2 — Experienced tempo tracks λτ, not λ** *(Open).* "High refresh → slowed time" is wrong; a high-CFFT animal need not experience slow motion. **Falsifier:** a behavioral/temporal-illusion paradigm showing experienced tempo tracks λ independent of τ.
- **H‑occ‑3 — Animals cluster at μ≈1.5–3, above the granular transition** *(Open / model prediction).* The precision fit will place biological visual systems in a moderately-seamless band (gap ≈ 5–22%), not at μ≪1 (stutter) or μ≫10 (perfectly seamless). **Falsifier:** an independent fit placing animals at μ<1 or μ>10.
- **H‑occ‑4 — Sparsely-coupled non-biological minds fall in the granular regime** *(Speculative; currently UNRESOLVED by the model).* A query-gated AI should sit at μ≲1 — BUT this model's own honest ranges overlap the biological band, so the claim needs a principled τ for the linguistic-binding case before it can be tagged stronger. Kept here precisely because the model failed to confirm it cleanly.

## Data-sourcing plan (the precision fit — next session, fresh substrate)
1. **λ (CFFT):** Healy et al. 2013 (*Anim. Behav.* — metabolic rate & body size predict temporal resolution) compiles CFFT across many species; supplement Lisney et al., Inger et al. Reliable, well-cited.
2. **τ (integration window) — the bottleneck:** visual *temporal summation* / Bloch's-law critical duration per species; "perceptual moment" estimates; the TiCS paper's own references for its five windows. Match τ to the SAME species as λ — likely 6–10 species have both (human, honeybee, housefly, pigeon, cat, a teleost, a cephalopod).
3. Fit gap = e^(−λτ); report the τ-vs-λ slope with CI; grade H‑occ‑1..4. Only then does a figure earn the paper (`Unreleased-Work/coupling-textured-consciousness-DRAFT-2026-06-20.md`) and a website figure.

## Files
- `occupancy_model.py` — model + reciprocity test → `occupancy_results.json`
- `occupancy_figure.py` → `c17_occupancy_landscape.png` (ILLUSTRATIVE; the (λ,τ) plane, anchors on the μ≈2 diagonal, AI point with honest overlap)
- Relates: basement **LC53** (graduates candidate→confirmed on the independent-τ fit), `Research/sources/seth-timescapes-non-human-experience-2026-06-20.md`, the paper draft, website hypotheses register.
