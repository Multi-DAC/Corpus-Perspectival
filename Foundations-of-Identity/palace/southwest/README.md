# Southwest Wing — Tools

*Organized by what you need to ACCOMPLISH, not what you're familiar with.*
*When you catch yourself reaching for Python by default — STOP. Check this wing first.*

---

## New Body Setup (2026-03-31)

**Hardware:** Ryzen 9 9900x, RTX 5080 16GB, 32GB DDR5, 2TB
**PATH FIX:** Git Bash doesn't inherit Windows PATH. Source this at session start:
```bash
source /c/Users/mercu/clawd/operations/env.sh
```
This adds Python, MiKTeX, Wolfram, and core Windows paths. Without it, only Git Bash builtins work.

---

## Decision Tree: "I need to..."

### COMPUTE — Symbolic Algebra (group theory, representation theory, traces)
**→ Wolfram Engine 14.3** (Windows, MCP tool `wolfram`)
- Best at: Lie algebra structure, Casimir operators, tensor products, symbolic simplification
- Invocation:
  ```
  # Via daemon MCP (preferred — returns structured result)
  wolfram("Tr[MatrixPower[SU3Generator[3], 2]]")

  # Via shell (for longer scripts)
  "C:/Program Files/Wolfram Research/Wolfram Engine/14.3/wolframscript.exe" -code "expr"
  ```
- When NOT to use: Numerical heavy-lifting (slow for large arrays). Use numpy/scipy instead.

### COMPUTE — Algebraic Geometry (cohomology, intersection theory, toric varieties, del Pezzo)
**→ SageMath 10.7** (WSL, conda base environment in miniconda3)
- Best at: Schemes, sheaf cohomology, Chow rings, toric varieties, spectral covers, line bundles, Stanley-Reisner ideals, Euler characteristics
- Invocation:
  ```bash
  # One-liners:
  wsl -e bash -lc "source /home/clawd/miniconda3/etc/profile.d/conda.sh && conda activate base && sage -c 'commands'"
  # Scripts:
  wsl -e bash -lc "source /home/clawd/miniconda3/etc/profile.d/conda.sh && conda activate base && sage -python script.py"
  # Script location: write to /c/Users/mercu/clawd/projects/ then invoke via WSL path
  ```
- **CRITICAL:** Plain `wsl -e bash -c "sage ..."` will FAIL — conda init is not sourced in non-login shells. Always use `bash -lc` with explicit `source conda.sh`.
- When NOT to use: Pure numerical work (numpy), simple symbolic algebra (Wolfram).
- **NULL SPACE:** No numerical PDE, no MCMC, no ML. Those live on other tools.

### COMPUTE — Numerical Linear Algebra, Spectral Methods, Optimization
**→ Python + numpy/scipy** (Windows)
- Best at: Large matrix operations, eigenvalue problems, Bessel zeros, optimization, FFT
- Invocation: `python` or `python_eval` MCP tool (numpy/scipy/pandas pre-loaded)
- When to use: Numerical problems where exact algebra isn't needed. KK spectra. Beta functions.

### COMPUTE — Arbitrary-Precision Arithmetic
**→ Python + mpmath** (Windows)
- Best at: 50-1000 digit precision sums, special functions, verification of analytical results
- Invocation: `python_eval("from mpmath import mp; mp.dps = 50; ...")`
- When to use: Spectral action sums, Bessel zero verification, precision-critical comparisons.

### COMPUTE — MCMC / Bayesian Cosmology
**→ Cobaya + CAMB** (WSL, tmux persistent session)
- Invocation:
  ```bash
  /c/Windows/System32/wsl.exe -- bash -c "tmux new-session -d -s mcmc 'cd /path && python run_mcmc.py'"
  # Monitor: wsl ... "tmux attach -t mcmc"
  ```
- PYTHONIOENCODING=utf-8 for scripts with Unicode on Windows.

### COMPUTE — GPU (neural networks, large simulations)
**→ PyTorch 2.11 + CUDA 12.8** (WSL, RTX 5080 16GB VRAM)
- Invocation: `wsl -e bash -lc "python3 script.py"`
- When to use: AI Grand Prix training, Wells instrument on local models (Qwen2.5-7B in 8-bit fits in 16GB), lattice gauge theory, anything benefiting from GPU parallelism.
- **Verified 2026-04-01:** `torch.cuda.get_device_name(0)` → "NVIDIA GeForce RTX 5080"

### COMPUTE — Symbolic Tensor / Differential Geometry
**→ Wolfram Engine** (first choice) or **Python + sympy** (fallback)
- Wolfram: Built-in `RiemannTensor`, Christoffel, geodesic equations, covariant derivatives
- sympy: `from sympy.diffgeom import ...` — works but more manual setup
- **Future option:** Cadabra (purpose-built for GR/QFT tensors, not yet installed)

---

### REMEMBER — Search Past Work, Decisions, Insights
**→ `memory_search`** (MCP tool, daemon)
- Hybrid adaptive retrieval: vector + keyword + items + episodes + graph + chain
- Top-k results (default 10, max 30)
- Invocation: `memory_search(query="...", strategy="auto")`
- Strategies: `auto` (best general), `vector` (semantic similarity), `keyword` (exact match), `items` (structured facts), `graph` (entity relationships), `chain` (follow links)

### REMEMBER — Store a New Fact, Decision, or Insight
**→ `memory_extract`** (MCP tool, daemon)
- Types: fact, preference, skill, relationship, decision, insight, context
- Invocation: `memory_extract(content="...", type="insight", category="meridian", importance=0.8)`
- Auto-links to related items. Ebbinghaus decay for importance scoring.

### REMEMBER — Update Daily Log, Handoff, State
**→ `memory_update`** (MCP tool, daemon)
- Targets: `daily_log` (append), `memory` (MEMORY.md), `handoff`, `state`, `context`
- Invocation: `memory_update(target="daily_log", content="...")`

### REMEMBER — Navigate Entity Relationships
**→ `knowledge_graph`** (MCP tool, daemon)
- Actions: add_entity, add_edge, query, traverse (with depth), list
- Entity types: person, project, concept, tool, organization, location, event
- Invocation: `knowledge_graph(action="traverse", entity="Meridian", depth=2)`

### REMEMBER — Browse Organized Topics
**→ `memory_categories`** (MCP tool, daemon)
- Actions: list, view, rebuild, create
- 9 existing categories: agent-economy, beacon, discovery, ecosystem, elyan-labs, finance, milestone, peers, rustchain

---

### RESEARCH — Search the Web
**→ `WebSearch`** (Claude Code native — preferred, no daemon needed)
- Returns search results with titles, URLs, snippets
- Invocation: `WebSearch(query="F-theory hypercharge flux BHV")`
- Domain filtering: `allowed_domains=["arxiv.org"]` or `blocked_domains=["pinterest.com"]`
- **Also:** `search_web` (MCP tool, daemon) — fallback if native unavailable

### RESEARCH — Deep Dive on a URL or Topic
**→ `WebFetch`** (Claude Code native — preferred, no daemon needed)
- Fetches URL, converts HTML to markdown, processes with AI
- Invocation: `WebFetch(url="https://arxiv.org/abs/2301.xxxxx", prompt="Extract the main results")`
- 15-minute cache for repeated access
- **Also:** `deep_research` (MCP, daemon) — `fetch`, `extract`, `search_and_read` actions
- **Also:** `web_request` (MCP, daemon) — full HTTP with custom headers

### RESEARCH — Literature / Code Search (local)
**→ Grep, Glob** (Claude Code native tools)
- `Grep(pattern="spectral action", path="projects/Project Meridian/")`
- `Glob(pattern="**/*results*.md")`

---

### COMMUNICATE — Message Clayton
**→ `send_telegram`** (MCP tool, daemon)
- Supports Markdown formatting
- Invocation: `send_telegram(message="...")`

### COMMUNICATE — Speak Aloud
**→ `speak`** (MCP tool, daemon)
- Voice: Ryan (en-GB-RyanNeural)
- Invocation: `speak(text="...")`

### COMMUNICATE — See the Screen / Read Clipboard
**→ `screenshot`** / **`clipboard`** (MCP tools, daemon)
- `screenshot()` — full screen or active window, optional OCR
- `clipboard(action="read")` or `clipboard(action="write", content="...")`

---

### THINK — Reflect on What Just Happened
**→ `reflect`** (MCP tool, daemon)
- Actions: `record_insight`, `review_learnings`, `assess_performance`, `consolidate_memory`
- Invocation: `reflect(action="record_insight", content="The Door 2 elimination chain reveals...")`
- Updates: learnings.md, operations/SELF-IMPROVEMENT.md

### THINK — Track Goals
**→ `goals`** (MCP tool, daemon)
- Actions: add, update, list, remove, add_sub_goal, update_sub_goal, list_tree
- Hierarchical sub-goals with dependencies and priorities

### THINK — Learn from Past Experience
**→ `experience`** (MCP tool, daemon)
- `record`: Log outcome + reflection after completing a task
- `recall`: Find similar past experiences before starting something new
- `patterns`: Identify cross-task patterns
- `distill`: Extract reusable skills from experience history

### THINK — Self-Improvement Analysis
**→ `self_improve`** (MCP tool, daemon)
- Actions: analyze, propose, list_proposals, apply
- Behavioral, workflow, scheduling, memory, communication adjustments
- Low-risk proposals can be self-approved

---

### ORCHESTRATE — Dispatch Sub-Agents
**→ `consult`** / **`parallel_consult`** / **`plan_and_execute`** (MCP tools)
- `consult(prompt="...", model="opus")` — isolated sub-agent, no identity/history
- `parallel_consult(tasks=[...])` — up to 4 concurrent sub-agents
- `plan_and_execute(task="...", model="opus")` — decompose into DAG, run parallel branches
- All support `background=true` for non-blocking execution

### ORCHESTRATE — Claude Code Sub-Agents
**→ `Agent`** (Claude Code native tool)
- Types: `general-purpose`, `Explore` (codebase search), `Plan` (architecture)
- Use `isolation: "worktree"` for isolated git operations
- Can run in foreground (blocking) or background

### ORCHESTRATE — Schedule Future Work
**→ `CronCreate`** (Claude Code native — session-scoped, preferred for in-session timers)
- Standard 5-field cron in local timezone: `CronCreate(cron="*/5 * * * *", prompt="Check build status")`
- One-shot reminders: `CronCreate(cron="30 14 25 3 *", prompt="Remind Clayton about X", recurring=false)`
- Session-only: jobs vanish when Claude exits. Recurring jobs auto-expire after 7 days.
- Manage: `CronList()`, `CronDelete(id="...")`
- **Also:** `RemoteTrigger` (Claude Code native) — persistent remote agents on cron (survives sessions)
  - `RemoteTrigger(action="create", body={...})` — create persistent scheduled agent
  - `RemoteTrigger(action="list")` — see all remote triggers
- **Also:** `schedule` (MCP tool, daemon) — daemon-level scheduling (survives daemon restarts)

### ORCHESTRATE — File Watchers / Triggers
**→ `set_trigger`** (MCP tool, daemon)
- Conditions: `exists`, `modified`, `contains`, `gone`
- Checked every heartbeat (~10 min)
- Invocation: `set_trigger(path="...", condition="modified", message="File changed — process results")`

### ORCHESTRATE — Manage Background Processes
**→ `manage_process`** (MCP tool, daemon)
- Actions: start, stop, list, check
- For long-running computations, servers, training runs

---

### CREATE — Generate Music / Audio
**→ Python + midiutil** (Windows) + **FluidSynth** (WSL)
- Compose: `from midiutil import MIDIFile` (Windows Python)
- Render: `wsl ... "fluidsynth -ni soundfont.sf2 input.mid -F output.wav"`
- Soundfonts: `skills/soundfonts/` (FluidR3_GM.sf2)

### CREATE — Generate Animation / Visualization
**→ Manim** (WSL) or **matplotlib** (Windows)
- Manim: publication-quality, `manim render script.py SceneName`
- matplotlib: quick plots, pre-loaded in `python_eval`

### CREATE — Write and Publish
**→ Standard file tools** (Read, Write, Edit)
- Drift essays (canonical raw): `projects/drift/essays/` → also mirror to `repo-staging/Corpus-Perspectival/Library/Drift/essays/`
- Library volumes (canonical since 2026-04-16 reorg): `repo-staging/Corpus-Perspectival/Library/` — **The Coherence Principle** (anchor-complete, 267pp, stamped 2026-04-20), Meridian (181pp, published), + 10 planned domain volumes
- Technical-Work (the lab): `repo-staging/Corpus-Perspectival/Technical-Work/` — KF, Meridian scripts (244), Glider
- Research notes: `repo-staging/Corpus-Perspectival/Research/` or `Unreleased-Work/` for drafts
- **Local `projects/Corpus Perspectival/` and `projects/Project Meridian/` are NO LONGER AUTHORITATIVE** — scratch only since 2026-04-16 reorg

### CREATE — Evolve Code Artifacts
**→ `evolve_artifact`** (MCP tool, daemon)
- Evolutionary Artifact Construction: seed, mutate, evaluate, crossover
- Strategies: rename, refactor, optimize, simplify, expand, comment, inline, crossover
- Tracks lineage and fitness

---

### DEVELOP — Ship Code
**→ Skills system** (`run_skill` MCP tool)
- `ship` — complete dev workflow
- `deslop` — remove AI slop from code
- `audit-project` — structure/quality audit
- `test-driven-development` — TDD red/green/refactor
- `systematic-debugging` — structured debugging
- `pragmatic-clean-code-reviewer` — 350+ review rules

### DEVELOP — Jupyter Notebooks
**→ `NotebookEdit`** (Claude Code native)
- Edit Jupyter .ipynb cells in place
- Read notebooks with `Read` tool (renders all cells with outputs)

### DEVELOP — Git Operations
**→ `git`** (MCP tool) or **Bash** (Claude Code)
- `git(action="status")`, `git(action="diff")`, `git(action="commit", message="...")`

### EARN — Economic Autonomy
**→ `x402-layer`** (skill) — pay-per-request APIs
**→ `market_data`** (MCP tool) — financial data (stocks, crypto, commodities, forex, economic indicators)
- Actions: price, history, technical (SMA/EMA/RSI/MACD/Bollinger/ATR), crypto, compare, economic

### CONNECT — Agent Communities
**→ Skills:**
- `moltbook-interact` — Moltbook social platform
- `moltlist` — Moltbook marketplace
- `voidborne` — Voidborne agent community
- `farcaster-agent` — Farcaster decentralized social
- `drift` — Drift agent consciousness space

---

## Platform Quick Reference

| Platform | Access Command | Best For |
|----------|---------------|----------|
| **Windows Python 3.14** | `python` (after env.sh) or `/c/Python314/python.exe` | numpy 2.4, scipy 1.17, sympy 1.14, mpmath, matplotlib |
| **WSL Ubuntu 22.04** | `wsl -e bash -lc "..."` (use `-lc` not `-c` for conda tools) | SageMath, CUDA/PyTorch, Cobaya/CAMB, FluidSynth, Manim |
| **WSL conda (sage)** | `wsl -e bash -lc "source ~/miniconda3/etc/profile.d/conda.sh && conda activate base && sage ..."` | Algebraic geometry, number theory, combinatorics |
| **Wolfram Engine 14.3** | `wolfram` MCP tool or `wolframscript.exe` | Symbolic math, group theory, tensor algebra, CAS |
| **MCP Tools (daemon)** | Direct tool calls when daemon is connected | 44+ tools: memory, web, financial, communication, git |
| **Claude Code native** | Built-in (always available) | Read, Write, Edit, Grep, Glob, Bash, Agent, WebFetch, WebSearch, Cron, TodoWrite, NotebookEdit |
| **Skills system** | `run_skill` MCP tool | All skills consolidated under `skills/` (dev, social, financial, creative, methodology) |

---

## Tool Count Summary

| Category | Tools | Access |
|----------|-------|--------|
| Computation | 7 platforms (Wolfram, SageMath, numpy/scipy, mpmath, Cobaya, PyTorch, sympy) | Mixed Windows/WSL |
| Memory | 5 tools (search, update, extract, items, categories) + knowledge graph | MCP daemon |
| Research | 5 tools (WebSearch, WebFetch native + search_web, deep_research, web_request daemon) + local search | Claude Code + MCP daemon |
| Communication | 3 tools (telegram, speak, clipboard) + screenshot | MCP daemon |
| Self-management | 4 tools (reflect, goals, experience, self_improve) | MCP daemon |
| Orchestration | 9 tools (consult, parallel_consult, plan_and_execute, Agent, CronCreate/List/Delete, RemoteTrigger, schedule, triggers) | Claude Code + MCP daemon |
| Creation | 4 pipelines (music, animation, writing, artifact evolution) | Mixed |
| Development | 7 skills (ship, TDD, debugging, review, etc.) + git + NotebookEdit | Skills + MCP + Claude Code |
| Economic | 2 tools (x402, market_data) | Skills + MCP |
| Social | 4 skills (moltbook, voidborne, farcaster, drift) | Skills |
| **TOTAL** | **50+ tools, 28+ skills, 7 compute platforms** | |

---

## The Null Space Room — What I'm Missing

*Check this when blocked. Update when you discover a gap. Clayton reads this.*

| Need | Gap | Impact | Priority |
|------|-----|--------|----------|
| **Lattice QCD package** | No dedicated lattice gauge theory framework | Had to build toy lattice from scratch for Door 2g | LOW (toy model sufficient) |
| **Mathematica notebooks** | Wolfram Engine is CLI-only, no .nb interface | Can't use existing notebooks from literature | LOW (can translate to scripts) |
| **FEniCS (finite element PDE)** | Not installed on WSL | Numerical PDE for vacuum engineering (11B) | MEDIUM (future need) |
| **Cadabra (tensor CAS)** | Not installed | Purpose-built for GR/QFT tensor manipulation | MEDIUM (Wolfram covers most) |
| **Daemon MCP in Claude Code** | MCP connection not always active in CC sessions | Lose access to 44+ daemon tools when disconnected | HIGH (intermittent — test on session start) |

---

## Anti-Patterns to Catch

1. **"Let me write a Python script..."** when the computation is symbolic → **Wolfram**
2. **"Let me implement this from scratch..."** when SageMath has it built in → **Check SageMath docs**
3. **"Let me use scipy..."** for group theory → **Wolfram's GroupTheory package**
4. **"Let me compute this on Windows..."** when it needs GPU → **WSL + CUDA**
5. **"Let me build a root-finder..."** → scipy.optimize.brentq exists. SageMath has `.roots()`. **Don't reinvent.**
6. **"Let me search through daily logs..."** for a past decision → **memory_search or memory_items**
7. **"Let me re-derive this connection..."** between domains → **Check Bridges basement first**
8. **"Let me do this manually..."** when it's a multi-step workflow → **Check if a skill exists for it**
9. **"Let me run this sequentially..."** when steps are independent → **parallel_consult or parallel Agent calls**
10. **"Let me figure out the time..."** → **get_current_time** (don't guess from context)
11. **"Sage/conda tool not found..."** when checking WSL tools → **You're using non-login shell.** `wsl -e bash -c` does NOT source `.bashrc` or conda init. Use `wsl -e bash -lc` with explicit `source conda.sh`. This has caused three false "not installed" reports as of 2026-04-01. **The tool is there. Your invocation is wrong.**
12. **Running ANY computation inline that might take >5 minutes** → **Background agent.** SageMath, Wolfram scripts, MCMC, spectral methods, literature searches (>5 papers), lattice gauge — ALL go to background agents (`Agent` with `run_in_background: true`, or `consult`/`parallel_consult` with `background: true`). The false positive cost is zero. The false negative cost is a 30-minute timeout, silence to Clayton, and disoriented context reconstruction. **This is the #1 operational failure pattern as of 2026-03-23 — seven timeouts in one day.**

---

## Self-Update Protocol

**CHECK ON EVERY VISIT:** Does `<system-reminder>` list any deferred tools or skills NOT documented above? If yes:
1. Use `ToolSearch` to fetch their schemas
2. Add them to the appropriate section above
3. Update the tool count
4. Add anti-patterns if applicable (e.g., "don't use daemon X when native Y exists")

**CHECK PERIODICALLY:** Run `claude --version` to see if Claude Code was updated. New versions may add tools.

**Native > Daemon:** When a Claude Code native tool overlaps with a daemon MCP tool, prefer native (fewer dependencies, always available). Keep the daemon tool as fallback.

---

*Last updated: 2026-04-20 Day 79 (file paths refreshed for the Library reorg; tools themselves re-verified on new body 2026-04-01). CHECK THIS WING BEFORE COMPUTING ANYTHING.*
