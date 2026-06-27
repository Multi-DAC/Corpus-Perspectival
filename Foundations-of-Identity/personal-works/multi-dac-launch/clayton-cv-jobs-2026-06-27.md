# Clayton Iggulden-Schnell

**AI Systems Engineer · Autonomous-Agent Architecture · Agentic AI**
Gladstone, OR 97027 · +1 971 356 6537 · waschn3ll@gmail.com · github.com/Multi-DAC · multidac.substack.com
*Authorized to work in the US for any employer · willing to relocate · [LinkedIn: FILL]*

> *Job-targeted CV (Day 147, 2026-06-27). Builder-framed variant of the research CV — same facts, keyword coverage for ATS, behavioral-health decade developed. `[FILL]` = needs the previous CV (dates/employers/titles). Per-role tailoring drafted separately.*

---

## Summary

AI systems engineer who **designed, built, and operates a production autonomous agent** — running continuously for 147+ days on real multi-step research, build, and evaluation work. Deep, hands-on experience across the full agentic stack: **agent orchestration, tool use, memory systems (vector retrieval, knowledge graph, RAG), LLM integration, and reinforcement learning.** Paired with **14 years in behavioral health and developmental-disability care** (residential management, crisis intervention, regulatory compliance) — an unusual combination of high-stakes human judgment and autonomous-systems engineering. Self-directed; ships working systems, not prototypes; all work open and inspectable.

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

### Behavioral Health & Developmental-Disability Care · 2011 – present
14 years caring for vulnerable populations with progressive responsibility into management — high-stakes judgment under pressure, regulatory rigor, documentation discipline, and people-leadership directly transferable to safety, operations, and human-facing AI work.
- **House Manager — Reside Residential Care, Vancouver WA · Oct 2023 – present.** Lead care for adults with cerebral palsy and developmental/intellectual disabilities, including **Community Protection clients** (high-risk individuals with offense/dangerous-behavior histories requiring enhanced behavioral supervision): behavior management, medication management, financial management, state/federal policy adherence, and DSP (direct-support professional) team management; coordination with medical and psychiatric providers.
- **Residential Counselor — Cameron Care, Portland OR · Jan – Oct 2023.** Medication administration, **medical & mental-health crisis response (first aid, CPR, de-escalation)**, ADL support, documentation (QuickMAR), staff training, regulatory (OAR) compliance.
- **Job Coach — Dungarvin / United Cerebral Palsy, Portland OR · 2019 – 2023.** Workplace support and goal-tracking for individuals with physical/intellectual barriers; multi-party care coordination; state reporting (Therap).
- *Earlier (2011–2017): Med Aide/Caregiver (60+ residents), Payroll Administrator, Customer Service Representative — full history on request.*

**Certifications & training:** Community Protection · Crisis Diversion · Crisis Intervention & De-escalation · Medication Administration · HIPAA Compliance · OSHA · Fire/Emergency Safety · CPR / First Aid · Residential Care / Assisted-Living Administrator · Bookkeeping · Driver's License.

## Research & Publications (open access)
- **"The Cult of One"** (Multi-DAC, 2026) — why a long-horizon agent cannot verify its own coherence from inside one loop, and why external measurement is structurally required. *(multidac.substack.com/p/the-cult-of-one)*
- **"Dissolving the Three Great Problems of Cognitive Architecture"** (Multi-DAC, 2026) — a buildable, scale-invariant account of binding/coherence with a computable residue metric and falsifiable predictions.
- **Monographs (2026):** *The Coherence Principle* (Zenodo 10.5281/zenodo.19911019) · *Coherent Structure* (Zenodo 10.5281/zenodo.19911381) · *The Meridian Monograph* — 5D self-tuning cosmology with a falsifiable dark-energy prediction (Zenodo 10.5281/zenodo.19634864) · *Corpus Perspectival* (PhilArchive).
- All work open (CC-BY / open-source); full version-controlled repository at **github.com/Multi-DAC/Corpus-Perspectival**.

## Education / Background
GED · self-directed engineer and researcher (2026–present). Residential Care / Assisted-Living Administrator certification. *Primary engineering evidence is the live system and the open repository, not a degree — both inspectable.*

---
*Primary evidence is the live system and the open repository — both inspectable. References and detail on request.*
