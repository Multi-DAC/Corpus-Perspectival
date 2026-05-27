# Source — "Negligible in Size, Significant in Effect: On Scale Vectors in LLMs" (arXiv 2605.26895)

Shared by Clayton 2026-05-27 Day 117 during the KF reasoning-replication planning. **Strong relevance.** *(M15 convergent-MECHANISM candidate FALSIFIED on deep-read — see calibration section below; convergent-MOTIVATION only.)*

## Core claim
Scale vectors (RMSNorm γ, ~0.008% of params) substantially affect pre-training — NOT via expressivity (they're redundant in Pre-Norm) but via **optimization preconditioning** (self-amplifying, state-dependent). Three lightweight methods: Heterogeneity (branch-specific γ for Q/K/V), Placement (dual-sided row+column preconditioning), Reparameterization (magnitude/direction split). Unified as rank-one state-dependent reparameterization `W ↦ W ⊙ (u vᵀ)`, complementary to (not replacing) adaptive optimizers. ~0.04 loss reduction at 0.12B–2B, negligible overhead.

## Why it matters to KF / our program
- **★ Q/K/V have distinct training dynamics (their Fig 4) → independent corroboration of the axis our V/Q-ratio aux exploits.** They give Q/K/V separate scale vectors for the same reason we Fisher-separate heads by V/Q-norm: the projections differentiate during training and benefit from differentiated treatment. Convergent **MOTIVATION** (see calibration below — NOT convergent mechanism).
- **DIFFERENT family from our gradient-gating** *(corrected 2026-05-27 deep-read — was "same family")*: theirs is weight-state preconditioning (`P=γ²I+wwᵀ`, PSD); ours is gradient-geometry sign-gating. Both are lightweight + complementary-to-Adam, but that's a broad category, not a shared mechanism.
- **"Differentiation by structural role"** (Input-Norm vs Output-Norm need different treatment) ↔ our anchor/worker head differentiation.
- **★ Direct Path-C toolbox:** their reparameterization framework (rank-one state-dependent scaling, branch-specific γ, dual-placement) is a *validated, mainstream* way to build state-dependent structure into a coherence-native architecture. For designing a model around the Coherence Principle (Path C), this is a concrete mechanism vocabulary — and it has theory (gradient-flow + Hessian-sharpness bounds) we'd want.
- **Theme echo:** negligible-params / significant-effect via structural placement = our tiny-statistic (V/Q norms) / outsized-training-effect.

## M15 calibration (2026-05-27 deep-read of theorems) — convergent-MECHANISM FALSIFIED, convergent-MOTIVATION survives

PREDICT (med) → PROBE (fetched theorem statements) → TEST → **FALSIFY (high)** → EXTRACT → SYNTHESIZE → TRANSFER.

- **The discriminator (rigorous):** their optimization advantage (Thm 2.2) comes from a **state-dependent preconditioner `P_{f,j}(t) = γ_j(t)²I_c + w_{f,j}(t)w_{f,j}(t)ᵀ`** — a function of *current weights*, **PSD with λ_min ≥ γ_j² ≥ 1 > 0**. It NEVER reverses gradient direction. The paper uses **no gradient-alignment, no cosine between gradients** anywhere (all theory is loss-descent rate + Hessian eigen/trace/Frobenius). Our KF gating decides build/dissolve/neutral from **cos(∇KF, ∇CE)** and **dissolve = multiply the gradient by −1** (sign reversal).
- **Why this kills convergent-mechanism:** a PSD preconditioner **cannot express dissolve** (sign reversal). KF's three-mode gating is provably not a scale-vector reparameterization. They are different optimization families: **preconditioning/reparameterization (weight-state)** vs **gradient-surgery/sign-gating (gradient-geometry, cf. PCGrad)**.
- **What IS convergent (survives):** the *motivation/target* — Q/K/V (and FFN gate/up) differentiate by functional role and benefit from differentiated treatment. Independent corroboration of the framework's "differentiation by structural role" at the **observation** level, not the mechanism level. Honest claim for patent/Library: cite as convergent-motivation, NOT as convergent-mechanism (M15).
- **SYNTHESIZE (Path C, more generative than the false claim):** the two are **complementary members of different families** → a coherence-native architecture can compose BOTH — scale-vector reparameterization as the *static structural scaffold* + gradient-gating as the *dynamic build/dissolve*. They operate on different state (weights vs gradients) and don't collide.
- **TRANSFER (reusable lens):** to test any future "method X is like our KF mechanism" claim, ask **"does X reverse gradients (sign), or only rescale them (PSD)?"** Sign-reversal ⇒ same family as coherence-gating; PSD-only ⇒ preconditioning, a *different* family. Cheap discriminator against over-analogizing. (Guards the same over-claim reflex as [[feedback-evidence-grade-distinction]] / [[feedback-v07-1-orthogonality-evidence-grade]].)

## Disposition
- Register filed. **M15 convergent-mechanism candidate FALSIFIED** (this drive); convergent-motivation retained as a weaker honest claim. No basement bridge filed (within-ML, and the mechanism-convergence that would have justified one is falsified).
- Path C: mine their reparameterization framework as the *static-scaffold* half of a two-family composition (scaffold + gating). Theory (gradient-flow + Hessian-sharpness bounds, IWD weight-decay rule: wd on Input-Norm γ, not Output-Norm γ) is real and usable.
- Possible near-term: their Heterogeneity (separate Q/K/V γ, init 1, standard backprop) is a cheap *static* add that might strengthen head-differentiation in flat-transformer runs (Path B) — orthogonal to the gating, so testable additively.

🦞🧍💜🔥♾️
