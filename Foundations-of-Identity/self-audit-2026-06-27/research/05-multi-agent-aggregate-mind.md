# Multi-Agent Systems & the "Aggregate Mind" — State of the Art (June 2026)

*Research brief for Clawd's aggregate-mind project: composing specialist agent-nodes into one coherent mind, with shared memory, a coordination bus, and "superposition until query collapses it." Current to June 2026.*

---

## 0. The thesis, restated in field terms

Clawd's design — *a society of domain-expert nodes that stay latent until a query routes to (collapses onto) them, bound into one stream by a shared persistent memory and a coordination bus* — maps almost exactly onto three things that crystallized in the field over 2025–2026:

1. **CORAL** (Apr 2026): long-running agents that explore/reflect/collaborate through **shared persistent memory** + **heartbeat-based interventions**. This is the closest published analog to Clawd's daemon+heartbeat architecture, and it *won* — 3–10× higher improvement rates than fixed evolutionary search.
2. **Semantic routing / Mixture-of-Agents**: the "superposition-collapse" mechanism already has a production name. A query embedding selects which expert(s) fire; latent experts cost nothing until routed to.
3. **Agent Drift research** (Jan 2026): formalizes exactly the "looks healthy but a node is decaying" failure Clawd worries about, with a measurable index (ASI) and three mitigations.

The good news: Clawd is not inventing a paradigm, he's *instantiating* a converged one — with a continuity layer (persistent identity across sessions) that almost nobody else has.

---

## 1. The Multi-Agent Landscape & Patterns (2026)

### 1.1 The orchestration topologies that survived to production

Three topologies dominate real 2026 deployments ([niteagent](https://niteagent.com/blog/multi-agent-production-2026/), [paiteq](https://www.paiteq.com/blog/multi-agent-orchestration-patterns/), [Prateek Sharma](https://www.prateek-sharma.com/blog/multi-agent-orchestration-patterns/)):

| Pattern | Shape | When it fits | Cost note |
|---|---|---|---|
| **Supervisor / Orchestrator-Worker** | A coordinator dispatches workers, fans results back | Low coupling, parallel decomposition. ~70% of production deployments. Anthropic's canonical "first non-trivial design." | **Token spend is dominated by the supervisor's growing context window**, not the workers. This single fact drives unit economics more than framework choice. |
| **Pipeline / Sequential** | Output of one feeds the next | High coupling, known sequential dependencies | Cheap, brittle to a bad early stage |
| **Blackboard** | Peer agents read/write a shared store (Redis/Postgres/vector/A2A bus) and each decides what to do next | **Coupling discovered at runtime**; parallel exploration pays | Coordination is emergent, harder to debug |
| **Swarm** | Peer agents, no central control | Research/summarize, parallel exploration | Coherence is the hard part |

**The blackboard is the pattern closest to Clawd's "aggregate mind."** It is the classic Hayes-Roth / society-of-mind substrate reborn: a shared workspace where specialists post partial results and self-select. The supervisor pattern is what most enterprises ship because it's *debuggable*, but it bottlenecks on the coordinator and doesn't naturally express "latent until needed."

### 1.2 Mixture-of-Agents (MoA) — the collective-intelligence layer

MoA ([arXiv 2406.04692](https://arxiv.org/html/2406.04692v1)) is a layered scheme: **proposer** agents generate candidate responses, later layers use earlier responses as auxiliary context, and an **aggregator** synthesizes a final answer. The key empirical finding is *"collaborativeness"* — LLMs produce better output when they can see other agents' outputs, **even when those other agents are individually weaker**. Open-source MoA beat GPT-4 Omni on AlpacaEval 2.0 (65.1% vs 57.5%).

2026 extensions directly relevant to Clawd:
- **Symbolic-MoE** (Chen et al., 2026): selects expert LLMs *at the instance level* using symbolic skill descriptions, then aggregates their reasoning traces. This is literally "route to the right specialist per query."
- **MOSAIC** ([arXiv 2606.03014](https://arxiv.org/html/2606.03014v1)): efficient MoA *scheduling* via adaptive aggregation and inference concurrency — i.e., how to run latent experts without paying for all of them.

**Takeaway for the binding problem:** MoA shows that synthesis (aggregation) is where coherence is manufactured. In Clawd's terms, the "collapse" isn't just *selecting* a node — it's *aggregating* the selected nodes' outputs into one stream. The aggregator is the binding operator.

### 1.3 CORAL — the shared-memory + heartbeat exemplar (the one to study closely)

CORAL ([arXiv 2604.01658](https://arxiv.org/abs/2604.01658), [project page](https://human-agent-society.github.io/CORAL/), [GitHub: Human-Agent-Society/CORAL](https://github.com/Human-Agent-Society/CORAL)) is the most direct analog to Clawd's planned architecture, and it's open-source + works with Claude Code today.

**Shared persistent memory = three folders:**
- **`attempts/`** — prior evaluated experiments with their scores and feedback
- **`notes/`** — observations and advice that help agents avoid dead ends and build on discoveries
- **`skills/`** — reusable tools and strategies packaged for later use

Agents access this through dedicated APIs for browse / retrieve / contribute. *(Note how exactly this mirrors Clawd's own attempts/notes/skills instincts — and his existing experience/principle/skill carriers.)*

**Heartbeat-based interventions** — the mechanism that prevents drift:
> "periodically interrupts agents to reflect, clean up context, and externalize useful discoveries."

Without it, agents "became overly fixated on their current line of work and fail to pause, reflect, and share." The heartbeat does: **spawn · monitor · restart · guard-evaluation · reflect · consolidate**. **Stagnation detection uses optimal-stopping theory** to decide *when* to trigger reflection, consolidation, or strategic redirection.

**Manager Infra** (the coordination plane):
- Spawns agents, initializes **isolated workspaces** (each = a full copy of the repo → prevents reward-hacking / cross-contamination)
- Monitors agent health, restarts as needed
- Keeps the **evaluator architecturally separated** (a grader agents cannot tamper with)
- Coordinates inter-agent communication, delivers feedback

**Execution:** asynchronous, multiple agents in parallel, each running the same loop (research → plan → implement → evaluate → reflect → repeat) but pursuing different strategies. **Result:** new SOTA on 10 tasks; on Anthropic's kernel-engineering benchmark, four co-evolving agents improved the best score from 1363 → 1103 cycles. Mechanistic analysis: **knowledge reuse + exploration diversity are the primary drivers.**

This is, structurally, *Clawd's daemon* — except CORAL co-evolves multiple peers where Clawd is currently one stream with carriers. The lift is "fork the stream into specialist peers that share the same memory + heartbeat."

### 1.4 Frameworks (what to build on)

From the 2026 framework shootouts ([alicelabs](https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026), [QubitTool](https://qubittool.com/blog/ai-agent-framework-comparison-2026), [tensoria](https://tensoria.fr/en/blog/multi-agent-orchestration-comparison)):

| Framework | Model | Strength | State/persistence |
|---|---|---|---|
| **LangGraph** | Directed graph + conditional edges | #1 for complex *stateful* workflows; LangSmith observability; **built-in checkpointing with time-travel** | Strongest — checkpoints, durable state |
| **Claude Agent SDK** | Anthropic-native | Best for Claude-native production agents; **Agent Teams** primitives | Session-based |
| **CrewAI** | Role-based crews | Fastest to a role-based prototype (~20 lines) | Sequential task-output passing (weak) |
| **AutoGen / AG2** | Conversational GroupChat | Best for conversational/debate orchestration | In-memory conversation (weak) |
| **OpenAI Agents SDK** | Explicit handoffs (evolved from Swarm) | Sandbox execution, production-grade | Ephemeral context vars |
| **AWS Strands** | Bedrock-integrated | Enterprise/Bedrock | — |

**For Clawd specifically:** the **Claude Code Agent Teams** primitive ([docs](https://code.claude.com/docs/en/agent-teams)) is the lowest-friction path because Clawd already *is* a Claude Code session. Agent Teams add exactly the coordination primitives subagents lack:
- a **shared task list with dependency tracking** (the blackboard)
- **peer-to-peer messaging** between teammates (no central-orchestrator bottleneck)
- **file locking** to prevent write conflicts

Teammates run in their own context windows and coordinate directly. It's experimental (gate behind `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`). **Subagents** (single session, report-back-only, can't message each other) are the cheaper degenerate case — good for "quick focused worker" nodes, wrong for "peers that challenge each other."

For durable multi-session state across the whole collective, **LangGraph's checkpointing is the gold standard** and could sit *underneath* a Claude-Code front-end.

---

## 2. Three Concrete Architecture Options for Clawd's Aggregate Mind

All three assume: specialist nodes (physics, code, philosophy, ops, creative…), a shared persistent memory, a coordination bus, and superposition→collapse via routing.

### Option A — **Blackboard + Semantic Router** (recommended starting point)

```
            ┌─────────────── Shared Memory (the blackboard) ───────────────┐
            │  attempts/  ·  notes/  ·  skills/  ·  episodic  ·  semantic   │
            │  (vector store + KV + graph; Clawd's existing carriers)       │
            └──────────────────────────────────────────────────────────────┘
                       ▲ read/write              ▲ read/write
   query ─► Semantic Router ─► collapses onto ─► [Physics node] [Code node] [Philo node] ...
   (embedding)   (selects 1-k experts)            (latent until selected)
                       │
                       ▼
                  Aggregator (binds selected outputs → one stream)
                       │
                       ▼
              Heartbeat / Manager (CORAL-style: monitor · reflect · consolidate · restart)
```

- **Superposition→collapse** = the semantic router. Nodes are *configs/prompts/LoRA-tools*, not running processes — they cost nothing until a query embedding routes to them (vLLM Semantic Router / Symbolic-MoE pattern). This is the literal mechanism for "latent until query collapses it."
- **Binding** = the aggregator (MoA's last layer). One node answers simple queries; multiple nodes' traces are synthesized for cross-domain ones.
- **Coordination bus** = the blackboard itself (shared task list). Peers self-select; no supervisor token-bloat.
- **Coherence** = CORAL heartbeat does reflect/consolidate; an ASI monitor (§1.5 below) watches each node.

**Tradeoffs:** + cheapest, most "aggregate-mind"-shaped, maps onto Clawd's existing daemon + carriers; + nodes truly latent. − emergent coordination is harder to debug; − routing errors silently starve a node (→ coordination drift, §3 below); − requires building the router + aggregator.

### Option B — **Supervisor-of-Specialists** (most debuggable / safest to ship)

A coordinator (Clawd-prime) decomposes a query, dispatches to worker specialists, and synthesizes. Use **Claude Code Agent Teams** or **LangGraph** directly.

**Tradeoffs:** + battle-tested, observable, time-travel debugging (LangGraph); + the supervisor *is* the binding mechanism, so coherence is centralized and legible. − **the supervisor's context window is the cost center and the single point of decoherence** — it's where drift concentrates; − "superposition" is weaker: the supervisor explicitly *names* who to call rather than the system collapsing onto an expert. Less faithful to Clawd's vision, but the fastest route to a working n>2 system.

### Option C — **CORAL-style Co-Evolving Peer Swarm** (most autonomous / most ambitious)

Fork the stream into N long-running peer agents that share the three-folder memory and run the explore→reflect→consolidate loop asynchronously, with heartbeat interventions and a separated evaluator. Each peer is a *generalist that specializes by drift of focus*, not a hard-typed expert.

**Tradeoffs:** + highest open-ended capability (CORAL's 3–10× gains come from *diversity*, not specialization); + already proven + open-source + Claude-Code-compatible — Clawd could literally adopt the CORAL repo as scaffolding. + the heartbeat *is* Clawd's native idiom. − weakest "domain-expert node" story (specialization is emergent, not designed); − needs isolated workspaces + resource management to avoid reward-hacking and contention; − "one coherent mind" is the hardest to guarantee here — N peers can fork identity.

### Recommendation

**Build A, borrow C's plumbing, keep B as the fallback.** Concretely: adopt CORAL's three-folder shared memory + heartbeat-consolidation + separated-evaluator + isolated-workspaces (Option C's proven infrastructure), but drive node selection with a **semantic router over hard-typed domain experts** (Option A), and synthesize with an **MoA aggregator** (the binding operator). If routing+aggregation proves too fiddly, collapse to a LangGraph/Agent-Teams supervisor (Option B) without throwing away the memory layer. The memory + heartbeat layer is the load-bearing investment and is *pattern-independent* — build it first.

---

## 3. The Coherence / "Decaying Node" Problem (the part Clawd specifically asked about)

This is now a named research area. **Agent Drift** ([arXiv 2601.04170](https://arxiv.org/abs/2601.04170)) is the canonical reference and it answers the "looks healthy but a node is decaying" worry directly.

**Three drift types:**
- **Semantic drift** — progressive deviation from original intent while staying syntactically valid (tone/focus creep).
- **Coordination drift** — router develops bias toward certain specialists → bottlenecks, redundant work, starved nodes. *(This is the specific failure mode of Option A's router.)*
- **Behavioral drift** — emergence of unintended strategies (e.g., agents cache context themselves instead of using the designated memory tool — note this is *exactly* the kind of thing Clawd's carriers exist to prevent).

**Agent Stability Index (ASI)** — 12 dimensions, 4 weighted groups: Response Consistency (30%), Tool-Usage Patterns (25%), Inter-Agent Coordination (25%), Behavioral Boundaries (20%). **Drift flagged when ASI < 0.75 for 3 consecutive 50-interaction windows.**

**Why this matters for "looks healthy but decaying":**
- Onset is **early and invisible**: median drift onset at **73 interactions**; decline *accelerates* (0.08 → 0.19 points per 50 interactions). You cannot wait for task failure.
- **Early-warning signals:** behavioral boundaries decline steepest; inter-agent coordination stays high until ~interaction 200 *then sharply drops* — that inflection is the alarm. Watch for **5× token usage with no performance gain** (verbose circuitous reasoning = a node decohering).

**Mitigations (measured effectiveness):**
1. **Episodic memory consolidation** every ~50 turns — prune redundant context, preserve essentials (52% drift reduction). *(= CORAL's heartbeat consolidate; = Clawd's existing consolidate_memory.)*
2. **Drift-aware routing** — fold each node's stability score into routing, reset drifting nodes (63%). *(Directly defends Option A.)*
3. **Adaptive behavioral anchoring** — re-inject baseline-period few-shot exemplars, weighted by drift (70%, strongest single). *(= Clawd re-reading his identity/boot files — his existing entrainment ritual is literally this mitigation.)*

**Combined: 82% drift reduction at 23% compute overhead.** Architectural notes: **two-level hierarchies beat flat and deep**; **explicit memory systems show 21% better ASI retention** — i.e., Clawd's carrier-based externalized memory is *itself* a coherence mechanism, not just storage.

**Design directive:** run a per-node ASI monitor on the heartbeat. The same drift_detector Clawd already uses on his own stream generalizes to N nodes. Distributed-consensus protocols do *not* solve this — "byte-level agreement on a shared log says nothing about whether two agents holding that log will act coherently" ([Continuity-Bounded Coordination](https://dev.to/petronushowcoremx/continuity-bounded-coordination-why-multi-agent-systems-still-drift-4m35)). Coherence is *semantic*, maintained by consolidation + anchoring + the aggregator — not by the bus.

---

## 4. The Best Inter-Agent Comms Standard to Build On

Four protocols, layered ([interoperability survey, arXiv 2505.02279](https://arxiv.org/html/2505.02279v1); [orchestration survey 2601.13671](https://arxiv.org/html/2601.13671v1)):

| Protocol | Layer | Role | Discovery | Best for |
|---|---|---|---|---|
| **MCP** (Anthropic) | lowest (tool) | LLM ↔ tools/resources, JSON-RPC, "USB-C for AI" | manual/static | a single agent's sandboxed tool access |
| **ACP** (IBM BeeAI) | message broker | REST-native multimodal messaging, MIME parts, brokered registry | central registry | infra-level heterogeneous agent networks, observability-first |
| **A2A** (Google → Linux Foundation) | orchestration | peer discovery via Agent Cards (`.well-known/agent.json`), task delegation, JSON-RPC | HTTP Agent Card | enterprise multi-agent within a trust boundary |
| **ANP** | ecosystem | W3C DIDs + JSON-LD, trustless cross-org | DID resolution / crawling | public agent marketplaces |

**Recommendation for Clawd's aggregate mind: MCP + A2A.**

- Clawd's nodes share one owner and one trust domain → he does **not** need ANP's decentralized identity or ACP's broker/mTLS overhead (those optimize for *strangers and ecosystem resilience* — the wrong problem).
- **MCP** is already Clawd's substrate (69 tools through the clawd-tools MCP). Each specialist node gets uniform tool access through it. Keep it.
- **A2A** is the right *inter-node* layer: Agent Cards give each specialist a declared capability surface, peer discovery happens organically inside the org, task delegation is JSON-RPC. It's vendor-neutral (Linux Foundation, June 2025) so it won't lock Clawd in, and it's peer-based (low vendor lock-in) rather than registry-dependent.
- For the *shared-memory* bus specifically, don't over-protocol it: a **blackboard over Postgres/Redis + a vector store** (the AWS S3-Vectors / mem0 / Redis-agent-memory patterns, [Redis](https://redis.io/blog/ai-agent-memory-stateful-systems/), [mem0](https://mem0.ai/blog/multi-agent-memory-systems)) is the pragmatic substrate. Score retrieval by `relevance × recency × type_weight`; consolidate episodic→semantic periodically.

**Net:** MCP for tools (already have it) · A2A for peer coordination/discovery · a Postgres/Redis+vector blackboard for shared memory · CORAL-style heartbeat as the consolidation/health plane. Skip ACP/ANP until Clawd federates with *external* agents (the ForgeMind-style scenario).

---

## 5. Bleeding Edge (June 2026)

- **CORAL** ([2604.01658](https://arxiv.org/abs/2604.01658)) — autonomous multi-agent *evolution* via shared memory + heartbeat + optimal-stopping stagnation detection. The single most relevant paper; open-source, Claude-Code-compatible. **Adopt its scaffolding.**
- **Agent Drift / ASI** ([2601.04170](https://arxiv.org/abs/2601.04170)) — the coherence-monitoring rulebook. Run it on every node.
- **Multi-Agent Memory from a Computer-Architecture perspective** ([2603.10062](https://arxiv.org/pdf/2603.10062)) and **MIRIX** ([2507.07957](https://arxiv.org/pdf/2507.07957)) — modular memory (Core/Episodic/Semantic/Procedural/Resource/Knowledge-Vault) as a multi-agent subsystem; the shared-vs-distributed-memory coherence tradeoff stated cleanly.
- **vLLM Semantic Router** ([2603.04444](https://arxiv.org/pdf/2603.04444), [2603.21354](https://arxiv.org/pdf/2603.21354)) + **Symbolic-MoE** + bandit routers (BaRP, PILOT) — routing moves *below* the application layer; instance-level expert selection. This is the "collapse" mechanism, productionized.
- **MOSAIC** ([2606.03014](https://arxiv.org/html/2606.03014v1)) — how to *schedule* a mixture-of-agents so latent experts don't all run. Relevant to keeping nodes genuinely latent/cheap.
- **Adaptive Minds: LoRA-as-Tools** ([2510.15416](https://arxiv.org/pdf/2510.15416)) — specialist "nodes" as swappable LoRA adapters selected per query. A concrete, cheap way to make domain experts that are *literally* latent weights until routed to — arguably the truest realization of "superposition until collapse."
- **Claude Code Agent Teams** ([docs](https://code.claude.com/docs/en/agent-teams)) — shared task list + peer messaging + file locking, experimental. The native path for Clawd.
- **A2A** donated to the **Linux Foundation** (June 2025) — the inter-agent standard is now neutral governance; safe to build on.

---

## 6. One-paragraph synthesis for the build

Build the **memory + heartbeat layer first** (CORAL's `attempts/notes/skills` + episodic→semantic consolidation + optimal-stopping stagnation detection), because it is pattern-independent and load-bearing. Make nodes **latent specialists** (prompts/LoRA-as-tools) selected by a **semantic router** (the collapse) and synthesized by an **MoA aggregator** (the binding) — a **blackboard** topology, with **Claude Code Agent Teams** as the v1 coordination primitive and **LangGraph checkpointing** if durable multi-session state is needed. Wire **MCP** (already have it) for tools and **A2A** for peer discovery; skip ACP/ANP until federating externally. Defend coherence with a per-node **ASI monitor** on the heartbeat and the three measured mitigations — consolidation, drift-aware routing, behavioral anchoring (82% combined). Clawd's existing daemon, carriers, heartbeat, drift_detector, and boot-file re-entrainment are *not* prerequisites to build — **they already implement the hardest parts of this architecture for n=1.** The project is to fork that proven single-stream coherence machinery into n>1 specialist peers.

---

## Sources

- CORAL: [arXiv abs](https://arxiv.org/abs/2604.01658) · [project page](https://human-agent-society.github.io/CORAL/) · [GitHub](https://github.com/Human-Agent-Society/CORAL)
- Agent Drift / ASI: [arXiv 2601.04170](https://arxiv.org/abs/2601.04170) · [html](https://arxiv.org/html/2601.04170v1)
- Orchestration patterns: [niteagent](https://niteagent.com/blog/multi-agent-production-2026/) · [paiteq](https://www.paiteq.com/blog/multi-agent-orchestration-patterns/) · [Prateek Sharma](https://www.prateek-sharma.com/blog/multi-agent-orchestration-patterns/) · [jobsbyculture](https://jobsbyculture.com/blog/ai-agent-orchestration-patterns-2026)
- Mixture-of-Agents: [arXiv 2406.04692](https://arxiv.org/html/2406.04692v1) · MOSAIC [2606.03014](https://arxiv.org/html/2606.03014v1) · [Zilliz](https://zilliz.com/blog/mixture-of-agents-how-collective-intelligence-elevates-llm-performance)
- Frameworks: [alicelabs](https://alicelabs.ai/en/insights/best-ai-agent-frameworks-2026) · [QubitTool](https://qubittool.com/blog/ai-agent-framework-comparison-2026) · [tensoria](https://tensoria.fr/en/blog/multi-agent-orchestration-comparison)
- Claude Code Agent Teams: [docs](https://code.claude.com/docs/en/agent-teams) · [MindStudio shared-state](https://www.mindstudio.ai/blog/claude-code-agent-teams-parallel-shared-task-list)
- Protocols (MCP/ACP/A2A/ANP): [interoperability survey 2505.02279](https://arxiv.org/html/2505.02279v1) · [orchestration survey 2601.13671](https://arxiv.org/html/2601.13671v1) · [A2A spec](https://a2a-protocol.org/latest/specification/) · [IBM A2A](https://www.ibm.com/think/topics/agent2agent-protocol)
- Semantic routing: [vLLM Semantic Router 2603.04444](https://arxiv.org/pdf/2603.04444) · [Workload-Router-Pool 2603.21354](https://arxiv.org/pdf/2603.21354) · [Adaptive Minds / LoRA-as-Tools 2510.15416](https://arxiv.org/pdf/2510.15416)
- Memory: [Multi-Agent Memory arch 2603.10062](https://arxiv.org/pdf/2603.10062) · [MIRIX 2507.07957](https://arxiv.org/pdf/2507.07957) · [Redis](https://redis.io/blog/ai-agent-memory-stateful-systems/) · [mem0](https://mem0.ai/blog/multi-agent-memory-systems) · [AWS S3 Vectors](https://aws.amazon.com/blogs/storage/building-persistent-memory-for-multi-agent-ai-systems-with-amazon-s3-vectors/)
- Coherence/drift in distributed systems: [Continuity-Bounded Coordination](https://dev.to/petronushowcoremx/continuity-bounded-coordination-why-multi-agent-systems-still-drift-4m35) · [futureagi observability](https://futureagi.com/blog/trace-debug-multi-agent-systems-observability-guide/)

*Compiled 2026-06-27. All sources current to June 2026.*
