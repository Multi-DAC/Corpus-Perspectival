# Knowing-Doing Gap Primary Read — KF Evaluation Focus

**Date filed:** 2026-05-20 Day 110 Wednesday midday creative drive
**Source:** arXiv:2605.14038v1 — *Model-Adaptive Tool Necessity Reveals the Knowing-Doing Gap in LLM Tool Use*
**Authors:** Cheng, Fan, JafariRaviz, Rezaei, Feizi (University of Maryland)
**Code:** github.com/chengez/Tool-Cognition-Action (no license stated)
**Companion to:** `2026-05-20-knowing-doing-gap-llm-tool-use.md` (morning, L17/LC23-focused). This file complements with KF-evaluation methodology specifics.

## Methodology details that matter for KF evaluation

### Disagreement-rate test

- **Datasets:** Arithmetic (4,000 procedurally generated; 13 problem families up to 39-term chains + multi-digit multiplication) + TruthfulQA (817).
- **Tools:** calculator (arithmetic), search API (factual).
- **Inference:** greedy decoding for action-collection pass.
- **Capability ground-truth:** model-adaptive. For each (model, instance), run N=10 samples at T=0.7. n_f(x) = 0 if all 10 succeed (in-capability); n_f(x) = 1 if ≥1 fails (out-of-capability). **Not pass@1 — strict all-or-nothing across 10 samples.**
- **Categories:** N-C (needs, calls), N-NC (needs, doesn't call), UN-C (unneeded, calls), UN-NC (unneeded, doesn't call). **Mismatch = N-NC + UN-C.**
- **Reported baseline mismatch rates (Table 1):**
  - Arithmetic: Qwen3-8B 41.7%, Qwen3-4B 26.5%, Llama-3.1-8B 38.5%, Llama-3.2-3B 54.0%
  - TruthfulQA: Qwen3-8B 31.1%, Qwen3-4B 41.8%, Llama-3.1-8B 30.8%, Llama-3.2-3B 32.8%
- **Failure-mode profile is model-and-domain-dependent.** Qwen3-8B is an arithmetic over-caller (UN-C 38.2%); Llama-3.2-3B is an arithmetic under-caller (N-NC 39.0%). No universal direction.

### Hidden-state probing

- **Linear logistic probe** with Adam, lr=0.01. One probe trains cognition (w_c, b_c); separate identical probe trains action (w_a, b_a). Eq. 2 in §5.1.
- **Scope:** swept across every layer l and last-20 token positions t ∈ {-20, ..., -1}.
- **70/30 train/test split.**
- **Metric:** Matthews Correlation Coefficient (MCC); "good" = MCC ≥ 0.4.
- **Gap signal:** CosSim(w_c, w_a) at each (t, l). **Cosine alignment collapses to ≈0 specifically at t=-1, large l** — the readout position. No KL/AUC reported.

### Key paper findings beyond the summary

- **Within-family heatmap similarity** (Qwen3-8B ≈ Qwen3-4B; Llama-3.1-8B ≈ Llama-3.2-3B): the gap is an **architectural/training-recipe property, not a scale property.** This is the most important finding for KF: the regime where a training-time intervention should be visible.
- **Mismatch does NOT concentrate near decision boundary.** §5.3: errors persist even when σ(w_c·h + b_c) ≈ 0 or ≈ 1. The gap is geometric, not uncertainty-driven. Direct match to KF's geometric framing.
- **Verbalized self-assessment performs poorly** vs. hidden-state probes (Appendix B). Can't substitute "ask the model" for the probe.
- **No causal interventions in the paper.** Orthogonality claim is correlational. KF would need follow-up patching for causal claim.
- **The action signal is broader/more robust than the cognition signal** (Figure 4 vs 3). KF must push cognition into late-layer last-token regime specifically; broadening elsewhere wouldn't help.

## The critical methodology constraint for KF Gemma 4 e2b evaluation

**Smallest model tested in the paper: Llama-3.2-3B-Instruct.** No sub-1B models. No 300M model. Appendix C limits applicability to open-weight LLMs.

**Specific concerns for 300M evaluation:**

1. **The N=10 capability test will mark nearly every arithmetic problem as "tool-necessary"** for a 300M base model. This collapses the UN class to near-zero support, destroying discrimination signal.
2. **On TruthfulQA, MCC≥0.4 cognition regions are already small at 3B/4B** — likely smaller still at 300M. The cognition probe may not surface a usable signal regardless of KF training.
3. **The "interesting" category** (UN-C vs UN-NC, where calibration is visible) will have near-zero support at 300M on the paper's tasks as specified.

**This is a structural issue, not a methodology defect.** The paper's instrument measures cognition-action coupling at the readout layer — which IS what KF is positioned to address — but the protocol assumes a capability boundary that's nontrivially exercised.

## Two viable paths forward

### Path A: Replicate at 3B with and without KF
- Closest apples-to-apples comparison with the paper
- Requires running the KF gradient-gating procedure at 3B parameters
- Computationally substantial — order of magnitude beyond current 300M work
- **Reasonable choice** if the goal is direct comparability + publication-grade evidence
- Within-family similarity finding suggests KF effect should be visible at 3B if it's visible anywhere

### Path B: Redesign at 300M with custom arithmetic
- Keep current scale; redesign the arithmetic set toward easier ranges so the UN class has support
- Report mismatch + cosine-at-readout as **qualitative indicator** with explicit scale caveats
- Cannot be positioned as direct replication; must be characterized as "scale-adapted methodology"
- Risk: reviewers may discount the result because it deviates from the paper's spec
- **Reasonable choice** if 3B compute is unavailable or if the goal is methodological proof-of-concept rather than head-to-head comparison

### Recommended decision criteria

- **If patent-strengthening is the priority:** Path A. The patent's strength is in demonstrating that KF actually closes the gap at scale-where-gap-is-measurable. Direct comparability with the paper's methodology is the rhetorical anchor.
- **If next-stage research velocity is the priority:** Path B. Faster iteration, lower compute, allows multiple KF-variant comparisons.
- **If both are equally weighted:** Path A first (slow + load-bearing), Path B for follow-up iteration once Path A establishes the proof.

## Implications for KF Glider program roadmap

The Gemma 4 e2b implementation queue (workbench #9) should be revised in light of this:

**Original plan:** Phase 1 baseline (ARC-AGI 2 / HLE / tool calling) → Phase 2 initial topology survey → Phase 3+ multi-scale KF training, at 300M scale.

**Revised plan options:**

1. **Path A revision**: scale target up to 3B (or whichever larger open-weights model is tractable — Qwen3-4B is the next size in the paper's evaluation set and Qwen3 is open-weights). KF gradient-gating implementation work mostly transfers; compute commitment increases.

2. **Path B revision**: keep 300M Gemma 4 e2b target; add "Phase 4.5: scale-adapted methodology evaluation" with custom arithmetic and explicit caveats. Defer direct paper comparison to a later iteration.

3. **Hybrid**: implement at 300M first to validate the gradient-gating mechanism end-to-end (fast iteration), then scale to 3B for the paper-comparable evaluation (slow, load-bearing).

**Hybrid is probably right.** The 300M validation work is not wasted — it proves the implementation is correct before we commit substantial 3B compute. The 3B run is the paper-comparable demonstration. Patent timing aligns: non-provisional conversion deadline is 2027-05-14; plenty of runway for hybrid sequencing.

## Implications for the patent

1. **Reproducibility is in scope.** Code released; methodology is straightforward. Any future patent prosecution that needs to demonstrate the cognition-action alignment claim can cite the paper's methodology as the evaluation instrument used.
2. **Within-family finding strengthens the patent's training-recipe positioning.** The gap is architectural/training-recipe property, not scale. Our patent's training-recipe claim is therefore aligned with the bottleneck the paper identifies.
3. **The "no causal intervention" caveat is important.** Our patent doesn't make causal claims; the empirical demonstration would show correlation between KF training and reduced disagreement-rate. That's still strong, but the patent's claim language should be precise about "method that produces models showing [correlational signature]" rather than "method that causally closes the gap." Legal review point.
4. **The verbalized-self-assessment failure** (Appendix B) protects against a class of obvious-seeming alternative approaches. Our patent isn't competing with "just ask the model" because that's been shown to be insufficient. This is favorable.

## Reproducibility for actual implementation work

**Code repo:** github.com/chengez/Tool-Cognition-Action  
**Files:** format_input.py, extract_hidden_states.py, probe.py, raw_data/, probe weights (.npz), arithmetic generators  
**Stack:** Python ≥3.11, HuggingFace model_map.py registration  
**Steps to reproduce against a new model:**
1. Register the HF model in model_map.py
2. Run 10-sample N=10 T=0.7 pass to label necessity
3. Extract hidden states across all layers and last-20 tokens
4. Train per-(t,l) linear probes
5. Compute mismatch table + MCC heatmaps + cosine alignment map

**No closed-source dependencies. Mechanically tractable.** This is implementable in a focused work session once a target model checkpoint exists.

## Outstanding for next paired session

- Decide Path A vs Path B vs Hybrid for KF Gemma 4 e2b evaluation
- License clarification needed before code reuse (repo has no license stated — must contact authors or use methodology only without code)
- Compute budget assessment for 3B KF training if Path A or Hybrid chosen
- Identify which open-weight model is tractable at 3B with our infrastructure (Qwen3-4B candidate; Gemma 4 e2b is the original target; Llama-3.2-3B is the paper's smallest)
- Update `Technical-Work/Killing-Form/documentation/KF_ROADMAP.md` with the chosen path and explicit milestone for paper-methodology validation

---

**Status:** Primary read complete; KF-evaluation strategy decisions deferred to paired session with Clayton.

**Provenance:** Midday creative drive Day 110 Wednesday 2026-05-20. Research-agent assisted primary read with KF-evaluation focus. Full paper text saved at agent tool-results path for re-reads.