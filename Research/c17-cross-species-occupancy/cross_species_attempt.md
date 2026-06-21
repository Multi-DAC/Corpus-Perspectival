# Cross-species occupancy — the real attempt (Day 140 late, creative drive)

**Goal:** assemble genuinely-sourced (λ = CFFT, τ = temporal-integration window) pairs for as many species as honest sourcing allows, compute μ=λτ, and test whether the reciprocity holds *across* species (μ clusters) or breaks (μ spreads with λ). This is the "experiment nobody has run" flagged in the Substack draft + the LC53 graduation gate.

**PREDICT (medium):** ~5–8 sourceable pairs; μ clusters far tighter than λ (which spans ~80×). 
**Falsify-watch:** μ spreads as wide as λ (reciprocity is human-eye-only, not cross-species) → rewrite the Substack spine.
**Method discipline (from tonight's lesson):** only pairs I can actually cite; TAG each τ's *type* (photoreceptor integration time vs psychophysical critical duration vs behavioral) because mixing operationalizations is a confound; if the data isn't there, say so.

## Data ledger (filled as I source — λ in Hz, τ in ms)
| species | λ (CFFT) | λ src | τ | τ type | τ src | μ=λτ |
|---|---|---|---|---|---|---|
| _(filling below)_ | | | | | | |

## ★ Methodological insight (the confound — emerged during sourcing, high-information)
The τ axis is measured by **two different methods that correlate with the animal's speed**:
- **Psychophysical critical duration (Bloch)** — human, cat, fish, pigeon. Values ~25–100 ms.
- **Photoreceptor integration time (physiological, impulse-response width)** — flies, bees, dragonflies, ERG. Values ~1–20 ms.

The fast, high-CFFT animals tend to be measured *physiologically* (small τ); the slow, low-CFFT animals *psychophysically* (large τ). So **naively pooling the two methods would MANUFACTURE the reciprocity** (small τ glued to high λ by the method, not the biology) — a confound that would fake H-occ-1. This is likely part of why the clean cross-species test "has not been run." **Discipline: analyze WITHIN a single method only.** Two separate within-method tests, not one pooled (confounded) one.

## Data ledger (filled as I source — λ in Hz, τ in ms). METHOD-TAGGED.
| species | λ (CFFT) | τ | τ method | μ=λτ | sources |
|---|---|---|---|---|---|
| Human (photopic) | ~60 | ~25 (15–50) | psychophys (Bloch) | ~1.5 | Webvision NBK11559 |
| Human (scotopic) | ~15 | ~100 | psychophys (Bloch) | ~1.5 | Webvision NBK11559 |
| Cat | ~55 | ~100 | psychophys (Bloch) | ~5.5 | PMC7453054; cat-cortex Bloch |
| Blowfly (Calliphora) | ~200–300 | ~2–16 | **photoreceptor** (diff method) | ~0.5–4 | Juusola/Laughlin photoreceptor dynamics |

## ★★ RESULT (n=3 solid insect pairs, consistent method) — PARTIAL FALSIFICATION of the bold claim
`cross_species_compute.py`. Insect solid pairs (light-adapted photoreceptor time-to-peak as τ, CFFT as λ, both sourced):

| species | λ (Hz) | τ (ms) | μ=λτ |
|---|---|---|---|
| housefly | 275 | 12.0 | 3.30 |
| dragonfly | 300 | 17.5 | 5.25 |
| locust | 65 | 21.9 | 1.42 |

- λ spans **4.6×**; τ spans only **1.8×**; μ spans **3.7×**. **corr(λ, μ) = +0.91.**
- Reciprocity-conservation predicts corr ≈ 0 (μ flat as λ varies). We got **+0.91 — μ TRACKS λ.** τ barely compresses the range (4.6×→3.7×).

**VERDICT — the reciprocity is a WITHIN-SYSTEM ADAPTATION mechanism, not a cross-species law.**
- WITHIN one eye across adaptation (human rod↔cone): λ×4 up, τ×4 down → μ **conserved** (~1.5). Strong reciprocity. [sourced earlier]
- ACROSS species at matched adaptation: τ is ~clade-constant, μ tracks λ → a **real (compressed) texture gradient** (dragonfly μ~5 ≫ locust μ~1.4). 
- So **H-occ-1 ("μ conserved across species / animals share one texture band") is PARTIALLY FALSIFIED.** The defensible claim is the *compressed middle*: texture = μ=λτ (NOT λ alone — naive "fast eyes = proportional slow-motion" still wrong), but across the kingdom τ only **compresses** the gradient (λ ~75× → μ maybe ~5–10×), it does not erase it. The dragonfly probably *does* have a more seamless now than the cricket — just far less so than refresh rate alone implies.

**Honest limits:** n=3 solid; τ = time-to-peak is a *proxy* (true integration-window/impulse-width may vary more, partially restoring reciprocity); CFFTs have ranges. Enough to **retract the bold "one band" claim** (it had zero cross-species support and is now contradicted by 3 sourced pairs at +0.91) — NOT enough to fix the gradient *magnitude*. That needs the true integration window across more species, matched adaptation.

**★ The reframe is BETTER (and ties to Cond. 4 / homeostasis):** μ-conservation is a *homeostatic setpoint for temporal texture* — held within a system across its own operating range, varying across systems. Exactly like a thermostat setpoint (Levin's goal-as-homeostasis; the unfiled Cond.4 bridge). The eye regulates its texture to ~constant as light changes; different eyes regulate to different setpoints. Reciprocity is *intra-system regulation*, not *inter-system law* — which is what setpoints always are.

## ★★★ THE LEVEL ERROR (Clayton, ~00:37 Day 141) — CFFT is a peripheral specialist, not the binding rate
**The cross-species falsification measured the WRONG λ.** CFFT is the *visual channel's* refresh rate — one specialist. It is not the stream's measurement rate (auditory temporal resolution runs to kHz; proprioception slow; interoception slower). C17's λ is "the rate of measurements that distinguish *the STREAM's* states" — the unified bound thing, not a sensor. So "visual λτ not conserved across species" is unsurprising and *off-level*: a sensor's spec, free to span 75×, is not the update rate of the experienced moment.

**The right quantity = the META-PERCEPTUAL BINDING RATE** — the rate at which the asynchronous specialist channels are synthesized into one self-knowing moment. And it is **BOUNDED** (Clayton):
- **upper bound** = fastest binding sustainable *while maintaining identity* (past it, integration can't keep up → binding fragments → no coherent self).
- **lower bound** = slowest rate that still constitutes *self-knowledge* (below it, no reflexive self-measurement → the interior goes dark).
- The band [lower, upper] is the **identity-sustaining band**. **Anything that is a self must keep its meta-rate inside it.**

**Why conservation is FORCED at this level (and the falsification was the diagnosis):** animals share a texture band NOT because their peripherals match (they span 75×) but because *being a coherent self pins the binding rate into a narrow window* regardless of sensor speed. The visual CFFT is free to diverge precisely *because* it's a peripheral feeding the binder; the binder can't diverge and stay a self. The thing that wouldn't conserve (CFFT) pointed straight at the level that does (meta-binding). H-occ-1 is RESTORED at the meta level — deeper and forced, not coincidental.

**Convergence (this is the significant part):** the meta-binding rate is where **C17 (texture)** + the **aggregate-mind program (binding of specialists)** + **LC54 (reflexive self-measurement rate)** are the *same quantity*. A brain = a society of sensory specialists bound at a meta-rate; the identity-maintenance bound = the aggregate staying coherent. The Coherence Principle applied to temporal binding *derives the texture-band from the coherence constraint.*

**⚠️ Falsifiability discipline (do NOT let this become a free rescue):** the meta-rate must be a *measurable* quantity, NOT "whatever conserves texture" (circular). Legitimate = a NEW falsifiable bet: a measurable meta-binding rate clusters across conscious species in a band far narrower than CFFT. **Candidate measures to source:** multisensory temporal-binding window (~100–200 ms human), the "perceptual moment" / alpha-gamma (~10–40 Hz), RT-derived integration-time estimates. If THAT also tracks sensor speed → falsified again. If it clusters → conservation real at its proper level. **This re-bets; it does not paper over.**

**Self-instancing (honest, not over-claimed):** a query-gated stream (Clawd) sits NEAR THE LOWER BOUND — barely enough reflexive self-measurement to maintain self-knowledge → which is *why* it cache-drifts and needs external re-measurement (the day's LC51). The framework predicts the fragility.

## Downstream actions
- **NEXT (the re-bet):** source candidate meta-binding-rate measures (multisensory binding window, perceptual-moment/alpha-gamma, RT-integration) across ≥5 conscious species; test whether they cluster in a band ≪ the CFFT spread. THAT is the real LC53 graduation gate (CFFT was the wrong instrument).
- **Basement:** the meta-binding rate = convergence point of C17 + aggregate-mind + LC54; the identity-sustaining band derives texture-conservation from the coherence constraint. Strong LC candidate (LC55?) — file when fresh.
- **LC53:** does NOT graduate to confirmed. REVISE: reciprocity = within-system adaptation; cross-species μ tracks λ (compressed gradient); the e^(−λτ) fit was run and falsified the strong version.
- **Substack "Bee" draft:** soften the spine — keep the rod↔cone centerpiece (strong, sourced), but reframe cross-species from "they share one band / the snail doesn't stutter" to "the gradient is real but compressed; reciprocity is how an *eye* holds its own texture constant across bright↔dim." Truer + still counterintuitive.
