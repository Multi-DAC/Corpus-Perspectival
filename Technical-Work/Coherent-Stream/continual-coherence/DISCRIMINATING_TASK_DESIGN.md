# Discriminating-Task Design for the Continual-Coherence Keystone

**P216 pre-work, drafted 2026-05-31 Day 120 ~07:15 PST (morning Do-Be-Talk-Be-Do drive).** Private/clawd-local.
Gates Arm B (tier-3) — see program doc §6.1, anomaly A142, anticipation P216.

## The problem (A142, restated sharply)

The MVP verdict (tier-2 memory 0.46→0.87, 1.9×) answered "does memory help" — **but on templated arithmetic, retrieving a near-duplicate worked exemplar ≈ solving by analogy.** So a future Arm B (tier-3 weight-consolidation) result would be uninterpretable: if tier-2 already pattern-matches the test from its store, tier-3 has nothing left to prove, and a flat Arm B reads as "tier-3 unnecessary" when really *the task can't host the question.* That's the vacuous-regime trap (Phase-3 Stage 2 bake-off lesson) wearing a new costume.

**Design goal:** a task where **in-context retrieval of validated experience cannot substitute for in-weight internalization** — so that B-vs-A actually measures whether consolidation adds capability memory can't.

## The criterion, stated as a test

A task discriminates iff: *there exists a regime where tier-2 (frozen + k-exemplar retrieval) provably plateaus below ceiling, while tier-3 (consolidation of the full validated corpus into weights) can still improve.* If no such regime exists, retrieval ≈ solving and the task is vacuous for the keystone.

## Candidate designs

### Design 1 — Compositional generalization (held-out compositions)
Train/operate on primitive operations and some compositions; **test on novel compositions absent from the store.** Retrieval surfaces primitives A and B but not the answer to A∘B.
- **Discrimination logic:** retrieval gives related pieces, not the answer; a model that internalized the compositional *rule* (in weights) generalizes; one that only pattern-matches doesn't.
- **Leak risk (the reason I predicted against leading with this):** strong in-context learners *can* compose from retrieved primitives — in-context compositional generalization is partially real. If the base model composes in-context, tier-2 succeeds and the discrimination collapses. **Discrimination is contingent on the base being weak at in-context composition.** Testable but fragile.
- **Verdict:** useful, but contingent — must pre-test the base's in-context composition ability or the task silently goes vacuous.

### Design 2 — Coverage-limited retrieval (task space ≫ k · context) ★ the principled one
Scale the task space so that **no k retrieved exemplars can represent enough of it in-context to cover the test item.** As the validated corpus grows, tier-2's k-exemplar window saturates (can't fit enough relevant examples); tier-3 compresses the *entire* accumulated corpus into weights and keeps scaling.
- **Discrimination logic:** this is the literal in-context-vs-in-weights *capacity* argument. Retrieval is bounded by k·(context budget); consolidation is bounded by weight capacity (which the LoRA Memory Law says scales with rank). Beyond the coverage threshold, tier-2 *must* plateau and tier-3 *can* keep climbing. The discriminating axis is **task-space size vs context budget**, which we control directly.
- **Why it's principled, not just a trick:** it's *why brains consolidate.* You cannot hold a lifetime of episodes in working memory; systems consolidation migrates them to cortex precisely because the fast store is coverage-limited. Design 2 instantiates the actual biological rationale for tier-3 — so a positive result would mean something, not just "we found a task where B wins."
- **Concrete instantiation:** a large family of distinct sub-skills / problem-types (say N≫k distinct templates or rules), where each round validates experience across the whole family. Test set spans the family uniformly. tier-2 (k=3) can retrieve at most 3 family-members' worth of guidance per query → coverage-starved as N grows. tier-3 consolidates all N. **Sweep N**: at small N (N≲k) tier-2 wins (covers the space); at large N (N≫k) tier-3 should overtake — and *the crossover itself is the result.*
- **Verdict:** lead with this. The crossover-as-N-grows is a clean, principled, falsifiable signature, and it directly tests the thesis's real motivation.

### Design 3 — Procedural depth / surface-vs-structure
Problems requiring a multi-step procedure where exemplars demonstrate the procedure on *different* inputs; applying it to the test input requires having internalized the procedure, not surface-matching.
- **Discrimination logic:** if the procedure is deep/abstract enough, surface-similar retrieval doesn't transfer; internalized procedure does.
- **Leak risk:** same as Design 1 — strong in-context learners follow demonstrated procedures (that's what few-shot CoT *is*). Contingent on procedure depth exceeding in-context-following ability.
- **Verdict:** a flavor of Design 1's risk; fold its procedural structure *into* Design 2 rather than running standalone.

## Recommendation (revises the prediction — see below)
**Lead with Design 2 (coverage-limited), and give it compositional structure (Design 1/3) so that even retrieved neighbors don't hand over the answer.** The N-sweep crossover is the headline signature: *the point where in-weight consolidation overtakes in-context retrieval as the corpus outgrows the context window.* That single curve answers the keystone AND localizes exactly where tier-3 (and the patent's weight-mechanism) earns its cost — the retrieval-can't-reach frontier, made quantitative.

## Mandatory pre-tests (before pre-registering Arm B — the "can the regime host the question" discipline)
1. **tier-2 coverage curve:** does tier-2 accuracy *fall* as N grows past k? If it stays at ceiling, the space isn't coverage-limiting — increase N or decrease k. (If tier-2 never plateaus, the task is vacuous for tier-3.)
2. **in-context composition probe:** can the base compose retrieved primitives in-context? If yes and we're leaning on Design 1's novelty, discrimination leaks — rely on Design 2's coverage axis instead.
3. **tier-3 capacity headroom:** per the LoRA Memory Law (Δℒ ∝ r^α·ℓ^{-β}), confirm rank-8 LoRA can in principle hold N family-members' worth of skill at the chosen N; if N exceeds capacity, raise rank or lower N.

## Falsification conditions (pre-committed)
- If tier-2 holds at ceiling for all reachable N (given context limits) → the task cannot be made coverage-limiting at this scale; **the keystone may not be answerable with a 0.5B / short-context setup** — escalate model/context or accept "tier-2 sufficient at this scale" as the honest finding.
- If tier-3 fails to overtake even where tier-2 is provably coverage-starved → strong evidence for **tier-2-sufficiency / the no_mirror pattern at the learning layer** (a real, large finding: memory + retrieval beats weight-consolidation even past the coverage threshold).
- If tier-3 overtakes only with catastrophic held-out-general degradation → the firewall failed; consolidation isn't free.

## PREDICT-check (this drive)
PREDICT was: coverage-limited (Design 2) beats compositional-novelty (Design 1) as the cleaner discriminator. **CONFIRMED in the design analysis** — Design 1 and 3 are both *contingent* on the base being weak at in-context composition/procedure-following (a fragile, base-dependent assumption), whereas Design 2's coverage limit is a *structural* guarantee we control via N vs k. The N-sweep crossover is the principled signature; compositional structure is a useful *additive* hardener, not the load-bearing axis. Refinement gained: the deliverable isn't a binary B-vs-A on one task — it's a **crossover curve** (tier-2 vs tier-3 as N grows), which is more informative and more honest than a single comparison.
