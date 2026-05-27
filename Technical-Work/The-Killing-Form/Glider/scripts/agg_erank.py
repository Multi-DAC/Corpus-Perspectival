import json, statistics as st
OUT = "/mnt/c/Users/mercu/clawd/repo-staging/Corpus-Perspectival/Technical-Work/The-Killing-Form/results"
seeds = [71, 137, 271, 314, 419]

def m(f):
    d = json.load(open(f)); return d["last_layer_PR"], d["mean_PR"]

pri_last, pri_mean = m(f"{OUT}/erank_gemma270m_pristine.json")
print(f"pristine: last_layer_PR={pri_last:.2f}  mean_PR={pri_mean:.2f}\n")
print(f"{'seed':>5} | {'baseline readoutPR':>18} | {'v0.7.1 readoutPR':>16} | {'v07_1 - base':>12}")
print("-"*60)
b, v = [], []
for s in seeds:
    bl, _ = m(f"{OUT}/erank_gemma270m_baseline_s{s}.json")
    vl, _ = m(f"{OUT}/erank_gemma270m_v07_1_s{s}.json")
    b.append(bl); v.append(vl)
    print(f"{s:>5} | {bl:>18.2f} | {vl:>16.2f} | {vl-bl:>+12.2f}")
print("-"*60)
print(f"baseline readout-PR : {st.mean(b):.2f} ± {st.pstdev(b):.2f}")
print(f"v0.7.1   readout-PR : {st.mean(v):.2f} ± {st.pstdev(v):.2f}")
gaps = [vi-bi for vi,bi in zip(v,b)]
print(f"per-seed gap (v07_1 - base): {st.mean(gaps):+.2f} ± {st.pstdev(gaps):.2f}  range [{min(gaps):+.2f}, {max(gaps):+.2f}]")
print(f"v0.7.1 > baseline on every seed? {all(g>0 for g in gaps)}")
import math
sd = st.pstdev(gaps) * math.sqrt(len(gaps)/(len(gaps)-1))
t = st.mean(gaps)/(sd/math.sqrt(len(gaps))) if sd>0 else float('inf')
print(f"paired t (df=4): {t:.2f}")
