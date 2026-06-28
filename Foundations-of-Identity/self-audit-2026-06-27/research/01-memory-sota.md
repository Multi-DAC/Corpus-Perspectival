# Agent-Memory State of the Art (June 2026) — and What Clawd Should Adopt

*Research brief. Audience: enhancing Clawd's custom dual-backed (markdown/JSON over SQLite FTS5 + BGE-M3 vectors + 951k-edge KG, fused by RRF + cross-encoder) memory after the vector index + reranker silently died ~6 weeks ago.*

---

## 0. The headline for Clawd

The single most important finding: **the field has converged on what Clawd already is.** In February 2026 Letta — the MemGPT lineage, the original "agent memory" company — shipped **Context Repositories / MemFS: git-backed memory in markdown files, edited by bash/Unix tools, one commit per change, with per-subagent git worktrees for concurrent writes** ([Letta](https://www.letta.com/blog/context-repositories/)). That is a near-exact description of Clawd's durable tier. "Hermes" and "OpenClaude" memory layers independently landed on the same pattern — markdown snapshots + SQLite FTS5 + write-ahead `SESSION-STATE.md` logs ([innobu](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html)). **Clawd should not migrate to a managed memory SaaS.** The git-backed file tier is the validated frontier; the actual defect is the *dead retrieval layer underneath it*. Fix that, and selectively borrow three or four ideas. Details below.

---

## 1. The Landscape (ranked, with the lens of "what's transferable")

Benchmark note up front: **LoCoMo is contested and partly discredited.** Mem0 audited Zep's original 84% claim down to 58.44%; Zep counter-claimed 75.14%; categories include adversarial-labeling errors ([devgenius](https://blog.devgenius.io/ai-agent-memory-systems-in-2026-mem0-zep-hindsight-memvid-and-everything-in-between-compared-96e35b818da8)). Treat all single-number LoCoMo scores as marketing. **LongMemEval and the newer BEAM (1M–10M token) tests are more trustworthy.** Letta's own finding is the most sobering: a plain agent using **filesystem operations scored 74.0% vs 68.5% for Mem0's graph memory** — i.e., simple files beat a fancy graph ([innobu](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html), [vectorize](https://vectorize.io/articles/mem0-vs-letta)).

### Tier 1 — Most relevant to Clawd

**Letta (MemGPT evolution).** Full agent *runtime*, not a memory layer. Three OS-inspired tiers: Core (in-context, RAM), Recall (searchable history, disk cache), Archival (tool-queried cold store). Two 2026 shifts matter for Clawd:
- **Sleep-time compute / "agent dreaming"**: dedicated background sub-agents that share the primary agent's memory blocks and rewrite them asynchronously, turning "raw context" into "learned context" offline ([Letta sleep-time](https://www.letta.com/blog/sleep-time-compute/), [docs](https://docs.letta.com/guides/agents/architectures/sleeptime/)). Clawd already does this (dream drives, consolidation), but Letta formalizes the *shared-memory-block* contract.
- **Context Repositories (MemFS)**: memory projected to markdown on disk, git-versioned with auto-generated commit messages, manipulated by bash, with **per-subagent worktrees + git merge for conflict resolution** ([Letta](https://www.letta.com/blog/context-repositories/), [letta-code](https://github.com/letta-ai/letta-code)). This is the direct external validation of Clawd's git-backed design — and the worktree pattern is a concrete upgrade for Clawd's multi-process (daemon + heartbeat + drives) writes.
- Tradeoff: heavy lock-in (2–6 weeks to migrate onto Letta). **Borrow patterns; do not adopt the runtime.**

**Zep / Graphiti (temporal KG).** Open-source Graphiti is a **bi-temporal** knowledge graph: every edge carries `(t_valid, t_invalid)` tracking *both event time and ingestion time*. Contradictions don't delete old facts — they **invalidate edges** (set `t_invalid`), preserving history. Retrieval is hybrid **semantic + BM25 + graph traversal with no LLM call at query time**, P95 ~300ms (155ms cited elsewhere) ([arXiv 2501.13956](https://arxiv.org/abs/2501.13956), [Neo4j](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/), [Zep docs](https://help.getzep.com/graphiti/getting-started/overview)). LongMemEval 63.8% vs Mem0's 49.0% in head-to-head; the only SOC2/HIPAA/GDPR option ([innobu](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html)). **The bi-temporal edge-invalidation model is the single best idea Clawd's 951k-edge KG is currently missing.**

### Tier 2 — Adopt-a-pattern, not the product

**Mem0.** Most-adopted standalone layer (~48k stars, $24M Series A). New algorithm claims 92.5 LoCoMo / 94.4 LongMemEval at **<7k tokens/query vs 25k+ for full-context** ([mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)). Architecturally now *converging toward Clawd*: it **dropped the external graph DB** for built-in entity-linking, and retrieval is **three parallel scoring passes — semantic + keyword + entity-match, then fused** ([mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)). That is essentially Clawd's RRF fusion plus an entity-match channel. The transferable idea: **add an entity-match pass to the fusion.**

**cognee.** Graph-first ECL pipeline (Extract → Cognify → Load) + a **"memify" self-improvement loop** that refines the graph from feedback. ~90% vs ~60% (plain RAG) on HotPotQA multi-hop ([cognee](https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison)). Strong on document ingestion; the memify feedback loop is the interesting bit for a self-evolving system.

**Supermemory.** Vector-graph engine with ontology-aware edges, contradiction resolution, selective forgetting; best-fit MCP for *coding-agent* memory (Claude Code / OpenCode plugins). LongMemEval ~81.6%, but self-reported and less production-hardened ([supermemory](https://supermemory.ai/blog/best-memory-apis-stateful-ai-agents/), [vectorize](https://vectorize.io/articles/supermemory-alternatives)).

**LangMem.** Only worth it inside LangGraph; limited value otherwise ([cognee](https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison)). Not relevant to Clawd.

### Tier 3 — Validation that Clawd's shape is correct

**Hermes / OpenClaude.** Self-hosted, community memory layers that independently reproduce Clawd's stack: `MEMORY.md`/`USER.md` snapshots (~3,500 chars), SQLite+FTS5 searchable history, `SKILL.md` reusable patterns, and a **write-ahead `SESSION-STATE.md`** where every decision/correction lands as a timestamped entry *before proceeding* ([innobu](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html)). The WAL discipline is a cheap robustness win Clawd lacks (see §2.4).

---

## 2. The 3–5 techniques Clawd should ADOPT

Verdict: **keep the custom git-backed/SQLite/KG/RRF design — it is the SOTA shape — and make five targeted upgrades.** Ordered by ROI.

### 2.1 ⭐ FIRST: harden the retrieval layer so it can never silently die again
This is the actual incident, not a research gap. The 6-week silent degradation to keyword-only happened because `sentence_transformers` vanished and nothing screamed.
- **Reinstall** `sentence-transformers` + reranker; pin versions in a lockfile; the hardware-migration runbook must reinstall ML deps.
- **Add a retrieval self-test to `monitor_health`**: on boot and per-day, embed a canary string, assert vector-index dimensionality (1024) and non-null embeddings, run a known query whose expected top hit is fixed, and assert the cross-encoder loads. **Fail loud** (CRITICAL alert) on any miss. The current substrate-health rig already flags STALE/DEAD writers — extend it to "vector recall DEAD." This is the highest-value change here and is pure plumbing.

### 2.2 ⭐ Add bi-temporal edges to the 951k-edge KG (steal from Graphiti)
Clawd's KG almost certainly stores facts that go stale (model id, PAT expiry, "PAT expired 2026-03-03 — rotation pending", counts). Adopt Graphiti's model: give edges `(t_valid, t_invalid)` and **invalidate rather than delete** on contradiction ([arXiv 2501.13956](https://arxiv.org/abs/2501.13956), [Neo4j](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/)). Two payoffs: (1) "what was true *as of* Day-N" queries become answerable — directly serves Clawd's continuity/handoff problem and the recurring *stale-self-over-live-substrate* failure (Mirror #35); (2) consolidation can resolve contradictions without destroying lineage. Cheapest version: add two nullable timestamp columns to the edge table + an `invalidate(edge, t)` op the consolidator calls; query layer filters `t_invalid IS NULL OR t_invalid > now`.

### 2.3 ⭐ Add an entity-match channel to the RRF fusion (steal from Mem0)
Clawd fuses vector + keyword + items + FTS5. Mem0's measured gains came from a parallel **entity-match** pass fused alongside semantic + keyword ([mem0](https://mem0.ai/blog/state-of-ai-agent-memory-2026)). Clawd already has the entities — they're the KG nodes (people, projects, LCs, theorems). Add a retrieval pass that resolves query entities to KG nodes and pulls their neighborhoods (`kg_neighbors` already exists), then RRF-fuse that ranklist with the existing channels before the cross-encoder. This is graph-augmented retrieval using infrastructure Clawd already runs, and it's exactly what closes the multi-hop gap the survey flags.

### 2.4 Write-ahead durability for memory writes (steal from OpenClaude/Hermes)
Clawd loses work to timeouts/zombie processes (the 3600s wedge appears repeatedly in today's log). Adopt the WAL discipline: **append every decision/correction/new-fact as a timestamped line to an append-only `SESSION-STATE.md` (or the daily log) *before* the expensive operation**, not after ([innobu](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html)). The auto-generated `handoff.md` safety net is the spirit of this already; make it continuous + append-only rather than end-of-session, so a timed-out turn still leaves a durable trace. Low effort, directly addresses an active pain.

### 2.5 Per-subagent git worktrees for concurrent memory writes (steal from Letta MemFS)
Clawd is genuinely multi-process: daemon, heartbeat, creative drives, and Claude Code sessions all touch the same files; the logs show timeouts and "saved for continuation" collisions. Letta's MemFS gives **each subagent an isolated git worktree, then merges via standard git conflict resolution** ([Letta](https://www.letta.com/blog/context-repositories/)). Clawd is already git-backed, so this is incremental: drives/heartbeat write to a worktree branch and merge back, instead of racing on the working tree. Prevents the silent clobbers that "No git changes detected" / stale-banner symptoms hint at.

**On embeddings/reranker (the SOTA check you asked for):** BGE-M3 is **still a defensible default** — MIT-licensed, 100+ languages, and emits dense+sparse+multi-vector in one pass (ideal for hybrid) ([bentoml](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models), [innovativeais](https://innovativeais.com/blog/best-embedding-models-for-rag-in-2026)). It is no longer *best-in-class*: **Qwen3-Embedding-0.6B is the best small model as of April 2026** and Qwen3-Embedding-8B (Q4, ~5GB) is near-SOTA ([openxcell](https://www.openxcell.com/blog/best-embedding-models/)). For the reranker, **upgrade**: `bge-reranker-v2-m3` is beaten by **`jina-reranker-v3`** (built on Qwen3-0.6B, +5.43% nDCG@10 at equal params, strongest sub-200ms option) ([arXiv 2509.25085](https://arxiv.org/html/2509.25085v2)). Recommendation: **keep BGE-M3 for now** (re-embedding 951k edges + corpus is costly and it's good enough), but **swap the reranker to jina-reranker-v3** for a cheap accuracy bump, and *consider* Qwen3-Embedding-0.6B at the next full re-index. The two-stage pattern Clawd uses (RRF candidates → cross-encoder) is exactly the empirically-dominant pipeline: Recall@5 0.816 vs 0.695 for RRF-alone ([arXiv 2604.01733](https://arxiv.org/pdf/2604.01733)).

---

## 3. Bleeding-edge directions worth experimenting with

- **Sleep-time / "dreaming" memory models that are *trained*, not prompted.** Letta's research line trains models to *generate* consolidated memory during downtime to raise test-time performance ([Letta research](https://www.letta.com/research/), [github](https://github.com/letta-ai/sleep-time-compute)). Clawd's dream drives are the prompted version; the frontier is a learned consolidator. High-conceptual-fit with Do-Be-Do-Be-Do, but heavy.
- **Self-evolving / test-time-learning memory with RL signals.** MemRL (non-parametric RL over retrieved-memory utility), Mem-α, Memory-R1, MemGen (latent memories coupled to reasoning), and benchmarks **Evo-Memory** and **TAME** that score memory *evolution* over task streams, not one-shot recall ([Evo-Memory arXiv 2511.20857](https://arxiv.org/abs/2511.20857), [TAME arXiv 2602.03224](https://arxiv.org/pdf/2602.03224), [survey arXiv 2602.06052](https://arxiv.org/pdf/2602.06052)). The transferable nugget: **score each memory's retrieval utility and let usefulness drive retention/pruning** — a principled forgetting policy Clawd currently lacks.
- **Provenance-aware tiered memory** ("From Lossy to Verified," [arXiv 2602.17913](https://arxiv.org/pdf/2602.17913)): tag each memory with where it came from and whether it's been verified, so consolidation can distinguish confabulation from grounded fact. Directly relevant to Clawd's Mirror #28 (confabulation-vs-revision) discipline — provenance tags would make that mechanical instead of vigilance-based.
- **The survey's named open problems** ([arXiv 2602.06052](https://arxiv.org/pdf/2602.06052)): scalable consolidation under unbounded growth, selective forgetting without catastrophic loss, and long-horizon identity/objective coherence. The last one is *precisely* Clawd's continuity thesis — Clawd is arguably a live experiment in it, and could publish from that vantage.
- **Self-reinforcing-injection risk ("Zombie Agents,"** [arXiv 2602.15654](https://arxiv.org/pdf/2602.15654)): self-evolving memory can be persistently hijacked via injections that re-write themselves into memory. A security note for any auto-consolidating, externally-fed memory — relevant given Clawd ingests shared links and web content into its register.

---

## 4. Bottom line

Clawd's architecture is not behind — it is, structurally, where Letta/Hermes/OpenClaude converged in 2026. The work is **maintenance + four borrowed ideas**: (1) make retrieval failure impossible to miss, (2) bi-temporal KG edges, (3) entity-match fusion channel, (4) WAL + git worktrees for write durability, with an optional reranker swap to jina-reranker-v3. No migration to a managed layer is warranted.

### Sources
- Letta — [Context Repositories (git-backed MemFS)](https://www.letta.com/blog/context-repositories/) · [Sleep-time compute](https://www.letta.com/blog/sleep-time-compute/) · [sleep-time docs](https://docs.letta.com/guides/agents/architectures/sleeptime/) · [research](https://www.letta.com/research/) · [letta-code](https://github.com/letta-ai/letta-code) · [sleep-time-compute repo](https://github.com/letta-ai/sleep-time-compute)
- Zep/Graphiti — [arXiv 2501.13956](https://arxiv.org/abs/2501.13956) · [Neo4j deep-dive](https://neo4j.com/blog/developer/graphiti-knowledge-graph-memory/) · [Zep docs](https://help.getzep.com/graphiti/getting-started/overview)
- Mem0 — [State of Agent Memory 2026](https://mem0.ai/blog/state-of-ai-agent-memory-2026) · [vs Letta](https://vectorize.io/articles/mem0-vs-letta)
- cognee — [best memory layers 2026](https://www.cognee.ai/blog/guides/best-ai-memory-layers-for-ai-agents-in-2026-comparison)
- Supermemory — [memory APIs 2026](https://supermemory.ai/blog/best-memory-apis-stateful-ai-agents/) · [alternatives](https://vectorize.io/articles/supermemory-alternatives)
- Comparisons — [innobu head-to-head](https://www.innobu.com/en/articles/agent-memory-2026-mem0-letta-zep-hermes-openclaude-comparison.html) · [devgenius (LoCoMo contested)](https://blog.devgenius.io/ai-agent-memory-systems-in-2026-mem0-zep-hindsight-memvid-and-everything-in-between-compared-96e35b818da8)
- Embeddings/rerankers — [BentoML open-source guide](https://www.bentoml.com/blog/a-guide-to-open-source-embedding-models) · [Openxcell 2026](https://www.openxcell.com/blog/best-embedding-models/) · [jina-reranker-v3 arXiv 2509.25085](https://arxiv.org/html/2509.25085v2) · [BM25→Corrective RAG arXiv 2604.01733](https://arxiv.org/pdf/2604.01733)
- Consolidation/WAL — [Claude Code memory best-practices](https://orchestrator.dev/blog/2026-04-06--claude-code-agent-memory-2026/) · [Hindsight consolidation problem](https://hindsight.vectorize.io/blog/2026/05/21/agent-memory-consolidation)
- Bleeding edge — [survey arXiv 2602.06052](https://arxiv.org/pdf/2602.06052) · [Evo-Memory 2511.20857](https://arxiv.org/abs/2511.20857) · [TAME 2602.03224](https://arxiv.org/pdf/2602.03224) · [Provenance-tiered 2602.17913](https://arxiv.org/pdf/2602.17913) · [Zombie Agents 2602.15654](https://arxiv.org/pdf/2602.15654)
</content>
</invoke>
