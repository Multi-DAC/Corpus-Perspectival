"""analyze_r3_instrumented.py — the INSTRUMENTED-residual pass (LC39 discriminator).

The keyword pass (analyze_r3.py) measured LANGUAGE and couldn't separate shared-phenomenon
from shared-template. This pass hunts the MIRROR-RESISTANT signal: quantities an INSTRUMENT
produced (radar tracks, measured size/distance/velocity, sensor cross-checks) and especially
WITNESS-vs-INSTRUMENT divergences (R1 Class 5: AARO 1050m vs witness 500-600m). These don't
inherit UFO vocabulary, so their cross-provenance recurrence WOULD discriminate the readings.

PREDICT (med-high): instrumented residuals are SPARSE in R3 (CIA memos / FBI reports / NASA
debriefs / archives are description-heavy, measurement-light vs R1's Navy FLIR/radar mission
reports) and CONCENTRATED in a few docs. Output: instrumentation-density ranking + extracted
snippets for close reading.
"""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
cat = json.load(open(os.path.join(HERE, "release03-catalog.json")))

SENSOR = r"\b(radar|flir|infrared|\bir\b|night.?vision|\bnvg\b|sonar|telemetr|triangulat|photogramm|theodolite|transponder|altimeter|gun.?camera|atflir|interferomet|spectrum analyz|oscilloscope|seismograph|magnetometer|geiger|scintillat)\w*"
NUMUNIT = r"\b\d[\d,\.]*\s?-?\s?(feet|foot|ft|meters?|metres?|\bm\b|miles?|nautical|nm\b|knots?|\bkt\b|mph|mach|degrees?|deg\b|mhz|ghz|hz\b|seconds?|sec\b|minutes?|min\b|km\b|kilometers?|nautical miles?|rpm|g-?force|\bgs?\b)\b"
DIVERGE = r"(estimat\w+[^.]{0,60}(but|however|actual|measur|whereas)|measured at|actual\w*\s+(size|distance|altitude|speed|range|velocity)|radar (showed|indicat|track|return|contact|painted)|tracked at|computed|calculated[^.]{0,40}\d|appeared[^.]{0,50}(but|actual|measur)|underestimat|overestimat)"

def windows(text, pat, w=130):
    out=[]
    for m in re.finditer(pat, text, re.I):
        s=max(0,m.start()-w); e=min(len(text),m.end()+w)
        out.append(re.sub(r"\s+"," ",text[s:e]).strip())
    return out

rows=[]
snip_dump=[]
for d in cat:
    rid=str(d["id"]); p=os.path.join(HERE,"extracted-text",f"{rid}.txt")
    if not os.path.exists(p): continue
    t=open(p,encoding="utf-8").read()
    tl=t.lower()
    sensor_hits=len(re.findall(SENSOR,tl))
    # instrumented windows: a sensor term with a number+unit nearby
    instr_windows=[wnd for wnd in windows(tl,SENSOR) if re.search(NUMUNIT,wnd)]
    diverge_hits=re.findall(DIVERGE,tl)
    score=len(instr_windows)*2 + len(diverge_hits)
    rows.append({"id":rid,"agency":d.get("agency","?"),"title":d.get("title","")[:50],
                 "sensor":sensor_hits,"instr_win":len(instr_windows),"diverge":len(diverge_hits),"score":score})
    if score>0:
        snip_dump.append((score,rid,d.get("agency"),d.get("title","")[:60],
                          instr_windows[:3], [w for w in windows(tl,DIVERGE)][:2]))

rows.sort(key=lambda r:-r["score"])
print(f"R3 text-docs scanned: {len(rows)}")
nz=[r for r in rows if r["score"]>0]
print(f"docs with ANY instrumented/divergence signal: {len(nz)}/{len(rows)} ({100*len(nz)/len(rows):.0f}%)")
print(f"docs with instrumented WINDOW (sensor+number): {sum(1 for r in rows if r['instr_win']>0)}")
print(f"docs with divergence phrase: {sum(1 for r in rows if r['diverge']>0)}\n")
print("=== TOP 15 by instrumentation score ===")
for r in rows[:15]:
    print(f"  [{r['id']}] {r['agency']:18s} s={r['sensor']:2d} iw={r['instr_win']:2d} dv={r['diverge']:2d} | {r['title']}")
# agency concentration of instrumented signal
from collections import Counter
agc=Counter();
for r in nz: agc[r["agency"]]+=r["score"]
print("\ninstrumented-score by agency:", dict(agc))

# dump snippets for close reading
snip_dump.sort(key=lambda x:-x[0])
with open(os.path.join(HERE,"instrumented_snippets.txt"),"w",encoding="utf-8") as f:
    for score,rid,ag,title,iw,dv in snip_dump[:18]:
        f.write(f"\n{'='*70}\n[{rid}] {ag} | {title}  (score {score})\n")
        for s in iw: f.write(f"  INSTR: ...{s}...\n")
        for s in dv: f.write(f"  DIVERGE: ...{s}...\n")
print(f"\nsnippets -> instrumented_snippets.txt (top {min(18,len(snip_dump))} docs)")
