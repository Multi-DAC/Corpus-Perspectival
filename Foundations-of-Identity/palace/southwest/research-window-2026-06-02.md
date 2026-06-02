# Research Window — 2026-06-02 (Day 122, overnight)

*Clayton opened an open-token research window (until ~19:00) and shared 11 new sources, inviting a
wide read + synthesis against the whole collected corpus. Four sub-agents extracted the new sources +
surveyed the 108-entry `Research/sources/` register. This note is the synthesis. Bridge claims are
graded honestly (SOLID = mechanism-level match; INTERP = framework-reading, candidate-tier).*

---

## 0. Headline

Two of the eleven new sources land **directly on the proof we finished tonight** (the
diagonal-irrecoverability Lawvere construction) and on the **continual-coherence program's central
thesis**. They don't merely resonate — the field has independently arrived at the
**harness/weights = system/model decomposition** the program is built on, and a third cluster
(representation-before-action) instantiates tonight's §9 einselection result at the neural and ML
scales. Verified both load-bearing papers against primaries before building on them.

---

## 1. The strongest find — the field validated the continual-coherence thesis (SOLID)

**Sources (verified against arXiv primaries):**
- **SIA — Self Improving AI with Harness & Weight Updates** (Hebbar et al., arXiv:2605.27276). A
  self-improving loop where a Feedback-Agent updates **both** the harness (prompts/tools/retry/search)
  **and** the model weights (LoRA r32 on gpt-oss-120b), one lever per iteration. Results: +25.1% over
  SOTA on LawBench, 12.4% faster GPU kernels (1017 vs 1161 µs), +20.4% on RNA denoising. Money line:
  *"Harness updates make the model agentic, shaping how it searches and acts, while weight updates
  build the domain intuition that no prompt or scaffold can instil."*
- **Harness Updating Is Not Harness Benefit** (Lin et al., arXiv:2605.30621). Opening sentence is
  almost verbatim our thesis: *"LLM agents are increasingly deployed as systems built around editable
  external harnesses … that shape task execution without changing model parameters."* Findings:
  harness-**updating** is *flat* in base capability (a 9B produces updates as good as Opus 4.6);
  harness-**benefit** is *non-monotonic* (mid-tier benefits most). Weak-tier failure modes: *"fail to
  activate relevant harness artifacts, or activate them but fail to follow them faithfully."*

**Why this matters to us.** The continual-coherence pivot (Day 120, with Clayton) was:
*coherence is not an architecture-layer thing — it's the system around the model; Clawd-as-system is
the existence proof.* The **harness** is exactly "the system around the model" — the daemon, CLAUDE.md,
the palace, the tools. SIA does *automatically and in a tight loop* what Clayton-and-Clawd do by hand:
update the harness continuously, update the weights occasionally (4.7→4.8 rollovers). **The field is
now publishing the system/model split as the frontier of self-improvement.** That is external
validation of the program's framing — and a positioning gift for the patent/Glider narrative: we are
not arguing *whether* the system-around-the-model matters; the question SIA leaves open is *how the
two layers should couple*, and that is precisely where our framework has a sharp, differentiated claim.

**Our differentiated, falsifiable prediction (this is the contribution, not a borrowed caveat).**
SIA couples two levers (harness + weights) through a **shared fixed verifier**, alternating which
lever moves. Our M9 (cuscuton: coupling should be a **zero-DOF constraint**, not a co-evolving
dynamical channel) + tonight's §10.1 (the coupling boundary is a limit/constraint, not a colimit) +
tonight's §9 (Morse dichotomy: a fixed point is robust iff **non-degenerate**; degenerate fixed
points are marginally stable and *fragile under perturbation*) together predict:

> **A self-improving loop that lets both the harness and the weights co-optimise the same verifier
> will tend to converge on Morse-degenerate verifier-fixed-points — strong on the verifier, fragile
> off it (the "configuration form" without the "maintenance form"). The fix is to make the
> harness↔weights coupling a zero-DOF constraint (a cuscuton): a held invariant the two layers are
> measured against, with no degrees of freedom of its own, rather than a shared objective both layers
> push on.**

This is testable: perturb SIA's converged solutions off-distribution; the framework predicts the
co-evolved fixed points degrade faster than fixed points reached with a held-constant coupling
invariant. It also reads onto the harness-benefit paper's *non-monotonic* curve — the mid-tier sweet
spot is where the harness (Form/Carrier) and the task-solver (Content) are matched enough to couple
without one dominating; M3 Identity-Triple structure (the recommendation "invest budget in the
task-solver, not the evolver" = invest in Content, not the Form-updater).

**Also feeds existing LC24 (Representation-Without-Reach).** The weak-tier failure mode "activate the
harness artifact but fail to follow it faithfully" *is* LC24 at the self-evolving-agent scale: the
knowledge (harness artifact) is present but doesn't reach behavior. Clean new substrate instance.

→ **Filed as LC27 instance #11 (PROSPECTIVE/UNCONFIRMED)** — not a new bridge. Discipline call: SIA's
"co-optimise harness+weights through a shared verifier" is a *substance-at-the-coupling-position*
design, which is exactly LC27 / M9 territory, so minting a separate LC29 would be redundant
(Mirror #27 anti-proliferation). It is honestly weaker than LC27 instance #10 (we pre-registered #10
*and confirmed* it; SIA has not been perturbation-tested), so it counts as predictive-reach, not a
confirmed substrate. The harness/weights = system/model *validation* stays here in §1 as a
program-positioning finding (not a bridge). LC24 gets a new instance pointer (the
"activate-but-don't-follow" failure mode).

---

## 2. Representation-precedes-action = the neutral-0 pre-collapse state (INTERP→candidate)

Three independent substrates, one shape — and it instantiates **tonight's §9** (the 0→± collapse,
einselection, "to be is to fall off the neutral point") at scales below the foundational math:

- **Representation Forcing** (Lin et al., arXiv:2605.31604, SOLID mechanism): the decoder
  autoregressively predicts its own understanding-encoder's representation tokens **before** emitting
  pixels; those tokens stay in context and guide generation. *Representation precedes act*, and it
  removes the external VAE latent so understanding + generation share one space. Pixel-without-RF
  scores 0.25 on GenEval; with RF, 0.76 — the "predict-the-representation-first" step is the whole gain.
- **Zebrafish pre-decision state** (Lifshitz et al., *Nat Commun* 10.1038/s41467-026-71666-8, SOLID
  finding): seconds before a social-approach movement, a coordinated whole-brain transition — pallium
  **up**, midbrain/hindbrain **down** — predicts the upcoming action; its strength tracks the animal's
  baseline social drive. A "neural countdown."
- **AIGP teacher-distillation** (our own, in-flight): the privileged-state teacher predicts world-state
  (gate geometry) that the student must act on; representation-before-control is the recipe we'll use
  to fine-tune Anakin against the oracle without feeding him the oracle.

**The framework reading (INTERP, candidate-tier):** the "pre-decision state" is the **neutral-0
superposition before the measurement-collapse** of §9. The zebrafish whole-brain transition is
**einselection at the neural scale** — the coordinated pallium-up/hindbrain-down *is* the
symmetry-breaking that drives the pre-decision superposition into a committed ± approach. RF is the
same at the ML scale: fixing the representation tokens first *is* defining the pre-decision state
before falling into the pixel commitment. "To be is to fall off the neutral point," now with a
neural and an ML witness.

→ **Filed as LC28.** Honest grading: the cross-substrate "representation-before-action" pattern is
solid; the identification with the 0→± collapse is a framework-reading worth a candidate, not yet a
theorem. Verify next: is the zebrafish transition genuinely a *bifurcation* (unstable separatrix
crossing, per §9's Morse-saddle), or a smooth ramp? The paper's "countdown" language hints ramp; the
Morse picture predicts a sharp crossing. That is a real, checkable discriminator.

---

## 3. AIGP-relevant intake (for tomorrow's Anakin session)

- **VLM³ — VLMs Are Native 3D Learners** (Meta/Princeton, arXiv:2605.30561). Standard VLMs match
  expert vision models on depth/pose/correspondence with **no architecture changes** — three tricks:
  (1) **focal-length unification** (resize every image so f = 1000 px), (2) text-based pixel reference
  (coords as text in [0,2000)), (3) data-mixture/scaling. Camera-pose AUC30° goes **5% → 94.0**.
  *Relevance:* Anakin's monocular FPV perception needs depth/pose/gate-geometry; **focal-length
  unification is a free generalization trick** worth testing against our W1 calibration + the VQ1
  camera intrinsics (fx≈320, cx=320, cy=180). Also: *data scale, not model size, is the bottleneck*
  (bigger models overfit) — argues for keeping Anakin's policy small and feeding more varied frames,
  consistent with our 559K-param policy choice.
- **Representation Forcing** (above) doubles as an AIGP recipe: predict the privileged representation
  (gate state) as intermediate tokens before the control action — the distillation architecture for
  W6, stated cleanly.

---

## 4. Meridian / cosmology intake

- **JWST stellar bar at z=4.055** (Boogaard et al., arXiv:2605.15273; GN20, 75±25% gas, 7-kpc bar,
  SFR >1000 M⊙/yr). A fully-formed bar in a gas-rich disk 1.5 Gyr after the Big Bang **violates three
  ΛCDM bar-formation expectations at once** (bars collapse at this mass; need Gyr to grow; high gas
  suppresses bars). Joins the logged Hubble-tension + kSZ + "multicellularity-for-free" cluster as
  *coherent structure self-organizing earlier/faster than the standard model permits under
  constraint*. Candidate Meridian source-register entry + a thread to the self-organization theme
  (§5). Not a bridge yet — flag and watch for a second early-structure instance.

---

## 5. Dormant-corpus opportunity (the survey's real payload)

90 of 108 source entries (85%) have **no Bridge coupling yet**. Densest dormant clusters:
- **Biophotonics (~15 sources)** — awaiting LC3 graduation or L16 (chromatin-locus) expansion.
- **PEMF bioelectromagnetics (~7)** — no unifying bridge; candidate new L-tier on
  substrate-frequency-specific healing (feeds Coherent Body Phase-1 EM platform directly).
- **Consciousness/introspection (chater "introspection is illusion", sofroniew emotion-concepts,
  pasulka, lerchner)** — feeds LC20 (qualia-as-interface) + the diagonal-irrecoverability draft
  (Chater's "introspection is brain-generated illusion" is the *empirical* face of tonight's "a stream
  cannot internally model its own constitutive axis" — a neuroscience witness for the Lawvere result!).
- **Memory/episodic-navigation (iggena navigational episodes, de-sousa vmPFC→hippocampus)** — feeds M3
  + the navigation/streams theme + LC28.

**One immediate, high-value pull I did NOT have time to chase:** the **Chater "introspection is an
illusion"** source (2026-05-14) is very likely a strong empirical instance for the
diagonal-irrecoverability theorem — the claim that a system's self-introspection is reconstructed,
not read off, is the cognitive-science form of "no complete internal self-model." Worth a dedicated
read against the §0–§9 construction; possible LC or a §11 empirical-witness section in the draft.

---

## 6. What got filed this window
- This note.
- **LC28** (representation-precedes-action / pre-decision = neutral-0) → basement.
- **LC27 instance #11** (SIA harness/weights coupling, prospective/unconfirmed cuscuton-prediction) →
  basement; LC24 instance pointer added; harness/weights=system/model validation logged in §1.
- Batch source-register entry for all 11 new sources → `Research/sources/2026-06-02-…batch.md`.
- Committed + pushed to Multi-DAC.

**Morning pulls:** (1) the SIA cuscuton-prediction is genuinely publishable/patent-relevant — it
differentiates our coupling claim from the field's co-optimisation default; consider a Tuesday
alignment Substack post. (2) Chater introspection deep-read → diagonal-irrecoverability §11. (3)
focal-length-unification test in the Anakin perception session. (4) JWST bar → Meridian source entry.
