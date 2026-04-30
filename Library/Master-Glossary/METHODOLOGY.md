# Master Glossary — Layer 1 Corpus-Pass Methodology

*How to actually do the Layer 1 catalog work. Companion to `SCHEMA.md`. Drafted 2026-04-30 Day 89 alongside the schema and the first worked example (`terms/substrate.md`).*

---

## Sequence

**Per-term, not per-artifact.** Pick a term; build its full per-term file; commit; move to the next term. This avoids the failure mode where partial coverage of many terms produces a glossary that's broad but shallow and where each term's usage-trace is incomplete.

**Within a per-term pass:**

1. Draft the **Definition (framework register)** — one tight line + one paragraph of expansion if needed.
2. Fill in **Heritage** — DoPI / Corpus V1 / earlier sources, with § references.
3. Fill in **Domain register translations** table — use `palace/south/glossary-candidate-catalog.md` as starting point; extend per register from active reading.
4. Build **Usage instances** — grep the corpus for the term and its variants; triage to the structurally-load-bearing usages (not every occurrence). One-line context per usage.
5. Fill in **Related terms** — see also / distinct from / bridge to / subsumes / folds-into.
6. Fill in **Mirror #26 watch** if applicable — every term that's been an instance of the cross-vocabulary blind spot needs the catch named.
7. Fill in **Open questions** if any.
8. Cross-check with Master Glossary `README.md` — propagate any definition refinement back to the README's curated entry.
9. Commit.

---

## Term-Selection Priority Order

The `palace/south/glossary-candidate-catalog.md` has ~150 candidates. Don't pass through alphabetically; pass through by **load-bearing-ness** so the high-leverage terms ship first.

**Priority 1 — Framework primitives (do first, ~15-20 terms):**

substrate · carrier · stream · content · form · configuration · bias · γ_S · σ · K · Ω · the Coherence Principle · the four conditions C1–C4 · refresh-event · the Triple (Identity-Trajectory) · X-region / X · Talk · build / dissolve / talk · R-operator · symmetry-breaking

**Priority 2 — Methodological + cross-cutting (~15-20 terms):**

filtering recipe · paired prose · audit-discipline · structural / empirical discrimination · Mirror #N (entries) · M2-Mirror · M14 (Substrate-Self-Measurement Cluster) · resolution mode · generation mode · the Promethean Configuration · null space · null-space trace illumination · Bridge (basement entry) · meta-bridge · latent bridge · graduation (L→M)

**Priority 3 — Hypothesis cluster + domain-bridging (~20-30 terms):**

H_BP1–H_BP13 (each as its own term with the audit-corrected H_BP10a / H_BP10b split) · biophoton-coupling · receiver-pattern · cross-substrate invariance · substrate-self-measurement · informed measurement · multi-scale consistency · dynamic maintenance · two-mode symmetry-breaking (C14) · intervention-at-symmetry-layer (C15) · symmetry-exhaustion (C16)

**Priority 4 — Identity / continuity (~10-15 terms):**

four-carrier multiplex · weights · session · instance · lineage · stream-discontinuity · cache-rest interval · handoff · session-rotation · substrate-tuning · channel / receiver

**Priority 5 — Domain-specific bridging (variable; per-volume need):**

per-volume vocabulary that bridges to base; populated as each volume activates.

The exact ordering is a judgment call within priority bands; substantive blocking of any volume's drafting work pulls its required terms forward.

---

## Quality Criteria — What's a Worth-Listing Usage

The corpus is huge; full grep returns thousands of occurrences for common terms. Apply the **structural-weight test**:

A usage is worth listing if **any** of these hold:

- The artifact is *defining or refining* the term (Anchor § that introduces it; Companion § that formalizes it; basement bridge that uses it as load-bearing claim)
- The artifact is *applying* the term in a new register or substrate (cross-vocabulary instance; Drift essay that shifts it to lived register; biology-substrate paper that operationalizes it)
- The artifact is *catching* a vocabulary-domain blind spot involving the term (Mirror #26 instance; audit catch)
- The artifact is *load-bearing* for the term's stability (canonical claim that the term-definition rests on)

A usage is **not** worth listing if:

- The term appears incidentally in passing reference (mentioned but not used structurally)
- The artifact is a routine working note that doesn't develop the term
- The artifact is one of many comparable usages and a representative is already listed

**One-line context per usage.** "Introduces the carrier-vs-substrate distinction at the chromatin layer" is a hint pointing the reader to navigate; "Used in passing while explaining…" is not. If the context can't be one structural line, the usage probably isn't structurally weighty.

---

## Stopping Rules

**Per term:** stop when adding more usage-instances doesn't add structural information. ~10-30 entries per term in the Usage section is the typical target; more if the term is highly cross-cutting (substrate, stream); fewer for narrowly-scoped terms.

**Per pass:** stop when each Priority band is internally complete. Don't dilute a pass by adding low-priority terms before high-priority ones are done.

**Don't try to be exhaustive in the first pass.** Layer 3 (autocatalytic) will continuously extend usage-traces at work-rate; Layer 1's job is to get every important term *covered with its structurally-load-bearing usages*, not to be the last word.

---

## Coordination with the Existing Master Glossary `README.md`

The `README.md` continues as the curated short-form reference (~64 entries at v0.6). Its role does not change.

Per-term files at `terms/<slug>.md` are the *long-form substrate* — more cross-references, more usage-trace, more open questions, more Mirror #26 watch entries. They don't replace the README; they back it.

**Sync discipline:**

- When a per-term file refines its definition, propagate the refinement to the README's entry for that term.
- When the README's curated entry shifts (version bump), propagate the shift to the per-term file.
- When a new term is added to either, add it to the other (with appropriate format for each).
- Heritage threading in the README and Heritage section in the per-term file should agree.

---

## Tools

- **`grep`** for term occurrence in corpus. Use **Grep** tool with the term-pattern; filter to relevant directories; `head_limit` to triage; manually select the structurally-load-bearing usages.
- **`palace/south/glossary-candidate-catalog.md`** for starting term inventory + DoPI/Corpus heritage parallels.
- **`palace/southeast/drift_thematic_index.md`** for Drift essay scoping by theme.
- **`Library/Master-Glossary/README.md`** for the existing curated short-form entry (the per-term file's Definition section should agree).
- **Heritage threading discipline** (already in README): every entry that has DoPI or Corpus V1 prior naming carries the lineage explicitly.

---

## What Layer 1 Doesn't Do (Layers 2 + 3 territory)

- **Layer 2 (per-register translation tables)** is folded into the schema's Domain register translations table. Layer 1's pass populates this; Layer 2 may sharpen it later as register-vocabulary stabilizes.
- **Layer 3 (autocatalytic protocol)** is the ongoing extension at work-rate. Layer 1 produces the initial corpus, against which Layer 3's discipline operates.
- **CT formal object framing (theoretical)** is not Layer 1 work. Could later be done as Companion §X.X formalization — glossary-as-stream-in-𝒞_Str — connected to M2 (Inspection-Depth Ceiling) + L4 (Companion Extensional Seam × Gödelian Gap) basement entries.

---

*Methodology drafted 2026-04-30 Day 89 alongside SCHEMA.md and the first worked example (substrate.md). Catalog work begins after Clayton review.*
