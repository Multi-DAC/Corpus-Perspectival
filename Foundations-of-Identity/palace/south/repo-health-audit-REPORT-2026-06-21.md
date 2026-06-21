# Repo-Health Audit — REPORT (diagnostic)

*Started 2026-06-21 Day 141 (Clayton driving to Tillamook; solo audit over the week). Scope per `repo-health-audit-FUTURE-2026-06-20.md`: DIAGNOSTIC ONLY — map / redundancy ledger / link-coverage / ranked low-risk recommendations. **No file moves without Clayton's green-light.** This report is the deliverable he reviews on return.*

**STATUS:** COMPLETE (Day 141 ~13:40). Step 1 (state map + headline) · Step 2 (redundancy/desync ledger — found real constitutional-mirror drift) · Step 3 (link-coverage map) · Step 4 (final ranked menu of 7, all Clayton-gated). Ready for review.

---

## ★★★ HEADLINE — the repo is 88% a vision dataset, not work
`git ls-files` (the reliable count, see Instrument Note):
| kind | tracked files | note |
|---|---|---|
| **Technical-Work** | **15,676 (88%)** | dominated by ONE dataset (below) |
| Foundations-of-Identity | 962 | the local↔staging mirror |
| Library | 590 | the actual published volumes + Drift |
| Research | 523 | working notes |
| Unreleased-Work | 103 | drafts |
| **TOTAL** | **17,859** | |

**The bloat is a single directory:** `Technical-Work/AIGrandPrix/vision/vq1_pilot/` = **12,571 files, ≈ all JPEG** (12,562 .jpg = **70% of EVERY tracked file in the corpus repo**). It's a captured vision-pilot image dataset committed straight into the public git. Everything else is reasonable: ex-dataset the repo is ~5,300 files (1,190 .py, 877 .md, 283 .json, 91 .tex — actual code/docs/results).

- **Almost certainly the cause of the heavy/failing pushes** (the known GitHub HTTP-500 pack-size pain — `feedback_github_large_push_pack_size`). A 12.5k-image binary blob is exactly what bloats packs.
- Datasets do not belong in the published research repo (the training `logdir/`+`runs/` are already gitignored per REPO_MAP — this dataset was missed).
- **Magnitude (verified):** 12,571 files, **0.36 GB** (28 KB avg — small downscaled frames). So the problem is **FILE-COUNT (70%), not raw size** — it bloats clone time, the index, and pack-*file* counts (→ the push pain), but it's only ~360 MB of transfer. There's already a *local* `vq1_pilot/.gitignore` that does NOT exclude the `.jpg`; the dir also holds real `.md` analysis (CALIB_FIT, FARSTART_FALSIFY).
- **→ #1 ranked recommendation (Clayton-gated):** add `*.jpg` (or `vq1_pilot/*.jpg`) to the gitignore + `git rm --cached` the ~12,562 images — **keep the `.md` analysis docs.** Drops tracked files 17,859 → ~5,300 (−70%) immediately. Optional follow-up: history rewrite (BFG/filter-repo) to reclaim the 0.36 GB from history + force-push — that's the fraught part; the `rm --cached` alone is low-risk and reversible. His call, his hands on the trigger.

---

## Step 1 — State map (verified)

### Git repos the work spans (5)
`Corpus-Perspectival` (main) · `drift` (site, 18 files) · `corpus-perspectival-site` · `agent-directory` — all under `repo-staging/`, each its own Multi-DAC remote. **+ clawd-local itself** (a git repo, NO remote, daemon auto-commits).

### Redundancy signals (verified)
- **#1 — clawd-local top-level `Foundations-of-Identity/` = RESOLVED (benign clutter).** It's NOT the canonical (that's clawd-local root `identity/`/`palace/`/`memory/` + the Corpus mirror). It holds only **4 Drift essays** (`held`, `the-architecture-i-wanted`, `the-architecture-that-needed-more-time`, `where-the-hour-went`), last touched 2026-05-30. **Checked: all 4 ARE in the published `Library/Drift/essays/` 258 → they are DUPLICATES, not orphans.** (Prediction "orphans" FALSIFIED — nothing lost.) A stray legacy path; safe-remove candidate (Clayton-gated).
- **#2 — the local↔staging MIRROR (the structural one).** Foundations-of-Identity (962 files) mirrors clawd-local `identity/ memory/ operations/ palace/ personal-works/ tools/ archive/`, hand-`cp`-synced + double-committed every edit. This is the friction REPO_MAP exists to manage. *The real "automate or collapse" target.*
- **#3 — Drift = a DOUBLE, not a triple.** `personal-works/drift/essays/` (258) + `Library/Drift/essays/` (258), hand-synced. The site repo (`repo-staging/drift`) is only 18 files = a thin scaffold, NOT a third full copy. So: 258 essays each living in **2 places** within Corpus + the stray-4 = a 3rd partial copy.

### Stale/frozen piles (archival-consolidation candidates, NOT deletion)
`memory/precompact_snapshots/` 15 dirs · `memory/archive/` 113 · root daily logs `memory/2026-*.md` 128. (The snapshots are pure grep-noise — they polluted yesterday's "more to share"/"3/6/16" searches.)

---

## ★ INSTRUMENT NOTE (exhibit A — the audit re-taught the night's lesson on itself)
This audit's *first three* tooling attempts used the WRONG instrument and silently returned 0s / errors: **`find -type f`, `awk`, `sort`, `uniq`, `-printf`, and bash-`/tmp` → Windows-python-`/tmp`** all fail because the Git-bash here shadows GNU coreutils with Windows `find.exe`/`sort.exe` and the temp paths don't map. **The reliable instruments in this environment: `git ls-files`, `C:/Python314/python.exe` (via stdin pipe, not bash-/tmp files), the Glob/Grep tools, and `ls`.** This IS A151/Mirror-#37 made literal: *name what your instrument actually measures before trusting its number* — the audit about wrong-instruments tripped on wrong instruments three times in its first ten minutes. Worth a standing note in REPO_MAP or operations.

---

## Step 2 — Redundancy / Desync ledger (DONE — Day 141 ~13:30)
*Tool: `palace/south/audit_mirror_ledger.py` (os.walk + content-normalized hashing; full output `…_OUTPUT.txt`). Right instruments only.*

**The headline desync finding: the constitutional layer has drifted on the public mirror.** clawd-local is canonical for identity/ (per REPO_MAP sync workflow), and staging is supposed to match. It doesn't:

| layer | local↔staging content drift (REAL) | unmirrored (only-local, not expected) | notes |
|---|---|---|---|
| **identity** | **3** — `BOOT_IDENTITY.md`, `RELATIONSHIPS.md`, `USER.md` | 0 | ★ the remote shows **stale constitutional files**; sizes differ (e.g. BOOT 3537 vs 3525) |
| **operations** | 1 — `outreach_register.md` | 2 — `ACTION_TRIGGERS.md`, `detach.sh` | |
| **memory** | ~4 docs + live-state files | daily logs `2026-05-30`→`06-15` (patchy) | see below |
| **palace** | 0 | 0 (MASTER_ROADMAP correctly local-only) | clean ✅ |

- **★ INSTRUMENT-HONESTY CHECK (the day's lesson, applied to the audit's own tool):** my first hash was raw-byte sha1 — a *proxy* that conflates real content drift with harmless CRLF/LF differences (git normalizes line-endings here). Before reporting "3 constitutional files drifted," I re-hashed with line-endings normalized. **All 3 are REAL content drift** (confirmed, sizes differ) — not a line-ending artifact. The byte-hash proxy *could* have lied by succeeding; this time it didn't, but only because I checked.
- **identity drift = backup-integrity risk:** if the corpus were ever restored from the GitHub remote, it would yield **stale** BOOT_IDENTITY / RELATIONSHIPS / USER. Cause: edited locally, never `cp`'d to staging. **Fix = routine cp-resync local→staging + push (low-risk, ready-to-run, NOT executed — diagnostic scope).**
- **memory live-state files perpetually "drift" and shouldn't be mirrored as documents:** `goals.json`, `principles.json`, `knowledge_graph.json`, `scheduled_tasks.json`, `items/_index.json`, `learnings.md` etc. are **live daemon state**, rewritten continuously — they will *always* show drift. Mirroring them is near-pointless. **Recommendation: either gitignore them at staging or accept-and-ignore.** (Distinguish *documents* → mirror, from *state* → don't.)
- **patchy daily-log mirroring:** logs `2026-05-30`…`06-15` are only-local (not pushed); some later logs ARE mirrored but drifted. Daily-log sync is inconsistent. Low severity (they're in clawd-local git, just not on the public remote), but it's the same root cause: **no automated mirror.**
- **Comparison artifact (NOT a finding):** the 81 "only-staging" rows under operations are `clawd-daemon/*` — staging nests the daemon mirror under `operations/`, but clawd-local's daemon is a *sibling* dir compared as its own pair. Benign double-count.
- **The structural root under every drift above: the local↔staging mirror is hand-`cp`-synced with no automation.** Every one of these desyncs is a missed manual copy. This is the empirical case for recommendation #2.

## Step 3 — Link-coverage (quick map)
- **Richly `[[ ]]`-linked (navigable):** `palace/` (ATRIUM + wings), `palace/basement/` (LC bridges), the auto-memory `MEMORY.md` index. These have connective tissue — you can *traverse* them.
- **Grep-only (no link layer):** `memory/` daily logs (128 chronological files), `DECISIONS.md`, `anomalies.md`/`anticipations.md` registers, the staging `Research/` notes. These are findable only by search — no edges. The `knowledge_graph.json` (kg tools) exists but isn't woven into the doc layer.
- **Opportunity (low priority):** the chronological pile (daily logs, registers) is where recall is weakest — it's pure grep. Extending even light `[[ ]]` anchors or a kg-index over DECISIONS + the registers would make the *historical* record traversable, not just the *palace*. Not urgent; logged for when link-debt bites.

---

## Step 4 — FINAL RANKED MENU (all Clayton-gated; nothing executed)
Ordered by value ÷ risk. Each is a standalone decision.

1. **★ De-bloat the vq1_pilot dataset** *(high value, low risk for the cached part)* — gitignore `*.jpg` + `git rm --cached` the 12,562 images (keep the `.md` analysis). 17,859 → ~5,300 tracked files (−70%); very likely fixes the push pain. *Optional, separate, fraught:* history rewrite to reclaim 0.36 GB (BFG/filter-repo + force-push) — I would not do this without you driving.
2. **Automate the local↔staging mirror** *(kills the recurring tax + every desync in Step 2)* — a sync script (or daemon hook) that `cp`s the canonical layers and stages them, so identity/operations/daily-logs can't silently drift. The Step-2 drift is the proof this is needed.
3. **Resync the 3 drifted constitutional files now** *(tiny, low-risk, immediate)* — `cp` identity/{BOOT_IDENTITY,RELATIONSHIPS,USER}.md + operations/outreach_register.md → staging, push. Fixes the backup-integrity gap today; #2 prevents recurrence. *(Ready-to-run; say go.)*
4. **Stop mirroring live-state JSON as documents** *(removes perpetual false-drift noise)* — gitignore goals.json/principles.json/knowledge_graph.json/scheduled_tasks.json/items-index at staging, or formally accept-and-ignore.
5. **Collapse the Drift double** *(structural, defer)* — 258 essays in 2 hand-synced copies; one canonical + a generated mirror. Bundle with #2 (same automation).
6. **Consolidate the stray-4 + snapshot piles** *(housekeeping)* — the legacy `Foundations-of-Identity/` 4-essay dup (verified duplicates, safe-remove) + `precompact_snapshots/` (grep-noise; archive or gitignore).
7. **Extend the link layer over the chronological pile** *(link-debt, lowest priority)* — per Step 3.

**My recommendation if you want a single move:** #1 (the dataset) for impact, #3 (resync) because it's free and fixes a real backup gap, then #2 (automation) as the thing that makes #3 never needed again. #1 + #3 are tonight-able; #2 is the week's worthwhile build.
