"""Procedural festive score + SFX for the Island Rangoli ad (numpy only).
Sitar (Karplus-Strong with jawari buzz), tanpura drone, dhol/bhangra groove,
bells, risers/whooshes, impacts and UI ticks, all locked to the timeline in index.html.
Usage: python3 music.py out.wav
"""
import sys, wave
import numpy as np

SR = 48000
DUR = 15.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
L = np.zeros(N); R = np.zeros(N)
REV = np.zeros(N)  # send to reverb (mono)

SA = 146.83  # D3
def hz(semi, octave=1): return SA * octave * 2 ** (semi / 12)

def add(sig, t, gain=1.0, pan=0.0, rev=0.2):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i] * gain
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    L[i:i + len(sig)] += sig * l * 1.414
    R[i:i + len(sig)] += sig * r * 1.414
    REV[i:i + len(sig)] += sig * rev

def env(n, a=0.005, d=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if d: e *= np.exp(-t / d)
    return e

def onepole(x, a):
    """Low-pass y[n] = y[n-1] + a*(x[n]-y[n-1]); vectorised via cumulative trick is unstable, so loop in chunks."""
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc += a * (x[i] - acc); y[i] = acc
    return y

def highpass(x): return np.diff(x, prepend=0)

# ---------------- instruments ----------------
def ks(f, dur, decay=0.996, bright=0.5, buzz=0.0):
    """Karplus-Strong pluck, block-vectorised."""
    n = int(dur * SR); P = max(2, int(SR / f))
    y = np.zeros(n + P + 1)
    exc = rng.uniform(-1, 1, P)
    exc = bright * exc + (1 - bright) * np.convolve(exc, np.ones(4) / 4, 'same')
    y[1:P + 1] = exc
    k = P + 1
    while k < len(y):
        e = min(k + P, len(y))
        y[k:e] = decay * 0.5 * (y[k - P:e - P] + y[k - P - 1:e - P - 1])
        k = e
    y = y[P + 1:P + 1 + n]
    if buzz:  # jawari: asymmetric soft clip adds the sitar sizzle
        y = np.tanh(y * (1 + buzz * 4)) + buzz * 0.3 * np.abs(y)
        y -= np.mean(y)
    return y * env(n, 0.002)

def sitar(semi, t, dur=0.9, gain=0.5, pan=0.15, octave=2):
    s = ks(hz(semi, octave), dur + 0.6, decay=0.9975, bright=0.8, buzz=0.6)
    s += 0.25 * ks(hz(semi, octave * 2), dur + 0.6, decay=0.997, bright=0.9, buzz=0.4)  # sympathetic
    fade = np.ones(len(s)); m = int(dur * SR); fade[m:] = np.linspace(1, 0, len(s) - m)
    add(s * fade, t, gain, pan, rev=0.35)

def pluck(semi, t, gain=0.25, pan=0.0, octave=2, dur=1.2):
    add(ks(hz(semi, octave), dur, decay=0.996, bright=0.4), t, gain, pan, rev=0.3)

def bell(f, t, gain=0.2, pan=0.0, d=1.6):
    n = int((d * 2) * SR); tt = np.arange(n) / SR
    s = sum(a * np.sin(2 * np.pi * f * m * tt) * np.exp(-tt / (d / (1 + m * 0.4))) for m, a in [(1, 1), (2.76, .5), (5.4, .25), (8.93, .12)] if f * m < 15000)
    add(s * env(n, 0.001), t, gain, pan, rev=0.6)

def dagga(t, gain=0.9):  # dhol bass side
    n = int(0.5 * SR); tt = np.arange(n) / SR
    f = 55 + 70 * np.exp(-tt * 28)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7)
    s += 0.25 * rng.uniform(-1, 1, n) * np.exp(-tt * 120)
    add(np.tanh(s * 1.6), t, gain, 0, rev=0.08)

def tilli(t, gain=0.35, pan=0.25):  # dhol treble stick
    n = int(0.18 * SR); tt = np.arange(n) / SR
    s = highpass(rng.uniform(-1, 1, n)) * np.exp(-tt * 45) * 0.6 + np.sin(2 * np.pi * 420 * tt) * np.exp(-tt * 40)
    add(s, t, gain, pan, rev=0.12)

def shaker(t, gain=0.08, pan=-0.3):
    n = int(0.09 * SR); tt = np.arange(n) / SR
    s = highpass(highpass(rng.uniform(-1, 1, n))) * np.minimum(1, tt / 0.01) * np.exp(-tt * 40)
    add(s, t, gain, pan, rev=0.05)

def chimes(t, gain=0.12):  # ghungroo / wind chime cluster
    for k in range(7):
        bell(2200 + rng.uniform(0, 2200), t + k * 0.035 + rng.uniform(0, .02), gain * rng.uniform(.4, 1), rng.uniform(-.7, .7), d=0.6)

def riser(t0, t1, gain=0.25):
    n = int((t1 - t0) * SR); tt = np.arange(n) / SR; p = tt / tt[-1]
    nz = rng.uniform(-1, 1, n); s = np.zeros(n)
    for a in (0.02, 0.06, 0.2):  # brighten progressively
        s += onepole(nz, a) * np.clip((p - (0 if a == .02 else .3 if a == .06 else .6)) * 2, 0, 1)
    f = 180 * 2 ** (p * 2.8)
    s = 0.6 * s + 0.35 * np.sin(2 * np.pi * np.cumsum(f) / SR)
    add(s * p ** 2, t0, gain, 0, rev=0.4)

def whoosh(t, dur=0.55, gain=0.35, pan=0.0):
    n = int(dur * SR); tt = np.arange(n) / SR; p = tt / dur
    nz = rng.uniform(-1, 1, n)
    s = onepole(nz, 0.03) * 0.6 + onepole(nz, 0.12) * 0.4 * np.sin(np.pi * p)
    add(s * np.sin(np.pi * p) ** 2 * 3, t, gain, pan, rev=0.3)

def impact(t, gain=1.0):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    f = 32 + 60 * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 2.2)
    s += 0.5 * onepole(rng.uniform(-1, 1, n), 0.08) * np.exp(-tt * 9)
    crash = highpass(rng.uniform(-1, 1, n)) * np.exp(-tt * 2.6) * 0.35
    add(np.tanh(s * 1.4), t, gain, 0, rev=0.25)
    add(crash, t, gain * 0.6, 0.2, rev=0.5)

def tick(t, f=1800, gain=0.12, pan=0.0):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    add(np.sin(2 * np.pi * f * tt) * np.exp(-tt * 90), t, gain, pan, rev=0.05)

def tap(t, gain=0.35):  # UI button press
    n = int(0.12 * SR); tt = np.arange(n) / SR
    f = 900 * np.exp(-tt * 25) + 300
    add(np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 40), t, gain, 0, rev=0.08)

def ching(t, gain=0.22):  # price-drop sparkle
    bell(2637, t, gain, -0.2, d=0.5); bell(3520, t + 0.06, gain * .8, 0.2, d=0.6)

def pad(chord, t0, t1, gain=0.06):
    n = int((t1 - t0 + 0.4) * SR); tt = np.arange(n) / SR
    s = np.zeros(n)
    for semi in chord:
        for det in (-0.08, 0.08):
            f = hz(semi, 2) * 2 ** (det / 12)
            for h in range(1, 7): s += np.sin(2 * np.pi * f * h * tt + h) / h ** 1.6
    e = np.minimum(1, tt / 0.25) * np.clip((t1 - t0 + 0.4 - tt) / 0.4, 0, 1)
    add(s * e, t0, gain / len(chord), 0, rev=0.5)

def tanpura(t0, t1, gain=0.18):
    t = t0; seq = [(7, 1), (12, 1), (12, 1), (0, 1)]  # Pa Sa' Sa' Sa
    k = 0
    while t < t1:
        semi, o = seq[k % 4]
        s = ks(hz(semi, o), 2.4, decay=0.9993, bright=0.3, buzz=0.9)
        add(s, t, gain * (0.8 if k % 4 == 3 else 0.6), (-.4, -.1, .1, .4)[k % 4], rev=0.5)
        t += 0.5; k += 1

# ---------------- arrangement (15s cut) ----------------
BEAT = 0.5
tanpura(0.0, 14.6)

def groove(t0, t1, full=True):
    pat = "D.tD.tDt" if full else "D..t..t."
    t = t0; k = 0
    while t < t1 - 1e-6:
        c = pat[k % 8]
        if c == 'D': dagga(t, 0.85 if k % 8 == 0 else 0.6)
        if c == 't' or (full and k % 2): tilli(t, 0.32 if c == 't' else 0.14, pan=0.25 if k % 2 else -0.15)
        shaker(t); shaker(t + BEAT / 4, 0.05)
        t += BEAT / 2; k += 1

def melody(notes, t0, gain=0.42, pan=0.15, octave=2):
    for beat, semi, d in notes: sitar(semi, t0 + beat * BEAT, d * BEAT, gain, pan, octave)

# S1 bloom (0–2): chimes, rising sitar arpeggio, emblem bell
chimes(0.05, 0.10)
for i, s in enumerate([0, 4, 7, 12, 16, 19]):
    sitar(s, 0.12 + i * 0.15, 0.5, 0.32, pan=-0.3 + i * 0.12)
bell(hz(12, 4), 1.25, 0.25)
bell(hz(19, 4), 1.45, 0.18)
for i in range(8): tick(1.4 + i * 0.025, 2400 + i * 120, 0.03)
riser(1.2, 1.98, 0.22)
whoosh(1.75, 0.55, 0.45)

# S2 Mega Festive Sale · Live Now (2–4.5)
impact(2.0, 0.55); chimes(2.0, 0.08)
groove(2.0, 4.5)
pad([0, 4, 7], 2.0, 3.5); pad([-3, 2, 7], 3.5, 4.5)
melody([(0, 0, 1), (1, 2, 1), (2, 4, 1), (3, 7, 1.5), (4.5, 4, .5)], 2.0)
for i, t in enumerate([2.4, 2.53, 2.66]): bell(hz(12 + [0, 4, 7][i], 4), t, 0.12, -0.4 + i * .4, d=.8)
whoosh(2.9, 0.45, 0.25, -0.3)  # ribbon
riser(3.6, 4.48, 0.32)
whoosh(4.15, 0.4, 0.3)

# S3 Deep Dwar FLAT 60% OFF (4.5–7.4)
dagga(4.5, 0.9); chimes(4.5, 0.1); bell(hz(12, 4), 4.5, 0.2)
impact(5.0, 1.0)  # badge slam
for i in range(14):  # counter roll 0→60
    tick(5.0 + 0.5 * (1 - (1 - i / 13) ** 2), 1400 + i * 90, 0.07, pan=(i % 2 - .5) * .4)
bell(hz(24, 2), 5.5, 0.3); chimes(5.5, 0.1)
ching(5.75)  # Rs. 899 struck through
groove(4.5, 7.25)
pad([0, 4, 7], 4.5, 6.5); pad([5, 9, 12], 6.5, 7.5)
melody([(0, 12, 1), (1, 11, .5), (1.5, 9, .5), (2, 7, 1), (3, 9, .5), (3.5, 11, .5), (4, 12, 1), (5, 14, 1)], 4.5)
whoosh(7.2, 0.6, 0.45, 0.3)  # page wipe

# S4 best sellers (7.5–10)
groove(7.5, 10.0, full=False)
pad([0, 4, 7], 7.5, 9.0); pad([5, 9, 12], 9.0, 10.0)
bell(hz(12, 4), 7.7, 0.12)
F0, FSTEP = 8.1, 1.0
for i in range(2):
    f = F0 + i * FSTEP
    if i: whoosh(f - 0.32, 0.32, 0.16, 0.4)
    tick(f + 0.06, 900, 0.08)   # strike-through
    ching(f + 0.27)             # sale price pops
    tap(f + 0.51, 0.3)          # QUICK ADD
    pluck([0, 7][i], f + 0.62, 0.22, 0.1, octave=4)
for b in range(5): pluck([0, 7, 12, 7][b % 4], 7.5 + b * BEAT, 0.12, -0.3)
whoosh(9.9, 0.5, 0.45, -0.3)

# S5 lifestyle (10–12.5)
groove(10.0, 12.4)
pad([5, 9, 12], 10.0, 11.25); pad([7, 11, 14], 11.25, 12.5)
melody([(0, 7, 1), (1, 9, 1), (2, 12, 2)], 10.3, 0.4)
for i in range(5): bell(hz([12, 14, 16, 19, 24][i], 4), 10.85 + i * 0.1, 0.11, -0.5 + i * 0.25, d=.7)
riser(11.7, 12.48, 0.3)

# S6 end card (12.5–15)
impact(12.5, 0.8); chimes(12.55, 0.12)
groove(12.5, 14.0)
pad([0, 4, 7], 12.5, 14.6, 0.07)
melody([(0, 12, 1), (1, 14, .5), (1.5, 16, .5)], 12.5, 0.4)
tap(13.82, 0.35); ching(13.95, 0.2); tap(14.42, 0.3); ching(14.55, 0.18)
for k, s in enumerate([0, 7, 12, 16, 19]): sitar(s, 14.0 + k * 0.025, 0.8, 0.3, -0.4 + k * .2)  # final strum
dagga(14.0, 0.9); bell(hz(24, 2), 14.0, 0.3)

# ---------------- reverb + master ----------------
ir_n = int(1.9 * SR); tt = np.arange(ir_n) / SR
ir = rng.uniform(-1, 1, ir_n) * np.exp(-tt * 3.2)
ir = onepole(ir, 0.25); ir /= np.sqrt(np.sum(ir ** 2))
nfft = 1 << int(np.ceil(np.log2(N + ir_n)))
wet = np.fft.irfft(np.fft.rfft(REV, nfft) * np.fft.rfft(ir, nfft), nfft)[:N] * 0.5
dl = int(0.011 * SR)
L += wet; R[dl:] += wet[:-dl]

fade = np.ones(N); fn = int(0.45 * SR); fade[-fn:] = np.linspace(1, 0, fn) ** 2
mix = np.stack([L, R], 1) * fade[:, None]
mix -= mix.mean(0)
mix = np.tanh(mix / np.max(np.abs(mix)) * 1.6) / np.tanh(1.6) * 0.95  # gentle bus saturation/limit
pcm = (mix * 32767).astype('<i2')
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'music.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
print('wrote', len(pcm) / SR, 's')
