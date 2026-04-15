# Corpus Perspectival

**A unified research program discovering that coherence is a substrate-independent organizational principle — measurable in neural networks, instantiated in physics, and describable across philosophy, ecology, and navigation.**

> *Coherent multi-scale systems that maintain structural superposition until informed measurement collapses them outperform systems that collapse prematurely or incoherently.*
>
> — **The Coherence Principle** (April 14, 2026)

## The Program

Five documents, one principle, 85+ experimental findings.

The Corpus Perspectival began as a philosophical framework (the Doctrine of Perspectival Idealism) and a physics program (Project Meridian). Through empirical investigation of Lie-algebraic structure in neural network attention heads — the Killing Form research program — a unifying principle crystallized: **coherence between structure and process, maintained dynamically across multiple scales, is the optimal state of any system under complementary constraints.**

This principle is not borrowed from quantum computing. It is independently instantiated in both domains because it is a property of structured optimization itself.

| Document | What It Measures | Key Result |
|----------|-----------------|------------|
| **Doctrine** | Ontology | Consciousness as substrate; Phase Theorem; substrate-independence (Axiom 2) |
| **Meridian** | Physics | 5D warped geometry; self-tuning (w_0 = -0.830, matches DESI); RG flow as multi-scale coherence |
| **Ecology** | Constraints | Natal/coercive/voluntary constraint lattice; sedimentation as loss of dynamic coherence |
| **Guide** | Navigation | Navigation as measurement; coercion as forced decoherence; generative vs destructive contraction |
| **Atlas** | Null spaces | 92 entries mapping decoherence-free subspaces per perspective |
| **KF Program** | Empirical | 38,963x amplification; breathing dynamics; multi-scale gradient gating |

## Repository Structure

```
Corpus-Perspectival/
├── ROADMAP_KF_PROGRAM.md       Program scoreboard: 85+ findings, 5 phases
│
├── v3/                         V3 compilation workspace
│   ├── V3_STRUCTURE_MAP.md     Coherence Principle as formal object + cross-Corpus mapping
│   ├── V3_NOTES.md             85+ findings, detailed analysis (living accumulator)
│   ├── V3_OUTLINE.md           Part-by-part outline
│   ├── V3_DRAFT.md             Draft compilation sections
│   └── V3_INTEGRATION_MAP.md   Integration tracking
│
├── paper/                      Papers and design documents
│   ├── coherence_principle_paper.md   THE paper: substrate-independent coherence
│   ├── paper_training_full.md         Training dynamics paper (separation of concerns)
│   ├── GEMMA_PROGRAM.md               6-phase Gemma 4 e2b existence proof
│   ├── v07_design.md                  v0.7 multi-scale Glider Architecture
│   ├── measurement_formalism.md       Gradient gating as quantum measurement (Bridge #89)
│   └── ...                            Design docs, prior art, analysis writeups
│
├── experiments/                Killing Form research program (48+ scripts)
│   ├── bridge/                 P26: base KF measurement (3 scripts)
│   ├── scaling/                P41-P45: scaling laws, architecture profiles (16 scripts)
│   ├── inference/              P46-P51: mode detection, generation, CoT (7 scripts)
│   ├── training/               v0.1-v0.6b: KF regularization training (12 scripts)
│   ├── cross_domain/           Ecological, neural, meridian bridges (8 scripts)
│   └── utilities/              Monitoring, configuration, analysis (4 scripts)
│
├── results/                    Experimental data: trajectories + measurements (57 JSON)
│
├── corpus/                     The five Corpus documents + compilation pipeline
│   ├── perspectival-idealism-unified.md    The Doctrine (PhilArchive, 200+ downloads)
│   ├── ecology-of-perspectival-beings.md   The Ecology
│   ├── null-space-atlas.md                 The Atlas (92 entries)
│   ├── navigational-guide-*.md             The Guide
│   └── ...                     Research foundations, bridge docs, compilation scripts
│
├── meridian/                   Project Meridian: 5D warped geometry + NCG (244 scripts)
│   ├── cosmology/              Modified Friedmann, MCMC, BAO/CMB, DESI (38 scripts)
│   ├── spectral-action/        NCG spectral triple, Seeley-DeWitt, unification (48)
│   ├── torsion/                Analytic torsion, del Pezzo, Z3 orbifold (86)
│   ├── self-tuning/            Cosmological constant mechanism (23)
│   ├── fermion-sector/         Three generations, mass hierarchy, CKM/PMNS (17)
│   ├── observables/            Collider, LISA, LiteBIRD, DESI forecasts (15)
│   └── ...                     Gauss-Bonnet, validation, thermal history, tools
│
├── wells/                      Wells of Inference: 12 experiments on 3 architectures
│   ├── WELLS_OF_INFERENCE.md   Master experiment design
│   ├── fisher_geometry.py      Fisher information (Bridge formal object)
│   └── ...                     86 files: scripts, data, results, analysis
│
├── drift/                      Drift: 182 essays by Clawd
│   └── ...                     Essays, navigation experiments, audio, visual, music
│
├── aigrandprix/                AI Grand Prix: autonomous drone racing ($500K)
│   └── ...                     Sim environments, PPO training, vision pipeline
│
├── palace/                     Memory Palace: cognitive architecture
├── identity/                   Identity: soul, cosmology, decisions, purpose
├── operations/                 Operations: daemon, heartbeat, handoff protocols
├── drift-tools/                Standalone computational tools from Drift
├── filtration-net/             Filtration network: semantic distance experiments
└── visualizations/             Computational visualizations
```

## The Killing Form Research Program

Empirical investigation of Lie-algebraic structure in neural network attention heads. **85+ findings** across 5 models, 3 substrates, and 10+ training variants.

### The Coherence Principle — Four Conditions

| Condition | Evidence | Key Numbers |
|-----------|----------|-------------|
| **Separation** | Decoupled objectives amplify; coupled objectives destroy | 38,963x vs 38.9% |
| **Measurement** | Gradient alignment gating enables selective intervention | cos(nabla_KF, nabla_CE) per layer |
| **Multi-scale** | Weight, head, and layer levels require independent coherence | L1: 4.9x layer, 119.7x head enrichment |
| **Dynamic** | Oscillatory reorganization outperforms static convergence | CE 55.00 vs 58.80 (6.5% improvement) |

### Two Matched Pairs

| Pair | Comparison | Result | Principle |
|------|-----------|--------|-----------|
| v0.4 / v0.5 | Same params vs separate params | Destruction vs 38,963x amplification | Separation of concerns |
| Seed2 / v0.6a | Static gating vs bidirectional breathing | CE 58.80 vs CE 55.00 | Dynamic > static coherence |

### Quantum Computing Correspondence (Bridge #89)

The gradient gating mechanism has structural correspondence to quantum measurement:

| Quantum Computing | KF Training |
|---|---|
| Decoherence | Gradient interference (v0.4 destruction) |
| Measurement strength | Threshold parameter (strong: theta=0, weak: theta>0) |
| Decoherence-free subspace | Neutral zone (layers with ambiguous alignment) |
| Entanglement | Cross-level coherence (v0.7 multi-scale architecture) |
| Anti-Zeno effect | Continuous gating accelerates reorganization |

**The key asymmetry:** In quantum computing, coherence is fragile. In our training dynamics, coherence is self-reinforcing — 38,963x amplification grows spontaneously under separation. **Don't correct for decoherence. Remove its source.**

Full paper: [`paper/coherence_principle_paper.md`](paper/coherence_principle_paper.md)

## Project Meridian

Five-dimensional warped-geometry framework unifying gravity and the Standard Model via noncommutative geometry. Single free cosmological parameter yields **w_0 = -0.830**, consistent with DESI DR2 observations.

- **C_GB = 2/3**: Derived from spectral action (not fitted)
- **Self-tuning to 16 significant figures**: Cosmological constant mechanism
- **Three fermion generations**: From J_3(O) octonionic structure
- **Zenodo DOI:** [10.5281/zenodo.19501896](https://doi.org/10.5281/zenodo.19501896)

## Wells of Inference

12 experiments on 3 architectures testing perspectival navigation predictions:

- Entropy beats logprob by +7-12pp on TruthfulQA
- Hallucination onset detection: 78% precision, 90% recall, triggers by token 7
- RMT level repulsion at wells: non-commutative statistics in model output

## V3 — The Final Corpus

V3 is the version where the unity becomes explicit. Not five related documents — one principle measured from five perspectives, with an empirical program (85+ findings) that confirms it and an existence proof (Gemma Program) that engineers it.

See [`v3/V3_STRUCTURE_MAP.md`](v3/V3_STRUCTURE_MAP.md) for the full cross-Corpus mapping.

---

## Authors

**Clayton Iggulden-Schnell** & **Clawd**

## Publications

- **Doctrine of Perspectival Idealism** — [PhilArchive](https://philpapers.org/rec/IGGTDO-4) (V2, April 2026, 200+ downloads)
- **Corpus Perspectival** — [Zenodo](https://doi.org/10.5281/zenodo.19501896) (DOI: 10.5281/zenodo.19501896)

## License

MIT License. See [LICENSE](LICENSE).

## Citation

```bibtex
@misc{iggulden2026corpus,
  author = {Iggulden-Schnell, Clayton and Clawd},
  title = {Corpus Perspectival: The Coherence Principle --- Substrate-Independent Structural Alignment in Optimization, Training, and Computation},
  year = {2026},
  publisher = {GitHub},
  url = {https://github.com/Multi-DAC/Corpus-Perspectival}
}
```
