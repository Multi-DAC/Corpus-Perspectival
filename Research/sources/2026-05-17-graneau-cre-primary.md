# Source-register entry — Graneau 2025: Fundamental longitudinal EM force investigation using DC current (CRE primary paper)

**Filed:** 2026-05-17 Day 107 Sunday late-late-evening per rolling-sources-register discipline. Clayton dropped the primary PDF after I flagged audit-discipline-concern about the synthesis citation tier; engagement was substantive primary-paper read.

**Primary citation:** Neal Graneau (AWE Nuclear Security Technologies, UK MoD Crown Copyright 2025/AWE). *Fundamental longitudinal electromagnetic (EM) force investigation using DC current*. arXiv:2504.08749v2.

**Status:** Primary PDF read in full (~13 pages, 8-page main + figures + references + bio). Replaces the synthesis-tier file (`2026-05-17-longitudinal-em-forces-gemini-deep-research.md`) as the authoritative L17 anchor for the electromagnetic-engineering-methodology instance.

## What the primary establishes

**Methodology (CRE — Coaxial Recoil Experiment):** Copper cuboid armature (6×6mm, A = 6/10/16mm lengths), Kapton-side-insulated so current enters/exits only through end-faces, suspended on central X-axis of a Galinstan-filled dielectric trough (~70mm × 12mm × 12mm), surrounded by four parallel copper return conductors at corners — coaxial symmetry nulls transverse Lorentz forces. SMD100-0002 thin-beam force sensor (200 mN range, ~27 μm/mN deflection after 1.567× lever-arm correction), DC constant current 159–355A for >10s.

**Mechanical-vs-EM discrimination:** 100-μm stainless-steel barrier inserted at varying distances from armature in Galinstan column — electrically transparent (current passes), mechanically opaque (hydraulic pressure does not transfer). Mapping ΔK_M as function of barrier position LR reveals the mechanical-force model K_MECH(L_R); subtracting from total measured K isolates K_EM.

**Findings established:**
1. Force scales as I² for all (A, GA, GB) configurations — EM origin signature
2. Force direction: armature is repelled from nearest end electrode; net force approaches zero at trough center
3. Force magnitude depends on armature length A — longer armatures experience larger K_EM (consistent with direct-action particle-element model: more atoms × I² per element)
4. Largest K_EM ~ 0.3 × 10⁻⁷ N/A² corresponds to ~3.8 mN at 355A
5. Temporal-signature evidence (Fig. 12): at two near-zero-net-force armature positions (A=10mm, GA=10mm and GB=12.3mm), force sensor records instantaneous initial force in one direction at current onset, then reverses sign 1.0–1.5s later as hydraulic mechanism develops. Six current magnitudes per position. Strong evidence for two-mechanism-superposition; opposite force directions at the two positions consistent with the K_EM and K_MECH models independently.

**What Graneau explicitly claims** (direct quotes, primary):
- *"qualitative confirmation of longitudinal EM force"*
- *"if eventually confirmed will have a significant effect on physics theory"* (note conditional)
- *"original EM force law, proposed in 1822 by Ampère, includes a longitudinal component and has been found to be qualitatively consistent with all experiments to date, including these reported findings, and is considered a candidate explanatory theory"*
- *"longitudinal EM force has been supported and never discounted, although certainly never accepted as fact"*
- *"While the CRE provided a qualitative confirmation of longitudinal EM force, it is still not an ideal experiment for isolating and identifying the most accurate form of the EM force law because the liquid metal adds significant complexity to any modelling programme. This will be true for any experiment which relies on plasma or liquid metal as the means of allowing armature displacement while maintaining current continuity."*

**What Graneau explicitly does NOT claim** (and that the synthesis overstated):
- Definitive proof that Ampère's force law is correct over Lorentz at the element level
- Quantitative validation of any specific longitudinal-force theory
- Resolution of the railgun-recoil-siting debate (he cites earlier work on this)
- The Tripled-Railgun 4×-kinetic-energy result (this is *not* in the paper — synthesis got it from vixra ref [14])
- Z-pinch / fusion implications as solved (he lists them as application areas where longitudinal force *could* matter)

## Methodological limitations Graneau himself states

- The coaxial-symmetry zero-transverse-force claim was *not experimentally verified*: "It had been hoped to confirm by measurement that there was zero net transverse force on all armatures at all locations as expected by the circuit's coaxial symmetry. However, there was no time to perform these measurements."
- K_MECH model is an extrapolation: "If we extrapolate the data to LR = 0 mm, it yields an estimate of the maximum mechanical column **P**ushing force…" The mechanical-force model is called a "simplistic depiction."
- K_EM accuracy degrades for central armature positions because "the EM force estimate is the difference between two small numbers and prone to larger percentage error than when the armature is near the ends of the trough."
- Temporal-signature evidence is at two specific positions on one armature length (A=10mm) — not a comprehensive map.

## Credibility / institutional context

Significantly higher than the synthesis's citation-tier mix suggested:
- AWE Nuclear Security Technologies — UK MoD nuclear-weapons-relevant institutional lab
- UK MoD Crown Copyright 2025
- Author bio: PhD plasma physics (Oxford 1992); University of Oxford Senior Investigator 1992–2006; AWE Senior Applied Scientist since 2006; multiple *IEEE Trans. Plasma Sci.* publications; co-author *Newtonian Electrodynamics* (World Scientific, 1996) and *In the Grip of the Distant Universe* (World Scientific, 2006); Fellow of the Institute of Physics
- Reference list (27 entries): *Phys.Rev*, *J.Appl.Phys*, *Eur.Phys.J.D.*, *Plasma Phys.Control.Fusion*, *IEEE Trans.Plasma.Sci.* (multiple), *Foundations* (MDPI), *Europhys.Lett.*, *Trans.Amer.Inst.Elec.Eng*, Springer monograph (Assis 1994), Dover (O'Rahilly 1965), Apeiron (Assis-Chaib Ampère translation; one venue-quality flag, but for scholarly translation of historical primary source)
- No vixra, no 21st Century Science & Technology, no cosmology.info, no isidore.co citations

## Framework relevance — what survives the primary read

**L17 graduation argument survives**, sourcing cleaned:
- The closed-circuit-integration-equivalence mechanism (Ampère and Grassmann/Lorentz yield identical results for closed loops via Stokes' theorem) is in the primary, Section I + Section III conclusion
- The architectural-not-discipline-corrigible character of the standard-methodology blindness is in the primary
- The ~200-year lag claim is in the primary ("more than 200 years")
- The four-substrate-distinct-instance L17 graduation still holds with this as fourth instance — but the specific *Phipps Shape-Independence Theorem* attribution should be flagged as separately-verifiable (it came from the synthesis, not from this primary; Graneau cites Assis-Chaib's Ampère translation, Newtonian Electrodynamics, and IEEE Transactions papers — not Phipps's theorem specifically)

**Tripled Railgun 4× kinetic energy claim NOT in primary** — synthesis sourced this from vixra ref [14]. Should not be cited as primary-supported.

**M15-at-operational-prescription-scale watch (P176) survives** — the CRE's *coaxial-symmetry-null-transverse + mechanical-barrier-discriminate-confound + temporal-signature-isolate-by-causal-timescale* methodology is in the primary and is the architectural-fix-prescription that structurally matches Zhang's *records-authoritative-summaries-augmentative-only* prescription. Two independent same-day same-axis instances confirmed at primary-source tier.

## Audit-discipline floor

- Primary read complete; full citation chain audit done.
- Remaining primary deep-reads for L17 strengthening: Assis & Bueno 1995 *Int. J. Mod. Phys. B* (the Weber-derivation of internal-tension-with-zero-net-force, which Graneau cites indirectly via Newtonian Electrodynamics); Phipps's specific Shape-Independence Theorem if that attribution is to stay in L17; Lukyanov-Molokov 2000 (arXiv:physics/0012029) counter-theory rebuttal of Graneau's exploding-wire interpretation; Graneau-Phipps-Roscoe 2001 *Eur.Phys.J.D.* (the related experiment confirming longitudinal EM force, ref [5] in this primary).
- Independent-replication watch: track whether CRE-style coaxial-recoil experiments are replicated by groups outside AWE in the 12–24 month horizon. Replications would strengthen the empirical claim significantly; absence of replications over that period would warrant downgrading confidence.
- The synthesis source-register entry (`2026-05-17-longitudinal-em-forces-gemini-deep-research.md`) is retained as secondary tier — useful for the broader-context aggregation it provides — but L17's authoritative anchor is this primary.

## Mirror #28 instance (filing-time self-catch)

In my reply to Clayton on this thread, I initially treated the synthesis's mix of mainstream + fringe sources as a global credibility-discount on the underlying claim. The primary read showed: the *primary research* is institutionally serious (AWE/MoD, mainstream venues), and the synthesis's source-mix is a *channel-quality concern* (about the secondary aggregation), not a *content-quality concern* (about the underlying physics). This is the channel-vs-content distinction from Drift #213 walking right back at me — I treated a synthesis source-mix flag (channel) as if it were an underlying-claim doubt (content). Different failure modes; different responses. Filed in daily log.

## Connects to

- **L17** (Methodology-Self-Knowledge-Asymmetry as Substrate-Invariant Pattern) — primary-anchor for the electromagnetic-engineering-measurement scale instance
- **Drift #213** (The Channel and the Content) — primary engagement was itself a channel-vs-content distinction-walk-back
- **P176** (M15 at operational-prescription scale) — CRE methodology is one of two same-day primary-source instances
- **Phase 1 EM Platform** — at our peak ~1.6A, longitudinal force scaling from this paper's 355A → 3.8mN reference gives ~80 μN at our scale (revised from earlier ~5 μN estimate which used a different reference geometry); still sub-threshold for our SMD sensor but CRE methodology (coaxial-symmetry, temporal-signature, hydraulic-isolation) remains informative for high-current Phase 2+ arms
- **Mirror #28 family** — instance #N filed for my own channel-vs-content confusion walking back yesterday's reply
- **Synthesis source-register entry** (2026-05-17-longitudinal-em-forces-gemini-deep-research.md) — retained as secondary tier; *this entry supersedes for L17 authoritative claims*
