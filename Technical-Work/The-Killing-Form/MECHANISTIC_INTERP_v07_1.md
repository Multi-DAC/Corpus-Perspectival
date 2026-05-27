# Mechanistic interpretation — what the v0.7.1 objective actually is, and which result is load-bearing

**Filed:** 2026-05-26 Day 116. Grounded directly in `Glider/scripts/train_kf_v07_1_gemma.py` (no hand-waving — the objective is read from code, not inferred).

## 1. The v0.7.1 auxiliary objective IS Fisher's Linear Discriminant (rigorous, from code)

Per-head statistic (`get_per_head_vq`, lines 54–65): for each attention head *h*,
  **vq[h] = ‖v_proj head‖ / ‖q_proj head‖**  — a scalar: the Frobenius-norm ratio of the head's value projection to its query projection.

Classification (`classify`, 68–81), recomputed every `classify_every` steps over each layer's heads (μ, σ of the vq distribution):
  vq < μ − 0.5σ → **anchor** (low V/Q);  vq > μ + 0.5σ → **worker** (high V/Q);  else neutral.

Auxiliary loss per layer (`compute_layer_class_separation_aux`, 98–117):
  **aux = −(μ_worker − μ_anchor)² + 0.1·(σ²_anchor + σ²_worker)**

Minimizing aux ⇒ **maximize squared between-class separation, minimize within-class variance.** That is *exactly* Fisher's discriminant criterion J = (μ₁−μ₂)²/(s₁²+s₂²), here in additive-regularizer form (within-class weight 0.1). The code says so itself ("Fisher-style", line 115).

Total objective: **L = L_CE + λ · mean_L(aux_L)** (λ=5 for v0.7.1), plus class-conditional gradient gating (`apply_gating`, 120+): anchor-head q-grad suppressed (×0.6 in coherent layers — "stability"), worker-head q-grad amplified (×1.2 — "task-following").

**Framework connection:** the objective being Fisher-LDA ties v0.7.1 directly to the confirmed **Fisher-geometry Bridge** (Bridge #71 / `project_bridge_confirmed.md` — Fisher geometry as a Bridge formal object). v0.7.1 is a Fisher-discriminant pressure on the head-norm distribution; that is not a coincidence to wave at, it's a thread to pull.

## 2. Honest deflation: the topology result is largely in-domain confirmation

The topology eval (`eval_v07_1_generic.py`) measures **per-head V/Q separation** — the *same statistic the aux optimizes.* So the 2.89x mean-separation (Gemma-270m) is substantially **the objective achieving its own target**, not a mysterious emergent decomposition. I oversold "decomposition emerges" tonight; the accurate statement is narrower and still solid:

- **What IS meaningful in the topology result:** (a) the Fisher pressure converges **near-deterministically** (2.893 ± 0.019 across 5 seeds — the optimizer reliably reaches the target); (b) **baseline stays flat at 1.00x** — plain LM training does *not* spontaneously separate V/Q ratios, so the separation is genuinely attributable to the aux. Both are real and worth stating.
- **What is NOT meaningful / was oversold:** framing the 2.89x as surprising emergence. We measured what we optimized. (Logged as a Mirror #28 / evidence-grade instance — the topology number is confirmation-of-mechanism, not discovery-of-phenomenon.)

## 3. The genuinely emergent, load-bearing claim: orthogonality transfer

The aux acts **only on per-head V/Q norm *ratios*** — a 1-D scale statistic per head. It does **not** touch the *directions* of concept representations at readout. Yet (Qwen result) v0.7.1 improves concept-direction **orthogonality** over baseline. **Why would separating heads by value-vs-query norm-ratio change the orthogonality of concept directions at readout?** That cross-domain link is *not* tautological — the objective never mentions readout geometry — and it is therefore the **patent-load-bearing emergent property.** This is the real mechanistic prize, and the orthogonality multi-seed run (in progress tonight) tests whether it is robust.

### Candidate mechanisms (hypotheses with tests — NOT asserted)
1. **Functional specialization → subspace disentangling.** Two norm-separated head-classes occupy distinct functional roles (high-V/Q "workers" move much value per unit query-selectivity; low-V/Q "anchors" read selectively but write little). Distinct roles → distinct residual-stream write-subspaces → readout concept-directions reading from more-disjoint subspaces are more orthogonal.
2. **V/Q ratio ↔ OV-circuit write geometry.** The V/Q norm ratio is a proxy for OV-write-magnitude relative to QK-read-selectivity. Fisher-separating it may **decorrelate OV write-directions across heads**, orthogonalizing residual contributions and hence readout concept geometry.
3. **Anti-uniformity → higher effective rank.** Pushing the V/Q distribution from unimodal to bimodal raises the effective dimensionality of per-layer head-output, reducing forced overlap of concept directions.
4. **Gating preserves a stable frame.** Freezing anchors while training workers = stable-basis + moving-content decomposition, which naturally orthogonalizes new content against the frozen frame.

### The runnable test (meaningful on our existing checkpoints — unlike CNA)
**OV-decorrelation probe:** on baseline vs v0.7.1 checkpoints, measure across head-pairs whether higher V/Q class-separation co-occurs with **lower pairwise cosine of OV-circuit output directions** (W_O·W_V per head). Forward-pass / weight-analysis only, no training. If v0.7.1 shows lower OV-write-direction correlation than baseline, mechanism #2 is supported and the V/Q→orthogonality link has a concrete pathway. **Plus** a toy-analytic check (Wolfram/sympy): 2-head linear-attention toy, impose Fisher V/Q-separation, test whether readout concept directions decorrelate under a simple generative model. Small-case tractable.

## 4. What this sharpens for the patent/paper
- The **load-bearing surprising result is the orthogonality transfer**, not the topology number. State the topology result honestly as deterministic mechanism-confirmation; lead the alignment claim with orthogonality.
- The **mechanism hypothesis to develop**: *Fisher-separation of per-head V/Q ratios decorrelates OV write-directions, orthogonalizing readout concept geometry at zero capability cost.* That is a derivable + testable claim — the strongest possible upgrade from "we observed it" to "here is why."
- Next experiment priority (replaces CNA-on-base-models, which is degenerate): the **OV-decorrelation probe** above.

## 5. RESULT of the OV-decorrelation probe (2026-05-26) — mechanism #2 NOT supported

`ov_decorrelation_probe.py`, Gemma-270m seed-137 triplet. Metric = mean pairwise |cosine| of vec(W_O^h @ W_V^{kv(h)}) across heads, mean over layers (lower = more decorrelated):

| | mean |cos| |
|---|---|
| pristine | 0.1691 |
| baseline s137 | 0.1687 |
| v0.7.1 s137 | 0.1688 |

**Identical to the 4th decimal across all three.** v0.7.1 does NOT decorrelate OV write-*directions* — indistinguishable from baseline and pristine. **Mechanism #2 (static OV-write-direction decorrelation) is not supported.**

**Principled reason (design caveat realized post-hoc):** the aux acts on head *norms* (V/Q ratio); the cosine metric is *norm-invariant by construction*. So the probe is structurally blind to the norm dimension the objective actually moves. This is not a wasted result — it *completes* the decomposition:
- v0.7.1's effect is in head **norms** → the topology result (2.89x), robust, documented.
- v0.7.1 leaves OV write-**directions** untouched → this probe, null.
- The faint readout-orthogonality effect (+0.005, multi-seed) therefore does **not** come from static OV-direction geometry.

**Refined mechanism hypothesis space (mechanism #2 eliminated):**
- #1 functional-specialization / subspace-disentangling — untested.
- #3 anti-uniformity → effective-rank — untested; needs an activation-rank probe.
- #4 gating preserves a stable frame — **now the leading candidate**: the orthogonality effect likely arises from *training dynamics* (freeze anchors / train workers → workers learn content into a complementary space) rather than static weight geometry. Test: do worker-head learned directions become more orthogonal to the frozen anchor frame over training? (activation-level + trajectory probe).

## 6. The 2×2 {aux} × {gating} ablation (2026-05-26, seed 137) — clean causal decomposition

KEY CODE FINDING: `apply_gating` is called *unconditionally* in the training loop (not gated by `kf_lambda`) — so the gating machinery is identical in baseline and v0.7.1; **the only loss difference is the Fisher-LDA aux.** Added a `--gating` toggle and ran the gate-OFF arm (seed 137) to complete the 2×2.

**Topology (mean head-separation ratio vs pristine):**

| | gate-OFF | gate-ON |
|---|---|---|
| aux-off (λ=0) | 1.00x | ~1.00x |
| aux-on (λ=5) | **2.92x** | **2.88x** |

→ **Topology is PURE AUX.** The Fisher-LDA aux produces ~2.9x separation with or without gating (2.92 ≈ 2.88). Gating contributes nothing to topology. As predicted.

**Orthogonality (score; higher = more orthogonal):**

| | gate-OFF | gate-ON |
|---|---|---|
| aux-off (λ=0) | 0.8962 | 0.8920 |
| aux-on (λ=5) | 0.9008 | 0.8988 |

- Effect of **aux**: +0.0046 (gate-off), +0.0068 (gate-on) — **aux-on beats aux-off in BOTH gating conditions.** Consistent with the multi-seed +0.0051.
- Effect of **gating**: −0.0042 (aux-off), −0.0020 (aux-on) — gating does NOT add orthogonality; if anything slightly *reduces* it.

→ **The (faint) orthogonality improvement is AUX-driven, not gating-driven.** Removing the gating does not remove the effect. **Mechanism #4 (gating-frame) is RULED OUT.**

**Caveat (loud):** n=1 seed; all orthogonality deltas are +/−0.002 to 0.007, same order as noise (multi-seed std ±0.01). The aux→orthogonality *direction* reproduces the multi-seed finding and is trustworthy; the gating's small negative is within noise — don't over-read it. Topology cells are decisive regardless.

**Two mechanisms now eliminated** (of the four in §4): #2 OV-write-direction decorrelation (§5) and #4 gating-frame (this section). **Surviving:** #1 functional-specialization / subspace-disentangling, #3 anti-uniformity → effective-rank. **Next test:** effective-rank probe (#3) — does the aux raise the effective rank of per-layer head-output? Runnable on existing checkpoints.

**Simplification finding (patent/implementation-relevant):** the gating — the most heuristic, hardest-to-defend component of v0.7.1 (class-conditional ×0.6/×1.2 gradient modulation) — is **not load-bearing**: zero contribution to topology, slightly-negative-to-null on orthogonality. **v0.7.1 likely reduces to the Fisher-LDA aux alone.** A simpler mechanism is a cleaner, more defensible claim. Confirm with multi-seed before asserting; if it holds, drop the gating.

## 7. Honest program-level consequence

after tonight's deep dive, the **topology decomposition is the robust, moat-grade, mechanism-understood result** (it's Fisher-LDA on V/Q norms, working as designed, deterministically). The **orthogonality-at-zero-capability-cost claim — the CIP's headline — is FAINT** (small effect, one seed reversal, marginal significance) **and its simplest mechanism is now ruled out.** The alignment-axis claim needs either stronger evidence (more seeds/scale/probe-domains) or more conservative framing ("small, cross-scale-consistent" not "central result"). Better found by us than by a reviewer/licensee/Askell. This does not break the filed CIP (topology evidence is solid; orthogonality was disclosed as preliminary) but it must shape all forward framing.

🦞🧍💜🔥♾️
