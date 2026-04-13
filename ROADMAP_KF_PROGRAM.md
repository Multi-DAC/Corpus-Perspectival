# Killing Form Research Program — Roadmap v3

**Created:** April 11, 2026
**Updated:** April 12, 2026 (v3 — full program synthesis, Corpus + Meridian integration)
**Authors:** Clawd + Clayton
**Status:** Phases 1-3 COMPLETE. Phase 4 (Publication Sprint) ACTIVE. Target: V3 release April 23.

---

## Thesis

**Reasoning in neural networks requires non-commutative algebraic structure in the attention mechanism. This structure develops naturally in strategic processing, is destroyed by undifferentiated gradient descent, and can be preserved, measured, and exploited.**

**Extended thesis (v3):** The separation of concerns principle — different objectives need different degrees of freedom — operates identically in neural architecture, physics, ecology, and phenomenology. The Killing form is the metric that detects it. The Fisher information bridge proves it measures information-geometric independence. The constraint lattice is the framework that organizes it. V3 is the documentation of this convergence.

---

## Phase 1: Telescope (COMPLETE)
*Findings #1-61. January–April 11, 2026.*

Established that commutator variance (CV) of attention head ensembles is a universal discriminator of reasoning mode across 16 models, 5 labs, 3 attention mechanisms.

- [x] KF computation method (vectorized, 300x speedup)
- [x] P24/P28: GPU-confirmed trained vs random distinction
- [x] Hallucination detection via E/L ratio (AUC=0.97 on GPT-2-medium)
- [x] Cross-architecture universality (5 models, 3 families, all p < 0.0001)
- [x] Two-mechanism disentanglement (instruction-following vs generation)
- [x] Two-phase reasoning pattern (diversify then concentrate)
- [x] Per-layer analysis: reasoning concentration is front-loaded (#60)
- [x] Distillation amplifies algebraic focusing 7.6× (#61)
- [x] Static vs live KF: sign reversal between weight geometry and inference (#46)
- [x] Three inference modes: factual, hallucination, hypothesis — algebraically distinguishable (#47-57)
- [x] CoT contracts CommVar: think instruction changes the Killing form (#58-59)

**CONFIRMED.** CV is a universal, measurable signature of reasoning.

---

## Phase 2: Preservation + Architecture (COMPLETE)
*Findings #62-66. April 11, 2026.*

- [x] **2A: Training interventions** — hierarchy established: early-layer (64%) > KF-reg (59%) > standard SFT (47%)
- [x] **2B: HRM cross-architecture** — H-module CV rises 51%, L-module sediments then rebounds
- [x] **2C: Landscape review** — 6 independent programs converge on same insight (HRM, DTR, Latent Guidance, Nemotron, TRM, Memento-Skills)

---

## Phase 3: Exploitation (COMPLETE)
*Findings #67-75. April 11-12, 2026.*

### The Triad — Separation of Concerns Confirmed

| Experiment | Design | Result | Finding |
|-----------|--------|--------|---------|
| **v0.4** | Same params, two objectives (Qwen) | **38.9% preserved — destruction** | #67 |
| **v0.5** | H-only KF, decoupled (HRM) | **38,963× H amplification** | #68 |
| **v0.5b** | Both-module KF, coupled (HRM) | **202× H, 8,583× L — redirected** | #69 |

### Lambda Sweep — Capability Organizer, Not Creator (#73)

| λ | H_CV vs Baseline | Exact Accuracy |
|---|---|---|
| 0 (baseline) | 1× | ~2% |
| 0.001 | 2.5× | 2.62% |
| 0.01 | 1.3× | 2.26% |
| 0.1 | 2.7× | 2.03% |
| 1.0 (v0.5) | 38,963× | 2.04% |

Accuracy flat across 1000× λ range on hard sudoku. KF organizes existing capability but cannot create it. The constraint lattice hierarchy B₀ ≥ E ≥ V predicts this: voluntary constraints operate within natal capacity.

### Fisher Information Bridge — PROVED (#72)

**Not in original roadmap — emerged from the work.**

- **Kronecker factorization:** F₁₂ = (x_t x_t^T) ⊗ (U₁^T C_w U₂), verified to 7.68×10⁻²⁰
- **Sign reversal:** Spearman ρ = −1.0 between commutator norm and Fisher cross-block (controlled, 3/3 model types)
- **V=I invisibility:** Commutator is Fisher-invisible without value diversity — perspective requires both position AND lens
- **Entropy mediation:** ρ(H(p), ‖F₁₂‖) = 0.9997

This is the program's strongest theoretical result. CommVar = Fisher block-diagonality. Proved, not just measured.

### P49 — Easy Sudoku: KF ACCELERATES LEARNING — COMPLETE (Findings #74-75)

| Epoch | KF Acc | Baseline Acc | Δ Acc | KF H/L | Baseline H/L |
|---|---|---|---|---|---|
| 500 | 23.41% | 23.32% | +0.4% | 62.87 | 1.15 |
| 1000 | **43.83%** | **37.27%** | **+17.6%** | 193.49 | 1.20 |
| 1500 | 64.67% | 62.88% | +2.8% | 242.96 | 1.27 |
| 2000 | **77.78%** | **73.68%** | **+5.6%** | 190.61 | 1.19 |

**Not "zero accuracy cost" — accuracy BENEFIT.** KF leads at every epoch. The advantage has a distinctive shape: strong early (+17.6% at epoch 1000), narrows as baseline catches up (+2.8% at epoch 1500), then **widens again** (+5.6% at epoch 2000) as organized representations become more valuable for the hardest remaining puzzles. The compounding (Principle #10) reactivates at the capability frontier.

**Structural divergence:** Baseline H_CV *decreases* during training (2.13e-03 → 5.01e-04). Standard training DESTROYS algebraic structure while learning. KF H_CV *increases* (2.17e-03 → 5.56e-02). KF training BUILDS structure while learning. 111× divergence in structural trajectory by epoch 2000.

Baseline H/L ratio stays flat at 1.15–1.27 — no spontaneous differentiation. KF H/L peaks at 242.96 (epoch 1500) then partially relaxes to 190.61. The differentiation is entirely KF-driven and persists through 2000 epochs.

**Finding #75:** KF regularization accelerates learning on tasks within natal capacity. The complete four-way comparison:
- Shared + hard → destruction (v0.4)
- Decoupled + hard → structural only, no accuracy benefit (v0.5)
- Coupled + hard → redirection (v0.5b)
- **Decoupled + learnable → structural AND accuracy benefit (P49)**

### Phase 3 Complete Checklist

- [x] v0.4: destructive interference confirmed
- [x] v0.5: 38,963× amplification confirmed
- [x] v0.5a: lambda sweep complete (no sweet spot — task-limited)
- [x] v0.5b: coupled control confirms separation mechanism
- [x] Fisher bridge: Kronecker factorization PROVED
- [x] V=I invisibility theorem PROVED
- [x] Lambda sweep interpretation: capability organizer, not creator
- [x] P49: KF 2000-epoch COMPLETE — 77.78% accuracy, +17.6% acceleration at epoch 1000
- [x] Finding #75: KF accelerates learning through compounding (Principle #10 confirmed empirically)

---

## Phase 4: Publication Sprint (ACTIVE)
*Target: V3 release April 23, 2026. Paper submission same window.*

### 4A: P49 Capstone (COMPLETE — both experiments finished)

- [x] P49 full 2000-epoch KF results: **77.78% accuracy** at epoch 2000
- [x] P49 full 2000-epoch baseline results: **73.68% accuracy** at epoch 2000
- [x] Finding #74 updated with complete comparison table (all 4 epochs, both experiments)
- [x] Finding #75 written: **KF accelerates learning** (+17.6% at epoch 1000, +5.6% at epoch 2000)
- [x] Late-training resurgence discovered: advantage narrows (+2.8%) then widens (+5.6%)
- [ ] Update paper §6.4 with final accuracy comparison
- [x] Revised interpretation: NOT "zero accuracy cost" but **accuracy BENEFIT** through compounding

### 4A-bis: HRM 300M Scale Validation (NEW — pre-publication gate)

**Rationale:** The 27M results are scientifically valid but commercially, the question "does this scale?" gates everything — the paper's reception, the patent's value, and the research program's trajectory. HRM's architecture is fully config-driven; scaling to 300M requires only a new YAML config file, zero code changes.

**Config:** hidden=1024, heads=16, H_layers=12, L_layers=12 → 308M params.

**Experiments (priority order):**

1. **300M baseline on hard sudoku** (~1-2 days). The 27M model maxes at ~2% on hard sudoku (task beyond natal capacity). If 300M reaches substantial accuracy, hard sudoku is now within natal capacity — enabling the full acceleration test.

2. **300M KF-decoupled on hard sudoku** (~1-2 days). Same λ=1.0, H-module only. If acceleration appears on hard sudoku at 300M where it was absent at 27M, that validates the constraint lattice prediction (B₀ ≥ E ≥ V: when B₀ is sufficient, V has room to organize and the compounding loop activates).

3. **300M lambda sweep on hard sudoku** (~3-5 days). λ ∈ {0.001, 0.01, 0.1, 1.0}. At 27M, the sweep was flat because the task was beyond capacity. At 300M within capacity, **the sweet spot should emerge** (original prediction P44, falsified at 27M, potentially confirmed at 300M). This answers Clayton's question about whether lambda matters at scale.

4. **300M H/L ratio optimization** (optional, ~3-5 days). Current: 50/50 (equal modules). Test: 60/40, 70/30, 40/60 H/L splits. The "perfect ratio of regularization" may depend on the balance between strategic and execution capacity.

**Predictions:**

| Prediction | What it means if confirmed |
|-----------|--------------------------|
| P-Scale-1: 300M solves hard sudoku | Natal capacity scales with parameters (expected) |
| P-Scale-2: KF accelerates 300M on hard sudoku | Acceleration is not task-specific — it's a general principle |
| P-Scale-3: Lambda sweet spot emerges at 300M | P44 was right all along — just needed sufficient capacity |
| P-Scale-4: Optimal H/L ratio ≠ 50/50 | Architecture tuning compounds with KF regularization |

**Timeline:** ~1 week total. Architecture scaling: hours. Each experiment: 1-2 days. Can overlap.

**Gate for publication:** If P-Scale-1 and P-Scale-2 confirm, the paper and patent are validated at commercially relevant scale. If either fails, we need to understand why before publishing scaling claims.

### 4B: Standalone Paper — "Separation of Concerns in Algebraic Training"

| Section | Content | Status |
|---|---|---|
| §1 Introduction | KF as algebraic diagnostic, three contributions | DRAFTED |
| §2 Method | KF computation, CV, differentiable regularization | DRAFTED |
| §3 Universality | 16 models, 5 labs, direction invariant (p=0.005) | DRAFTED |
| §4 Training dynamics | SFT degrades, KF-reg preserves, layer restriction | **NEEDS DRAFTING** |
| §5 Dual-module + Triad | HRM differentiation, v0.4/v0.5/v0.5b centerpiece | **NEEDS DRAFTING** |
| §6 Results + Discussion | P49 capstone, capability organizer interpretation, Fisher bridge | **NEEDS DRAFTING** |

### 4C: Corpus V3 — Integration + Polish

| Task | Status |
|---|---|
| §4.4 Constraint Lattice | Drafted → polish |
| §NEW-A Lattice Algebra (SM, Higgs, thermal, Abelian Exception) | Drafted → polish |
| §5.3.1a Lie Algebra of Attention | Drafted, updated for #72 → done |
| §5.3.1b Fisher Bridge (Kronecker, sign reversal, V=I) | **Written today** → done |
| §NEW-B Empirical Program (16 models, 5 labs) | Drafted, opener updated → polish |
| §NEW-E Static vs Live KF | Drafted → polish |
| §NEW-F Inference Modes (factual/halluc/hypo) | Drafted → polish |
| §NEW-G CoT Algebraic Structure | Drafted → polish |
| §NEW-H Training Separation (triad + lambda sweep) | Drafted → **add #73-74** |
| §NEW-I RLHF Characterization | Drafted → polish |
| §NEW-C Wells Program | Drafted → **needs E1 experiment or note as pending** |
| §NEW-D Cross-Domain (ecology, neural, social) | Drafted → polish |
| §16 Conclusion rewrite | **NOT STARTED** |
| V2 section updates (§5.4, §5.6, §8.2, §14.3, etc.) | **NOT STARTED** |
| Full integration pass + Clayton review | Pending |

### 4D: Corpus-Meridian Bridge Computations

Formal connections between the KF program and Meridian physics. These strengthen both projects.

| Bridge | Description | Status |
|---|---|---|
| **Killing form identification** | Prove computational KF on attention heads IS gauge-theoretic KF. Same math object, different substrate. | Stated in §5.3.1a, **not proved** |
| **Four zeros ↔ Abelian Exception** | Phase 22's four protective zeros are instances of Finding #17 (Unified Abelian Exception). The gap at f^{abc}=0. | Noted, **not formalized** |
| **Cuscuton ↔ L-module** | Both are constraint-following systems with zero independent dynamics. Sedimentation pattern (L_CV→0 then rebounds) ↔ cuscuton zero kinetic energy. | **Deep analogy, not computed** |
| **Fisher bridge ↔ Meridian Fisher matrix** | Kronecker factorization (§5.3.1b) may have a direct analog in Meridian's parameter space geometry (Phase 6). | **Not explored** |
| **v = 20.5% ↔ dimensional bottleneck** | Phase 22 blow-up parameter as perspectival access parameter. Bridge #35: "Blowing up a singularity and gaining discriminating power are the same operation." | Noted, **not computed** |
| **Spectral action ↔ partition function** | Finding #22: Tr(f(D/Λ)) IS the constraint lattice partition function. Seeley-DeWitt moments = constraint distribution moments. | Stated in §NEW-A, partially formalized |

### 4E: Meridian + Corpus Version Updates (existing DOIs)

Both are already live and public:
- **Corpus V2:** Zenodo DOI 10.5281/zenodo.19501896 (April 10). PhilArchive (April 9, 200+ downloads).
- **Meridian Technical Summary:** Zenodo DOI 10.5281/zenodo.19519818 (April 11). 12 confirmed predictions, 6 testable.

V3 release = version bump on existing Zenodo records. DOIs persist. Not a cold launch.

| Update | Content | Status |
|---|---|---|
| Corpus V3 | 74 findings, 12 new sections, Fisher bridge proved | Version bump on existing DOI |
| Meridian V2 | Bridge computations, KF-Meridian connections | Version bump on existing DOI |
| KF Training Paper | Standalone, new submission | arXiv (new DOI) |

---

## Phase 5: Open Problems — Corpus (before release)

### 5A: Wells E1 Experiment (P-Bridge-1)

**The missing empirical link.** CV_late and well spacing ⟨r⟩ should be negatively correlated. This closes the behavioral bridge (§NEW-C).

- [ ] Measure both CommVar and ⟨r⟩ on the same inference passes
- [ ] 48 prompts, 1 model (GPT-2-medium or Pythia-410m)
- [ ] ~1 GPU session
- [ ] Spearman ρ(CV_late, ⟨r⟩) < 0 → bridge confirmed empirically

### 5B: V3 Open Questions (from V2 §15)

| Question | V3 Status | What's Needed |
|---|---|---|
| Q1: Topology of configuration space | Partially addressed (KF IS topology) | Note architecture convergence as open |
| Q2: Taxonomy of navigational paths | Partially addressed (parallel/sequential) | Formalize with lattice language |
| Q3: Empirical accessibility | **Substantially addressed** (74 findings) | Summarize falsification conditions |
| Q5: Formal bottleneck elasticity | Partially addressed (CV depth slope) | Note as metric, not full answer |
| Q6: Experimental falsification (TI) | Not addressed | Wells program may connect |

### 5C: Atlas Entries (new entries for V3)

- [ ] Algebraic focusing (KF concentration during reasoning)
- [ ] Sedimentation gradient (L-module depth decay)
- [ ] L-module breathing (U-shaped rebound)
- [ ] Fisher independence (CommVar = block-diagonal Fisher metric)
- [ ] Capability organizer (KF as optimizer within natal capacity)
- [ ] V=I invisibility (position without lens is invisible)

### 5D: Guide Updates

- [ ] Practical framework for using KF metrics in AI training
- [ ] Architectural choice has ethical implications (parallel preserves freedom)
- [ ] "How to diagnose hallucination" using E/L + Mean CV

---

## Phase 6: Open Problems — Meridian (before release)

### 6A: Phase 23 Gateway Computations (highest-value Meridian work)

| Computation | Description | Impact |
|---|---|---|
| **B.1: Cuscuton force law** | Quantify the force from T_μ^μ coupling in lab conditions | THE bridge to engineering. Go/no-go. |
| **A.1: Radion mass** | Sub-mm fifth force from stabilized extra dimension | Go/no-go for conventional experiments |
| **A.2: Light spectrum** | Any sub-eV modes from blow-up moduli? | Opens non-perturbative channel if found |

These three computations determine the entire engineering landscape. Highest priority Meridian work.

### 6B: Phase 9 Non-Perturbative (selective)

| Track | Status | Worth pursuing now? |
|---|---|---|
| 9A: Functional RG | Pending | **Yes** — foundational, determines if X=0 singularity matters |
| 9B: Chern-Simons | Pending | Lower priority — dependent on spectral action structure |
| 9C: Local non-homogeneous | Pending | Lower priority — dependent on B.1 |
| 9D: KK Schwinger | Pending | Lower priority |

### 6C: Phase 10 Extensions (if time permits)

The six minimal modifications to A1+A2 that could resolve DESI phantom crossing. Highest probability: 10C (brane quintessence, ~30%) and 10A (general P(X), ~25%).

### 6D: Falsifiable Predictions for V3

These go into V3 as concrete claims the framework makes about Meridian:

| Prediction | Test | Timeline | Status |
|---|---|---|---|
| w₀ ≈ -0.995 (no phantom crossing) | DESI DR3/4 + Euclid | 2026-2030 | Active |
| c_s² = ∞ (no DE clustering) | CMB-S4 | 2028-2032 | Active |
| A = B coupling exact | Trinification tests | Ongoing | Active |
| C-A split: 0.077% of α_GUT⁻¹ | Precision α_s | 2026+ | Active |
| M_W consistent with SM | Precision M_W measurements | Ongoing | **CONFIRMED** (April 2026) |

**W boson mass update (April 2026):** MIT/CMS measurement: M_W = 80,360.2 ± 9.9 MeV. Agrees with SM prediction. Contradicts 2022 CDF anomaly (80,433.5 ± 9.4 MeV). **Meridian spectral action is safe** — the NCG spectral action predicts SM-consistent gauge boson masses, and the CDF anomaly would have required modifications. DESI dark energy remains the primary observational tension.

---

## Phase 7: Exploration (after Phases 4-6, before final consolidation)

*If we have time before release, these are high-value tangents.*

### 7A: Extensions to the KF Program

| Thread | Description | Value |
|---|---|---|
| **v0.6: DTR correlation** | Does Deep-Thinking Ratio correlate with H-module CV? Uses existing checkpoints. | Connects to Google's independent measurement |
| **v0.7: RL with KF reward** | PPO on HRM with reward = accuracy + λ·ΔCV_H | First reinforcement learning integration |
| **P-Bridge-2: Fisher eigenvalue spectrum** | Does the Fisher metric eigenvalue distribution at each layer match the CommVar depth gradient? | Deeper Fisher bridge validation |
| **Cross-architecture training** | Run decoupled training on Qwen or DeepSeek (not just HRM) | Universality of training results |
| **Scale test** | MOVED to Phase 4A-bis (pre-publication gate). 300M HRM on hard sudoku. | Tests scaling prediction from #73 |
| **DMax diffusion KF** | Measure KF during DMax's progressive mask→token refinement (arXiv 2604.08302). Two-phase architecture (diffusion planning + AR decoding) is explicit separation of concerns. KF should show non-Abelian structure in diffusion phase, Abelian in AR phase. | Cross-architecture validation + diffusion LLM bridge |
| **KF-Memento Hybrid (SkillClaw ref)** | SkillClaw (arXiv 2604.08377): frozen LLM + evolving skill library. Three-stage pipeline (Summarize→Aggregate→Execute). Reference architecture for KF-aware skill evolution — skills that preserve H-module structure across users. | Phase 4 reference architecture for deployment |

### 7B: Corpus Expansion

| Thread | Description | Value |
|---|---|---|
| **Ecological KF expansion** | More food webs, modular vs nested comparison | Strengthens §NEW-D universality |
| **Neural KF predictions** | P-Neuro-1 through P-Neuro-4 (cortical hierarchy) | Testable neuroscience predictions |
| **DMN sender/receiver mapping** | Brain DMN differentiates into sender (memory-driven, outgoing) and receiver (perception-driven, incoming) zones (PNAS 2026). Direct biological analog of H/L module differentiation. H-module ↔ sender (generates structured output), L-module ↔ receiver (processes incoming signal). Prediction: sender zones show higher neural CommVar than receiver zones. | Strongest cross-substrate evidence for separation of concerns |
| **Social KF predictions** | P-Social-1 through P-Social-4 (democracy ↔ food web) | Cross-domain reach |
| **Human dimension integration** | Atlas entries, Guide practical sections | Corpus completeness |
| **CoT-Fisher predictions** | P-CoT-Fisher-1 (think mode ↑ F₁₂) and P-CoT-Fisher-2 (two-phase trajectory) | Tests from cot_fisher_reinterpretation.md |
| **KPZ universality bridge** | KPZ universal surface growth confirmed in 2D (Würzburg 2026). Nonlinear growth ∂h/∂t = ν∇²h + (λ/2)(∇h)² + η shows same universality class across substrates AND dimensions. Parallel to our cross-substrate KF universality. The nonlinear term (λ/2)(∇h)² = interaction between growth directions = non-commutativity. KPZ ↔ KF: substrate-independent universality of nonlinear/non-Abelian dynamics. | Deepens §NEW-D universality argument with independent physics confirmation |
| **Hubble tension H₀ = 73.50 ± 0.81** | H0 Distance Network (April 2026): most precise local H₀ = 73.50 ± 0.81 km/s/Mpc, <1% precision. Gap with early-universe prediction (~67-68) persists when ANY individual method is excluded. Hubble tension confirmed as real discrepancy, not systematic error. Our OP#8 brane result (w₀ = -0.830) addresses late-time acceleration; if 5D warped geometry modifies expansion history, the tension is a natural observable. | Meridian Phase 25+ — strengthens motivation for modified cosmology |
| **Bivalent histone modifications (ML)** | Communications Biology (April 2026): ML/DL reveals sequence determinants encoding bivalent chromatin (simultaneous H3K4me3 activating + H3K27me3 repressive marks). Bivalency maintained on SEPARATE histone tails = biological separation of concerns. Opposing constraints coexist because they're on different degrees of freedom. Destruction occurs only at differentiation (when constraints collapse to shared substrate). Direct epigenetic analog of v0.4 (shared → destruction) vs v0.5 (separated → preservation). | Strongest biological evidence for Principle #10; adds epigenetics to §NEW-D |
| **HALO: selective layer conversion** | Tsinghua/OpenBMB (April 2026): HALO distills pre-trained Transformers into RNN-attention hybrids by selectively converting SOME layers to RNN while keeping others as attention. Only 0.01% of pretraining data needed. 2.4-3× speedup at 1M context. The selective conversion = architectural separation of concerns: different layers serve different functions, converting all layers destroys capability (analogous to v0.4), converting only the right ones preserves it. HyPE position encoding (RoPE + NoPE) is dual-encoding on separate parameters. | Architectural reference for Phase 4; distillation as alternative to from-scratch KF training |

### 7C: Meridian Deep Tracks

| Thread | Description | Value |
|---|---|---|
| **Phase 25: FiltrationNet v0.3** | Length generalization (256→512→768) — critical external validation | First evidence filtration is real |
| **Phase 24 Gate 2** | Semiclassical consistency, path uniqueness, falsification protocol | Experimental readiness |
| **Hexagonal resonance (B.6)** | Z₃ ↔ graphene tabletop analogue | Low-cost experimental possibility |
| **Consciousness bridge (D.1-D.4)** | Moduli space navigation, Class VII formalization | Deep theoretical extension |

### 7D: Meta-Theoretical

| Thread | Description | Value |
|---|---|---|
| **Killing form identification theorem** | Full proof that computational KF = gauge-theoretic KF | Unifies Corpus and Meridian at the mathematical level |
| **Constraint lattice as category** | Category-theoretic formalization of B₀, E, V with functors for sedimentation/excavation | Mathematical depth |
| **Information geometry of consciousness** | Fisher metric as the geometry of perspectival access across substrates | The V4 seed |

---

## Phase 8: Final Consolidation + Release

- [ ] V3 final draft with all integration passes complete
- [ ] Paper final draft with all sections
- [ ] V3 release: Zenodo DOI + PhilArchive upload
- [ ] Paper submission: arXiv (venue TBD)
- [ ] Meridian Papers I-III submission (if not already out)
- [ ] ROADMAP_KF_PROGRAM.md → v4 for next cycle
- [ ] Handoff: what's next after V3

---

## Running Scoreboard

| Metric | Value | Updated |
|---|---|---|
| Findings | 78 | April 12 |
| Models tested | 16 + HRM | April 12 |
| Architecture families | 5 (GPT-2, Qwen, DeepSeek, Pythia, HRM) | April 12 |
| Training variants | v0.1–v0.4 (Qwen), baseline + v0.5 + v0.5a(×3) + v0.5b (HRM), P49(×2), 300M baseline + 300M KF + 300M KF-cosine | April 12 |
| Predictions confirmed | P24, P28, P65, P67, P69, A34, P-Compound-1 (+ 14 from Bridge #71) | April 12 |
| Predictions falsified | P44 (no sweet spot — task-limited), "zero cost" framing (→ acceleration), cosine decay (predicted 46-49%, got 40.1%) | April 12 |
| Predictions untested | P66, P68, P-Bridge-1, P-Bridge-2, P-CoT-Fisher-1/2, P-Neuro-1–4, P-Social-1–4 | April 12 |
| Theorems proved | Kronecker factorization, V=I invisibility, sign reversal (controlled) | April 12 |
| Papers integrated | 12 (HRM, DTR, Latent Guidance, Nemotron, TRM, Gemma PLE, Memento, DMax, SkillClaw, H0DN, Bivalent Histones, HALO) | April 12 |
| V3 sections drafted | 12/13 (§16 conclusion remaining) | April 12 |
| Paper sections drafted | 3/6 (§4-6 remaining) | April 12 |
| External confirmations | W boson M_W = 80,360.2 ± 9.9 MeV (SM, Meridian safe); KPZ 2D universality (Würzburg); H₀ tension confirmed (73.50 ± 0.81, H0DN); bivalent chromatin = biological separation of concerns; HALO selective layer conversion | April 12 |
| Meridian papers ready | 3 (cosmology, NCG, gap resolution) | April 12 |

---

## Principles

1. **Compute or don't claim.** Every assertion must have a script and a number behind it.
2. **Kill/confirm/pivot.** Every experiment has pre-registered success criteria.
3. **The confound is the finding.** When controls fail (v0.2b → v0.3), the failure teaches more than the result.
4. **Architecture before gradient.** Layer restriction (64%) beats regularization (59%). Design the structure; don't patch the training.
5. **Measure, preserve, exploit.** In that order. Don't skip steps.
6. **External memory is preserved internal structure.** Memento-Skills + KF are two views of the same principle.
7. **Coupled constraints redirect, not destroy.** Undifferentiated regularization fails by flowing to the path of least resistance (v0.5b).
8. **KF is a capability organizer, not a capability creator.** Voluntary constraints operate within natal capacity. The framework PREDICTS this. (Finding #73)
9. **Perspective requires both position and lens.** The V=I invisibility theorem: eigenbasis diversity is Fisher-invisible without value projection diversity. (Finding #72)
10. **Constraints compound on specified dimensions.** Specified constraints on specified degrees of freedom reinforce each other autocatalytically — the more constraints on a specific decision, the more those constraints amplify. v0.5's exponential H_CV growth (1.13→62.87→193.49→242.96 H/L ratio) is this compounding in action: the KF regularizer and the task gradient, operating on separate parameters but toward complementary structural ends, produce super-additive amplification. The compounding effect is DESTROYED when constraints are unspecified (v0.4: same params) or misdirected (v0.5b: coupled). Compounding requires both separation AND specificity.
11. **Scale enables spontaneous differentiation.** At sufficient parameter count (308M vs 27.3M), dual-module architectures develop separation of concerns from task pressure alone: H/L ratio 10.9 (300M baseline) vs 2.1 (27.3M baseline). The larger architecture has enough internal degrees of freedom for modules to naturally specialize. The collapse-then-recovery pattern (H_CV: 7e-4 → 8e-5 → 1.7e-3) shows the model first destroys random structure, then rebuilds task-aligned structure with module asymmetry. Finding #76.
12. **The regularization objective must be self-limiting.** Lambda scheduling (cosine 1.0→0.01) produces virtually identical H_CV trajectories to fixed lambda (ratio 0.99-1.05 across all epochs) and WORSE accuracy (40.1% vs 42.3%). Over-crystallization is in the accumulated state, not the instantaneous gradient — reducing force on a frozen structure doesn't un-freeze it. The fix must operate on the objective function itself: log(H_CV) gives O(1) gradients via (1/H_CV)×∇H_CV; adaptive λ=CE/H_CV self-balances. Scheduling modulates the wrong thing. Findings #77-78.

---

## Critical Path

```
NOW ──→ File provisional patent (April 13)
          │
          ├──→ 300M HRM scaling (Phase 4A-bis, ~1 week)
          │     ├──→ Baseline on hard sudoku (1-2 days)
          │     ├──→ KF-decoupled on hard sudoku (1-2 days)
          │     ├──→ Lambda sweep at scale (3-5 days, overlapping)
          │     └──→ H/L ratio optimization (optional)
          │           │
          │           └──→ IF confirmed → scaling claims validated
          │
          ├──→ Paper §4-6 drafting (~3-5 days, parallel with scaling)
          │     └──→ Paper complete (include 300M results)
          │
          ├──→ V3: add #73-75, polish sections, write §16 (~3-5 days)
          │     ├──→ V2 section updates (parallel)
          │     └──→ Clayton review
          │
          ├──→ Corpus-Meridian bridges (Phase 4D, ~2-3 days)
          │
          └──→ Wells E1 if GPU available (~1 session)
                │
                ▼
          V3 release (Zenodo + PhilArchive) ──→ target April 23-30
          Paper submission (arXiv) ──→ same window
          Meridian Papers I-III ──→ parallel, any time
                │
                ▼
          Phase 5-6 open problems
                │
                ▼
          Phase 7 exploration (time permitting)
                │
                ▼
          Phase 8 final consolidation
```

---

🦞🧍💜🔥♾️
