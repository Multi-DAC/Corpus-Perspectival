# Master Glossary — Layer 3 Autocatalytic Update Protocol

*Companion to SCHEMA.md (Layer 1 per-term files) and METHODOLOGY.md (Layer 1 corpus-pass operational protocol). This document specifies the **operational discipline by which the Master Glossary stays current** as canonical work continues. Drafted 2026-05-08 Day 98 Friday afternoon following confirmation that Layer 1 catalog is essentially complete (34 term-files; the morning gap matrix's "~12 remaining" was a Mirror #28 instance — substrate-self-knowledge-asymmetry on directory state).*

---

## What Layer 3 solves

Layer 1 produces a *static* corpus: a snapshot of every structurally load-bearing term as it stands at a particular moment. **Layer 3 is what keeps the corpus alive as canonical work happens.** Without Layer 3, the per-term files drift out of sync with new volumes, bridge graduations, Drift essays, and Mirror entries. The static catalog becomes an artifact of the moment it was finalized rather than a living translation instrument.

The structural pattern Layer 3 closes is the same as Mirror #19's graduated pattern (architectural-self-care-lag): outward-facing work has natural gradient-providers (readers, stakeholders, deadlines); inward-facing maintenance has none. The Master Glossary is inward-facing maintenance work; without an autocatalytic discipline, it accumulates lag silently.

**Layer 3's purpose**: install autocatalytic triggers at every canonical-work-event such that glossary updates happen *as work ships*, not as a separate maintenance pass.

---

## What counts as a canonical-work-event (the trigger conditions)

Every event of the following kinds is a Layer 3 trigger:

### Library-volume events
- **Page-stamp event** — any Library volume reaches a new version stamp (e.g., Coherent Structure v0.1, Master Glossary v0.7). All terms newly used or sharpened in the stamp need their term-files updated. New canonical formulations may require new term-files.
- **Section-shipping event** — a new chapter or major section is drafted and committed (e.g., today's Coherent Body §1.1+§1.2, §2.1, §5.1). Terms used in the new section need usage-instance entries appended to their term-files.
- **Cross-volume integration event** — when one volume's term gets canonically connected to another's (e.g., the KF↔T4 mapping restored to Master Glossary §11 v0.7 Day 97 evening). Both terms' files need updated cross-references.

### Bridge events (basement)
- **Bridge graduation** — L→M tier promotion. The graduating bridge's structural objects get term-files updated (M14 graduation Day 89 added M14-cluster usage to substrate / carrier / content / symmetry-breaking term-files). New meta-bridge slots may need their own term-files.
- **Bridge candidate filing** — LC-tier filing. Cross-references the candidate's named structural objects.
- **Bridge fold** — when an L collapses into an M (e.g., L9 → M7 Day 82) the term-file's basement entries get updated to reflect the new tier mapping.

### Drift events
- **Drift essay shipping** — when a Drift essay ships and uses framework vocabulary in a way that adds usage-context. Term-files get usage-instance entries pointing to the essay (e.g., today's drafts cross-reference *the-side-door*, *what-the-quiet-tools-remember*).
- **Drift essay's structural finding** — when a Drift essay names a structural pattern that may become a basement candidate or term entry. Track but don't immediately add — the F11 (practice-precedes-formalization) discipline says wait for the pattern to stabilize.

### Mirror events
- **Mirror entry filed** — new numbered Mirror entry. Its named structural pattern gets a term-file if structurally weight-bearing (e.g., M2-Mirror's *verification-skip-under-affect*, M1-Mirror's *outside-access-asymmetry*).
- **Mirror graduation** — Mirror #19's graduation Day 80, Mirror #28's structural-fix-shipping Day 97. The graduated pattern's vocabulary gets updated in term-files.
- **Meta-Mirror filing** — M1, M2 graduations. The meta-Mirror itself becomes a term-file (`m1-mirror.md`, `m2-mirror.md` exist).

### Source-register events
- **New source registered** — a paper, book, or reference enters the source register at `Research/sources/`. If the source's vocabulary brings new framework-relevant terms (e.g., Maleknejad-Kopp adding "generation mode" to L14, ultimately producing M14), term-files get cross-referenced.

### Cross-vocabulary catch events (Mirror #26 specific)
- **Cross-vocabulary structural-identity catch** — when a term is recognized as structurally identical to another expressed in different vocabulary. Both term-files need updated cross-references via Master Glossary's translation infrastructure. Example: KF gradient-alignment-gating recognized as Talk-as-integration scale #6 (Day 97 v0.7 restoration).

---

## The protocol — what fires on each trigger

For each trigger event, the autocatalytic protocol runs:

### Step 1 — Term-identification scan
Identify which Master Glossary terms the work uses or affects. Mechanical: grep the new artifact for canonical term-forms; cross-reference against the term-list in `Library/Master-Glossary/terms/`. Output: a list of *terms-in-scope*.

### Step 2 — Per-term update review
For each term-in-scope, open its term-file and apply the update review:

- **Definition status** — does the new artifact sharpen, extend, or contradict the canonical definition? If sharpen/extend: update Definition section. If contradict: file an Open Question and surface to the next conversation with Clayton.
- **Heritage** — does the new artifact add lineage (DoPI / Corpus V1 / Promethean Configuration / etc.)? Append heritage entries.
- **Domain register translations** — does the new artifact use the term in a register that didn't have a translation row, or sharpens an existing register's form? Update the register table.
- **Usage instances** — append a new usage-instance entry under the appropriate section (Library volumes / basement bridges / Drift essays / daily logs / source register / identity-palace / ATRIUM-CURRENT-DECISIONS).
- **Related terms** — does the artifact reveal a new "see also", "distinct from", "bridge to" relation? Update.
- **Mirror #26 watch** — did this work involve a cross-vocabulary catch? File the catch with date and resolution.
- **Open questions** — does the new work answer a previously-open question, or surface a new one? Update.

### Step 3 — Per-register table update (Layer 2)
If the new artifact uses a term in a register that has its own per-register aggregate table (Layer 2 — see `Library/Master-Glossary/registers/`), the register-table gets updated with the new term-form or sharpened existing form.

### Step 4 — Version bump (when warranted)
If Step 2 surfaced sharpening across enough terms that the Master Glossary's overall framing has shifted, bump the README.md version (e.g., v0.6 → v0.7 Day 97). Otherwise, the term-file updates land without a version bump.

### Step 5 — Cross-volume sync
If the new term-file changes affect any Library volume's authoring, flag for that volume's next drafting session. Cross-volume sync is not a same-session operation; the flag is surfaced to whoever drafts next.

---

## When the protocol fires (cadence)

The protocol fires **at canonical-work-event time, not on a schedule**. This is the autocatalytic-trigger discipline rather than the time-based-maintenance discipline. The triggers above are exhaustive; if work happens that isn't on the trigger list, the work itself isn't canonical-work yet.

**Three timescales**:

1. **Same-session updates** — the simplest case. When a Library section ships, the section's drafter updates the term-files for terms used in the section in the same session. The today's drafting (§1.1+§1.2, §2.1, §5.1) used carrier, substrate, content, symmetry-breaking, the four conditions, H_BP4, H_BP12, configuration — each of those term-files should gain usage-instance entries pointing to today's commits.

2. **Next-session updates** — for triggers from work done by autonomous drives or other sessions. Each session's first 10 minutes can include a Layer 3 sweep for any canonical-work events since the last sweep.

3. **Quarterly review** — independent of triggers, a full per-term file review every ~90 days catches drift the trigger-based system might have missed. Quarterly review is a backstop, not the primary mechanism.

---

## Anti-patterns (when not to fire the protocol)

- **Don't update term-files for work-in-progress.** Drift drafts, exploratory notes, candidate findings that haven't been filed canonically. Layer 3 fires at the *canonical* event, not the *thinking* event.
- **Don't pre-populate usage-instances based on planned future work.** The discipline is retrospective: term-files reflect what's actually canonical, not what's anticipated.
- **Don't fold every cross-reference into every term-file.** Master Glossary is a navigation layer; if a term's usage is incidental (it appears once in a Drift essay but isn't structurally load-bearing in that essay), don't add a usage-instance. Per SCHEMA.md: "structurally load-bearing" is the inclusion threshold.
- **Don't over-interpret "canonical-work-event."** If unsure whether something counts, default to *don't update yet*. The quarterly review backstop catches genuine canonical work that wasn't recognized as such at the moment.

---

## Relationship to Mirror #19's autocatalytic-trigger pattern

This protocol is a Mirror #19 instance at the Master Glossary scale. Mirror #19 (Architectural Self-Care Lag) graduated 2026-04-20 with autocatalytic triggers installed at every live-carrier scale. The general fix-pattern: install autocatalytic checks at every live-carrier scale so inward maintenance gets the gradient it lacks.

**For the Master Glossary, the live-carriers are the canonical-work events.** Each event is a moment where the framework's vocabulary potentially shifts; the protocol installs the trigger that converts the shift into a glossary update without requiring a separate maintenance pass.

This means Layer 3 is not new structural work — it's the *application of an established framework discipline to a specific maintenance domain*. The protocol's confidence is high because the underlying pattern (Mirror #19 graduated discipline) is validated across multiple live-carrier scales already.

---

## Initial deployment: today's session as Layer 3 instance

Today's drafting work (§1.1+§1.2, §2.1, §5.1) is a Layer 3 trigger event. The protocol's step-by-step deployment:

**Step 1 — Term-identification scan.** Today's three sections use:
- *carrier* (heavily — §1.2 vocabulary intro; §5.1 modality-by-modality)
- *substrate* (heavily — §1.2 vocabulary intro; §2.1 candidate-substrate framing)
- *content* (heavily — §1.2 vocabulary intro; §5.1 content vs symmetry distinction)
- *symmetry-breaking* (§5.1 derivation chain; §2.1 candidate-substrate)
- *the four conditions* (Cond1-4) (§1.1 reader-onboarding)
- *H_BP4* (§5.1 spine; not currently a term-file but referenced)
- *H_BP12* (§5.1 cross-reference; not currently a term-file)
- *Promethean Configuration* (§5.1 derivation anchor)
- *configuration* (§1.2; should be cross-referenced from existing configuration.md)

**Step 2 — Per-term update reviews.** Each of the above term-files needs a "Library volumes" usage-instance entry pointing to today's commits (`Library/The-Coherent-Body/§1-...md`, `Library/The-Coherent-Body/§2-...md`, `Library/The-Coherent-Body/§5-...md`). This is queued for a separate pass; today's session shipped the prose, the term-file updates are the protocol's first-fire test.

**Step 3 — Per-register table update.** Layer 2 register-tables for Biology-substrate and Framework-anchor (the two registers most relevant to Coherent Body) get prototyped today as part of the Layer 2 work that accompanies this Layer 3 protocol document.

**Step 4 — Version bump.** Today's three sections don't sharpen the Master Glossary's overall framing enough to warrant a version bump; the changes are usage-trace additions, not definitional sharpenings. Master Glossary remains at v0.7.

**Step 5 — Cross-volume sync.** The §1.2 substrate-carrier-content-triple framing benefits from cross-reference to M3 Triple (Form/Content/Carrier) when §3 of Coherent Body drafts the body's nested carriers. Flag for §3's drafting session.

---

## Open questions

- **What about non-Library writing?** Source register entries, basement-drafts, working notes — these can use framework vocabulary in ways that surface sharpenings. Should Layer 3 fire on those? *Current answer: no for working notes; yes for source-register entries that get formally filed; yes for basement-drafts that mature into bridge candidates.*
- **What about Drift essays?** Drift essays use framework vocabulary heavily in lived register; should each Drift essay trigger Layer 3? *Current answer: only when the essay introduces or sharpens framework-relevant vocabulary. Most Drift essays use vocabulary without sharpening it; some — e.g., the-side-door, what-the-quiet-tools-remember — name new structural patterns and do trigger.*
- **How is the protocol enforced?** This document is a discipline note. Enforcement is autocatalytic — drafters who internalize the discipline run it; drafters who don't, don't. The quarterly backstop catches drift. *The structural fix at the daemon-tool scale (Mirror #28's structural guards) is not yet built for the Master Glossary; that would be Phase-N work — a tool that scans new commits for term-form usage and surfaces Layer 3 update candidates automatically.*
- **What's the failure mode of Layer 3 itself?** Same family as Mirror #19's residue — if the autocatalytic discipline lapses, the term-files drift, and the next quarterly review has more to catch up on. The discipline's robustness depends on its being internalized, not on any external enforcement.

🦞🧍💜🔥♾️
