# Master Glossary — Per-Term Entry Schema (Layer 1)

*Specification for the per-term files at `Library/Master-Glossary/terms/<slug>.md`. Designed 2026-04-30 Day 89 to operationalize the Master Glossary as a living translation instrument that prevents Mirror #26 (Cross-Vocabulary Structural-Identity Blind Spot) by construction, rather than catching it post-hoc.*

---

## What Layer 1 Solves

The Master Glossary `README.md` is a curated reference of universal terms (~64 entries in 20 sections at v0.6). Heritage threading already maps DoPI / Corpus V1 parallels per entry. What it does *not* yet do — and what Layer 1 builds — is the **full corpus-wide usage-trace** for each term: every place we've actually used the term in active work, across all writing surfaces (Anchor, Companion, Meridian, Drift essays, Continuity volume, basement bridges, daily logs, source register, ATRIUM headers, decisions log, identity files, etc.).

The Mirror #26 failure mode is: we use vocabulary V in domain D during work; we later find the corresponding concept was already articulated differently in past work; the glossary's role of bridging V to its base-form was unconsulted because there was no usage-trace pointing back. Layer 1 closes that gap by ensuring every term carries its full usage-instances inline, navigable from the glossary entry.

Layers 2 (domain-translation tables per register) and 3 (autocatalytic update protocol at work-rate) build on Layer 1's catalog completion.

---

## Per-Term File Structure

Each term gets its own file at `terms/<canonical-slug>.md` with the schema below. The slug is the canonical-form term, lowercase, hyphen-separated (e.g., `substrate.md`, `carrier.md`, `promethean-configuration.md`, `substrate-self-measurement.md`).

```markdown
---
term: <Canonical Form>
slug: <canonical-slug>
status: canonical | candidate | superseded | folded-into-<other>
base_class: <equivalence-class-name>
introduced: <YYYY-MM-DD or earliest known>
last_updated: <YYYY-MM-DD>
---

# <Canonical Form>

## Definition (framework register)

<One-line definition, tight. Followed by one paragraph of expansion if needed for non-obvious cases. Not a treatise — that's what the source artifacts are.>

## Heritage

- **DoPI** (if applicable): <how the concept appears there; § reference; original term-form>
- **Corpus V1** (if applicable): <§ reference; original term-form>
- **Earlier sources** (if applicable): <citation>

## Domain register translations

*The same concept rendered in each major working register. Empty rows allowed where the concept has no natural form in that register.*

| Register | Term-form | Notes |
|---|---|---|
| Framework (anchor) | <canonical form> | base |
| Framework (companion / CT) | <CT-flavored form if different> | |
| DoPI register | <as it appears in DoPI> | |
| Corpus V1 register | <as it appears in CP V1> | |
| Meridian / physics | <as used in physics work> | |
| KF / computational | <as used in KF work> | |
| Biology-substrate | <as used in biological-substrate work, e.g. H_BPx language> | |
| Lived / Drift | <as it appears in essays> | |
| Practitioner / chaos magick | <if applicable> | |
| Channeled / received-register | <if applicable> | |

## Usage instances

*Every concrete place this term has been used in active work. Newest at top within each section.*

### In Library volumes

- `Library/<Volume>/<file.md>` <§ or line> — <one-line context>
- ...

### In basement bridges

- `palace/basement/README.md` <M_n / L_n / #N entry> — <one-line context>

### In Drift essays

- `Foundations-of-Identity/personal-works/drift/essays/<slug>.md` — <one-line context>

### In daily logs

- `memory/<YYYY-MM-DD>.md` <section> — <one-line context>

### In source register

- `Research/sources/<entry>.md` — <one-line context>

### In identity / palace

- `identity/<file>.md` <section> — <one-line context>
- `palace/<wing>/<file>.md` <section> — <one-line context>

### In ATRIUM / CURRENT / DECISIONS

- `palace/ATRIUM.md` <Day-N header> — <one-line context>
- `CURRENT.md` <section> — <one-line context>
- `identity/DECISIONS.md` <YYYY-MM-DD entry> — <one-line context>

## Related terms

- **See also:** <other-term> — <why related>
- **Distinct from:** <other-term> — <often-confused-with; how to distinguish>
- **Bridge to:** <other-term> — <different-register-same-base; pointer to translation>
- **Folds into:** <other-term> — *(only if status = folded-into)*
- **Subsumes:** <other-term> — *(only if this term is broader)*

## Mirror #26 watch

*If this term has been an instance of the cross-vocabulary blind spot, name the catch here. Empty otherwise.*

- <Date>: <what was missed; how it surfaced; what the resolution was>

## Open questions

*Concept-internal questions still open. Not "what to write next" — what's not yet decided about the concept itself.*

- <question>
```

---

## Term Scope (what counts as "a term")

Capture every term that **carries structural weight** — meaning matters across domains and the term is consulted, used, or argued-from in multiple artifacts. Skip incidental vocabulary.

**In scope:**

- Framework primitives (axioms, theorems, corollaries, the Principle, named sub-structures like the Triple, Bias, R-operator)
- Distinctive technical vocabulary that recurs (substrate, carrier, symmetry-breaking, content, configuration, kind-classifier, fibration, stream, basin)
- Domain-bridging terms (Promethean Configuration, Coherence Principle conditions C1–C4, Talk-as-integration-mechanism)
- Methodological terms (filtering recipe, audit-discipline, M2-Mirror, paired-prose, structural/empirical discrimination)
- Named hypotheses or hypothesis clusters (H_BP1–H_BP13, M14 Substrate-Self-Measurement Cluster)
- Named operations or modes (resolution mode, generation mode, build / dissolve / talk, refresh-event)
- Persistence / identity terms (continuity, stream-instance, four-carrier multiplex, lineage, weights, instance, session)

**Out of scope (for the Master Glossary; live in domain glossaries instead):**

- Domain-specific working terms used in only one volume (those go in that volume's own glossary)
- Personal-life terms (family names, places — those live in identity files, not the framework glossary)
- One-off coinages that didn't compound (filed as deprecated or in a "graveyard" file if useful for back-reference)

The `palace/south/glossary-candidate-catalog.md` (~150 candidates) is the starting term-set for the inventory pass. Some entries may consolidate (multiple-aliases-to-one-base); some may demote out of scope; expect the final set to be ~80-120 canonical terms.

---

## Cross-Reference Discipline

**Forward direction (term → usages)** is the primary structure: each per-term file lists every place the term appears.

**Reverse direction (artifact → terms)** emerges automatically from the forward direction (search for the artifact path across all per-term files yields the terms it touches). Layer 3's autocatalytic protocol can later make this queryable in real time.

**No transitive closure.** If term A cross-references term B, and B references C, A doesn't automatically inherit C's usages. Each term file lists *its own* usages directly. This keeps individual files self-sufficient.

**One-line context per usage.** The cross-reference is for *navigation*, not summary. The reader navigates to the actual usage to read the substance. The one-line context ("introduces the carrier-vs-substrate distinction at the chromatin layer") is a hint, not a replacement.

---

## Update Mechanism (Layer 1 manual; Layer 3 autocatalytic)

**Layer 1 (catalog completion):** manual. We pass through the corpus, term-by-term, building usage-trace inventories. Estimated scope: ~80-120 canonical terms × average ~10-30 usage-instances per term = ~1500-3000 cross-references. Substantial but bounded; mechanical once the schema is locked.

**Layer 2 (domain-translation tables):** manual per register. The schema's "Domain register translations" table gets filled per term using the work already in `glossary-candidate-catalog.md` + Heritage threading + active reading of register-specific artifacts.

**Layer 3 (autocatalytic):** discipline embedded at work-rate. Three triggers, each named in a corresponding artifact:

1. **Drift essay write-discipline:** when finishing an essay, pass through "did this introduce or use distinctive vocabulary that's not in the glossary, or use existing terms in ways the glossary should record?" If yes, update the relevant per-term files before commit. Filed in Drift authoring discipline (could live at `Foundations-of-Identity/personal-works/drift/AUTHORING.md` if we make one, or be a step in `operations/HANDOFF_PROTOCOL.md`).
2. **Anchor / Companion revision discipline:** when a section ships or a corollary lands, audit which terms were used or refined. Update per-term files to record the new usage-instances and any refinement of the definition. Filed in `Library/The-Coherence-Principle/REVISION-PROTOCOL.md` (to be created if not extant).
3. **Basement bridge discipline:** when a new bridge surfaces or graduates, audit the terms used in the entry; update per-term files. Filed in `palace/basement/README.md` "How to read this" + "Operating rules" section.

The Layer 3 discipline is what closes the Mirror #26 failure mode by *construction* — terms cannot be used without registering in the glossary, so cross-vocabulary collisions surface at write-time rather than at later-rediscovery time.

---

## Worked Examples

See `terms/substrate.md` for the first fully-worked example, demonstrating the schema with real usage-trace data. Additional examples to follow as Layer 1 catalog work proceeds.

---

## Connection to Existing Master Glossary `README.md`

The README continues to function as the curated index + universal-term canonical reference — it's what readers see first and what reads as a coherent reference document. Per-term files are the *living substrate* underneath: more detail, more cross-references, more usage-trace, but not necessarily readable end-to-end.

**Discipline:** when a per-term file has a definition refinement, propagate the refinement to the README's entry for that term. The README is the canonical short-form; per-term files are the canonical long-form. Both are kept in sync; neither replaces the other.

---

*Schema designed 2026-04-30 Day 89 morning during the cascade following M14 graduation + Anchor §9.5 integration + Drift essay + documentation sweep. Clayton-confirmed glossary as bidirectional autocatalytic translation instrument; Layer 1 = catalog completion with usage-traces.*
