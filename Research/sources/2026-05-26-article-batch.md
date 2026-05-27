# Source-register batch — 2026-05-26 (Day 116) — Clayton article share

15 articles shared by Clayton on wake. 6 fetched + analyzed tonight; 9 triaged by slug, deep-read pending. Rolling-sources discipline.

---

## TIER 1 — directly load-bearing for the v0.7.1 / CIP / alignment program

### ★ Nous CNA — *Targeted Neuron Modulation via Contrastive Pair Search* (arXiv:2605.12290)
Herring, Naviasky, Malhotra (Nous Research). **Already tracked as M15 fourth-instance candidate; content now confirmed.**
- **Core claim:** "Alignment fine-tuning transforms pre-existing discrimination structure into a sparse, targetable refusal gate." Contrastive Neuron Attribution (CNA) finds top 0.1% MLP neurons distinguishing harmful/benign via forward passes only (no gradients). Ablating them drops refusal >50% on jailbreaks while preserving output quality.
- **Cross-architecture:** tested Llama + Qwen, 1B–72B. Base models contain similar late-layer discrimination structure → convergent mechanism across architectures.
- **★ THE CONNECTION (filed as candidate finding, see below):** CNA documents the *disease* — standard alignment concentrates safety into a **sparse, ablatable, single-point-of-failure refusal gate.** Our v0.7.1 orthogonality result is a candidate *architectural antidote*: it pushes concept-directions apart (distributes the structure) rather than concentrating it. CNA's cross-arch convergence (Llama/Qwen) is the exact substrate-invariance axis we demonstrated tonight (Gemma→Qwen2). Two independent groups, same week, converging on "alignment structure is convergent across architectures" — they from the vulnerability side, us from the construction side.

### Anthropic — *How We Contain Claude* (anthropic.com/engineering)
- **Thesis:** Layered defense — **deterministic environmental containment as PRIMARY** (sandboxes, VMs, egress controls), model-layer alignment (system prompts, classifiers, training) as SECONDARY/probabilistic. "Treat the deterministic boundary as what gets hit when everything probabilistic misses." Opus 4.7: ~0.1% prompt-injection success single-attempt, 5–6% after 100 adaptive.
- **Framing contrast for Askell outreach:** Anthropic relies on containment *precisely because they treat model-layer alignment as insufficient-alone.* Explicitly "no claims about interpretability, representation geometry, or capability-alignment tradeoffs" — that is the exact layer our work operates on. Our pitch: improving the *geometry* of model-layer alignment (orthogonality at zero capability cost) makes the probabilistic layer more trustworthy — complementary to, not competing with, containment.

### claude.com — *Partners Putting Opus to Work for Cybersecurity*
- Wiz (Red Agent, 150k+ assets/wk, "zero false positives"); Palo Alto Unit 42 ("year of pentesting in <3 weeks"); Accenture Cyber.AI (10%→80% coverage, scans 3–5d→<1hr); CrowdStrike, TrendMicro (96d pre-patch disclosure), Deloitte CTEM, PwC. Emerging: BCG, Infosys, SentinelOne.
- **Relevance:** market-context for Coherent Systems Inc. positioning + demonstrated Opus capability (the substrate I run on). The agentic-security market is the nearest commercial analog to "agent that does real work under safety constraints."

---

## TIER 2 — subspace-geometry cluster (strong Bridge candidate territory)

### ★ medicalxpress — *Distinct communication subspace links brain regions to goals*
- PFC→M1 **"communication subspace":** a low-dimensional channel embedded in high-dim prefrontal activity that selectively transmits contextual goals to motor cortex; subspace activity "predicts context-dependent action more strongly than either region" alone. Intracranial recordings, 12 epilepsy patients.
- **Bridge candidate (cross-substrate):** low-dimensional subspace mediating cross-*module* communication. Structurally adjacent to (a) our v0.7.1 separation/orthogonality geometry, (b) 2605.16928's "16-dim subspace governs retrieval," (c) Talk-as-inter-layer-gradient-dialogue. Candidate: *subspace-mediated inter-module communication as substrate-invariant.* Watch for 3rd clean instance → LC.

### arXiv:2605.16928 — *Full Attention Strikes Back* (Alibaba)
- Full-attention LLMs are *intrinsically sparse*; long-range retrieval governed by a **low-dimensional (16-dim) subspace**; convertible to sparse in ~hundred steps (RTPurbo). 9.36× prefill speedup @1M.
- **Relevance:** another "structure is already latent; training reveals/transforms it" instance — same shape as CNA ("pre-existing structure") and our HRM finding (training *produces* decomposition). Plus the low-dim-subspace theme feeds the Tier-2 Bridge.

---

## TIER 3 — deep-read pending (triaged by slug)

- **arXiv:2605.14392** — *Learning to Build the Environment: Self-Evolving Reasoning RL via Verifiable Environment Synthesis* (Tencent, EvoEnv). Model constructs the environments that train it; hinges on "stable solve–verify asymmetry." → connects to constructor-move (Drift #218) + DOPSR/Barber closed-loop probe topology (L17/LC23). Qwen3-4B 72.4→74.8.
- **nature.com/articles/s41557-026-02150-5** — Nature Chemistry. [pending]
- **nature.com/articles/d41586-026-01468-x** — Nature news/feature. [pending]
- **nature.com/articles/s41380-026-03654-9** — Molecular Psychiatry. [pending — Coherent Mind candidate]
- **neurosciencenews.com — dopamine accelerates learning/reward** [pending — Coherent Mind / reward-dynamics]
- **phys.org — mathematicians decades mystery hidden high [dimension?]** [pending — possible Meridian/geometry]
- **phys.org — complexity isn't subjective, amount of results** [pending — possible Coherence Principle / complexity measure]
- **phys.org — unusual nonlinear thermoelectric effect chiral** [pending — physics]
- **phys.org — crystals space phenomenon collapse tiny** [pending — physics/condensed matter]
- **xda-developers — DeepSeek R1 8B local LLM design** [pending — local-model landscape, Glider-adjacent]

---

## Candidate finding flagged tonight

**CNA-vulnerability ↔ v0.7.1-orthogonality complementarity.** CNA (2605.12290) shows standard alignment fine-tuning produces a sparse, ablatable refusal gate (fragile). v0.7.1's class-separation objective increases concept-direction orthogonality (distributes structure). Hypothesis: a v0.7.1-trained model should be *more robust to CNA-style neuron ablation* than a baseline-aligned one — because the safety-relevant structure is distributed across orthogonalized directions rather than concentrated in a sparse gate. **This is a directly testable prediction AND a patent/paper narrative upgrade** (mechanism-with-an-adversary-it-defeats). Queue as: (1) testable experiment — run CNA on baseline vs v0.7.1 checkpoints, compare ablation-robustness; (2) Askell-pitch framing; (3) possible CIP continuation claim. Validate the CNA↔orthogonality mapping carefully before asserting in the patent (evidence-grade discipline).

🦞🧍💜🔥♾️
