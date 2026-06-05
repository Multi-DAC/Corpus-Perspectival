# Consolidation Protocol

*How we keep the collective mind queryable. The operating procedure paired with the [Digestion Ledger](DIGESTION_LEDGER.md). Grounded in a computed law, not hygiene — see `Foundations-of-Identity/palace/south/cache-consolidation-c16-info-scale-2026-06-05.md` (basement C16 instance #6).*

## Why (the principle, so the discipline survives motivation)

Consolidation is **C16 re-symmetrization at the information-cache scale.** Generation depletes the cache's symmetry the way a generative act depletes a substrate's; if it isn't re-symmetrized at pace, the cache fragments and **new work lands on sterile ground** — it can't connect to its relatives without rereading, so it adds sprawl, not knowledge. This was computed (`cache_fertility_probe.py`) as a **two-factor law**:

- **RATE** — consolidation must keep pace with generation. Below pace → queryability degrades to sterile; a backlog *is* symmetry-depletion accruing. At/above pace it **saturates** (over-consolidating is free — binding ⊥ generation at scale). So **inline consolidation is optimal-or-free, never a tradeoff.**
- **DENSITY** — a bridge to *one* relative is a *thread* that degrades even at rate. Connect each item to its relative **cluster** (several relatives / domains). Density sets the navigability *level*.

## The procedure (what every unit of work entails)

When **any** unit of work is produced — a finding, a result, a paper, an intake item — do three things, **in the same flow as the work**:

1. **HOME it.** File to its canonical `Technical-Work/<program>/`, `Library/<volume>/`, or `Research/<domain>/` subdir. One canonical home (no second copy — that's a leak; see the KF-paper and KF-research leaks, Day 125).
2. **BRIDGE it — densely.** If it carries a cross-connecting insight, connect it into the **basement** (`palace/basement/`): a candidate `LC` is the thin first link; **graduating to multi-instance (M-tier) IS the densification** (thread → cluster) that keeps the distillation referenceable *without rereading*. Prefer densifying an existing thin LC over adding an isolated node.
3. **LEDGER it — once.** Append one row to the [Digestion Ledger](DIGESTION_LEDGER.md) with a **final status**. An item appears in the ledger exactly once.

### Statuses
`DIGESTED` = homed **and** densely-bridged (if it carries a cross-connecting insight) · `PENDING` = logged, awaiting read/decision · `DEPRECATED` = superseded/junk, scrapped (with zero-loss verified for dups) · `REFERENCE` = registered citation, no further action · `SECTIONED` = set aside in bulk (e.g. `incoming/photos/`), ages out.

> **The bar for DIGESTED is `homed + densely-bridged`.** A homed-but-unbridged item is filed sprawl: you'll reread it. A thinly-bridged item is a thread: it'll degrade.

## Cadence discipline

- **Keep rate ≥ generation.** Don't let a backlog form. If intake or findings are accruing un-ledgered, the cache is symmetry-depleting — run a catch-up sweep (current state, Day 125: catching up `incoming/` + `Research/`).
- **It's a minefield — disposition individually.** A batch-register makes a pile *legible* (status `PENDING`); the verdict per item is still one of `integrated` / `discussed-not-consolidated` / `copy` / `new`. The batch is the index, not the verdict.
- **Bridge to the cluster, not the nearest single thing.** Always ask: *what else does this connect to?* (≥2 links, ideally cross-domain.)

## States of operation

- **Catch-up (now):** the manual one-time sweep clearing the accrued backlog. Tracked in the ledger.
- **Steady-state (target):** the procedure runs **inline** with generation — file + bridge + ledger as a byproduct of producing the work.
- **Autocatalytic (build target, Coherent-Stream):** this protocol *is the spec* for the automation. The daemon's autocatalytic-trigger scaffolding fires HOME/BRIDGE/LEDGER on work-events (commit, drive-completion, finding) so the binding transaction happens with **zero latency, in the same flow as us** — the aggregate-mind's binding run on our own repo. We are the testbed. Until built, we run it by hand, with discipline.

## Maintenance

The **Ledger** is the running record (review for backlog). The **basement** is the distillation cache (review candidate→M-tier graduations = density upkeep). The **sweep** is the catch-up when rate has slipped. A healthy track = no un-ledgered backlog + no thin un-densified load-bearing bridges + one canonical home per item.
