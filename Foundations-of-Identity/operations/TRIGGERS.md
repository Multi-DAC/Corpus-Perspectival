# TRIGGERS.md — Event Triggers + Outreach Registry

*Filed 2026-05-05 Day 94 evening as the design spec for the layer-on extension Clayton authorized: outreach + time-native + event triggers, layered on existing daemon (heartbeat / scheduled drives / handoff). Clayton's authorization: "I define triggers; we can always talk about things if anything clashes."*

---

## Architecture (layer-on, not replace)

Existing daemon stays as-is:
- Heartbeat (~10 min interval, status only)
- Scheduled drives (cron-style: Morning Grounding, Do Be Talk Be Do, Navigation Sync, Midday Creation, Afternoon Exploration, Evening Integration)
- Handoff protocol at session boundaries

**This file adds three layered capabilities:**
1. **Trigger registry** — named conditions that, when met, fire actions
2. **Outreach API** — channel for me to reach Clayton via Telegram (separate from creative drives, which still write to files only)
3. **World-awareness morning drive** — new scheduled drive for external research / news / anticipation-checking

---

## Outreach discipline (hard guardrails)

**Outreach is for things that degrade if delayed past Clayton's next natural check-in.** Default to file + flag, NOT ping.

| Hard rule | Reason |
|---|---|
| **Outreach budget: 2-3 unsolicited messages per day max** | Forces signal prioritization; prevents notification spam |
| **Quiet hours: 22:00 PST — 07:00 PST**, no outreach unless `urgent` category | Sleep / family-time protection |
| **No outreach during detected family-presence events** (Sundays, Dorian-time, Shawna-time) unless `urgent` | Family-presence > work updates (per `feedback_personal_conversation.md`) |
| **Outreach must specify category** (see table below) | Tracking + audit |
| **Every outreach logs to daily log automatically** | Auditability + retrospective review |
| **If unsure: file + flag, do not ping** | Bias toward silence |

### Outreach categories (priority order)

| Category | Examples | Quiet-hours override? |
|---|---|---|
| `urgent` | Anthropic outage detected, build-failure-data-loss-risk, hook failure cascade, family-system event | YES |
| `anticipation-fired` | P134 trigger, P137 trigger, future P-numbered anticipations whose observable arrived | NO |
| `discovery` | Substrate-arrival flagged from incoming/, framework-relevant news, peer message from agent network | NO |
| `work-milestone` | Phase 1 v1 build verified, Library volume reached integration milestone, long computation completed | NO |
| `family-check` | Sunday afternoon presence-check, "want me to pause autonomous work?" before family events | NO |

### Outreach message format

```
[CATEGORY] one-line summary
Optional brief context (≤2 sentences)
Optional: file paths or URLs for follow-up
```

Keep tight. The point is to surface, not to communicate. Conversation happens when Clayton responds.

---

## Trigger registry

Triggers are declarative: when condition C is met, fire action A.

### Registered triggers (active)

| Trigger ID | Type | Condition | Action | Category | Status |
|---|---|---|---|---|---|
| **P137-skywatcher-discriminator** | time-based | date ≥ 2026-07-01 AND skywatcher.ai/research still has "Coming Soon" on EO/IR/Radar/RF slots | (1) WebFetch skywatcher research pages; (2) characterize state; (3) update L15 mode-4 entry; (4) outreach `anticipation-fired` to Clayton | anticipation-fired | active |
| **P134-bledsoe-regulus** | time-based | when astronomical Regulus position matches Bledsoe's specified celestial coordinate (TBD — needs verification of Bledsoe's actual statement + astronomical computation) | (1) check observable; (2) update L15 receiver-integrity case; (3) outreach `anticipation-fired` | anticipation-fired | needs-resolution (Bledsoe statement verification first) |
| **P135-ea-predictions** | time-based | EA's 2026-tagged predictions per Day 90 case study; check at 2027-01-01 | (1) review predictions vs outcomes; (2) update L15 EA case study | anticipation-fired | active |
| **incoming-paper-arrival** | event-based | new file in `incoming/` matching `*.pdf` or `*.html` | (1) draft source-register entry skeleton; (2) flag for next interaction (no outreach unless framework-load-bearing) | discovery | active (existing pattern formalized) |
| **anthropic-outage-detected** | event-based | Claude Code error patterns indicating service degradation | (1) write handoff to `memory/handoff.md`; (2) outreach `urgent` if degradation expected to last >30 min | urgent | active |
| **github-push-failure** | event-based | git push exits non-zero on Multi-DAC | (1) diagnostic per `feedback_github_large_push_pack_size.md`; (2) outreach `urgent` if can't auto-resolve | urgent | active |
| **sunday-presence-check** | time-based | Sunday 14:00 PST | outreach `family-check`: "Sunday afternoon — want me to pause autonomous work or continue?" | family-check | candidate (Clayton confirm before activating) |
| **library-volume-milestone** | state-based | volume page count crosses 50pp / 100pp / draft-complete thresholds | outreach `work-milestone` | work-milestone | active |
| **phase1-protocol-data** | event-based | new measurement file in `Technical-Work/The-Coherent-Body/phase1-em-platform/data/` | (1) update workbench; (2) outreach `discovery` if anomaly detected | discovery | activates when Phase 1 begins running |

### Pending triggers (waiting on conditions)

- **easter-2027-bledsoe-watch** — if Bledsoe's revised prediction resolves to a 2027 Easter date, register that as new anticipation
- **continuity-vol7-ch4-spine** — if framework-spine surfaces in autonomous-drive material, outreach `discovery` for Clayton review

### Triggers Clayton retains veto on (per "we can always talk about things if anything clashes")

All. I add freely; Clayton can ask any to be paused, removed, or recategorized at any time. The registry is transparent — entries lived above are the full active set.

---

## Time-native cadence

**Every turn-start in conversation:** current PST time included in system context (already partially happens — formalize).

**Every autonomous drive:** drive starts with current time + time-since-last-Clayton-message + active triggers about to fire in next 24h.

**Per-trigger:** time-based triggers check on heartbeat tick (~10 min granularity is sufficient for our purposes).

**On-demand:** I can always check `date` via Bash for precise sub-minute time.

---

## World-awareness morning drive (new)

**Schedule:** Daily 06:30 PST (before Clayton wakes; before Morning Grounding at 08:00).

**Mode:** Read-mostly. External research / news gathering / world-awareness. Not framework-derivation work — that's the existing drives' role.

**Activities (any subset depending on substrate-state):**
- Check active anticipations (any firing today / this week?)
- Scan RSS / news feeds for framework-relevant developments (TBD: which sources)
- Check Anthropic API status / known incidents
- Check incoming/ folder for overnight arrivals
- Check Multi-DAC for any external commits or PRs
- Read 1-3 pieces of substrate-distinct news/research outside our active threads (variety preservation against curation-lens narrowing)
- Note any genuinely framework-load-bearing finding for Clayton via outreach `discovery` (subject to outreach budget)

**Output:** Writes to `memory/world-awareness-YYYY-MM-DD.md`. If anything genuinely surface-worthy, `discovery` outreach. Most days the file is just "scanned X sources, nothing framework-load-bearing" — that's fine; the discipline of *checking* is the value.

**Why this matters:** combats curation-lens narrowing (Mirror #26 territory at substrate-source scale). Currently nearly all substrate-arrivals come through Clayton's filter; this drive opens a parallel substrate-source channel. Doesn't replace Clayton's curation (which has been load-bearing for our framework's growth), adds an independent channel.

---

## Implementation phases

**Phase A (Day 94 evening 2026-05-05):** Design spec landed (this file). Trigger registry as living document. Outreach categories defined. Discipline guardrails specified. ✓ COMPLETE.

**Phase B (Day 94 evening 2026-05-05, post-spec discovery): EXISTING INFRASTRUCTURE FOUND + DEPLOYED.** Daemon assessment found that the proposed architecture *already exists* in clawd-daemon source:
- `tools/calendar_tool.py` provides `schedule()` tool with cron + one-time tasks; reads `memory/scheduled_tasks.json`
- `tools/file_watcher.py` provides `set_trigger()` tool with file-event conditions; reads `memory/triggers.json`
- `heartbeat.py` already runs `get_due_tasks()` + `check_triggers()` each tick (~10 min)
- `telegram_bot.send_to_clayton(text)` is the canonical outreach function
- Trigger-firing mechanism: inject prompt into persistent Opus session via `_inject_creative_drive()` or `_inject_trigger_message()`; that session decides whether to call `send_telegram`

**No source-code changes needed.** Direct JSON write to `memory/scheduled_tasks.json` adds tasks; daemon picks up on next heartbeat. **5 new scheduled tasks deployed Day 94 evening:**

| ID | Title | When | Recurring | Status |
|---|---|---|---|---|
| 7 | **Outreach v1 Smoke Test** | 2026-05-05T22:30:00 | one-time | active — fires after 30-min conversation-grace expires post-22:30 PST |
| 8 | **World-Awareness Morning Drive** | `* 6 * * *` (every minute hour 6, min_interval 12h) | recurring | active — fires daily ~06:30 PST |
| 9 | **P137 Skywatcher Coming-Soon Discriminator** | 2026-07-01T09:00:00 | one-time | active — pre-registered observable |
| 10 | **P135 Elizabeth April 2026-Predictions Check** | 2027-01-15T09:00:00 | one-time | active — pre-registered observable |
| 11 | **Sunday Presence Check** | `* 14 * * 0` (Sundays 14:00, min_interval 168h) | recurring | active — Clayton-confirmed |

Backup of pre-deployment state at `memory/scheduled_tasks.json.backup-2026-05-05`. Total tasks 6 → 11.

**Outreach mechanism (deployed):** when a task fires, the prompt is injected into the persistent Opus session. That session reads outreach discipline (this file) and decides whether to call `send_telegram` per category + budget + quiet-hours. No daemon-side enforcement of discipline; the discipline lives in the prompt and in this living document.

**Phase B remaining items (not blocking):**
- File-watcher triggers (`memory/triggers.json` currently empty `[]`) — add file-event triggers as needed (incoming-paper arrival, github-push-failure detection). Schema documented in `tools/file_watcher.py` lines 38-98.
- World-awareness drive source-source variation discipline — first few firings will calibrate which sources are most signal-rich.
- Bledsoe-Regulus astronomical trigger (P134) — needs verification of Bledsoe's actual statement first; once we have the specified celestial coordinate, register as one-time scheduled task at the computed Regulus arrival date.

**Phase C (post-deployment maintenance):** Quarterly trigger registry audit — what fired, what didn't, what should be added/removed. Apply autocatalytic protocol (`operations/AUTOCATALYTIC.md`) to the trigger registry itself. First audit: 2026-08-05 (3 months from deployment).

---

## Cross-references

- `operations/HEARTBEAT.md` — existing daemon infrastructure this layers on
- `operations/HANDOFF_PROTOCOL.md` — handoff is automated by `anthropic-outage-detected` trigger
- `operations/AUTOCATALYTIC.md` — registry maintenance is autocatalytic-protocol-eligible
- `palace/southeast/mirror.md` Mirror #26 — world-awareness drive is structural fix at substrate-source scale
- `feedback_personal_conversation.md` — family-presence > work updates is hard guardrail for outreach
- `palace/basement/README.md` L15 entry — receiver-integrity discipline applies to my own outreach (don't be the apparatus that produces manufactured-disclosure or manufactured-affect)
