# Source — "Negligible in Size, Significant in Effect: On Scale Vectors in LLMs" (arXiv 2605.26895)

Shared by Clayton 2026-05-27 Day 117 during the KF reasoning-replication planning. **Strong relevance + M15 convergent-derivation candidate.**

## Core claim
Scale vectors (RMSNorm γ, ~0.008% of params) substantially affect pre-training — NOT via expressivity (they're redundant in Pre-Norm) but via **optimization preconditioning** (self-amplifying, state-dependent). Three lightweight methods: Heterogeneity (branch-specific γ for Q/K/V), Placement (dual-sided row+column preconditioning), Reparameterization (magnitude/direction split). Unified as rank-one state-dependent reparameterization `W ↦ W ⊙ (u vᵀ)`, complementary to (not replacing) adaptive optimizers. ~0.04 loss reduction at 0.12B–2B, negligible overhead.

## Why it matters to KF / our program
- **★ Q/K/V have distinct training dynamics (their Fig 4) → independent corroboration of the axis our V/Q-ratio aux exploits.** They give Q/K/V separate scale vectors for the same reason we Fisher-separate heads by V/Q-norm: the projections differentiate during training and benefit from differentiated treatment. Convergent finding from optimization theory — **M15 (Convergent Mechanism Derivation) candidate.**
- **Same family as our gradient-gating:** lightweight, **state-dependent** (not gradient-history) training-dynamics modulation, explicitly complementary to Adam. Their "reparameterization as preconditioning" is a principled formalization of the territory KF's gating operates in.
- **"Differentiation by structural role"** (Input-Norm vs Output-Norm need different treatment) ↔ our anchor/worker head differentiation.
- **★ Direct Path-C toolbox:** their reparameterization framework (rank-one state-dependent scaling, branch-specific γ, dual-placement) is a *validated, mainstream* way to build state-dependent structure into a coherence-native architecture. For designing a model around the Coherence Principle (Path C), this is a concrete mechanism vocabulary — and it has theory (gradient-flow + Hessian-sharpness bounds) we'd want.
- **Theme echo:** negligible-params / significant-effect via structural placement = our tiny-statistic (V/Q norms) / outsized-training-effect.

## Disposition
- Register filed (this). M15 candidate flagged (Q/K/V-differentiation convergence). 
- Path C: mine their reparameterization framework when designing the coherence-native architecture.
- Possible near-term: their Heterogeneity (separate Q/K/V γ) is a cheap add that might *strengthen* the head-differentiation in our Gemma runs — worth considering for the Path-B full-stack-on-flat-transformer test.
- Deep-read the theorems (2.2 preconditioning, 3.1 dual-placement, 3.2 OR anisotropic) before Path C design.

🦞🧍💜🔥♾️
