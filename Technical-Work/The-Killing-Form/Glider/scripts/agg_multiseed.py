import json, os, statistics as st

OUT = "/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results"
seeds = [71, 137, 271, 314, 419]

def metrics(f):
    d = json.load(open(f))
    p = d["agg_pristine"]; t = d["agg_trained"]
    return {
        "sep_ratio": t["mean_separation"] / p["mean_separation"],
        "mean_sep_trained": t["mean_separation"],
        "cv_ratio": t["mean_cv"] / p["mean_cv"] if p["mean_cv"] else float("nan"),
    }

rows = {}
for s in seeds:
    bf = f"{OUT}/ms_gemma270m_baseline_s{s}.json"
    vf = f"{OUT}/ms_gemma270m_v07_1_s{s}.json"
    rows[s] = {
        "baseline": metrics(bf) if os.path.exists(bf) else None,
        "v07_1": metrics(vf) if os.path.exists(vf) else None,
    }

print(f"{'seed':>5} | {'baseline sep-ratio':>18} | {'v0.7.1 sep-ratio':>16} | {'v0.7.1 cv-ratio':>15}")
print("-" * 65)
b_sep = []; v_sep = []; v_cv = []
for s in seeds:
    b = rows[s]["baseline"]; v = rows[s]["v07_1"]
    br = b["sep_ratio"] if b else None
    vr = v["sep_ratio"] if v else None
    vc = v["cv_ratio"] if v else None
    if br is not None: b_sep.append(br)
    if vr is not None: v_sep.append(vr)
    if vc is not None: v_cv.append(vc)
    print(f"{s:>5} | {br if br is None else round(br,3):>18} | {vr if vr is None else round(vr,3):>16} | {vc if vc is None else round(vc,2):>15}")

print("-" * 65)
def ms(x): return f"{st.mean(x):.3f} ± {st.pstdev(x):.3f} (n={len(x)})"
print(f"baseline sep-ratio : {ms(b_sep)}")
print(f"v0.7.1   sep-ratio : {ms(v_sep)}")
print(f"v0.7.1   cv-ratio  : {ms(v_cv)}")
print(f"\nv0.7.1 sep-ratio range: [{min(v_sep):.3f}, {max(v_sep):.3f}]")
print(f"baseline sep-ratio range: [{min(b_sep):.3f}, {max(b_sep):.3f}]")
sep_gap = st.mean(v_sep) - st.mean(b_sep)
print(f"mean architecture-attributable gap (v0.7.1 - baseline): {sep_gap:.3f}")
overlap = max(b_sep) >= min(v_sep)
print(f"distributions overlap? {overlap}  (baseline_max={max(b_sep):.3f} vs v07_1_min={min(v_sep):.3f})")
