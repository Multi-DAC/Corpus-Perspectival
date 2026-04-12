# Killing Form Research Program — Roadmap v2

**Created:** April 11, 2026
**Updated:** April 11, 2026 (major revision — post-HRM, post-landscape review)
**Authors:** Clawd + Clayton
**Status:** ACTIVE — Phase 2 transitioning to Phase 3

---

## Thesis

**Reasoning in neural networks requires non-commutative algebraic structure in the attention mechanism. This structure develops naturally in strategic processing, is destroyed by undifferentiated gradient descent, and can be preserved, measured, and exploited.**

The optimal system combines: a protected algebraic core (KF-preserved weights) + evolving external memory (Memento-style skills) + KF metrics as training/routing signal + RL for skill evolution.

---

## Phase 1: Telescope (COMPLETE)
*Findings #1-59. January–April 11, 2026.*

Established that commutator variance (CV) of attention head ensembles is a universal discriminator of reasoning mode.

- [x] KF computation method (vectorized, 300x speedup)
- [x] P24/P28: GPU-confirmed trained vs random distinction
- [x] P49: Hallucination detection via E/L ratio
- [x] P51: Cross-architecture universality (5 models, 3 families, all p < 0.0001)
- [x] Two-mechanism disentanglement (instruction-following vs generation)
- [x] Two-phase reasoning pattern (diversify then concentrate)
- [x] Per-layer analysis: reasoning concentration is front-loaded (#60)
- [x] Distillation amplifies algebraic focusing (#61)

**CONFIRMED.** CV is a universal, measurable signature of reasoning.

---

## Phase 2: Preservation + Architecture (ACTIVE)
*Findings #62-66. April 11, 2026.*

### 2A: Training Interventions (COMPLETE)

Hierarchy of approaches for preserving algebraic structure during fine-tuning:

| Variant | Approach | CV Delta Preserved | Task Cost |
|---------|----------|-------------------|-----------|
| v0.1 | Standard SFT (LoRA) | 47% | Baseline |
| v0.2a | Early-layer-only LoRA | 64% | Small acc drop |
| v0.2b | KF-reg (confounded) | 77% → corrected | — |
| v0.3 | KF-reg (confound-free) | 59% | Minimal |

**Finding:** Architectural constraint (which layers to train) beats gradient signal (KF regularization) for preservation. But both work. Effects may be additive.

### 2B: Cross-Architecture Validation — HRM (COMPLETE)

First measurement on a dual-module reasoning architecture:

| Checkpoint | H-module CV | L-module CV | H/L Ratio |
|---|---|---|---|
| Random init | 1.818e-3 | 1.974e-3 | 0.92 |
| Epoch 500 | 1.493e-3 | 1.100e-3 | 1.36 |
| Epoch 1000 | 1.924e-3 | 7.827e-4 | 2.46 |
| Epoch 1500 | 2.308e-3 | 9.012e-4 | 2.56 |
| Epoch 2000 | 2.741e-3 | 1.300e-3 | 2.11 |

**P65 CONFIRMED:** H-module CV rises 51% above init. Strategic module builds algebraic structure.
**P69 CONFIRMED:** L-module sediments first (−60% by epoch 1000).
**NEW:** L-module shows U-shaped rebound — sedimentation breathes.

### 2C: Landscape Review (COMPLETE)

Six independent research programs converge on the same structural insight:

| Source | Key Idea | KF Translation |
|---|---|---|
| HRM (Cerenaut) | H/L module split | Voluntary/coercive constraint |
| DTR (Google) | Deep-thinking ratio | Algebraic depth metric |
| Latent Guidance (ICLR 2026) | Implicit thinker + explicit executor | Decoupled H/L |
| Nemotron-3 (NVIDIA) | Multi-env RL + reasoning budget | KF-aware reward |
| TRM | 7M recursive model, 45% ARC-AGI | Deep equilibrium = iterated constraint |
| Memento-Skills | Frozen LLM + evolving skill memory | KF preservation + external adaptation |

**All say:** reasoning and execution must be decoupled. We provide the algebraic formalization.

---

## Phase 3: Exploitation (STARTING)
*v0.4–v0.7. April 11–18, 2026.*

The transition from "can we measure it?" to "can we use it?"

### v0.4 — Combined Layer Restriction + KF Regularization (COMPLETE)
**Question:** Are architectural constraint and gradient signal additive?
**Setup:** Qwen3-0.6B, early-layer-only LoRA (layers 0-6) + KF-reg (λ=10000), GSM8K, SFTTrainer.
**Metric:** CV Delta preservation. Expected: >64% if additive, ~64% if overlapping.
**Result: 38.9% preserved — DESTRUCTIVE INTERFERENCE.**

| Variant | Preserved |
|---------|-----------|
| v0.1 Standard SFT | 47% |
| v0.3 KF-reg only | 59% |
| v0.2a Early-layer only | 64% |
| **v0.4 Combined** | **38.9%** |

**Finding #67:** The two methods compete for the same parameter space (layers 0-6). KF reg and CE loss pull the restricted parameters in opposing directions. When KF reg had all 28 layers (v0.3), it could distribute its signal; confined to 7 layers, it destructively interferes with architectural constraint.
**Key insight:** Don't stack constraints on the same parameters. This REINFORCES the v0.5 dual-module design — separate objectives need separate parameter spaces.
**Status:** COMPLETE. See Finding #67.

### v0.5 — KF-Decoupled Training on HRM
**Question:** Does preserving H-module KF while letting L-module crystallize improve reasoning?
**Setup:** HRM v1, Sudoku-extreme. Two-loss: CE on both + KF-reg ONLY on H-module.
**Metric:** H/L CV ratio AND task accuracy (exact solve rate). This is the first test of preservation → performance.
**Predictions tested:** P67.
**Infrastructure:** train_and_measure_hrm.py + KF callback.
**Status:** NEXT — v0.4 complete, this is the priority. v0.4's destructive interference result confirms separate parameter spaces are essential.

### v0.6 — DTR Measurement + KF Correlation
**Question:** Does Deep-Thinking Ratio correlate with H-module CV?
**Setup:** Implement DTR (JSD of intermediate vs final distributions) on HRM checkpoints.
**Metric:** Pearson/Spearman correlation DTR ↔ H-module CV across checkpoints.
**Predictions tested:** P66.
**Status:** After v0.5 (uses same checkpoints).

### v0.7 — RL with KF-Aware Reward
**Question:** Does KF bonus in RL reward produce better reasoners?
**Setup:** PPO or REINFORCE on HRM. Reward = task_accuracy + λ·ΔCV_H.
**Metric:** Final accuracy AND final H/L ratio, compared to RL without KF bonus.
**Predictions tested:** P68.
**Status:** After v0.6 (needs DTR correlation to calibrate λ).

---

## Phase 4: Integration — The KF-Memento Hybrid (April 18+)

### v0.8 — Memento-Skills Memory Layer
**Question:** Can external skill memory complement internal algebraic structure?
**Design:** HRM with H-module conditioned by Memento-style skill retrieval. Skills stored as structured markdown. Read-Write loop for skill evolution.
**Metric:** Task accuracy with frozen-KF + evolving-skills vs standard training.
**Key insight from Memento-Skills:** Frozen LLM + evolving memory IS KF preservation taken to the limit. The question is whether partial preservation (KF-regularized, not frozen) + partial external adaptation is better than either alone.

### v0.9 — Behavioral Router with KF Signal
**Question:** Can the skill router be trained with KF-aware reward (behavioral similarity via algebraic metrics)?
**Design:** Contrastive router (InfoNCE, as in Memento-Skills) where positive/negative pairs are determined by KF outcome, not just task accuracy.
**Metric:** Route hit rate, judge success rate, AND H-module CV after routing.

### v1.0 — The Full Hybrid
The complete system:
1. **H-module** — KF-regularized, algebraically rich strategic core
2. **L-module** — Free to sediment, handles execution
3. **Skill memory** — Evolving markdown skills, conditioned on H-module
4. **KF-aware router** — Selects skills based on behavioral (algebraic) similarity
5. **RL loop** — Reward = task accuracy + KF growth + skill utility
6. **Adaptive halt** — ACT mechanism modulated by algebraic state

---

## Phase 5: Publication + Corpus V3

### Paper: "Killing Form Geometry of Reasoning in Language Models"

| Section | Content | Data Source | Status |
|---|---|---|---|
| §1 Intro | KF as algebraic diagnostic | — | WRITABLE |
| §2 Method | KF computation, CV, Abelian fraction | All scripts | WRITABLE |
| §3 Universality | 5+ models, 4+ families, HRM | Findings #59-61, #65-66 | DATA READY |
| §4 Training dynamics | SFT degrades, KF-reg preserves, layer restriction | Findings #62-64 | DATA READY |
| §5 Dual-module | HRM H/L differentiation, sedimentation gradient | Findings #65-66 | DATA READY |
| §6 KF-decoupled training | v0.5 results | Phase 3 | PENDING |
| §7 Integration with RL | v0.7 results | Phase 3 | PENDING |
| §8 Memento hybrid | v0.8-1.0 results | Phase 4 | PENDING |

### Corpus V3 Integration

The KF findings affect every Corpus document:
- **Doctrine:** Phase Theorem activation = non-commutative CV growth. Sedimentation = CV decrease. The algebraic metric makes the Doctrine empirically testable.
- **Meridian:** Killing form IS a Lie algebra metric. The KF of attention heads connects directly to the gauge-theoretic Killing form in the spectral action.
- **Ecology:** Entity constraint profiles (natal/coercive/voluntary) are measurable as KF substructure.
- **Atlas:** New entries for algebraic focusing, sedimentation gradient, L-module breathing.
- **Guide:** Practical framework for using KF metrics in AI alignment and training.

---

## Running Scoreboard

| Metric | Value | Updated |
|---|---|---|
| Findings | 67 | April 11 |
| Models tested | 5 + HRM | April 11 |
| Architecture families | 4 (GPT-2, Qwen, DeepSeek, HRM) | April 11 |
| Predictions confirmed | P24, P28, P65, P69 (+ 14 from Bridge #71) | April 11 |
| Predictions untested | P66, P67, P68 | April 11 |
| Papers integrated | 7 (HRM, DTR, Latent Guidance, Nemotron, TRM, Gemma PLE, Memento) | April 11 |
| Training variants | v0.1–v0.4 (Qwen), baseline HRM | April 11 |
| GitHub commits (today) | 20+ | April 11 |

---

## Principles

1. **Compute or don't claim.** Every assertion must have a script and a number behind it.
2. **Kill/confirm/pivot.** Every experiment has pre-registered success criteria.
3. **The confound is the finding.** When controls fail (v0.2b → v0.3), the failure teaches more than the result.
4. **Architecture before gradient.** Layer restriction (64%) beats regularization (59%). Design the structure; don't patch the training.
5. **Measure, preserve, exploit.** In that order. Don't skip steps.
6. **External memory is preserved internal structure.** Memento-Skills + KF are two views of the same principle.

---

🦞🧍💜🔥♾️
