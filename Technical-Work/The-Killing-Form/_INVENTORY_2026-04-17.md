# Local `projects/Corpus Perspectival/` Inventory — 2026-04-17

**Status:** This directory is **NO LONGER AUTHORITATIVE** since the 2026-04-16 reorganization. The canonical home is `repo-staging/Corpus-Perspectival/` (mirrored to `Multi-DAC/Corpus-Perspectival` on GitHub).

This inventory was written during the overnight execution scope so wake-Clayton can decide what to keep, archive, or delete. **No files have been deleted.**

## Top-Level Sizes (132 MB total)

| Subdir | Size | Likely status |
|--------|------|---------------|
| `visualizations/` | 88 MB | Heaviest. Check overlap with `Library/Meridian/figures/` and `Technical-Work/*/figures/` |
| `experiments/` | 18 MB | Pre-reorg KF experiment outputs. Likely mirrored under `Technical-Work/Killing-Form/` |
| `latex_build/` | 8.9 MB | Build artifacts (regenerable). Safe to remove if Library build pipeline is the active one |
| `published/` | 8.2 MB | Published PDFs. Compare against `Library/*/build/*.pdf` |
| `results/` | 3.0 MB | Numeric outputs. Cross-check `Technical-Work/Killing-Form/results/` |
| `figures/` | 2.5 MB | Figures. Cross-check `Library/Meridian/figures/` |
| `corpus/` | 2.2 MB | Corpus text. Almost certainly mirrored under `Library/` |
| `v3/` | 596 KB | Pre-Library V3 structure. Superseded by Library reorg |
| `research/` | 312 KB | Working notes. Compare against `Research/` |
| `paper/` | 224 KB | Likely paper drafts. Compare against `Unreleased-Work/` |
| `logs/` | 92 KB | Run logs. Mostly archive-safe |
| `analysis/` | 52 KB | Analysis outputs. Small, probably already migrated |
| `scripts/` | 36 KB | Scripts. Compare against `Technical-Work/*/scripts/` |

## Top-Level Files (root of the dir)

- `kf_trajectory_300m.json` (18 KB, Apr 12) — KF training trajectory
- `kf_trajectory_300m_scheduled.json` (6 KB, Apr 14) — scheduled-variant trajectory
- `kf_trajectory_v05.json` (7 KB, Apr 12) — v0.5 trajectory
- `v07_design.md` (17 KB, Apr 14) — **Possibly unique to local.** v0.7 design doc. Check if migrated to `Technical-Work/Killing-Form/documentation/`.

## Recommended Cleanup Path (for wake-Clayton or wake-Clawd to execute)

1. **Diff `published/` vs `Library/*/build/`** — if Library has the canonical PDFs, archive local
2. **Diff `experiments/` vs `Technical-Work/Killing-Form/experiments/`** — migrate any unique files, then archive
3. **Verify `v07_design.md` is in `Technical-Work/Killing-Form/documentation/`** — if not, copy first
4. **`latex_build/` is regenerable** — safe to delete after confirming Library pipeline works
5. **Move trajectory JSONs into `Technical-Work/Killing-Form/results/`** if not already there
6. **Final step:** rename dir to `_DEPRECATED_Corpus_Perspectival/` so it's visible-but-not-active for one more cycle, then delete next session

## Why Not Done Tonight

Clayton's authorization was "do that one carefully" — this is substantial work that benefits from a wake-session that can verify each diff before deleting. The cost of a wrong delete (lost in-progress drafts) outweighs the cost of one more cycle of clutter.

Inventory written: 2026-04-17 ~02:50 AM PST (overnight execution scope, post-renovation)
