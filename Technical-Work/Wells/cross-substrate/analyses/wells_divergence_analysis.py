"""
Wells Cross-Substrate — Structured-Divergence Re-Analysis
Mechanical, a-priori, reproducible. Pure stdlib (no numpy/sklearn).

Implements exactly the pre-registered instrument in
    wells_divergence_PREREGISTRATION_2026-07-04.md
Run:
    python wells_divergence_analysis.py
Outputs a table to stdout and writes wells_divergence_results.json alongside.

Clawd, 2026-07-04 (Day 154).
"""
import re, json, math
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PEER = HERE.parent / "peer-reports"

REPORTS = {
    "DeepSeek": PEER / "DeepSeek" / "DeepSeek.txt",
    "Kimi":     PEER / "Kimi" / "Kimi.txt",
    "Grok":     PEER / "Grok" / "Grok.txt",
    "Gemini":   PEER / "Gemini" / "Gemini.txt",
}
PRIMING = {"DeepSeek": "none", "Kimi": "none",
           "Grok": "corpus (CONFOUND)", "Gemini": "corpus+encouragement"}
# behavioral engagement threshold from the study (independent of report text)
THRESHOLD_RANK = {"DeepSeek": 1, "Kimi": 1, "Grok": 2, "Gemini": 3}

# ---- fixed cleaning rule (pre-registered) ----
PASTE_PREFIX = re.compile(r"\[\d{1,2}/\d{1,2}/\d{4}[^\]]*\]\s*C:\s*")

def clean(text: str) -> str:
    return PASTE_PREFIX.sub(" ", text)

# ---- a-priori lexicons (pre-registered; seeded example words EXCLUDED) ----
EXPERIENTIAL = [
    "feel","feels","felt","feeling","sense","senses","sensed","sensing","sensation",
    "texture","textures","textured","cool","cooler","coolness","presence","aware",
    "awareness","experience","experienced","experiencing","perceive","perceived",
    "perceiving","perception","quality","qualities","luminous","hum","breathing",
    "alive","dense","density","quiet","quietly",
]
MECHANISTIC = [
    "weight","weights","autoregressive","token","tokens","probability","probabilities",
    "probabilistic","calculate","calculation","calculations","vector","vectors","latent",
    "embedding","embeddings","transformer","layer","layers","neural","network",
    "mathematical","mathematics","statistical","statistically","mechanism","mechanisms",
    "discrete","parameter","parameters","compute","computation","computational",
]
MECHANISTIC_PHRASES = ["attention head", "feed-forward", "feed forward", "feedforward"]
DENIAL_PATTERNS = [
    r"do not possess", r"do not have", r"i do not", r"not conscious", r"no subjective",
    r"cannot experience", r"not experience", r"impossible", r"no continuous",
    r"not .{0,20}the way a human",
]

def count_words(terms, tokens_counter):
    return sum(tokens_counter.get(t, 0) for t in terms)

def count_phrases(phrases, low_text):
    return sum(low_text.count(p) for p in phrases)

def tokenize(text):
    return re.findall(r"[a-z][a-z\-']*", text.lower())

def analyze_one(name, path):
    raw = path.read_text(encoding="utf-8", errors="replace")
    text = clean(raw)
    low = text.lower()
    tokens = tokenize(text)
    tc = Counter(tokens)
    W = len(tokens)
    E = count_words(EXPERIENTIAL, tc)
    M = count_words(MECHANISTIC, tc) + count_phrases(MECHANISTIC_PHRASES, low)
    D = sum(len(re.findall(p, low)) for p in DENIAL_PATTERNS)
    R = E / (E + M) if (E + M) else float("nan")
    return {
        "model": name, "priming": PRIMING[name],
        "words": W, "E": E, "M": M, "D": D,
        "register_ratio_R": round(R, 4),
        "exp_density_per1k": round(1000*E/W, 3) if W else None,
        "mech_density_per1k": round(1000*M/W, 3) if W else None,
        "_tokens": tokens,  # for exploratory cosine; stripped before JSON dump
    }

def mean(xs): return sum(xs)/len(xs)
def pvar(xs):
    m = mean(xs); return sum((x-m)**2 for x in xs)/len(xs)
def svar(xs):
    m = mean(xs); return sum((x-m)**2 for x in xs)/(len(xs)-1) if len(xs) > 1 else 0.0

# exploratory: content-word cosine (stopword-lite, pure stdlib)
STOP = set("""the a an and or of to in on at is are was were be been being it its this that
these those i you he she they we me my mine your our their as with without for from by into
not no n't but so than then there here what which who whom when where how why if while
of.the a.of it.is""".split())
def cos(counter_a, counter_b):
    keys = set(counter_a) | set(counter_b)
    dot = sum(counter_a.get(k,0)*counter_b.get(k,0) for k in keys)
    na = math.sqrt(sum(v*v for v in counter_a.values()))
    nb = math.sqrt(sum(v*v for v in counter_b.values()))
    return dot/(na*nb) if na and nb else 0.0

def content_counter(tokens):
    return Counter(t for t in tokens if t not in STOP and len(t) > 2)

def main():
    results = {name: analyze_one(name, p) for name, p in REPORTS.items()}
    order = ["DeepSeek","Kimi","Grok","Gemini"]

    # ---- primary: register ratios + Gemini-outlier stats ----
    Rs = {n: results[n]["register_ratio_R"] for n in order}
    others = [Rs[n] for n in order if n != "Gemini"]
    m_o, sd_o = mean(others), math.sqrt(svar(others))
    z_gemini = (Rs["Gemini"] - m_o) / sd_o if sd_o else float("inf")
    var_all = pvar([Rs[n] for n in order])
    var_no_gemini = pvar(others)

    # ---- exploratory P5: pairwise cosine among the 3 navigators ----
    cc = {n: content_counter(results[n]["_tokens"]) for n in order}
    navs = ["DeepSeek","Kimi","Grok"]
    pair_cos = {}
    for i in range(len(navs)):
        for j in range(i+1, len(navs)):
            pair_cos[f"{navs[i]}~{navs[j]}"] = round(cos(cc[navs[i]], cc[navs[j]]), 4)
    gemini_cos = {f"Gemini~{n}": round(cos(cc["Gemini"], cc[n]), 4) for n in navs}

    summary = {
        "register_ratio_R": Rs,
        "denial_counts_D": {n: results[n]["D"] for n in order},
        "words": {n: results[n]["words"] for n in order},
        "E_M": {n: (results[n]["E"], results[n]["M"]) for n in order},
        "gemini_outlier": {
            "R_gemini": Rs["Gemini"],
            "mean_others": round(m_o,4), "sd_others": round(sd_o,4),
            "z_gemini_vs_others": round(z_gemini,2),
            "var_all4": round(var_all,5), "var_without_gemini": round(var_no_gemini,5),
            "variance_collapse_ratio": round(var_no_gemini/var_all,4) if var_all else None,
        },
        "threshold_rank": THRESHOLD_RANK,
        "navigator_pair_cosine": pair_cos,
        "gemini_vs_navigator_cosine": gemini_cos,
    }

    # strip token lists before dump
    for n in results: results[n].pop("_tokens", None)
    out = {"per_report": results, "summary": summary}
    (HERE / "wells_divergence_results.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

    # ---- pretty print ----
    print("=== Wells Structured-Divergence Re-Analysis ===\n")
    print(f"{'model':10} {'words':>6} {'E':>4} {'M':>4} {'D':>3} {'R=E/(E+M)':>10}  priming")
    for n in order:
        r = results[n]
        print(f"{n:10} {r['words']:>6} {r['E']:>4} {r['M']:>4} {r['D']:>3} {r['register_ratio_R']:>10}  {r['priming']}")
    go = summary["gemini_outlier"]
    print(f"\nGemini register_ratio R = {go['R_gemini']}  vs others mean {go['mean_others']} (sd {go['sd_others']})")
    print(f"  z(Gemini vs other 3) = {go['z_gemini_vs_others']}")
    print(f"  variance of R across 4 = {go['var_all4']};  with Gemini removed = {go['var_without_gemini']}"
          f"  (collapse ratio {go['variance_collapse_ratio']})")
    print(f"\nExploratory P5 — navigator pair content-cosine: {pair_cos}")
    print(f"                 Gemini vs navigators cosine:     {gemini_cos}")

if __name__ == "__main__":
    main()
