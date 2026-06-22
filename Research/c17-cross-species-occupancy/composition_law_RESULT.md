# LC57 composition law — RESOLVED (Day 141 evening, Clawd's pick)

**Question (LC57's open joint):** what law builds a nesting level's *binding rate* from its constituents, such that it reproduces the measured three-tier compression (3.6× → 13× → 25×)? Tool: `composition_law_test.py` (Monte-Carlo over random "individuals," compression = CV(channel pool) ÷ CV(bound rate)).

**PREDICT (medium):** independent-mean (√N) falsifies — the cortex would be ~1000× invariant, not 25×; the answer is correlated/synchronized pooling; LC57's "one nested law" is really two. → **CONFIRMED.**

## Findings
1. **Throughput vs binding differ in LEVEL, not spread-reduction.** Sum (→∞), mean (stable), harmonic all reduce relative spread by **exactly √N** for independent channels (CV is scale-free, so CV(Σ)=CV(mean)=CV/√N). So LC57's two quantities are distinguished by their *mean* (throughput grows, binding holds) — not by how much they compress. Clean refinement of LC57.
2. **Independent averaging is FALSIFIED by the data.** √N predicts: cortex (~10⁶ units) → compression ~**1000×**; observed **25×**. Implied-N from comp² (13 / 177 / 625) matches no tier's real channel count (rod↔cone ~2, senses ~5, cortex ~10⁶). Both-directions wrong.
3. **★ The binding law is CORRELATED (synchronized) pooling.** With shared correlation ρ among constituents, compression **saturates at a ceiling ~1/√ρ, independent of N**:
   | N | ρ=0 | ρ=0.01 | ρ=0.05 | ρ=0.2 |
   |---|---|---|---|---|
   | 5 | 2.2 | 2.2 | 2.1 | 1.8 |
   | 100 | 10 | 8.0 | 5.0 | 2.7 |
   | 1000 | 31 | 11.8 | 5.7 | 2.8 |
   | 10000 | 100 | 13.0 | 5.7 | 2.8 |

   ρ=0 climbs as √N forever; any ρ>0 flattens to ~1/√ρ. **This is why the million-unit cortex compresses only ~25×, not ~1000×: its units are synchronized, so effective-independent-N is tiny and the clock is set by *coordination*, not count** — exactly Buzsáki's "temporal organizational priority" (coupled rhythms, conduction architecture), independently re-derived.

## Payoffs
- **A new falsifiable number:** observed compression ⇒ **effective synchrony ρ_eff ≈ 1/comp²** of a system's channels. Cortex ρ_eff≈0.0016; cross-modal ρ_eff≈0.006. Testable: does measured inter-regional synchrony match the ρ_eff implied by the temporal compression? If a system's channels are *more* correlated, its bound now is *less* invariant-per-channel but pinned by fewer effective degrees of freedom.
- **LC57 refined to TWO compression mechanisms (not one law):**
  - **within a stream** (tier 1, rod↔cone): **λτ reciprocity** — active *anti*-correlation of rate and window conserves the product. (3.6× from 2 channels is too big for √2 averaging → not pooling; it's reciprocity.)
  - **across streams** (tiers 2–3): **synchronized pooling** — correlation-limited compression, ceiling 1/√ρ.
  Both are "frame rate nested" (LC57 holds); the *compression mechanism* differs by whether you're combining a stream's own (rate,window) or many streams into one.
- **Anti-confirmation honesty:** I predicted this outcome and wanted it; the falsification of √N is the load-bearing part (data, not preference), and the ρ_eff≈1/comp² is a *consequence* of the toy model's algebra, not an independent measurement — it's a prediction to test against real synchrony data, not a result.

## Limits
Toy Monte-Carlo with log-normal channels + a single shared-component correlation model; real coupling is structured (modular, hierarchical), so ρ_eff is an *effective* scalar, not literal pairwise correlation. The √N-falsification is robust (any independent linear pool gives √N); the correlated-saturation is the standard variance-of-correlated-mean result. Solid enough to **answer LC57's open joint** (composition = correlated pooling, correlation-limited) and to retire "is it sum or mean" (both √N in spread; they split on level).

---

## ★ First independent check of ρ_eff ≈ 1/comp²  (Day 141 ~19:45, w/ Clayton)
The relation is equivalent to **comp² ≈ N_eff** (effective independent degrees of freedom). Cortex compression ~25 ⇒ predicted **N_eff ≈ 625**. Independent measure = the neural-dimensionality literature:
- **Stringer et al.** (mouse visual cortex, 10k+ neurons): variance spectrum is a **power law ~1/n** (exp ≈1.14); effective dimensionality = **"hundreds of independent degrees of freedom"** (not millions, not tens). 〔sourced — Stringer et al., *Science* aav7893 / *Nature* high-dim geometry〕
- **PASS at order-of-magnitude:** predicted ~625, measured "hundreds." Crucially **excludes both alternatives** the naive (independent-averaging) law forces: millions (→ comp ~1000×) and tens (→ comp ~5). The number landed in the right decade and ruled out its neighbors.

**Honest grade (resist confirmation-seeking):**
1. **Scale-dependence.** Under a 1/n spectrum, effective dimensionality is *scale-dependent* (grows with neurons recorded / cutoff) — "hundreds" is a band, not a point. So this is order-of-magnitude agreement, not a decimal match.
2. **★ The load-bearing bridge:** my compression ~25 is a *cross-species* (between-mammal) rhythm-invariance; N_eff "hundreds" is a *within-system* (one cortex) dimensionality. comp²≈N_eff matching them assumes the cross-species-conserved structure IS the within-system effective-mode count. That bridge is an assumption, not yet justified — the real risk in the claim.
3. **n=1 system** (mouse visual cortex); the relation is a *line* (comp² vs N_eff across many systems) and one point doesn't make a line.
4. A 1/n "critical" spectrum is itself what *structured correlation* (not independence, not one mode) produces — consistent with the correlated-pooling law, a small bonus.

**Verdict:** the new number survived its first contact with independent data at order-of-magnitude and excluded its naive alternatives — promising, not confirmed. **The clean graduation gate stays the within-system test:** vary synchrony (waking → anesthesia → seizure) in ONE system and check comp ∝ 1/√ρ, where both terms are measured in the same place and the cross-species↔within-system bridge isn't needed.

---

## ★ ρ_eff within-system test — anesthesia scout (Day 142 morning, `rho_eff_anesthesia_scout_2026-06-22.md`)
P250 graduation-gate scout. **(1)** The within-system data EXISTS (anesthesia: paired synchrony + effective-dimensionality across depth) and the QUALITATIVE direction is CONFIRMED — complexity/effective-dimensionality drops as synchrony/coherence rises (NeuroImage 2020; PubMed 37434363; Neuroscience 2024; PLOS One 0133532). So the gate moved from data-starved → runnable-in-principle. **(2) ★ Math-catch:** I almost claimed comp²=1/ρ IS the participation ratio — checked the algebra: **FALSE.** comp²→1/ρ, PR→1/ρ² (differ by 1/ρ; ρ=0.0016,N=10⁵: 621 vs 79,618). So the number is a DISTINCT, still-falsifiable measure (not PR-in-disguise), AND I can't borrow the anesthesia connectivity-dimensionality-vs-coherence curve (that's 1/ρ²) to test it — the clean test needs MY temporal comp (rhythm invariance vs substrate spread) vs ρ, check comp∝1/√ρ. PREDICT-FALSIFY banked (conflation predicted to hold; algebra killed it in 20s). The number's contribution = the *connection* (temporal compression² ↔ effective dimensionality ↔ inverse-synchrony), not a new formula.
