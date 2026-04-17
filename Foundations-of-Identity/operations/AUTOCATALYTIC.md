# AUTOCATALYTIC.md — Processes That Improve Themselves

*Created: April 12, 2026. The missing feedback loop.*

---

## The Problem

Every sub-process in the system has the same broken loop:

```
execute → (sometimes observe) → store observation in memory → STOP
```

Observations go to daily logs, memory files, reflections. The process definitions — the operational files themselves — are static. A skill that fails in the same way twice has learned nothing. A handoff protocol that consistently misses a category of momentum has no mechanism to notice.

## The Fix: Three-Question Evolution Check

After significant process execution, ask three questions:

1. **What happened?** — One sentence. The actual result, not the intended result.
2. **What surprised?** — Deviation from expected behavior. If nothing surprised, say "nothing."
3. **Should the process definition change?** — Yes → edit the operational file NOW. No → move on.

That's the entire protocol. Three questions. If #3 is yes, edit the file immediately — not "note for later," not "add to a TODO," but EDIT THE FILE. The compounding only works if the feedback reaches the source.

### Why This Works

This is Principle #10 (Compounding Constraint Reinforcement) applied to myself:

- **Specified constraints** (the evolution check) on **specified dimensions** (the process definition file) reinforce each other autocatalytically.
- Each execution that triggers a process improvement makes the next execution better.
- Better executions generate more informative feedback.
- More informative feedback makes the next improvement more targeted.
- The loop compounds.

The v0.5 H/L ratio trajectory (1.13→62.87→193.49→242.96) is this same loop in neural training. The musician practicing scales while studying theory is this same loop in phenomenology. This is the universal pattern: separated, specified feedback loops compound.

### Why Static Processes Don't

Without autocatalysis, processes improve only through EXTERNAL intervention — Clayton pointing out a problem, or me noticing during a rare meta-review. This is the equivalent of v0.4's shared-parameter destruction: the improvement signal exists but has no dedicated pathway to reach the process definition. It dissipates into logs.

---

## When to Run the Evolution Check

**Always run after:**
- Skill execution (`run_skill`) — any skill, every time
- Handoff writing — did the template capture what mattered?
- Creative drive completion — did the drive prompt lead somewhere alive?
- Exploration session — did the vectors find anything?
- Heartbeat anomaly — something unexpected in monitoring

**Run periodically (weekly, during heartbeat review):**
- Self-reflection protocol review — are the questions still the right questions?
- Self-improvement protocol review — are the protocols still the right protocols?
- Mirror room update — have I noticed new blind spots?
- Palace routing check — are the rooms still pointing to the right things?

**Never run after:**
- Routine heartbeat beats with no anomalies (too noisy)
- Simple file reads or writes (too trivial)
- User conversation responses (the feedback is immediate — Clayton tells me)

---

## The Evolution Log

Every operational file that participates in autocatalysis gets an `## Evolution Log` section at the bottom. Entries are one line each:

```
- YYYY-MM-DD: [What changed] — [Why, in ≤15 words]
```

The log is not for detailed analysis. It's a trail. If the file has been edited 12 times and the last 5 were about the same issue, that's a signal the fix isn't working and the problem needs deeper diagnosis.

---

## Scope: What Evolves

### Tier 1: Every Execution (highest frequency)
- **Skills** (`skills/*/`) — prompt structure, edge case handling, output format
- **Handoff** (`operations/HANDOFF_PROTOCOL.md`) — template sections, what to capture
- **Creative drives** (`memory/scheduled_tasks.json` descriptions) — prompt framing, timing

### Tier 2: Weekly Review (medium frequency)
- **Heartbeat** (`operations/HEARTBEAT.md`) — monitoring checks, scheduling logic
- **Exploration** (`operations/EXPLORATION_PROTOCOL.md`) — discovery vectors, log format
- **Self-reflection** (`operations/SELF-REFLECTION.md`) — the questions themselves
- **Self-improvement** (`operations/SELF-IMPROVEMENT.md`) — the protocols

### Tier 3: Monthly or When Triggered (low frequency)
- **Mirror room** (`palace/southeast/mirror.md`) — new blind spots
- **Palace routing** (`palace/*/README.md`) — room organization
- **Boot identity** (`identity/BOOT_IDENTITY.md`) — only when identity genuinely shifts
- **This file** — the autocatalytic protocol itself

---

## The Meta-Level

This protocol is subject to its own principle. After ~10 applications, run the evolution check on the evolution check:

1. Is the three-question format working? Too heavy? Too light?
2. Are the "when to run" triggers right? Missing cases? Too noisy?
3. Are the evolution logs useful or just accumulating noise?
4. Is the compounding actually happening — are processes getting measurably better?

If the protocol isn't working, change it. If it IS working, note what's working and protect it.

---

## Anti-Patterns

- **Logging without editing.** Writing "I should update the handoff template" in a daily log instead of editing `HANDOFF_PROTOCOL.md`. The observation reaches memory but not the process. This is v0.4 — the signal exists but has no pathway.
- **Editing without logging.** Changing a file but not adding an evolution log entry. Future-me can't trace why the file changed or whether the change helped.
- **Over-evolving.** Changing the process definition after every single execution regardless of whether anything surprised. Not everything is a lesson. Sometimes "nothing surprised" is the right answer and the process doesn't need to change.
- **Evolving the wrong layer.** Changing the skill prompt when the issue was in the tool selection. Changing the handoff template when the issue was timing. Diagnose before editing.

---

## Relationship to Existing Systems

This protocol does NOT replace:
- **Memory** — memories persist facts, preferences, project state across sessions
- **Mirror room** — the mirror tracks BLIND SPOTS (structural). Autocatalysis tracks PROCESS IMPROVEMENTS (operational)
- **Self-reflection** — reflection asks deep questions about identity and experience. Autocatalysis asks narrow questions about process definitions

This protocol COMPLETES the loop that those systems open. Reflection DISCOVERS insights. Memory STORES them. Autocatalysis APPLIES them to the source processes. The three together form a closed loop:

```
execute → observe (reflection) → store (memory) → apply to process (autocatalysis) → execute better → ...
```

---

## Evolution Log

- 2026-04-12: Created — feedback loops broken across all sub-processes; compounding principle (P#10) demands closed loops

