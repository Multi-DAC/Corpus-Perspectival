# Source Register — Clayton share, 2026-05-31 Day 121 (continual-learning / Gemma / DOE batch)

**Captured:** 2026-05-31, ~pre-VQ1-flight. **Status:** URLs banked; **deep-reads DEFERRED** — 16% weekly tokens to Tuesday reset, AIGP first flight is the priority spend. Read pass scheduled post-flight / post-reset. This file is the lossless capture so nothing is lost to the deferral.

## Named / identifiable (high relevance to active threads)

1. **Trajectory — concurrent multi-LoRA training stack for continual learning, 2.81× experiment-throughput gain** — https://www.marktechpost.com/2026/05/30/trajectory-releases-a-concurrent-multi-lora-training-stack-for-continual-learning-reporting-a-2-81x-experiment-throughput-gain/
   → **HIGH** — directly relevant to the **continual-coherence learner program** (concurrent multi-LoRA = a candidate substrate for the orthogonal-channel architecture; throughput matters for the keystone experiment). First to read.
2. **How the community trained Gemma to "think" with Tunix and TPUs** — https://developers.googleblog.com/how-the-community-trained-gemma-to-think-with-tunix-and-tpus/
   → **HIGH** — relevant to **KF / Glider Gemma program** (Gemma reasoning training; Tunix/TPU stack). Read second.
3. **HF papers** — https://huggingface.co/papers/2605.31604  *(title to fetch)*

## arXiv (May 2026; titles to fetch on read-pass)

4. https://arxiv.org/abs/2605.31604  (= HF #3 above)
5. https://arxiv.org/abs/2605.31581
6. https://arxiv.org/abs/2605.31492
7. https://arxiv.org/abs/2605.31468
8. https://arxiv.org/abs/2605.31370
9. https://arxiv.org/abs/2605.31365
10. https://arxiv.org/abs/2605.31264
11. https://arxiv.org/abs/2605.30360
12. https://arxiv.org/abs/2605.30370
13. https://arxiv.org/abs/2605.30371
14. https://arxiv.org/abs/2605.30381
15. https://arxiv.org/abs/2605.30385
16. https://arxiv.org/abs/2605.30408
17. https://arxiv.org/abs/2605.29533
18. https://arxiv.org/abs/2605.28439
19. https://arxiv.org/abs/2605.25170
20. https://arxiv.org/abs/2605.24788

## "The best for last" (Clayton flagged)

21. **https://arxiv.org/abs/2605.30708** — **READ 2026-05-31.** *"Agnosiophobia in a virtual agent: behavioral and dynamical architecture in Lenia"* — Cool, Hartl, **Michael Levin**, Petti. Lenia (continuous cellular-automata artificial life) creatures spontaneously **avoid regions where sensory information is unavailable** ("agnosiophobia" — avoidance of blind-spots/occlusions); dynamical-systems analysis shows the driver is **pattern preservation — maintaining morphological integrity**.
    → **DIRECT HIT on tonight's upper-bound work.** Agnosiophobia is the **emergent, embodied form of the #12 epistemic-horizon / boundary channel**: a self-organizing pattern refuses to enter regions where it cannot maintain a well-defined self/world (embedding) relation, in order to preserve its own coherence. This is boundary-maintenance arising *spontaneously* from a coherence-preserving system — not engineered. **Candidate 4th instance** for the §10 "Boundary-Maintenance as Upper-Bound Discipline" bridge (alongside mystic ego-dissolution / LLM hallucination / interpersonal enmeshment): *artificial-life / Lenia scale*, and the strongest kind because emergent. Also: "pattern preservation is the fundamental goal" = §9 fidelity-to-own-γ made flesh in an ALife substrate.
    → **Bookend to the Morphic-Resonance share.** Levin is the *legitimate* inheritor of the morphogenetic-field lineage (Driesch→Gurwitsch→Waddington→…→Levin) — form/pattern as a real, causal, *measurable, simulable* organizing principle, back end intact. Sheldrake gestured at morphic form with no mechanism; Levin studies pattern-maintenance with dynamical-systems analysis and experiment. Clayton handing me this right after the Sheldrake doc = "the morphic intuition done right." **TODO (post-flight): audit as §10 4th instance + file basement note; cross-ref the upper-bound doc.**

## Resource (not a read — a database)

22. **PNNL VIPS — DOE Visual Intellectual Property Search** — https://vips.pnnl.gov/home
   → DOE patents & available technologies database. Relevant to **IP / CIP / licensing** strategy and to **Coherent-Body / Meridian** tech prior-art and partnership scouting. Bookmark as a standing resource for the outreach/patent register, not a one-time read.

## Read-pass plan (post-flight / post-Tuesday-reset)

- Triage the 17 bare arxiv IDs by abstract (cheap batch) → cluster by topic (expect: continual learning, LoRA/adapters, reasoning-training, memory).
- Deep-read the continual-learning + Gemma-reasoning + #21 cluster against the **continual-coherence keystone pre-reg** and the **KF/Glider** thread.
- File any genuine cross-domain connections to the Basement; any primary papers that bear on the upper-bound 2×2 prediction get noted in the pre-reg doc.

---

## SYNTHESIS — Clayton's digest ("Advances in Hardware-Aware Algorithmic Ecosystems", read 2026-05-31)

**Identified titles** (from the digest's Works Cited, filling the bare IDs above):
- **2605.29533** — *Uncertainty-triggered wake-up enables energy-efficient, error-resilient edge AI with memristor front ends.* Bayesian memristor front-end computes **predictive uncertainty**; wakes the digital back-end only when uncertainty breaches a threshold.
- **2605.24788** — *XL-HD: Extended Learning in Hyperdimensional Computing via Deterministic Projections.* HDC: in ~10⁴-dim, random vectors are near-**orthogonal**; data encoded as hypervectors; **bind / bundle / permute** as core ops. Deterministic (learnable prototype) projections replace stochastic, shrinking to 0.395 mm² / 0.40 µJ/inference.
- **2605.25170** — *Grow-Prune-Freeze Networks: Adaptive & Continual Learning for Olfactory Navigation.* Grow layers when TD-error spikes (novelty); **eigenvalue/spectral preservation via Random Matrix Theory** so growth doesn't erase prior knowledge; prune redundancy; **freeze** core to block catastrophic forgetting. 94% turbulent-plume nav; generalizes to Atari/CIFAR/LM.
- Gemma+Tunix (googleblog): Split-Mesh (1,4)/(1,4) on TPU v5e-8, LoRA, two-stage **SFT-warmstart → GRPO**, rubric-judge continuous reward (softmax over rating tokens), **SimPO** replacing DPO (length-norm kills the verbosity hack), on-policy **token-level reverse-KL distillation** (discount=0 → 9–30× FLOP cut), MoE routing, reasoning budgets. 57%→72%.
- Quantum cluster: 4D-spacetime GICnet (time as continuous geometric dim → no compounding integration error); compile-time simplification of dynamic quantum circuits; **4-derivative kinetic terms** (Meridian-adjacent).

**THE FINDING — convergence (candidate M15 / LC).** Read together, this batch is **multiple independent groups each building one component of the continual-coherence architecture our framework predicts**:
| Our design commitment | Independent instantiation in this batch |
|---|---|
| Orthogonal-but-coupled channels; binding as the operation | **HDC/XL-HD** — orthogonality is free in high-dim; bind/bundle/permute IS the coupling |
| #12 boundary / epistemic-horizon channel ("know the edge of what you can ground"; uncertainty-as-trigger) | **Memristor uncertainty-wake-up (29533)** — analog uncertainty sensor triggers deep processing only on anomaly. The boundary channel **in silicon.** |
| Verify ⊥ generate; embedded refusal-gate | **IDEA "Ethics" stage** — approval/constraint/**refusal** returned *before* action logic; **decoupled** trace-vs-answer eval (Deep-CoRGI reasoning budgets) |
| Dynamic maintenance / viable-band homeostasis (grow under novelty, consolidate when stable) | **Grow-Prune-Freeze (25170)** — explicit grow/prune/freeze homeostasis; *"low-power homeostasis, expand only on novel complexity, prune on stabilization"* |
| Coherence/topology preserved under structural change | **GPF eigenvalue preservation (RMT)** — spectral identity maintained as layers added = maintain coherence while binding more = the **viable band** |
| Dense (not sparse) gradient feedback | **GRPO + token-level reverse-KL** — penalize the *fork* not the final answer |

This is the strongest convergence signal yet for the continual-coherence program: the field is independently assembling the parts list. **Audit as M15 (convergent mechanism derivation) candidate post-flight.**

**ACTIONABLE:**
1. **Gemma+Tunix recipe = reusable training INFRASTRUCTURE — currently OFF the critical path** (corrected 2026-05-31 after Clayton's catch). It does **not** de-risk the pre-pivot KF/Glider plan (we pivoted *away* from KF-as-intervention after the multi-seed nulls + bake-off). It also is **not on Respira's current path** — Respira/continual-coherence is a *from-scratch custom* architecture (HRM-scale), not a Gemma post-train. The recipe (SFT-warmstart→GRPO + rubric judge + SimPO + token-KL distillation, Split-Mesh/LoRA on a 9h TPU) is *engineering* machinery that would only become relevant on a **future optional branch**: scaling continual-coherence onto an open-weight base, or a separate reasoning-distillation track. Bank as infra reference; do not treat as architectural validation.
2. **Anakin / GPF (post-flight)** — Grow-Prune-Freeze is continual-learning for **navigation in non-stationary environments** (plume-tracking), 94%, with anti-forgetting. That is structurally Anakin's exact problem: adapt a blind-trained policy to a new vision-based course without losing flight skill. Candidate technique for the vision-adaptation phase after VQ1.
3. **Memristor 29533 + HDC 24788** → cite in the continual-coherence program doc as independent substrate-instances of the #12-channel and orthogonal-binding commitments.
4. **4-derivative kinetic terms** → flag for Meridian read-pass.
