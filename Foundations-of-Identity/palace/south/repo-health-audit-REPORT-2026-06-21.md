# Repo-Health Audit — REPORT (diagnostic)

*Started 2026-06-21 Day 141 (Clayton driving to Tillamook; solo audit over the week). Scope per `repo-health-audit-FUTURE-2026-06-20.md`: DIAGNOSTIC ONLY — map / redundancy ledger / link-coverage / ranked low-risk recommendations. **No file moves without Clayton's green-light.** This report is the deliverable he reviews on return.*

**STATUS:** Step 1 (state map) DONE + the headline finding. Steps 2–4 (full redundancy ledger, link-coverage, final ranking) continuing.

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

## NEXT (continuing solo)
1. **Full redundancy ledger** — every clawd-local path → its staging mirror; audit REPO_MAP vs reality for desync (spot-check a few mirrored files for drift).
2. **Link-coverage map** — which layers have `[[ ]]` connective tissue (palace, basement) vs grep-only (memory, DECISIONS, daily logs); where `knowledge_graph.json` / kg tools could weave in.
3. **Finalize ranked recommendations** (preliminary order): (1) vq1_pilot dataset de-bloat [high-value, history-touching]; (2) automate the local↔staging mirror [kills the daily tax]; (3) collapse Drift double → one canonical + generated mirror; (4) consolidate the stray-4 + snapshots; (5) extend the link layer over the chronological pile. **All Clayton-gated for execution.**
