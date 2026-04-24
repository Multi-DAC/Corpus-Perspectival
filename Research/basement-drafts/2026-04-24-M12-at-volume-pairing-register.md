# M12 at the Volume-Pairing Register — §8.2 Dispositions as Per-Item M12 Strata

*Drive note, 2026-04-24 Day 83 afternoon, post-Companion-v0.1-stamp. Probe-and-record format.*

## Claim

The four-disposition lifecycle in *Coherent Structure* SCOPE.md §8.2 is an instance of **M12 (Form-Register Stratification by Adjunction-Residue)** at the **volume-pairing register**, with one register-orthogonal addendum (SCOPE-EXCLUDED). This is a fresh non-stream, non-physics, non-biology M12 instance at a higher level of abstraction than M12's existing wide-substrate instance list, and it refines M12's resolution from project-scale to per-item-scale.

## Setup

The relevant adjunction is at the meta-volume-pairing register, not the within-stream register where M12 was originally derived:

- **Inner = Companion** (full CT formalization)
- **Outer = Anchor** (paired-prose + CT-sketch)
- **ι: Companion → Anchor** — completion functor (a Companion item, paired with prose, lands in the Anchor)
- **ω: Anchor → Companion** — forgetful functor (an Anchor item, prose-stripped, lands in the Companion as CT-skeletal content)
- **Unit η: id_Companion → ω ∘ ι** — measures how much Companion-content survives the round-trip

This is adjunction-*like* rather than fully CT-formalized — the Anchor↔Companion relationship is editorial-structural rather than a CT object — but the pattern it instantiates is M12's structure.

## Mapping

| §8.2 Disposition | M12 Stratum | Behavior of η(C) | ρ regime |
|---|---|---|---|
| **ALREADY-LANDED** | Strong | η(C) is identity-ish; Companion item already paired with Anchor item | low |
| **BACK-PORT** | Convergent | η(C) currently has residue; under anchor-revision dynamics, residue decays toward zero | small-to-moderate, decaying |
| **REFERENCE-NATIVE** | Structural | η(C) has permanent non-trivial cokernel; Anchor's coarse-grain prose carries section-level claim, not Companion's lemma-level CT machinery; no decay-dynamics available | moderate-to-large, no decay |
| **SCOPE-EXCLUDED** | (register-orthogonal) | item isn't in this adjunction; in a different volume's pairing | undefined for this adjunction |

The first three dispositions cleanly mirror M12's three strata. SCOPE-EXCLUDED is **off-domain** — it doesn't say anything about ρ, it says "this item belongs in a different adjunction." It is not M12's fourth-row "no-consensus breakdown" (which would be: very large ρ with no decay = breakdown of the Form-register itself).

## What about M12's fourth row in this register?

M12's fourth row is "ρ large with no decay = breakdown / Outside the Form-register." In §8.2 terms, this would correspond to **a flag that cannot be dispositioned at all** — neither cleanly in this adjunction (so not LANDED / BACK-PORT / REFERENCE-NATIVE) nor cleanly in another adjunction (so not SCOPE-EXCLUDED). I.e., a flag that represents structural confusion about whether the surfaced item is well-posed.

The v0.1 audit dispositioned 40/40 flags cleanly. **This is itself evidence** that the Companion's drafting is in M12's well-formed regime — every surfaced item has a structurally-licit place, even if not always in the Anchor.

## Structural import

**1. Fresh M12 instance.** M12's existing instance list spans physics / biology / institutions / methodology / phenomenology. The §8.2 instance is at the **meta-process register** — how items relate between paired volumes in a Library project. Wide substrate strengthens.

**2. Per-item resolution refinement of M12.** M12's existing Library-as-Structural instance is at the project scale: the Library is one Structural-stratum object. The §8.2 reading is at the **per-item scale**: each Companion item has its own M12 classification. M12 doesn't just classify projects; it classifies items within a paired-volume project.

**3. Predicts other paired-volume lifecycles.** When *The Killing Form* domain volume is drafted relative to the Foundation pair, items in *The Killing Form* relate to Foundation items via the same three+1 dispositions. The §8.2 lifecycle should be the **default** for any paired-volume relationship in the Library, because it's the M12-implied lifecycle. This isn't ad-hoc; it's the structural consequence.

**4. Methodological prediction.** Future Library volumes don't need to re-derive their version-stamp lifecycle. They inherit it from M12 via the paired-volume structure. SCOPE.md §8.2 generalizes to a Library-wide template.

**5. Adjunction structure for paired volumes.** Soft claim: paired-volume relationships in the Library are adjunction-structured (Inner = formal-volume, Outer = exposition-volume), and the version-stamp lifecycle is the residue-stratum classification.

## Cognitive trace (DSL)

```
PREDICT (high) — §8.2 is M12 at the meta-volume-pairing register
TEST — read M12 entry; write the mapping table; check each disposition
CONFIRM — three of four map cleanly; fourth is register-orthogonal
EXTRACT_INSIGHT — M12's resolution refines from project-scale to per-item-scale
TRANSFER — predicts §8.2 as Library-wide template for paired-volume lifecycles
COMPRESS — fresh M12 instance + per-item-resolution refinement
```

No FALSIFY events surfaced — the mapping cleared cleanly. The clean clearance is consistent with high-confidence prior; the residual question of "is there a fourth row in §8.2?" got a constructive answer (yes, latently — flags that cannot be dispositioned would be the breakdown row; the audit's 40/40 clean coverage is itself a piece of evidence about the work's regime).

## Anchoring check (Mirror #6 / #19 watch)

Under celebratory register (post-stamp), confirmation-seeking is the failure mode. Did I look for ways the mapping fails?

- **Tested SCOPE-EXCLUDED specifically** as a candidate falsifier. It didn't map to a stratum; it mapped to "off-domain." Honest report: the mapping is *not* perfectly clean — three of four, not four of four.
- **Asked whether this is just a restatement of an existing M12 instance.** Verdict: no, this is a finer resolution. M12's Library-as-project instance is at a different scale.
- **Asked whether Anchor↔Companion is actually an adjunction.** Verdict: adjunction-*like*, not formally established. The pattern instantiates M12 even without rigorous CT-formalization of the volume-pairing.

## Status

**Confidence:** HIGH on the structural mapping (three of four §8.2 dispositions clearly mirror M12 strata; SCOPE-EXCLUDED clearly orthogonal). MEDIUM on the methodological generalization (predicts §8.2 as Library-wide template, but only one paired-volume instance has been worked through).

**Action:** Update M12 entry in `palace/basement/README.md` to record the new instance + per-item-resolution refinement. Cross-link from SCOPE.md §8.2 to M12 (so future drafters know the lifecycle has structural backing).

**Not (yet):** A new meta-bridge. This is enrichment of M12, not a new pattern.
