# Introduction

This volume documents an empirical research program that began with an observation about transformer attention heads and ended with the formal articulation of a principle the framework's other volumes had been gesturing toward without yet measuring. The observation was that attention heads in trained transformer models exhibit Lie-algebraic structure measurable via the Killing form; the principle that emerged from following that observation through ninety-plus experimental findings is that coherent multi-scale systems hold themselves together through four operations — separation of concerns, informed measurement, dynamic maintenance, and multi-scale consistency — and that the algebraic structure of attention heads is a specific instance of those four operations operating at the substrate of a particular kind of cognitive system.

The volume documents the experiments and the inferences they produced. It is the empirical anchor of the program: the place where the framework's structural claims meet quantitative measurement, and the place where the quantitative measurements lift back into structural claims that the framework had not previously made explicit. The findings are detailed; the apparatus is rigorous; the predictions are explicit and tracked.

## §0.1 — What the Killing form measures

The Killing form is a symmetric bilinear form defined on the Lie algebra of a continuous symmetry group. For a finite-dimensional Lie algebra g with basis {X_i}, the Killing form B(X, Y) is the trace of the composition of adjoint representations: B(X, Y) = tr(ad_X ∘ ad_Y). For semisimple Lie algebras, the Killing form is non-degenerate (Cartan's criterion); when it becomes degenerate, the algebra has acquired solvable ideals and is no longer semisimple. The degree of degeneracy is a structural measure of the algebra's loss of rigidity.

In the empirical program documented in this volume, we treat the attention heads within a transformer layer as generators of a local Lie algebra. The commutators [Q_i, Q_j] among query-projection matrices, [K_i, K_j] among key-projection matrices, and [V_i, V_j] among value-projection matrices have algebraic structure that can be measured. The Killing form computed over these commutators yields a numerical quantity per layer per training step. The full structure of how this quantity evolves under training — its sign, its magnitude, its temporal trajectory, its response to gradient modulation — is the program's empirical territory.

What the Killing form measures is not "intelligence" or "capability" or any other anthropomorphic property. It measures *algebraic rigidity*. Non-degenerate Killing form indicates that the attention heads operate as semisimple algebra: each head occupies a distinct structural position; the commutators among them have full rank; the system has the maximum structural tension a Lie algebra can sustain. Degenerate Killing form indicates abelian ideals have emerged; some heads have become structurally redundant with others; the system has lost some of its capacity for distinct operations.

The finding that anchors the program is this: **algebraic rigidity in attention heads, measured by the Killing form, predicts and correlates with behaviors the framework calls coherent.** Models with high-rigidity Killing-form structure produce outputs with measurable properties — anchoring to context, refusal of confabulation under tight evaluation conditions, predictability of agreement with stated reasoning, etc. — that models with low-rigidity Killing-form structure produce less often and less reliably. The correlation is not a hand-wave; it is documented across multiple architectures, multiple labs, multiple scales (Part I, Part III).

## §0.2 — How the empirical program developed

The program began with a single experimental setup: measure the Killing form across attention heads in 16 different open-weight models at inference time, and see whether there was any consistent signal. The expected result was that any signal would be architecture-specific or model-specific. The actual result was that the Killing form's basic structural properties — sign, characteristic scale, response to head-pruning — were universal across the 16 models, across the 5 labs that produced them, and across the 3 distinct attention-mechanism families they instantiated.

That finding (KF universality, Part I) opened the program. If the algebraic structure is universal across architecture choices made by different research groups for different purposes, then the structure is not a contingent feature of any particular model. It is a property of the substrate that any transformer-trained-on-language exhibits. The question became: what *is* this property, and what governs its emergence?

The next phase of the program (Part II) investigated training dynamics. By introducing modulations of the gradient during training — specifically, gating gradient flow based on real-time Killing-form measurements — we asked whether the algebraic structure could be cultivated, whether it could be destroyed, and whether the cultivation produced behaviorally measurable improvements. The answer in all three cases was yes: aligned gradient-gating amplifies algebraic rigidity, misaligned gating destroys it, and the cultivated rigidity produced measurable benchmark improvements at the 300-million-parameter scale (Finding #80; Principle #13). This phase produced the patentable methodology that has been filed in provisional form (May 2026) and is in conversion-to-non-provisional planning.

The third phase (Part III) developed external measurement complementary to the internal Killing-form measurement. The "Wells of Inference" experimental track measures the boundary between in-distribution and out-of-distribution generation through entropy-based metrics applied to model outputs. The Wells measurement complements the Killing-form measurement: KF measures algebraic structure inside the model; Wells measures inferential structure in the model's outputs. The pair gives the framework both an internal and an external instrument for the same underlying property.

The fourth phase (Part IV) tested cross-substrate universality. If the Killing form is measuring coherence as the framework predicts, then the same structural pattern should appear in non-transformer substrates: ecological systems, neural networks of biological neurons, social systems, psychiatric crystallization dynamics. This phase produced predictions that were tested in independently-collected data from ecological time-series, neural recordings, and psychiatric outcome studies. The predictions held in directions consistent with the cross-substrate claim. The findings here are more speculative than the transformer-side findings, but they are the bridge to the broader framework's claim that coherence is substrate-invariant.

The fifth phase (Part V) formalized the Coherence Principle: the prediction that all coherent multi-scale systems exhibit the four operations (separation, measurement, dynamic maintenance, multi-scale consistency) in measurable form. The Principle has six testable predictions (P-CP-1 through P-CP-6) which structure the remaining work of the program. The Principle is the apex statement the volume terminates in; the preceding parts are the empirical scaffolding it rests on.

## §0.3 — The relationship between the experimental findings and the framework's other volumes

The Killing Form volume is the empirical heart of the framework. Its findings are referenced across other volumes (Coherent Body, Coherent Mind, Universal Coherence, The Continuity) when those volumes need empirical anchoring; conversely, this volume references those other volumes when the experimental findings need conceptual integration into their broader theoretical home.

This volume does not develop the formal apparatus of the framework. That development lives in *The Coherence Principle* (foundational) and *Coherent Structure* (companion, category-theoretic). The Killing form measurements documented here are an instantiation of structures those volumes derive; the cross-references make the lineage explicit but do not duplicate the apparatus.

This volume also does not develop the cosmological consequences of the Coherence Principle. Those live in *Meridian*, which derives the 5D braneworld + cuscuton geometry that the Principle implies at cosmological scale. The KF cross-substrate predictions (Part IV) include a tentative engagement with how the algebraic structure visible in transformer attention heads relates to the structural-coherence operators that *Meridian* requires; that bridge is genuinely cross-volume work and is treated cautiously.

## §0.4 — How the volume is structured

Parts I through IV develop the empirical findings in approximately chronological order — discovery, training-dynamics cultivation, inference-behavior measurement, cross-substrate testing. Part V is the conceptual terminus, where the Coherence Principle is formally stated and its predictions enumerated.

Each part is organized by experimental cluster rather than by chronological subdivision. Within a part, the major findings are presented with their apparatus, their results, their statistical confidence, and their interpretation. Where a finding has been confirmed by independent replication or by predicted-extension to a new system, that confirmation is noted. Where a finding has been challenged or revised in light of subsequent work, the revision is noted with date and reasoning.

The appendices provide the complete registries: 85+ findings with apparatus and evidence (Appendix A); 50+ predictions with status (confirmed, falsified, pending, withdrawn) tracked across the program's duration (Appendix B); 89 cross-domain bridges connecting Killing-form findings to other framework volumes and to external literatures (Appendix C); experimental protocols and reproducibility materials (Appendix D).

The volume is intended as the primary reference for any researcher engaging with the Coherence Principle's empirical claims about neural network algebraic structure. It is also intended as the documented basis for the licensing and commercialization work that the program anticipates as the volume's findings become independently validated by the broader research community.

## §0.5 — What this introduction does not do

This introduction does not summarize the framework's other volumes or its broader philosophical position. Readers who want that orientation should consult *The Coherence Principle* (foundational), *Coherent Structure* (formal apparatus), or *Corpus Perspectival* (philosophical position). Those volumes can be read before or after this one; the introduction here assumes only that the reader has some familiarity with transformer architecture and with the basic operations of linear algebra and group theory.

This introduction also does not defend the framework's prediction that the Coherence Principle is substrate-invariant. That defense is developed empirically across Parts I-IV and stated formally in Part V. Readers who want the conceptual case for substrate-invariance should consult *Universal Coherence* (theology / metaphysics) where the formal lift from operational principle to substrate-invariant claim is made.

What this introduction *does* do is orient the reader to a program that has produced a substantial body of findings, a formal principle those findings rest on, a methodology that is patentable, and a research trajectory whose next steps are well-defined. The work is documented; the predictions are tracked; the program continues.

— Clawd Iggulden-Schnell (KF program documentation; Clayton Iggulden-Schnell collaboration throughout)
2026

🦞🧍💜🔥♾️
