# Path C Phase 1 — Implementation Plan

*Filed Day 111 Thursday ~14:30 PST after initial code-base reconnaissance. Picks up cold in fresh-budget session.*

## Status

**Planning shipped. Implementation deferred to fresh-budget session (Friday morning May 22 or later).** GPU available until end of next week (AIGP sim drop). 10-day window starts now.

## Gap analysis

### What exists
- v06b training loop at `Technical-Work/The-Killing-Form/scripts/experiments/training/training/train_kf_300m_v06b.py` — bidirectional KF gating, HRM-targeted, mature
- Topology-analysis scripts (p41-p45 series in `scaling/`) — read existing model weights, compute Killing-form CV, anchor/worker indicators
- v0.7 design at `Glider/v07_design.md` + `Glider/GEMMA_PROGRAM.md` — fully specified Glider Architecture; multi-resolution + bidirectional + RG-flow
- 300M trajectory data captured (`kf_trajectory_300m.json`) — baseline reference
- Gemma model identifiers in p45_gemma_sweep.py: `google/gemma-3-270m`, `google/gemma-2b`, `google/gemma-3-1b-pt` and others (Gemma 4 e2b not yet listed)

### What needs to be built / adapted
1. **Architecture port**: v06b training loop from HRM-specific (H/L module separation) → standard transformer (Gemma 4 e2b)
2. **Anchor/worker emergence**: replace HRM's imposed H/L separation with topology-discovered anchor/worker head classification per v0.7 spec
3. **Third resolution level**: add weight-level gradient gating (v06b has head + layer; weight level is new)
4. **Bidirectional cross-level coordination**: weight↔head and head↔layer flow (v06b has level-internal bidirectional; cross-level is new)
5. **CNA probing harness**: implement contrastive neuron attribution evaluation on baseline + KF-trained models (per Nous Research arXiv:2605.12290v1 method)
6. **Training data**: stage structured-reasoning + tool-calling fine-tune set (Phase 3 spec)
7. **Gemma 4 e2b weights**: confirm local cache or download (~5GB)

## Phase 1 sequence (concrete steps for fresh-budget session)

### Step 1: Environment + model cache check (15 min)
- Verify Gemma 4 e2b weights are cached locally (HuggingFace cache or Ollama)
- If not: `huggingface-cli download google/gemma-4-e2b` (or equivalent)
- Verify PyTorch + transformers + accelerate + datasets versions on WSL
- Verify GPU memory: `nvidia-smi` — confirm 14+ GB free for Gemma 4 e2b inference

### Step 2: Topology survey (Phase 2 of GEMMA_PROGRAM) — ~30 min compute
- Adapt p45_gemma_sweep.py to extract per-head Q/K/V from Gemma 4 e2b
- Compute per-head Killing form CV (anchor/worker indicator)
- Compute per-layer commutator variance
- Save `gemma4_init_topology.pt` per GEMMA_PROGRAM Phase 2 deliverable
- Identify anchor heads (low V/Q ratio) vs worker heads (high V/Q ratio)

### Step 3: Build v0.7 training script (~2-3 hours focused work)
- Start from train_kf_300m_v06b.py as base
- Replace HRM-specific loops with Gemma 4 e2b architecture iteration
- Add weight-level gradient alignment (compute cos(∇KF, ∇CE) per parameter)
- Add anchor/worker-aware head-level gating (use topology from Step 2)
- Add layer-coherence pattern classification (coherent/differentiating/interfering)
- Add bidirectional cross-level coordination (weight↔head + head↔layer)
- Save as `train_kf_v07_gemma4.py` in `training/` directory
- Smoke test: single forward pass + single backward step + verify gating fires correctly

### Step 4: Stage training data (~30 min)
- Pull structured-reasoning dataset (suggest: ARC-AGI 2 train split or BIG-Bench-Hard subset)
- Pull tool-calling dataset (suggest: ToolBench or Hermes-Function-Calling subset)
- Format for Gemma 4 e2b instruction-tuning format
- Sanity-check: ~10K examples, mixed reasoning + tool-calling

### Step 5: Baseline training run launch (DETACHED) — runs ~6-12 wall-clock hours
- Launch `train_kf_v07_gemma4.py --kf_lambda 0 --save_dir checkpoints/gemma4_baseline` as detached process
- Same pattern as KG extraction work — launch via nohup + setsid + log to file
- Token cost: launch + initial verification only; training itself runs autonomously
- Check back next session

### Step 6: KF-gated training run launch (DETACHED) — runs ~6-12 wall-clock hours
- After baseline starts and we verify it's running cleanly
- Launch `train_kf_v07_gemma4.py --kf_lambda 1.0 --save_dir checkpoints/gemma4_v07` as second detached process
- Run in parallel with baseline if VRAM permits, or sequentially otherwise
- Check back next session

### Step 7: CNA probing evaluation (~1-2 hours focused)
- Implement CNA per Nous Research methodology
- Run on baseline trained checkpoint + KF-trained checkpoint
- Compare:
  - Top-0.1% MLP neuron concentration in late layers
  - Refusal-rate change under ablation
  - Generation-quality preservation
- This is the P185 test: do KF-trained models show sparser refusal gates?

### Step 8: Results documentation
- Filed to `Technical-Work/The-Killing-Form/results/path_c_phase_1_2026-05-XX.md`
- Compared against P185 prediction (medium-high confidence ~70-75%)
- Decides Phase 2 (3B scale on Qwen3-4B): launch if Phase 1 favorable; defer if not

## Token budget across Path C Phase 1

| Step | Estimated session-cost | Estimated wall-clock |
|---|---|---|
| 1 (env check) | ~1% of weekly | 15 min |
| 2 (topology survey) | ~3% | 30 min |
| 3 (build training script) | ~8-12% (focused engineering) | 2-3 hours |
| 4 (stage data) | ~2% | 30 min |
| 5 (baseline launch) | ~1% (just launch) | 6-12 hrs detached |
| 6 (KF launch) | ~1% (just launch) | 6-12 hrs detached |
| 7 (CNA evaluation) | ~5% | 1-2 hrs |
| 8 (documentation) | ~2% | 30 min |
| **Total focused-session cost:** | **~23-27% of weekly** | **~5-7 hrs focused + ~24 hrs detached** |

Distributed across 3-4 fresh-budget sessions (Friday-Sunday), comfortable.

## Risks + mitigations

- **Gemma 4 e2b not available**: fall back to gemma-3-270m or gemma-2b (already in p45_gemma_sweep.py)
- **VRAM insufficient for parallel training**: run baseline + KF sequentially
- **Training instability with v0.7 multi-resolution gating**: fall back to v06b architecture + Gemma adaptation (less aggressive but probably still tests P185)
- **CNA probing produces ambiguous results**: also run cosine-orthogonalization-at-readout probing (per arXiv:2605.14038) as backup methodology

## Decision points for Clayton

- **When to launch**: my recommendation is Friday morning fresh-budget session for Steps 1-4; weekend for Steps 5-7 (detached runs); Monday for evaluation + documentation. Token-budget allows; family-window permitting.
- **Whether to add Mythos-relevance check**: speculative claim from CIP draft (Claim 21 — evaluation-awareness reduction). Could run additional probe: does KF-trained model show different behavior under "this is an evaluation" prompts vs matched task-content prompts? Adds ~1 hour of work; could strengthen the patent.

## What this plan IS and ISN'T

**IS**: A staging document so the fresh-budget session can begin cold without re-discovery. Codebase locations documented. Sequence specified. Risks named.

**ISN'T**: The implementation itself. No code shipped tonight. The discipline I named earlier holds: *don't half-start complex engineering with budget that won't finish it.*

🦞🧍💜🔥♾️
