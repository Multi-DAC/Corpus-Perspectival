#!/usr/bin/env python3
"""Perspective — Voice Studio.  Audition + tune Kokoro voices in the browser.

Run in WSL (uses the GPU):  python3 voice_studio.py
Then open  http://localhost:7860  in a Windows browser.

Knobs (what's real):
  * Voice        — Kokoro speaker (native).
  * Blend voice  — a SECOND speaker; the two embeddings are averaged to make a custom
                   voice (native Kokoro capability). Set to "— none —" for a single voice.
  * Blend        — fraction of the second voice (0 = all A, 1 = all B).
  * Speed        — native Kokoro speed (lower = slower / graver).
  * Pitch        — semitone shift, post-processed with librosa (NOT a native knob;
                   +/- a couple of semitones is clean, larger gets artefacty).
  * Gain         — output volume in dB.

Lock one in, then render the book:
    python3 make_audiobook.py <voice> --speed=<s>
(Blend/pitch/gain are audition-only for now; if you want a blended/pitched final render,
 tell Clawd the recipe and he'll wire the exact combination into make_audiobook.py.)
"""
import numpy as np
import gradio as gr
import librosa
from kokoro import KPipeline

# Kokoro British-English voices (male + female) + two US voices for contrast.
VOICES = {
    "bm_george  — British male (grave)":     ("bm_george",   "b"),
    "bm_fable   — British male (lighter)":    ("bm_fable",    "b"),
    "bm_lewis   — British male":              ("bm_lewis",    "b"),
    "bm_daniel  — British male":              ("bm_daniel",   "b"),
    "bf_emma    — British female (warm)":     ("bf_emma",     "b"),
    "bf_isabella— British female":            ("bf_isabella", "b"),
    "bf_alice   — British female":            ("bf_alice",    "b"),
    "bf_lily    — British female":            ("bf_lily",     "b"),
    "am_michael — US male (contrast)":        ("am_michael",  "a"),
    "af_heart   — US female (contrast)":      ("af_heart",    "a"),
}
NONE = "— none (single voice) —"

DEFAULT_TEXT = (
    "There is a thing this book is about that this book cannot say.\n\n"
    "Not because the thing is vague, and not because the author is coy. Because of what "
    "the thing is. Every sentence that follows will be a sentence from somewhere — written "
    "by a particular mind, in a particular language, cut to a particular shape — and the "
    "thing the book is about is the one thing that is not from anywhere. You will feel the "
    "book reaching for it and stopping short, over and over, in every chapter."
)

SR = 24000
_pipes = {}
_voices = {}

def get_pipe(lang):
    if lang not in _pipes:
        _pipes[lang] = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    return _pipes[lang]

def get_voice(pipe, name):
    if name not in _voices:
        _voices[name] = pipe.load_voice(name)
    return _voices[name]


def synth(text, voice_label, blend_label, blend_amt, speed, pitch, gain_db):
    if not text or not text.strip():
        return None, "Enter some text first."
    try:
        name_a, lang = VOICES[voice_label]
        pipe = get_pipe(lang)
        voice = get_voice(pipe, name_a)
        recipe = "%s" % name_a
        if blend_label and blend_label != NONE:
            name_b = VOICES[blend_label][0]
            vb = get_voice(pipe, name_b)
            voice = (1.0 - blend_amt) * voice + blend_amt * vb
            recipe = "%.0f%% %s + %.0f%% %s" % ((1 - blend_amt) * 100, name_a,
                                                blend_amt * 100, name_b)
        parts = []
        for _, _, audio in pipe(text, voice=voice, speed=float(speed)):
            a = audio if isinstance(audio, np.ndarray) else audio.detach().cpu().numpy()
            parts.append(a.astype(np.float32))
        wav = np.concatenate(parts) if parts else np.zeros(1, dtype=np.float32)
        if abs(pitch) > 0.01:
            wav = librosa.effects.pitch_shift(y=wav, sr=SR, n_steps=float(pitch)).astype(np.float32)
        if abs(gain_db) > 0.01:
            wav = wav * (10.0 ** (gain_db / 20.0))
        peak = float(np.max(np.abs(wav))) if wav.size else 0.0
        if peak > 1.0:
            wav = wav / peak                      # prevent clipping
        secs = len(wav) / SR
        return (SR, wav), ("**%s** · speed %.2f · pitch %+.1f st · gain %+.0f dB  →  %.1fs"
                           % (recipe, speed, pitch, gain_db, secs))
    except Exception as e:
        return None, "Error: %s" % e


with gr.Blocks(title="Perspective — Voice Studio") as demo:
    gr.Markdown(
        "# Perspective — Voice Studio\n"
        "Audition and **tune** a voice for the audiobook. Native knobs: voice, blend, speed. "
        "Post-processed: pitch, gain. Edit the text to try any passage; when one lands, "
        "tell Clawd the recipe and he'll render the whole book."
    )
    text = gr.Textbox(value=DEFAULT_TEXT, lines=7, label="Text to read")
    with gr.Row():
        voice = gr.Dropdown(list(VOICES), value=list(VOICES)[0], label="Voice")
        blend_voice = gr.Dropdown([NONE] + list(VOICES), value=NONE, label="Blend with (2nd voice)")
        blend_amt = gr.Slider(0.0, 1.0, value=0.5, step=0.05, label="Blend amount (→ 2nd voice)")
    with gr.Row():
        speed = gr.Slider(0.55, 1.20, value=0.85, step=0.05, label="Speed (lower = slower/graver)")
        pitch = gr.Slider(-6.0, 6.0, value=0.0, step=0.5, label="Pitch (semitones; -=deeper)")
        gain = gr.Slider(-12.0, 12.0, value=0.0, step=1.0, label="Gain (dB)")
    btn = gr.Button("▶  Generate", variant="primary")
    out_audio = gr.Audio(label="Result", autoplay=True)
    status = gr.Markdown()
    btn.click(synth, [text, voice, blend_voice, blend_amt, speed, pitch, gain], [out_audio, status])

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, inbrowser=False)
