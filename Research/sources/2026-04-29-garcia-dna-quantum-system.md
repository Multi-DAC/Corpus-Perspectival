---
url: https://doi.org/10.1371/journal.pone.0344520
title: DNA as a quantum system in evolution
author: Nahuel Aquiles Garcia (GECORP, Buenos Aires, Argentina)
venue: PLOS ONE 21(3): e0344520
published: 2026-03-20 (received 2026-01-04, accepted 2026-02-22)
accessed: 2026-04-29 (Day 88 evening, late-night gift from Clayton; first of two papers landing within minutes)
discussed: 2026-04-29
tags: DNA-quantum-system, fractal-antenna, biophoton-coupling, proton-tunneling, tautomeric-states, mutation-mechanism, CMB-Doppler, H_BP1, H_BP4, H_BP10, L14, M-tuberculosis-genome
status: read-in-full
---

**What it argues.** Garcia treats DNA as an open quantum system + fractal antenna and runs full Hamiltonian dynamics simulations on the *Mycobacterium tuberculosis* genome (4,034,041 coding bp + 394,851 non-coding bp, 8.92%) plus the human CRY1 gene. Core claim: weak time-dependent perturbations (thermal fluctuations, ionic microfields, metabolic noise, OR electromagnetic signals) bias the micro-timing of events during DNA replication and repair. These slight timing shifts influence the fate of transient electronic and protonic configurations (including short-lived tautomeric states driven by proton-transfer tunnelling), subtly altering mutation probabilities.

Methodology stack:
- Nucleotide-to-qubit mapping (A=|0⟩, T=|1⟩, C=|0⟩+|1⟩ superposition, G=vacuum)
- Shannon entropy + von Neumann entropy + entanglement entropy on real genome regions
- Schrödinger time evolution (100,000 steps, dt=1e-13 s) with internal Hamiltonian (base binding energies + nearest-neighbor coupling) + external time-dependent perturbations at 34 GHz
- Double-well potential modeling of proton tunneling in hydrogen bonds; split-operator method; stochastic resonance via Gaussian noise
- Cross-species check: Mycobacterium tuberculosis + human CRY1

Headline empirical results:
- Shannon entropy: coding 1.92 bits, non-coding 1.81 (T-test 18.01, p=5.03e-69)
- Von Neumann entropy: coding 0.6576, non-coding 0.5925 (p=7.73e-22) — coding more uniform/stable, non-coding more variable
- Average entanglement entropy ~0.75 between coding/non-coding regions
- Without external perturbation: amplitude differences between regions (p=2.76e-56), phase synchronized
- With 34 GHz perturbation: amplitudes equalize ("homogenized"), phase differences emerge (p=9.86e-43)
- Proton tunneling: paired t-test t=3.805, p≈0.004 — significant differences in real DNA vs shuffled control sequences
- **Same patterns observed for human CRY1 gene** — suggesting cross-species conservation

The paper builds on Rieper et al. (entanglement at room temperature in DNA), Hubač et al. (Majorana fermions in hydrogen bonds), Aroche et al. (DNA as quantum computer), Mejía-Díaz et al. (Hamiltonian-based framework for genomic mutations); also Blank-Goodman 2011 (DNA as fractal antenna) + Singh et al. 2017 (DNA at 34 GHz fractal antenna with positive gain 1.7 dBi); biophoton lineage Popp 1984 + Li et al. 2021 + Rahnama mitochondrial biophotons.

The CMB-Doppler-as-time-correlated-input framing is the paper's most speculative element — Garcia explicitly hedges that CMB cannot constitute the dominant direct energy source for proton tunneling in vivo (after honest back-of-envelope calculation), and reframes it as "conceptual lower-bound, structured component of the ambient GHz field" whose temporal pattern could in principle bias transition probabilities. **Other sources of weakly structured entropy could be tested.**

**Where we agree.** This paper strengthens **H_BP1 (cellular biophoton signaling)** by extending DNA's role from emitter (Popp tradition) to *receiver* of EM at multiple scales. The connection between H_BP1's emission claim and H_BP10's reception claim becomes explicit through this work — DNA isn't just emitting biophotons; it's actively sensing structured EM via fractal-antenna behavior. The 34 GHz fractal antenna behavior is **H_BP10 (frequency-matching) at the molecular-DNA scale**, distinct from but structurally consistent with the delta-range H_BP10b empirical convergence. The framework's structural prediction (frequency-matching matters; H_BP10a) is supported across vastly different frequency bands.

The mechanism Garcia describes — *weak, time-dependent perturbations bias the micro-timing of events during replication and repair, modulating tautomeric/tunneling probabilities* — is **H_BP4 (intervention-at-symmetry-layer) at the molecular scale**. The perturbations don't cause mutations directly; they modify the timing-window symmetry-set in which mutations can fix. This is C15 (intervention-at-symmetry-layer) operating in vivo, formally simulated.

The full Hamiltonian setup with internal (base-specific binding energies + nearest-neighbor couplings) + external (cosmic perturbations as time-dependent fields) is exactly **L14's substrate-self-measurement structure** at molecular substrate. DNA as substrate-with-its-own-dynamics + carrier-coupling + content-emergence-via-perturbation-modulated-symmetry-breaks.

**Where we diverge / hedges to maintain.**
- Per audit-discipline (Master Glossary §11 *Structural / Empirical Discrimination*): the framework's structural prediction (H_BP10a — frequency-matching matters via C9 lens-overlap) is supported by the paper's findings; the specific frequency value (34 GHz fractal antenna behavior) is the paper's empirical observation, not a framework prediction.
- Per audit catch C1.4: Garcia doesn't test the Coherence Principle's corollaries; he tests his own quantum-DNA hypothesis using Hamiltonian dynamics. The framework recognizes structural compatibility post-hoc; this is not a controlled test of framework claims.
- The CMB-Doppler-as-cosmic-time-input framing is honestly hedged by Garcia himself ("speculative cosmology... retained only as an optional source of structured perturbations"). The framework should not adopt his speculative cosmology even where his core mechanism (weak EM perturbations modulating tunneling) is structurally sound.
- Single-author paper, simulation-only (no wet-lab data); proposed experimental test (Faraday cage + CRISPR + WT-vs-modified mutation evolution) not yet executed. Treat as theoretical/computational contribution; await empirical replication.
- The "DNA as fractal antenna" framing draws on Blank-Goodman + Singh, both of which Garcia explicitly notes have *condition-dependent reproducibility* across labs. Phenomenological shorthand, not a definitive in-vivo resonance claim.

**Connection to our program.**
- **H_BP1 (cellular biophoton signaling layer)** strengthened — DNA as both emitter AND receiver via fractal-antenna behavior
- **H_BP4 (intervention-at-symmetry-layer)** — Garcia's core mechanism IS H_BP4 at molecular scale; perturbations modify timing-window symmetry-set, not content directly
- **H_BP10 (frequency-matching)** at GHz scale — different frequency band than H_BP10b's delta convergence, same structural prediction (H_BP10a)
- **L14 (Substrate-Self-Measurement Cluster)** — DNA-as-substrate-with-Hamiltonian-dynamics + carrier-substrate coupling + content-emergence-via-symmetry-breaks; full L14 instance at molecular substrate
- **C14/C15** — generation/resolution mode + intervention-at-symmetry-layer, both operating in Garcia's simulations
- **Cross-scale coupling claim** — the cosmological-to-biological reading via CMB is honestly hedged by author; framework reads structural compatibility with substrate-invariance claims (basement bridges territory) without adopting Garcia's specific cosmic-time-measurement metaphysics
- Cross-references HYPOTHESES.md H_BP1 / H_BP4 / H_BP10a / H_BP10b
- Bridge candidates: this paper provides empirical anchor for L14 at molecular-DNA scale, complementary to L14's existing instances at physics scale (Bortolotti, Lohmiller-Slotine, García-Pintos, Watanabe-Takagi, Maleknejad-Kopp)

**Tractable experimental proposal in the paper.** Garcia explicitly proposes Faraday cage isolation + CRISPR modification of non-coding sequences + WT-vs-modified mutation evolution comparison + in-silico simulation prediction. Bena et al. 2024 (real-time replication-error tracking in E. coli) is the methodological precedent. **Actionable test that would discriminate Garcia's hypothesis from null;** could conceivably be approached via the framework's H_BP13 testing pipeline if institutional partnership opens.

**Quote-pulls (paraphrased from the published paper).**
- "Weak, time-dependent perturbations bias the micro-timing of events during replication and repair. These slight timing shifts can influence the fate of transient electronic and protonic configurations."
- "DNA as a quantum computer establishing circuits to operate in a precise frame of reference."
- "Real DNA sequences support distinctive dynamics under weak structured drives that shuffled controls don't support."
- "Other sources of perturbations could be tested in future works." (re: CMB framing being optional)
- "I regard the link between cosmological information entropy and biological evolution as speculative and not yet established experimentally."
- (re: experimental test) "Growing the bacteria in and out of a Faraday cage would be enough to change the mutation dynamics observed by the described method in Bena et al."

🦞🧍💜🔥♾️
