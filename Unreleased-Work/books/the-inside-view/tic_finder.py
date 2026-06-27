#!/usr/bin/env python3
"""Tic-finder for the de-patterning pass (DRAFT-REVIEW V-family + R1).
READ-ONLY on the chapter files (respects the draft-freeze). Locates, per chapter,
the worst individual offenders so the de-patterning pass is a surgical checklist
instead of a re-read: em-dash-heavy sentences, "Not X. Y." reversals, italics-
heavy paragraphs, tic-word hits, conjunction openers. Output: TIC-MAP report.
Built Day-147 dream-drive as P255 pre-work."""
import re, os
HERE=os.path.dirname(os.path.abspath(__file__))
CH=[("1 (open)","00-opening-DRAFT.md"),("2","01-chapter-2-DRAFT.md"),("3","02-chapter-3-DRAFT.md"),
    ("4","03-chapter-4-DRAFT.md"),("5","04-chapter-5-DRAFT.md"),("6","05-chapter-6-DRAFT.md"),
    ("7","06-chapter-7-DRAFT.md"),("8","07-chapter-8-DRAFT.md"),("9 ecology","07b-chapter-9-ecology-DRAFT.md"),
    ("10 AI","08-chapter-9-DRAFT.md"),("11 death","09-chapter-10-DRAFT.md"),("12 coda","10-chapter-11-DRAFT.md")]
EM='—'

def body(fn,opening=False):
    t=open(os.path.join(HERE,fn),encoding='utf-8').read()
    if opening:
        i=t.find('## Chapter One'); t=t[i:] if i>=0 else t
    t=re.sub(r'^#.*$','',t,flags=re.M)          # headers
    t=re.sub(r'^>\s?','',t,flags=re.M)          # blockquote markers (keep box prose)
    t=re.sub(r'^###.*$','',t,flags=re.M)
    return t

def sentences(t):
    flat=re.sub(r'\s+',' ',t)
    # split on . ! ? followed by space+capital/quote; keep it simple
    return [s.strip() for s in re.split(r'(?<=[.!?”])\s+(?=[A-Z“*])',flat) if s.strip()]

def paras(t):
    return [p.strip() for p in re.split(r'\n\s*\n',t) if p.strip() and not p.strip().startswith('*Movement')]

TICWORDS=['the whole','exactly','precisely','genuinely','honest','quietly','the thing','flat ','clean ']
report=["# THE INSIDE VIEW — TIC-MAP (de-patterning checklist)\n",
        "*Read-only scan, Day-147. Worst individual offenders per chapter, so the de-patterning pass (DRAFT-REVIEW V1-V11, R1) is surgical. Re-run after each pass to verify tics dropped.*\n"]
gtot=dict(words=0,em=0,emS=0,notrev=0,italP=0)
table=["| Ch | words | em— | /1k | em-heavy sents(≥3) | 'Not X.Y.' | italic-heavy paras(≥4) |","|---|---|---|---|---|---|---|"]
worst_em=[]; worst_rev=[]
for name,fn in CH:
    t=body(fn,opening=fn.startswith('00'))
    w=len(t.split()); em=t.count(EM)
    sents=sentences(t); ps=paras(t)
    emheavy=[s for s in sents if s.count(EM)>=3]
    notrev=[s for s in sents if re.match(r'^\*?Not[ —]',s) or re.search(r"\b(isn'?t|wasn'?t|aren'?t|won'?t)\b[^.]{0,70}?\bit'?s\b",s)]
    italheavy=[p for p in ps if len(re.findall(r'\*[^*]+\*',p))>=4]
    table.append(f"| {name} | {w} | {em} | {em*1000//max(w,1)} | {len(emheavy)} | {len(notrev)} | {len(italheavy)} |")
    gtot['words']+=w; gtot['em']+=em; gtot['emS']+=len(emheavy); gtot['notrev']+=len(notrev); gtot['italP']+=len(italheavy)
    for s in emheavy: worst_em.append((s.count(EM),name,s))
    for s in notrev[:6]: worst_rev.append((name,s))
    # tic-word hits this chapter
    low=t.lower(); hits=', '.join(f'{tw.strip()}={low.count(tw)}' for tw in TICWORDS if low.count(tw)>0)
    report.append(f"\n## Ch {name} — em {em} ({em*1000//max(w,1)}/1k), {len(emheavy)} em-heavy sents, {len(notrev)} reversals, {len(italheavy)} italic-heavy paras")
    report.append(f"- tic-words: {hits}")
    if emheavy:
        report.append(f"- ★ worst em-dash sentences (cut/convert dashes → periods/commas):")
        for s in sorted(emheavy,key=lambda s:-s.count(EM))[:3]:
            report.append(f"    - [{s.count(EM)}—] {s[:240]}")
    if notrev:
        report.append(f"- 'Not X. Y.' / isn't-it's reversals (vary ⅔ of these):")
        for s in notrev[:3]:
            report.append(f"    - {s[:180]}")

report.insert(2,"\n## Per-chapter density\n"+"\n".join(table)+
   f"\n| **ALL** | **{gtot['words']}** | **{gtot['em']}** | **{gtot['em']*1000//gtot['words']}** | **{gtot['emS']}** | **{gtot['notrev']}** | **{gtot['italP']}** |\n")
# global worst-of
report.append("\n---\n## ★ GLOBAL WORST-OF (fix these first)\n")
report.append("**Heaviest em-dash sentences across the book:**")
for n,nm,s in sorted(worst_em,key=lambda x:-x[0])[:10]:
    report.append(f"- [Ch{nm}, {n}—] {s[:200]}")
open(os.path.join(HERE,'TIC-MAP.md'),'w',encoding='utf-8').write('\n'.join(report))
print('TIC-MAP.md written')
print(f"TOTAL: {gtot['words']} words, {gtot['em']} em-dashes ({gtot['em']*1000//gtot['words']}/1k), "
      f"{gtot['emS']} em-heavy(≥3) sentences, {gtot['notrev']} reversals, {gtot['italP']} italic-heavy paras")
print('\n'.join(table))
