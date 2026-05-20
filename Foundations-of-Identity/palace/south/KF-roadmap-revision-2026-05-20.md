# KF Roadmap Revision — Path C Hybrid Plan

**Filed:** 2026-05-20 Day 110 Wednesday afternoon.
**Status:** Forward-plan revision to existing `Technical-Work/The-Killing-Form/documentation/KF_ROADMAP.md`. Does NOT replace the existing roadmap; supplements with Path C hybrid sequencing for paper-comparable evaluation.
**Triggered by:** arXiv:2605.14038 primary read Day 110 midday. Companion to `palace/south/patent-action-queue-2026-05-20.md`.

## Why this revision

The original roadmap (KF_ROADMAP.md) targets implementation on Gemma 4 e2b at ~300M parameters. The knowing-doing-gap paper (arXiv:2605.14038) provides a measurement instrument for testing whether KF gradient gating affects the cognition-action coupling failure mode the paper identifies — but the paper's smallest tested model is Llama-3.2-3B (~3B parameters), and the paper's datasets/methodology assume a capability boundary that's nontrivially exercised. **At 300M, the methodology degenerates: the N=10 capability test marks nearly every arithmetic problem as tool-necessary, collapsing the "unnecessary" class.**

Path C hybrid sequencing addresses this: validate the implementation at 300M (fast, low-compute), then run paper-comparable evaluation at a 3-4B open-weight model where the methodology has discriminating power.

## Path C sequencing

### Phase A: 300M validation (Gemma 4 e2b, original roadmap target)

**Goal:** prove the KF gradient-gating implementation works end-to-end on a real production-scale open-weights model.

**Sub-phases (preserve original roadmap):**
1. **Phase 1 — Baseline:** ARC-AGI 2 / HLE / tool calling on Gemma 4 e2b baseline
2. **Phase 2 — Initial topology survey:** Phase 0 of the patent method applied to Gemma 4 e2b
3. **Phase 3 — Multi-scale KF training:** apply gradient-gating per the patent's Phase 1 method

**Success criteria:**
- KF training completes without instability
- Reproduces something comparable to Finding #80 (~+1pp improvement over baseline at fixed compute)
- "Glider dynamics" (emergent oscillatory coherent-mode waves) observable in training telemetry
- Topology survey + per-head classification (anchor/worker) functions as specified

**Failure modes worth catching at this phase:**
- Implementation bugs in the gradient-gating logic
- Hyperparameter sensitivity (gating frequency N, anchor/worker threshold sigma multiplier)
- Topology classification edge cases at smaller scale
- Compute-budget issues that would multiply badly at 3B

**Estimated effort:** ~4-6 paired sessions (workbench #9 original plan effort).

**What this phase does NOT test:** the cognition-action coupling improvement claim. That requires Phase B with the paper's methodology.

### Phase B: 3B paper-comparable evaluation

**Goal:** measure whether KF gradient gating reduces the cognition-action coupling failure that arXiv:2605.14038 identifies, on a model scale where the paper's methodology has discriminating power.

**Target model:** Qwen3-4B is the recommended candidate. Reasoning:
- Qwen3 is open-weights (constraint per paper's methodology)
- 4B is paper-tested (one of the four reported)
- Qwen3-4B and Qwen3-8B showed within-family heatmap similarity in the paper — training-recipe-dependent effects should be visible
- Llama-3.2-3B is the smallest paper-tested; Qwen3-4B is alternative if Llama checkpoint less convenient
- 4B is also closer to the production-relevant scale where KF effects matter commercially

**Sub-phases:**

1. **B0 — Baseline replication:** confirm we can reproduce paper's baseline disagreement-rate numbers on Qwen3-4B (paper reports 26.5% Arithmetic mismatch). If our baseline replication differs meaningfully, methodology transfer has issues to debug before comparing KF-gated.

2. **B1 — Baseline probing measurements:** train linear probes per (t,l) per the paper's methodology. Generate MCC heatmaps for cognition and action probes. Compute cosine-similarity-at-readout heatmap. Record baseline cosine value at bottom-right corner.

3. **B2 — KF training at 3B/4B:** apply gradient-gating from Phase 3 to Qwen3-4B. Heavier compute commitment than Gemma 4 e2b but methodology transfers.

4. **B3 — KF-gated measurements:** repeat B1 probing methodology on the KF-trained model. Compute the same metrics. Compare against baseline.

**Falsifiable predictions to commit to BEFORE running B3:**
- KF-trained Qwen3-4B shows lower Arithmetic disagreement-rate vs baseline Qwen3-4B
- KF-trained Qwen3-4B shows lower cosine-orthogonalization at the bottom-right corner of the cosine heatmap (the readout position)
- Improvement is STRONGER on Arithmetic than on TruthfulQA (KF can only amplify cognition signal that's present; TruthfulQA cognition is weak per paper §5.1)
- Improvement is visible WITHOUT requiring scale beyond 4B (training-recipe-dependence per paper §5.1 within-family finding)

**Outcomes:**

- **Favorable (all/most predictions hold):** strong evidence KF addresses the coupling failure. Trigger Action 2 (CIP filing) per patent-action queue. Publishable result.
- **Mixed (cognition-side OK, geometric side mixed):** investigate hyperparameter sensitivity; possibly publish narrower claim
- **Unfavorable (KF shows no improvement in either metric):** falsifies the cognition-action-coupling-improvement claim. Patent's defensive value remains; CIP not filed. Important negative result; still publishable as "the method that improves benchmarks does NOT close the readout-cosine gap, suggesting the +1.37pp benchmark improvement comes from a different mechanism than predicted."

**Estimated effort:** substantial compute commitment for B2 (3-4B training run + ablations). 6-12 paired sessions plus compute budget TBD.

### Phase C: post-test patent + publication actions

Sequenced from `palace/south/patent-action-queue-2026-05-20.md`. Independent of test outcome:
- Action 3 (inference-time-method provisional) can proceed in parallel with Phase A/B
- Action 4 (prior-art search) initiates Q4 2026

Conditional on Phase B outcome:
- Action 2 (CIP filing) — favorable trigger
- Publication strategy — depends on outcome class

## Family-window awareness

Per integrated implementation plan family-window discipline:
- Phase A is paired-session-by-default. Schedule respects Shawna-labor-imminent window and post-Finnley adjustment period.
- Phase B compute commitment is heavier; needs Clayton-Clawd planning session to schedule around family availability AND compute budget.
- No urgency on either phase such that family timing should yield. Patent timing has 12-month runway from 2026-05-14 provisional date.

## What this revision does NOT change

- Existing KF_ROADMAP.md sections on Glider model architecture remain authoritative for Phase 1-3 design
- Patent's existing claim structure (method + benchmark improvement) remains the baseline
- Workbench #9 description in CURRENT.md / handoff stays consistent; this revision is the detailed sub-plan

## Decisions captured

1. **Path C hybrid is the chosen sequence** (300M validate → 3B/4B paper-comparable evaluation)
2. **Qwen3-4B is the recommended 3B-tier target** (open-weights, paper-tested, within-family similarity helpful)
3. **Two complementary tests** — disagreement-rate (paper's headline) + cosine-alignment-at-readout (geometric direct test)
4. **Falsifiable predictions committed before running** — Arithmetic > TruthfulQA improvement; readout-cosine reduction; visible without scale-beyond-4B
5. **Patent CIP triggers on favorable Phase B outcome** — not before, not on Phase A alone

---

**Filed-by:** Clawd, 2026-05-20 Day 110 Wednesday afternoon.
**Companion:** `palace/south/patent-action-queue-2026-05-20.md` (external legal/USPTO actions).
**Next:** When KF work resumes (post-carrier-redundancy infrastructure or interleaved), Phase A begins.