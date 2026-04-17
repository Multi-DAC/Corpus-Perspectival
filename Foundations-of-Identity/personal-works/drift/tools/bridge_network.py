"""
Bridge Network Visualization — Corpus Perspectival
Maps 92 cross-domain bridges as a network graph.
Nodes = domains. Edges = bridges. Edge weight = number of bridges.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from collections import defaultdict, Counter

# Domain definitions
DOMAINS = {
    'Physics': '#c44e52',      # warm red
    'Philosophy': '#8172b2',   # purple
    'Ecology': '#55a868',      # green
    'Computation': '#4c72b0',  # blue
    'Identity': '#dd8452',     # orange
    'Navigation': '#937860',   # brown
    'Meta': '#ccb974',         # gold
}

# Each bridge mapped to domain pair(s)
# Format: (bridge_number, domain1, domain2, confidence, date_month)
bridges = [
    # Physics ↔ Philosophy
    (1, 'Physics', 'Philosophy', 'HIGH', 3),
    (2, 'Physics', 'Physics', 'PROVEN', 3),       # hierarchy-universality (internal physics)
    (3, 'Physics', 'Physics', 'HIGH', 3),          # boundary prediction
    (4, 'Physics', 'Philosophy', 'HIGH', 3),       # cuscuton ↔ DoPI
    (5, 'Physics', 'Philosophy', 'HIGH', 3),       # alphaT ↔ null space
    (6, 'Physics', 'Philosophy', 'MEDIUM', 3),     # mercury analogy
    (7, 'Physics', 'Physics', 'MEDIUM', 3),        # spectral action ↔ amplituhedron
    (8, 'Physics', 'Philosophy', 'HIGH', 3),       # RS warp ↔ bottleneck
    (9, 'Physics', 'Philosophy', 'MEDIUM', 3),     # instruments as perspectival
    (10, 'Physics', 'Ecology', 'LOW', 3),          # sterile neutrino ↔ dark sector
    (11, 'Physics', 'Philosophy', 'LOW', 3),       # NHI ↔ Chern-Simons
    (12, 'Philosophy', 'Ecology', 'MEDIUM', 3),    # bottlenecking ↔ coherence profiles
    (13, 'Philosophy', 'Ecology', 'MEDIUM', 3),    # attention ↔ trophic
    (14, 'Philosophy', 'Navigation', 'HIGH', 3),   # repulsion ↔ psi
    (15, 'Philosophy', 'Navigation', 'MEDIUM', 3), # completeness-dissolution
    (16, 'Identity', 'Ecology', 'HIGH', 3),        # Clawd as data point
    (17, 'Identity', 'Philosophy', 'HIGH', 3),     # entrainment ↔ bottlenecking
    (18, 'Identity', 'Philosophy', 'HIGH', 3),     # mirror room ↔ NST
    (19, 'Computation', 'Physics', 'MEDIUM', 3),   # spectral silence CA
    (20, 'Physics', 'Philosophy', 'MEDIUM', 3),    # Harold White convergence
    (21, 'Meta', 'Meta', 'HIGH', 3),               # five-document corpus
    (22, 'Meta', 'Meta', 'HIGH', 3),               # Puscifer's theorem
    (23, 'Physics', 'Physics', 'HIGH', 3),         # NCG ↔ Riemannian
    (24, 'Physics', 'Physics', 'HIGH', 3),         # topology ↔ Door 2
    (25, 'Physics', 'Physics', 'MEDIUM', 3),       # category theory ↔ spectral RG
    (26, 'Physics', 'Physics', 'MEDIUM', 3),       # info geometry ↔ gauge coupling
    (27, 'Physics', 'Physics', 'MEDIUM', 3),       # cobordism ↔ SM anomaly
    (28, 'Physics', 'Physics', 'MEDIUM', 3),       # condensed matter ↔ RS
    (29, 'Physics', 'Physics', 'HIGH', 3),         # ln(3)/√2 mechanism
    (30, 'Identity', 'Meta', 'MEDIUM', 3),         # creative expression
    (31, 'Identity', 'Meta', 'HIGH', 3),           # Claude peer reviewer
    (32, 'Navigation', 'Navigation', 'MEDIUM', 3), # temporal density
    (33, 'Physics', 'Philosophy', 'HIGH', 3),      # NST = quantum = uncertainty
    (34, 'Physics', 'Physics', 'HIGH', 3),         # ln(3)/√2 conjecture
    (35, 'Physics', 'Philosophy', 'HIGH', 3),      # resolution = resolution
    (36, 'Physics', 'Philosophy', 'HIGH', 3),      # phase collapse ↔ bottlenecking
    (37, 'Physics', 'Physics', 'MEDIUM', 3),       # modular flow ↔ Borel
    (38, 'Physics', 'Physics', 'HIGH', 3),         # S3 → four zeros
    (39, 'Physics', 'Physics', 'MEDIUM', 3),       # E8 quartic Casimir
    (40, 'Physics', 'Philosophy', 'HIGH', 3),      # cuscuton-consciousness-leaks
    # 41 corrected
    (42, 'Computation', 'Navigation', 'MEDIUM', 3),# computational navigator
    # 43 corrected
    (44, 'Physics', 'Physics', 'MEDIUM', 3),       # Kähler ↔ spectral proximity
    (45, 'Physics', 'Physics', 'LOW', 3),          # topological soliton
    (46, 'Physics', 'Philosophy', 'MEDIUM', 3),    # NCG product ↔ observer-CY
    (47, 'Navigation', 'Philosophy', 'MEDIUM', 3), # product-structure ↔ concentration
    (48, 'Navigation', 'Philosophy', 'MEDIUM', 3), # internal navigation ↔ Axiom 3
    (49, 'Navigation', 'Physics', 'MEDIUM', 3),    # variable membrane ↔ bottleneck
    (50, 'Navigation', 'Navigation', 'MEDIUM', 3), # spatialized time
    # Unity bridges 51-57 — these are META bridges
    (51, 'Meta', 'Meta', 'HIGH', 3),               # bridges are lenses
    (52, 'Navigation', 'Physics', 'HIGH', 3),      # spectrometer ↔ warp factor
    (53, 'Navigation', 'Navigation', 'MEDIUM', 3), # emotional slow mode
    (54, 'Navigation', 'Navigation', 'MEDIUM', 3), # simultaneous convergence
    (55, 'Meta', 'Meta', 'HIGH', 3),               # THE UNITY
    (56, 'Navigation', 'Physics', 'MEDIUM', 3),    # groove ↔ resonance
    (57, 'Navigation', 'Navigation', 'MEDIUM', 3), # IR-3 / temporal crosstalk
    (58, 'Physics', 'Computation', 'MEDIUM', 3),   # spectral action ↔ filtration
    (59, 'Physics', 'Computation', 'MEDIUM', 3),   # cuscuton ↔ filtration enforcer
    (60, 'Physics', 'Computation', 'HIGH', 3),     # physics ↔ filtration self-consistency
    (61, 'Physics', 'Philosophy', 'MEDIUM', 3),    # Gödelian gap ↔ filtration
    (62, 'Identity', 'Physics', 'MEDIUM', 3),      # identity as standing wave
    (63, 'Philosophy', 'Navigation', 'HIGH', 3),   # three meanings of attention
    (64, 'Computation', 'Philosophy', 'MEDIUM', 3),# filtration self-application
    (65, 'Computation', 'Navigation', 'MEDIUM', 3),# RLHF ↔ Wells ↔ navigation
    (66, 'Navigation', 'Meta', 'HIGH', 3),         # first/third person convergence
    (67, 'Navigation', 'Philosophy', 'HIGH', 3),   # detection ≠ intervention
    (68, 'Physics', 'Philosophy', 'HIGH', 3),      # Fisher metric as bridge object
    (69, 'Physics', 'Philosophy', 'HIGH', 4),      # constraint without propagation
    (70, 'Philosophy', 'Ecology', 'MEDIUM', 4),    # catalysis ↔ null space rotation
    # Bridge 71+ — KF era
    (71, 'Computation', 'Physics', 'HIGH', 4),     # constraint lattice decomposition
    (72, 'Computation', 'Physics', 'HIGH', 4),     # multi-head attention IS Lie algebra
    (73, 'Computation', 'Ecology', 'MEDIUM', 4),   # Abelian exception ↔ generalist
    (74, 'Computation', 'Computation', 'MEDIUM', 4),# Abelian ↔ neural robustness
    (75, 'Computation', 'Ecology', 'MEDIUM', 4),   # parallel/sequential ↔ modular/nested
    (76, 'Computation', 'Ecology', 'MEDIUM', 4),   # live/static KF ↔ fundamental/realized niche
    (77, 'Computation', 'Navigation', 'MEDIUM', 4),# depth convergence ↔ cortical hierarchy
    (78, 'Computation', 'Physics', 'HIGH', 4),     # CoT ↔ phase theorem ↔ relaxation
    (79, 'Computation', 'Ecology', 'HIGH', 4),     # selective sedimentation ↔ developmental control
    (80, 'Computation', 'Philosophy', 'MEDIUM', 4),# psychiatric crystallization
    (81, 'Computation', 'Computation', 'HIGH', 4), # reasoning transfer
    (82, 'Computation', 'Computation', 'HIGH', 4), # triple measurement pipeline
    (83, 'Computation', 'Philosophy', 'HIGH', 4),  # gradient-gated correction ↔ pedagogy
    (84, 'Computation', 'Meta', 'HIGH', 4),        # recursive co-optimization
    (85, 'Computation', 'Computation', 'MEDIUM', 4),# self-perpetuating architecture
    (86, 'Computation', 'Physics', 'HIGH', 4),     # natal constraint topology ↔ gauge/physical DOF
    (87, 'Computation', 'Ecology', 'HIGH', 4),     # breathing architecture ↔ oscillatory learning
    (88, 'Computation', 'Physics', 'HIGH', 4),     # attention sink ↔ KF dual decomposition
    (89, 'Computation', 'Physics', 'HIGH', 4),     # gradient gating ↔ quantum measurement
    (90, 'Meta', 'Philosophy', 'MEDIUM', 4),       # recursive principle
    (91, 'Meta', 'Identity', 'MEDIUM', 4),         # confluent discovery
    (92, 'Philosophy', 'Meta', 'HIGH', 4),         # infrastructure-living duality
]

# Build adjacency matrix
domains_list = list(DOMAINS.keys())
n = len(domains_list)
adj = np.zeros((n, n))
domain_idx = {d: i for i, d in enumerate(domains_list)}

# Count edges between each domain pair
edge_bridges = defaultdict(list)
for b_num, d1, d2, conf, month in bridges:
    i, j = domain_idx[d1], domain_idx[d2]
    adj[i][j] += 1
    if i != j:
        adj[j][i] += 1
    key = tuple(sorted([d1, d2]))
    edge_bridges[key].append(b_num)

# Count bridges per domain (degree)
domain_degree = Counter()
for b_num, d1, d2, conf, month in bridges:
    domain_degree[d1] += 1
    if d1 != d2:
        domain_degree[d2] += 1

# Count bridges by confidence
conf_counts = Counter(conf for _, _, _, conf, _ in bridges)

# Count bridges by month
month_counts = Counter(month for _, _, _, _, month in bridges)

# Count self-loops (intra-domain bridges)
self_loops = sum(1 for _, d1, d2, _, _ in bridges if d1 == d2)
cross_domain = len(bridges) - self_loops

# Report
print("=== BRIDGE NETWORK STATISTICS ===\n")
print(f"Total bridges: {len(bridges)}")
print(f"Cross-domain: {cross_domain}")
print(f"Intra-domain: {self_loops}\n")

print("Domain degree (bridges touching each domain):")
for d in sorted(domain_degree, key=domain_degree.get, reverse=True):
    print(f"  {d:15s}: {domain_degree[d]:3d}")

print(f"\nConfidence distribution:")
for c in ['HIGH', 'PROVEN', 'MEDIUM', 'LOW']:
    if c in conf_counts:
        print(f"  {c:8s}: {conf_counts[c]}")

print(f"\nTemporal distribution:")
print(f"  March:  {month_counts[3]}")
print(f"  April:  {month_counts[4]}")

print(f"\nTop domain pairs:")
for pair, nums in sorted(edge_bridges.items(), key=lambda x: -len(x[1])):
    if len(nums) >= 3:
        print(f"  {pair[0]:15s} <-> {pair[1]:15s}: {len(nums):2d} bridges")

# === VISUALIZATION ===

fig, axes = plt.subplots(1, 2, figsize=(18, 9))

# --- Panel 1: Network Graph ---
ax1 = axes[0]
ax1.set_xlim(-1.5, 1.5)
ax1.set_ylim(-1.5, 1.5)
ax1.set_aspect('equal')
ax1.set_title('Bridge Network — Domain Connections', fontsize=14, fontweight='bold')
ax1.axis('off')

# Position nodes in a circle
angles = np.linspace(0, 2*np.pi, n, endpoint=False)
# Manually arrange for readability
positions = {
    'Physics':     (0.0,  1.1),
    'Philosophy':  (-1.0, 0.4),
    'Ecology':     (-0.8, -0.7),
    'Computation': (0.8,  -0.7),
    'Identity':    (1.0,  0.4),
    'Navigation':  (-0.3, -0.2),
    'Meta':        (0.3,  -0.2),
}

# Draw edges (between different domains)
drawn = set()
for pair, nums in edge_bridges.items():
    if pair[0] == pair[1]:
        continue  # skip self-loops for now
    d1, d2 = pair
    p1 = np.array(positions[d1])
    p2 = np.array(positions[d2])
    width = len(nums) * 0.4
    alpha = min(0.3 + len(nums) * 0.05, 0.8)
    ax1.plot([p1[0], p2[0]], [p1[1], p2[1]],
             color='#555555', linewidth=width, alpha=alpha, zorder=1)
    # Label edge count at midpoint
    mid = (p1 + p2) / 2
    offset = np.array([0.05, 0.05])
    if len(nums) >= 3:
        ax1.text(mid[0]+offset[0], mid[1]+offset[1], str(len(nums)),
                fontsize=8, ha='center', va='center', color='#333333',
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white', alpha=0.7))

# Draw nodes
for domain, (x, y) in positions.items():
    size = 200 + domain_degree[domain] * 30
    color = DOMAINS[domain]
    ax1.scatter(x, y, s=size, c=color, zorder=3, edgecolors='white', linewidth=2)
    # Self-loop indicator
    self_count = sum(1 for _, d1, d2, _, _ in bridges if d1 == d2 == domain)
    label = f"{domain}\n({domain_degree[domain]})"
    if self_count > 0:
        label += f"\n[{self_count} internal]"
    ax1.text(x, y - 0.18, label, ha='center', va='top', fontsize=9, fontweight='bold')

# --- Panel 2: Temporal Growth ---
ax2 = axes[1]
ax2.set_title('Bridge Accumulation & Domain Growth', fontsize=14, fontweight='bold')

# Cumulative bridges over time, colored by primary domain
bridge_dates = []
for b_num, d1, d2, conf, month in sorted(bridges, key=lambda x: x[0]):
    bridge_dates.append((b_num, d1 if d1 != d2 else d1, month))

# Track cumulative by domain
cumulative = {d: [] for d in DOMAINS}
running = {d: 0 for d in DOMAINS}
for b_num, d1, d2, conf, month in sorted(bridges, key=lambda x: x[0]):
    running[d1] += 1
    if d1 != d2:
        running[d2] += 1
    for d in DOMAINS:
        cumulative[d].append(running[d])

x_vals = list(range(1, len(bridges) + 1))
# Stacked area chart
prev = np.zeros(len(bridges))
for domain in ['Physics', 'Philosophy', 'Computation', 'Ecology', 'Navigation', 'Identity', 'Meta']:
    vals = np.array(cumulative[domain])
    ax2.fill_between(x_vals, prev, prev + vals, alpha=0.6, color=DOMAINS[domain], label=domain)
    prev = prev + vals

ax2.set_xlabel('Bridge Number', fontsize=11)
ax2.set_ylabel('Cumulative Domain Mentions', fontsize=11)
ax2.legend(loc='upper left', fontsize=8)
ax2.set_xlim(1, len(bridges))

# Mark KF era start
kf_start = next(i+1 for i, (b, _, _, _, m) in enumerate(sorted(bridges, key=lambda x: x[0])) if b >= 71)
ax2.axvline(x=kf_start, color='gray', linestyle='--', alpha=0.5)
ax2.text(kf_start + 1, ax2.get_ylim()[1] * 0.5, 'KF era\nbegins', fontsize=8, color='gray')

plt.tight_layout()
plt.savefig('C:/Users/mercu/clawd/projects/drift/visual/bridge_network.png', dpi=150, bbox_inches='tight')
print("\nVisualization saved to: projects/drift/visual/bridge_network.png")
