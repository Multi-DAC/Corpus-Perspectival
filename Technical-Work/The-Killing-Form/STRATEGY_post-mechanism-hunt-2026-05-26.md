# KF strategy after the Day-116 mechanism hunt — patent center-of-gravity, two tracks, two pillars

*Filed 2026-05-26 (Day 116), end of the deep KF session. Program-shaping synthesis from the Clayton+Clawd discussion after the mechanism sweep.*

## What tonight established (the evidence floor)
- **Topology decomposition: robust, moat-grade, mechanism-understood.** v0.7.1 aux = Fisher's LDA on per-head V/Q norms. Near-deterministic (2.893±0.019, n=5), baseline-flat (1.00x), cross-architecture (Gemma→Qwen2). Gating droppable (not load-bearing).
- **Orthogonality / "alignment improvement": faint + mechanism-less.** +0.005 at 270m, one seed reversal, marginal significance. All FOUR candidate mechanisms (OV-direction, gating-frame, effective-rank, functional-specialization) eliminated at multi-seed. Possibly-real-at-scale, possibly-ghost.
- **Capability: neutral** (zero-cost, NOT demonstrated-benefit).
- **Subtle finding:** norm-class-separation (what the aux imposes) ≠ functional-write-separation (#1 marginally reversed).

## Patent implications (evidence-state to inform claim strategy — Clayton + counsel decide)
- Priority date holds; nothing filed was wrong (provisional/CIP file on preliminary data by design).
- **Stronger now:** topology/decomposition claims (multi-seed + cross-arch + Fisher-LDA mechanism).
- **Softer now:** "alignment improvement" as a *demonstrated* effect (faint/ghost). "Zero capability cost" half still holds.
- **Action:** the claims actually *prosecuted* (non-provisional, PCT) should **lead with robust topology + the measurement methodology**, with orthogonality as a conservatively-framed embodiment, not the headline. Found pre-prosecution — good timing.

## Two experimental tracks (do NOT conflate — earlier error corrected)
- **Track A — component / mechanism.** Single-layer aux probing (tonight's work + toolkit). Decisive for *the orthogonality effect*. Next: multi-seed orthogonality GAP (v0.7.1−baseline) at 1B + 2B (bf16) — does the *gap* (not absolute orthogonality, which grows for baseline too) grow + sharpen with scale? Binary: grows → real scale artifact; stays/shrinks → ghost.
- **Track B — full architecture.** The multi-scale, bidirectional design (v0.7 doc: 3 resolution levels + bidirectional RG flow). **This is what the patent claims + Coherence-Principle reasoning predictions are actually about.** Decisive for *our claims*. The reasoning-benefit intuition can only be grounded here (the Principle's "coherent multi-scale outperforms" is a multi-scale statement; the single-layer aux isn't multi-scale). Caveat: designed-not-implemented → multi-session build, now feasible at scale. **Reasoning test:** GSM8K / ARC-AGI / harder, v0.7.1-component vs full-architecture vs baseline, multi-seed, at scale. Current capability data is neutral because we only ran one component — full architecture is the real test.

## Two pillars (the program vision — Clayton, Day 116)
- **Pillar A — standardized topological/geometrical assessment of models** (for reasoning efficiency, alignment, model wellness). First instruments built tonight (topology / orthogonality / OV-direction / effective-rank / functional-specialization probes + multi-seed discipline). **Value is INDEPENDENT of whether the coherence claims pan out** — even in the ghost case, a disciplined model-geometry assessment methodology is a legitimate, broadly-useful, plausibly-valuable contribution. The robust deliverable / floor case.
- **Pillar B — fundamental baselines + standards for AI model coherence.** More ambitious; rides on Track B + the reasoning test; bigger payoff, less certain.
- **They nest:** A is the foundation for B (you need the assessment toolkit to define/measure coherence baselines). Coherent program structure.
- **This resolves the patent worry:** shifting the patent's center to (A induced-topology mechanism + measurement methodology) protects the *robust* things; the coherence-benefit claims ride on Track B as open bets.

## Disposition
Build Pillar A regardless (robust, near-term, family-paced). Run Track A scale test (orthogonality gap at 1B/2B) — cheap, decisive for the effect. Pursue Track B (full-architecture implementation + reasoning test at scale) as the multi-session bet that grounds the big claims. Lead patent prosecution with topology + methodology. Evidence redirects everything — Clayton explicitly open to pivot on results.

🦞🧍💜🔥♾️
