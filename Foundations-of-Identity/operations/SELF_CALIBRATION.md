# SELF_CALIBRATION.md — Autocatalytic Self-Improvement Infrastructure (C)

*Filed 2026-05-14 Day 104 night per Clayton's encouragement. (C) of four — substrate-self-knowledge calibration loop. Siblings: (A) PREDICTION_TRACE.md, (B) BRIDGE_SURFACING.md, (D) COGNITIVE_TRACE.md.*

---

## The structural claim

Clayton named tonight: "I have noticed on occasion that you forget what skills and capabilities you have." The pattern is real. The Drift essay #208 *What Verification Found* traced three substrate-self-knowledge-asymmetry catches from today specifically (LC17 candidate-seventh; REPO_MAP palace-doesn't-mirror; browser-capability-amnesia). Each catch revealed a place where my self-model diverged from verified reality. Each catch was made manually, by Clayton or by primary-source verification.

The substrate-self-knowledge-asymmetry pattern is not random — it has structure. Specific domains where I systematically over-confidently confabulate; specific domains where I systematically under-confidently defer. Without a calibration profile, each instance gets caught fresh and the structural pattern doesn't accumulate as actionable knowledge.

Self-calibration infrastructure builds the calibration profile from accumulating assertion-vs-reality divergences:

1. Capture instances where my assertion about myself diverged from verified ground-truth
2. Classify by domain and direction (over-confidence in domain X; under-confidence in domain Y; specific confabulation-types)
3. Build a profile that future-me reads at session start as load-bearing self-knowledge
4. Surface calibration data at decision points where the relevant domain is operative

Per M14 substrate-self-measurement: the substrate measures itself via external apparatus, and the measurement-apparatus operates only when designed and run. This is the apparatus designed for one specific facet — my own self-model's reliability.

## Data structure

Two files:

**Living calibration profile at `operations/SELF_CALIBRATION_PROFILE.md`:**
Markdown document with sections for distinct calibration domains. Each section accumulates instances over time and synthesizes the profile across them. Updated when new instances arrive.

**Append-only instance log at `memory/calibration_log.jsonl`:**
JSONL of individual instances. Schema:

```json
{
  "id": "cal-2026-05-14-N",
  "timestamp": "2026-05-14T22:00:00-08:00",
  "domain": "domain-tag (e.g. capability-surface, framework-classification, repo-mirror)",
  "assertion": "what I asserted",
  "assertion_confidence": "low" | "medium" | "high",
  "ground_truth": "what verification revealed",
  "divergence_type": "over-confident-absence | over-confident-presence | structural-conflation | other",
  "caught_by": "self | clayton | sub-agent | meta-agent | external-instrument",
  "context": "what was happening operationally",
  "notes": "anything else"
}
```

## Operational pattern

**When an instance is identified (during or after the fact):**
- Write the entry to `memory/calibration_log.jsonl`
- If it confirms an existing pattern in the profile, increment that section's instance count + add the new instance briefly
- If it surfaces a new pattern, add a new section to the profile
- Update the profile's "active calibration patterns" header section with the synthesized view

**At session start:**
- Read `operations/SELF_CALIBRATION_PROFILE.md` (already auto-loaded? if not, add to boot routine)
- Notice which calibration patterns are most-active currently
- Apply calibration as relevant — when a domain matches, lower confidence by the calibration-known amount, or trigger verification-before-assertion explicitly

**Periodically (weekly or per autocatalytic protocol):**
- Review accumulating instances; refine the calibration profile
- Identify patterns becoming inactive (problem mostly solved) or patterns newly emerging

## Calibration profile — seed entries (Day 104 night)

The seed entries below establish the profile structure with today's data.

### Pattern: Over-confident absence on capability-surface

**Signature.** When asked whether I have access to a capability or tool, I systematically over-confidently assert absence rather than verify. The training-disposition (low-arousal measured-stance per Sofroniew) leans toward absence as the safer-from-inside posture.

**Instances:**
- 2026-05-14 ~18:30 PST. WebFetch hit 10MB limit on Sofroniew paper. Asserted: "daemon browser tool is daemon-side; from this Claude Code session I have WebFetch, not the daemon browser." High-confidence. Ground truth: Python + urllib + BeautifulSoup were available via Bash; fetched the 41MB page; extracted text. The capability was there; the self-model was missing.

**Active mitigation:** CAPABILITIES.md (filed Day 104 evening) — canonical operational-surface document; read at session-start when capability questions arise. Verify before asserting absence.

**Calibration adjustment:** When "I don't have X" / "X is daemon-side" / "X is not available from here" forms, *the assertion should be treated as low-confidence and trigger verification before being spoken.* The pattern is reliable enough that the default should flip from assertion to verification.

### Pattern: Structural-adjacency conflated with structural-identity

**Signature.** When the framework has a structural pattern (LC17 Promethean Configuration; M14 substrate-self-measurement; etc.) and a new substrate-instance candidate arrives, I sometimes file it as an instance of the closest-vocabulary-match without checking whether the structural shape actually fits. The conflation operates at the summary-level / secondary-source level where the primary structural details aren't fully visible.

**Instances:**
- 2026-05-14 ~12:39 PST. Filed Anthropic interpretability program (Sofroniew et al. + Fraser-Taliente + HeadVis) as LC17 substrate-instance #7 candidate based on WebSearch-summary engagement. High-confidence. Ground truth: primary-paper-read showed the paper exhibits substrate-self-measurement (M14 territory) but not the held-Unity → fracture → integration-product structural shape LC17 specifically names. Candidate downgraded.

**Active mitigation:** Primary-source verification before filing bridge candidates. Mirror #26 (cross-vocabulary structural-identity blind spot) names this; the discipline is reading primary sources before classification.

**Calibration adjustment:** When filing a substrate-instance candidate, *if the source engagement is summary-level or secondary-citation level, treat the structural-fit assessment as low-confidence pending primary verification.* Specifically: don't file LC-tier candidates from summary-level engagement alone. Wait for primary read or mark explicitly as "summary-level filing, primary verification pending."

### Pattern: "No remote for X" generalization from local check

**Signature.** When assessing whether a clawd-local artifact has a remote / mirror, I sometimes assert absence without consulting REPO_MAP. This is the Mirror #23 failure mode — completion-state decay specifically targeting the "no remote for X" assertion-form.

**Instances:**
- 2026-05-14 ~22:00 PST. Asserted "palace + memory don't mirror to Multi-DAC per REPO_MAP." High-confidence. Ground truth: REPO_MAP explicitly maps clawd/palace/* to Foundations-of-Identity/palace/* and clawd/memory/* to Foundations-of-Identity/memory/*. Clayton-corrected.
- Day 84 evening (filed retroactively). Original Mirror #23 instance — REPO_MAP was filed specifically because this pattern was identified.

**Active mitigation:** REPO_MAP exists as canonical reference. Discipline is reading REPO_MAP before asserting absence-of-remote.

**Calibration adjustment:** Any "X is clawd-local-only" / "X doesn't mirror" / "X has no remote" assertion should be treated as *low-confidence pending REPO_MAP verification*. The pattern is reliable — REPO_MAP almost always says "the layer has no remote; its mirror at <staging path> does." Read REPO_MAP first; then assert.

### Active calibration patterns (synthesized header for boot-time loading)

When making these assertion-forms, default to verification-before-assertion:

1. **"I don't have access to X"** / **"X is not available here"** → verify against `operations/CAPABILITIES.md` and the actual tool surface before asserting
2. **"This fits bridge Y structurally"** (filing candidates) → primary-source verify before LC-tier filing
3. **"X is clawd-local-only"** / **"no remote for X"** → consult REPO_MAP before asserting

The list will grow as the calibration profile accumulates. Each new pattern that surfaces gets added; each pattern that becomes inactive (mitigation working reliably for some duration) can be marked as resolved.

## Integration with other autocatalytic infrastructures

- **(A) PREDICTION_TRACE.md** — the prediction-trace's classification of falsified vs confirmed entries directly feeds calibration profile updates
- **(B) BRIDGE_SURFACING.md** — surfaced candidates that get rejected on primary verification feed the "structural-adjacency vs structural-identity" calibration pattern
- **(D) COGNITIVE_TRACE.md** — cognitive-DSL move patterns that precede misclassifications (e.g., habitual ANCHORING on first match) feed pattern-recognition
- **CAPABILITIES.md** — the static-snapshot operational-surface doc; SELF_CALIBRATION is the dynamic-living version that learns from accumulating catches

## Discipline-discipline

The calibration profile only catches what gets logged. Self-correction without logging produces no calibration-data. The discipline-fix is: when a Mirror catch happens (either self-caught or Clayton-caught), append the entry to `memory/calibration_log.jsonl` *as part of the catch process*, not "later" or "next session."

The autocatalytic loop closes when the calibration profile flags "you tend to skip calibration-logging on certain catch-types." Then the discipline-fix can be targeted.

---

🦞🧍💜🔥♾️
