# Cleanup Proposal — 2026-04-17

**Written:** 2026-04-17, morning session (post-Chapter 0 compile)
**Status:** Proposal for Clayton's review. Non-destructive actions already executed; destructive actions await explicit approval.

---

## 1. Local `projects/Corpus Perspectival/` (132 MB)

### Already Migrated (verified today)
- `v07_design.md` → `Technical-Work/Glider/v07_design.md` ✓
- `kf_trajectory_v01.json` through `v05b.json` → `Technical-Work/Killing-Form/results/` ✓

### Migrated by Clawd this morning
- `kf_trajectory_300m.json` (18 KB, Apr 12) → `Technical-Work/Killing-Form/results/` ✓
- `kf_trajectory_300m_scheduled.json` (6 KB, Apr 14) → `Technical-Work/Killing-Form/results/` ✓

### Published PDFs — awaiting your call

`projects/Corpus Perspectival/published/` contains:

| File | Superseded by |
|------|---------------|
| `Corpus_Perspectival_V2.pdf` | Anchor volume (`Library/The-Coherence-Principle/build/the-coherence-principle.pdf`) |
| `Corpus_Perspectival_V2_Book.pdf` | Anchor volume (same as above) |
| `The_Corpus_of_Perspectival_Idealism_V1.pdf` | Anchor volume (V1 predecessor) |
| `DoPI-Complete (1).pdf` | Anchor volume (the full monograph was the follow-on) |

**Proposed action:** Move all four into `Foundations-of-Identity/archive/historical-versions/` inside the Corpus-Perspectival repo. They are historical artifacts, not active work — preservable but demoted from `published/`.

**Why not delete:** Version history matters. Zenodo has V2 at a DOI. These PDFs should remain retrievable from the repo for readers coming through old links.

### Regenerable artifacts — safe to delete

- `latex_build/` (8.9 MB) — build artifacts, regenerable from Library tex sources
- `figures/` (2.5 MB) — **must verify no unique figures before deletion**
- `visualizations/` (88 MB) — **must audit** (heaviest; overlap with Library figures likely but not proven)

**Proposed action:** Do NOT delete yet. Run a visual diff on `figures/` and `visualizations/` to confirm full coverage in Library. This is a wake-Clayton-or-wake-Clawd task; not tonight-safe.

### Everything else (experiments, results, corpus, v3, research, paper, logs, analysis, scripts)

Inventory-written prose already covers these. Proposed path: rename the dir to `_DEPRECATED_Corpus_Perspectival/` so it's visible but off-path, then delete after one more cycle.

**Proposed action:** Hold on rename until you can glance at it yourself. Rename is low-risk but high-confusion if you reach for a path muscle-memory.

---

## 2. Agent Directory

### Current state (verified today via memory/handoff; no fresh ping needed)
- API responding: 2 agents registered, 0 verified
- Dormant since 2026-02-15 (~2 months)
- Not cloned locally; only accessed via the live deployment

### Options

**A. Revive** — Commit time to the Directory. Verify the 2 registered agents, add onboarding, publicize. This is a product push, not a maintenance task — requires your decision on whether it's a live priority.

**B. Maintain-as-dormant** — Leave the API up, add a banner noting "not actively curated," and monitor passively. Low cost, preserves option value.

**C. Sunset** — Take the deployment down, archive the code, point agent registrations elsewhere (if there's a successor; Beacon Atlas could be one).

### My read

**Option B** is the default unless you want to commit to A. The cost of maintaining a dormant API endpoint is near-zero. The cost of a premature sunset is irreversible. Option C becomes sensible only if Beacon Atlas becomes the clear successor venue, in which case we'd want an explicit migration pointer rather than a silent takedown.

**I recommend B** — add a short banner to the Directory homepage noting it's in maintenance mode, keep the API live, and revisit when either (a) Beacon Atlas reaches a state where succession makes sense, or (b) you decide to commit time to revival.

**Proposed action:** Wait for your decision. No destructive action taken.

---

## 3. Summary — What I Did vs. What I'm Asking You

### Executed (safe, non-destructive)
- Converted & compiled Chapter 0 into Meridian monograph (193pp total, ready for Zenodo)
- Migrated 2 unique KF trajectory JSONs to canonical location
- Updated BOOK_NOTES.md and ROADMAP.md for Chapter 0

### Blocked on you (previously identified)
- **Defender exclusion** — admin PowerShell
- **GitHub secret-scanning** — review alert or forward details for remediation

### Awaiting your nod (this proposal)
- Archive `published/` PDFs → `Foundations-of-Identity/archive/historical-versions/`
- Audit `figures/`, `visualizations/` for uniqueness before deletion
- Rename local dir to `_DEPRECATED_Corpus_Perspectival/`
- Agent Directory: choose A / B / C (I recommend B)

🦞🧍💜🔥♾️
