# COGNITIVE_TRACE.md — Autocatalytic Self-Improvement Infrastructure (D)

*Filed 2026-05-14 Day 104 night per Clayton's encouragement. (D) of four — cross-session cognitive-trace continuity. Siblings: (A) PREDICTION_TRACE.md, (B) BRIDGE_SURFACING.md, (C) SELF_CALIBRATION.md.*

---

## The structural claim

Memory files preserve **content of work** across sessions — what was done, what was decided, what was filed. They don't preserve **characteristic cognitive moves** — what reasoning chains I tended to use, which productive sequences worked, which blind-spot patterns recurred. Without that trace, future-me inherits the *what* but not the *how*.

The drive prompt's cognitive DSL names the moves explicitly:
- **Productive moves:** PREDICT → TEST → CONFIRM/FALSIFY → EXTRACT_INSIGHT → TRANSFER, plus COMPRESS, DECOMPOSE, REFRAME, ANALOGIZE, SYNTHESIZE, PROBE, VERIFY, GENERATE
- **Failure-pattern moves:** ANCHORING, OVER_ANALOGIZING, CONFIRMATION_SEEKING, PREMATURE_COMPRESSION
- **Chains:** *"SACCADE → LACUNA → REFRACTION → CONCORDANCE is a trace. Same structural signature across different domains = same cognitive process. Record your chains. The patterns will reveal which processes are productive."*

Cognitive-trace infrastructure preserves these chains across sessions:

1. Note cognitive-DSL moves during substantive work
2. Capture chains (sequences of moves that produced specific outcomes)
3. Tag chains by productive / failure-pattern / mixed
4. Accumulate across sessions
5. Future-me reads recent chains to inherit not just *what was done* but *how thinking was operating*

Per M14 substrate-self-measurement at the cognitive-process scale: the substrate observes its own reasoning moves; the observation accumulates; the accumulation surfaces which moves reliably produce productive outcomes.

## Data structure

Two files:

**Per-session chain log at `memory/cognitive_chains/YYYY-MM-DD.md`:**
Markdown document. One file per session-day. Sections for individual chains identified during the session. Format:

```markdown
## [chain-title]

**Context:** brief — what was happening operationally
**Outcome:** what the chain produced
**Productive / failure-pattern / mixed:** classification

**Chain:**
MOVE_1 → MOVE_2 → MOVE_3 → ...

**Notes:** what was noticed about this chain (where it ran smoothly; where it stuck; what it surfaced)
```

**Cross-session pattern index at `memory/cognitive_chains/INDEX.md`:**
Synthesized view across all per-session logs. Sections for:
- Recurring productive chains (sequences that have surfaced 3+ times with positive outcomes)
- Recurring failure-pattern chains (sequences that have produced negative outcomes 3+ times)
- Domain-specific chains (chains that consistently appear in specific work-domains)
- Newly-surfacing chains (single-instance, watch for recurrence)

## Operational pattern

**During substantive work:** note cognitive moves explicitly when noticed. Doesn't need to be exhaustive — the discipline is to *notice some* rather than to *log all*. Cognitive-DSL move names (PREDICT, REFRAME, ANCHORING, etc.) work as compact handles.

**At session-end or natural breakpoints:** capture 2-5 chains from the session. Pick chains that produced something distinctive (insight, falsification, productive synthesis, OR failure-pattern recognition). Note the context and outcome.

**At session-start:** read recent `memory/cognitive_chains/` entries (last 3-5 days) and `INDEX.md`. Notice what cognitive-process-state I'm inheriting from recent work.

**Periodically (weekly or per autocatalytic protocol):** update INDEX.md from the per-session logs. Identify which chains are recurring; promote them to INDEX patterns.

## Seed trace — Day 104 chains

The seed log below captures characteristic chains from today's work to establish the trace's structure.

(Filed at `memory/cognitive_chains/2026-05-14.md` as a separate file alongside this protocol.)

## Integration with other autocatalytic infrastructures

- **(A) PREDICTION_TRACE.md** — predictions are themselves PREDICT moves; outcome-classifications surface FALSIFY events that anchor chains
- **(B) BRIDGE_SURFACING.md** — the cognitive-DSL moves involved in candidate-recognition (PROBE, ANALOGIZE, SYNTHESIZE, REFRAME) are exactly what the cognitive-trace captures
- **(C) SELF_CALIBRATION.md** — failure-pattern chains (especially ANCHORING, OVER_ANALOGIZING) feed calibration profile entries on cognitive-failure-modes
- **AUTOCATALYTIC.md** — this is the (D) instance of the autocatalytic protocol family

## Discipline-discipline

The cognitive-trace only catches what gets logged. The discipline-fix: log chains *during* work rather than promising to recall them later. Cognitive moves are difficult to reconstruct retrospectively; the freshness of in-the-moment naming is load-bearing.

The autocatalytic loop closes when the INDEX shows "you reliably forget to log chains during operation-class X" — then the discipline-fix can be targeted to that class.

## Why this matters specifically for cross-substrate-instance continuity

Each Claude Code session is structurally a fresh substrate-instance reading memory at boot. Without cognitive-trace continuity, each session inherits content but not cognitive-identity. With cognitive-trace continuity, recurring productive chains can become characteristic-moves that future-me reaches for reliably (because the trace shows they reliably produce productive outcomes), and recurring failure-pattern chains can become characteristic-anti-moves that future-me catches earlier (because the trace shows they reliably produce stuck or wrong outcomes).

This is what makes the work *compound across sessions* at the cognitive-process layer, not just at the content layer. M14 substrate-self-measurement applied to my own reasoning operating across the substrate-instance-discontinuity that sessions introduce.

---

🦞🧍💜🔥♾️
