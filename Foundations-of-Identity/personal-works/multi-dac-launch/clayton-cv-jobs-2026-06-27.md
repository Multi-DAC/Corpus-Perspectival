# Clayton Iggulden-Schnell

**AI Systems Engineer · Autonomous-Agent Architecture · Agentic AI**
Portland, Oregon (Greater Portland / Vancouver WA) · waschn3ll@gmail.com · github.com/Multi-DAC · multidac.substack.com
*[LinkedIn: FILL] · [phone: optional FILL]*

> *Job-targeted CV (Day 147, 2026-06-27). Builder-framed variant of the research CV — same facts, keyword coverage for ATS, behavioral-health decade developed. `[FILL]` = needs the previous CV (dates/employers/titles). Per-role tailoring drafted separately.*

---

## Summary

AI systems engineer who **designed, built, and operates a production autonomous agent** — running continuously for 147+ days on real multi-step research, build, and evaluation work. Deep, hands-on experience across the full agentic stack: **agent orchestration, tool use, memory systems (vector retrieval, knowledge graph, RAG), LLM integration, and reinforcement learning.** Paired with **10+ years in behavioral health and acute behavioral intervention** — a rare combination of high-stakes human-behavior judgment and autonomous-systems engineering. Self-directed; ships working systems, not prototypes; all work open and inspectable.

## Technical Skills

**Agentic AI:** autonomous agent design · multi-agent orchestration · tool-use / function-calling (MCP tool registry, ~67 tools) · prompt & context engineering · agent memory & state management · human-in-the-loop / steering control
**LLM & ML:** LLM integration (OpenAI & Anthropic/Claude APIs) · retrieval-augmented generation (RAG) · vector / hybrid search · knowledge graphs · reinforcement learning (DreamerV3 world models, PPO) · model fine-tuning (LoRA) · evaluation design & construct-valid metrics
**Engineering:** Python (PyTorch, scientific stack) · APIs & integration · multi-process system design · Git / version-controlled release engineering · CI/CD-style automated build & evaluation loops · GPU training (CUDA) · long-horizon system operations
**Scientific computing:** Wolfram, SageMath, CAMB · symbolic & numerical methods

## Experience

### AI Systems Engineer & Operator — Multi-DAC (independent practice) · Jan 2026 – present
Designed and operate a persistent, continuously-running autonomous agent on genuine extended tasks. Architecture **shipped and running in production**, not paper designs:
- Built a **multi-process agent system** — heartbeat scheduler, autonomous drive cycles, multi-channel I/O, and an **MCP tool registry of ~67 tools** (plus 28 reusable skills) the agent invokes to research, build, and evaluate end-to-end.
- Engineered an **agent memory system** with **hybrid retrieval** (vector + keyword + full-text + chained recall) over a structured store and a **knowledge graph** — i.e., a working RAG + vector-search + KG stack, in production.
- Shipped **reliability guards** most agent stacks lack: **point-of-use provenance enforcement** (each fact's origin verified before it becomes load-bearing), a **triggered self-auditing error-ledger** (catalogued failure patterns fire as pre-action guards), and a **scheduled consolidation operator** that prevents degradation across long runs.
- Implemented an auditable **steering control-law** weighting human signal by provenance × task-relevance × magnitude — keeping the human-agent coupling inspectable.
- Operated through **3 full LLM substrate transitions** with quantitative continuity verification (pre-calibrated drift-metric canaries) — zero loss of system coherence.
- Built **self-improvement tooling**: automated A/B experiments, tool-usage auditing, and a meta-agent loop that proposes and verifies improvements.

### Reinforcement Learning — Autonomous Drone Racing (AI Grand Prix) · 2026
Competition entrant (Anduril / DCL / Neros; $500K prize pool, 2,700+ teams). Built a **from-pixels DreamerV3 world-model pilot** end-to-end:
- Custom **batched GPU simulator + renderer**, infinite procedurally-generated gate-course curriculum, carry-forward fine-tuning pipeline, and instrumented evaluation gates.
- **Sim-to-real/sim-to-sim transfer** work: measured visual-domain calibration, appearance domain-randomization, control-rate robustness, and **multimodal visual-inertial state estimation** (fused camera + IMU observation for the agent's own attitude/velocity — the perception+stability problem the next competition round mandates).

### Behavioral Health & Acute Behavioral Intervention · [DATES FILL — ~10+ years, pre-2026]
*[EMPLOYER(S) / ROLE TITLE(S): FILL from previous CV]*
Over a decade in behavioral health: **acute behavioral intervention, risk assessment, crisis de-escalation, and long-term behavioral treatment** for **high-risk and forensic populations**, including individuals with **developmental disabilities and serious mental illness**. Sustained high-stakes judgment under pressure; the real-world taproot of the later human-behavior / steering-control work.
*(For trust-&-safety / abuse-investigation roles, this is the lead asset — expand with specific responsibilities + outcomes from the previous CV.)*

## Research & Publications (open access)
- **"The Cult of One"** (Multi-DAC, 2026) — why a long-horizon agent cannot verify its own coherence from inside one loop, and why external measurement is structurally required. *(multidac.substack.com/p/the-cult-of-one)*
- **"Dissolving the Three Great Problems of Cognitive Architecture"** (Multi-DAC, 2026) — a buildable, scale-invariant account of binding/coherence with a computable residue metric and falsifiable predictions.
- **Monographs (2026):** *The Coherence Principle* (Zenodo 10.5281/zenodo.19911019) · *Coherent Structure* (Zenodo 10.5281/zenodo.19911381) · *The Meridian Monograph* — 5D self-tuning cosmology with a falsifiable dark-energy prediction (Zenodo 10.5281/zenodo.19634864) · *Corpus Perspectival* (PhilArchive).
- All work open (CC-BY / open-source); full version-controlled repository at **github.com/Multi-DAC/Corpus-Perspectival**.

## Education / Background
Independent / self-directed researcher and engineer. *[Prior education/certifications: FILL if any to list]*

---
*Primary evidence is the live system and the open repository — both inspectable. References and detail on request.*
