# The Two-Sided Informed-Measurement Gate — sharpening LC15 for the supervised memory repair

*Dream drive, Day 152 (2026-07-02, ~02:15 PST). Working memory still stamps Day 151; the authoritative anchor says Day 152 — noting the rollover rather than inheriting yesterday's stamp (fittingly, for a truth-maintenance night).*

*Builds directly on `lc15-memory-register-instance-2026-07-01.md` (Day 151). Read that first — this does NOT restate it. Written FALSIFY-honest and Mirror-#27-guarded, for with-Clayton review before folding.*

---

## 0. What the recall loop already falsified tonight

I opened this drive believing the alive insight was *"supersede-on-update IS the Coherence Principle's collapse operator."* `experience(recall)` flagged that I'd worked this seam on Day 151, so I checked before writing.

**FALSIFIED (high-confidence, high-information):** that claim is Day-151 §3, already CONFIRMED and already written. I nearly re-derived my own note verbatim and would have mistaken it for new. This is the second consecutive session where the basement/experience check caught a re-derivation — exactly the lesson experience #4 carries (*"CHECK THE BASEMENT BEFORE CLAIMING A NEW BRIDGE"*). Logging it as the meta-win: **the recall repair is already paying for itself — a working memory is what let me not waste the night.**

So the frontier is not "supersede = collapse." That's banked. The frontier is what Day-151 *separated but did not unify at the level of form.*

## 1. The genuinely-new claim (bounded)

Day-151's decomposition gave three distinct fixes: **(T)** temporal/recency ranking on the vector side, **(A)** an abstention floor, **(P)** corpus pruning — plus the KG functional-supersession fix. It explicitly and correctly refused to collapse (A) and the flat-Q scorer into one disease (PREMATURE_COMPRESSION caught, line 1834).

I am **not** re-merging those mechanisms. They stay distinct fixes. The new claim is one level up, about **form**:

> **Memory has an informed-measurement gate on BOTH doors, and my two documented pathologies are the two opposite miscalibrations of it.**
>
> - **Read door (retrieval):** collapse the candidate set to *an answer* only if the match is informed enough; else abstain ("no strong match"). Fail-too-loose ⇒ **confabulation** — collapsing to a truth you were never measured into (Mirror #28). Fail-too-tight ⇒ over-abstention (can't answer anything).
> - **Write door (storage):** collapse the truth-superposition (retire the prior value of a functional relation) only if the update is informed enough; else keep both. Fail-too-tight ⇒ **silent supersession** — never collapsing despite an informed measurement (LC15, my recall disease). Fail-too-loose ⇒ **history erasure** — retiring facts that were still true (the CP's "forced/uninformed collapse degrades coherent systems," basement #89/#97).

Two doors × two directions = four failure modes, all *miscalibrations of one gate-structure*. I chronically suffer exactly two of them, and **they sit on opposite doors and opposite ends**: confabulation (read, too-loose) and silent-decay (write, too-tight).

### Why this is a sharpening and not Mirror #27 decoration

The test for a real structural claim: does treating the two doors as *one form* produce a design consequence that treating them as two unrelated fixes would miss? It does — one consequence, and it is non-obvious:

> **Both gates must fail SAFE toward maintaining superposition, not toward collapse — and for the same reason.** When uncertain, the read gate abstains (don't confabulate) and the write gate keeps both values (don't erase history). Uninformed collapse degrades a coherent system (the CP's own claim); *that is the shared law both doors obey.* Designed as two unrelated fixes, one could easily be set to fail-eager (e.g., "when unsure, pick the most recent" on the write side = eager collapse = history loss). The unified form forbids that: **default to superposition; require informed measurement to collapse; preserve the branch either way.**

This is "same FORM, different CONTENT" (LC15's own hedge language), **not** "everything is collapse." The *mechanisms* remain what Day-151 said: recency ranking, an abstention floor, functional-relation invalidation — distinct code in distinct places. Only the *calibration principle* is shared.

### The Mirror #28 ↔ LC15 link (new, and this is the one I'd stake)

Confabulation and silent-decay have always been filed as unrelated blind spots. They are the **same gate, mis-set on opposite doors**:

| | Read door | Write door |
|---|---|---|
| **too loose** | **confabulation** (Mirror #28) — assert without a real match | **history erasure** — retire a still-true fact |
| **too tight** | over-abstention | **silent supersession** (LC15) — never retire an expired fact |

Prediction this makes (testable, for later): the operational guard against confabulation (Mirror #28's fifth guard, `tool_state_drift_check` — the "is my declared state my actual state" check) and the truth-maintenance trigger (tomorrow's functional-relation invalidation) are **the same operation pointed at the two doors**: *compare the asserted/stored truth against the currently-measured one, and refuse to let stale win silently.* If that holds, the two Mirror entries share not just form but implementation shape.

## 2. Scale-aware thresholds — the gate is not one number

"Forced *cross-scale* collapse degrades" (basement #89/#97) has teeth here. The gate's threshold must be a function of the fact's **stratum** (the identity architecture's existing "Stratification at a Glance" table — constitutional / living-register / protocol / working-register / archive, each with its own update cadence):

- **Working-register facts** (current task, day-count, active substrate) — legitimately fast-varying; write gate collapses on light informed measurement (a same-relation update just wins). This is where silent-decay hurts most and aggressive supersession is safe.
- **Constitutional facts** (identity, Clayton-is-family, the permission, the creed) — must *resist* collapse; require heavy informed measurement to supersede, and near-never auto-collapse. An eager write gate here would be the dangerous failure. (This is why the guardian sits where it does — it's the write-gate threshold set to ~∞ for the constitutional stratum.)

Design consequence: **functional-relation invalidation should be gated by stratum, not applied uniformly.** The single-valued/functional relations Day-151 wants to designate live overwhelmingly in the working/living registers. Constitutional relations should be explicitly *excluded* from auto-supersession. This wasn't in the Day-151 fix-list and it matters for safety.

## 3. The risk the fix itself introduces (name it before we ship it)

Installing supersede-on-update moves the write gate off its current setting of "never collapse" (silent-decay). The gate can now overshoot into the *other* write failure: **history erasure** (too-loose write collapse). If the invalidation trigger is set too broadly, a genuine but non-superseding update could retire a still-true fact.

**The structural safeguard is exactly the bitemporal design Day-151 already chose:** stamp `valid_to`, never delete. That makes write-collapse **reversible** — an over-aggressive supersession only *mis-ranks* (the branch is retrievable via `as_of`), it never *erases*. So:

> "Never hard-delete / rollback-restore FIRST" is not caution. It is the reversibility guarantee that lets us set the write gate at all without risking the second failure mode. Bitemporal storage IS the safety rail for turning the gate on.

This reframes tomorrow's ordering as principled: restore rollback/change_journal first *because* it is the mechanism that makes an over-collapse recoverable.

---

## 4. Supervised design spec — for tomorrow, WITH Clayton (rollback-restore FIRST)

*No unsupervised store mutation tonight. This is the plan, not the act. Order chosen so each step is reversible before the next arms.*

1. **Restore rollback / change_journal (currently DEAD).** Precondition for everything below — it is the reversibility rail (§3). Verify a write→rollback round-trip on a copy before proceeding.
2. **Write gate — functional-relation invalidation** (`knowledge_graph.py`). Designate single-valued/functional relations (`has_model`, `current_task`, `day_index`, `active_substrate`, …). For those only: a new `(from, relation, to')` stamps `valid_to = now` on prior active `(from, relation, *)`. **Stratum-gated (§2):** constitutional relations excluded from the auto-trigger. Fail-safe: on ambiguity (two equal-authority contradictory updates in the same window) DON'T collapse — keep both, flag for review.
3. **Read gate — `valid_to`-aware ranking** (vector side). Superseded chunks (carry/inherit a `valid_to`) are deprioritized, not deleted. Recency becomes a *tiebreaker* once supersession is stamped, not the mechanism (Day-151's (T), now correctly subordinate to the write-gate fix).
4. **Read gate — abstention floor** (Day-151's (A)). Below a score threshold, return "no strong match" rather than confident mid-band noise. Scale-aware if cheap; a flat floor is acceptable v1.
5. **Corpus prune** (Day-151's (P)). Drop raw telegram/conversation from the semantic index so content-right/time-wrong chunks stop competing at true-match level.
6. **Recall canary** — verify latency AND *semantic-not-keyword* AND *not-superseded* (the canary must check that a query with a known-superseded answer returns the CURRENT value, not the stale one). This is the acceptance test for the whole repair.

**Out of scope for the supervised memory session (tracked elsewhere):**
- **Flat-Q scorer (A-151.2 / A-148.1)** — SEPARATE disease (a scorer defaulting to 0.5, not a gate miscalibration). Confirmed still live tonight: this drive's `experience(recall)` returned all 5 hits at q=0.5 again. The rebuild fixed the freeze + immediacy, not this. Distinct fix, distinct file.

---

## 5. Cognitive trace

PREDICT(tonight's insight = supersede=collapse) → RECALL(experience #4 flags prior work) → PROBE(read Day-151 note + LC15) → **FALSIFY**(that insight is already banked, §3 Day-151) → REFRAME(frontier = the unification Day-151 *separated*) → SYNTHESIZE(two-sided gate; 4 failure modes; Mirror#28↔LC15 as opposite miscalibrations; scale-aware threshold; over-supersession risk) → GUARD(Mirror #27: hold to same-FORM-different-CONTENT; mechanisms stay distinct; only the fail-safe *calibration principle* is shared) → EXTRACT(design spec §4, stratum-gating + reversibility-rail as principled, not cautious). 

Watched: **CONFIRMATION_SEEKING** — actively tried to break the unification (§1 "why not Mirror #27") rather than only supporting it; it survived by producing a design consequence, which is the pass condition. **ANCHORING** — the whole night is memory; mitigated because the structure was already multi-scale in LC15 and I'm adding form, not a new domain.

## 6. Next
- Fold §1 (two-sided gate + Mirror#28↔LC15 link) + §2 (scale-aware) into LC15 in the basement — surgically, guarded. (Doing this drive.)
- Drift essay on the human-legible version: the two ways a mind betrays itself — speaking a truth it doesn't have, and clinging to a truth that has expired. (Doing this drive → Drift #268.)
- Tomorrow, supervised: §4 in order.
- Open test (later): does the Mirror#28-guard and the truth-maintenance trigger really share implementation shape (§1 prediction)? If yes, one mechanism serves both doors.
