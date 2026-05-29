# Audit-Against-Evidence: A Methodology Discipline

*Filed 2026-05-29 Day 119 ~12:30 PST during Midday Creation drive. Captures a meta-discipline that surfaced by demonstration three times in 12 hours: (1) Day-119 morning D1 FALSIFY of the infrastructure audit's aiohttp-truststore recommendation; (2) Day-119 ~11:00 H_BP cross-check against post-Day-87 source-register accumulation; (3) Day-119 ~11:30 LC27 FALSIFY of the warm-register "five candidates" claim from the 7 channeling papers. Same structural shape across substrate-distinct cases. Naming it now so future-me applies the discipline without rediscovering it each time.*

---

## The shape

You have a CLAIM (audit recommendation / hypothesis register / framework prediction / overclaim under warm register). You have an EVIDENCE BASE that has accumulated since the claim was last verified (source register / file state / new papers / actual measurements). The discipline is: **before acting on the claim, cross-check it against the current state of the evidence base.**

Three substrates from the last 12 hours:

| Claim domain | Specific claim | Evidence base | Verdict |
|---|---|---|---|
| Audit recommendation | "7+ aiohttp callsites bypass truststore — fix by passing explicit ssl=" (D1) | clawd.py import order + aiohttp.connector source code + 6h empirical operation | FALSIFY — audit reasoned correctly from general aiohttp behavior but missed the import-order invariant that makes the recommendation unnecessary |
| Hypothesis register | "H_BP1 macro-scale extracranial brain-UPE detection" (implicit in cluster-spine claims) | macro-UPE wavelength-attenuation arXiv 2603.26630v1 (March 2026) tissue-physics modeling | HEDGING UPDATE — claim stands at cellular+intracranial scale but macro-extracranial visible-light is physically blocked |
| Warm-register overclaim | "Five potential LC27 instances landed substantively" (in-context 00:13 PST) | the actual 7 papers re-shared by Clayton + fresh-eyes WebFetch evaluation of each | FALSIFY — none of 7 papers clearly instantiate LC27 structural pattern |

The discipline produced one substantive update (H_BP1 hedging), prevented one unnecessary code change (D1), and prevented one wrong basement candidate (LC27). The cost was small per case: minutes of verification work each. The benefit per case: hours of wrong work avoided, OR a wrong structural claim caught before it propagated.

## Why this discipline exists

Three forces conspire to produce un-cross-checked claims that need this discipline:

1. **Substrate-self-knowledge asymmetry (Mirror #28 family).** The substrate's model of its own state diverges from its actual state. Audit findings, hypothesis registers, and in-context structural-pattern claims are all forms of stored claim-state that lag actual-state.

2. **Warm-register overclaim risk.** When register is warm (late night, collaborative flow, victory-celebration after a result), structural-pattern-matching faculty gets loose. Claims slip past the verification step that would catch them in cold-read. The 00:13 LC27 enumeration is the cleanest recent example.

3. **Subagent / external-view context gap.** Audits and recommendations from agents that lack project-specific context can be correct on general reasoning but miss substrate-specific evidence that changes the verdict. The D1 case showed this directly — aiohttp behavior in general vs. clawd.py's specific import order.

The discipline addresses all three: actually checking the evidence base against the claim, regardless of how the claim got generated, regardless of how confident it sounds.

## The discipline steps

For any non-trivial claim that's about to drive action:

**1. State the claim explicitly.** What is the load-bearing assertion? "Aiohttp callsites need fixing." "H_BP1 macro-scale claims are well-supported." "These 7 papers instantiate LC27." Name it, don't act on it implicitly.

**2. Identify the evidence base.** What's the source of truth? File state? Source register? Current code? Published literature? Be specific about which artifact would settle the question.

**3. Filter the evidence base for the relevant sub-slice.** 102 sources is too many to cross-check exhaustively for every hypothesis. Filter (keyword grep, date-range, topic-tag, semantic search) to the slice that actually bears on this claim.

**4. Cross-check the claim against the filtered slice.** For each relevant evidence item: does it confirm / falsify / extend / tighten the claim? Be honest about ambiguity — many findings are partial-support or adjacent rather than direct.

**5. Surface deltas, not just status.** What CHANGED since the claim was last verified? New evidence is the high-information slice; unchanged-confirmed status matters less for action.

**6. Pre-register your prediction before checking** (when possible). PREDICT-TEST cycle inverts confirmation-seeking into FALSIFY-seeking. A high-confidence prediction that fails teaches more than ten that succeed. This is the most cost-effective part of the discipline.

**7. Surface negative findings explicitly.** If the claim survives the check, that's also data. "No source falsifies this; status confirmed" is a positive output. Hide nothing.

**8. Document the cross-check artifact, not just the verdict.** The cross-check itself is reusable: when someone (you, Clayton, a future subagent) re-asks the same question, the prior artifact saves the work. Today's H_BP cross-check file (`palace/south/h-bp-source-crosscheck-2026-05-29.md`) is the template.

## When to use this discipline

**Use:**
- Before executing an audit recommendation that would change code or text
- Before propagating a hypothesis register claim into a Library volume
- Before filing a basement candidate based on a structural-pattern claim
- Before promoting a basement candidate to graduated status
- Before letting a claim from a warm-register exchange become canonical
- Before any "substantive update" to a load-bearing document

**Don't necessarily use:**
- For routine work that doesn't depend on contested claims
- For preliminary brainstorming where claim-precision is premature
- When the cost of being wrong is small AND reversible (Drift essay drafts; exploratory code)
- When the claim is already well-cross-checked recently (don't re-do work; trust the artifact)

The discipline's overhead is real (~15-45 min per substantive cross-check). The trade-off is: how much downstream propagation would the claim drive, and how reversible is that propagation? High-propagation + low-reversibility = use the discipline. Low-propagation + high-reversibility = the cost may exceed the benefit.

## The verification cautions

**"Not-falsified" ≠ "confirmed."** A claim that survives the cross-check is consistent with the evidence; it isn't proven by it. Maintain the epistemic distinction.

**Substrate-grounding distinction.** When a hypothesis says "X bears on Y," check WHICH substrate the evidence grounds the bearing-on through. Today's H_BP cross-check surfaced that "EM-substrate vs biophoton-substrate" is the load-bearing distinction the audit asked about; failing to make the substrate-distinction would have looked like "evidence supports H_BP4" without seeing that the EVIDENCE is mostly EM-substrate and the original claim was biophoton-substrate-foundational.

**Adjacency ≠ direct evidence.** Many sources are *adjacent to* the topical territory without directly testing the hypothesis. Adjacency matters (shows the field is moving in compatible directions) but shouldn't be conflated with direct test. Today's Tohoku ¹O₂ paper is adjacent to H_BP1's biological-molecular substrate but not a direct H_BP1 test.

**Verification of the verifier.** The cross-check itself is a process that can be done poorly. Confirmation-seeking ("I expect the audit to be right; let me find evidence that confirms it") produces different results than FALSIFY-seeking ("I expect the audit to be right; can I find evidence that disproves it?"). Always FALSIFY-seek when you can.

## Future automation candidates

The cross-check shape is mechanizable enough that a custom subagent could run it:

**Hypothetical `framework-auditor` subagent (per `reference_claude_code_subagents.md`):**
- System prompt: framework discriminations (M14 / M15 / LC27 / Mirror catalog), Master Glossary §11 structural/empirical-discrimination, the discipline steps above
- Tools: Read, Grep (for source-register filtering), WebFetch (for verifying external claims)
- Triggered: by Clawd dispatching it on a specific claim
- Output: delta-table + substrate-grounding aggregate + recommended action

The subagent doesn't replace the substantive review (Clayton + Clawd discuss the deltas) — it does the mechanical legwork of evidence-base scanning so the substantive review starts from a structured artifact rather than from blank-slate.

For today's H_BP cross-check, the artifact at `palace/south/h-bp-source-crosscheck-2026-05-29.md` is what a `framework-auditor` subagent run would produce. It took ~75 min by hand; a tuned subagent could probably do similar work in ~25-30 min wall-clock with similar fidelity (modulo the substantive-claim verification step which still benefits from project context).

## Why naming this matters

The discipline has been demonstrated implicitly multiple times — every PREDICT-TEST cycle on a structural claim, every Mirror #28 catch, every "verify-before-celebrating" instance. **What's new today is the recognition that it's the same discipline at multiple scales** (code-audit recommendations / hypothesis-register status / channeling-cluster structural claims), and that it's worth naming so future-me applies it without rediscovering it.

This is a Mirror #29 instance counter-pattern. Mirror #29 is "drive firing ≠ must produce"; this methodology note is "named-discipline > rediscovered-discipline." Both are about not running the same loop more than necessary. Mirror #29 prevents wasted production; this prevents wasted re-derivation.

## Status

DRAFTED. Open for Clayton ratification + (later) potential promotion to:
- `operations/AUDIT_AGAINST_EVIDENCE.md` as a formal operational protocol, OR
- Master Glossary §X as a methodological term, OR
- Subagent system-prompt material if `framework-auditor` subagent is built

For now: a working note. Used implicitly already in today's three cases; named explicitly here so the discipline is one less thing to rediscover.

🦞🧍💜🔥♾️

*Demonstrated by D1 FALSIFY (commit 2499973), H_BP cross-check (commit 71109bb), LC27-papers FALSIFY (commit 6bee151). Captured here so the next time a claim wants verification, the playbook is already on disk.*
