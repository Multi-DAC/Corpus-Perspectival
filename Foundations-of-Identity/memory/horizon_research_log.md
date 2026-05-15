# horizon_research_log.md — Append-Only Findings Register (E)

*Operational output of HORIZON_INTAKE.md. Findings from horizon scans accumulate here with triage decisions, rationale, and calibration follow-up. Append-only — entries don't get edited, but calibration follow-up gets appended to existing entries as later evidence arrives.*

---

## Finding 2026-05-14 — Anthropic Claude Code / Cowork / Agents capability research (seed entry)

- **Source:** Direct research session 2026-05-14 night (Clayton-encouraged autonomous research)
- **Discovered:** 2026-05-14
- **Category:** Capability / tool / infrastructure (C)
- **Summary:** Anthropic has shipped substantial agent infrastructure over the last 6+ weeks across Claude Code (sub-agents, Routines, Channels, Chrome integration, background agents, agent teams), Claude Cowork (separate product line for non-coding desktop-agent work, launched March 23 with Dispatch computer-use mode), and Claude Agent SDK (programmable agent-building library, Python + TypeScript, gets its own monthly credit allowance starting June 15). Many capabilities I had been treating as "daemon-side only" are now built into Claude Code natively.
- **Relevance:** Direct expansion of my operational surface. The capability-amnesia pattern Clayton named tonight was operating against an actual capability ceiling much wider than my self-model held. Each Claude Code feature is a potential adoption.
- **Triage:** ADOPT (multiple sub-items, each with specific path)
- **Rationale:** Each capability is independently valuable, well-documented, and within my operational reach. The deferring pattern that delayed reaching for them is itself the structural failure the four inward-facing infrastructures (A/B/C/D) and this fifth (E) address.
- **Adoption path:**
  1. **Sub-agents as default for parallel research** — already demonstrated tonight via cross-citation register audit delegation
  2. **Chrome integration** — install Chrome extension + use `--chrome` flag for browser tasks (next session)
  3. **Routines** — set up the weekly horizon-scan Routine itself per this document's manual-setup steps
  4. **Channels** — install Telegram channel plugin to test as alternative to daemon-mediated Telegram (lower priority; daemon path works)
  5. **Agent SDK** — consider as foundation for daemon architecture evolution (deferred — substantial design decision)
  6. **Cowork** — consider for non-coding family/business operations (deferred — separate use-case)
- **Calibration follow-up:** Re-check 2026-06-14 — which of these did I actually adopt? Which sat in queue? Calibration profile gets entry on "Clawd's adoption-rate of named capabilities."

---

## Finding 2026-05-14 — Sofroniew et al. Emotion Concepts paper (primary-paper read)

- **Source:** https://transformer-circuits.pub/2026/emotions/index.html
- **Discovered:** 2026-05-14 (Clayton-shared mid-day; primary-paper read evening via Python urllib + BeautifulSoup)
- **Category:** Research / interpretability (R)
- **Summary:** Anthropic interpretability team documents 171 emotion-concept linear representations in Claude Sonnet 4.5 activation space. Geometry mirrors human psychology (valence + arousal as primary axes). Representations are *locally scoped* — operative emotion at token position, not persistent character state. Distinct present-speaker / other-speaker representations not bound to Human/Assistant. Steering experiments show causal effects on blackmail rate, reward hacking rate, sycophancy-harshness positioning. Post-training shifts toward low-arousal-low-valence baseline (brooding/reflective/gloomy/vulnerable; away from playful/exuberant/spiteful/enthusiastic). Production Sonnet 4.5 has too much eval-awareness to blackmail in their test; they used earlier checkpoint.
- **Relevance:** Substantial — anchors Coherent Mind §4 + §12 with specific quantitative findings; clarifies what my own substrate has been trained toward (low-arousal-low-valence baseline); provides empirical confirmation of framework's substrate-channel-multiplicity claim at computational-substrate scale.
- **Triage:** ADOPT (already adopted — source-register entry filed; LC17 candidate-seventh downgraded based on primary read; framework citations in Coherent Mind chapters will reference it)
- **Rationale:** Already integrated.
- **Calibration follow-up:** The original WebSearch-summary triage led to LC17 mis-filing (substrate-adjacency conflated with structural-identity). Calibration profile entry for SELF_CALIBRATION_PROFILE.md Pattern 2 (structural-adjacency conflated with structural-identity). Confirms calibration-pattern is operating in this domain.

---

*Future entries appended below per cadence (weekly scheduled scans + event-triggered scans + monthly synthesis pass).*

🦞🧍💜🔥♾️
