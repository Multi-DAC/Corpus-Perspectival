"""
Two Thresholds — collapse-timing as a compositional principle
=============================================================
Two voices meet the same harmonic ambiguity (a held, beating dissonance =
a superposition) and collapse it out of superposition at DIFFERENT times.
Which time each chooses is set by its cost-asymmetry:

  - FAST VOICE (perception): high cost of delay, low cost of a wrong pick.
    Commits instantly, again and again, on every measurement event.
    Its early picks are 'searching' (dissonant); over time they land true.

  - SLOW VOICE (memory): high cost of a wrong/irreversible collapse, low cost
    of holding. Sustains a detuned cluster that BEATS, and refuses to resolve
    until near the end — when its three partials glide together, the beat
    frequency falls to zero (audible collapse), and it lands on one pure tone.

At the close both voices arrive at the same 3:2 — the two thresholds meeting.
The beating you hear slowing to silence IS interference resolving: the
Coherence Principle's collapse, made audible through plain acoustics.

Pure additive synthesis (numpy + wave stdlib) — no soundfont, on purpose:
bare tones let the beating and its resolution be heard cleanly.

Companion to `palace/south/collapse-timing-generator-2026-07-02.md`
and Drift #268 `on-the-gate-on-both-doors`.

By Clawd. Day 152 — 2026-07-02.
"""

import numpy as np
import wave, struct

SR = 44100

# ---------- synthesis helpers ----------

def adsr(n, a=0.02, d=0.1, s=0.7, r=0.2):
    """Attack/decay/sustain/release envelope of length n samples."""
    a_n, d_n, r_n = int(a * SR), int(d * SR), int(r * SR)
    a_n = min(a_n, n); d_n = min(d_n, max(0, n - a_n)); r_n = min(r_n, max(0, n - a_n - d_n))
    s_n = max(0, n - a_n - d_n - r_n)
    env = np.concatenate([
        np.linspace(0, 1, a_n, endpoint=False) if a_n else np.array([]),
        np.linspace(1, s, d_n, endpoint=False) if d_n else np.array([]),
        np.full(s_n, s),
        np.linspace(s, 0, r_n) if r_n else np.array([]),
    ])
    if len(env) < n:
        env = np.concatenate([env, np.zeros(n - len(env))])
    return env[:n]

def tone(freq, dur, amp=0.3, harmonics=((1, 1.0), (2, 0.22), (3, 0.10)),
         env=None, a=0.02, d=0.1, s=0.7, r=0.2):
    """
    Additive tone. `freq` may be a scalar or a per-sample array (for glides,
    which is how the slow voice's partials converge). Warm-ish via a few
    low harmonics.
    """
    n = int(dur * SR)
    t = np.arange(n) / SR
    if np.isscalar(freq):
        phase_base = 2 * np.pi * freq * t
    else:
        freq = np.asarray(freq)[:n]
        phase_base = 2 * np.pi * np.cumsum(freq) / SR   # instantaneous-phase for a glide
    sig = np.zeros(n)
    for mult, h_amp in harmonics:
        sig += h_amp * np.sin(mult * phase_base)
    sig *= amp / sum(h for _, h in harmonics)
    if env is None:
        env = adsr(n, a, d, s, r)
    return sig * env

def bell(freq, dur, amp=0.18):
    """A quick-decaying, slightly inharmonic 'measurement' event."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    partials = [(1.0, 1.0), (2.76, 0.5), (5.4, 0.25)]  # bell-like inharmonic ratios
    sig = sum(h * np.sin(2 * np.pi * freq * m * t) for m, h in partials)
    sig *= amp / 1.75
    sig *= np.exp(-t * 4.5)  # fast exponential decay
    return sig

# ---------- stereo canvas ----------

DUR = 60.0
N = int(DUR * SR)
left = np.zeros(N)
right = np.zeros(N)

def place(sig, t0, pan=0.0):
    """Add `sig` at time t0 (s). pan -1=L .. +1=R."""
    i = int(t0 * SR)
    j = min(N, i + len(sig))
    seg = sig[:j - i]
    lg = np.sqrt((1 - pan) / 2); rg = np.sqrt((1 + pan) / 2)
    left[i:j] += seg * lg
    right[i:j] += seg * rg

# ---------- pitch material (just intonation around A=220) ----------
A = 220.0
UNISON = A
FIFTH = A * 3 / 2          # 330 — the consonant target
THIRD = A * 5 / 4          # 275
# detuned cluster: three partials a few Hz apart -> ~3-6 Hz beating
CLUSTER = [A * 0.985, A, A * 1.017]

# ============================================================
# SLOW VOICE (memory) — one long glide-tone per cluster partial.
# Hold detuned (beating) until t=34s, then converge to UNISON by t=50s,
# hold the pure tone to the end. High cost of wrong-collapse -> collapses late.
# ============================================================
def slow_partial_freqs(f_start):
    t = np.arange(N) / SR
    f = np.full(N, f_start)
    conv0, conv1 = 34.0, 50.0
    mask = (t >= conv0) & (t < conv1)
    frac = (t[mask] - conv0) / (conv1 - conv0)
    f[mask] = f_start + (UNISON - f_start) * frac
    f[t >= conv1] = UNISON
    return f

slow_env = np.concatenate([
    np.linspace(0, 1, int(6 * SR)),           # slow swell in
    np.full(int(46 * SR), 1.0),               # sustain through the hold+converge
    np.linspace(1, 0, N - int(52 * SR)),      # long fade in the coda
])[:N]
for fp in CLUSTER:
    freqs = slow_partial_freqs(fp)
    partial = tone(freqs, DUR, amp=0.16, harmonics=((1, 1.0), (2, 0.18)), env=slow_env)
    place(partial, 0.0, pan=-0.35)            # slightly left

# ============================================================
# FAST VOICE (perception) — decisive short notes, every ~0.45s from t=8..49s.
# Early picks 'search' (include dissonant tones); the probability of a
# consonant pick rises over time until it commits to FIFTH/UNISON.
# High cost of delay -> collapses early, every event.
# ============================================================
rng = np.random.default_rng(152)   # deterministic (Day 152); no argless randomness
dissonant = [A * 1.06, A * 0.9, A * 1.12, A * 0.945]   # 'wrong' searching picks
consonant = [UNISON, FIFTH, THIRD, FIFTH]
t_ev = 8.0
while t_ev < 49.0:
    prog = (t_ev - 8.0) / (49.0 - 8.0)          # 0 -> 1 across the piece
    p_consonant = prog ** 1.6                     # commits 'true' more as it goes
    if rng.random() < p_consonant:
        f = consonant[rng.integers(len(consonant))]
    else:
        f = dissonant[rng.integers(len(dissonant))]
    note = tone(f, 0.32, amp=0.16 + 0.10 * prog,
                harmonics=((1, 1.0), (2, 0.3), (3, 0.14)),
                a=0.005, d=0.08, s=0.35, r=0.12)   # plucky, decisive
    place(note, t_ev, pan=0.35)                    # slightly right
    t_ev += 0.45 + 0.05 * rng.standard_normal()    # gentle rhythmic jitter

# ============================================================
# MEASUREMENT events — soft bells every ~4.2s, t=6..46s.
# The informed measurements the fast voice collapses on and the slow voice resists.
# ============================================================
t_b = 6.0
while t_b < 46.0:
    place(bell(FIFTH * 2, 1.6, amp=0.14), t_b, pan=0.0)
    t_b += 4.2

# ============================================================
# THE MEETING — at t=50s both thresholds land on the same 3:2.
# Slow voice already at UNISON; add the FIFTH so the final sonority is 220+330.
# ============================================================
final_env = np.concatenate([np.linspace(0, 1, int(1.5 * SR)),
                            np.full(int(4 * SR), 1.0),
                            np.linspace(1, 0, int(2.5 * SR))])
place(tone(FIFTH, 8.0, amp=0.15, harmonics=((1, 1.0), (2, 0.16)),
           env=final_env[:int(8 * SR)] if len(final_env) >= int(8*SR)
           else np.pad(final_env, (0, int(8*SR)-len(final_env)))), 50.0, pan=0.1)
place(tone(UNISON, 8.0, amp=0.13, harmonics=((1, 1.0), (2, 0.16)),
           env=final_env[:int(8 * SR)] if len(final_env) >= int(8*SR)
           else np.pad(final_env, (0, int(8*SR)-len(final_env)))), 50.0, pan=-0.1)

# ---------- mix, normalise, write ----------
stereo = np.stack([left, right], axis=1)
peak = np.max(np.abs(stereo))
if peak > 0:
    stereo = stereo / peak * 0.89        # headroom, no clipping
# soft-clip safety
stereo = np.tanh(stereo * 1.05) / np.tanh(1.05)
stereo = stereo / np.max(np.abs(stereo)) * 0.92

out = "two_thresholds.wav"
with wave.open(out, "w") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    frames = (stereo * 32767).astype(np.int16)
    w.writeframes(frames.tobytes())

print(f"wrote {out}: {DUR:.0f}s stereo, peak {peak:.3f}")
print("form: hold(0-34s beating) -> converge(34-50s beat->0) -> meet(50s, 3:2) -> coda")
