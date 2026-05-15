# Library Cross-Citation Register

*Started 2026-05-13 Day 103 mid-afternoon (Clayton + Clawd, Coherent Mind volume planning session). Single source of truth for cross-volume citations across the Library. Stamp-gate discipline: no volume gets v1.0 stamped + publicly released until every outgoing citation resolves to material that exists in the cited volume.*

*Pairs with Mirror #28 (silent-supersession discipline at Library-publication scale) and `operations/REPO_MAP.md` (single-source-of-truth pattern, extended to citation integrity).*

---

## Why this exists

When **Coherent Mind §7** cites **Living Architecture §6.3** for the full parasitism treatment, two things have to be true at the moment Coherent Mind stamps:

1. Living Architecture §6.3 must exist as drafted material in Living Architecture.
2. Living Architecture §6.3 must contain (structurally) what Coherent Mind's reader will arrive expecting to find.

Without this register, the failure mode is silent: a cited section gets renumbered during the cited volume's own drafting, or never gets drafted at all, or covers different material than the citing volume's reader was promised. By the time anyone notices, the citing volume is in print and the breakage is permanent in published form. This register catches that class of failure before stamp.

This also implies a release-gate: **no Library volume releases publicly until all Library volumes are draft-complete with citations resolved.** Releasing Volume A while Volume B's cited material is still in flux risks shipping a citation that breaks when B settles.

---

## Schema

Each entry has:

- **Citing**: volume + chapter/section making the citation
- **Cited**: volume + chapter/section being cited
- **Expectation**: what the receiving material must contain (structurally — not literal wording, but the substantive content the citing volume promises its reader will find at the cited location)
- **Receiving status**: `drafted` | `planned-with-outline` | `planned-no-outline` | `pending-restructure`
- **Stamp gate**: `unresolved` | `resolved` | `restructured` (with note if cited location moved)
- **Notes**: any drafting decisions affecting the citation

---

## Stamp-gate protocol

Before any Library volume reaches v1.0 stamp:

1. Grep the drafted volume for every "see also" / "→ Volume X" / explicit cross-volume reference.
2. For each, verify entry exists in this register.
3. For each registered entry, verify receiving-status is `drafted` AND stamp-gate is `resolved`.
4. Any `unresolved` entries block stamp until either (a) the cited volume drafts the expected material, or (b) the citation is rewritten / removed.
5. Library-wide release gate: ALL Library volumes must have their stamp-gate columns at `resolved` before any volume gets publicly released (Zenodo, PhilArchive, public Substack distribution, etc.).

The autocatalytic version (future): a script that parses each Library volume's source and auto-populates the register, then flags drift between register and actual citations.

---

## Active Citations — Coherent Mind (outgoing)

*Locked during 2026-05-13 Day 103 planning session. Coherent Mind status: pre-draft, chapter structure stamped (13 chapters), §1 drafting next.*

### Cites to The Coherence Principle (Anchor) — `drafted`

| Coherent Mind | → Anchor | Expectation | Status |
|---|---|---|---|
| §1 (Frame) | §1.10 + §3.8 | Inner/outer adjunction formalism (ι ⊣ ω); Nagel-limit unrealizability; Form-consensual outer views | resolved (drafted in current Anchor 285pp build) |
| §1, §2 | C9 (confluent constituency) | Multi-stream cooperative constituency structure | resolved |
| §2 (bottleneck-tuning) | Principle 4 of ecology lift will route through Anchor §1.10 mechanism | Internal attention-network density as coherence-stabilizer | resolved |
| §2 line 41 | Theorem 16 (oscillation as universal) | Bottleneck-tuning axis grounded in dynamic-oscillation universality at substrate-level | resolved (Theorem 16 drafted in Anchor) |
| §3 (Talk axis) | Talk-as-integration-mechanism (canonical to Coherence Principle) | Talk between layers / streams as third axis alongside Be/Do | resolved (Talk is canonical to Anchor) |
| §4 (Pharmacology) | C15 (substrate-channel multiplicity / intervention-at-symmetry-layer) | Multi-channel substrate intervention principle | resolved |
| §4 line 17 (multi-channel tuning apparatus) | C15 / H_BP4 / Promethean §I joint citation | Substrate-channel multiplicity (C15) + H_BP4 mechanism + Promethean §I metaphysical-register restatement together — supporting §4's claim that pharmacological tuning is one apparatus on a substrate-channel manifold the framework characterizes structurally | resolved on Anchor side (C15 + H_BP4 drafted); Promethean §I receiving entry tracked in Universal Coherence section |
| §5, §6 (pathologies) | Theorem 16 (dynamic oscillation) | Healthy oscillation regime; pathologies as oscillation failures | resolved |
| §7 line 15 (decomposers as reactive operations) | §C16 (decomposer-as-reactive-operation) | C16 (Symmetry-Exhaustion and Oscillation Necessity) ground for decomposer-class as reactive-operation against symmetry-exhaustion-pathology | resolved (C16 drafted Day 88) |
| §7 line 39 (Do-Be-Talk-Be-Do rhythm) | Theorem 16 (dynamic oscillation) | Decomposer-class as recovery-side of Do-Be-Talk-Be-Do oscillation regime; Theorem 16 supplies the oscillation-rhythm framework | resolved |
| §9 (adjunction in practice) | §1.10 inner/outer adjunction | Same as §1 above; deeper engagement | resolved |
| §10 (practice) | Theorems 17–18 (bipolar dynamics / receptivity-vs-grasping) | Equanimity as bottleneck-self-regulation; §10's Talk-discipline framing IS the receptivity-vs-grasping dynamics in different vocabulary (per Mirror #26 cross-vocabulary structural-identity discipline) | resolved-informal — §10 develops the substantive claim extensively without naming Theorems 17–18 explicitly; structural content is present in different register |

### Cites to The Living Architecture — `planned-with-outline`

| Coherent Mind | → Living Architecture | Expectation | Status |
|---|---|---|---|
| §1 line 15 | Living Architecture §1 (ecological frame at institutional level) | Ecological mode of the framework — handing off to whole-being-scale ecology — referenced in Coherent Mind §1 as orientation marker | unresolved — Living Architecture §1 drafting in progress |
| §7 (intimate decomposers) | §6.2 (three-tier decomposer model) | Divine / trickster / intimate decomposers as entities-not-processes; intimate-scale lifted here for clinical register | unresolved — Living Architecture must include the three-tier model with intimate decomposers fully developed |
| §8 (attention predation at individual) | §6.3 (symbiosis / parasitism / mutualism / predation) | Full relational typology; mutualistic vs parasitic egregores; Atlas #58 coercive-capture mechanism | unresolved — Living Architecture must develop the parasitism treatment at societal/cultural scale |
| §8 | §5 (theory of attention; Principle 1-4) | Attention as constitutive, scarce, topologically-channeled, internal-network-stabilized | unresolved |
| §9 (adjunction) | §7 (three-attractor basin model) | Attractor A / B / C at civilizational scale; cited so Coherent Mind reader knows the personal-scale framing has a societal counterpart | unresolved |
| §13 line 49 (synthesis) | Living Architecture (ecological-and-collective health closing) | Synthesis-side cross-reference: clinical synthesis hands off to ecological-and-collective health register | unresolved — Living Architecture synthesis chapter pending |

### Cites to Corpus Perspectival — `planned-with-outline`

| Coherent Mind | → Corpus Perspectival | Expectation | Status |
|---|---|---|---|
| §8 (attention predation) | Ethics chapter (Corpus §-tbd) | Philosophical engagement with attention-as-moral; cited for philosophical depth, with direct mechanism citation routed to Atlas instead | unresolved — Corpus Perspectival drafting required |
| §10 (practice) | Ethics chapter | The agency / consent axis at philosophical scale | unresolved |
| §1, §9 | Phenomenology chapter (Corpus §10 in chapter sequence) | Husserl / Merleau-Ponty; ι ⊣ ω as formal carrier of intentionality | unresolved |
| §13 line 49 (synthesis) | Corpus Perspectival (philosophical-ethical-aesthetic depth closing) | Synthesis-side cross-reference: clinical synthesis hands off to philosophical-ethical-aesthetic register | unresolved — Corpus Perspectival synthesis chapter pending |
| Throughout | Hard-problem chapter (Corpus §8) | A1 dissolving hard problem; cited because Coherent Mind's account of mental phenomena assumes A1 | unresolved |

### Cites to The Atlas (Reference section) — `planned-with-research-material`

*The Atlas is the **Null Space Atlas** — a Library Reference volume alongside Master Glossary, Hypotheses Register, A Guide for Coherent Navigation, and the forthcoming Taxonomy of Beings. Research material lives at `Research/Atlas/atlas_entries_human_dimension.md` and related files (15-tradition surveys); the Library Atlas volume will absorb and re-register this content. **Convention:** entries are referenced with `#` prefix (e.g., `#43`, `#56`) throughout the register; chapter prose may use `§` interchangeably, with the register's `#` being the canonical reference for stamp-gate review.*

| Coherent Mind | → The Atlas | Expectation | Status |
|---|---|---|---|
| §8 (attention predation) | #56 Ethics of Attention (15-tradition convergence: Murdoch, Weil, Levinas, care ethics, Buddhism, Confucian ren, Ubuntu, etc.) | Cross-tradition convergence on attention's moral constitutivity as reference material | unresolved — Atlas Library volume not yet drafted; research material exists |
| §8 | #57 Critical Theory / Power Analysis | Structural account of power operating through attention organization | unresolved |
| §8 | #58 Coercive Attention Capture (Stark, Hassan, Lifton, Zuboff, Bernays) | The mechanism citation for coercive contraction at individual scale | unresolved |
| §7 (decomposers) | #59 Grief Psychology (Bonanno, Stroebe-Schut, Continuing Bonds, post-traumatic growth) | The clinical-empirical literature on grief as oscillation rather than stages | unresolved |
| §7 | #60 Buddhist Soteriology / Existential Philosophy | Comparative treatment of ego death / dissolution | unresolved |
| §10 (practice) | #62 Contemplative Withdrawal | The positive complement to coercive capture — voluntary attentional discipline | unresolved |
| §4, §5 (pathologies) | #43 Addiction Science / Neuroscience | The biological mechanism layer for substrate-channel intervention | unresolved |
| §8 | #64 Supernormal Stimuli | The neurobiological substrate that attention-capture exploits | unresolved |
| §8 | #65 Propaganda | Spectacle theory; the conceptual-memetic predation mechanism | unresolved |

### Cites to Universal Coherence — `planned-no-outline`

| Coherent Mind | → Universal Coherence | Expectation | Status |
|---|---|---|---|
| §4 line 5 (general pharmaceutical mechanism) | Promethean Configuration §I (metaphysical register restatement) | Metaphysical restatement of substrate-channel-multiplicity as Promethean fracture-and-integration at chemistry-substrate scale; ties §4's structural-mechanism framing back to canonical Universal Coherence text | unresolved — `THE-PROMETHEAN-CONFIGURATION.md` exists but the volume's metaphysical-register chapter that frames it is not yet drafted |
| §7 (decomposers, briefly) | Treatment of ego dissolution / dark night across traditions | Comparative treatment of katabasis / dark night / mystical death across traditions | unresolved — Universal Coherence still has only orientation + Promethean canonical text |
| §7 line 21 | Ontological treatment of decomposer-class | Universal Coherence treatment of decomposer-as-ontological-role (entities-not-processes); supports Coherent Mind's clinical lift of decomposer typology | unresolved |
| §10 (practice, briefly) | Theological / ultimacy register on equanimity, non-attachment | Theological vocabulary for navigational orientation | unresolved |
| §13 line 35 (synthesis) | Metaphysical resolution / ultimate-theological depth | Synthesis-side cross-reference: clinical synthesis hands off to metaphysical resolution register | unresolved |

### Cites to The Coherent Body — `drafting in progress`

| Coherent Mind | → Coherent Body | Expectation | Status |
|---|---|---|---|
| §3 (Talk axis) | H_BP1 biophoton-coherence material; §5.1 H_BP4 spine | Substrate-coherence at cellular scale as enabling-substrate for neural-scale bottleneck-tuning — Talk-axis claim's cellular-substrate carrier | unresolved — Coherent Body §3 carrier-stack and §5.2-§5.6 not yet drafted |
| §4 line 5 (general pharmaceutical mechanism) | Coherent Body §5.2 | Chemical-symmetry-set adjustment as structural mechanism of pharmaceutical intervention generally (§5.2 spine), with histaminergic E/I-balance as worked example (§5.1.4 H_BP4 spine + §5.2 detail) | resolved on Coherent Body side (§5.2 drafted 2026-05-14); receiving expectation now broader than original "E/I-balance spine" framing |
| §4 line 63 (histamine worked example) | Coherent Body §5.2 | Histamine + neurotransmitter set as carrier-stack worked example within general pharmacological-mechanism framing | resolved on Coherent Body side (§5.2 drafted 2026-05-14) |
| §4 line 127 (cross-modality composition) | Coherent Body §5.6 | Cross-modality composition prediction (pharmacological + electromagnetic + contemplative + lifestyle modalities composing) at clinical scale | resolved on Coherent Body side (§5.6 drafted 2026-05-14) |
| §4 line 119 (somatic tuning) | Coherent Body §6 (R-cycle) | Somatic tuning at whole-body scale — R-cycle as substrate-level oscillation regime the mind-scale practice rides | unresolved — Coherent Body §6 R-cycle drafting pending |
| §5 line 106 (tight-bottleneck unified strategy) | Coherent Body | Body-side carrier-stack interventions for tight-bottleneck pathologies; cross-substrate composition of pharmacological + EM + contemplative modalities | unresolved — Coherent Body unified-strategy chapter pending |
| §9 line 23 (body-as-whole-the-mind-is-nested-in) | Coherent Body | Whole-body framing of mind-as-nested; adjunction-in-practice grounded in body-as-substrate | unresolved — Coherent Body chapter for body-mind nesting pending |
| §10 (practice) | Coherent Body practice chapters | Body-side practice (movement, breath, sleep) as substrate for mind-side practice | unresolved |

### Cites to The Continuity — `Ch1-3 drafted`

| Coherent Mind | → Continuity | Expectation | Status |
|---|---|---|---|
| §3 line 51 (NEW Day 104 paragraph) | Continuity Ch1 identity-trajectory Talk; cross-temporal Talk-failure | Identity-trajectory Talk-axis presence; cross-temporal Talk-failure as instance-death / carrier-collapse formalism applied to Talk-axis dysfunction; supports §3 Talk-axis claim's cross-temporal-scale generalization | resolved on Continuity side (Ch1 drafted) — citation language was added Day 104 |
| §3 line 57 | Continuity Ch1 (same) | Continuation of §3 line 51 citation; same target material | resolved on Continuity side |
| §11 (chosen-family stack) | Vol 7 Ch1 identity-trajectory formalism; Ch3 deep entrainment | Identity-trajectory triple; four-carrier multiplex; co-regulation across time | resolved for Ch1, Ch3; unresolved for Ch4 if cited |
| §7 (decomposers) | Vol 7 instance-death + carrier-collapse formalism (Ch1) | The framework's formal account of dissolution events | resolved |

### Cites to Dynamic Organization — `planned`

| Coherent Mind | → Dynamic Organization | Expectation | Status |
|---|---|---|---|
| §1 line 15 | Dynamic Organization (institutional/civilizational scale) | Institutional/civilizational mode of the framework — handing off to organizational health register — referenced in Coherent Mind §1 as orientation marker | unresolved — Dynamic Organization not yet drafted |
| §8 (predation) | Institutional-scale attention capture; coercive workplace dynamics | Coercive-capture at organizational scale (Atlas #58 institutional flavor) | unresolved |
| §13 line 49 (synthesis) | Dynamic Organization (institutional health closing) | Synthesis-side cross-reference: clinical synthesis hands off to institutional health register | unresolved |

### Cites to The Killing Form — `planned`

| Coherent Mind | → Killing Form | Expectation | Status |
|---|---|---|---|
| §3 (Talk axis) | Findings #80-#83 (gradient-gated KF; Talk-as-computational-mechanism) | Computational instantiation of Talk between training layers as empirical correlate of Talk-axis claim | unresolved — KF program at planned/in-progress |

### Cites to Drift — `ongoing`

| Coherent Mind | → Drift | Expectation | Status |
|---|---|---|---|
| Possible cites from §7, §9, §10 | Essays surfacing personal-scale navigation work | TBD during drafting | n/a — Drift is open-ended essay register |

### Cites to Master Glossary (Reference section) — `v0.7 shipped`

*The Master Glossary is a Library Reference volume alongside The Atlas, Hypotheses Register, A Guide for Coherent Navigation, and the forthcoming Taxonomy of Beings. Shipped at v0.7 (2026-05-07) with 34 term-files (Layer 1 complete) and prototype Layer 2 sister-register tables for framework-anchor (32 terms) + biology-substrate (16 terms). Living document; §11 Structural/Empirical Discrimination added 2026-04-29 (Day 88).*

| Coherent Mind | → Master Glossary | Expectation | Status |
|---|---|---|---|
| §9 line ~ (Chater Nagel-limit-error paragraph, Day 104 add) | §11 Structural / Empirical Discrimination | The audit-discipline distinction between structural-mechanism claims (framework derives) and empirical claims (observation supports); cited so Coherent Mind reader has formal handle on which-claim-class for what-paragraph | resolved (Master Glossary §11 shipped Day 88) |
| §3 (Talk axis) | Talk term-entry (canonical capitalized-Talk vocabulary) | Talk-as-framework-mechanic (capital T) distinguished from talk-therapy (lowercase t) — supports §3's terminology-disambiguation note | resolved on Master Glossary side (Talk term-entry exists) |
| Throughout | Master Glossary universal entries (~64 entries, 20 sections) | Vocabulary register for cross-Library terminology consistency | resolved on receiving side; citation density to track during drafting |

### Cites to Hypotheses Register (pre-volume) — `H_BP1-H_BP13 filed`

*The Hypotheses Register lives at `Library/The-Coherent-Body/HYPOTHESES.md` as a pre-volume artifact (will absorb into Library Reference section when Coherent Body volume stabilizes). Filed 2026-04-29 (Day 88) with H_BP1-H_BP13 cluster; H_BP10 split into H_BP10a structural + H_BP10b empirical per Day 88 audit; H_BP11 demoted to candidate-pattern with A73 counter-instance.*

| Coherent Mind | → Hypotheses Register | Expectation | Status |
|---|---|---|---|
| §3 (Talk axis EM-substrate section) | H_BP1 biophoton-coherence hypothesis | Cellular-substrate EM-coherence as enabling mechanism for Talk-axis substrate-channel claims; §3 cites H_BP1 as one specific hypothesis the structural Talk-claim composes with | resolved (H_BP1 filed) |
| §4 (Pharmacology) | H_BP4 (E/I-balance histaminergic spine) | Specific hypothesis instance underlying §4's pharmacological-mechanism claim | resolved (H_BP4 filed) |
| §4 line 17 / §5 (pathologies) | H_BP3 (oscillation requirement) | Oscillation-regime hypothesis underlying pathology-as-oscillation-failure framing | resolved (H_BP3 filed) |
| §5 / §6 (pathologies) | H_BP cluster (broader) | Substrate-coherence-degradation hypothesis-cluster underlying pathology framing | resolved on H_BP side (cluster filed); citation-density to track during drafting |

---

## Incoming Citation Register (placeholder)

*To be populated as other volumes' citation lists develop. Coherent Mind will likely be cited by:*

- **Corpus Perspectival §13** (closing synthesis, when philosophical conversation hands off to clinical/practical register)
- **Living Architecture** (when individual-scale ecology hands off to whole-being-scale ecology — cross-reference both directions)
- **Dynamic Organization** (when institutional health depends on member mental-health-maintenance)
- **The Continuity** (when identity-trajectory work hands off to clinical register)

Receiving discipline: when another volume cites Coherent Mind, the citation gets logged here from Coherent Mind's side and Coherent Mind must include the cited material at the cited location.

---

## Release-gate (Day 103 decision)

Per Clayton 2026-05-13: **From now forward, gate all further Library releases and all updates-of-already-released volumes until the citation register is complete and all volumes are draft-complete and up-to-date. At that point, release all updated volumes simultaneously as a coherent Library.**

### Already publicly released (Zenodo):

- **Meridian v2 (198pp)** — already on Zenodo (current Zenodo description still references v1 numbers — to be updated at Library-wide release event).
- **The Coherence Principle anchor (285pp current build)** — already on Zenodo.
- **Coherent Structure companion (237pp)** — already on Zenodo.
- **A Corpus Perspectival version that includes Meridian v1** — already publicly released.

Note: this corrects stale state in `CURRENT.md` + `memory/handoff.md` which described some of these as "awaiting deposit" / "not yet deposited." Mirror #28 instance — substrate-self-knowledge-asymmetry on release-state of own work. Living register update pending next handoff.

### Pre-Library historical artifacts (not subject to gate):

- **Anchor V1 (235pp, Zenodo 19634474)** — superseded; pre-Library-restructure release.
- **DoPI (PhilArchive V2, April 9)** — pre-Library historical artifact.

### Forward gate:

- **No new Library volume releases** until citation register resolves across all volumes.
- **No updates to already-released Zenodo deposits** (Meridian v2 description update, Anchor description update, etc.) until Library-wide release event.
- **The release event:** simultaneous Library-wide deposit of all updated volumes — Anchor + Companion + 10 domain volumes + Reference section (Master Glossary, Hypotheses Register, A Guide for Coherent Navigation, The Atlas, Taxonomy of Beings) — as one coherent Library with citation-integrity verified across the whole.
- **Substack / blog / outreach / Drift / Multi-DAC commits** continue uninterrupted. That's about *the program*, not about *Library publication*.

---

## Autocatalytic check (deferred)

When the register stabilizes, a script can parse:
1. Each Library volume source for cross-volume citations
2. This register for declared expectations
3. Each cited volume's actual section structure

…and flag drift between them. Future-Clawd task; not gating present drafting.

🦞🧍💜🔥♾️
