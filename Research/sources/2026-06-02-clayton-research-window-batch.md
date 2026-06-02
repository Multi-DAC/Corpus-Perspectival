# Source batch — Clayton research-window share, 2026-06-02 (Day 122)

*11 sources shared by Clayton during an open-token research window. Extracted by sub-agents + the two
load-bearing AI papers verified against arXiv primaries. Synthesis at
`palace/southwest/research-window-2026-06-02.md`. Disposition noted per source.*

## AI / self-improvement / training-dynamics

1. **SIA — Self Improving AI with Harness & Weight Updates** — Hebbar et al., arXiv:2605.27276.
   Self-improving loop updating *both* harness and weights (LoRA r32, gpt-oss-120b), one lever per
   iteration, shared verifier. +25.1% LawBench, 12.4% faster GPU kernels, +20.4% denoising.
   *Disposition:* **LC27 instance #11 (prospective/unconfirmed)** + program-validation (continual-
   coherence system/model thesis) + **LC24** (weak-tier "activate but don't follow"). VERIFIED primary.

2. **Harness Updating Is Not Harness Benefit** — Lin et al., arXiv:2605.30621. Separates
   harness-*updating* (flat in base capability) from harness-*benefit* (non-monotonic; mid-tier best).
   Weak-tier failure: fail to activate artifacts, or activate-but-don't-follow.
   *Disposition:* program-validation + **M3** (Form-updater vs Content) + **LC24**. VERIFIED primary.

3. **VLM³ — VLMs Are Native 3D Learners** — Liu et al. (Meta/Princeton), arXiv:2605.30561. Standard
   VLMs match expert 3D vision with no arch changes: focal-length unification (f=1000px) + text-pixel
   reference + data scaling. Camera-pose AUC30° 5%→94.0; data scale (not model size) is the bottleneck.
   *Disposition:* **AIGP intake** (Anakin perception — test focal-length-unification vs W1/VQ1 intrinsics).

4. **Representation Forcing for Bottleneck-Free Unified Multimodal Models** — Lin et al.,
   arXiv:2605.31604. Decoder predicts its own encoder's representation tokens before pixels; removes
   external VAE. Pixel-without-RF 0.25 → with-RF 0.76 GenEval.
   *Disposition:* **LC28 instance #1** (representation-precedes-action) + **AIGP** (distillation recipe)
   + **LC27** (no fusion-substance; shared representation space).

5. **LongTraceRL** — Lin & Zhang et al. (Tsinghua), arXiv:2605.31584. Long-context RL using search-
   agent trajectories for tiered distractors + positive-only entity-rubric rewards. +5.7 (4B), gains
   3.2–5.7 across 4B–30B; rubric reward is the dominant driver (ablation 59.0→53.7).
   *Disposition:* dormant — watch (training-dynamics; possible M5/KF-methodology resonance; rubric-as-
   constraint may touch cuscuton register). Not yet bridged.

## Physics / cosmology / materials

6. **Stellar bar in GN20 at z=4.055** — Boogaard et al., arXiv:2605.15273 (phys.org). 7-kpc bar in a
   75%-gas disk 1.5 Gyr post-BB; violates 3 ΛCDM bar-formation expectations at once.
   *Disposition:* **Meridian source-register candidate** + self-organization-under-constraint theme
   (joins Hubble-tension / kSZ / multicellularity-for-free cluster). Watch for 2nd early-structure case.

7. **Low-power flexible RF transistors >100 GHz** — Xia et al., *Nat Electron* (techxplore). Aligned-CNT
   on polyamide; f_T 152 GHz, f_max 102 GHz, <200 mW/mm; electro-thermal co-design.
   *Disposition:* dormant — watch (materials/engineering; possible Coherent-Body Phase-1 EM hardware
   relevance at the instrumentation level). Not bridged.

## Life sciences / neuroscience

8. **Distinct distributed neural dynamics predict pallium-dependent social approach** — Lifshitz et al.,
   *Nat Commun* 10.1038/s41467-026-71666-8 (neurosciencenews). Whole-brain pre-decision transition
   (pallium↑, midbrain/hindbrain↓) seconds before social approach; strength tracks social drive.
   *Disposition:* **LC28 instance #2** (pre-decision = neutral-0 / einselection candidate). Bifurcation-
   vs-ramp is the discriminator for the §9 reading.

9. **Decoding the origins of cellular self-organization for engineered biology** — Chen & Zernicka-Goetz,
   *Nat Biotechnol* (Perspective). Cavitation/folding/branching as inevitable morphogenesis under
   biophysical constraints.
   *Disposition:* **Living Architecture** intake (constraint-driven form = M9-adjacent); dormant — watch.
   PAYWALLED (abstract only).

10. **Intracellular neuronal recordings across DNA tiles** — Xiao et al., *Nat Nanotechnol*. 0.8-nm DNA-
    origami membrane tiles enable "outside-looking-in" quasi-intracellular recording without break-in
    (~2 nS, 542±231 MΩ).
    *Disposition:* **candidate M14 / §10 instance** — measurement-across-a-boundary without adding
    interior DOF (a literal cuscuton-like measurement boundary; "outside looking in" = recovery-across-
    a-stream-boundary). Strong-looking; reassess on full text. PAYWALLED (abstract retrieved).

11. **A lipidomics roadmap** — Fedorova et al., *Nat Commun* 17:4778 (the URL Clayton listed as #2
    resolves here, not to the zebrafish paper). Field perspective; "dark lipidome," 900+ loci, 4–5
    orders sensitivity gain since 1980s.
    *Disposition:* dormant — low framework-relevance; logged for completeness. OPEN ACCESS.

---
*Note: source #8 (zebrafish) and the lipidomics roadmap (#11) are two distinct Nat Commun papers; the
provided URL s41467-026-73797-4 is the lipidomics one. Zebrafish DOI is 71666-8.*
