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
