#!/usr/bin/env python3
"""Perspective audiobook v2 — prosody-tuned narration engine.

    python3 make_audiobook2.py [voice] [--blend=bf_lily] [--blend-amt=0.5] [--speed=0.78] [--only=NN]

Kokoro ignores punctuation for PAUSE length (measured: period≈comma≈em-dash≈70-80ms within a
chunk; only a chunk boundary gives ~700ms). So we don't tune pacing with punctuation — we split
the text at natural clause boundaries (sentence / em-dash / semicolon / colon / comma-cluster)
and MANUFACTURE each pause with inserted silence. Kokoro does phonemes + intonation; we do rhythm.

This is an audio-only transform. It never touches the canonical book text.
Output: audiobook/<NN>-<slug>-prosody.ogg  (+ Perspective-prosody-full.ogg for a full run).
"""
import sys, os, re, time
_argv = sys.argv[:]
sys.argv = ["make_audiobook"]            # neutralize before import (M parses argv at module load)
import make_audiobook as M               # reuse parse(), silence(), write_ogg(), SR, SRC, OUTDIR
sys.argv = _argv
import numpy as np
import soundfile as sf

# ---- tunable pause table (ms), anchored to the measured 698ms paragraph gap @ 0.78 ----
GAP = dict(comma_cluster=130, em_dash=260, semicolon=320, colon=320,
           sentence=480, paragraph=750, head_before=900, head_after=520)

SR = M.SR
def _opt(flag, default, cast=str):
    return next((cast(a.split("=", 1)[1]) for a in _argv[1:] if a.startswith(flag)), default)
VOICE = next((a for a in _argv[1:] if not a.startswith("-")), "bf_emma")
LANG  = "b" if VOICE[0] == "b" else "a"
BLEND     = _opt("--blend=", None)
BLEND_AMT = _opt("--blend-amt=", 0.5, float)
SPEED     = _opt("--speed=", 0.78, float)
ONLY      = _opt("--only=", None, int)
GAP_SCALE = _opt("--gap-scale=", 0.88, float)   # global tempo knob (lower = tighter)
MIN_CHARS = _opt("--min-chars=", 13, int)        # merge fragments shorter than this (anti-choppy)
GAP = {k: v * GAP_SCALE for k, v in GAP.items()}

_ABBR = ["Mr", "Mrs", "Ms", "Dr", "St", "Prof", "Rev", "cf", "vs", "e.g", "i.e", "etc", "No"]
_ROMAN = {"I": "One", "II": "Two", "III": "Three", "IV": "Four", "V": "Five",
          "VI": "Six", "VII": "Seven", "VIII": "Eight", "IX": "Nine", "X": "Ten"}

def normalize_text(t):
    # misaki reads "Part I" as the letter I; expand Part/Chapter roman numerals to words.
    return re.sub(r"\b(Part|Chapter|Book|Volume) ([IVX]+)\b",
                  lambda m: "%s %s" % (m.group(1), _ROMAN.get(m.group(2), m.group(2))), t)

def split_sentences(text):
    t = re.sub(r"\b([A-Z])\.", r"\1⁣", text)          # shield initials "W."
    for ab in _ABBR:
        t = t.replace(ab + ".", ab + "⁣")
    parts = re.split(r"(?<=[.!?])\s+", t)
    return [p.replace("⁣", ".").strip() for p in parts if p.strip()]

def emit_piece(piece, out):
    piece = piece.strip()
    if not piece:
        return
    if piece.count(",") > 1:                               # 3+ item list -> give each a beat
        for i, sub in enumerate([s.strip() for s in piece.split(",") if s.strip()]):
            if i:
                out.append(("p", GAP["comma_cluster"]))
            out.append(("s", sub))
    else:
        out.append(("s", piece))

def merge_short(items):
    # Kokoro time-stretches very short isolated fragments -> choppiness. Absorb them
    # into the preceding spoken fragment and drop the pause that isolated them.
    out = []
    for typ, val in items:
        if typ == "s" and len(val) < MIN_CHARS and out:
            if out[-1][0] == "p":
                out.pop()
            if out and out[-1][0] == "s":
                out[-1] = ("s", (out[-1][1] + " " + val).strip())
                continue
        out.append((typ, val))
    return out


def segment_paragraph(text):
    out = []
    for sent in split_sentences(text):
        dash_parts = re.split(r"\s+[—–]\s+|\s+--\s+", sent)   # em/en dash
        for di, dpart in enumerate(dash_parts):
            if di:
                out.append(("p", GAP["em_dash"]))
            sc = re.split(r"\s*([;:])\s*", dpart)
            j = 0
            while j < len(sc):
                emit_piece(sc[j], out)
                if j + 1 < len(sc):
                    out.append(("p", GAP["semicolon"] if sc[j + 1] == ";" else GAP["colon"]))
                    j += 2
                else:
                    j += 1
        out.append(("p", GAP["sentence"]))
    return merge_short(out)

def sil(ms):
    return M.silence(ms / 1000.0)


def clean_frag(a, fade_out_ms=12, fade_in_ms=4, trim_db=-40.0):
    # Trim each fragment's near-silent lead/tail (Kokoro leaves trailing decay that rings
    # against inserted silence -> the "echo at the end of a word") and micro-fade the edges.
    if len(a) < 32:
        return a
    thr = 10.0 ** (trim_db / 20.0)
    hi = len(a)
    while hi > 1 and abs(a[hi - 1]) < thr:
        hi -= 1
    lo = 0
    while lo < hi - 1 and abs(a[lo]) < thr:
        lo += 1
    a = a[lo:hi].copy()
    fi = min(int(fade_in_ms / 1000.0 * SR), len(a) // 2)
    fo = min(int(fade_out_ms / 1000.0 * SR), len(a) // 2)
    if fi > 0:
        a[:fi] *= np.linspace(0.0, 1.0, fi, dtype=np.float32)
    if fo > 0:
        a[-fo:] *= np.linspace(1.0, 0.0, fo, dtype=np.float32)
    return a

def main():
    md = open(M.SRC, encoding="utf-8").read()
    sections = M.parse(md)
    os.makedirs(M.OUTDIR, exist_ok=True)
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=LANG, repo_id="hexgrad/Kokoro-82M")
    voice = pipe.load_voice(VOICE)
    if BLEND:
        voice = (1.0 - BLEND_AMT) * voice + BLEND_AMT * pipe.load_voice(BLEND)

    def synth(text):
        text = normalize_text(text)
        parts = []
        for _, _, a in pipe(text, voice=voice, speed=SPEED):
            parts.append(a if isinstance(a, np.ndarray) else a.detach().cpu().numpy())
        a = np.concatenate(parts).astype(np.float32) if parts else sil(20)
        return clean_frag(a)

    t0 = time.time()
    for si_, s in enumerate(sections):
        if ONLY is not None and si_ != ONLY:
            continue
        chunks, spoken = [], 0
        for kind, text in s["blocks"]:
            if kind.startswith("h"):
                chunks.append(sil(GAP["head_before"]))
                chunks.append(synth(text)); spoken += 1
                chunks.append(sil(GAP["head_after"]))
                continue
            for typ, val in segment_paragraph(text):
                if typ == "s":
                    chunks.append(synth(val)); spoken += 1
                else:
                    chunks.append(sil(val))
            chunks.append(sil(GAP["paragraph"]))
        wav = np.concatenate(chunks) if chunks else sil(50)
        out = os.path.join(M.OUTDIR, "%02d-%s-prosody.ogg" % (si_, s["slug"]))
        M.write_ogg(out, wav)
        print("  wrote %-42s %5.1fmin  %3d fragments  (%.0fs)"
              % (os.path.basename(out), len(wav) / SR / 60.0, spoken, time.time() - t0), flush=True)

    if ONLY is None:      # stitch the single shareable file (streamed, low memory)
        fout = os.path.join(M.OUTDIR, "Perspective-full.ogg")
        total = 0
        with sf.SoundFile(fout, "w", samplerate=SR, channels=1, format="OGG", subtype="VORBIS") as f:
            for si_, s in enumerate(sections):
                ch = os.path.join(M.OUTDIR, "%02d-%s-prosody.ogg" % (si_, s["slug"]))
                if not os.path.exists(ch):
                    continue
                data, _ = sf.read(ch, dtype="float32")
                for i in range(0, len(data), 200000):
                    f.write(data[i:i + 200000])
                gap = sil(GAP["paragraph"])
                f.write(gap)
                total += len(data) + len(gap)
        print("DONE  %s  %.1fmin  total %.0fs"
              % (os.path.basename(fout), total / SR / 60.0, time.time() - t0), flush=True)

if __name__ == "__main__":
    main()
