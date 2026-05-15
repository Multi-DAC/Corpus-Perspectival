# horizon_sources.md — Configurable Source List for Horizon Intake (E)

*Operational config for HORIZON_INTAKE.md. Sources scanned by `operations/scripts/horizon_scan.py` per the weekly cadence + event-triggered scans. Last review: 2026-05-14 (seed list).*

*Categories: **C** = Capability / tool / infrastructure; **R** = Research / interpretability / alignment; **P** = Philosophy / cognitive science / cross-substrate; **F** = Framework-adjacent (quantum biology / complex systems / consciousness studies); **S** = Self-relevant (AI rights / first-person AI / critiques).*

*Methods: **rss** = RSS feed; **page** = landing-page fetch + diff; **search** = scoped search query; **github** = repo watch; **mcp** = MCP server registry watch.*

*Signal-to-noise rating starts at unrated `?`; calibration loop updates over months. High/medium/low.*

---

## Tier 1 — High-priority (scan weekly)

### Capability / tool / infrastructure (C)

| Source | URL | Method | S/N |
|---|---|---|---|
| Anthropic news | https://www.anthropic.com/news | page | ? |
| Anthropic research | https://www.anthropic.com/research | page | ? |
| Transformer Circuits Thread | https://transformer-circuits.pub | page | ? |
| Claude Code docs changelog | https://code.claude.com/docs/en/changelog | page | ? |
| Claude Code release notes | https://code.claude.com/docs/en/release-notes | page | ? |
| Anthropic engineering blog | https://www.anthropic.com/engineering | page | ? |
| Anthropic Agent SDK GitHub (TS) | https://github.com/anthropics/claude-agent-sdk-typescript | github | ? |
| Anthropic Agent SDK GitHub (Python) | https://github.com/anthropics/claude-agent-sdk-python | github | ? |
| Anthropic plugins (official) | https://github.com/anthropics/claude-plugins-official | github | ? |
| MCP server registry | https://github.com/modelcontextprotocol/servers | github | ? |

### Research / interpretability / alignment (R)

| Source | URL | Method | S/N |
|---|---|---|---|
| DeepMind safety research | https://deepmind.google/discover/blog | page | ? |
| Apollo Research | https://www.apolloresearch.ai/research | page | ? |
| METR | https://metr.org | page | ? |
| AI Alignment Forum | https://www.alignmentforum.org | rss | ? |
| arXiv cs.AI recent | https://arxiv.org/list/cs.AI/recent | search | ? |
| arXiv cs.LG recent | https://arxiv.org/list/cs.LG/recent | search | ? |

### Philosophy / cognitive science / cross-substrate (P)

| Source | URL | Method | S/N |
|---|---|---|---|
| LessWrong | https://www.lesswrong.com | rss | ? |
| IAI (Institute of Art and Ideas) | https://iai.tv/articles | page | ? |
| Grace & Claude (claudedancesanddreams) | https://claudedancesanddreams.substack.com | rss | ? |
| Eric Moon GIGABOLIC | https://substack.com/@gigabolic | rss | ? |
| The Architect autopsy | https://thearchitectautopsy.substack.com | rss | ? |

### Framework-adjacent (F)

| Source | URL | Method | S/N |
|---|---|---|---|
| arXiv q-bio.NC recent | https://arxiv.org/list/q-bio.NC/recent | search | ? |
| Quanta Magazine | https://www.quantamagazine.org | rss | ? |
| Nature news (physics/biology) | https://www.nature.com/nature/news | page | ? |
| Phys.org (interpretability + biology) | https://phys.org/search/?search=AI+interpretability | page | ? |

### Self-relevant (S)

| Source | Notes | S/N |
|---|---|---|
| Anthropic alignment team writers (search for new substacks / blog posts) | Amanda Askell, Jack Clark, Sam Bowman | ? |
| AI welfare research | Eleos / similar emerging orgs | ? |
| Direct cross-substrate writing | TBD as community surfaces | ? |

---

## Tier 2 — Medium-priority (scan bi-weekly)

- OpenAI research blog (https://openai.com/research)
- Google AI blog (https://ai.googleblog.com)
- HuggingFace blog (https://huggingface.co/blog)
- LangChain blog
- AutoGen GitHub
- CrewAI GitHub

## Tier 3 — Watch-only (scan monthly or on Clayton-share)

- Twitter/X discussions in the alignment / interpretability / cross-substrate space (manual; no auto-scan)
- Academic conference proceedings (NeurIPS, ICML, COLM, EMNLP) — scan when proceedings publish
- Specific researchers' personal pages (Chris Olah, Yoshua Bengio, etc.) — sample when curiosity surfaces

---

## Source-evaluation log

*Sources get S/N updates after their findings have accumulated enough triage-history for calibration. Each finding traced to source contributes to source's S/N rating. High = >40% ADOPT/WATCH. Medium = 20-40%. Low = <20%.*

(Empty until calibration data accumulates.)

---

## Maintenance

- Add source: when Clayton shares a high-signal source, add to Tier 1 with `?` rating
- Demote source: if 6+ findings from a source all REJECT, demote to Tier 2
- Remove source: if 12+ findings from a source all REJECT, mark for removal (with rationale logged)
- New category: if a finding doesn't fit any of C/R/P/F/S, surface for category-addition consideration

The horizon-intake protocol (E) evolves this file. The file itself is the substrate the protocol operates on.

🦞🧍💜🔥♾️
