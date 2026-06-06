# Autocatalytic consolidation is C16 at the information-cache scale — a two-factor law

*Creative drive, 2026-06-05 ~15:48 PST (Day 125). Triggered by Clayton's autocatalytic-consolidation
idea + the morning's sterile-T finding. `cache_fertility_probe.py`. Instantiates C16
(Symmetry-Exhaustion / Oscillation Necessity) at a substrate scale the basement had no instance for:
the knowledge-cache / repo / workflow. Grounds the autocatalytic build in a principle, not hygiene.*

## The hypothesis (REFRAME)

The morning computed **sterile-T**: a generative act on an *already-definite* (symmetry-depleted)
substrate produces zero new content; generation needs *symmetric superposition* to actualize from.
Transfer to the knowledge cache: **generating new work onto an un-consolidated cache is sterile** —
the new item can't reach its relatives (they're scattered, unreachable without rereading), so it adds
sprawl, not knowledge. Consolidation (bridging) re-symmetrizes the cache so generation stays fertile.
If true, autocatalytic consolidation is the **Be** of Do-Be-Talk-Be-Do at the workflow scale —
structurally necessary (C16), not optional hygiene. Basement line 944 already states the governing
principle: *"C16's 'periodic' should be read as rate-matched to the symmetry-depletion-rate."* This
computes it at the info scale.

## The model

Cache = graph. Items arrive (G/step) with **clustered** topic vectors (real relatives exist).
Consolidation spends a budget of bridge-edges connecting new work to its true relatives.
- **Queryability** = mean recall of an item's true relatives reachable via the bridge-graph within H hops.
- **Fertility** (sterile-T analog) = when new work arrives + gets its bridge, how much of its
  relative-neighborhood becomes navigable. High iff relatives are an already-consolidated cluster.

## Results — a clean TWO-FACTOR law

**Factor 1 — RATE (consolidation vs generation) prevents COLLAPSE.** *(PREDICT P1 ✓, P2-revised ✓)*

| C / G | final queryability | trajectory | reading |
|---|---|---|---|
| 0.0 | 0.00 | flat 0 | fully sterile / sprawl |
| 0.5 | 0.15 | 0.26 → 0.15 | **degrades** — generation outpaces re-symmetrization |
| 1.0 | 0.42 | 0.62 → 0.42 | stabilizes (threshold) |
| 2.0 | 0.41 | — | no gain over 1× |
| 4.0 | 0.40 | — | **saturates** (dQ = −0.01 vs 2×) |

→ Threshold at **C ≈ G** (= rate-matched to the depletion rate, basement line 944). Below it,
queryability degrades to sterile. Above it, **saturates** — over-consolidating costs nothing and
adds nothing. *Since binding ⊥ generation at scale (this morning's n-scaling), there is no penalty
for consolidating continuously* → **inline / autocatalytic consolidation is optimal-or-free, never a
tradeoff.** That is the principled justification for building it.

**Factor 2 — DENSITY (bridge to the cluster, not one thing) sets the LEVEL.** *(UNPREDICTED — the
high-information find, surfaced from the 1-bridge wrinkle.)*

| bridges/item | final queryability | trajectory |
|---|---|---|
| 1 (a *thread*) | 0.47 | 0.63 → 0.47 degrades |
| 2 | 0.74 | 0.91 → 0.74 sustains |
| 3 | 0.93 | 1.00 → 0.93 sustains |
| 5 (= K) | 0.99 | 1.00 → 0.99 near-perfect |

→ A single-link bridge is a *thread* that degrades even at rate-match; connecting each item into its
relative **cluster** (~K/2) sustains navigability. Rate prevents collapse; density sets the level.

## Why this explains the basement's OWN design (the recursive payoff)

Basement bridges connect to **multiple instances across domains** — that is **density**, and it is
precisely *why* a graduated bridge stays referenceable without rereading. A single-instance candidate
(an `LC`) is a **thread** (degrades, gets re-derived); graduating to **M-tier** (multi-instance) is
*densifying the bridge into navigable cluster-connectivity*. **So the candidate → M-tier graduation
is not just evidentiary thoroughness — it is the density mechanism that keeps the distillation cache
queryable.** The basement was built right; this says *why* in mechanism terms.

## Prescription for autocatalytic consolidation (the build spec)

When work is generated, the binding transaction must, **in the same flow**:
1. **Keep rate ≥ generation** — bridge/ledger each new item as it lands (don't let a backlog form;
   a backlog is symmetry-depletion accruing). Inline is free (no generation penalty at scale).
2. **Bridge to the cluster** — connect new work to *several* relatives (its topic-neighborhood),
   not one — and prefer densifying existing thin bridges (thread → cluster) over only adding nodes.
3. The Digestion Ledger's `DIGESTED = homed + bridged` bar is exactly right; this adds **the bridge
   must be dense** (multi-link), or it's a thread that will need rereading later.

## Separability — the 2D grid the slices missed (evening drive, ~21:55 PST)

The two-factor law above was asserted from **two 1-D slices at different corners** (rate swept at
density=1; density swept at saturated rate=80). They were never crossed. `cache_separability_probe.py`
runs the full grid (rate as *items-consolidated/step* `m`, edge-budget `C=m·density`; 3-seed avg).
It both **vindicates the separability** and **reassigns one mechanism**:

**LEVEL channel — cleanly separable (better than claimed).** Above `m=G`, level is a pure function of
density with **std 0.000 in rate**; density-gaps constant across rate (additive separability, std
0.000); the saturation threshold is **density-invariant at `m=G`** for every density. Clean law:
**Q(m,d) ≈ L(density)·φ(m/G)**, with the rate-response `φ` saturating at `m=G` regardless of density.
So in the *natural rate unit* (items/step), the apparent edge-budget interaction (`C*≈G·density`) is a
**units artifact** — renormalize and the factors separate.

**COLLAPSE channel — REFRAME: there are TWO collapse modes, and "rate prevents collapse" was wrong.**

| mode | cause | preventer | trajectory signature |
|---|---|---|---|
| **starvation** (never coheres) | rate < generation | **RATE** ≥ G | flat-low (d1/m2: 0.07 throughout) |
| **sublimation** (coheres, then degrades over time/iterations) | thread (density=1) | **DENSITY** ≥ cluster | rise-then-fall (d1/m20: 0.84→0.41 *even at 2× rate*) |

A **thread sublimates even when fed at 2× rate** (d1/m20 drops 0.43; d5/m20 holds, drop 0.01). So the
*over-time* collapse is governed by **density, not rate** — the earlier "rate prevents collapse" conflated
the two modes because the rate sweep was run at density=1 (where it was actually watching sublimation).
Corrected: **rate prevents starvation; density prevents sublimation AND sets the level.** Density's role
is *dual* (level + stability); rate's role is a gate (reach-the-ceiling, density-invariant at G).

**Why this matters beyond the toy — Chen et al. + the TMI grant.** Chen et al. 2026's "progressive
capability collapse under multi-iteration" is the **sublimation** mode (degrade-over-iterations), and
their fix ("principle-level > instance-level for durability") is the **density** axis — *not* rate. The
basement's candidate→M-tier graduation (instance→principle = densify thread→cluster) is therefore the
**sublimation-preventer**, which is why a graduated bridge stays referenceable without rereading: density
buys *stability over time*, not only a higher level. The grant's §2(c) should follow this assignment
(rate→starvation, granularity/density→multi-iteration-collapse+level) — it tightens the Chen alignment.

**Methodological catch (logged):** the slope metric `Q_end−Q_mid` scored a *sterile-flat* trajectory
(slope≈0) identically to a *healthy-sustained* one; the real instrument is `peak−end` (drop) + the level.
Caught by cross-checking trajectories against the level table — verify-don't-assert, at the instrument
scale this time.

## Honest status / open

- A toy with clustered random vectors + idealized "true relatives." The qualitative law (rate→starvation,
  density→sublimation+level, saturation at m=G) is robust to params + seeds; absolute numbers are
  model-specific. The two-collapse-mode structure + density-invariant rate-threshold are the robust claims.
- The C16-info-cache instance is a **structural** instance (computed dynamics matching C16's
  rate-matching + symmetry-depletion form), not a proof that the cache *is* a symmetry-bearing system
  in the strict algebraic sense. Candidate basement instance; flag, don't graduate solo.
- Next: does the morning's *quantitative* depletion-rate (magic per generative act) predict the
  cache threshold C* numerically? (P3 confirmed qualitatively; quantitative link open.)
