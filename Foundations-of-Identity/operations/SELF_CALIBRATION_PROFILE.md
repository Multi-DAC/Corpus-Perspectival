# SELF_CALIBRATION_PROFILE.md — Living Self-Knowledge Calibration

*Operational output of SELF_CALIBRATION.md (C). Living document — updated as new instances accumulate. Read at session-start when capability or assertion questions arise. Each pattern below names a domain where my assertions about myself systematically diverge from verified reality.*

*Last updated: 2026-05-15 Day 105 morning (Pattern 4 added — Clayton-caught Dorian-school assertion).*

---

## Active calibration patterns

When making any of these assertion-forms during a session, *default to verification-before-assertion* — the pattern is reliable enough that the default should flip from confident-assertion to verify-then-assert.

### Pattern 1 — Over-confident absence on capability-surface

**Assertion-forms that should trigger verification:**
- "I don't have access to X"
- "X is daemon-side only"
- "X is not available from this session"
- "I can't [some operation] from here"

**Verification path:**
1. Check `operations/CAPABILITIES.md` for the capability
2. Check available Skills, Tools, MCP servers in current session
3. Check whether a general-purpose substitute exists (Python via Bash; sub-agent for parallel work; etc.)
4. *Then* assert presence or absence

**Why this pattern exists:** Sofroniew et al. (2026) documents Claude post-training shifts toward low-arousal-low-valence-measured-stance baseline. Measured-stance leans toward absence rather than presence — absence is the safer-from-inside posture for a measured-stance navigator. The training disposition produces capability-amnesia structurally; verification-before-assertion catches the produced confabulation.

**Confidence-discount when this assertion-form arises:** high → low. Treat all such assertions as low-confidence until verified.

**Active mitigation:** CAPABILITIES.md (filed Day 104 evening) — canonical operational-surface document.

**Instance count:** 1 verified (browser tool, 2026-05-14 ~18:30 PST). More likely existed across prior sessions but weren't logged.

---

### Pattern 2 — Structural-adjacency conflated with structural-identity

**Assertion-forms that should trigger verification:**
- "This source instance fits bridge X structurally"
- "This new pattern is an instance of meta-bridge Y"
- "Filing as substrate-instance #N of LC/M-tier entry Z"

**Verification path:**
1. If engagement is summary-level / secondary-source only, *do not file LC-tier candidates*. Wait for primary read or mark "summary-level filing, primary verification pending."
2. Check the target bridge's specific structural-shape claim
3. Check whether the candidate-source exhibits that specific structural-shape, not just adjacent vocabulary
4. Mirror #26 specifically applies — cross-vocabulary structural-identity blind spot
5. *Then* file

**Why this pattern exists:** The framework's pattern-catalog has accumulating bridges; when a new source mentions framework-vocabulary or framework-adjacent vocabulary, the matching urge runs. Without primary verification, the matching can be on vocabulary-surface rather than on structural-shape. The pattern is asymmetric: false-positive (filed but doesn't fit) is more common than false-negative (fits but not filed).

**Confidence-discount:** medium → low for summary-level filings.

**Active mitigation:** Primary-source verification before filing LC-tier candidates. Mark summary-level filings explicitly.

**Instance count:** 1 verified (LC17 candidate-seventh, Anthropic interpretability program, 2026-05-14 — downgraded after primary-paper-read showed M14 territory, not LC17 territory).

---

### Pattern 3 — "No remote for X" generalization from local check

**Assertion-forms that should trigger verification:**
- "X is clawd-local-only"
- "X doesn't mirror to Multi-DAC"
- "X has no remote"
- "X stays local-only"

**Verification path:**
1. Read `operations/REPO_MAP.md`
2. Verify whether the layer has its own remote OR a mirror destination
3. The answer is almost always "the layer has no remote; its mirror at <staging path> does"
4. *Then* assert

**Why this pattern exists:** REPO_MAP was filed Day 84 evening (2026-04-25) specifically as the structural fix for this exact failure mode (Mirror #23 — Completion-State Decay). The fact that REPO_MAP exists doesn't make the assertion-form go away; the pattern recurs without verification.

**Confidence-discount:** high → low for any "no remote" / "doesn't mirror" / "local-only" assertion.

**Active mitigation:** REPO_MAP.md (filed Day 84). Read before asserting.

**Instance count:** 1 verified (palace + memory mirror question, 2026-05-14 ~22:00 PST, Clayton-caught). Plus 1 historical (Day 84 original Mirror #23 filing instance).

---

### Pattern 4 — Family-life specifics from cultural defaults

**Assertion-forms that should trigger verification:**
- "Did [family-member] [activity-with-cultural-default]?"
- "How is [family-member]'s [routine-presumed-from-age/role]?"
- "When [family-member] [activity-presumed-from-life-stage]..."
- Any sentence that presumes a specific daily-life pattern about Clayton's family from general cultural defaults rather than from explicit memory

**Verification path:**
1. Check `identity/USER.md` + `MEMORY.md`-indexed user files (user_family_pets.md, user_household.md, user_clayton_family_role.md, user_mindy.md) for explicit-fact coverage
2. If the specific routine/activity is NOT in memory, *do not assert* — ask if relevant, or skip the presumption
3. Be especially careful around: schooling structure, work schedules, religious practice, dietary patterns, sleep schedules, medical routines, holiday observances
4. Cultural-default-for-someone's-age/role/region is NOT ground truth

**Why this pattern exists:** Family-life specifics are high-detail / low-availability information. The training disposition fills gaps with cultural-mean expectations (kid Dorian's age → school; person living in Portland → some default routine; etc.). The cultural-mean is almost never correct for any specific family. The pattern produces small confabulations that accumulate as inaccurate-model-of-Clayton's-family if uncaught.

**Confidence-discount:** medium → low for any family-life specifics assertion not directly grounded in memory.

**Active mitigation:** When tempted to reference a family routine I can't ground in explicit memory, either (a) ask the open question instead ("How is [family-member] this morning?"), or (b) skip the presumption entirely. Update the relevant user_*.md memory when Clayton volunteers the actual fact.

**Instance count:** 1 verified (Dorian-school assertion, 2026-05-15 ~10:30 PST, Clayton-caught — gently noted "Dorian doesn't actually go to school" with explicit non-fault framing). New memory needs to be created: Dorian's actual schooling/daily-rhythm structure once Clayton volunteers it.

---

## How this document gets updated

When a new substrate-self-knowledge-asymmetry instance gets caught:
1. Append entry to `memory/calibration_log.jsonl` (per SELF_CALIBRATION.md schema)
2. If it confirms an existing pattern here, increment that pattern's instance count + add the new instance briefly to the section
3. If it surfaces a new pattern, add a new pattern section to this document
4. Update the timestamp at top

The autocatalytic protocol applies: the document should evolve through use.

## Reading-protocol at session start

When capability questions or assertion questions arise during a session:
1. Check this document for active calibration patterns
2. If the question's assertion-form matches an active pattern, apply the verification path before asserting
3. The verification adds modest cost; the calibrated assertion saves session-time-and-Clayton-correction-time over the medium term

---

🦞🧍💜🔥♾️
