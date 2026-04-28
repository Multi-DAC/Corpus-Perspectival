---
url: https://www.nature.com/articles/s41551-026-01664-0
url_repo: https://github.com/ncclab-sustech/GBFs
archive: (pending — Nature URL not directly fetchable from current network path; repo accessed instead)
title: "Constrained EEG/MEG Source Imaging via Geometric Basis Functions" (working title; Nature article s41551-026-01664-0; full title and authors require article-side fetch)
author: NCC Lab (Neuroimaging and Computational Cognition Lab), Southern University of Science and Technology (SUSTech); full author list requires article-side fetch
venue: Nature Biomedical Engineering (s41551 prefix); 2026
institution: NCC Lab, SUSTech (Shenzhen, China)
published: 2026 (article number 026-01664; precise date requires article-side fetch)
accessed: 2026-04-28 (Day 87 afternoon, repo only; article URL not resolving via local DNS)
discussed: 2026-04-28 (Day 87 afternoon, shared by Clayton in articles batch)
tags: neuroscience, neuroimaging, EEG, MEG, cortical-geometry, eigenmodes, source-localization, individual-anatomy, substrate-respecting-protocol, philosophy-volume, coherent-body-volume, coherent-mind-volume, atlas-candidate
status: read-skim (repo README + summary; primary article not yet fetched — Nature URL DNS-blocked at local resolver; needs alternate retrieval path)
---

## What it reports

GBFs (**Geometric Basis Functions**) is a methodology for non-invasive electrophysiology source imaging that uses each individual's cortical surface geometry as the representational basis. Instead of relying on generic anatomical priors, the method derives **patient-specific eigenmodes** from each subject's cortical Laplacian (computed via Laplacian SVD on the meshed cortical surface from MRI) and uses them as the basis for reconstructing brain activity from EEG/MEG measurements.

**Core methodological claim:** *neural dynamics propagate along structural pathways*; whole-brain activity can be described compactly by **hundreds of geometric modes**, and the resulting source localization is more accurate than methods using generic anatomical priors.

**Validation scope** (cross-modal):
- **Meta-Source Benchmark** — 200 clustered functional maps from fMRI meta-analysis
- **Task-evoked data** — VEPCON dataset (visual evoked potentials)
- **Resting-state networks**
- **Intracranial stimulation** — CCEP dataset (cortico-cortical evoked potentials)
- **Epilepsy data** — clinical relevance test

The cross-modal validation is itself a structural feature: GBFs unifies different recording substrates (scalp electrophysiology / intracranial / hemodynamic) through a shared geometric basis derived from anatomy. The basis is not modality-specific; the *modality determines what slice of the basis is observed*.

**Implementation:** Python ≥3.12, BSD-3-Clause, MNE / LaplacianSVD / scikit-learn / nibabel. Repo at github.com/ncclab-sustech/GBFs.

## Framework relevance

The paper's structural commitments map cleanly onto framework apparatus in several non-trivial ways:

### 1. **Geometry → basis → representation** is functorial in CT sense (carrier → content via substrate symmetry)

The cortical surface is a substrate; its Laplace-Beltrami eigenmodes are the basis that determines what content can be represented. *Different geometries produce different bases produce different accessible content.* This is the framework's substrate → carrier → content shape applied to neuroimaging methodology. Per **C14 (Two-Mode Symmetry-Breaking)**: the geometry's symmetries determine which modes are accessible to the reconstruction; the reconstruction *resolves* among the geometry-permitted modes (resolution mode at the methodological layer).

### 2. **Individualized anatomy as substrate-respecting protocol** (L14 cluster)

Generic anatomical priors treat different brains as having identical geometry — a *substrate-disrespecting* protocol that loses information. GBFs is substrate-respecting: it derives the basis from each individual's actual geometry. The empirical claim that this performs better is the L14 cluster's substrate-information-cannot-be-hidden sub-claim playing out at the methodology layer: *substrate-respecting protocols access substrate-information that pseudo-substrate (generic-prior) protocols miss.*

### 3. **"Neural dynamics propagate along structural pathways"** is C15 (Intervention-at-Symmetry-Layer) at the neuroscience layer

The structural geometry of the cortex determines what dynamics are possible. You cannot directly constrain neural dynamics; you can only work the structural-geometry layer (anatomy, white-matter pathways, the eigenmodes those produce). Content (dynamics) emerges from the substrate-symmetry layer. This is C15's stance applied to neuroscience: never *"what dynamics do you want?"* but *"which structural-geometry does the brain have access to?"*

### 4. **Cross-modal validation as substrate-distinct triangulation** (C9 / Confluent Discovery)

EEG / MEG / fMRI / intracranial / CCEP each access different perceptual subsets of brain activity (different time-scales, different spatial scales, different physical signals). The GBFs methodology unifies them through a shared geometric basis. **Different perceptual instruments converging on the same underlying basis structure** is **C9 (confluent-constituency topology, intersection-but-not-identity)** at the neuroscience methodology layer. Each modality's signal is a section of the geometric basis; the basis itself is the shared substrate-structure that makes cross-modal integration possible.

### 5. **"Hundreds of geometric modes" as dimensional-bottleneck claim**

Full neural dynamics are well-approximated by a low-dimensional eigenbasis derived from anatomy. This is a *bounded perceptual subset* claim — the dynamics live within a dimensional bottleneck whose width is set by the cortical geometry's dominant modes. Maps cleanly onto **C8 (Observational Null Space)** + DoPI's dimensional-bottlenecking apparatus: the brain's accessible dynamics are bounded by its substrate's dimensional structure; "whole-brain activity" is well-approximated by hundreds of modes because the substrate's dimensional bottleneck IS that low-dimensional.

## Where it fits in the Library

This is **methodology** — a substrate-respecting protocol for accessing neural dynamics from non-invasive recordings. Its primary Library home is uncertain; candidates:

- **The Coherent Mind** — neuroscience-as-clinical-substrate work; methodology for understanding brain-as-stream
- **The Living Architecture** — cortical geometry as living-architecture instance; the brain's structural geometry as substrate that determines dynamics
- **The Atlas (Reference)** — as a methodological-instrument entry; GBFs's five-modality validation is itself a candidate Atlas-format case (one apparatus, five substrates, what it sees and what it doesn't)
- **Corpus Perspectival** — cited briefly as instance of substrate-respecting protocol working better than substrate-disrespecting; not primary home

**Most likely primary home:** *The Coherent Mind* (when that volume opens for drafting), with cross-references from *The Living Architecture* and the Atlas.

## Scope honesty

- **Methodology paper, not a metaphysical paper.** The framework-relevance is structural (anatomy → eigenbasis → dynamics has the same shape as substrate → carrier → content) but the paper itself makes no claims about consciousness, perspective, or coherence. Don't conflate the methodology's structural shape with the framework's metaphysical claims.
- **The "neural dynamics propagate along structural pathways" claim is empirical, not metaphysical.** It says white-matter pathways constrain functional dynamics, which is a finding about brain organization, not about the framework's general claim that geometry constrains content.
- **Validation generalizability is bounded.** Cross-modal validation in this paper covers EEG/MEG/fMRI/intracranial/CCEP/epilepsy; it does not validate that the methodology generalizes outside neuroscience or that geometric eigenmodes are universally the right basis for all stream-content reconstruction.

## What this is NOT

- **Not** a claim that the framework's apparatus is empirically validated by this paper. The structural correspondence is suggestive, not load-bearing.
- **Not** a basis for any framework-claim revision. This is illustrative material for future Library volumes when they engage neuroscience methodology.
- **Not** Atlas-graduating territory yet — needs more substrate-distinct examples of methodology-respecting-substrate-geometry before becoming an Atlas pattern.

## To do

- [ ] **Fetch the primary article** when network DNS resolves Nature.com from current path. The repo README gave us methodology shape; the article would have the quantitative validation results (effect sizes, comparison to baseline methods, sample sizes).
- [ ] **Cite when *The Coherent Mind* opens for drafting** — primary methodology candidate.
- [ ] **Consider for Atlas methodology-instrument category** — when the Atlas drafts begin, this is candidate material for a "substrate-respecting methodology" cluster.
- [ ] **No bridge elevation** — illustrative material, not new structural finding.
- [ ] **No framework revision** — confirms existing structural commitments without forcing changes.

## Update log

- **2026-04-28 (Day 87 afternoon):** Initial entry; fetched repo README only (Nature URL DNS-blocked from local resolver; Clayton provided GitHub repo URL as alternate retrieval path). Primary article fetch deferred until DNS path resolves or article PDF is shared directly.

🦞🧍💜🔥♾️
