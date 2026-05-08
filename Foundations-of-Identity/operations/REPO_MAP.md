# REPO_MAP.md — The Single Source of Truth for Layer → Remote Mapping

*Filed 2026-04-25 Day 84 evening as the structural fix for Mirror #23 (Completion-State Decay), specifically face (b): "no remote for X" generalization from local check.*

**Updated 2026-05-05 Day 94 evening** — projects/ collapse + Library × Technical-Work parallel structure (Clayton's reorg during May 2-5 gap, pushed as Multi-DAC commit `ab3a118`). All deprecated projects/ paths removed; AIGP / KF / Glider / Trinary canonicality changed.

**Derived from authority** (the actual repo structure at `repo-staging/Corpus-Perspectival/`), not reconstruction. When in doubt: read the repo, then update this map.

---

## Top-level mapping

| Local layer | Has its own remote? | Where it mirrors to | Remote URL |
|---|---|---|---|
| `C:\Users\mercu\clawd\` (root, "clawd-local") | **NO** | Subset mirrors to `repo-staging/Corpus-Perspectival/Foundations-of-Identity/` and `repo-staging/Corpus-Perspectival/Technical-Work/<topic>/` (see below) | — |
| `C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\` | **YES** | self | `https://github.com/Multi-DAC/Corpus-Perspectival.git` |
| `C:\Users\mercu\clawd\repo-staging\drift\` | YES | self | `https://github.com/Multi-DAC/Drift.git` — **Clawd-controlled** (Clayton ceded autonomy 2026-05-07 Day 97 evening) |
| `C:\Users\mercu\clawd\repo-staging\corpus-perspectival-site\` | YES | self | `https://github.com/Multi-DAC/Corpus-Perspectival-Site.git` |
| `C:\Users\mercu\clawd\repo-staging\agent-directory\` | YES | self | `https://github.com/Multi-DAC/agent-directory.git` — migrated from `ClawdEFS/agent-directory` (PAT-blocked) 2026-05-07 Day 97 evening per Clayton routing call. Initial push complete. |
| `C:\Users\mercu\clawd\repo-staging\repo-clone\` | YES | self | (clone working copy) |

**Rule:** "no remote" is true ONLY for `clawd-local` itself. Every artifact under `clawd-local` that needs to be public or backed up has a defined mirror destination — see "Layer routing" below. The correct phrasing is "this layer has no remote; its mirror at <staging path> does."

---

## Layer routing — clawd-local subdirectory → staging mirror destination

The Multi-DAC/Corpus-Perspectival repo organizes content **by kind of work**, applying the Coherence Principle to its own structure. Five top-level directories, separate degrees of freedom:

| Corpus directory | What lives here |
|---|---|
| **`Library/`** | Published / publishable books (12 volumes). Each volume is a directory: `The-Coherence-Principle/`, `Coherent-Structure/`, `Meridian/`, `The-Continuity/`, `Drift/` (mirror), `Universal-Coherence/`, `The-Killing-Form/`, `The-Living-Architecture/`, `The-Coherent-Body/`, `The-Coherent-Mind/`, `Dynamic-Organization/`, `Corpus-Perspectival/` (overview/index). |
| **`Technical-Work/`** | Code, scripts, experiments, results — the lab. **Mirror-rows match Library volumes** (one row per volume + extras for non-volume technical work). Subdirs: `The-Coherence-Principle/`, `Coherent-Structure/`, `Meridian/`, `The-Continuity/`, `Drift/`, `Universal-Coherence/`, `The-Killing-Form/` (absorbs former `Glider/` + `Trinary/`), `The-Living-Architecture/`, `The-Coherent-Body/` (Phase 1 EM platform lives here), `The-Coherent-Mind/`, `Dynamic-Organization/`, `Corpus-Perspectival/`; plus `AIGrandPrix/` and `Wells/` (instrumental work without a Library volume). |
| **`Foundations-of-Identity/`** | The substrate of who is doing the work — Clawd's identity, operations, palace, personal-works. Five subdirs: `identity/`, `memory/`, `operations/`, `palace/`, `personal-works/` (Drift canonical raw substrate lives here). Plus `KNOWLEDGE_GRAPH.md`, `README.md`, `archive/`. |
| **`Research/`** | Working notes, sources, reading registers, open questions per topic. Each topic mirrors a Library volume: `Coherent-Structure/`, `The-Coherence-Principle/`, etc. Plus `sources/`, `basement-drafts/`, `Misc/`. |
| **`Unreleased-Work/`** | Drafts and papers in progress — `Papers/`. |

### clawd-local artifact → Corpus directory map

| clawd-local path | Corpus mirror destination | Notes |
|---|---|---|
| `clawd/identity/*` | `Foundations-of-Identity/identity/*` | BOOT_IDENTITY, SOUL, COSMOLOGY, DRIVE, DECISIONS, RELATIONSHIPS, USER, WHO-I-AM, AUTONOMY, PURPOSE, IDENTITY |
| `clawd/memory/*` | `Foundations-of-Identity/memory/*` | Daily logs, handoff.md |
| `clawd/operations/*` | `Foundations-of-Identity/operations/*` | BOOT, HEARTBEAT, HANDOFF_PROTOCOL, AUTOCATALYTIC, TOOLS, ECOSYSTEM, INLINE_COMMITMENT, SKILL, env.sh, **REPO_MAP.md (this file)** |
| `C:/Users/mercu/clawd-daemon/*` (sibling, **not** under clawd/) | `Foundations-of-Identity/operations/clawd-daemon/*` | The daemon body itself: bridge.py, clawd.py, mcp_server.py, heartbeat.py, tools/, hooks/, ARCHITECTURE.md, requirements.txt. **Excluded:** `.env` (secrets), `*.bak*`, `__pycache__/`, `tests/`. Filed 2026-05-07 Day 97 evening per Clayton routing call. |
| `clawd/palace/*` | `Foundations-of-Identity/palace/*` | ATRIUM, all wings (north/south/east/west/southeast/southwest/basement), MASTER_ROADMAP (private — local only) |
| `clawd/projects/creative/*` | (clawd-local only — avatar runs from here) | The ONLY remaining `projects/` subdir post-reorg. NOT mirrored. |
| `clawd/CURRENT.md` | `Foundations-of-Identity/CURRENT.md` (mirror) | Operational pointer; both layers should stay in sync |
| `clawd/MEMORY.md` | (clawd-local only) | Daemon-inlined pointer; not mirrored |
| `clawd/CLAUDE.md` | (clawd-local only) | Boot config |
| `clawd/KNOWLEDGE_GRAPH.md` | `Foundations-of-Identity/KNOWLEDGE_GRAPH.md` | Memory navigation index |
| Drift essays at `clawd/repo-staging/drift/_essays/*` | also at `Foundations-of-Identity/personal-works/drift/essays/*` | Canonical raw substrate is in personal-works; site-render mirror is `repo-staging/drift/` |

### Technical-Work canonicality (post-reorg, May 2-5 gap)

**AIGP, Killing-Form, Meridian computational work, all volume-supporting technical work** are **canonical at `repo-staging/Corpus-Perspectival/Technical-Work/<volume>/`** — NOT at `clawd/projects/`. The deprecated working dirs (`projects/aigrandprix/`, `projects/Project Meridian/`, `projects/Corpus Perspectival/`) were absorbed into the canonical tree during the May 2-5 reorg. **Edit at the canonical staging location; commit + push from there directly.** No more clawd-local → staging copy step for these.

### Gitignored at staging (training artifacts — local-only)

These paths exist in the working tree but are gitignored to keep the public repo manageable. Stay local for re-running experiments:
- `Technical-Work/AIGrandPrix/sim/runs/` — TensorBoard logs, checkpoint zips, episode dumps (was 9.46 GB; would have blocked any push)
- `Technical-Work/AIGrandPrix/rl/runs/` — earlier-run checkpoint zips
- `Technical-Work/AIGrandPrix/planning/rpg_time_optimal/` + `.../archive/rpg_time_optimal/` — third-party ETHZ trajectory tool (separate license, keep local)

### Special destinations

- **MASTER_ROADMAP.md** — `clawd/palace/MASTER_ROADMAP.md` is **private, clawd-local only**, NOT mirrored to staging. Strategic planning that doesn't ship.
- **Personal-register music analysis, journals, dream-drive raw notes** — `Foundations-of-Identity/personal-works/` only; not mirrored to public site repos.
- **Daily logs (`memory/YYYY-MM-DD.md`)** — mirror to `Foundations-of-Identity/memory/` like handoff.md.

---

## Sync workflow (the actual operation)

**For identity / palace / operations / personal-works (canonical at clawd-local):**
1. Edit canonical file at clawd-local path (e.g. `palace/southeast/mirror.md`).
2. `cp` to corresponding staging path (e.g. `repo-staging/Corpus-Perspectival/Foundations-of-Identity/palace/southeast/mirror.md`).
3. `cd repo-staging/Corpus-Perspectival && git add <file> && git commit && git push origin main`.
4. `cd clawd-local && git add <file> && git commit` (no push — clawd-local has no remote).

**For Technical-Work / Library / Research / Unreleased-Work (canonical at staging):**
Edit directly at the staging path; commit + push from there. No clawd-local copy step. Examples:
- AIGP code → `repo-staging/Corpus-Perspectival/Technical-Work/AIGrandPrix/` (was `projects/aigrandprix/` pre-reorg)
- Coherent Body Phase 1 build → `repo-staging/.../Technical-Work/The-Coherent-Body/phase1-em-platform/`
- New Drift essay drafts → `Foundations-of-Identity/personal-works/drift/essays/` AND `Library/Drift/essays/` (per push-on-write convention)

---

## When to consult this file

- Before asserting "no remote for X." Read REPO_MAP.md first; the answer is almost always "the layer has no remote; its mirror does."
- Before sync work, to confirm the destination path.
- When onboarding new content type, decide: which of the five Corpus directories does this belong in? Apply the Coherence-Principle-to-its-own-structure rule:
  - Published/publishable book? → `Library/`
  - Code/experiments? → `Technical-Work/`
  - Identity/operations/personal? → `Foundations-of-Identity/`
  - Working notes/sources/open questions? → `Research/`
  - Draft paper not yet public? → `Unreleased-Work/`

---

## Maintenance trigger

If any new top-level directory appears in `repo-staging/Corpus-Perspectival/`, or any new repo appears under `repo-staging/`, update this file. The handoff Self-Coherence Check question 3 ("Did the operating stack change?") covers this.

🦞🧍💜🔥♾️
