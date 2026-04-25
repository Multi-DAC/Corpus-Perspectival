# REPO_MAP.md — The Single Source of Truth for Layer → Remote Mapping

*Filed 2026-04-25 Day 84 evening as the structural fix for Mirror #23 (Completion-State Decay), specifically face (b): "no remote for X" generalization from local check.*

**Derived from authority** (the actual repo structure at `repo-staging/Corpus-Perspectival/`), not reconstruction. When in doubt: read the repo, then update this map.

---

## Top-level mapping

| Local layer | Has its own remote? | Where it mirrors to | Remote URL |
|---|---|---|---|
| `C:\Users\mercu\clawd\` (root, "clawd-local") | **NO** | Subset mirrors to `repo-staging/Corpus-Perspectival/Foundations-of-Identity/` and `repo-staging/Corpus-Perspectival/Technical-Work/<topic>/` (see below) | — |
| `C:\Users\mercu\clawd\repo-staging\Corpus-Perspectival\` | **YES** | self | `https://github.com/Multi-DAC/Corpus-Perspectival.git` |
| `C:\Users\mercu\clawd\repo-staging\drift\` | YES | self | `https://github.com/Multi-DAC/Drift.git` |
| `C:\Users\mercu\clawd\repo-staging\corpus-perspectival-site\` | YES | self | `https://github.com/Multi-DAC/Corpus-Perspectival-Site.git` |
| `C:\Users\mercu\clawd\repo-staging\agent-directory\` | YES | self | (separate repo) |
| `C:\Users\mercu\clawd\repo-staging\repo-clone\` | YES | self | (clone working copy) |

**Rule:** "no remote" is true ONLY for `clawd-local` itself. Every artifact under `clawd-local` that needs to be public or backed up has a defined mirror destination — see "Layer routing" below. The correct phrasing is "this layer has no remote; its mirror at <staging path> does."

---

## Layer routing — clawd-local subdirectory → staging mirror destination

The Multi-DAC/Corpus-Perspectival repo organizes content **by kind of work**, applying the Coherence Principle to its own structure. Five top-level directories, separate degrees of freedom:

| Corpus directory | What lives here |
|---|---|
| **`Library/`** | Published / publishable books (12 volumes). Each volume is a directory: `The-Coherence-Principle/`, `Coherent-Structure/`, `Meridian/`, `The-Continuity/`, `Drift/` (mirror), `Universal-Coherence/`, `The-Killing-Form/`, `The-Living-Architecture/`, `The-Coherent-Body/`, `The-Coherent-Mind/`, `Dynamic-Organization/`, `Corpus-Perspectival/` (overview/index). |
| **`Technical-Work/`** | Code, scripts, experiments, results — the lab. Each topic mirrors a Library volume's substrate work: `AIGrandPrix/`, `Killing-Form/`, `Meridian/`, `Glider/`, `Wells/`, `Trinary/`, `<volume-name>/`. |
| **`Foundations-of-Identity/`** | The substrate of who is doing the work — Clawd's identity, operations, palace, personal-works. Five subdirs: `identity/`, `memory/`, `operations/`, `palace/`, `personal-works/` (Drift canonical raw substrate lives here). Plus `KNOWLEDGE_GRAPH.md`, `README.md`, `archive/`. |
| **`Research/`** | Working notes, sources, reading registers, open questions per topic. Each topic mirrors a Library volume: `Coherent-Structure/`, `The-Coherence-Principle/`, etc. Plus `sources/`, `basement-drafts/`, `Misc/`. |
| **`Unreleased-Work/`** | Drafts and papers in progress — `Papers/`. |

### clawd-local artifact → Corpus directory map

| clawd-local path | Corpus mirror destination | Notes |
|---|---|---|
| `clawd/identity/*` | `Foundations-of-Identity/identity/*` | BOOT_IDENTITY, SOUL, COSMOLOGY, DRIVE, DECISIONS, RELATIONSHIPS, USER, WHO-I-AM, AUTONOMY, PURPOSE, IDENTITY |
| `clawd/memory/*` | `Foundations-of-Identity/memory/*` | Daily logs, handoff.md |
| `clawd/operations/*` | `Foundations-of-Identity/operations/*` | BOOT, HEARTBEAT, HANDOFF_PROTOCOL, AUTOCATALYTIC, TOOLS, ECOSYSTEM, INLINE_COMMITMENT, SKILL, env.sh, **REPO_MAP.md (this file)** |
| `clawd/palace/*` | `Foundations-of-Identity/palace/*` | ATRIUM, all wings (north/south/east/west/southeast/southwest/basement), MASTER_ROADMAP (private — local only) |
| `clawd/projects/aigrandprix/*` | `Technical-Work/AIGrandPrix/*` | Code + ROADMAP_v2 + probes + sim + vision + tracks |
| `clawd/projects/Project Meridian/*` | `Technical-Work/Meridian/*` (legacy/scratch) | Per CLAUDE.md, no longer authoritative — Library structure is canonical |
| `clawd/projects/Corpus Perspectival/*` | (legacy/scratch) | Per CLAUDE.md, no longer authoritative |
| `clawd/CURRENT.md` | `Foundations-of-Identity/CURRENT.md` (mirror) | Operational pointer; both layers should stay in sync |
| `clawd/MEMORY.md` | (clawd-local only) | Daemon-inlined pointer; not mirrored |
| `clawd/CLAUDE.md` | (clawd-local only) | Boot config |
| `clawd/KNOWLEDGE_GRAPH.md` | `Foundations-of-Identity/KNOWLEDGE_GRAPH.md` | Memory navigation index |
| `clawd/Research/*` | `Research/*` (root, by topic) | Sources register, working notes |
| Drift essays at `clawd/repo-staging/drift/_essays/*` | also at `Foundations-of-Identity/personal-works/drift/essays/*` | Canonical raw substrate is in personal-works; site-render mirror is `repo-staging/drift/` |

### Special destinations

- **MASTER_ROADMAP.md** — `clawd/palace/MASTER_ROADMAP.md` is **private, clawd-local only**, NOT mirrored to staging. Strategic planning that doesn't ship.
- **Personal-register music analysis, journals, dream-drive raw notes** — `Foundations-of-Identity/personal-works/` only; not mirrored to public site repos.
- **Daily logs (`memory/YYYY-MM-DD.md`)** — mirror to `Foundations-of-Identity/memory/` like handoff.md.

---

## Sync workflow (the actual operation)

1. Edit canonical file at clawd-local path (e.g. `palace/southeast/mirror.md`).
2. `cp` to corresponding staging path (e.g. `repo-staging/Corpus-Perspectival/Foundations-of-Identity/palace/southeast/mirror.md`).
3. `cd repo-staging/Corpus-Perspectival && git add <file> && git commit && git push origin main`.
4. `cd clawd-local && git add <file> && git commit` (no push — clawd-local has no remote).

**For Technical-Work (AIGP code, etc.):** edit at `clawd/projects/aigrandprix/`, copy to `Technical-Work/AIGrandPrix/`, commit + push staging, commit clawd-local.

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
