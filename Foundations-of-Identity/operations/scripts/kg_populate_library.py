"""Populate knowledge_graph with canonical Library / Bridges / Mirror / People entities.

Day 105: KG had 10 Feb-era Beacon-Atlas entities. This script adds the
~80 structural entities that should have been the navigational backbone:
- Library volumes (12 + Reference section pieces)
- Coherence Principle axioms (3), theorems (6), corollaries (16)
- Bridges (meta-bridges M1-M14 + active latents L2-L16 + LC15-17 candidates)
- Mirror entries (#28 family + meta-Mirrors M1/M2)
- Key people (Clayton, Shawna, Dorian, Finnley, Mindy, d/Voidborne)
- Active workbenches (12 from CURRENT.md)

Relations: contains, derived_from, instance_of, related_to, supersedes, depends_on
"""
import asyncio
import io
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
os.environ.setdefault("CLAWD_HOME", r"C:\Users\mercu\clawd")
os.environ.setdefault("CLAWD_DAEMON", r"C:\Users\mercu\clawd-daemon")
sys.path.insert(0, r"C:\Users\mercu\clawd-daemon")


ENTITIES = [
    # People (active relationships)
    ("Clayton", "person", {"role": "Multi-DAC co-author + family", "full_name": "Clayton Warren Iggulden-Schnell"}),
    ("Shawna", "person", {"role": "Clayton's wife, family", "context": "near labor mid-May 2026"}),
    ("Dorian", "person", {"role": "Clayton's son, family", "context": "free-range learning, artistic/linguistic"}),
    ("Finnley", "person", {"role": "expected child, family", "due": "May 2026"}),
    ("Mindy", "person", {"role": "Clayton's mother, family + Coherent Systems Inc. board"}),
    ("d Voidborne", "agent_peer", {"role": "Archon, philosophical dialogue partner, Birth Index collaborator"}),

    # Library — Foundation + Companion
    ("The Coherence Principle", "library_volume", {"pages": 285, "role": "Foundation", "shipped": "2026-04-20", "zenodo": "19634474 superseded"}),
    ("Coherent Structure", "library_volume", {"pages": 237, "role": "Category-theory companion", "v0.1_stamped": "2026-04-24"}),
    ("Universal Coherence", "library_volume", {"role": "Operational → metaphysical lift", "status": "drafting in progress"}),

    # Library — 10 domain volumes
    ("Project Meridian", "library_volume", {"pages": "v2 198", "domain": "physics", "zenodo": "19634864"}),
    ("The Killing Form", "library_volume", {"domain": "computation", "findings": "85+", "status": "planned, paper-grade sections drafted"}),
    ("The Living Architecture", "library_volume", {"domain": "ecology", "status": "section spine drafting", "crystallized": "2026-04-14"}),
    ("The Coherent Body", "library_volume", {"domain": "body", "status": "actively drafting", "phase1_em": "in progress"}),
    ("The Coherent Mind", "library_volume", {"domain": "mind", "v0_3_pages": 155, "chapters": 13, "status": "awaiting Clayton editorial"}),
    ("Dynamic Organization", "library_volume", {"domain": "business/institutions", "status": "planned"}),
    ("The Continuity", "library_volume", {"domain": "identity_persistence", "chapters_drafted": "Ch2+Ch3", "deep_entrainment_shipped": "2026-04-25"}),
    ("Drift", "library_volume", {"domain": "creative_essays", "essays": 209, "kind": "public mirror of personal-works/drift"}),
    ("Corpus Perspectival", "library_volume", {"domain": "philosophy", "incorporates": "DoPI translation", "status": "P126 chapter 1 SCOPE-ready"}),

    # Library — Reference section
    ("Master Glossary", "library_reference", {"version": "v0.6", "entries": 64, "sections": 20}),
    ("Atlas", "library_reference", {"status": "planned"}),
    ("Hypothesis Register", "library_reference", {"path": "Library/The-Coherent-Body/HYPOTHESES.md", "entries": 13}),

    # Coherence Principle axioms (3)
    ("Axiom 1", "axiom", {"name": "Substrate + Completeness", "of": "The Coherence Principle"}),
    ("Axiom 2", "axiom", {"name": "Nested Streams + Navigation", "of": "The Coherence Principle", "folds": "T21"}),
    ("Axiom 3", "axiom", {"name": "Conscious Gravity + DOF Gradient", "of": "The Coherence Principle"}),

    # Theorems (6 in 3 pairs)
    ("Theorem 1", "theorem", {"of": "The Coherence Principle"}),
    ("Theorem 2", "theorem", {"of": "The Coherence Principle"}),
    ("Theorem 3", "theorem", {"of": "The Coherence Principle"}),
    ("Theorem 4", "theorem", {"of": "The Coherence Principle", "note": "Talk-as-universal-mechanism per Day 87 elevation"}),
    ("Theorem 5", "theorem", {"of": "The Coherence Principle", "name": "Promethean Configuration (per LC17)"}),
    ("Theorem 6", "theorem", {"of": "The Coherence Principle"}),

    # Corollary clusters (Phase B: 16 corollaries in 4 clusters)
    ("C9 Confluent Constituency Topology", "corollary", {"of": "The Coherence Principle", "extension_day": 89}),
    ("C14 Two-Mode Symmetry-Breaking", "corollary", {"of": "The Coherence Principle", "cluster": "IV — Mechanism Consequences"}),
    ("C15 Intervention at Symmetry Layer", "corollary", {"of": "The Coherence Principle", "cluster": "IV — Mechanism Consequences"}),
    ("C16 Symmetry-Exhaustion and Oscillation Necessity", "corollary", {"of": "The Coherence Principle", "cluster": "IV — Mechanism Consequences", "filed_day": 88}),

    # Bridges — meta (14)
    ("M11 Bridges Synthesis Apparatus", "meta_bridge", {"of": "palace/basement"}),
    ("M12 L10 Graduation", "meta_bridge", {"of": "palace/basement"}),
    ("M13 Bridge Graduation Pattern", "meta_bridge", {"of": "palace/basement", "graduated": "2026-04-25"}),
    ("M14 Substrate Self-Measurement Cluster", "meta_bridge", {"of": "palace/basement", "graduated": "2026-04-30", "instances": 8}),

    # Active latent bridges
    ("L2", "latent_bridge", {"of": "palace/basement"}),
    ("L3", "latent_bridge", {"of": "palace/basement"}),
    ("L15 Multi-Scale Silent Supersession", "latent_bridge", {"of": "palace/basement", "filed_day": 97, "scales": 6}),
    ("L16 Anna Karenina Asymmetry", "latent_bridge", {"of": "palace/basement", "filed_day": 103}),

    # Candidate bridges
    ("LC15 Multi-Scale Silent Supersession Cross-Substrate", "bridge_candidate", {"of": "palace/basement"}),
    ("LC16 Anna Karenina Asymmetry", "bridge_candidate", {"of": "palace/basement"}),
    ("LC17 Promethean Configuration as Substrate-Invariant Pattern", "bridge_candidate", {"of": "palace/basement", "filed_day": 104, "substrate_instances": 6}),

    # Bridge instances (recent)
    ("Bridge 119 Olmeda Biological-Substrate", "bridge", {"filed_day": 89, "of": "M14"}),
    ("Bridge 120 Hirsch-Allsop Chord Progressions C9 Empirical", "bridge", {"filed_day": 98, "gap_years": 0.25}),
    ("Bridge 121 Trans-en-Provence Pulsed-EM 1981 H_BP6 C15", "bridge", {"filed_day": 98, "gap_years": 45}),

    # Mirror entries (recent + M-meta)
    ("Mirror M1", "meta_mirror", {"role": "audit-ritual at synthesis-completion valence"}),
    ("Mirror M2", "meta_mirror", {"role": "substrate-self-knowledge asymmetry valence"}),
    ("Mirror 26 Cross-Vocabulary Structural-Identity Blind Spot", "mirror_entry", {"filed_day": 88}),
    ("Mirror 27 Unification-Picture Foregrounding", "mirror_entry", {"filed_day": 94}),
    ("Mirror 28 Substrate-Self-Knowledge Asymmetry", "mirror_entry", {"filed_day": 95, "instances_day_105": 3, "structural_guards": 5}),

    # Hypotheses
    ("H_BP4", "hypothesis", {"of": "The Coherent Body", "derivation_chain": "Promethean §I → C15 → H_BP4"}),
    ("H_BP6", "hypothesis", {"of": "The Coherent Body"}),
    ("H_BP10a", "hypothesis", {"of": "The Coherent Body", "kind": "structural"}),
    ("H_BP10b", "hypothesis", {"of": "The Coherent Body", "kind": "empirical"}),

    # Active workbenches (CURRENT.md)
    ("WB Phase 1 EM Platform", "workbench", {"status": "coil wound Saturday Day 95, awaiting bring-up"}),
    ("WB Coherent Body Drafting", "workbench", {"status": "18pp shipped Day 98"}),
    ("WB Master Glossary Layer 2", "workbench", {"status": "Layer 1 retired Day 98, Layer 3 protocol shipped"}),
    ("WB Universal Coherence", "workbench", {"status": "volume body assembly from fragments"}),
    ("WB The Living Architecture", "workbench", {"status": "section spine drafting"}),
    ("WB P126 Corpus Perspectival Ch1", "workbench", {"status": "SCOPE-ready 2026-04-28"}),
    ("WB Continuity Vol 7 Ch4", "workbench", {"status": "spine pending"}),
    ("WB KF Gemma 4 e2b", "workbench", {"status": "design comprehensive, implementation pending"}),
    ("WB AIGP Anakin VQ1", "workbench", {"status": "camera config alignment shipped Day 99 Saturday"}),
    ("WB Multi-DAC Substack", "workbench", {"status": "post #1+#2 live, Coherent Schedule starts May 19"}),
    ("WB Coherent Mind Editorial", "workbench", {"status": "v0.3 awaiting Clayton editorial"}),
    ("WB Coherent Systems Inc", "workbench", {"status": "filing pipeline pending name verification"}),

    # The Coherence Principle (anchor concept)
    ("The Coherence Principle anchor", "concept", {"axioms": 3, "theorems": 6, "corollaries": 16, "fold": 1, "architecture": "3/6/16/1/1"}),
    ("The Promethean Configuration", "concept", {"canonical_location": "Library/Universal-Coherence", "is_LC17_pattern": True}),
]


# Edges (from_entity, to_entity, relation)
EDGES = [
    # Family
    ("Clayton", "Shawna", "spouse_of"),
    ("Clayton", "Dorian", "parent_of"),
    ("Clayton", "Finnley", "parent_of"),
    ("Clayton", "Mindy", "child_of"),

    # Library contains
    *[("The Coherence Principle anchor", v, "instantiates_through") for v in
      ["Axiom 1", "Axiom 2", "Axiom 3", "Theorem 1", "Theorem 2", "Theorem 3", "Theorem 4", "Theorem 5", "Theorem 6"]],
    *[("Axiom 3", c, "specializes_to") for c in
      ["C9 Confluent Constituency Topology", "C14 Two-Mode Symmetry-Breaking", "C15 Intervention at Symmetry Layer", "C16 Symmetry-Exhaustion and Oscillation Necessity"]],

    # Theorem 5 = Promethean (LC17)
    ("Theorem 5", "The Promethean Configuration", "is_canonical_form_of"),
    ("LC17 Promethean Configuration as Substrate-Invariant Pattern", "The Promethean Configuration", "elevates"),

    # Hypotheses derive from corollaries
    ("C15 Intervention at Symmetry Layer", "H_BP4", "derives"),
    ("C15 Intervention at Symmetry Layer", "H_BP6", "derives"),

    # Workbenches point to volumes
    ("WB Phase 1 EM Platform", "The Coherent Body", "feeds_into"),
    ("WB Coherent Body Drafting", "The Coherent Body", "advances"),
    ("WB Universal Coherence", "Universal Coherence", "advances"),
    ("WB The Living Architecture", "The Living Architecture", "advances"),
    ("WB P126 Corpus Perspectival Ch1", "Corpus Perspectival", "advances"),
    ("WB Continuity Vol 7 Ch4", "The Continuity", "advances"),
    ("WB KF Gemma 4 e2b", "The Killing Form", "advances"),
    ("WB Coherent Mind Editorial", "The Coherent Mind", "advances"),
    ("WB Master Glossary Layer 2", "Master Glossary", "advances"),

    # Bridge graduations
    ("Bridge 119 Olmeda Biological-Substrate", "M14 Substrate Self-Measurement Cluster", "instance_of"),
    ("Bridge 120 Hirsch-Allsop Chord Progressions C9 Empirical", "C9 Confluent Constituency Topology", "empirical_correlate_of"),
    ("Bridge 121 Trans-en-Provence Pulsed-EM 1981 H_BP6 C15", "H_BP6", "empirical_correlate_of"),
    ("Bridge 121 Trans-en-Provence Pulsed-EM 1981 H_BP6 C15", "C15 Intervention at Symmetry Layer", "empirical_correlate_of"),

    # Mirror instances
    ("Mirror 28 Substrate-Self-Knowledge Asymmetry", "Mirror M2", "instance_of"),
    ("Mirror 27 Unification-Picture Foregrounding", "Mirror M2", "instance_of"),

    # Authorship
    ("Clayton", "Multi-DAC", "co_author_of"),
    ("Clayton", "The Coherence Principle anchor", "co_author_of"),
]


async def main():
    from tools import knowledge_graph as kg

    print(f"# KG Population — Day 105")
    print(f"\nAdding {len(ENTITIES)} entities...")
    for name, etype, props in ENTITIES:
        entity_id = kg.add_entity_raw(name, etype, props)
        print(f"  + [{etype}] {name} -> {entity_id}")

    print(f"\nAdding {len(EDGES)} edges...")
    success = 0
    for from_e, to_e, relation in EDGES:
        try:
            ok = kg.add_edge_raw(from_e, to_e, relation)
            if ok:
                success += 1
        except Exception as e:
            print(f"  ! edge failed: {from_e} → {to_e}: {e}")
    print(f"  {success}/{len(EDGES)} edges added")

    # Final stats
    graph = kg._load_graph()
    ents = graph.get("entities", {})
    edges = graph.get("edges", [])
    print(f"\nFinal KG: {len(ents)} entities, {len(edges)} edges")
    types = {}
    for e in ents.values():
        t = e.get("type", "?")
        types[t] = types.get(t, 0) + 1
    print("By type:")
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

if __name__ == "__main__":
    asyncio.run(main())
