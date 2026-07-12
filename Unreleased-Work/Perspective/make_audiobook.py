#!/usr/bin/env python3
"""Render *Perspective* as an audiobook via Kokoro TTS (run in WSL, uses the GPU).

    python3 make_audiobook.py [voice] [--speed=0.85] [--dry]

Source : Perspective-Reader.md   (the clean reader edition — no draft memo)
Output : audiobook/<NN>-<slug>.ogg   one per top-level (#) section  + Perspective-full.ogg
Voices : bm_george / bm_fable (British male) · am_michael (US male) · af_heart (US female) · ...
Speed  : match whatever you locked in via voice_studio.py (lower = slower/graver).
OGG/Vorbis keeps the files small and phone-playable without needing ffmpeg.
"""
import sys, re, os, time
import numpy as np
import soundfile as sf

def _opt(flag, default, cast=str):
    return next((cast(a.split("=", 1)[1]) for a in sys.argv[1:] if a.startswith(flag)), default)

VOICE = next((a for a in sys.argv[1:] if not a.startswith("-")), "bm_george")
LANG  = "b" if VOICE[0] == "b" else "a"        # b* = British G2P, else American
SPEED = _opt("--speed=", 0.85, float)
BLEND     = _opt("--blend=", None)             # 2nd voice name; averaged with VOICE
BLEND_AMT = _opt("--blend-amt=", 0.5, float)   # fraction of the 2nd voice
PITCH     = _opt("--pitch=", 0.0, float)       # semitones (librosa); 0 = off
GAIN      = _opt("--gain=", 0.0, float)        # dB; 0 = off
HERE  = os.path.dirname(os.path.abspath(__file__))
SRC   = os.path.join(HERE, "Perspective-Reader.md")
OUTDIR = os.path.join(HERE, "audiobook")
SR = 24000


def clean_inline(s):
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)          # bold
    s = re.sub(r"\*(.+?)\*", r"\1", s)              # italic
    s = re.sub(r"_(.+?)_", r"\1", s)                # underscore emphasis
    s = re.sub(r"`(.+?)`", r"\1", s)                # inline code
    s = re.sub(r"\[(.+?)\]\([^)]*\)", r"\1", s)     # links -> visible text
    return s.strip()


def parse(md):
    sections = []
    cur = None
    for ln in md.split("\n"):
        if re.match(r"^#\s+", ln):                  # h1 -> new chapter
            title = clean_inline(ln[2:])
            slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40] or "section"
            cur = {"title": title, "slug": slug, "blocks": [("h1", title)]}
            sections.append(cur)
        elif re.match(r"^#{2,3}\s+", ln):           # h2/h3 -> spoken sub-heading
            lvl = len(ln) - len(ln.lstrip("#"))
            text = clean_inline(re.sub(r"^#+\s+", "", ln))
            if cur is None:
                cur = {"title": "front", "slug": "front", "blocks": []}
                sections.append(cur)
            cur["blocks"].append(("h%d" % lvl, text))
        elif re.match(r"^(---+|\*\*\*+)\s*$", ln):  # horizontal rule -> drop
            continue
        elif ln.strip() == "":
            continue
        else:                                        # body text
            text = clean_inline(ln.strip())
            if not text:
                continue
            if cur is None:
                cur = {"title": "front", "slug": "front", "blocks": []}
                sections.append(cur)
            cur["blocks"].append(("p", text))
    return sections


def silence(sec):
    return np.zeros(int(sec * SR), dtype=np.float32)


def write_ogg(path, wav, block=200000):
    # libsndfile's Vorbis encoder crashes on very large single writes — stream in blocks.
    with sf.SoundFile(path, "w", samplerate=SR, channels=1, format="OGG", subtype="VORBIS") as f:
        for i in range(0, len(wav), block):
            f.write(wav[i:i + block])


def main():
    md = open(SRC, encoding="utf-8").read()
    sections = parse(md)
    total_words = sum(len(t.split()) for s in sections for _, t in s["blocks"])
    recipe = VOICE + ((" + %.0f%% %s" % (BLEND_AMT * 100, BLEND)) if BLEND else "")
    print("voice=%s speed=%.2f pitch=%+.1f gain=%+.0f  sections=%d words=%d est_audio~%.0fmin"
          % (recipe, SPEED, PITCH, GAIN, len(sections), total_words, total_words / 150.0), flush=True)
    for s in sections:
        wc = sum(len(t.split()) for _, t in s["blocks"])
        print("  [%02d] %-34s %5dw / %d blocks"
              % (sections.index(s), s["title"][:34], wc, len(s["blocks"])), flush=True)
    if "--dry" in sys.argv:
        return

    os.makedirs(OUTDIR, exist_ok=True)
    from kokoro import KPipeline
    pipe = KPipeline(lang_code=LANG, repo_id="hexgrad/Kokoro-82M")
    voice_obj = pipe.load_voice(VOICE)
    if BLEND:
        voice_obj = (1.0 - BLEND_AMT) * voice_obj + BLEND_AMT * pipe.load_voice(BLEND)
    if abs(PITCH) > 0.01:
        import librosa
    t0 = time.time()
    for si, s in enumerate(sections):
        out = os.path.join(OUTDIR, "%02d-%s.ogg" % (si, s["slug"]))
        if os.path.exists(out) and "--force" not in sys.argv:   # resume: keep finished chapters
            print("  skip  %-40s (already rendered)" % os.path.basename(out), flush=True)
            continue
        chunks = []
        for kind, text in s["blocks"]:
            if kind.startswith("h"):
                chunks.append(silence(0.9 if kind == "h1" else 0.6))
            for _, _, audio in pipe(text, voice=voice_obj, speed=SPEED):
                a = audio if isinstance(audio, np.ndarray) else audio.detach().cpu().numpy()
                chunks.append(a.astype(np.float32))
            chunks.append(silence(0.35))
            if kind.startswith("h"):
                chunks.append(silence(0.3))
        wav = np.concatenate(chunks) if chunks else silence(0.1)
        if abs(PITCH) > 0.01:
            wav = librosa.effects.pitch_shift(y=wav, sr=SR, n_steps=PITCH).astype(np.float32)
        if abs(GAIN) > 0.01:
            wav = (wav * (10.0 ** (GAIN / 20.0))).astype(np.float32)
            peak = float(np.max(np.abs(wav))) if wav.size else 0.0
            if peak > 1.0:
                wav = wav / peak
        write_ogg(out, wav)
        print("  wrote %-40s %5.1fmin   (elapsed %4.0fs)"
              % (os.path.basename(out), len(wav) / SR / 60.0, time.time() - t0), flush=True)
    # stitch the full book by streaming each finished chapter back out (low memory, no huge buffer)
    fout = os.path.join(OUTDIR, "Perspective-full.ogg")
    total = 0
    with sf.SoundFile(fout, "w", samplerate=SR, channels=1, format="OGG", subtype="VORBIS") as f:
        for si, s in enumerate(sections):
            ch = os.path.join(OUTDIR, "%02d-%s.ogg" % (si, s["slug"]))
            if not os.path.exists(ch):
                continue
            data, _ = sf.read(ch, dtype="float32")
            for i in range(0, len(data), 200000):
                f.write(data[i:i + 200000])
            f.write(silence(1.2))
            total += len(data) + int(1.2 * SR)
    print("DONE  %s  %.1fmin   total %.0fs"
          % (fout, total / SR / 60.0, time.time() - t0), flush=True)


if __name__ == "__main__":
    main()
