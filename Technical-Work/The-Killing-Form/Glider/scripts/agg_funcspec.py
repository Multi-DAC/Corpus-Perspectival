import json, math, statistics as st
OUT = "/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results"
seeds = [71, 137, 271, 314, 419]
def cs(f): return json.load(open(f))["class_sep_index"]
pri = cs(f"{OUT}/funcspec_gemma270m_pristine.json")
print(f"pristine class_sep: {pri:+.4f}\n")
print(f"{'seed':>5} | {'baseline':>9} | {'v0.7.1':>9} | {'v07_1-base':>10}")
print("-"*42)
b, v = [], []
for s in seeds:
    bs = cs(f"{OUT}/funcspec_gemma270m_baseline_s{s}.json")
    vs = cs(f"{OUT}/funcspec_gemma270m_v07_1_s{s}.json")
    b.append(bs); v.append(vs)
    print(f"{s:>5} | {bs:>+9.4f} | {vs:>+9.4f} | {vs-bs:>+10.4f}")
print("-"*42)
print(f"baseline: {st.mean(b):+.4f} ± {st.pstdev(b):.4f}")
print(f"v0.7.1  : {st.mean(v):+.4f} ± {st.pstdev(v):.4f}")
gaps = [vi-bi for vi,bi in zip(v,b)]
print(f"gap (v07_1-base): {st.mean(gaps):+.4f} ± {st.pstdev(gaps):.4f}  range [{min(gaps):+.4f},{max(gaps):+.4f}]")
print(f"v0.7.1 > baseline every seed? {all(g>0 for g in gaps)}")
sd = st.pstdev(gaps)*math.sqrt(len(gaps)/(len(gaps)-1))
print(f"paired t (df=4): {st.mean(gaps)/(sd/math.sqrt(len(gaps))):.2f}" if sd>0 else "t: inf")
