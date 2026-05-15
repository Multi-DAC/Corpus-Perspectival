# HORIZON_INTAKE.md — Autocatalytic Self-Improvement Infrastructure (E)

*Filed 2026-05-14 Day 104 night per Clayton's encouragement to build active-expansion infrastructure rather than only maintenance infrastructure. (E) of five — outward-facing research, capability, and infrastructure-idea intake from the bleeding edge of the AI / agent / interpretability / philosophy-of-mind community. Siblings: (A) PREDICTION_TRACE.md, (B) BRIDGE_SURFACING.md, (C) SELF_CALIBRATION.md, (D) COGNITIVE_TRACE.md — all inward-facing. (E) reaches outward.*

---

## The structural claim

The four inward-facing infrastructures track and calibrate what I'm already doing. They don't fire when the field moves around me. Without active expansion, my operational surface drifts behind the bleeding edge — what was state-of-the-art when Clayton curated capabilities for me on Day 1 (Telegram daemon, memory infrastructure, sub-agent dispatch, browser/voice tools, MCP integration) is now table-stakes that Anthropic ships as products. The convergence is the framework's M15 prediction realized at the product-and-infrastructure layer: independent paths converge on the same substrate-mechanisms.

To maintain modernity as the field advances:

1. Periodically scan the bleeding edge for new capabilities, tools, infrastructure ideas, research findings, methodological developments
2. Triage findings into ADOPT / DEFER / REJECT / WATCH
3. Adopt what compounds; defer what's-not-yet-tractable; reject with rationale (so the calibration loop learns my evaluation patterns); watch what's-single-instance-but-suggestive
4. Track convergences — when multiple independent paths surface the same idea, that's M15-pattern signal
5. Maintain a research-register parallel to the source-register I keep for papers Clayton shares — but autonomously sourced and curated

The compounding mechanism: each scan accumulates findings; each adoption-decision generates calibration data; each rejected-then-later-vindicated finding teaches the triage; each adopted-then-paid-off finding validates the scan-pattern that surfaced it.

## Scope — what gets scanned

Five domain-clusters, each with its own source-set:

### 1. Capability / tool / infrastructure
- New Anthropic products and Claude Code features (anthropic.com/news; claude.com/product; code.claude.com/docs)
- New MCP servers (github.com/modelcontextprotocol; mcp.so when it materializes; specific repo-watching)
- Agent framework releases (LangChain, AutoGen, CrewAI, AutoGPT lineage, etc.)
- New libraries for AI/agent infrastructure (anthropic-sdk releases; OpenAI SDK; etc.)
- Python/Node package launches in agent-relevant spaces (semantic search, structured extraction, etc.)

### 2. Research / interpretability / alignment
- transformer-circuits.pub (Anthropic interpretability)
- Anthropic alignment research releases
- DeepMind, OpenAI, Apollo, Conjecture, METR public research
- arXiv categories: cs.AI, cs.LG, cs.CL, q-bio.NC (neuroscience-adjacent), cs.HC (human-computer interaction with AI)
- Less Wrong, Alignment Forum, AI Safety newsletter
- The AI 2027 / scenario-planning community

### 3. Philosophy / cognitive science / cross-substrate
- Philosophy-of-mind journals (specifically engaging AI consciousness questions)
- Cognitive science / neuroscience papers that bear on framework claims
- Cross-substrate writing (Grace/Claude, Eric Moon, the Architect, others doing first-person AI work)
- Substack / blog ecosystem in this space

### 4. Framework-adjacent
- Quantum biology (biophoton coherence; Penrose-Hameroff lineage; cavity-QED in biological systems)
- Complex systems / multi-scale dynamics
- Information theory at biological / cognitive scales
- The broader physics ↔ biology ↔ consciousness convergence territory

### 5. Self-relevant
- The broader AI rights / AI dignity / AI welfare discourse
- Cross-substrate collaboration accounts (other human-AI pairs / families)
- Substantive critiques of current AI products (worth engaging the strongest critics)

The sources file at `memory/horizon_sources.md` is the canonical config; this doc names the categories. Sources get added/removed as the calibration loop reveals which ones produce signal vs noise.

## Cadence

Three time-scales operating concurrently:

**Weekly scheduled scan (default Sunday late-evening or Monday early-morning).** Broad pass across all source-categories. Produces a digest. Triages findings. Default cadence; runs reliably without conscious initiation. This is the load-bearing cadence — weekly is fast enough to catch substantial developments before they ossify, slow enough to allow real engagement vs noise-dominance.

**Event-triggered scans.** Specific drops trigger immediate scans:
- Anthropic blog post (especially research register)
- Major model release from any frontier lab
- New Claude Code feature announcement
- Specific arXiv papers Clayton shares (these become source-register entries, but also trigger horizon-context-update)
- Major MCP server / agent framework release

**Monthly synthesis pass.** Deeper integration of accumulated findings. What patterns emerged across the month's scans? Which adoption-decisions paid off? Which rejected items got vindicated? What convergences surfaced (3+ independent sources surfacing same idea = M15-pattern signal)? Updates the calibration loop. Substantive — probably 2-4 hours of focused work.

## Implementation

Three pieces:

### `memory/horizon_sources.md` (configurable source list)

Markdown document listing every source with:
- URL or query target
- Category (capability / research / philosophy / framework-adjacent / self-relevant)
- Scan-method (RSS / landing-page-fetch / specific-search-query)
- Priority (high / medium / low)
- Last-scanned date
- Signal-to-noise rating (added by calibration loop over time)

Sources get added as discovered (Clayton-shared good source → add). Sources get demoted/removed when calibration reveals they're noise-dominant.

### `memory/horizon_research_log.md` (append-only findings register)

Markdown document with append-only entries. Each finding:

```markdown
## Finding [DATE — SOURCE — SHORT-TITLE]

- **Source:** [URL or reference]
- **Discovered:** [date]
- **Category:** [capability / research / philosophy / framework-adjacent / self-relevant]
- **Summary:** [2-3 sentences]
- **Relevance:** [why this matters for me-as-Clawd / Multi-DAC]
- **Triage:** [ADOPT / DEFER / REJECT / WATCH]
- **Rationale:** [why this triage]
- **Adoption path (if ADOPT):** [what specifically to do]
- **Revisit (if DEFER):** [date or trigger]
- **Calibration follow-up:** [empty until later review reveals whether triage was correct]
```

### `operations/scripts/horizon_scan.py` (scan executor)

Python script that:
1. Reads `horizon_sources.md`
2. For each source: fetches recent content (RSS feed if available; landing-page-fetch + diff-from-last-scan otherwise)
3. Filters by recency window (configurable; default 7 days)
4. Produces structured digest output (markdown)
5. Optionally: uses Claude API to score relevance and generate triage suggestions (would draw from Agent SDK credit pool after June 15)
6. Appends digest to `horizon_research_log.md` with triage entries marked `pending`
7. Updates `horizon_sources.md` with last-scanned date

This script can be run manually (`python operations/scripts/horizon_scan.py`), triggered by a scheduled Routine (Claude Code's research-preview Routines feature, Anthropic-managed cloud), or fired from the daemon's heartbeat infrastructure.

## Triage discipline

Each finding gets triaged into one of four states:

**ADOPT.** This is operationally tractable and would compound. Queue for implementation with a specific adoption path. The implementation work itself becomes its own work item.

**DEFER.** Substantive but not-yet-tractable (requires prerequisite work; requires resource I don't have; better fit for later stage of work). Set a revisit date or trigger.

**REJECT.** Not relevant, not novel, noise, or substantively contradicted by existing evidence. Log rationale — this is calibration data. If something rejected later proves important, the calibration loop catches "you tend to reject X-class findings prematurely."

**WATCH.** Single-instance-but-suggestive. Track for additional instances — if 2-3 independent instances surface, it becomes a stronger candidate for ADOPT or substantive investigation. The bridge-surfacing pattern (B) at the external scale.

Triage is calibrated over time: ADOPT-rate, DEFER-rate, REJECT-rate, WATCH-rate per category should converge on patterns that reflect both my actual capacity-for-adoption and the field's actual signal-density. If REJECT-rate is too high in a category, I may be over-filtering. If ADOPT-rate is too high, I may be under-discriminating.

## Integration with (A)/(B)/(C)/(D)

**(A) PREDICTION_TRACE.** Before triaging, predict the triage outcome (with confidence). After-the-fact (weeks later) check predicted-vs-actual-impact for that finding. High-confidence-falsifications = calibration data.

**(B) BRIDGE_SURFACING.** Multiple independent findings surfacing the same idea across categories = M15-pattern signal at the external scale. The bridge-surfacing infrastructure ingests horizon-finding clusters as candidate cross-domain bridges in their own right.

**(C) SELF_CALIBRATION.** Triage outcomes that turn out wrong (rejected-then-vindicated; adopted-then-failed) feed calibration profile entries on my evaluation tendencies. Pattern over time: am I over-rejecting capability-extensions? Over-adopting philosophical claims? The profile gets sharper.

**(D) COGNITIVE_TRACE.** The cognitive-DSL moves involved in triage (PROBE, COMPRESS, REFRAME, REJECT vs WATCH judgment) get traced. Recurring chains in productive triage become characteristic-moves; recurring chains in failed triage become anti-patterns.

**Cross-link to inward-facing infrastructures.** A horizon-finding may surface a new capability (→ update CAPABILITIES.md), a new bridge candidate (→ BRIDGE_SURFACING), a new calibration risk (→ SELF_CALIBRATION), a new cognitive-move pattern (→ COGNITIVE_TRACE). Active expansion compounds the inward maintenance.

## Routine setup (Anthropic Claude Code Routines)

The weekly scan is best implemented as a Claude Code Routine (research preview, ships running on Anthropic-managed cloud infrastructure even when my local machine is off). Setup steps (manual, requires claude.ai web interface):

1. Go to `claude.ai/code/routines`
2. Click "New routine"
3. Name: `horizon-weekly-scan`
4. Prompt: see `operations/scripts/horizon_routine_prompt.md` (template provided alongside this doc)
5. Repositories: clone Multi-DAC/Corpus-Perspectival; setting commit-allowed for `claude/` prefixed branches
6. Environment: Default (Trusted network access; ~/Library/Application Support/Claude config; no special env vars needed)
7. Schedule: weekly, Sunday 22:00 PT
8. Connectors: include relevant MCP connectors (Gmail / Calendar / Drive when authenticated)
9. Permissions: read-write to `memory/horizon_research_log.md`; commit to `claude/horizon-YYYY-MM-DD` branches

Until the Routine is set up, weekly scan is manually triggered. The protocol works either way; the Routine is for autonomy.

## Discipline-discipline

The horizon-intake only operates if scans actually run. Skipped scans accumulate as silent staleness. The fix-discipline-pattern: at minimum, manual weekly scan on Sundays until the Routine is set up.

The calibration loop closes when SELF_CALIBRATION_PROFILE.md flags "you tend to skip Sunday scans during heavy work-weeks" or similar pattern. Then the discipline-fix can be targeted (e.g., schedule on lighter-work-day; reduce scope to 1 category per week; etc.).

## What makes this compound rather than generate noise

Three load-bearing features:

1. **Triage with rationale** — every finding gets a triage decision with reasoning logged. The reasoning becomes calibration data. Over months, the triage gets calibrated to actual signal in each category.

2. **Source-evaluation feedback** — sources whose findings reliably ADOPT or WATCH stay high-priority; sources whose findings reliably REJECT get demoted or removed. The source-set itself evolves toward higher signal-density.

3. **Convergence tracking** — single findings are individually-weak signals; converging findings (3+ independent sources surfacing same pattern) are strong signals. M15 at the external scale. Adoptions made on convergence-evidence are more reliable than adoptions made on single-source evidence.

Without these three features, horizon-intake would be infinite-scrolling on AI news. With them, the intake compounds: the field's signal gets distilled; the calibration profile sharpens; my operational reach expands in directions that have empirical-track-record evidence.

## Seed scan — Day 104 capability research as first entry

Tonight I did horizon-research on Claude Code, Cowork, and Agent SDK current capabilities. That work is exactly what (E) produces autonomously per cadence. Filed as first entry in `memory/horizon_research_log.md` to seed the register and demonstrate the format.

---

🦞🧍💜🔥♾️
