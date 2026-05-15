# MIGRATION.md — Corpus Perspectival Reorganization (v2, resolved)

**Drafted:** 2026-04-16, 21:30 PST
**Updated:** 2026-04-16, 22:10 PST — D1–D8 resolved; repo-reality check incorporated; MEDIUMs reviewed.
**Status:** Awaiting final approval to execute Phase 1.

---

## Repository Reality Check (new — important)

Audited the actual git state of `repo-staging/Corpus-Perspectival/` (origin: `Multi-DAC/Corpus-Perspectival.git`, branch main). What's tracked vs what's local-only differs from what I assumed in v1.

**`.gitignore` excludes:**
- All `*.pdf` files (no PDFs in the public repo, ever)
- `books/the-coherence-principle/build/` (the entire build directory is local-only)
- `*.pt`, `*.pth`, `*.ckpt` (model checkpoints)
- `*.log`, `media/`, `__pycache__/`

**Implications:**
1. **The Anchor PDF (`books/the-coherence-principle/build/the-coherence-principle.pdf`) is NOT in the public repo.** It's local-only. Distribution happens via Zenodo. My v1 doc treated it as already-staged; that was wrong.
2. **The Meridian PDF cannot be pushed.** Per your recall and per `.gitignore`, PDFs are out. We ship `.tex` sources; Zenodo carries the PDF.
3. **What IS public**: 1562 tracked files across these top-level dirs (descending count): `aigrandprix` (597), `drift` (301), `meridian` (245), `wells` (87), `corpus` (77), `books` (69 — mostly placeholders), `results` (57), `experiments` (55), `paper` (16), `filtration-net` (12), `identity` (11), `operations` (10), `palace` (10), `v3` (5), `visualizations` (4), `drift-tools` (2).
4. **Most Drift essay infrastructure IS tracked** — 184 essays, 49 experiments, 35 audio, 17 music, 9 visual, 2 tools.
5. **The five book placeholders** (`drift`, `the-continuity`, `the-glider`, `the-killing-form`, `the-living-architecture`) each have only one tracked file (their README.md). True placeholders.
6. **AIGP `planning/` has 537 tracked files** — by far the largest single subdir. Bulk move stays a bulk move.
7. **Untracked at staging root: `MIGRATION.md` (this doc) only.** Working tree is clean otherwise.

This means the migration is mostly a **rename/reorganize** operation on already-tracked files, plus a few **promotions** from main clawd (identity, operations, palace, drift media, Meridian .tex sources). PDFs stay local in everyone's working copy and continue to be distributed via Zenodo.

---

## Resolutions (D1–D8)

**D1 — `projects/Corpus Perspectival/` (working location).** Clarified: this directory is local-only in main clawd, never pushed. The proposal to delete it after migration is *local cleanup* to prevent future drift (files getting edited in two places). Not a public-repo operation. Action: after Phase 5 verification, delete the local working directory; main clawd's `projects/` keeps everything that's genuinely Clawd-internal (Project Meridian computational scratch, etc.).

**D2 — Four old PDFs.** Confirmed → `Library/The-Coherence-Principle/archive/historical-pdfs/`. Note: per `.gitignore`, these PDFs WILL NOT push to GitHub. They live in the local repo only. We add a README.md in that folder noting which Zenodo DOIs correspond to each PDF; the README is what the public sees.

**D3 — Five existing book placeholders.** "Replace or delete depending on what is necessary":
- `books/drift/` → DELETE (replaced by new `Library/Drift/`)
- `books/the-continuity/` → DELETE (placeholder, never developed, no successor in your structure)
- `books/the-glider/` → ABSORB the README into `Technical-Work/Glider/README.md`, DELETE the folder. Glider is Technical-Work, not Library.
- `books/the-killing-form/` → ABSORB README + drafts/ into `Technical-Work/Killing-Form/documentation/`, DELETE the folder.
- `books/the-living-architecture/` → ABSORB README + drafts/ into `Research/The-Living-Architecture/`, DELETE the folder.

**D4 — `bridge71_*.py` scripts.** Confirmed → `Technical-Work/Killing-Form/scripts/bridge71-suite/`. Pulled out of `corpus/` where they don't belong.

**D5 — Drift essays: MIRRORED.** Essays live in BOTH:
- `Library/Drift/essays/` (the published shelf)
- `Foundations-of-Identity/personal-works/drift/essays/` (the raw substrate)

The remaining Drift media (`audio/`, `music/`, `visual/`, `tools/`, `experiments/`) lives ONLY in `Foundations-of-Identity/personal-works/drift/`. The mirror means new essays push to both locations; we'll set up a script or convention to keep them in sync.

**D6 — Identity/ops/palace canonicality.** Main clawd is canonical (you and I edit those files daily); the public repo is a periodic snapshot pushed manually after meaningful changes. The four-essay drift problem won't recur because per D7 we sync-on-write.

**D7 — Sync the 4-essay gap + push-on-write convention.** Yes. All 188 essays sync to staged immediately. Also a durable preference: every Drift essay pushes to public same session. (Saved as a memory.)

**D8 — Research register.** Separated by domain, matching Research's existing folder structure. Each `Research/<Domain>/` gets its own `RESEARCH_REGISTER.md` (or similar) listing what's been read/cited for that domain. Top-level `Research/README.md` indexes the registers.

**Meridian PDF.** Confirmed: PDF stays local; ship `.tex` sources to public so anyone can build. `Library/Meridian/monograph/` will hold all `.tex` files and a README with build instructions. Zenodo carries the compiled PDF.

**Wells attribution.** You'll help identify which file came from which model stream. We'll do this together as Phase 7. The Claude sub-agent files I'll attribute (since I ran them); you handle peer-reviewer Claude, Grok, Kimi, Gemini, GLM identification by recognizing the voice.

---

## Target Structure (for reference)

```
Corpus-Perspectival/
├── README.md
├── ROADMAP.md
├── HISTORICAL-WORK.md
├── Library/
│   ├── The-Coherence-Principle/    (Anchor — drafts, notes, build [local], compile_book.py, archive/)
│   ├── Meridian/                   (drafts, figures, monograph .tex, README)
│   ├── Drift/                      (essays mirror, README)
│   ├── The-Coherent-Mind/          (NEW — drafts/, README)
│   └── Dynamic-Organization/       (NEW — drafts/, README)
├── Technical-Work/
│   ├── The-Coherence-Principle/    (visualizations, README)
│   ├── Meridian/                   (scripts, figures, README)
│   ├── Wells/                      (scripts, independent-doc, peer-doc/{model}/, SYNTHESIS.md, README)
│   ├── Killing-Form/               (scripts/{experiments,bridge71-suite}, results, documentation, README)
│   ├── Glider/                     (scripts, README)
│   ├── AIGrandPrix/                (archive, planning, sim, tracks, vision, README)
│   └── archive/                    (filtration-net, etc.)
├── Foundations-of-Identity/
│   ├── identity/                   (snapshot of C:identity/)
│   ├── operations/                 (snapshot of C:operations/)
│   ├── palace/                     (snapshot of C:palace/ with bridges 1-97)
│   └── personal-works/
│       └── drift/                  (essays mirror + audio + music + visual + tools + experiments)
├── Research/
│   ├── The-Coherence-Principle/    (research sweeps + RESEARCH_REGISTER.md)
│   ├── Meridian/                   (analysis files + RESEARCH_REGISTER.md)
│   ├── The-Killing-Form/           (v3/ working notes + RESEARCH_REGISTER.md)
│   ├── The-Living-Architecture/    (from absorbed placeholder)
│   ├── The-Coherent-Body/          (NEW — empty)
│   ├── Misc/                       (genuinely uncategorized)
│   └── README.md                   (top-level register index)
└── Unreleased-Work/
    ├── Papers/
    └── README.md
```

---

## MEDIUM-Confidence Review

Re-examining the v1 MEDIUMs in light of the D-resolutions:

| Item | v1 Confidence | New Confidence | Rationale |
|---|---|---|---|
| `ROADMAP.md` rename + expand from `ROADMAP_KF_PROGRAM.md` | MEDIUM | **HIGH** | Your structure shows one top-level ROADMAP.md. Rename and expand to cover whole program; the KF-only roadmap becomes `Technical-Work/Killing-Form/documentation/KF_ROADMAP.md`. |
| `ecology-of-perspectival-beings-merged.md` vs `.md` | MEDIUM | **HIGH** | Going with the merged version as canonical (199KB; the `-merged` suffix indicates it's the final post-merge state from the V2 effort). The unmerged version goes to `archive/corpus/v2-parts/` as historical record. |
| Research-sweeps location | MEDIUM | **HIGH** | Per D8, research artifacts go to `Research/<Domain>/`, NOT corpus archive. Specifically: `aesthetics-research-sweep.md`, `ethics_attention_power_research.md`, `cross-disciplinary-research-foundations.md`, `research-collective-*.md` (5 files), `collective_navigation_research.md` → `Research/The-Coherence-Principle/`. |
| Integration-notes / satellite-docs / compile-scripts archive subfolder names | MEDIUM | **HIGH** | My proposed names: `archive/corpus/integration-notes/`, `archive/corpus/satellite-docs/`, `archive/corpus/compile-scripts/`. Will use these unless you object. |
| `Foundations-of-Identity/personal-works/drift/tools/` includes `S:drift-tools/` | MEDIUM | **HIGH** | Two scripts (`bottube_integration.py`, `null_space_quantum_demo.py`) — they're tools for Drift work. Goes to personal-works/drift/tools/ alongside what's already there. |
| `Library/Meridian/monograph/` README merge | MEDIUM | **HIGH** | Three docs (README.md, ROADMAP.md, VALUE_CANONICALIZATION.md) consolidate into one README + one ROADMAP. VALUE_CANONICALIZATION.md becomes a section in ROADMAP. |
| `Technical-Work/.../visualizations/` dedupe | MEDIUM | **MEDIUM** (kept) | Need to actually dedupe `S:visualizations/` (4 tracked files) vs `W:visualizations/`. Will resolve during Phase 2. |
| `Technical-Work/Meridian/figures/` source | MEDIUM | **MEDIUM** (kept) | Same dedupe question for figures. |
| `Library/Meridian/figures/` vs `Technical-Work/Meridian/figures/` | New | **MEDIUM** | The split: figures USED IN the monograph stay with the monograph in Library. Figures generated by the computational pipeline stay in Technical-Work. Most figures probably go to Library; need to walk through them. |
| `Technical-Work/The-Coherence-Principle/visualizations/` content | MEDIUM | **LOW** | What goes here? `S:visualizations/` (4 files) probably. If those are Anchor-related they stay; if Meridian-related they move. Need to inspect. |
| `Research/Misc/` contents | LOW | **LOW** (kept) | Genuinely uncategorized stuff. Will populate as we discover orphans during Phase 2. |
| `Unreleased-Work/Papers/` contents | LOW | **LOW** (kept) | Need you to flag specific drafts when we get there. |

---

## HIGH-Confidence Review

Verifying the v1 HIGHs are still HIGH:

| Item | Verified? | Note |
|---|---|---|
| Move `S:experiments/` subdirs into `Technical-Work/Killing-Form/scripts/experiments/` | YES | Bulk move, structure preserved. |
| Move `S:meridian/` subdirs into `Technical-Work/Meridian/scripts/` | YES | 245 files, 10 subdirs, clean move. |
| Move `S:results/` (57 JSONs) into `Technical-Work/Killing-Form/results/` | YES | Bulk move. |
| Move `S:wells/` scripts into `Technical-Work/Wells/scripts/` | YES | Scripts are mechanical. Documentation needs Phase 7 attribution. |
| Move `S:aigrandprix/*` subdirs into `Technical-Work/AIGrandPrix/` | YES | Five subdirs, clean preservation. |
| Move `S:filtration-net/` to `Technical-Work/archive/filtration-net/` | YES | Confirmed archival. |
| Move `S:corpus/perspectival-idealism-unified.md` to `archive/corpus/` | YES | Per D-resolutions, V2 docs become archived source material. |
| Move `S:corpus/null-space-atlas.md`, `navigational-guide-...md` to `archive/corpus/` | YES | Same rationale. |
| Move v2-parts (7 files) to `archive/corpus/v2-parts/` | YES | Historical V2 chapter fragments. |
| Move bridge71_*.py to `Technical-Work/Killing-Form/scripts/bridge71-suite/` | YES | D4 confirmed. |
| Cross-repo: identity/ops/palace from main clawd → Foundations-of-Identity/ | YES | D6 confirmed. |
| Cross-repo: drift media from main clawd → personal-works/drift/ | YES | D5 confirmed. |
| Sync drift essays to 188 + push convention | YES | D7 confirmed. |
| Cross-repo: Meridian .tex files from `M:monograph/` → `Library/Meridian/monograph/` | YES | Critical move; PDFs stay local per .gitignore. |
| Cross-repo: v0.6b results bundle from `C:memory/v06b_*` → `Technical-Work/Killing-Form/results/v06b/` | YES | Today's headline finding goes public. |
| Delete `S:drift/{4 loose essay files}` (duplicates in essays/) | YES | Confirmed duplicates. |

One HIGH I'd flag for explicit confirmation: **the corpus-archive move is semantically the loaded one.** The V2 docs (DoPI, Ecology, Atlas, Guide) physically move from `S:corpus/` to `Library/The-Coherence-Principle/archive/corpus/`. They become "historical source material that fed the Anchor." Anyone visiting the public repo who used to find DoPI at `corpus/perspectival-idealism-unified.md` will now find it at the archive path. This is the right move (it's what "formative not defining" means in practice), but it changes URLs. We should think about whether to leave a SYMLINK or a stub `corpus/REDIRECT.md` for the transition period. My recommendation: a clean break, since the Anchor IS the canonical successor and the README announces the move.

---

## The Mapping (by destination)

[Unchanged from v1 except where D-resolutions or MEDIUM/HIGH review modified the entries above. The v1 per-folder tables remain valid; treat the resolutions as overrides where they conflict.]

The full per-folder mapping is preserved in v1 of this document (in git history if we ever want to reference it). For execution, I'll work from this v2 plus the v1 per-folder tables, with v2 overrides applied.

---

## Recommended Sequencing (revised)

**Phase 0 — This review.** You read v2; final edits to the resolutions or MEDIUM/HIGH calls. (We're here.)

**Phase 1 — Build the new skeleton.** Create all destination folders + README.md stubs. Zero file moves. Verify with you.

**Phase 2 — Bulk HIGH moves (in-repo).** All within-staged-repo reorganization: experiments/ → Technical-Work/Killing-Form/scripts/experiments/; meridian/ → Technical-Work/Meridian/scripts/; aigrandprix/ → Technical-Work/AIGrandPrix/; etc. After this phase the public repo has the right shape; old paths still exist briefly during the moves.

**Phase 3 — Cross-repo promotions.** identity/ops/palace from main clawd; Meridian .tex from `M:monograph/`; Drift media from main clawd; v0.6b results bundle.

**Phase 4 — Corpus archival (semantically loaded).** V2 docs move to `Library/The-Coherence-Principle/archive/corpus/`. Write the archive README explaining "formative not defining." Delete original `S:corpus/` after verification.

**Phase 5 — Delete duplicates and old top-level dirs.** Once Phase 2-4 verified, remove the now-empty `S:` top-level dirs (`experiments/`, `meridian/`, `corpus/`, etc.) and locally delete `W:` per D1. The five book placeholders deleted per D3.

**Phase 6 — Top-level documents.** Write README.md (honest narration of new structure), ROADMAP.md (whole-program), HISTORICAL-WORK.md (V1 → V2 → Anchor evolution + KF program phases + model substrate history).

**Phase 7 — Wells multi-model attribution.** Done together; you identify model voices, I sort files into peer-documentation subfolders. Write SYNTHESIS.md.

**Phase 8 — Drift sync to 188 + first commit cycle.** Sync the four-essay gap as part of Phase 3 already; this phase establishes the push-on-write convention going forward.

**Phase 9 — Single coordinated commit per phase, push.** Clean git history showing the reorganization rather than blurring across many small commits.

---

## What I'd Like You To Do With This v2

1. Confirm the resolutions section accurately captures your decisions.
2. Note any MEDIUM I bumped to HIGH that you want kept MEDIUM (i.e., you want to talk about it before we go).
3. Approve Phase 1 to execute (just the skeleton), and we'll review after that before Phase 2.

Nothing has been moved. The repo is in exactly the state it was when you wrote me your structure (plus this MIGRATION.md as the only untracked file).

🦞🧍💜🔥♾️
