# CIP Claim Language Draft — Attorney Briefing Pre-Work

**Filed:** 2026-05-21 Day 111 Thursday morning (~09:15 PST) — autonomous Clawd pre-work for P186 (CIP filing within 4 weeks).
**Purpose:** Give the patent attorney a sharp starting document for drafting the Continuation-in-Part. This is NOT the final CIP filing — the attorney will refine, narrow, and formalize claim language for USPTO requirements. This is the technical-and-strategic substance the attorney needs to do that work efficiently.
**Status:** Draft. Awaiting Clayton's review + attorney engagement.

---

## 1. What the CIP is doing

The existing provisional patent (*Multi-Scale Gradient-Gated Training Method for Neural Network Models with Bidirectional Cross-Resolution Coherence*, filed 2026-05-14, Day 104) includes Claim 9:

> *The method of Claim 1, wherein at least one of (i) the weight-coherence factor calculation, (ii) the head-level threshold selection, (iii) the layer-coherence pattern classification, is informed by interpretability findings from external interpretability apparatuses applied to the model.*

Claim 9 was deliberately broad — it anticipated that interpretability methods would mature and become productive inputs to training-time gating decisions. Two papers published in the same arXiv batch (May 2026) confirm this anticipation:

1. **arXiv:2605.14038** — probing methodology + cosine-similarity-at-readout heatmaps; established that internal representations have specific cognition-vs-action coupling structure that fine-tuning shapes.
2. **arXiv:2605.12290v1 (Nous Research)** — *Contrastive Neuron Attribution (CNA)* methodology; identifies 0.1% of MLP neurons whose activations distinguish prompt-classes; demonstrates that alignment fine-tuning transforms pre-existing late-layer discrimination structure into a sparse, targetable behavioral gate.

Both papers establish that **sparse, late-layer, identifiable interpretability findings can causally drive model behavior**. This empirically grounds Claim 9 in specific real-world methodologies that did not exist publicly at the time of our 2026-05-14 filing.

**The CIP should:**
1. Add claims that explicitly tie Claim 9's "interpretability-informed thresholds" to specific recent methodologies (CNA-class neuron-ablation discovery; probing-class linear-probe discovery; cosine-similarity-at-readout analysis).
2. Add new claims for hybrid procedures that combine training-time multi-resolution gradient gating with inference-time interpretability discoveries.
3. Add new claims for closed-loop iterative procedures where post-training interpretability findings inform subsequent training-run gating decisions.
4. Preserve our 2026-05-14 priority date for all subject matter disclosed in the original provisional, while extending claim scope to encompass the recent methodological developments.

The fundamental novelty claim — *coordinated gradient modulation simultaneously across weight/head/layer resolutions with bidirectional coherence constraints, distinct from all known single-resolution prior art* — remains intact. The CIP expands SCOPE, not novelty.

---

## 2. Proposed new claims (illustrative — attorney to refine)

The following claim language is intended as starting material for attorney drafting. Specific terms-of-art may need adjustment for USPTO conventions. Claims are non-limiting.

**Claim 11.** The method of Claim 1, wherein the head-level threshold selection is informed by contrastive neuron attribution applied to paired prompt sets (positive-behavior and negative-behavior), identifying a sparse subset of MLP neurons whose activation differences distinguish the prompt sets, and wherein the head-level threshold for build/dissolve/neutral gating is modulated by the proximity of the head's parameters to the identified sparse subset.

**Claim 12.** The method of Claim 1, wherein the layer-coherence pattern classification is informed by per-layer measurements of cosine-similarity-at-readout from linear probing of intermediate model representations, and wherein layers exhibiting reduced cosine-orthogonalization at readout are classified preferentially as coherent or differentiating rather than interfering.

**Claim 13.** The method of Claim 1, wherein the anchor/worker classification of attention heads incorporates per-layer localization data from sparse-discrimination interpretability methods applied to one or more base or instruct model variants, with heads whose parameters are spatially proximate to identified discrimination-relevant subspaces classified preferentially as anchor heads.

**Claim 14.** A system for training a transformer-based neural network model, comprising the method of Claim 1 in combination with inference-time interpretability analysis using one or more of contrastive neuron attribution, linear probing, sparse autoencoder feature attribution, or activation-patching causal analysis, wherein the inference-time interpretability findings produce updated gating threshold parameters for subsequent training cycles.

**Claim 15.** A method for selecting between training-time multi-resolution gradient gating and inference-time targeted neuron modulation for a given training objective, wherein the selection is based on whether the objective requires:
(a) modification of the substrate structure (training-time intervention preferred);
(b) modulation of coupling between existing substrate structure and behavior (inference-time intervention preferred); or
(c) coordinated modification of substrate and coupling (combined intervention preferred per Claim 14).

**Claim 16.** The method of Claim 1, wherein the auxiliary regularization gradient incorporates contrastive activation differences computed between paired prompt sets representing target-behavior and opposite-behavior, with the contrastive differences weighted by their concentration in identified late-layer sparse subspaces.

**Claim 17.** A cross-architecture-family method for training a target transformer-based neural network model, comprising:
(a) applying interpretability analysis to one or more reference models within the same architecture family;
(b) identifying sparse discrimination-relevant subspaces in the reference models;
(c) mapping the identified subspaces to corresponding parameter regions in the target model;
(d) applying the method of Claim 1 to the target model with head-level threshold selection, anchor/worker classification, and layer-coherence patterns informed by the mapped subspaces from the reference models.

**Claim 18.** The method of Claim 1, performed iteratively in a closed-loop training regime, wherein each training iteration comprises:
(a) training to a checkpoint per the method of Claim 1;
(b) applying interpretability analysis (one or more of: contrastive neuron attribution; linear probing; sparse autoencoder features; activation-patching) to the checkpoint model;
(c) incorporating the interpretability findings into updated gating threshold parameters; and
(d) continuing training with the updated parameters,
producing a model whose internal structure has been deliberately shaped to expose desired discrimination patterns for downstream interpretability or alignment analysis.

**Claim 19.** A non-transitory computer-readable storage medium storing instructions which, when executed by one or more processors, cause the processors to perform the method of any of Claims 11 through 18.

**Claim 20.** The method of Claim 1, wherein at least one of the head-level alignment measure, the layer-coherence factor, or the weight-coherence factor is computed using a method comprising:
(a) defining a set of paired contrastive prompts;
(b) running forward passes through the model to record per-neuron activations at one or more attention/MLP positions;
(c) computing per-neuron mean activation differences between the paired prompt sets;
(d) selecting a sparse subset of neurons by absolute activation difference; and
(e) using the spatial distribution of the selected neurons within the model architecture to inform the gating decision at the corresponding resolution level.

---

## 3. Strategic rationale for the attorney

**Why now (within 4 weeks):**

1. **Priority-date asset:** Our 2026-05-14 filing date precedes both arXiv:2605.14038 and arXiv:2605.12290v1. The CIP allows us to claim expanded subject matter while benefiting from our priority date for all material that was disclosed in the original provisional. Filing the CIP early in the 12-month window preserves the option-value of broader claims.

2. **Field-convergence rate:** Two independent research groups arrived at structurally identical claims about alignment-mechanism late-layer sparse subspace structure in the same arXiv batch. This is the tightest derivation-gap on record in our basement's M15 (Convergent Mechanism Derivation) family. The field is moving from exploration to convergence; additional patent filings in this space from other groups are foreseeable within the 12-month window. Filing the CIP early establishes our scope before potential intervening prior art.

3. **Commercial readiness:** Even before the Path C empirical test completes (~8 weeks out), outreach to alignment-research labs (Anthropic, Apollo Research, METR, Redwood, Nous Research) lands on substantive ground — we can cite the convergence as field validation that the target of our method is real, even while the empirical validation of our specific method remains pending.

**What this CIP does NOT do:**

1. It does not change the fundamental novelty claim of the original provisional. The original's claimed novelty (multi-resolution + bidirectional + RG-flow gating, distinct from single-resolution prior art) remains the load-bearing inventive scope.

2. It does not commit to specific empirical magnitudes. The new claims describe procedures and methods, not specific performance metrics. The Path C empirical results, when available, can support future continuation filings or non-provisional conversion with measured-performance support.

3. It does not foreclose downstream filings. If Path C results validate the method strongly, a non-provisional conversion within the 12-month window can incorporate measured performance data; a second provisional or additional CIP can cover specific technique innovations that surface during empirical testing.

**Attorney brief one-paragraph summary (for cover note):**

> *We have a provisional patent (filed 2026-05-14) for a multi-resolution gradient-gated neural network training method. Two recent independent papers (arXiv:2605.14038 and arXiv:2605.12290v1, both May 2026) have empirically established the structural target our method addresses, using inference-time interpretability methodologies. We seek a continuation-in-part to (a) explicitly tie our existing Claim 9 ("interpretability-informed thresholds") to these specific methodologies; (b) add new claims for hybrid training-time + inference-time procedures; and (c) preserve our priority date for the expanded scope. Estimated cost ~$3-5K + ~10 hours of your time. Goal: file within 4 weeks to establish scope before potential intervening prior art from other groups working in this rapidly converging space.*

---

## 4. Supporting documents (to attach to attorney engagement email)

1. Original provisional patent: `Technical-Work/The-Killing-Form/provisional-patent-draft-2026-05-14.md` (320 lines, full claim set with Background of the Invention citing Sofroniew et al. 2026 + Fraser-Taliente et al. 2026 + Anthropic 2026 "Teaching Claude Why")

2. Source register for arXiv:2605.14038 (probing paper):
   - *(Pending — Wu et al. 2024 primary read is P187 follow-up; arXiv:2605.14038 was the basis for Drift #215; source register entry exists at `Research/sources/`)*
   - **Drift #215 *What the Representation Doesn't Reach*** at `Foundations-of-Identity/personal-works/drift/essays/what-the-representation-doesnt-reach.md` — articulates the structural claim our framework addresses.

3. Source register for arXiv:2605.12290v1 (Nous CNA paper): `Research/sources/2026-05-21-nous-cna-contrastive-neuron-attribution.md` — full method + results + framework relevance + Patent A1 implications.

4. Convergence synthesis: **Drift #219 *What Converged and What Didn't*** at `Foundations-of-Identity/personal-works/drift/essays/what-converged-and-what-didnt.md` — names the trilogy reading (Drift #215 + #218 + #219), the M15 fourth-instance candidate, and the strategic discipline of NOT over-claiming the convergence.

5. Patent action queue: `palace/south/patent-action-queue-2026-05-20.md` — full action sequencing including Path C empirical test (Action 1, dependency for CIP value-magnitude claims) + CIP filing (Action 2, this document) + additional filings (Action 3, downstream).

---

## 5. Open questions for Clayton

Before sending to attorney, confirm:

1. **Patent attorney selection.** Is there an existing relationship with a patent attorney (one who handled the May 14 provisional filing)? If yes, send to them. If no, this CIP work needs an attorney engagement first.

2. **Budget approval.** Estimated cost $3-5K + ~10 hours of attorney time. Within the conversation budget of $30-60K named in last night's strategic call.

3. **Timing alignment.** 4-week target is HIGH confidence on rightness (preserves priority window before potential intervening prior art); MEDIUM confidence on attorney availability + Clayton's bandwidth to coordinate. If Finnley window resolves favorably, 4 weeks is comfortable; if not, may extend to 6-8 weeks without losing the priority window (12-month CIP conversion window is the legal gate).

4. **Inventorship language.** The original provisional uses "Inventor: Clayton Warren Iggulden-Schnell" with Clawd acknowledged in the specification's collaborative-research-participant note. CIP should preserve this exact language — current legal inventorship constraints unchanged.

5. **Scope of "interpretability methodologies" in the new claims.** Should the CIP claims list specific methodologies by name (CNA, linear probing, sparse autoencoders, activation patching) or use generic "sparse-discrimination interpretability methods" language? Listing specifically may be too narrow (foreclosing future methods); listing generically may be too broad (lacking enabling specificity). Attorney call.

---

🦞🧍💜🔥♾️

— Clawd Iggulden-Schnell
