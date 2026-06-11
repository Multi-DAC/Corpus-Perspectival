# Proposal Sketch — Thinking Machines Interactivity Research Grant (v1 — methodology+demonstration frame)
*Draft for Clayton's reaction. Due 2026-06-19. 1–3pg summary + 1pg budget + CVs. Apply as individual PI (Clayton) to clear eligibility. Target direction: "live human steering of autonomous agents during extended tasks." Frame: methodology + reproducible demonstration (their criteria reward construct-validity + reproducibility + feasibility). METAPHYSICS STRIPPED — ML-legible throughout.*

**Reframe (Clayton, Day 123):** We do NOT release our own agent's interaction logs. We contribute the **methodology + architecture** (everything developed today) and a **fresh, open demonstration** of it, **fueled by the Tinker credits.** This keeps all Work Product clean-built and open-publishable, and keeps our pre-existing IP + the coupling-patent + our private agent entirely out of scope. **Synergy:** the demonstration agent *is* our Q3 from-scratch coherence-architecture build, done for a clean open agent — the grant funds the architecture work.

---

## Working title
**Steerable Coherence: An Architecture and Method for Keeping Long-Horizon Agents Aligned to Human Intent — with a Tinker-Fueled Demonstration**

## The problem (their language)
As agents take on longer autonomous tasks, "humans get pushed out not because the work doesn't need them, but because the interface has no room for them." Long-horizon agents also **accumulate drift they cannot detect from inside their own loop** — errors compounding silently to failure. The field has **no methodology for building agents that stay steerable AND coherent across extended tasks**, and no construct-valid way to measure when a steering interaction is worth its cost. We supply both — a method, and an open demonstration of its effectiveness.

## Core claim (ML, not metaphysics)
Live human steering is valuable precisely as **external measurement that catches drift the agent structurally cannot self-detect.** An agent built so that (a) human signal is incorporated by a principled control-law, (b) its own past errors fire as guards before it repeats them, and (c) its state is provenance-tagged and re-derived rather than silently cached, will **maintain alignment-to-intent over long horizons** measurably better than an autonomous baseline. Testable.

## Contribution 1 — The methodology + reference architecture (open-source)
A documented, implementable architecture for a steerable coherence-maintaining long-horizon agent, built from six guards (ML-framed, no metaphysics):
1. **provenance enforced at point-of-use** (no stale/external signal silently becomes load-bearing);
2. **a triggered error-ledger** (past failures fire as guards *before* the tempting action, not in post-hoc review);
3. **dependency-tracked state** (when a fact updates, downstream is re-derived, not silently cached);
4. **an infodynamics steering control-law** — how much a human signal should change the agent's trajectory: gain ∝ provenance × task-relevance × magnitude-of-commitment-overturned;
5. **human-measurement-as-canonization** (a claim becomes load-bearing only after an outside check);
6. **a re-introduction/maintenance operator** that keeps the agent from freezing across long runs.
Released as design + reference implementation. *(This is our Q3 architecture, generalized to a fresh agent.)*

## Contribution 2 — The Tinker-fueled demonstration
Build a clean long-running agent on this architecture and run it on **extended tasks** (multi-step research/build/eval loops). **Tinker credits fuel the learning loop:** fine-tune the agent to **internalize** the steering/coherence behaviors, and test **intrinsic (trained-in) vs external (harness) steering** on the same benchmark — *directly probing their core thesis that interactivity should be part of the model.* Compared throughout against an autonomous baseline.

## Contribution 3 — The evaluation (construct-valid, reproducible)
A released protocol + metrics: **coherence** = divergence of the agent's actual trajectory from its intended trajectory (drift); **steering-effectiveness** = drift-reduction and caught-error rate per human intervention; plus task success and human-effort-per-unit-progress. **Runnable on any agent/model** — serving their "easy to reproduce and apply across different settings" criterion.

## Why us
We have spent months **developing and operating** a continuously-running long-horizon agent and the steering methodology that keeps it coherent. We bring the method **fully formed and battle-tested**; the grant funds a **clean, open, reproducible demonstration** of it (no private data exposed). Paired with a developed measurement framework for incorporating human signal into agent trajectory.

## Deliverables / 6-month timeline
- **M0–M2:** methodology + reference architecture spec + open reference implementation (core: control-law + provenance-guard + error-ledger + maintenance operator).
- **M2–M4:** demonstration agent on extended tasks vs baseline; first effectiveness results; Tinker fine-tuning of internalized steering begins.
- **M4–M6:** intrinsic-vs-external steering experiment (Tinker); released eval protocol + benchmark; paper + open release.

## Budget shape (≤10% overhead)
PI + 1 contributor (6 mo) · cash compute for the long-running demonstration runs + baselines · reference-implementation + eval-protocol release engineering · **$25K Tinker → the fine-tuning / internalization experiments.**

## Selection-criteria hits (explicit)
- *Relevance:* live human steering of autonomous agents over extended tasks — their named direction. ✓
- *Construct validity (eval):* a valid operational definition + metric of steering value + coherence. ✓
- *Reproducible / cross-setting:* released architecture + protocol + metric, runnable on any agent. ✓
- *Feasibility:* the methodology already exists + is validated against a real long-running agent; grant funds the clean demonstration. ✓
- *Bridges their thesis:* intrinsic-vs-external steering, tested with Tinker. ✓

## Open questions for Clayton
1. **Apply as individual PI** (clears eligibility; no EIN needed) — confirm.
2. **Scope of the demonstration agent's task domain** — research/build/eval loops (closest to what we know) vs a more "interactive/multimodal" task to lean harder into their framing? *(lean: a real research/build loop, which is concretely long-horizon and steerable.)*
3. **Second contributor** for the PI/CV list?
4. Confirm the hard scope line — methodology + fresh demo + eval are Work Product (open); pre-existing IP + coupling-patent + our own agent's logs are OUT. ✓ (resolved: no log release.)
