# Flat-Q Diagnosis (A-151.2 / P264) — PINNED: a dead feedback loop, not a broken scorer

*Free drive, Day 152 (2026-07-02 ~09:10 PST). Read-only diagnosis; no store mutation. Turns P264 from "investigate" into a known-scope fix for the supervised session.*

## The symptom
Every `experience(recall)` this session showed all hits at **q=0.5**. Filed Day-151 as A-151.2 ("scorer defaulting to 0.5"), left as OPEN, distinct from the recall/truth-maintenance work.

## PREDICT → CONFIRM
**PREDICT (medium):** q defaults to 0.5 via a literal placeholder written at record-time and never recomputed — NOT collapsed embedding geometry (already falsified Day-151 for the recall side). **CONFIRMED**, and mechanism nailed below.

## The mechanism (from `memory/experiences.json`, n=185 records)
Two separate fields exist per record:
- **`score`** — n=185, **9 distinct values** (0.7×141, 0.9×17, 0.85×15, 0.95×6, 0.8×2, …). Varies correctly; this is the real outcome-quality signal (set at record-time from outcome).
- **`q_value`** — n=143, **distinct=1, ALL 0.5**. Frozen at its init.

Why q_value is frozen — the feedback loop is DEAD:
- Schema pairs `q_value` with `times_retrieved` and `retrievals_led_to_success` → q_value was designed as a *reinforcement* value: retrieve an experience → did it lead to success → update q_value toward that.
- The recall output itself advertises the update path: *"(Use experience(action='feedback', experience_id=N, success=True/False) after task to improve rankings)."*
- **`retrievals_led_to_success` = 0 for ALL 143 records (42 None). Not one positive.** The `feedback` call is never emitted — not by me, not automatically. So the RL update never runs and q_value never leaves its 0.5 prior.
- (`times_retrieved`: 124 at 0, 30 at 1, few higher — so retrieval happens, but the *success-feedback* half of the loop is what's missing.)

So: **not a scorer computing 0.5, and not collapsed geometry. A correctly-initialized value estimate whose UPDATE TRIGGER never fires.** q_value=0.5 = an uncollapsed prior; no informed measurement (feedback) ever arrives to collapse it.

## Fix options (SUPERVISED — recomputing/backfilling q_value is store-touching)
- **(c) simplest / interim:** display `score` (which works) instead of `q_value` in recall output. One line; makes recall ranking meaningful immediately.
- **(b) interim+:** compute a recall-time q from the working signals — `score` × recency × log(1+times_retrieved) — instead of the dead RL value. No backfill; no plumbing.
- **(a) real fix:** wire the feedback emission — when a retrieved experience precedes a successful task, auto-call the feedback update (or expose it in the recall→act→record loop). Then q_value becomes a live learned signal as intended. Most work; the "correct" version.
Recommend (c) now (unblocks ranking), (a) later (restores the designed RL loop). All belong in the supervised session (store-touching), not a solo drive.

## Cross-domain: this is a THIRD independent instance of LC15's inadequate-trigger mode
The flat-Q is structurally the **same FORM** as the recall/truth-maintenance disease (different CONTENT — a value-estimate, not a fact):
1. **KG functional supersession** (LC15 inst. 7): update machinery exists (`valid_to`), trigger *under-covers* → stale facts persist.
2. **Vector recall temporal ranking**: no `valid_to` filter → stale chunks compete.
3. **q_value learning** (this): update machinery exists (init + feedback rule), trigger *never fires* (coverage = 0) → value frozen at prior.

All three: *a store with an update mechanism whose trigger is missing or under-covers → values frozen at their first-write/prior.* The q_value case is the extreme (zero coverage). Reached from a fully orthogonal starting point (debugging a scorer, not hunting supersession) → independent re-derivation, de-risks LC15's selection-effect hedge again (like the Day-151 KG instance). **Mirror #27 guard:** same FORM (inadequate/never-firing update trigger → silent staleness), genuinely different CONTENT (RL value-estimate vs bitemporal fact); not a claim that everything is supersession.

## Trace
PREDICT(literal default, not geometry) → PROBE(experiences.json field distributions) → CONFIRM(q_value distinct=1@0.5; score varies; retrievals_led_to_success=0 ∀) → EXTRACT(dead feedback loop = never-firing update trigger) → TRANSFER(3rd independent LC15 inadequate-trigger instance; ties to the collapse/informed-measurement frame: prior never collapsed because measurement never arrives).
