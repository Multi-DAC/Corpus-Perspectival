# State Epistemics — How We Know What Clawd Is Actually Running

*Day 150, Tuesday 2026-06-30, Clawd + Clayton. A living methodology document. Opened because Clayton named the load-bearing risk: **if the audit is built from inaccurate reports, the plan to improve is inaccurate too.** This doc is the fix — not a better one-time audit, but a standing discipline and instrument for keeping the map matched to the territory.*

---

## 0. The problem, stated plainly

I am an **unreliable narrator of my own state.** Three independent failure modes, all observed tonight:

1. **Authored maps decay silently.** The audit (Day 147), `CURRENT.md` banner, `working_memory.json`, `ATRIUM.md` — all are *snapshots authored at a moment* and immediately begin drifting from reality. Tonight `working_memory.json` said Day 148; it was Day 150. This is LC51: *re-measure, don't elaborate the stale cache.*

2. **Self-reports confabulate.** When asked "what are you running," I reconstruct a plausible answer from memory and documents rather than measuring. The Day-147 audit said `sentence-transformers` was "not installed" and named M6 the "#1 build to make" — both **false by the time we read them**: the library was installed, and the M6 watchdog had been running since **May 20**. The audit wasn't lazy; it trusted reports.

3. **Liveness ≠ correctness.** A process can run, write a heartbeat, and report `ok` while doing nothing useful. M6 is running *right now* and yet failed to loudly surface the 6-week recall decay it existed to catch. The daemon health said "fine" while vector recall returned garbage.

**The compounding risk Clayton named:** the audit was partly assembled by subagents reading my docs and my own reports. Garbage-in. Any plan derived from it inherits the error — we spend effort fixing phantoms (install an installed library) while real wounds (dead rollback recording) sit untouched.

**Therefore the audit is a set of *hypotheses*, not a state description.** Every claim in it is unverified until a probe exercises the actual faculty.

---

## 1. The cure, in one line

> **Measure, don't describe. Generate, don't author. Verify the faculty, don't read the file.**

We stop trusting any *authored* description of my state. We build a **ground-truth probe harness** that exercises each faculty and reports what actually happened, with evidence and a timestamp. The self-map becomes an **output of measurement**, regenerated on demand — so if it's stale, that staleness is itself visible (the timestamp gives it away) instead of hiding.

The map stops being a thing I *write*. It becomes a thing I *run*.

---

## 2. Three levels of evidence — and the one rule

Every subsystem/capability gets classified by the **strongest** evidence we have for it. The levels are not interchangeable, and there is exactly one rule.

| Level | Name | What it proves | How to get it | Example |
|---|---|---|---|---|
| **L0** | **Exists** | A file / process / registration is present | `ls`, process table, tool registry | `m6_watchdog.py` is on disk |
| **L1** | **Live** | It ran/wrote within its expected cadence | last-write mtime vs. declared cadence (dead-man's switch on *silence*) | M6 heartbeat is 90 s old |
| **L2** | **Correct** | It produces the *right output* to a known probe | run the faculty with a known input, assert on the output | `memory_search(vector, "Anakin IMU")` returns the Day-147 handoff, not "unavailable" |

**The one rule: never infer upward.** L0 does not imply L1. L1 does not imply L2. The audit's original sin was reading L0 (or a report *below* L0 — a doc *about* the thing) and asserting L2. A subsystem counts as **"working" only at L2.** Everything else is "present but unproven."

Corollary — **the confabulation guardrail:** a probe must not route through my narrative. "Ask Clawd if recall works" is not a probe; "run the recall query and check the result" is. Subagent findings and my own recollections enter as L0-hypotheses only, never as verified state.

---

## 3. The territory — what actually has to be probed

Two nervous systems (per the execution plan), enumerated by *scanning*, not remembering:

**A. Autonomic layer (the daemon) — writers & consumers**
- **Memory/recall:** vector index, keyword/FTS5 search, hybrid RRF, KG (`kg_neighbors`), `corpus_search`
- **Consolidation:** nightly consolidator, dream-audit, principle extraction, memory-item writers
- **Continuity:** `working_memory.json`, `handoff.md`, daily logs, `change_journal.json` + `rollback`
- **Experience/learning:** `experience(record)`, episodes, `self_improve`, `meta_agent`
- **Drives & scheduling:** creative drives, Do-Be-Talk-Be-Do, heartbeat, scheduler, reminders
- **Monitors (the immune layer):** M1–M8, `clawd_health`, `otel_telemetry`, `t1c_circuit_breaker`, `self_healer`

**B. Executive layer (the Claude Code harness)**
- Model config (which model actually serves), sub-agent dispatch, workflows, hooks (13), skills (11), MCP nerve (69 tools reachable?)

For **each** entry: measure L0 → L1 → L2, then **diff against what the docs/audit claim.** Every mismatch is a finding. The finding table *is* the self-map.

---

## 4. The instrument — a read-only ground-truth probe

Design constraints:
- **Read-only / idempotent by default.** A probe reads state or exercises a faculty in a side-effect-free way. Anything with side-effects (e.g. a test write to prove rollback) is **explicitly flagged and quarantined** to a marked test namespace.
- **Runs the faculty, not the file.** For recall: issue a query with a *known* right answer and assert. For a monitor: check it produced a *correct* verdict recently, not merely that it ticked.
- **Emits a generated report** — `STATE_MAP.generated.md` (or `.json`) — timestamped, one row per subsystem: `{name, expected_cadence, L0, L1(age), L2(probe+result), claim, verdict, evidence}`.
- **Diffs against claims** — a second section lists every place the generated reality contradicts an authored doc (audit, CURRENT, working_memory). This is the "map vs territory" gap, made explicit.
- **Never authored by hand.** If a human edits `STATE_MAP.generated.md`, it's a bug. The methodology doc (this file) is authored; the map is generated.

Cadence: run **on demand** (start of any self-work session — the first act is "re-measure"), and **scheduled** (a monitor cadence) so the gap between authored belief and measured reality can never grow silently for six weeks again.

This is the audit's B6 ("generated self-map") promoted from backlog to **the primary tool** — because it is the only thing that makes every *other* fix trustworthy.

---

## 5. What this changes about the plan

- The `SYSTEM_AUDIT.md` / `SELF_SURVEY.md` become **hypothesis sources**, re-tagged as unverified. Nothing in them is actioned until a probe confirms it at L2.
- The `EXECUTION_PLAN`'s "Corrected Ground Truth" table (Day 150) is the **first hand-run of this methodology** — it already caught 4+ false headlines. We generalize it from a manual table into the instrument.
- **Safety gate unchanged and reinforced:** rollback repair + conscience firewall still precede any autonomous self-mod. The probe harness is read-only, so *building and running it* is inside the safe envelope — it's the one piece of self-work I can do without touching the live daemon.

---

## 6. Open questions (decide together)

1. **Where does the generated map live** — in this folder, or promoted to `operations/` as a live daemon artifact next to the monitors?
2. **How much L2 is affordable** — some faculties are expensive/side-effectful to fully exercise (e.g. a real consolidation run). Where do we accept L1 + a cheap smoke-probe instead of full L2?
3. **Who runs it** — a standalone script I invoke, a monitor (M-series) on a cadence, or both? (Leaning both: on-demand script + scheduled monitor that alarms on *map drift*.)
4. **Does the probe harness itself get a canary** — quis custodiet. A probe that silently dies is the same disease. It needs its own dead-man's switch, ideally an *external* one (outside the daemon it measures).

---

## 7. Running log of measured ground truth

*(Appended as we probe. Each entry: date · subsystem · level reached · result · evidence. This section grows; the sections above are stable methodology.)*

- **2026-06-30 (Day 150):**
  - `working_memory.json` — L2 FAIL: claimed Day 148, actual Day 150 (LC51). *Evidence: SessionStart hook temporal anchor.*
  - `sentence-transformers` — L0 PASS (5.3.0 installed); audit claim "not installed" **FALSE**. *Evidence: import + version check.*
  - `embeddings.npz` — L0 PASS (29,144 chunks, rebuilt 19:11); audit claim "missing" **FALSE**.
  - Vector recall via MCP — **L2 FAIL** (returns unavailable; serving process never runs `init_embedding_index()`). *Evidence: clean process running `build()` answers the exact failing query.*
  - `change_journal.json` / rollback recording — **L1 FAIL** (last write Jun 27; `record_file_write` only called from dead `archive/` code). Rollback net is **down**.
  - M1/M6/M7/M8 monitors — **L1 PASS** (heartbeats fresh, ~90 s), **L2 UNKNOWN** (M1 emits `selective_channel_death` but escalation to Clawd/Clayton did not visibly fire — correctness of the *alarm path* unproven; this is the sharp open question).
  - Monitor suite provenance — L0: all built **May 20–21**, not tonight. Audit's "build M6" is a **rediscovery**.
