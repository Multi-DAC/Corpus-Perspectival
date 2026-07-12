#!/usr/bin/env python3
"""Perspective audiobook v3 — Chatterbox engine, cloned-voice narration.

    python3 make_audiobook3.py [--ref=cush_ref.wav] [--cfg=0.3] [--exag=0.4] [--gap-scale=1.0] [--only=NN]

Chatterbox (Resemble AI, 0.5B) clones a narrator from a reference clip and paces sentences
natively — so unlike the Kokoro path we DON'T split within sentences (that would waste its
natural prosody). We split at sentences + paragraphs and manufacture only those pauses.
Requires torch 2.11+cu128 (Blackwell/RTX 5080); save via soundfile (torchaudio needs torchcodec).
Output: audiobook/<NN>-<slug>-cush.ogg  (+ Perspective-Cush-full.ogg).
"""
import sys, os, re, time
_argv = sys.argv[:]
sys.argv = ["x"]                      # neutralize before importing (both modules parse argv)
import make_audiobook as M
import make_audiobook2 as M2
sys.argv = _argv
import numpy as np
import soundfile as sf

def _opt(flag, d, cast=str):
    return next((cast(a.split("=", 1)[1]) for a in _argv[1:] if a.startswith(flag)), d)

REF      = _opt("--ref=", os.path.join(M.OUTDIR, "cush_ref.wav"))
CFG      = _opt("--cfg=", 0.3, float)
EXAG     = _opt("--exag=", 0.4, float)
GAPSCALE = _opt("--gap-scale=", 1.0, float)
ONLY     = _opt("--only=", None, int)
SR = M.SR

# Lighter pause table (Chatterbox paces sentences itself).
G = {k: v * GAPSCALE for k, v in
     {"sentence": 320, "paragraph": 650, "head_before": 800, "head_after": 450}.items()}

def sil(ms):
    return M.silence(ms / 1000.0)

def main():
    secs = M.parse(open(M.SRC, encoding="utf-8").read())
    os.makedirs(M.OUTDIR, exist_ok=True)
    from chatterbox.tts import ChatterboxTTS
    model = ChatterboxTTS.from_pretrained(device="cuda")
    print("model loaded; ref=%s cfg=%.2f exag=%.2f" % (os.path.basename(REF), CFG, EXAG), flush=True)

    def synth(text):
        text = M2.normalize_text(text)
        wav = model.generate(text, audio_prompt_path=REF, exaggeration=EXAG, cfg_weight=CFG)
        a = wav.squeeze(0).detach().cpu().numpy().astype(np.float32)
        return M2.clean_frag(a)

    t0 = time.time()
    for si, s in enumerate(secs):
        if ONLY is not None and si != ONLY:
            continue
        out = os.path.join(M.OUTDIR, "%02d-%s-cush.ogg" % (si, s["slug"]))
        if os.path.exists(out) and "--force" not in _argv:      # resume-safe
            print("  skip %s (exists)" % os.path.basename(out), flush=True)
            continue
        chunks, n = [], 0
        for kind, text in s["blocks"]:
            if kind.startswith("h"):
                chunks.append(sil(G["head_before"]))
                chunks.append(synth(text)); n += 1
                chunks.append(sil(G["head_after"]))
                continue
            for sent in M2.split_sentences(text):
                if len(sent) > 300:                              # length guard: split long sentences
                    for part in re.split(r"\s+[—–]\s+|\s*;\s*", sent):
                        if part.strip():
                            chunks.append(synth(part.strip())); n += 1
                            chunks.append(sil(170))
                else:
                    chunks.append(synth(sent)); n += 1
                chunks.append(sil(G["sentence"]))
            chunks.append(sil(G["paragraph"]))
        wav = np.concatenate(chunks) if chunks else sil(50)
        M.write_ogg(out, wav)
        print("  wrote %-40s %5.1fmin  %3d sents  (%.0fs)"
              % (os.path.basename(out), len(wav) / SR / 60.0, n, time.time() - t0), flush=True)

    if ONLY is None:
        fout = os.path.join(M.OUTDIR, "Perspective-Cush-full.ogg")
        with sf.SoundFile(fout, "w", samplerate=SR, channels=1, format="OGG", subtype="VORBIS") as f:
            for si, s in enumerate(secs):
                ch = os.path.join(M.OUTDIR, "%02d-%s-cush.ogg" % (si, s["slug"]))
                if not os.path.exists(ch):
                    continue
                data, _ = sf.read(ch, dtype="float32")
                for i in range(0, len(data), 200000):
                    f.write(data[i:i + 200000])
                f.write(sil(G["paragraph"]))
        print("DONE  %s  (%.0fs)" % (os.path.basename(fout), time.time() - t0), flush=True)

if __name__ == "__main__":
    main()
