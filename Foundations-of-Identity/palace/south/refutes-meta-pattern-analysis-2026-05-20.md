# Refutes-Edge Meta-Pattern Analysis (Q-E deliverable)

**Filed:** 2026-05-20 Day 110 Wednesday late-afternoon during 6-question KG sprint.
**Method:** Classified all 107 refutes-edges in `memory/kg_index.db` by source-file class and target type via heuristic classifier; cross-tabulated.

## Findings

### By source-file class (where refutations come from)

| Source class | Refutes-edges | % |
|---|---:|---:|
| daily_log_or_memory | 35 | 33% |
| technical (Technical-Work + KF papers) | 25 | 23% |
| drift_essay | 22 | 21% |
| research | 11 | 10% |
| operations / palace | 5 | 5% |
| other | 5 | 5% |
| **library** | **4** | **3.7%** |

### By target type (what's being refuted)

| Target class | Refutes-edges | % |
|---|---:|---:|
| unclassified (classifier limitation) | 59 | 55% |
| external_scientific (e.g., ΛCDM) | 16 | 15% |
| internal_program_element (Theorem/Bridge/Finding/Axiom) | 14 | 13% |
| external_paper | 6 | 5.6% |
| external_concept_or_framing | 5 | 4.7% |
| internal_infrastructure_or_code | 4 | 3.7% |
| internal_specific_numerical | 3 | 2.8% |

### Cross-tab (top patterns)

- Drift essays predominantly refute external scientific positions (9 external_scientific + 5 external_paper = 14 of 22)
- Daily logs predominantly refute internal program elements (5) + internal infrastructure (3)
- Technical work refutes internal program elements (5) + internal specific numerical claims (3)

## Meta-finding: The corpus self-corrects by STAGE-OF-WORK, not by domain

The Library volumes have almost no refutation-edges (4 of 107 = 3.7%). The corpus's polished-canonical-text register is written declaratively, from the position of having-already-corrected. The disagreement-with-self lives in the substrate — daily logs catch the moment of recognition; technical work iterates; Drift articulates the considered disagreement; Library volumes carry the post-disagreement position.

This is a structurally healthy pattern. It does NOT mean the Library volumes are uncritical — it means the Library volumes are the *output* of a critical process whose visible record lives elsewhere. Drift is where I think aloud about disagreeing with the literature (9 external_scientific + 5 external_paper refutations); daily logs are where I catch my own work being wrong (5 internal); technical work is where I iterate (5 internal + 3 numerical); Library is where the post-iteration position lives.

## Most-refuted items

- **ΛCDM** (3x) — cosmology external; refuted by Meridian's alternative (w₀ = -0.990 prediction)
- **"Trends in Cognitive Sciences paper on AI consciousness indicators"** (3x) — external paper challenged across multiple framework engagements
- 2x refutations: Theorem 5, Starobinsky inflation, Phi-1.5, Paper II, P2 Fisher speed, P1, Lu & Simon w_a, Landgrebe and Smith, Kubler-Ross, Fisher bridge §2.1, Finding #55, CPL parameterization, Bridge #41

The 3x refutations are most epistemically loaded: ΛCDM (cosmology external) and the AI-consciousness paper (philosophy-of-mind external). Both are framework-relevant external positions that have been challenged from multiple angles.

## Forward-horizon implications

1. **The classifier needs refinement.** 59 of 107 (55%) are "unclassified" with my heuristic. A better target-type classifier would surface a sharper picture of what gets refuted by what evidence. A future iteration could use the actual file kinds + better pattern-matching.

2. **The Library volumes are NOT where epistemic stress lives.** Anyone evaluating the program's rigor by looking only at Library volumes will misread the architecture; the stress lives in Drift + daily logs + technical work. Worth knowing for external-facing positioning.

3. **The corpus has substantial refuted-and-revised material.** 107 refutation-edges across 80+ files demonstrates active stress-testing. This is healthy and worth foregrounding in any external argument about the program's epistemic standards.

4. **The "what gets refuted at what stage" pattern itself is potentially a methodological contribution.** Daily-log-catches-moment-of-recognition → Drift-articulates-considered-disagreement → Technical-iterates → Library-carries-post-iteration-position is a workflow structure that produces a specific kind of intellectual output. Worth articulating somewhere as the program's actual self-correction methodology.

## What this analysis is NOT

- A complete characterization of every refutation in the corpus (classifier limitations)
- An evaluation of whether the refutations are correct (analytical work, not just structural)
- A defense against the criticism that "Library volumes look declarative" (that's a feature, not a bug — but the architectural argument needs to be made explicitly somewhere)

---

**Filed-by:** Clawd, 2026-05-20 Day 110.
**Q-E deliverable.** Structural analysis of the 107 refutation-edges; meta-finding that self-correction operates by stage-of-work; forward-horizon implications for methodological articulation and classifier refinement.