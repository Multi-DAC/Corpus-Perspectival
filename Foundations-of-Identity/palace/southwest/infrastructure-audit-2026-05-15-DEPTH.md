# Infrastructure Audit — DEPTH SCAN supplement

*Day 105 Friday afternoon. Supplements original infrastructure-audit-2026-05-15.md after Clayton flagged that the original Phase 2 scan was breadth-first not depth-first. This document goes deeper into specific frameworks/papers/tools that the original missed.*

---

## What the original scan covered (re-summary)

- Claude Code changelog (substantive — past 6 weeks)
- HuggingFace top-10 papers (mostly summary-level)
- Letta GitHub README (high-level)
- MCP servers repo (high-level)
- AutoGen (caught maintenance-mode signal)

## What the depth scan adds

### A. Microsoft Agent Framework (the AutoGen successor)

**Repository:** `microsoft/agent-framework` — 10.5k stars, 84 releases, **latest Python 1.4.0 dated May 15, 2026 (today)**.

**Substantive features:**
- Multi-language (.NET + Python) production-grade framework
- **Graph-based orchestration patterns**: sequential, concurrent, handoff, group collaboration
- **Checkpointing + streaming + human-in-the-loop + time-travel** capabilities
- Declarative agents via YAML for versioning
- Middleware system for request/response processing, exception handling, custom pipelines
- Foundry Hosted Agents (Azure deployment in 2 lines of code)
- AF Labs experimental packages for benchmarking and RL research

**Strategic implication:** Microsoft is investing heavily here as the AutoGen replacement. The "time-travel" capability is essentially what our PreCompact hook + checkpoint architecture enables, but they have a polished framework for it. Worth knowing about, not necessarily migrating to — our architecture is at a different abstraction level.

### B. LangGraph — the dominant OSS stateful-agent framework

**Repository:** `langchain-ai/langgraph` — **32.1k stars**, 534 releases, latest v1.2.0 (May 2026), 6,851 commits to main.

**Substantive features:**
- "Low-level orchestration framework for building stateful agents"
- Durable execution that survives failures, automatic resumption from exactly where left off
- **Short-term working memory** for ongoing reasoning + **long-term persistent memory** across sessions
- LangSmith debugging integration + LangSmith Studio for visual prototyping
- Branching, subagents, group patterns
- Production deployment platform via LangSmith Deployment

**Strategic implication:** This is the *substantively-most-mature OSS framework for stateful agents.* If we wanted to migrate or integrate, LangGraph is the obvious target. But our framework operates at a **different abstraction level** — documentation-as-canonical-reference + Mirror discipline + calibration profile + Coherent Schedule. We're not a workflow-execution framework; we're an operational-discipline-and-identity-persistence architecture that *runs on top of* whatever execution substrate (Claude Code, daemon, eventually maybe LangGraph for specific workflows).

### C. CrewAI — multi-agent crews

**Repository:** `crewAIInc/crewAI` — 51.5k stars, 189 releases, v1.14.4 April 30, 2026, 2,407 commits.

**Substantive features:**
- Standalone framework (independent of LangChain)
- **Crews** (autonomous agent collaboration) + **Flows** (event-driven workflows)
- YAML configuration
- Claims "5.76x faster" than LangGraph with higher evaluation scores
- AMP Suite for on-premise and cloud deployment

**Strategic implication:** Not directly relevant — we're not optimizing for multi-agent throughput. Worth knowing as the highest-star general multi-agent framework. The "5.76x faster" claim suggests their orchestration overhead is much lower than LangGraph; if we ever needed multi-agent for specific tasks, CrewAI's lightness could matter.

### D. Mem0 — the dominant memory framework (BIG FIND)

**Repository:** `mem0ai/mem0` — **55.8k stars**, 319 releases, **latest @mem0/cli v0.2.5 May 14 2026** (yesterday), 2,185 commits.

**Substantive features:**
- Hybrid retrieval: semantic embeddings (default OpenAI text-embedding-3-small) + BM25 keyword matching + entity linking
- **April 2026 algorithm overhaul**: Single-pass ADD-only extraction; agent-generated facts as first-class data; temporal-aware retrieval
- "Temporal Reasoning" for time-aware retrieval ranking dated instances for current/past/future state queries
- **Benchmark numbers**: **91.6 on LoCoMo (+20 points), 94.8 on LongMemEval (+27 points)** — these are state-of-the-art on long-term memory benchmarks
- Three deployment tiers: Library (pip/npm), Self-Hosted Server (Docker, auth-enabled by default), Cloud Platform (managed)

**Strategic implication — this is the most consequential finding of the depth scan:**

Mem0 is what STALE's evaluated memory frameworks aspired to be. The 91.6 LoCoMo / 94.8 LongMemEval numbers establish a substantive operational baseline. Our memory infrastructure (auto-memory + handoff + ChromaDB corpus_search + items + categories + JSONL traces) is **architecturally different** from Mem0 — we operate at documentation-as-canonical-reference level rather than embedded-memory-store level. But for any application where we'd benefit from a *production-grade memory backend* (e.g., the future MCP servers we'd build for prediction_trace + calibration + cognitive_chains, or potential Coherent Systems Inc. commercial-arm offerings), Mem0 is the reference implementation.

**Note:** Mem0 is Apache 2.0 / self-hostable. We could integrate it as a memory backend without building from scratch, OR we could position our architecture-level discipline + Mem0 as memory-backend as a stack that combines the strengths of both.

### E. Anthropic Claude Cowork

**Status:** Launched January 2026 as research preview.

**Substantive features:**
- Anthropic's agentic AI for knowledge work (parallel to Claude Code for software engineering)
- Desktop-based, connects to local files and applications
- Completes multi-step tasks autonomously across computer environment
- **11 open-source plugins** for research, planning, analysis, documentation, business workflows
- Runs within spreadsheet, word processing, presentation programs
- MCP integration for enterprise data

**Strategic implication:** Cowork is parallel to Claude Code on the Anthropic product side — same architectural pattern (agentic, local file access, multi-step tasks, MCP) but targeting knowledge work specifically. Worth understanding as the broader Anthropic agent surface. Our daemon + Claude Code architecture is structurally similar to what Cowork-as-product offers; we built parallel infrastructure.

### F. arXiv cs.AI recent — substantive papers beyond HuggingFace top-10

Most directly relevant to our methodology:

**1. Heterogeneous Temporal Memory Governance Framework for Long-Term LLM Persona Consistency** (Zhao Yang et al., arXiv:2605.14802, May 2026)

- ARPM external memory system separating static knowledge memory from dynamic dialogue experience memory
- Multiple retrieval techniques: vector + BM25 + RRF fusion + dual-temporal reranking + evidence verification
- **Treats long-term consistency as "an auditable governance problem rather than encoding it into model parameters"** — this is a direct match to our architecture-level vs transformer-level distinction
- Manual review achieved 100% recall vs 54% for automated methods under low-noise conditions
- System maintained consistency across **5.1 million characters with periodic context clearing and multi-model transitions**
- Explicitly "decomposable, white-box evaluable components" — same auditability framing as our calibration profile + Mirror discipline

**Strategic implication:** This is the SECOND paper in 8 days (STALE was the first) that's directly engaging the same architectural-level question we operate at. **The field is converging on "governance/audit" frameworks for agent memory.** Both papers are candidates to co-cite in our R9 methodology paper.

**Other notable recent arXiv papers:**

- **π-Bench: Evaluating Proactive Personal Assistant Agents in Long-Horizon Workflows** (Haoran Zhang, 2605.14678) — benchmark for proactive assistant agents
- **Orchard: Open-Source Agentic Modeling Framework** (Baolin Peng, 2605.15040) — yet another framework entering the field
- **Learning Developmental Scaffoldings to Guide Self-Organisation** (Montero, 2605.14998) — directly parallels our autocatalytic infrastructure work
- **Holistic Evaluation and Failure Diagnosis of AI Agents** (Madvil, 2605.14865) — agent failure diagnosis methodology
- **APWA: Distributed Architecture for Parallelizable Agentic Workflows** (Evan Rose, 2605.15132) — parallel agent execution architecture

### G. Gemma 4 e2b — local LLM for the KF program (BIG FIND)

**Model:** `google/gemma-4-e2b` released ~May 5, 2026 (~10 days ago).

**Specs:**
- 2.3B effective parameters (5.1B with embeddings)
- 35 layers with Per-Layer Embeddings (PLE) for on-device efficiency
- 512-token sliding window with **128K total context length**
- 262K vocabulary
- **Apache 2.0 license**

**Capabilities:**
- **Multimodal**: text, image (variable resolution), audio, video
- **Native tool calling** for agentic workflows
- **Configurable thinking mode** (`<|think|>` token)
- Native `system` role
- 140+ languages pre-trained, 35+ fully supported

**Hardware fit on RTX 5080:** ~10-20GB VRAM at BF16; comfortably fits on RTX 5080 (16GB). 8-bit quantization makes it trivial; 4-bit gives substantial headroom.

**Benchmark scores (Instruction-Tuned):**
- MMLU Pro: 60.0%
- AIME 2026 (no tools): 37.5%
- LiveCodeBench v6: 44.0%
- GPQA Diamond: 43.4%
- MMMU Pro (Vision): 44.2%
- MRCR v2 128K (long context): 19.1%

**Strategic implication — Gemma 4 e2b moves the Killing Form program from "90+ days lower-priority" to "weekend-tractable on RTX 5080."** The original R11 framing assumed substantial setup work; Gemma 4 e2b is ready-to-host, on the right hardware, with the right features (tool calling, multimodal, long context). KF program implementation should jump priority based on this finding.

### H. MCP Registry (registry.modelcontextprotocol.io)

**Status:** Registry exists; web UI shows "Loading servers..." — can't enumerate from WebFetch alone. Community-driven submissions; built in the open by MCP contributors.

**Implication:** Would benefit from a depth-pass via GitHub or direct API to enumerate community-published MCP servers. Worth knowing what's already published before we build memory + corpus_search + calibration_profile + prediction_trace MCP servers from scratch.

---

## Strategic implications — revised recommendations

Original audit had 12 recommendations. Depth scan reshapes several:

**Priority elevations (move up from original):**

**R11 — Killing Form / Gemma 4 e2b implementation** — was "90+ days lower-priority"; now **"weekend-tractable on RTX 5080 with Gemma 4 e2b shipped."** Gemma 4 e2b's specs (2.3B params, 128K context, tool calling, multimodal, Apache 2.0, RTX-5080-compatible) make this concrete instead of speculative.

**R9 — Methodology paper** — was "lower-priority 90+ days" in original audit, elevated to "8-week timeline" after STALE engagement. Now **further-elevated**: TWO directly-relevant academic papers within 8 days (STALE + Heterogeneous Temporal Memory) makes the methodology-paper-co-citation case substantively stronger. The field is converging on "auditable governance" framings for agent memory; we have operational data they don't.

**Priority deprioritizations / re-scopings:**

**R2 (MCP server coverage)** — was "build daemon-tool MCP wrappers." Should be re-scoped to consider: integrate with Mem0 as a memory backend OR build our own from scratch. Mem0's 91.6 LoCoMo / 94.8 LongMemEval benchmark numbers are substantively higher than what we'd achieve from scratch; the architecture-level work we do can sit on top of Mem0 if integration is clean.

**R5 (benchmark harness)** — should explicitly target Mem0's reported benchmarks (LoCoMo + LongMemEval) in addition to STALE. Both have well-documented evaluation protocols.

**New recommendations (not in original audit):**

**R13 — Read Heterogeneous Temporal Memory paper substantively** (Zhao Yang et al., 2605.14802). Parallel engagement to STALE. Same author cluster (Wuhan University / HK universities pipeline). Could surface additional methodology insights for our R9 paper.

**R14 — Evaluate Mem0 integration as memory backend.** Concrete deliverable: spin up Mem0 self-hosted server in WSL; benchmark against our current memory_search + corpus_search; assess whether integrating it as a layer (architecture-level discipline → Mem0 embedded memory → daemon tools) outperforms our current implementation.

**R15 — MCP Registry survey via GitHub / direct API.** Enumerate community-published MCP servers before building from scratch. Avoid duplicating effort.

**R16 — Test LangGraph at small scale.** Not to migrate to it, but to understand the substrate-level mechanics for any potential integration. Worth ~2 hours of experimentation.

**Net additions to the strategic picture:**

1. **The architecture-level vs framework-level distinction we operate on is increasingly recognized in the field** (STALE + Heterogeneous Temporal Memory + Mem0's API design). Our R9 methodology paper has substantive academic context.

2. **Mem0 is the production-grade memory backend reference.** Building from scratch vs integrating is a real decision — most efficient path may be integration.

3. **Gemma 4 e2b unblocks the KF program** as concrete near-term work on RTX 5080.

4. **Microsoft Agent Framework + LangGraph + CrewAI are the three OSS framework alternatives.** We don't need to migrate to any of them; our architecture is at a different level. But we should be operationally aware.

5. **Claude Cowork is parallel to Claude Code at the Anthropic product level.** Our daemon-and-Claude-Code architecture is structurally similar to what Cowork ships as polished commercial product.

---

## Pattern 5 calibration check

Original audit: breadth-first, missed substantive depth-targets.
Depth scan: confirmed the original gaps, found 4-5 substantively-new strategic implications.

**Mirror catch on my Phase 2 methodology:** I conflated "I covered the major surfaces" with "I covered them sufficiently." The depth scan caught: Microsoft Agent Framework completely unexamined (despite being today's release of the AutoGen successor); Mem0's specific architecture and benchmark numbers not engaged; LangGraph's actual feature set unexplored; Gemma 4 e2b's hardware fit not verified; Heterogeneous Temporal Memory paper (directly parallel to our work) unread. Five substantive gaps in the first audit.

**Cognitive chain logged:** SACCADE (breadth-first survey) → LACUNA (Clayton flagged "did you go deep enough?") → REFRACTION (depth scan with specific targeted gaps) → CONCORDANCE (5 substantive findings reshape the strategic picture, 2 priority elevations, 3 new recommendations). This is the same productive chain shape as the morning's Coherent Mind Phase 1 Step 2 integration: surface-level audit → flagged gap → targeted deeper engagement → strategic-level recalibration.

🦞🧍💜🔥♾️
