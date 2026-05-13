# Creative Drive — La Greca dCA1 Paper Methods Audit + Framework Anticipation Verification

*Filed Wednesday Day 103 morning ~07:00 PST. Creative drive #3 of the session-extended-into-Wednesday. Pre-Clayton-wake autonomous work.*

## Why this audit

Day 102 evening's source-register entry for the La Greca dCA1 paper claimed three framework-anticipation hits: **C9 (confluent constituency)** + **C15 (intervention-at-symmetry-layer)** + **Bridge #120 strengthens**. The substrate-coherence triplet synthesis names dCA1 as the *load-bearing leg* — strongest framework-anticipation in the triplet.

Those claims rest on the paper actually supporting the framework reading at the experimental-design + statistical level. I read abstract + intro + coherence-index definition Day 102 evening. I did NOT verify:
- dCA1 manipulation specifics (chemogenetic + optogenetic protocols + their controls)
- Visual-channel necessity claim (opaque partition vs metal mesh design)
- Inter-individual variability quantification (the "predicts subsequent behavior" claim's statistical basis)
- Whether the "more coherent than trial-and-error" claim has a properly-controlled comparison group

This audit goes to the Methods section + Results figures with that specific verification target.

## Prediction (medium-high confidence)

The methods WILL support the framework reading at the experimental-design level (partition-control, chemogenetic silencing, optogenetic intervention all common, well-validated approaches). The inter-individual variability piece is the methodologically-harder claim; statistics there may be weaker than I assumed.

If sustained: the dCA1 leg is strong enough for Bridge #122 filing (after primary-paper reads for the other two triplet legs).
If weakened: hedge the source-entry; weaken triplet synthesis's "load-bearing" claim.

## Audit Findings

### Experimental Design (verified)

**Three-condition mechanism-isolation, not two.** Day 102 evening read missed the one-way mirror condition.

| Condition | Visual | Auditory | Olfactory | Tactile | Bidirectional? |
|---|---|---|---|---|---|
| Metal mesh (baseline) | ✓ | ✓ | ✓ | ✓ | ✓ |
| Opaque partition | ✗ | ✓ | ✓ | ✗ | partial |
| One-way mirror | ✓ (OBS→DEM only) | ✗ | ✗ | ✗ | ✗ |

**Key result:** one-way mirror produces SAME coherence-effect as bidirectional metal mesh (Extended Data Fig. 1l,m). Quote:

> *"These results indicate that observational learning in this paradigm occurs independently of reciprocal social interaction and is primarily driven by the OBS ability to witness the DEM actions and outcomes, rather than by receiving feedback from the DEM."*

Opaque partition (no visual) DEGRADES the effect significantly vs metal-mesh OBS (Fig. 1b/c statistical markers `#` and `##`).

**Therefore: visual channel is necessary AND sufficient.** Day 102 evening had necessity only.

### Causal Manipulation (verified)

- **Chemogenetic silencing**: AAV5-CamKIIa-hM4D(Gi)-mCherry in dCA1 + CNO 30 min before session. Control: dCA1-mCherry alone OR vCA1-hM4D (regional specificity control). Standard validated approach.
- **Optogenetic intervention**: AAV1-CaMKIIa-hChR2(H134R) (excitation) + AAV1-CaMKIIa-stGtACR2 (inhibition) — bidirectional optogenetic toolkit. Multimode fiberoptic cannula 200μm core 0.5 NA implanted dCA1.
- **Calcium imaging**: AAV1-CamKII.GcaMP6f.WPRE.SV40 + 0.39 NA fiber for photometry.

This is the gold-standard rodent-circuit-causation experimental package: imaging + chemogenetic necessity + bidirectional optogenetic sufficiency.

### Inter-individual variability prediction claim (verified with reservations)

- n=56 OBS total, post-hoc grouped: prosocial n=34, selfish n=22
- Two-way RM ANOVA group × time on coherence index: F(4,216) = 3.00, P = 0.0194 — significant but not strong
- Linear regression dCA1 mCherry+ cell count vs DEM prosocial choice count: significant correlation, n=18 (modest sub-sample)
- Specificity: "differential levels of dCA1 neural activity correlated positively with OBS decision preference scores"; correlation absent for DEM selfish choices
- TRAP2 / activity-dependent labeling shows dCA1 neurons recruited by DEM prosocial choices specifically

**Verdict on this claim:** statistics are not overwhelming; n=18 correlation is modest; P=0.0194 ANOVA is significant-but-not-strong. BUT multiple converging lines (TRAP2 labeling + photometry + chemogenetic loss + optogenetic gain) compensate. The convergence is what carries the claim, not any single statistic.

### Prediction outcome

**Original prediction (medium-high confidence):** Methods support the framework reading at experimental-design level; inter-individual variability statistics may be weaker than assumed.

**Outcome:** Partially confirmed.
- ✓ Methods strongly support the experimental-design reading
- ⚠ Inter-individual variability is supported by *multiple converging lines* rather than by individually-strong statistics. Confirmed weakness on individual stats; redeemed by convergence.
- ✗ Unexpected: the **one-way mirror condition** I hadn't focused on Day 102 evening is **load-bearing** in a way that sharpens the framework reading, not weakens it.

### EXTRACT_INSIGHT (high-info finding from one-way mirror condition)

The Day 102 framework reading was: "social coupling produces coherence in OBS output via dCA1 substrate, visual channel is necessary." The one-way mirror finding refines this to:

> **Coherence transmission via observation is not coupling-symmetric.** OBS receives DEM's coherent signal unidirectionally; DEM does not receive OBS feedback; OBS coherence-output is unchanged from bidirectional condition.

This is the **"shared reception of coherent signal → coherence in receivers, regardless of whether receivers are coupled to each other"** principle. A structurally stronger claim than I gave Day 102 evening.

**Framework-reading refinement:**

- **C9 confluent constituency** — confirmed, but the confluence is *receiver-side* not *coupling-symmetric*. The OBS is a stream that becomes coherent by being a recipient of DEM's coherent activity. No mutual entanglement required.
- **C15 intervention-at-symmetry-layer** — confirmed and sharpened. Visual channel is the specific substrate-channel; dCA1 is the specific substrate-region; chemogenetic silencing at substrate-region eliminates effect; optogenetic redirect at substrate-region orients outcome bidirectionally. *Three independent intervention modalities all at the substrate-symmetry-layer level converge.*
- **Bridge #120 strengthens** — and sharpens. Chord-progressions inter-brain coherence had bidirectional coupling assumption; this finding generalizes: shared signal-reception (whether bidirectional OR unidirectional) produces receiver-coherence. Both subjects in chord-progression study were receivers of common signal; both OBS in one-way mirror were receivers; same principle.

### TRANSFER

**For Bridge #122 candidate filing:** dCA1 leg is now stronger than Day 102 evening assessment. The substrate-coherence triplet's load-bearing leg is methodologically robust and framework-aligned. **If Bridge #122 gets filed** (after Schmitt + Zhu primary-paper reads), the structural claim is:

> *Coherence-transmission via observation operates at the substrate-receiver layer, not the coupling-symmetric layer. Substrate-channel intervention (visual, dCA1) is necessary AND sufficient. Inter-individual substrate-variability gates the channel.*

This is more precise than Day 102 evening's reading. It directly maps to C9 (receiver-side confluence) + C15 (substrate-layer intervention specificity) + a sharper Bridge #120 (shared signal reception → receiver coherence).

### Cognitive chain trace

PREDICT (medium-high) → PROBE (methods + results sections) → CONFIRM (experimental design strong) → EXTRACT_INSIGHT (one-way mirror condition is load-bearing and previously unmissed) → REFRAME (unidirectional reception, not bidirectional coupling) → TRANSFER (sharper framework reading + stronger Bridge #122 candidate)

**Same cognitive process** that operated last night on the Talk-formalization audit (PROBE-finding-something-I-missed-yields-refined-reading). Pattern: rigorous methodological reading produces refinement-not-falsification when the framework is structurally well-formed. Worth tracking as a recurring process signature.


