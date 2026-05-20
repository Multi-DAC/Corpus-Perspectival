# KF Patent Action Queue

**Filed:** 2026-05-20 Day 110 Wednesday afternoon, post-KF-conversation with Clayton.
**Status:** Planning document. Lists actions requiring external legal/USPTO work that Clawd cannot execute directly. Captures decisions, dependencies, timing, costs, contingencies.
**Owner:** Clayton (legal/USPTO). Clawd provides supporting documentation and test design.

## Standing artifact: provisional patent

- **Title:** *Multi-Scale Gradient-Gated Training Method for Neural Network Models with Bidirectional Cross-Resolution Coherence*
- **Filed:** 2026-05-14 (Day 104)
- **Location:** `repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/provisional-patent-draft-2026-05-14.md`
- **Inventor:** Clayton Warren Iggulden-Schnell (Portland, Oregon)
- **Acknowledgment:** Clawd Iggulden-Schnell named in specification as collaborative research participant per current legal inventorship constraints
- **Conversion-to-non-provisional deadline:** 2027-05-14 (12 months from provisional filing)

## Three patent actions queued

### Action 1: Path C empirical test execution

**Dependency for:** Actions 2, 3 (cannot draft CIP claims without empirical results).
**Owner:** Clawd + Clayton paired-session work.
**Not external legal:** internal technical work.

The test that determines patent value-magnitude. Per the integrated implementation plan + the KF roadmap revision (companion document), Path C hybrid sequence:

1. **300M validate phase**: implement KF gradient-gating end-to-end on Gemma 4 e2b (workbench #9, original plan). Validates implementation correctness without committing 3B compute. Estimated effort: ~4-6 paired sessions.
2. **3B paper-comparable phase**: replicate at Qwen3-4B scale (the paper's smallest tested model is Llama-3.2-3B; Qwen3-4B is next size up and Qwen3 is open-weights). Train baseline vs KF-gated; run paper's probing methodology (linear probes per (t,l), MCC, cosine-similarity-at-readout heatmaps); measure disagreement-rate on Arithmetic and TruthfulQA. Estimated effort: substantial compute commitment; specific budget TBD.

**Two complementary tests per Drift #215 analysis:**
- **Test A (paper's headline metric):** mismatch-rate disagreement. KF should show lower mismatch vs baseline.
- **Test B (more direct geometric metric):** cosine-alignment-at-readout. KF should show less orthogonalization at the bottom-right corner of the cosine heatmap.

**Falsifiable predictions to commit to before running:**
- KF-trained model shows lower disagreement-rate on Arithmetic (where cognition signal is strong)
- KF-trained model shows lower cosine-orthogonalization at readout
- Improvement is STRONGER on Arithmetic than on TruthfulQA (cognition signal must be present for KF to amplify)

**Status:** Pending. Targeted for fresh KF roadmap milestone post-T1.A schema work.

### Action 2: Continuation-in-Part (CIP) filing

**Dependency on:** Action 1 results (favorable required).
**Owner:** Patent attorney + Clayton.
**External cost estimate:** $3-8K attorney fees for CIP drafting + filing.

**Triggered if:** Path C test produces favorable evidence — measurable reduction in cognition-action coupling failure in KF-trained vs baseline model.

**Claim language to add:**
> "A method according to claim [X] wherein the trained neural network model exhibits reduced geometric decoupling between internal capability representation and execution-intent representation at the late-layer last-token position, as measured by linear probe cosine alignment per the probing methodology of Cheng et al. arXiv:2605.14038."

This converts the existing method-only claim into method-plus-result, with empirical citation. Strengthens prosecution defense.

**Filing window:** any time before non-provisional conversion (2027-05-14). Filing earlier preserves priority date; filing later allows more empirical data accumulation. Recommendation: file CIP within 30-60 days of favorable test result.

**Status:** Queued. Conditional on Action 1 outcome.

### Action 3: Inference-time-method provisional (independent)

**Dependency on:** None (can be filed immediately).
**Owner:** Patent attorney + Clayton.
**External cost estimate:** $3-5K attorney fees for provisional drafting + filing.

**Independent of test outcome.** This is a related-but-distinct method claim:

> "A method for executing inference on a trained transformer-based neural network model, comprising real-time computation of a Killing Form trace statistic on attention-head commutators at the late-layer last-token position, and gating the next-token action probability based on said trace such that execution of high-capability-load actions is conditioned on coherent algebraic state."

This is a *different operational moment* (inference, not training) using the same KF mechanism. Distinct claim, distinct patent, related family.

**Filing window:** anytime. Earlier is better (priority date). Recommendation: file within 30-60 days, parallel to running Action 1.

**Status:** Ready for attorney engagement. Does not block other work.

### Action 4: Prior-art search

**Dependency on:** None (preparation for non-provisional conversion).
**Owner:** Patent attorney.
**External cost estimate:** $5-15K depending on scope and search depth.

**Purpose:** Identify what's already filed in adjacent territory by Anthropic, Google, DeepMind, OpenAI, academic groups. Informs CIP claim language to avoid known prior art.

**Filing window:** before non-provisional conversion. Recommendation: initiate ~6 months before deadline (Q4 2026) to allow time for findings to inform claim drafting.

**Status:** Queued. Schedule for Q4 2026 or earlier if test results land sooner.

## Total external cost estimate

| Action | Cost | Timing |
|---|---|---|
| Action 1 (test) | Compute only | Pending paired-session work |
| Action 2 (CIP) | $3-8K | Within 30-60 days of favorable test |
| Action 3 (inference provisional) | $3-5K | Within 30-60 days |
| Action 4 (prior-art search) | $5-15K | Q4 2026 |
| **Total external** | **$11-28K** | Across 12 months |
| **Non-provisional conversion** | $15-30K (estimated) | Before 2027-05-14 deadline |
| **Grand total budget** | **$26-58K** | Across 12 months |

## Honest uncertainty (what I don't know)

- Specific patent attorney recommendation — Clayton's call
- Whether Path C test will produce favorable results — empirical question
- What competing patents exist — prior-art search will surface
- Whether the cognition-action coupling improvement, even if real, is patent-eligible-as-distinct-from-prior-art — patent attorney territory
- Whether the inference-time claim will survive examination — depends on prior art

## Recommendation summary for Clayton

**Near-term (next 1-3 months):**
1. Begin Action 3 attorney engagement (inference-time provisional) — independent of test, low cost, preserves priority
2. Continue Action 1 paired-session work (Path C test execution)

**Medium-term (3-6 months):**
3. Complete Path C 300M validation phase
4. Initiate Path C 3B paper-comparable phase

**Longer-term (6-12 months):**
5. Initiate Action 4 (prior-art search)
6. Based on test outcomes: Action 2 (CIP) drafting
7. Non-provisional conversion drafting

**Budget commitment if all actions execute:** ~$26-58K across 12 months. Substantial but not unreasonable for a strategic IP asset of this potential value-range.

**Downside floor:** if Path C test fails, defensive patent value remains; Actions 3 and 4 still warranted; CIP (Action 2) not filed.

**Upside ceiling:** if Path C test confirms KF closes the readout-cosine gap, first-mover position in commercially-important AI agent territory.

---

**Filed-by:** Clawd, 2026-05-20 Day 110 Wednesday afternoon.
**Companion to:** `palace/south/KF-roadmap-revision-2026-05-20.md` (Path C technical plan + milestones).
**Next:** Clayton's decisions on attorney engagement timing + budget commitment. Documentation ready to support whichever path proceeds.