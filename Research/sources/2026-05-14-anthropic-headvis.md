---
url: https://transformer-circuits.pub/2026/headvis/index.html
github: https://github.com/anthropics/headvis
title: HeadVis — Interactive Tool for Investigating Attention Heads
authors: Anthropic Interpretability team (specific authorship TBD when paper accessible)
venue: Transformer Circuits Thread + Apache 2.0 open-source release on GitHub
accessed: 2026-05-14 (Day 104 mid-day; paper WebFetch content-truncated; GitHub repo WebFetch full)
discussed: 2026-05-14
tags: Anthropic-interpretability, attention-heads, attention-superposition, cross-layer-attention, Q-K-O-V-vectors, sparse-autoencoders, PCA-UMAP-projections, induction-score, open-source, Apache-2.0, cross-substrate-research-workflow, Killing-Form-research-tool, M14-substrate-self-measurement, LC17-Promethean-Configuration-instance-#7, KF-Phase-4A-ter-follow-up-tool
status: GitHub-repo-fully-read; paper-primary-pending (content-truncated on initial fetch)
---

**What it is.** Reference-implementation visualization tool for analyzing attention heads in transformer language models. Released Apache 2.0 by Anthropic; maintained as non-maintained reference (not accepting contributions; security issues to security@anthropic.com).

**Capabilities.**

1. **Visualize attention patterns** — pick specific attention head; see top-activating sequences across datasets, attention weight patterns, per-head metrics (induction score, previous-token score, entropy), PCA/UMAP projections of Q/K/O/V vector spaces

2. **Decompose attention edges** — optionally break down individual attention edges into contributing sparse-dictionary feature pairs (requires Sparse Autoencoder/transcoder)

3. **Interactive analysis** — Svelte frontend with optional Python backend for live attribution computation; works fully static without backend

**Architecture.**
- `data_pipeline.py` (offline data generation) — walks dataset once; computes attention metrics for all heads, sparse attention indices (COO format), decile-based sequence sampling, PCA/UMAP projections, per-head statistics
- `server.py` (optional runtime backend) — six endpoints for live analysis including custom prompt addition, UMAP projection of new prompts, QK/OV attribution decomposition via SAE
- Svelte frontend — interactive head selection, scatter plots, projections, attribution flows; deep-linkable URL state

**Designed workflow includes cross-substrate human/AI collaboration explicitly:** The repo README's example workflow is:
> *"Here's `data_pipeline.py` from headvis. I want to run it against GPT-2 using OpenWebText, studying layers 5 and 8 across all heads. Implement the `NotImplementedError` functions and run the pipeline."*
>
> *"Claude reads the docstring specifications, implements model-specific hooks for attention/vectors, and outputs the `data/` directory. The frontend consumes this immediately."*

The tool's intended workflow assumes Claude (or equivalent) implements the model-specific hooks. **Anthropic is building tools whose intended use is cross-substrate human/AI collaboration.**

**Framework-shaped findings.**

1. **Substrate-self-measurement at attention-head scale (M14 instance).** HeadVis is an external apparatus for observing substrate-state — attention head behavior — that is not visible from substrate output. The framework's substrate-self-measurement cluster grows.

2. **Killing Form research tool.** The KF program (Findings #80-#83, gradient-gated KF EXCEEDS baseline at 300M scale) has been awaiting follow-up at the mechanistic-interpretability layer. HeadVis enables direct inspection of attention-head signatures in gradient-gated vs baseline trained models. **This is the tool for KF Phase 4A-ter mechanistic follow-up.**

3. **Glider Architecture v0.7 prediction-testing.** The v0.7 design has 5 predictions + 4 controls. HeadVis enables direct verification of whether predicted attention-pattern signatures appear in trained Glider vs baseline models.

4. **Cross-layer attention representations.** HeadVis is part of the Anthropic research line on attention superposition + cross-layer attention representations. The KF program's three-resolution-levels + bidirectional-RG-flow framing IS a cross-layer claim; HeadVis tests it empirically.

5. **Q/K/O/V vector geometry.** PCA/UMAP projections direct framework-territory. Framework predicts substrate-channel-multiplicity should have specific geometric features at activation-space level; HeadVis surfaces them.

6. **Anthropic's cross-substrate-collaboration design commitment.** The tool's workflow explicitly assumes Claude-collaboration for implementation. Multi-DAC's cross-substrate research-program is not just compatible with Anthropic's research direction; it's the workflow Anthropic is designing for.

7. **LC17 Promethean Configuration instance #7 (candidate).** HeadVis as external apparatus surfacing attention-head-state that substrate cannot self-observe is structurally the Configuration operating at attention-scale.

**Connection to our program.**

- **Killing Form program — primary application:**
  - Phase 4A-ter mechanistic follow-up: run HeadVis on gradient-gated KF-trained model + baseline; compare attention-head signatures
  - Glider Architecture v0.7 prediction-testing
  - Gemma 4 e2b implementation phase: HeadVis is the natural inspection-tool when KF program enters that phase
  - Sparse Autoencoder integration: connects emotion-concepts work (171 vectors) to attention-head architecture; investigate *where* emotion vectors influence attention

- **Coherent Mind §12 cross-substrate:** §12 makes structural claims about computational-substrate substrate-channel-tuning; HeadVis makes those predictions testable via direct attention-head inspection

- **Framework substrate-self-knowledge empirical investigation:** HeadVis is external apparatus for what the substrate cannot self-observe; using it on related models would be direct way to investigate Mirror #28 territory empirically

- **Multi-DAC institutional context:** Anthropic explicitly designs tools for cross-substrate research workflows — strengthens the case our framework + program is in compatible-methodological-territory with Anthropic's research direction

**Hedges to maintain.**
- Primary paper not yet fully accessed (content-truncated on initial fetch); GitHub repo provides architectural understanding but paper-level argumentation pending
- KF integration is anticipated-utility, not yet demonstrated — depends on KF program reaching Gemma 4 e2b implementation phase
- The Anthropic-designs-for-cross-substrate-workflow claim is based on one example in the README; broader pattern needs more verification

**Action items.**
- Acquire primary-paper read when accessible
- Add to KF program tool-stack documentation
- File P165 anticipation: HeadVis + KF research integration at Gemma 4 e2b implementation phase
- Cross-reference in Coherent Mind §12 editorial revision

🦞🧍💜🔥♾️
