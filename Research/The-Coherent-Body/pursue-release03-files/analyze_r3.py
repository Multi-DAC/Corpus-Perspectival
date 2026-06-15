"""analyze_r3.py — structure-vs-provenance test on PURSUE Release 03 (Day 134 creative drive).

PREDICT (med confidence): R3's phenomenological structure-classes (1-5, from R1's
unified-register taxonomy) recur ACROSS its agencies (CIA/FBI/DoW/NASA) and eras
(1949->2024), rather than clustering by provenance. Structure-invariance across a
provenance mix totally different from R1 (which was Navy/military mission reports) =
evidence for the 'shared structure, receiver-shaped content' reading. Provenance-
clustering would FALSIFY it.

Method: keyword feature extraction on the 52 extracted texts + catalog metadata, then
cross-tabulate structure-class x agency and x era. First pass — flagged for close read.
"""
import json, os, re, glob
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "release03-catalog.json")))
by_id = {str(d["id"]): d for d in cat}

# phenomenological-structure feature lexicon (maps to R1 taxonomy Classes 1-5 + transmedium)
FEAT = {
 "C1_diffuse_plasma": r"plasma|luminous|ball of light|glow|glowing|fiery|incandescen|orb of light|bright light",
 "C2a_round_spherical": r"spher|round|circular|\borb\b|\bball\b|football|oval|disc|disk|saucer",
 "C2b_diamond_triangle": r"triangl|diamond|delta|chevron|boomerang",
 "C2_cigar_cylinder": r"cigar|cylind|tic.?tac|capsule",
 "C3_channel_coupling": r"transparen|translucent|invisible|cloak|radar.{0,20}(no|not).{0,10}visual|visual.{0,20}(no|not).{0,10}radar",
 "C4_multiobject_lifecycle": r"split|separat|broke into|emitt|multiple object|formation|swarm|launch|spawn|cluster of",
 "C5_measured_kinematics": r"\bradar\b|altitude|knots|\bmach\b|coordinat|triangulat|measured|velocity|m/s|mph",
 "transmedium_USO": r"\bwater\b|submerg|underwater|ocean|\bsea\b|dove|transmedium|splash|beneath the surface|sonar|sonic",
 "motion_residual": r"right.angle|90.degree|instantaneous|motionless|hover|stationary|high.speed|sudden|accelerat|abrupt",
}

def era(d):
    s = f"{d.get('incidentDate','')} {d.get('title','')} {d.get('incidentLocation','')}"
    yrs = [int(y) for y in re.findall(r"(19[4-9]\d|20[0-2]\d)", s)]
    if not yrs: return "undated"
    y = min(yrs)
    return ("1940s-50s" if y<1960 else "1960s-70s" if y<1980 else
            "1980s-90s" if y<2000 else "2000s-10s" if y<2020 else "2020s")

rows = []
for d in cat:
    rid = str(d["id"]); ag = d.get("agency","?"); ty = d.get("type","?")
    p = os.path.join(HERE, "extracted-text", f"{rid}.txt")
    text = open(p, encoding="utf-8").read().lower() if os.path.exists(p) else ""
    feats = [k for k,rx in FEAT.items() if re.search(rx, text)]
    rows.append({"id":rid,"agency":ag,"type":ty,"era":era(d),
                 "title":d.get("title","")[:55],"has_text":bool(text),
                 "chars":len(text),"feats":feats})

# --- cross-tabs ---
struct_keys = ["C1_diffuse_plasma","C2a_round_spherical","C2b_diamond_triangle",
               "C2_cigar_cylinder","C3_channel_coupling","C4_multiobject_lifecycle","C5_measured_kinematics"]
print(f"R3 docs: {len(rows)}  (with text: {sum(r['has_text'] for r in rows)})\n")

print("=== STRUCTURE-FEATURE x AGENCY ===")
tab = defaultdict(Counter)
for r in rows:
    for f in r["feats"]:
        if f in struct_keys: tab[f][r["agency"]] += 1
for f in struct_keys:
    if tab[f]: print(f"  {f:24s}: {dict(tab[f])}")

print("\n=== STRUCTURE-FEATURE x ERA ===")
tab2 = defaultdict(Counter)
for r in rows:
    for f in r["feats"]:
        if f in struct_keys: tab2[f][r["era"]] += 1
for f in struct_keys:
    if tab2[f]: print(f"  {f:24s}: {dict(tab2[f])}")

print("\n=== transmedium / USO hits (R3 USO rumor test) ===")
for r in rows:
    if "transmedium_USO" in r["feats"]:
        print(f"  [{r['id']}] {r['agency']:18s} {r['era']:10s} {r['title']}")

print("\n=== per-doc feature table (structure features only) ===")
for r in sorted(rows, key=lambda x:(x["agency"],x["era"])):
    sf = [f.split("_")[0] for f in r["feats"] if f in struct_keys]
    flag = "" if r["has_text"] else " (no-text)"
    print(f"  [{r['id']}] {r['agency']:18s} {r['era']:10s} {','.join(sf) or '-':22s} {r['title']}{flag}")
