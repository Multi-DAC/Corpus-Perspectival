"""Is autocatalytic consolidation a PRINCIPLE (C16 at the info-cache scale), or hygiene?

Cache-as-graph: items (work/findings) arrive with clustered topic vectors (real relatives exist).
Consolidation spends a budget of bridge-edges connecting new work to its true relatives.
  - QUERYABILITY = can a query reach its relevant items via the bridge-graph (recall within H hops).
  - FERTILITY (the sterile-T analog) = when new work arrives + gets its 1 bridge, how much of its
    relative-neighborhood becomes navigable? High iff relatives are already a consolidated cluster
    (symmetric/superposed); low iff scattered (definite/depleted) -> the new work is STERILE.

Sweep consolidation rate C vs generation rate G.
PREDICT: P1 C<G -> queryability+fertility DEGRADE over time (generation outpaces re-symmetrization);
P2 threshold at C~G (not a delicate optimum); C>G saturates (binding-perp-generation at scale: more
consolidation costs nothing) -> justifies inline/autocatalytic consolidation.
"""
import numpy as np
import networkx as nx

rng = np.random.default_rng(0)
D, M, K, H = 16, 12, 5, 3          # dim, topic-clusters, #true-relatives, hop-horizon
G, T = 10, 40                       # generation rate (new items/step), steps -> 400 items
centers = rng.normal(size=(M, D))
centers /= np.linalg.norm(centers, axis=1, keepdims=True)


def topic_vec():
    c = centers[rng.integers(M)]
    v = c + 0.6 * rng.normal(size=D)
    return v / np.linalg.norm(v)


def run(C, dens=1):
    """C = consolidation budget (bridge-edges)/step; dens = relatives bridged per item.
    Returns (queryability_traj, fertility_traj)."""
    B = nx.Graph()
    vecs = []                       # topic vectors by node id
    consolidated = set()            # nodes that have >=1 bridge
    q_traj, f_traj = [], []

    def true_relatives(i, upto):
        # K nearest existing nodes (id < upto) by cosine
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
        # --- generation: add G new items ---
        new_nodes = []
        for _ in range(G):
            i = len(vecs)
            vecs.append(topic_vec())
            B.add_node(i)
            new_nodes.append(i)
        V = np.array(vecs)
        # measure FERTILITY of this step's new work: give each new node its 1 best relative-bridge,
        # then how much of its relative-neighborhood is navigable (sterile-T analog)
        fert = []
        for i in new_nodes:
            rel = true_relatives(i, i)             # relatives among pre-existing nodes
            if not rel:
                continue
            best = rel[0]                          # connect to nearest relative (1 bridge)
            B.add_edge(i, best)
            fert.append(reach_recall(i, rel))
            B.remove_edge(i, best)                 # probe only; real consolidation is budgeted below
        f_traj.append(np.mean(fert) if fert else 0.0)

        # --- consolidation: spend C bridge-edges on the unconsolidated backlog (newest first) ---
        backlog = [n for n in B.nodes if n not in consolidated]
        backlog.sort(reverse=True)
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

        # --- queryability: mean relative-recall via the bridge-graph over sampled queries ---
        qn = rng.choice(len(vecs), size=min(60, len(vecs)), replace=False)
        q_traj.append(np.mean([reach_recall(i, true_relatives(i, len(vecs))) for i in qn]))
    return q_traj, f_traj


print(f"cache-fertility probe  (G={G}/step, T={T} -> {G*T} items, K={K} relatives, H={H} hops)\n")
print(f"{'C (consol/step)':>16} {'C/G':>5} {'final queryability':>19} {'final fertility':>16} {'verdict'}")
results = {}
for C in (0, 5, 10, 20, 40):
    q, f = run(C)
    results[C] = (q, f)
    qf, ff = q[-1], f[-1]
    v = "STERILE/sprawl" if qf < 0.2 else ("sustained" if qf > 0.6 else "degrading")
    print(f"{C:>16} {C/G:>5.1f} {qf:>19.2f} {ff:>16.2f}  {v}")

# trajectory shape: does C<G DEGRADE over time while C>=G holds?
print("\nqueryability trajectory (start -> mid -> end):")
for C in (0, 5, 10, 20, 40):
    q = results[C][0]
    print(f"  C/G={C/G:.1f}:  {q[2]:.2f} -> {q[T//2]:.2f} -> {q[-1]:.2f}")

# threshold: smallest C sustaining queryability > 0.6
thr = next((C for C in (0,5,10,20,40) if results[C][0][-1] > 0.6), None)
print(f"\nfertility threshold (sustains queryability>0.6): C={thr}  (C/G={thr/G if thr else None})")
print("saturation check: does C=40 (4x) beat C=20 (2x) much?  "
      f"dQ={results[40][0][-1]-results[20][0][-1]:+.3f}")

# --- DENSITY experiment: fix backlog-clearing budget, sweep bridges-per-item (cluster vs thread) ---
print("\n=== density sweep (budget=80/step clears backlog; vary bridges-per-item) ===")
print(f"{'dens (rel/item)':>16} {'final queryability':>19} {'start->end':>14}")
for dens in (1, 2, 3, 5):
    q, f = run(80, dens=dens)
    print(f"{dens:>16} {q[-1]:>19.2f} {q[2]:.2f}->{q[-1]:.2f}  "
          f"{'SUSTAINS' if q[-1] > 0.7 else ('holds' if q[-1] > 0.55 else 'degrades')}")
print("\n-> rate (C>=G) prevents COLLAPSE; density (bridge to the cluster) sets the LEVEL.")
