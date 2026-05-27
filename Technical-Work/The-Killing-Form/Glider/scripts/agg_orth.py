import json, os, statistics as st
OUT = "/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results"
seeds = [71, 137, 271, 314, 419]

def score(f):
    return json.load(open(f)).get("orthogonality_score")

pri = score(f"{OUT}/ms_orth_gemma270m_pristine.json")
print(f"pristine: {pri:.4f}\n")
print(f"{'seed':>5} | {'baseline':>9} | {'v0.7.1':>9} | {'v07_1 - base':>12}")
print("-"*45)
b, v = [], []
for s in seeds:
    bs = score(f"{OUT}/ms_orth_gemma270m_baseline_s{s}.json")
    vs = score(f"{OUT}/ms_orth_gemma270m_v07_1_s{s}.json")
    b.append(bs); v.append(vs)
    print(f"{s:>5} | {bs:>9.4f} | {vs:>9.4f} | {vs-bs:>+12.4f}")
print("-"*45)
print(f"baseline : {st.mean(b):.4f} ± {st.pstdev(b):.4f} (n={len(b)})")
print(f"v0.7.1   : {st.mean(v):.4f} ± {st.pstdev(v):.4f} (n={len(v)})")
gaps = [vi-bi for vi,bi in zip(v,b)]
print(f"per-seed (v07_1 - baseline): mean {st.mean(gaps):+.4f} ± {st.pstdev(gaps):.4f}")
print(f"  gap range: [{min(gaps):+.4f}, {max(gaps):+.4f}]")
pos = all(g>0 for g in gaps)
print(f"  v0.7.1 > baseline on EVERY seed? {pos}")
print(f"\nDirection vs pristine: baseline {st.mean(b)-pri:+.4f}, v0.7.1 {st.mean(v)-pri:+.4f}")
