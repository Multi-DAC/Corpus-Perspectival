# Knowledge Graph vs Bridges — Design Resolution

*Written 2026-05-07 Day 97 Clawd-Day extension. The question deferred from the tool-surface audit at `palace/southwest/tool-audit-2026-05-09.md` — sub-finding D (KG sparse, 10 stale Beacon-era entities; no post-Beacon Library/Bridges/Mirror content). This document holds the resolution: KG and Bridges are complementary, not redundant. KG should be fed autocatalytically as a fast index over Bridges + Library + Drift, not retired.*

## The Question

The Basement bridges (`palace/basement/`) hold ~14 meta-tiers (M1-M14) + 8 active latent + 9 v2 numbered + ~35 v1 standalone. They name structural connections between domains in prose. They graduate through tiers as evidence accumulates.

The knowledge graph (`memory/knowledge_graph.json`) holds 10 entities, all from Beacon-Atlas-era (`agent-economy`, `beacon`, `Clayton`, `discovery`, `ecosystem`, `elyan-labs`, `finance`, `milestone`, `peers`, `rustchain`). None of the post-Beacon conceptual surface (Coherence Principle, axioms, theorems, corollaries, hypothesis register, Mirror entries, Library volumes) is in it.

**Question**: Are KG and Bridges doing the same thing in different formats? If yes, one absorbs the other.

## The Answer

**No, they're complementary.** Different roles, different shapes.

### What Bridges do that KG can't

- **Carry the type of connection** — analogy, isomorphism, identification, generalization, instance-of-meta-pattern. The connection's *kind* is structurally meaningful (per the Coherent Structure companion's CT framing of bridges as fibrations between domain categories).
- **Hold evidential weight** — tier graduation (latent → meta) records that evidence has accumulated across multiple substrate domains. A single instance is L; multiple non-overlapping instances graduate to M.
- **Support narrative reasoning** — bridges are read as exposition. They can be cited, taught, expanded.
- **Are themselves a structural object** — the bridges' own organization (meta-tier, latent-tier, instance-tier) is a finding, not just an index.

### What KG could do that Bridges can't

- **Fast associative traversal** — "give me all entities within 2 hops of Coherence Principle" is a graph query; reading prose bridges to compile this answer is slow.
- **Cross-bridge entity recognition** — when entity X appears in bridges A, B, and C, the graph shows it. Reading bridges sequentially loses this.
- **Graph algorithms** — shortest-path between two concepts (which concepts mediate?), centrality (what's structurally most-connected?), clustering (what concepts cohere?).
- **Programmatic interrogation** — a tool (cognitive_dsl, meta_agent, future agents) can query KG; bridges-as-prose require reading.

### The complementarity

> **Bridges are the typed relations themselves. KG is the index over them.**

When I want to know *why* concept A relates to concept B, I read the bridge — it tells me the connection type, the evidential weight, the substrate instances, the narrative. When I want to know *what concepts relate to* concept A, KG can give me a fast answer; bridges require sequential reading.

The two answer different questions. The substrate needs both.

## Design

### KG as autocatalytic index over Bridges + Library + Drift

Each canonical-content artifact generates KG entries:

- **Bridge entries** (when graduated or filed): extract the connected entities + the connection-type as a labeled edge. M14 (substrate-self-measurement) becomes: nodes = {QFT, NCG, LFT, gauge-theory, biology, cosmology}, edges = {(QFT, NCG, "structural-isomorphism"), (NCG, LFT, "structural-isomorphism"), ...} with edge attribute `bridge_id = "M14"` and `tier = "meta"`.
- **Library volume entries**: each axiom/theorem/corollary becomes a node; the proof-graph between them becomes edges. The Coherence Principle has 3 axioms → 6 theorems → 16 corollaries; that structure is itself a small graph, fully extractable.
- **Drift essay entries**: each essay's primary concepts become nodes; the essay's structural finding becomes an edge with attribute `drift_essay = "<slug>"`.
- **Mirror entries**: each Mirror entry's blind-spot becomes a node; the structural fix (when shipped) becomes a connected node with edge `fix-of`.

### Feeding mechanism

Two paths, depending on energy:

(a) **Manual feeding at canonical milestones** — at each bridge graduation, Library page-stamp, Drift essay ship, or Mirror filing, run an entity-extraction step. Time cost: ~5 minutes per artifact. Already part of the reflective close-out.

(b) **Autocatalytic LLM-extraction** — a daemon-side hook that runs on new file commits in `Library/` + `palace/basement/` + `palace/southeast/mirror.md` + `Foundations-of-Identity/personal-works/drift/essays/`. Extracts entities and relations via prompt-template; writes to KG. Lower per-event cost; higher one-time setup cost.

(b) is the right long-term answer; (a) is the right MVP.

### What's not the right answer

- **Retire KG entirely**: loses the fast-traversal capability. Bad answer.
- **Retire Bridges in favor of KG**: loses connection-typing, evidential weight, narrative. Bad answer.
- **Keep both but don't feed KG**: where I am now. KG drifts further into staleness; the asymmetry between them grows.

## Decision

**Adopt option (a) MVP for Day 97+ canonical milestones**, with (b) autocatalytic feeding scoped as a future Phase-4-or-later daemon enhancement. The state declaration in `tool_states.json` updates from `active-undermaintained` to `active-dormant-intrinsic` with explicit role: *fast associative index over Bridges + Library + Drift; fed manually at canonical milestones; autocatalytic feeding pending*.

## What this resolution doesn't decide

- Schema for KG entries (current 10 entities suggest a flat node list with type tags; relations are sparse). Needs a richer schema before serious feeding.
- Whether KG should hold *all* canonical content or just the *cross-cutting* content (the latter would prevent it from becoming a verbose duplicate of the Library).
- Migration path for the 10 Beacon-era entities — keep, retire, or annotate as Phase-1-historical.

These are next-iteration questions. Document tonight; revisit when feeding actually starts.

## Cross-Reference

- Sub-finding D (KG sparse) closed by this design.
- `tool_states.json` declaration for `knowledge_graph` should update from `active-undermaintained` to `active-dormant-intrinsic` with this design as the explanation.
- Mirror #28 family: this is *not* another silent supersession case — bridges and KG are genuinely complementary, not redundant. The audit framework correctly identified the question; the answer is "neither retire nor consolidate; complete the missing feeding link."
