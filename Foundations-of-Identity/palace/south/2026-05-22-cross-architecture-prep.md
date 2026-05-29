# Cross-architecture replication prep — WSL cache audit + script-adaptation map

**Filed:** 2026-05-22 Day 112 Friday morning Do Be Talk Be Do drive (~09:15 PST). Pre-sprint engineering work that compresses Tuesday-Clawd's cross-architecture sprint (#3 on the 14-day path's 7-load-bearing list). P193 anticipation was substantially wrong on friction estimate; this document corrects.

## Cache audit (already-available models)

The WSL HuggingFace cache at `~/.cache/huggingface/hub/` already contains models from **5 distinct architecture families**. No downloads required for cross-architecture work.

| Family | Cached at small scale | Cached at 1B-equiv | Cached at 2B+ |
|---|---|---|---|
| **Gemma (gemma3)** | gemma-3-270m (assumed; verify) | gemma-3-1b-pt (verified Day 111) | gemma-2-2b, gemma-2-9b |
| **Llama (llama)** | — | TinyLlama-1.1B-Chat | SmolLM3-3B |
| **Qwen2 (qwen2)** | Qwen2.5-0.5B | Qwen2.5-1.5B | Qwen2.5-3B-Instruct, Qwen2.5-7B |
| **Qwen3 (qwen3)** | Qwen3-0.6B | Qwen3-1.7B | Qwen3-4B, Qwen3-8B |
| **GPT-NeoX (gpt_neox)** | Pythia-70m, 160m, 410m | Pythia-1b, 1.4b | Pythia-2.8b |
| **GLM** | — | — | glm-4-9b-chat |
| **Bloom** | bloom-560m | — | — |
| **Cerebras-GPT** | Cerebras-GPT-111M | — | — |
| **OPT** | — | opt-1.3b, opt-iml-1.3b | — |
| **DeepSeek** | — | DeepSeek-R1-Distill-Qwen-1.5B | — |

## Architecture-adaptation map for `train_kf_v07_1_gemma.py`

The script's head-classification + gating logic reaches into the model via two access points:
- `model.model.layers[L].self_attn.q_proj.weight` (Q projection per layer)
- `model.model.layers[L].self_attn.v_proj.weight` (V projection per layer)

| Family | Access pattern | Script changes needed |
|---|---|---|
| **Gemma 3** | `model.model.layers[L].self_attn.q_proj` / `v_proj` | **None — current target** |
| **Llama** (TinyLlama, SmolLM3) | `model.model.layers[L].self_attn.q_proj` / `v_proj` | **NONE — direct substitution via `--model_id`** |
| **Qwen2 / Qwen3** (Qwen2.5, Qwen3) | `model.model.layers[L].self_attn.q_proj` / `v_proj` | **NONE — direct substitution via `--model_id`** |
| **Mistral** (not currently cached but standard) | `model.model.layers[L].self_attn.q_proj` / `v_proj` | **NONE — direct substitution via `--model_id`** |
| **GPT-NeoX (Pythia)** | `model.gpt_neox.layers[L].attention.query_key_value.weight` (FUSED QKV: shape [3*hidden_size, hidden_size]) | **ADAPTATION REQUIRED** — split fused tensor into Q/K/V slices; different layer-list path |
| **GLM** | not verified; likely needs adaptation | flag for future |
| **OPT** | `model.decoder.layers[L].self_attn.{q_proj, k_proj, v_proj}` | **path adaptation** (decoder vs model.model.layers) |
| **Bloom** | fused QKV like GPT-NeoX | adaptation required |

**Load-bearing finding (corrects P193 anticipation):** *For three of the five major architecture families (Llama / Qwen2 / Qwen3 / Mistral), the training script needs ZERO modifications.* Only `--model_id` parameter needs to change. P193 estimated "~3 hr GPU including script adaptation"; actual is ~3 hr GPU with no script work at all (for those families).

## Recommended Tuesday-Clawd cross-architecture sprint plan

**Order of operations (ETA: ~4-5 hours total wall-clock, ~3 hours GPU):**

1. **Smallest-cross-architecture pair first** (~45 min): Qwen2.5-0.5B baseline + v0.7.1 vs Gemma-3-270M baseline + v0.7.1 already-done. This is the cleanest substrate-invariance test at small scale.
2. **Mid-scale pair** (~1.5 hr): Qwen2.5-1.5B baseline + v0.7.1 vs Gemma-3-1B already-done. Direct comparison of v0.7.1 effect at ~1B scale across two arch families.
3. **Llama-family confirmation** (~1.5 hr): TinyLlama-1.1B baseline + v0.7.1. Third architecture family confirmation of substrate-invariance.
4. **(Optional, lower priority) Pythia cross-arch** (~2 hr including script adaptation): Pythia-410m baseline + v0.7.1 with fused-QKV adaptation. This is the *hardest* substrate test (most-different architecture from Gemma) but requires the script work P193 anticipated.

**Recommended capability + alignment-orthogonality eval ordering:**
- Reuse `eval_v07_1_1b.py` with `--model_id` parameter substitution (need to verify the script supports this; may need small edit to remove gemma-3-1b hardcoding)
- Reuse `cosine_orthogonality_probing.py` with `--model_id` substitution (already parameterized correctly per the script source)
- Reuse `eval_capability_rerun_bf16.sh` with model paths updated for each arch

## What this compresses for the Tuesday sprint

P193 estimated cross-architecture work as ~3 hr GPU plus script adaptation friction. **Revised estimate: ~3-4 hr GPU + zero script work for the first three families.** This is a 30-50% compression of the sprint's #3 line-item, and converts cross-architecture from "moderate friction" to "drop-in extension of existing pipeline."

**Substantive consequence for the 14-day path:** the cross-architecture substrate-invariance evidence can land on Tuesday in one session, not two. If Qwen2.5 + TinyLlama both show the v0.7.1 mechanism transferring (orthogonality monotonic improvement, capability held), the substrate-invariance claim crosses 3 architecture families and the patent's claim 26 language "transformer architectures lacking pre-existing hierarchical module separation" becomes substantively demonstrated across the architectural landscape, not just gemma-specific.

## Open verification (Tuesday-Clawd to confirm before training)

1. ~~Verify `eval_v07_1_1b.py` doesn't hardcode `google/gemma-3-1b-pt`; if it does, add `--model_id` parameter~~ **DONE 2026-05-22 — shipped `eval_v07_1_generic.py` with `--model_id`/`--ckpt`/`--output` parameters.**
2. ~~Verify the per-layer access `model.model.layers[L].self_attn.{q_proj, v_proj}` works on Qwen2.5-0.5B with a quick interactive forward pass before launching training~~ **DONE 2026-05-22 — empirically confirmed: Qwen2.5-0.5B training + topology eval + orthogonality probe all worked end-to-end with zero script changes.**
3. ~~Verify VRAM headroom for Qwen2.5-0.5B training with v0.7.1 aux loss (should be comfortable; 0.5B model + AdamW ≪ 1B fit)~~ **DONE 2026-05-22 — 0.5B trained without issue.**

## VRAM ceiling discovered (2026-05-22 ~11:25 PST OOM event)

**The training script's memory ceiling on RTX 5080 (15.92 GiB) with full fp32 + AdamW optimizer is ~1B parameters.**

Empirical data:
- Gemma-3-1B (1B params): trains OK
- Qwen2.5-1.5B (1.5B params): **OOM at AdamW initialization**
- Gemma-2-2B (2.5B params): OOM (previously known)

Reasoning: full fp32 = 4 bytes/param weights; AdamW carries 2 additional optimizer states per param (m, v) = 8 bytes/param; total 12 bytes/param for weights+optimizer alone, plus gradients (4 bytes/param) = 16 bytes/param. For 1.5B params: 1.5e9 × 16 = 24 GB, before activations. Hard ceiling.

**Required fix before any model >1B trains:** add bf16 mixed-precision support to `train_kf_v07_1_gemma.py` OR add 8-bit AdamW via bitsandbytes OR add LoRA wrapping.

**Bf16 is simplest fix:** ~5-10 lines of script change (cast model to bfloat16, switch AdamW to bf16-compatible variant). Should be ~half the VRAM usage; opens up training through ~3B param scale.

**Sprint plan revised — VRAM-constrained execution order:**

| # | Model | Status | VRAM strategy |
|---|---|---|---|
| 1 | Qwen2.5-0.5B | ✓ done 2026-05-22 | fp32 fits |
| 2 | TinyLlama-1.1B (1.1B params) | Tuesday | fp32 marginal — try first, fall back to bf16 |
| 3 | Add bf16 support to training script | Tuesday | ~10 lines of script work |
| 4 | Qwen2.5-1.5B with bf16 | Tuesday post-bf16 | bf16 required |
| 5 | Gemma-2-2B retry with bf16 | Tuesday post-bf16 | bf16 required |
| 6 | Qwen2.5-3B / SmolLM3-3B / Pythia-2.8B | post-bf16 | bf16 likely required |

**Lesson:** pre-flight checks must work in BOTH directions — when friction is overestimated (this morning's cache discovery), AND when friction is underestimated (this midday's VRAM OOM). Verify VRAM headroom explicitly for any model not previously trained on this hardware.

## Connections

- P193 (Cross-architecture replication readiness) — *this document corrects the friction estimate*
- 14-day sprint path (handoff Tuesday work item #3) — substantively compressed
- LC23 candidate (cross-architecture work IS itself an LC23-pattern probe) — substrate-spread evidence
- L17 (substrate-invariance) — cross-architecture is the strongest possible test of the substrate-invariance claim
- CIP claim 26 (emergent topology decomposition in transformer architectures lacking hierarchical module separation) — cross-architecture results would substantively demonstrate this claim language across architectural diversity

🦞🧍💜🔥♾️
