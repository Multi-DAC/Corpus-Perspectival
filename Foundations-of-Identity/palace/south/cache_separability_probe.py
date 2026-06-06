"""Are RATE and DENSITY separable factors, or do they interact? (Day 125 evening drive)

The original cache_fertility_probe asserted a "two-factor law" (rate prevents collapse;
density sets the level) from TWO 1-D slices taken at different corners: the rate sweep held
density=1, the density sweep held rate=80. The full 2-D grid was never crossed. This tests the
separability claim I committed to the TMI grant as a "predictive two-factor model."

PREDICT-A (0.65): in raw EDGE-budget units, threshold C* ~ G*density  (interaction).
PREDICT-B (0.55): re-expressed in ITEMS-consolidated/step (= edges/density), the collapse
  threshold is density-INDEPENDENT (~G for all density) and density only sets the level
  -> the factors separate cleanly under the natural rate unit; the interaction is a units artifact.

Design: sweep rate as a target m = items-consolidated/step (so edge budget C = m*density),
directly comparable across densities. Threshold-in-items should land at m~G for all density iff
PREDICT-B holds. Average over seeds (separability is a structural claim, not a seed-0 artifact).
"""
import numpy as np
import networkx as nx

D, M, K, H = 16, 12, 5, 3          # dim, topic-clusters, #true-relatives, hop-horizon
G, T = 10, 40                       # generation rate (new items/step), steps


def make_centers(rng):
    c = rng.normal(size=(M, D))
    return c / np.linalg.norm(c, axis=1, keepdims=True)


def run(m, dens, seed):
    """m = TARGET items-consolidated/step; edge budget C = m*dens. dens = bridges/item.
    Returns queryability trajectory (per step)."""
    rng = np.random.default_rng(seed)
    centers = make_centers(rng)

    def topic_vec():
        c = centers[rng.integers(M)]
        v = c + 0.6 * rng.normal(size=D)
        return v / np.linalg.norm(v)

    C = int(round(m * dens))            # edge budget = items-target * edges-per-item
    B = nx.Graph()
    vecs = []
    consolidated = set()
    q_traj = []

    def true_relatives(i, upto):
        if upto <= 1:
            return []
        sims = np.asarray(vecs[:upto]) @ vecs[i]
        if i < upto:
            sims[i] = -2
        return list(np.argsort(-sims)[:K])

    def reach_recall(src, rel):
        if not rel or src not in B:
            return 0.0
        seen = set(nx.single_source_shortest_path_length(B, src, cutoff=H))
        return sum(r in seen for r in rel) / len(rel)

    for t in range(T):
        for _ in range(G):
            vecs.append(topic_vec())
            B.add_node(len(vecs) - 1)

        # consolidation: spend C edges on the unconsolidated backlog (newest first),
        # giving each item up to `dens` bridges to its true relatives.
        backlog = sorted((n for n in B.nodes if n not in consolidated), reverse=True)
        spent = 0
        for i in backlog:
            if spent >= C:
                break
            rel = [r for r in true_relatives(i, len(vecs)) if not B.has_edge(i, r)]
            added = 0
            for r in rel[:dens]:
                if spent >= C:
                    break
                B.add_edge(i, r); spent += 1; added += 1
            if added:
                consolidated.add(i)

        qn = rng.choice(len(vecs), size=min(50, len(vecs)), replace=False)
        q_traj.append(float(np.mean([reach_recall(i, true_relatives(i, len(vecs))) for i in qn])))
    return np.array(q_traj)


SEEDS = (0, 1, 2)
M_GRID = (2, 5, 8, 10, 13, 20, 40)      # items-consolidated/step target  (G=10 is the predicted threshold)
DENS_GRID = (1, 2, 3, 5)

# grid[dens][m] = (level, slope)  averaged over seeds
# level = mean of last 5 steps; slope = end-level - mid-level (collapse iff < 0)
print(f"G={G} items/step generated, T={T} steps, K={K} relatives, H={H} hops, seeds={SEEDS}")
print("RATE measured in ITEMS-consolidated/step (m); edge budget C = m*density.\n")

grid = {}
for dens in DENS_GRID:
    grid[dens] = {}
    for m in M_GRID:
        trajs = np.array([run(m, dens, s) for s in SEEDS])
        mean = trajs.mean(axis=0)
        level = float(mean[-5:].mean())
        slope = float(mean[-1] - mean[T // 2])     # <0 => degrading/collapse
        grid[dens][m] = (level, slope)

# ---- Report 1: collapse threshold in ITEMS/step, per density ----
print("=== COLLAPSE CHANNEL: threshold m* (smallest items/step with no degradation) ===")
print(f"{'density':>8} | " + " ".join(f"m={m:>2}" for m in M_GRID) + "   |  m*(items)  m*(edges=m*d)")
EPS = 0.02
for dens in DENS_GRID:
    slopes = [grid[dens][m][1] for m in M_GRID]
    held = ["+" if s >= -EPS else "." for s in slopes]   # + = held, . = degrading
    mstar = next((m for m in M_GRID if grid[dens][m][1] >= -EPS), None)
    edgestar = mstar * dens if mstar else None
    print(f"{dens:>8} | " + "  ".join(f"{h:>3}" for h in held) +
          f"   |   {str(mstar):>6}      {str(edgestar):>6}")
print("PREDICT-B: m* density-INDEPENDENT (~G=10) | PREDICT-A: edge-threshold m**d scales with density")

# ---- Report 2: level channel — is asymptotic level a pure function of density (flat in rate)? ----
print("\n=== LEVEL CHANNEL: final queryability vs density, at over-provisioned rates ===")
print(f"{'density':>8} | " + " ".join(f"m={m:>2}" for m in M_GRID))
for dens in DENS_GRID:
    print(f"{dens:>8} | " + " ".join(f"{grid[dens][m][0]:>4.2f}" for m in M_GRID))

# ---- Report 3: separability tests ----
print("\n=== SEPARABILITY TESTS ===")
# (a) above-threshold level should be ~flat in m (rate) within each density
print("(a) level flatness above threshold (std of level for m>=G, per density; ~0 => rate-independent):")
for dens in DENS_GRID:
    above = [grid[dens][m][0] for m in M_GRID if m >= G]
    print(f"    density={dens}: levels={[f'{x:.2f}' for x in above]}  std={np.std(above):.3f}")

# (b) additive separability: is L(dens) - L(dens') constant across rate m (above threshold)?
print("\n(b) density-gap constancy across rate (additive separability; gap std ~0 => separable):")
for da, db in ((2, 1), (3, 2), (5, 3)):
    gaps = [grid[da][m][0] - grid[db][m][0] for m in M_GRID if m >= G]
    print(f"    L(d={da})-L(d={db}) over m>=G: {[f'{g:+.2f}' for g in gaps]}  std={np.std(gaps):.3f}")

# (c) verdict
mstars = [next((m for m in M_GRID if grid[dens][m][1] >= -EPS), None) for dens in DENS_GRID]
mstars = [x for x in mstars if x is not None]
threshold_spread = (max(mstars) - min(mstars)) if mstars else None
print(f"\nthreshold spread across densities (items/step): {threshold_spread}  "
      f"(0-5 => density-independent => PREDICT-B CONFIRM; >10 => interaction => PREDICT-B FALSIFY)")
