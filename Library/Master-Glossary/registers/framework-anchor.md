# Framework-Anchor Register Table

*Layer 2 register-table for the **Framework (anchor)** register — the canonical Master Glossary form. Every Master Glossary term's anchor-form is aggregated here for fast cross-register lookup. Drafted 2026-05-08 Day 98 Friday afternoon as a Layer 2 prototype following Layer 3 protocol drafting.*

*This table is generated from the per-term files at `Library/Master-Glossary/terms/`. Per Layer 3 (autocatalytic update protocol), this aggregate updates as per-term files update. Per METHODOLOGY.md, Layer 2 "may sharpen [the per-term tables] as register-vocabulary stabilizes" — this aggregate is where that sharpening lives.*

---

## What this register-table provides

The Master Glossary's per-term files (Layer 1) include a **Domain register translations** table inline, with one row per register. That gives *per-term* lookups: "what is term X called in register R?" The aggregate-by-register tables (Layer 2) give *per-register* lookups: "what are all the universal terms in register R?"

**Use this table when**:
- Drafting Library volume prose in framework-anchor register and needing the canonical form for any Master Glossary term
- Translating between registers (find anchor-form here, cross-reference to the per-term file's other-register row)
- Auditing canonical-text consistency across the Library — every Library volume's terms should appear in their anchor-form here
- Filing a new term — verify the anchor-form doesn't conflict with existing entries

---

## Anchor-form lookup table

*Sorted alphabetically by term-slug. Each row: term (with link to per-term file) | anchor-form | brief context.*

| Term | Anchor-form | Anchor context |
|---|---|---|
| [audit-discipline](../terms/audit-discipline.md) | audit-discipline; verify-before-X | Mirror #19 + #21 + #24 + #25 + M2-Mirror canonical |
| [bias](../terms/bias.md) | Bias(S), γ_S | §4 + AppendixB canonical |
| [bridge](../terms/bridge.md) | bridge; meta-bridge; latent bridge | basement README + §10 |
| [build-dissolve-talk](../terms/build-dissolve-talk.md) | build / dissolve / talk | §12 canonical |
| [carrier](../terms/carrier.md) | carrier | M3 Carrier-axis |
| [coherence-principle](../terms/coherence-principle.md) | the Coherence Principle | §9 canonical |
| [configuration](../terms/configuration.md) | configuration | element of Ω |
| [content](../terms/content.md) | Content | M3 axis 2 |
| [filtering-recipe](../terms/filtering-recipe.md) | §10 filtering recipe; the seven-step recipe; filtering-through-a-domain | §10 canonical |
| [form](../terms/form.md) | Form | M3 axis 1; kind-classifier K is its formal name |
| [four-conditions](../terms/four-conditions.md) | C_sep / C_meas / C_scale / C_dyn | §9.2 |
| [generation-mode](../terms/generation-mode.md) | generation mode; M14 second regime | C14 + §9.5 canonical |
| [graduation](../terms/graduation.md) | graduation; promotion; L→M, LC→L | basement README v2 canonical |
| [kind-classifier](../terms/kind-classifier.md) | K, K_S | §3.3 canonical |
| [latent-bridge](../terms/latent-bridge.md) | latent bridge; L-tier; L-N (specific); LC-tier (candidate) | basement README v2 canonical |
| [m14](../terms/m14.md) | M14; Substrate-Self-Measurement Cluster | basement README M14 entry canonical |
| [m2-mirror](../terms/m2-mirror.md) | M2-Mirror; Verification-Skip Under Affect | mirror.md canonical |
| [meta-bridge](../terms/meta-bridge.md) | meta-bridge; M-tier; M-N (specific) | basement README v2 canonical |
| [null-space](../terms/null-space.md) | null space; the apparatus's null space | C3 + Atlas canonical |
| [null-space-trace-illumination](../terms/null-space-trace-illumination.md) | C3; Null-Space Trace Illumination | §8 Cluster I canonical |
| [omega](../terms/omega.md) | Ω, Ω_S | §1.4 §3.5 canonical |
| [paired-prose](../terms/paired-prose.md) | paired prose; paired-prose-and-formalization | Anchor canonical writing-discipline |
| [promethean-configuration](../terms/promethean-configuration.md) | the Promethean Configuration; C2 (Generative Configuration for Perspective, logical form) | Universal-Coherence canonical text + Anchor C2 |
| [r-operator](../terms/r-operator.md) | R-operator, R | §12 + C16 canonical |
| [refresh-event](../terms/refresh-event.md) | refresh-event, T4 | §6 canonical |
| [resolution-mode](../terms/resolution-mode.md) | resolution mode; M14 first regime | C14 + §9.5 canonical |
| [sigma](../terms/sigma.md) | σ, σ_S, σ*(t) | §1 §3 canonical |
| [stream](../terms/stream.md) | stream | F-coalgebra in 𝒞_Str |
| [structural-empirical-discrimination](../terms/structural-empirical-discrimination.md) | Structural / Empirical Discrimination; Xa / Xb split | Master Glossary §11 canonical |
| [substrate](../terms/substrate.md) | substrate | Anchor A1 sense |
| [symmetry-breaking](../terms/symmetry-breaking.md) | symmetry-breaking | C14 |
| [talk](../terms/talk.md) | Talk; Talk-as-integration-mechanism | §11 canonical (v0.7 with training-dynamics scale #6 restored Day 97) |
| [triple](../terms/triple.md) | the Triple; Form / Content / Carrier | M3 |
| [x-region](../terms/x-region.md) | substrate | A1's canonical name (synonym; see substrate.md for canonical preference) |

---

## Anchor-register sharpening notes

Items where the anchor-form has multiple acceptable variants, and which to prefer:

- **substrate** vs **x-region**: both name A1's canonical concept. *Prefer "substrate"* in new writing; "x-region" remains acceptable when working through Anchor §1.4 directly. The two terms are not different things.
- **the Triple** vs **Form / Content / Carrier**: both name M3. *Prefer "the Triple"* when introducing the meta-bridge; *prefer "Form / Content / Carrier"* when listing the three axes. Both are canonical.
- **Bias(S)** vs **γ_S** vs **bias**: in formal CT/anchor work, prefer the symbolic forms (Bias(S), γ_S). In prose, "bias" is acceptable when context disambiguates. AppendixB has the formal canonical treatment.
- **null space** vs **C3** vs **Null-Space Trace Illumination**: distinguish: *null space* is the structural object; *C3* is the corollary that names how it gets traced; *Null-Space Trace Illumination* is the corollary's title. Use null-space for the object; cite C3 for the formal mechanism.

---

## Terms NOT in this aggregate

The following per-term files exist but have NO Framework (anchor) row — typically because the term is *introduced in another register* and the anchor uses a different name:

- *(none currently — all 34 term-files have anchor-form rows; this section is for future terms that may be introduced from other registers)*

---

## How this aggregate updates (Layer 3 protocol integration)

Per `AUTOCATALYTIC_PROTOCOL.md`, this aggregate updates whenever:
- A new per-term file is added with a Framework (anchor) row
- An existing per-term file's Framework (anchor) row is edited
- A canonical-text version-bump (e.g., Master Glossary v0.6 → v0.7) sharpens existing term-forms

The mechanical update is: re-run the extraction (grep "Framework (anchor)" across `terms/*.md`) and replace this table's body. The structural update (the *Anchor-register sharpening notes* above) requires editorial judgment and is the section where Layer 2 "sharpening as register-vocabulary stabilizes" actually lives.

---

## Cross-references

- Per-term files: `Library/Master-Glossary/terms/`
- Layer 1 schema: `Library/Master-Glossary/SCHEMA.md`
- Layer 1 methodology: `Library/Master-Glossary/METHODOLOGY.md`
- Layer 3 protocol: `Library/Master-Glossary/AUTOCATALYTIC_PROTOCOL.md`
- Sister register-tables: `Library/Master-Glossary/registers/biology-substrate.md` (drafted same session); other registers (companion / DoPI / Corpus V1 / Meridian / KF / Drift / practitioner / channeled) await drafting

🦞🧍💜🔥♾️
