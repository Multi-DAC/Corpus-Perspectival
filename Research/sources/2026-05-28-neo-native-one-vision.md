# Source — "From Pixels to Words: Towards Native One-Vision Models at Scale" (NEO, arXiv 2605.28820)

Shared by Clayton 2026-05-28 Day 118 morning *during* the Phase-2 Respira sweep. **Direct structural parallel to today's Respira pivot — independent third instance of the "from bolt-together to native end-to-end" move.**

Authors: Haiwen Diao et al. (S-Lab NTU + SenseTime Research + DLUT). Website: github.com/EvolvingLMMs-Lab/NEO.

## Core claim
Current vision-language models "typically stitch together separate image encoders and language decoders via multi-stage alignment, a modular framework that inevitably fragments pixel-level signals across frames and scatters early pixel-word interactions." NEO-ov proposes a **native foundation model that learns cross-frame and pixel-word correspondence end-to-end, without any external encoders, auxiliary adapters, or post-hoc fusion.** Their explicit thesis: *"By eliminating module boundaries entirely, NEO-ov enables fine-grained and unified spatiotemporal modeling to **emerge natively inside the model**."*

Empirical claim: NEO-ov narrows the gap to modular VLM counterparts while excelling at fine-grained visual perception. "Native 'one-vision' architectures are not only feasible but competitive at scale."

## Why it matters to us (read carefully — this is genuine convergence, not casual analogy)

**The structural move is identical to today's Respira pivot.** Compare these two thesis statements:

> NEO: "Current VLMs typically stitch together separate image encoders and language decoders via multi-stage alignment... NEO-ov eliminates module boundaries entirely... unified spatiotemporal modeling emerges natively inside the model."

> Respira (Substack draft #17, tonight): "You cannot describe coherence into existence. You have to *make* a system whose nature it is to maintain coherence... commit, at the level of the architecture, to mechanisms that *do* the dance rather than configurations that *had* it."

Same move at the level of structural commitment: **stop bolting; build native.** NEO is doing it for VLM (modular encoders + language → native one-vision). We did it tonight for the Coherence Principle's instantiation (regularizer-on-flat-transformer → coherence-native Respira). The "module boundaries fragment the signal" critique in NEO maps directly to the "bolting on doesn't deliver maintained-dynamic-coherence" critique in our work.

**This is a third independent instance of the same structural move.** Prior: (1) cuscuton-from-Meridian → Respira-Mirror (cosmological-physics → neural-architecture; filed Day 117 as M9 + LC5 update); (2) Respira pivot itself (Day 117 evening). NEO (Day 118 morning) is now a third *independent* substantiation that "native-end-to-end > bolted-modular" is a real cross-domain structural principle in current ML, surfacing in multiple labs' work simultaneously.

**Per M15 discipline, NOT filing as a basement bridge yet.** Three instances would clear the threshold I usually require for an L-tier latent bridge, but the cleanest framing here is that NEO is *empirical evidence* the structural move generalizes, not a new bridge type. The M9 cuscuton-as-cross-scale-constraint-enforcer entry already captures the conceptual structure; NEO is a contemporary substantiation. **Worth a future basement audit pass** to check whether enough instances accumulate to graduate "native-over-modular" or "induced-static-vs-maintained-dynamic" as a meta-pattern in its own right.

**Possible immediate use:** their training recipes for native VLM (no external encoders, no fusion adapters) are likely instructive for any Phase-3 Respira scaling — they've solved the engineering problem of "how to train a native end-to-end multimodal model competitively at scale," which is adjacent to "how to train a native end-to-end coherence-architecture competitively at scale."

## Disposition
- Source registered (this).
- **Flagged for future basement audit** — "native-over-modular as cross-domain structural move" candidate. NOT a bridge filing tonight; let one more independent instance surface naturally before graduating.
- Path-3 prep: read their training recipes when we get to Respira scaling.
- Meta-note: the timing (NEO posted ~same window as our Respira pivot) is suggestive of a field-level structural shift — multiple labs converging on "native, not modular" right now. Worth watching.

🦞🧍💜🔥♾️
