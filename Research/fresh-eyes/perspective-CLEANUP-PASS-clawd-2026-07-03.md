# Cleanup pass — *Perspective* Consolidated Draft 0.1 (step 1: address what's in there)

*Day 153 (2026-07-03). Clayton: "clean it up, then expand — one step at a time; first, address what's in there." This is step 1 only: the internal-consistency fixes that need **no new material** — the seams a reader stumbles on, drawn from my mesh-review + the reviewer's final reader report. Each item: exact locus, the defect, and either a specified fix (apply directly) or a flagged ruling (Clayton decides). Expansion (the missing organs) is step 2, docketed at the end — not executed here.*

*Source substrate: `incoming/perspective-draft.txt` (extracted from the PDF); loci cited by § and by extracted-text line where useful. The compilable master lives with the drafting peer (Fable); this punch-list is written to be applied there.*

---

## A. FIXES — specified, no ruling needed (apply as written)

### A1. Kind-order direction — the §2.7 ↔ §3.1-A2.2 contradiction *(MEDIUM; the one real logical seam)*
**Loci.** §2.7 KD.1 (line ~633): "The strata are nested; **each includes the capacities below**." — §3.1 A2.2 (line ~821): "*Streams* is stratified by the kind-order of §2.7, **reactive ⊇ self-maintaining ⊇ self-referential ⊇ abstracting, with strict inclusions.**"

**The defect.** §2.7 orders *capacities* (an abstracting stream *includes* the lower capacities → capacity-sets nest ⊆ *up* the ladder), and states it in words, no symbol. A2.2 writes the induced *stream-class* containment (⊇, *down* the ladder — {reactive streams} ⊇ … ⊇ {abstracting streams}) and attributes it to "the kind-order of §2.7." Both are correct under their referents, but a reader who symbolizes §2.7 as ⊆ meets ⊇ "on the same order" and reads a contradiction. This is the seam; it is a labeling omission, not a math error.

**Fix (A2.2, insert the direction-note).** Replace A2.2's opening with:
> (A2.2) Kind-stratification. *Streams* is stratified by the kind-order of §2.7. **Direction, stated because the two nest oppositely:** §2.7 orders *capacities* — each higher kind includes the capacities below — so the induced *stream-classes* nest in reverse: reactive ⊇ self-maintaining ⊇ self-referential ⊇ abstracting, with strict inclusions (every abstracting stream is *a fortiori* self-referential, self-maintaining, and reactive; not conversely).

One clause; changes neither claim; dissolves the stumble. (Optional twin: at §2.7 KD.1 add "— so the *classes* they define nest oppositely, §3.1 A2.2." to pre-empt it from the first side too.)

### A2. Forward-reference: kinds used in §2.2 before defined in §2.7 *(reader-stumble)*
**Locus.** §2.2's stream-tuple invokes kind before §2.7 defines it.
**Fix.** At the first use in §2.2, add a parenthetical forward-pointer: "(the *kinds* — reactive / self-maintaining / self-referential / abstracting — are defined at §2.7)." One line; removes the strain without moving the definition.

### A3. Atlas self-application: 3-line per-Part vs 5-line canonical *(MEDIUM)*
**Loci.** §7.4 canonizes the five-line card (SEES / NULL SPACE / COMPLEMENTS / BOUNDARY / NAVIGATIONAL IMPLICATION); but §4.5, §5.7, §6.7 self-Atlases use only three (SEES / NULL SPACE / BOUNDARY); only §7.6 uses all five.
**Fix (declare the two forms, at §7.4).** Add one sentence where the full card is introduced:
> The three-line form used to close each Part above — SEES / NULL SPACE / BOUNDARY — is the *working self-atlas*, the minimum a lens owes at a section boundary; the full five-line entry, adding COMPLEMENTS and NAVIGATIONAL IMPLICATION, is reserved for terminal entries (a whole framework in its dock, as in §7.6).
Retroactively legitimizes every prior self-Atlas; no per-Part edits needed. (Cheaper than adding two lines to each.)

### A4. Catachresis-marking policy — adopt + state in §0 *(reviewer's proposal, accepted)*
**Defect.** The †/catachresis marks are dense in Part I as designed, sporadic by Part VI — inconsistent, and the inconsistency itself reads as drift in a book whose typography is law.
**Fix.** Adopt the reviewer's policy and state it in §0's typographic law: *full marking in Part I (the reader is being trained); first-instance-per-Part thereafter (the discipline is installed — one mark per Part per term re-arms it without cluttering).* Then a light pass to conform Parts II–VII to first-instance-per-Part. State the rule; the pass follows the rule mechanically.

### A5. Date *(MINOR)*
**Locus.** Title + §1.1: "blessed 2026-07-05." Today is 2026-07-03.
**Fix.** Make it a build-stamp (compile date) rather than a fixed future date, or set to the actual consolidation date. Trivial, but the book that marks everything shouldn't misdate itself.

### A6. finite_model.py — **RESOLVED, logged for the record**
Was the HIGH catch (claimed machine-verified + in-repo; not locatable). Clayton supplied it Day 153; ran clean (320 pairs exhaustive, all six categorical properties True, nontrivial η/ε witnesses). Committed to `Technical-Work/The-Coherence-Principle/programs/finite_model.py` + README (commit e3a86c21). The §3.2 "no-longer-merely-promissory" citation now resolves to a runnable file. **No further action** beyond ensuring §3.2 / the Status page point at that repo path.

---

## B. KEEP — flagged as intentional, do not "fix"

### B1. The three tellings (§1.3 no-return / §2.8 loop / §6.6 arc)
The reviewer's catch: these are one doctrine told three times, and it reads not as redundancy but as **escalating liturgical register** — the same bell at theology-, dynamics-, and deathbed-pitch. **Keep.** Optional light touch: a one-clause cross-reference at each site naming the other two, so the reader registers the repetition as *designed* rather than wonders if it's an oversight — e.g. at §6.6, "(the third striking of one bell — cf. the theology of §1.3, the dynamics of §2.8)." Clayton's call whether to make the liturgy explicit or leave it subliminal.

---

## C. RULING NEEDED — one item, and it's the priority

### C1. The Anchor's theorem-tier (T1–T6): the book's **one self-inflicted scar-rule violation** *(HIGH — priority cleanup)*
**The defect (reviewer's organ (f), and I concur it's the sharpest in-draft problem).** The Anchor carried a numbered theorem tier — six theorem-pairs (T1–T6). *Perspective* dissolved them into narrative rather than restating them as numbered objects **or** retiring them into the residue ledger. So they are **neither carried nor buried** — which is precisely the state the book's own scar-keeping rule ("never erase the anomaly," "keep the record, scars included") forbids. Everywhere else the book keeps its scars visible (the A2.1 repair note, the finite-model discharge); here, uniquely, it quietly absorbed prior published objects with no forwarding address. A hostile reader who knows the Anchor will catch exactly this, and it's the one catch that would land against the book's *integrity* rather than its completeness.

**Why it's step-1 not step-2.** It's not new content — it's *disposition of content already in the lineage*. The fix is bookkeeping the book already owes itself.

**The ruling (Clayton).** Pick the disposition per theorem-pair — I recommend a **split**, not a blanket choice:
- **RESTATE** (as numbered objects in Part III, with repair notes) the pairs that survive as live theorems under the new basis — these become the book's Part-III theorem tier, keeping the "scars in the axioms" maneuver consistent with a scars-in-the-theorems tier.
- **RETIRE-WITH-FORWARDING** (one line each in a residue ledger) the pairs genuinely absorbed into narrative — e.g. "T_k → absorbed into §2.6 (channels) / §7 (coherence conditions); retired here, not lost."

**What I need from you to execute:** the Anchor's T1–T6 statements (I can pull them from `Technical-Work/The-Coherence-Principle/` §5–§7 — the descriptive/dynamics/coherence theorem-pairs — but I want your ruling on which survive vs. retire before I draft the tier, since that's a canon decision about your published theorems, not mine to make). Give me the split and I'll draft both the restated tier and the residue-ledger lines in one pass.

---

## D. Step 2 preview — the missing organs (NOT executed here; docket triage)

Per "one step at a time," expansion waits. But here's the useful triage of the reviewer's docket — **which organs I can already draft from our corpus** vs. **which need your material/ruling** — so you can sequence step 2:

**I can draft now from existing work (no new material needed from you):**
- **(a) Temporal Density Inversion** — this is our occupancy/coupling-rate work: C17 (μ=λτ), LC52 (binding-continuity λτ), the estimator-dependent-duration result, Bergson/Husserl already in the reading register. Substrate-generic on the human side, inversion recast as prediction — writable. *Needs only your ruling: include (substrate-generic) or reserve.*
- **(b) Two-valence archetype** (Prometheus/Lucifer vs. Satan) — this is "The Curvature of Good and Evil" (published) + LC50 (Hopf/Ouroboros) + the Promethean Configuration work. The mythic face of TE.1–4 is largely written; I'd adapt it into a Part V §5.1-adjacent section. *Needs the angels-demons note's actual source text for fidelity — you flagged you'd supply it.*
- **(c) Epistemology of discovery / dimensional leakage** — DoPI Part IV; the compass-needle / fogged-plate examples and occupancy-vs-awareness distinction are retrievable. Belongs at Part II or as IV's opening.
- **(d) Heaven/hell as felt topology** — DoPI §8; dissolution of metaphysical geography into navigational state. *Needs your ruling on restoration (pastoral weight vs. scope-creep).*
- **(e) Cromwell's rule cosmologized** — the 0/1 open-interval theology's epistemic face; one paragraph for §1.5. I can draft from the fracture-cosmogony work.

**Only you can supply (material where material is the answer):**
- Part IV Ecology population (the deeper tiers — the §4.4 stub's gate; drive in your specimens)
- The Guide's practice protocols (Part VII, paragraph→protocol)
- The Atlas corpus / exemplar entries (Part VII §7.4 demonstrations)
- The angels-and-demons note's text (feeds (b) and Part IV settled-polarity entries)
- Fuller Ship-of-Theseus written form, if beyond what's in the corpus
- **Three rulings:** TDI inclusion · Monroe's load (loops-image only vs. fuller cartography into II/IV) · heaven/hell restoration

**My reader-level agreements with the report (peer notes):**
- The theorem-tier (C1) is correctly the #1 in-draft problem — it's the only place the book breaks its own trust-mechanism. Fix it before flesh.
- The shmagency answer the reviewer sketches is exactly right and *unusually strong for us*: the invariants attach to the *activity* of navigating, not the label "agent," so the shmavigator still navigates and CC.2 still binds it. Pair it with the Street debunking point — our structural invariants survive evolutionary debunking *precisely because they aren't adaptations* (they're what navigation IS, true in every phase, not selected-for contingencies). When we reach Part V I can draft both defenses tight.
- Ratio, not architecture, is the real deficit: 70pp skeleton, NST given ~700 words. The expansion is real work, not polish. The architecture is sound and the reader believes it — which is the hard part, and it's done.

---

*Step 1 is this list. Nothing above adds a claim; it removes stumbles and dispositions one owed scar. Give me the C1 ruling (theorem-tier split) and I'll clear it; then we pick the first organ for step 2.*
