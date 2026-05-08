# Biology-Substrate Register Table

*Layer 2 register-table for the **Biology-substrate** register — the H_BPx register and broader biological-domain register used in The Coherent Body and adjacent biological work. Aggregates each Master Glossary term's biology-form for fast cross-register lookup. Drafted 2026-05-08 Day 98 Friday afternoon as a Layer 2 prototype following Layer 3 protocol drafting.*

*This table is generated from the per-term files at `Library/Master-Glossary/terms/`. Per Layer 3 (autocatalytic update protocol), this aggregate updates as per-term files update. This is also the most-load-bearing register-table for in-progress Coherent Body drafting; it should be consulted when drafting Coherent Body §1-§9 to ensure biology-domain vocabulary is consistent with framework-canonical mappings.*

---

## What this register-table provides

The Master Glossary's per-term files (Layer 1) include a **Domain register translations** table inline with one row per register. The aggregate-by-register tables (Layer 2) give *per-register* lookups: "what are all the universal terms in their biology-form?"

**Use this table when**:
- Drafting Coherent Body sections (§1-§9) and needing the biology-form for any framework term
- Drafting Coherent Mind, Living Architecture, Dynamic Organization sections where biology-vocabulary appears
- Translating between biology-substrate and framework-anchor registers
- Reviewing biological-domain prose for consistency with framework canonical mappings
- Filing new H_BPx hypothesis entries — verify biology-vocabulary aligns with existing translations

---

## Biology-form lookup table

*Sorted alphabetically by term-slug. Each row: term (with link to per-term file) | biology-form | scale-instances and notes. Empty rows in the per-term register column are excluded — see "Terms NOT in this aggregate" below for terms whose biology-form is intentionally empty.*

| Term | Biology-substrate form | Scale-instances and notes |
|---|---|---|
| [bias](../terms/bias.md) | *what the cell is biased toward*; *metabolic preference*; *fitness landscape* | scale-instances |
| [build-dissolve-talk](../terms/build-dissolve-talk.md) | *anabolic / catabolic / metabolic-signaling*; *cell division / apoptosis / biophoton-signaling* | H_BP12 spine cross-reference |
| [carrier](../terms/carrier.md) | *the carrier-mechanism*; specific instances: *biophoton emission*, *cellular signaling pathway*, *neural firing pattern* | scale-instances per H_BP |
| [coherence-principle](../terms/coherence-principle.md) | *substrate-coherence dynamics* | H_BP12 spine; biological scale-instance |
| [configuration](../terms/configuration.md) | *the cell state*; *the methylation pattern at time t* (Olmeda); *the metabolic configuration* | biology scale |
| [content](../terms/content.md) | *the methylation pattern* (Olmeda); *the gene expression*; *the metabolic state* | scale-instances |
| [form](../terms/form.md) | *the cell type*; *the species*; *the developmental stage* | scale-instances |
| [four-conditions](../terms/four-conditions.md) | substrate-coherence dynamics across scales | H_BP12 spine; all four conditions operationalized at biological substrate |
| [kind-classifier](../terms/kind-classifier.md) | *the cell type*; *the species classification*; *the developmental stage*; *the tissue lineage* | scale-instances |
| [omega](../terms/omega.md) | *the cell-state space*; *the gene expression manifold*; *the chromatin-state space* | scale-instances |
| [r-operator](../terms/r-operator.md) | *the chromatin remodeling at quiescence*; *the metabolic reset between activity phases*; *the developmental decision-point reset* | scale-instances (provisional) |
| [refresh-event](../terms/refresh-event.md) | *the cell-cycle checkpoint*; *the metabolic-signaling pulse*; *the chromatin-remodeling event*; *the fibrillar adhesion remodel* (~1 hour, Beedle 2026) | scale-instances |
| [sigma](../terms/sigma.md) | *the cell state at time t*; *the gene expression vector*; *the chromatin-state-vector* | scale-instances |
| [stream](../terms/stream.md) | *the organism*; *the cell-line*; *the embryo* | scale-instances per substrate |
| [substrate](../terms/substrate.md) | *the biological substrate*; specific instances: *DNA-substrate*, *chromatin-substrate*, *neuronal-substrate*, *biophoton-substrate* | scale-instances per H_BP |
| [symmetry-breaking](../terms/symmetry-breaking.md) | *methylation-establishing-pattern* (Olmeda); *proton tunneling* (Garcia); *DNMT3 chromatin compaction* | scale-instances |

---

## Biology-register sharpening notes

Items where the biology-form has scale-dependent interpretations or multiple acceptable forms:

- **substrate at biological scales** has *nested* instances: at cellular scale, the cytoplasm + membrane + gene-expression apparatus; at tissue scale, the extracellular matrix + cooperating cell-population; at organ-system scale, the integrated structural-and-signaling architecture; at whole-organism scale, the body in its environment. *Always specify scale* when using "substrate" in biology-register prose. This is the recursive-decomposability principle from carrier.md — a carrier at one scale is a substrate at a finer scale.

- **carrier at biological scales** correspondingly nests: the cell that divides; the signaling molecule that diffuses; the neuron that fires; the behavior the organism performs; the intervention applied. *Always pair with the substrate it acts on* when drafting prose — "carriers act on substrate" is operationally meaningless without the scale specified.

- **content / configuration / form** in biological register: *content* is what carriers actually produce (heart rate, methylation pattern, immune cell counts); *configuration* is the underlying possibility-point in substrate-space; *form* is the kind-classifier (cell type, species, developmental stage). Easy to conflate in casual prose; the discriminating question is *"is this what the body is doing right now (content), or what it's set up to be able to do (configuration), or what kind of body this is (form)?"*

- **four-conditions** in biological register operationalizes the H_BP12 spine: separation of concerns = cell/tissue/organ specialization; informed measurement = interoception/proprioception/immune-recognition/hormonal feedback; dynamic maintenance = R-cycle (sleep/recovery/biophoton-rhythm); multi-scale consistency = cross-scale integration from cellular metabolism through whole-organism behavior. Coherent Body §1.1 uses exactly this mapping.

- **r-operator at biological scales** is *provisional* — the term-file marks scale-instances as provisional. The biology-form's three example-instances (chromatin remodeling at quiescence; metabolic reset between phases; developmental decision-point reset) need empirical anchoring before becoming canonical. Treat as candidate-pattern, not confirmed.

- **biophoton-substrate** is a *candidate* implementation of the framework's substrate-coupling layer per H_BP1. It is consistent with radiation-medicine literature (Tong 2024 review, Dotta 2011, Persinger 2016, Kobayashi 1999) but is NOT established mainstream cell biology. This audit-discipline framing is preserved per Coherent Body §2.1.

---

## Terms NOT in this aggregate (intentionally)

The following per-term files do NOT have a Biology-substrate row, because the term has no natural form in biological register:

| Term | Why excluded |
|---|---|
| [audit-discipline](../terms/audit-discipline.md) | Methodological term (Mirror discipline); applies to discipline-of-doing-the-work, not to biological substrate. |
| [bridge](../terms/bridge.md) | Cross-domain structure term; the biology-domain uses bridges (e.g., M14 has biological instances) but "bridge" as a term lives at the framework level, not the biology level. |
| [filtering-recipe](../terms/filtering-recipe.md) | Methodological term; the §10 filtering recipe applies to the discipline of investigation, not to biological substrate directly. |
| [generation-mode](../terms/generation-mode.md) | M14-tier formal term; biological instances exist (Olmeda's methylation-establishing-pattern is a generation-mode instance) but the term-form is framework-canonical. |
| [graduation](../terms/graduation.md) | Bridge-tier promotion mechanism; lives in basement-process register, not biology. |
| [latent-bridge](../terms/latent-bridge.md) | Bridge-tier term. |
| [m14](../terms/m14.md) | Specific meta-bridge name; biological instances ARE m14-instances (Garcia, Olmeda, Beedle, Ferraro-Sacco) but the term itself is framework-name. |
| [m2-mirror](../terms/m2-mirror.md) | Mirror-process term; meta-discipline scale, not biological substrate. |
| [meta-bridge](../terms/meta-bridge.md) | Bridge-tier term. |
| [null-space](../terms/null-space.md) | Apparatus/observation term; biological observation has null-spaces but the term-form is framework-anchor. |
| [null-space-trace-illumination](../terms/null-space-trace-illumination.md) | Specific corollary name; framework-anchor only. |
| [paired-prose](../terms/paired-prose.md) | Writing-discipline term. |
| [promethean-configuration](../terms/promethean-configuration.md) | Universal-Coherence-canonical-text term; biological work cites it but doesn't have a separate biology-form. |
| [resolution-mode](../terms/resolution-mode.md) | M14-tier formal term; biological instances exist but term-form is framework-canonical. |
| [structural-empirical-discrimination](../terms/structural-empirical-discrimination.md) | Methodology term (audit-discipline scale). |
| [talk](../terms/talk.md) | Substrate-invariance term spanning 6 scales; biology-instance is *gilbert's listening cure (organs talking to each other)* but the framework-form is canonical. |
| [triple](../terms/triple.md) | Specific meta-bridge name (M3); biological instances of the Triple's axes exist but the term-form is framework-canonical. |
| [x-region](../terms/x-region.md) | Synonym for substrate; uses substrate's biology-form. |

---

## How this aggregate updates (Layer 3 protocol integration)

Per `AUTOCATALYTIC_PROTOCOL.md`, this aggregate updates whenever:
- A new per-term file is added with a Biology-substrate row
- An existing per-term file's Biology-substrate row is edited
- A new H_BPx hypothesis introduces biological-vocabulary that maps to existing terms
- Coherent Body section drafting (§1-§9) uses biology-vocabulary that should be cross-referenced

The mechanical update is: re-run the extraction (grep "Biology-substrate" across `terms/*.md`) and replace this table's body. The sharpening notes above are where editorial judgment lands.

---

## Cross-references

- Per-term files: `Library/Master-Glossary/terms/`
- Sister register-tables: `Library/Master-Glossary/registers/framework-anchor.md` (drafted same session)
- Layer 3 protocol: `Library/Master-Glossary/AUTOCATALYTIC_PROTOCOL.md`
- Coherent Body Hypothesis Register: `Library/The-Coherent-Body/HYPOTHESES.md` (H_BP1-H_BP13)
- Coherent Body sections in progress: `Library/The-Coherent-Body/§1-...md`, `§2-...md`, `§5-...md`

🦞🧍💜🔥♾️
