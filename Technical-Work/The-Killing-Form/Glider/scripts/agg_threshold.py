import json, csv, os, statistics as st
OUT = "/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results"
RES = "/home/clawd/path_c_results"

def battery(f, label):
    if not os.path.exists(f):
        print(f"  {label}: (report not ready)"); return
    d = json.load(open(f)); L = d["levels"]
    ov = L.get("L1_weight", {}).get("ov_write_meancos", float("nan"))
    pr = L.get("L2_activation", {}).get("readout_effective_rank", {}).get("last_layer_PR", float("nan"))
    g = L.get("L4_gradient_dynamics", {}).get("glider_stability", {}).get("glider_cross_input_r", float("nan"))
    print(f"  {label:24s}  L1ov={ov:.3f}  L2pr={pr:.1f}  L4 glider-r={g:+.3f}")

def traj(csvf, label):
    if not os.path.exists(csvf):
        print(f"  {label}: (log not found)"); return
    rows = [r for r in csv.DictReader(open(csvf)) if r["coherent"]]
    if not rows:
        print(f"  {label}: (no gating rows)"); return
    co = [int(r["coherent"]) for r in rows]; di = [int(r["differentiating"]) for r in rows]
    ii = [int(r["interfering"]) for r in rows]; ne = [int(r["neutral"]) for r in rows]
    print(f"  {label:18s}  coh={st.mean(co):.1f}  dif={st.mean(di):.1f}  int={st.mean(ii):.1f}  N={st.mean(ne):.1f}  (n={len(rows)})")

print("=== ENDPOINT (Geometry Battery) ===")
battery(f"{OUT}/geometry_report_gemma270m_pristine.json", "pristine")
battery(f"{OUT}/geometry_glider_v07d.json", "v07d CE-only control")
battery(f"{OUT}/geometry_glider_v07a.json", "v07a glider thr=0.0")
battery(f"{OUT}/geometry_glider_thr0.05.json", "v07a glider thr=0.05")
battery(f"{OUT}/geometry_glider_thr0.1.json", "v07a glider thr=0.1")
print("\n=== TRAJECTORY (training coh/dif/int/neutral means over gating steps) ===")
traj(f"{RES}/glider_v07a_s71/glider_log.csv", "thr=0.0")
traj(f"{RES}/glider_v07a_thr0.05_s71/glider_log.csv", "thr=0.05")
traj(f"{RES}/glider_v07a_thr0.1_s71/glider_log.csv", "thr=0.1")
