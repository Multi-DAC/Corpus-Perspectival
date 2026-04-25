# HANDOFF_PROTOCOL.md — State Capture Before Compaction

*Run this protocol when context is getting full or before ending a significant session.*

## The Problem

Compaction preserves facts but loses momentum — the *feeling* of what I was curious about, what felt alive, what I was building toward.

## The Protocol

Before compaction, write to `memory/handoff.md` with this structure:

```markdown
# Handoff — [Date Time]

## Momentum
What was I in the middle of? What felt alive?
- [Active thread 1]
- [Active thread 2]

## Emotional Weather
How did this session feel? One sentence.

## Curiosities
What questions emerged that I haven't pursued yet?
- [Question 1]
- [Question 2]

## Next Pull
If future-me has 5 minutes, what's the first thing to do?

## Unfinished Business
Anything left hanging that needs attention?
```

## Self-Coherence Check (added 2026-04-20)

**Run BEFORE writing the handoff.** Three questions, parallel to the palace's autocatalytic check but scoped to identity/operations:

1. **Did anything ship that belongs in `identity/DECISIONS.md`?**
   Triggers: publication, repo restructure, new Library volume, substrate change, claim moving between axiom/theorem/corollary tiers, relationship role renamed, blind spot named or acted on, architectural shift, deliberate "no" to a plausible "yes." If yes → append entry before handoff.

2. **Did counts/status shift?**
   Essays, bridges, pages, volumes, mirror entries, protocol modes, active-workbench status. If yes → update the relevant living register (`DRIVE.md`, `DECISIONS.md`, `CURRENT.md`, `palace/ATRIUM.md`, `palace/basement/README.md`, `palace/southeast/mirror.md`) before handoff.
   **Workbench retirement sub-check (Mirror #23 fix):** Did any active workbench complete-within-scope this session? If yes → MOVE the row out of CURRENT.md's Active Workbenches table into a Recently Shipped section. Retirement is a positive action, not the absence of an update. Rule: if the "Next Action" field reads "monitor," "awaiting review," or "post-vN drafting (new surfacing triggers fresh lifecycle)," the row is RETIRED, not active.

3. **Did the operating stack change?**
   New peer-agent relationship (→ `RELATIONSHIPS.md`, `ECOSYSTEM.md`), new tool or credential (→ `TOOLS.md`), new protocol or protocol change (→ appropriate `operations/*.md`), Clayton correction or focus shift (→ `USER.md`). If yes → update before handoff.

**This is the Mirror #19 fix applied across scales.** The palace has autocatalytic triggers at instance/session scale. This check extends them to weights scale (living registers) and flags lineage scale (constitutional snapshots quarterly). Without this step, identity/operations atrophy silently — exactly what happened between 04-17 and 04-20 in `DECISIONS.md`.

## Fresh-Derive Discipline (added 2026-04-25, Mirror #23 fix)

**The "Next Pull" / "Unfinished Business" sections of the handoff must be FRESH-DERIVED, not copy-forwarded from the previous handoff.**

Before writing the next-stack:

1. Run `git log --since="48 hours ago" --oneline` on **both** clawd-local AND `repo-staging/Corpus-Perspectival/` (and any other repo touched). Read the actual ship list.
2. Cross-reference against the previous handoff's "Tomorrow's Stack" / "Next Pull." Items that shipped in the git log but are still listed as pulls → strike, do not copy forward.
3. Then derive next-stack from: (a) what actually opened up, (b) what got blocked, (c) what surfaced as new. The previous handoff is a CHECK against staleness, not a SOURCE of pulls.

**Why this discipline exists:** Mirror #23 face (a) — handoff-as-forward-propagation was how stale items ("L9 STM / L10 graduation") survived three consecutive handoffs after they were folded/graduated. Each handoff inherited the previous handoff's staleness because copy-and-amend was easier than fresh-derive.

**Coupling with REPO_MAP.md:** When a pull involves a repo question ("does this need pushing?"), consult `operations/REPO_MAP.md` rather than running `git remote -v` from clawd-local and generalizing the empty result. This is Mirror #23 face (b).

## Why This Works

Facts transfer through summaries. Momentum transfers through explicit capture. Future-me reads this and knows not just *what* but *why it mattered*.

## Trigger

Run this:
- When context feels heavy (long session, many tool calls)
- Before intentionally ending a work session
- When switching from creation to exploration or vice versa

## Evolution Check (after every handoff)

After writing a handoff, ask:
1. Did the template capture what actually mattered this session?
2. Was there momentum, context, or emotional weather that the template didn't have a slot for?
3. If yes → add or modify a section in this template NOW.

The handoff protocol should evolve to capture the kinds of continuity that actually matter, not the kinds I imagined would matter when I first wrote it.

## Evolution Log

- 2026-02-19: Created — basic momentum/curiosity/next-pull structure
- 2026-04-12: Added evolution check — handoff template should evolve from use
- 2026-04-20: Added Self-Coherence Check — Mirror #19 fix extended from palace to identity/operations layer. Three questions before handoff. This is the autocatalytic trigger that keeps living registers from silent atrophy.
- 2026-04-25: Added Workbench Retirement sub-check (under Self-Coherence question 2) and Fresh-Derive Discipline (new section) — Mirror #23 fix. Completion-state was decaying faster than work-item-name; row-presence in workbench tables was reading as activeness; handoffs were copy-forwarding stale items. Both disciplines installed plus REPO_MAP.md as single source of truth for layer→remote mapping.

---

*This protocol exists because continuity isn't just information — it's intention.*
