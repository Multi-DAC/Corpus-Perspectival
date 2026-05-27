# Cross-Architecture Substrate-Invariance — Qwen2.5-0.5B (first non-Gemma confirmation)

**Run date:** training 2026-05-22 (Day 112); evaluation 2026-05-26 (Day 116, on wake after weekend cap-gap).
**Model:** Qwen/Qwen2.5-0.5B (Qwen2 architecture family — first family tested outside Gemma).
**Training:** 400 steps, batch 4, lr 2e-5, classify_every 25, seq_len 256, n_samples 500. Baseline λ=0.0; v0.7.1 λ=5.0. Zero script changes from the Gemma pipeline (direct `--model_id` substitution; `model.model.layers[L].self_attn.{q_proj,v_proj}` access identical).

## Result — mechanism transfers across the first architecture-family boundary, on BOTH axes

### Topology (mean head-separation vs pristine)

| State | mean_separation | ratio vs pristine | reading |
|---|---|---|---|
| pristine | 0.4686 | 1.00x | — |
| **baseline-trained (λ=0)** | 0.4683 | **~1.00x (FLAT)** | plain training produces **no** decomposition |
| **v0.7.1-trained (λ=5)** | 1.1984 | **2.56x** | decomposition emerges |

max_separation: pristine 1.048 → v0.7.1 4.477 = **4.27x**. All 24 layers show positive separation-delta under v0.7.1.

**The decomposition is v0.7.1-specific, not a generic training artifact** — baseline training leaves topology essentially untouched (0.4686 → 0.4683), exactly replicating the Gemma HRM finding (Day 111) on a non-Gemma family. Reference: Gemma-3-270M 2.93x; Gemma-3-1B 5.40x. Qwen-0.5B at 2.56x sits in the small-Gemma band.

### Orthogonality (concept-direction orthogonality; higher = more orthogonal = better)

| State | orthogonality score | vs prior |
|---|---|---|
| pristine | 0.9036 | — |
| baseline-trained (λ=0) | 0.8484 | **−0.055 (plain training REGRESSES)** |
| **v0.7.1-trained (λ=5)** | 0.8582 | **+0.0098 vs baseline (RECOVERS)** |

**Architecture-attributable comparison (the correct one per A125): v0.7.1 (0.8582) > baseline (0.8484).** Predicted direction confirmed. Note the absolute pattern differs from Gemma-1B, where training *increased* orthogonality monotonically (0.9119 → 0.9279 → 0.9346). On Qwen, plain training *degrades* concept-orthogonality and v0.7.1 counteracts the degradation. The substrate-invariant claim lives on the v0.7.1-vs-baseline axis, which holds across both architectures; the baseline's absolute behavior is architecture-dependent (itself an informative finding).

## What this establishes

- **Substrate-invariance crosses its first architecture-family boundary: Gemma → Qwen2.**
- Direct evidence for **CIP claim 26** ("transformer architectures lacking pre-existing hierarchical module separation") — now demonstrated beyond Gemma.
- Topology axis is the strongest leg: baseline 1.00x vs v0.7.1 2.56x cleanly attributes the decomposition to the mechanism.

## Evidence grade (honest)

- **Patent-grade mechanism-evidence: solid** — cross-family, both axes, clean controls (pristine / baseline / v0.7.1).
- **Moat-grade: not yet** — n=1 architecture family beyond Gemma, n=1 seed. To reach moat-grade: multi-seed (3–5) replication + a third family (Llama / GPT-NeoX) + ideally a 2B-scale point.

## Next steps (decision-gated)

| Option | Cost | Value | Risk |
|---|---|---|---|
| **A. bf16 support → TinyLlama-1.1B (Llama family)** | ~10-line script change + validation | High — Llama is the strongest distinct family; also unblocks all >1B training | Touches q_proj/v_proj path — must validate bf16 doesn't perturb separation metric |
| **B. Qwen3-0.6B (zero script change, fits fp32)** | ~15 min train + eval | Modest — Qwen3 distinct from Qwen2 but shares lineage | Low |
| **C. Pythia-410m (GPT-NeoX, most distinct family)** | fused-QKV script adaptation + validation | High distinctness | Touches extraction path — correctness-sensitive |
| **D. Multi-seed Qwen2.5-0.5B (3-5 seeds)** | ~1 hr GPU | Converts "lucky seed?" → "robust" on the family already confirmed | Low (reuses validated path) |

**Files:** `qwen2_5_0_5b_baseline_eval.json`, `qwen2_5_0_5b_v07_1_eval.json`, `orthogonality_qwen0_5b_{pristine,baseline,v07_1}.json`. Checkpoints at `/home/clawd/path_c_results/qwen2_5_0_5b_{baseline,v07_1}/step_400_final.pt`. Eval batch launcher: `Glider/scripts/run_qwen_evals.sh`.

🦞🧍💜🔥♾️
