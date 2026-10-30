"""Trilhas originais (sem direitos autorais) para os vídeos do POS, sintetizadas em numpy.

A: house/pop animado 124 BPM (opção 1).  B: groove tropical/lo-fi 100 BPM (opção 2).
Uso: python3 musica.py A saida.wav duracao_s
"""
import sys, numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 44100
T0 = 2.2
rng = np.random.default_rng(7)

def nota(n):  # número MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def env(n, a=0.005, d=0.1, s=0.6, r=0.1, dur=None):
    dur = dur or n / SR
    t = np.arange(n) / SR
    e = np.where(t < a, t / a, np.where(t < a + d, 1 - (1 - s) * (t - a) / d, s))
    rel = max(dur - r, 0)
    e = np.where(t > rel, e * np.clip(1 - (t - rel) / r, 0, 1), e)
    return e

def lp(x, fc, ordem=2):
    return sosfilt(butter(ordem, fc, "low", fs=SR, output="sos"), x)

def hp(x, fc, ordem=2):
    return sosfilt(butter(ordem, fc, "high", fs=SR, output="sos"), x)

def kick(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 50 + 120 * np.exp(-t * 35)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7)
    x += 0.3 * np.exp(-t * 300) * rng.standard_normal(n) * 0.3
    return x

def clap(dur=0.25):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    e = np.exp(-t * 18) * (1 + 0.6 * (np.sin(2 * np.pi * 90 * t) > 0) * (t < 0.03))
    return hp(lp(x * e, 6000), 900) * 0.8

def hat(dur=0.06, aberto=False):
    n = int((0.22 if aberto else dur) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (14 if aberto else 70)) * 0.35

def saw(f, n, det=0.0):
    t = np.arange(n) / SR
    x = 0
    for d in (-det, 0, det) if det else (0,):
        ph = (t * f * (1 + d)) % 1.0
        x = x + (2 * ph - 1)
    return x / (3 if det else 1)

def pluck(f, dur, brilho=3000):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 12) + 0.25 * np.sin(2 * np.pi * 3 * f * t) * np.exp(-t * 20)
    return lp(x * np.exp(-t * 6), brilho)

def marimba(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 4 * f * t) * np.exp(-t * 30)) * np.exp(-t * 9)

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    out = np.zeros(n); bloco = 2048
    for i in range(0, n, bloco):
        fc = 400 + 9000 * (i / n) ** 2
        out[i:i + bloco] = lp(x[i:i + bloco], fc)
    return out * (t / dur) ** 2 * 0.5

def impacto():
    k = kick(0.9) * 1.2
    n = len(k); t = np.arange(n) / SR
    boom = np.sin(2 * np.pi * 42 * t) * np.exp(-t * 3)
    return k + 0.6 * boom + lp(rng.standard_normal(n), 1500) * np.exp(-t * 6) * 0.4

def por(trilha, som, seg, ganho=1.0):
    i = int(seg * SR)
    if i >= len(trilha): return
    j = min(len(trilha), i + len(som))
    trilha[i:j] += som[:j - i] * ganho

def mestre(L, R, dur, alvo_rms=0.16):
    x = np.stack([L, R], 1)
    x = np.tanh(x * 1.3) / np.tanh(1.3)          # saturação leve / limitador suave
    rms = np.sqrt(np.mean(x ** 2)); x *= alvo_rms / max(rms, 1e-9)
    x = np.clip(x, -0.98, 0.98)
    n = len(x); f_in, f_out = int(0.05 * SR), int(1.2 * SR)
    x[:f_in] *= np.linspace(0, 1, f_in)[:, None]; x[-f_out:] *= np.linspace(1, 0, f_out)[:, None]
    return x

def trilha_A(dur):
    """House/pop 124 BPM em Lá menor: Am F C G."""
    bpm = 124; b = 60 / bpm; n = int(dur * SR) + SR
    bat = np.zeros(n); bx = np.zeros(n); acL = np.zeros(n); acR = np.zeros(n); fx = np.zeros(n)
    duck = np.ones(n)
    prog = [(57, [69, 72, 76]), (53, [65, 69, 72]), (48, [64, 67, 72]), (55, [67, 71, 74])]
    beats = int(dur / b) + 2
    for k in range(beats):
        t = k * b
        intro = t < T0  # gancho: só pad + riser
        if not intro:
            por(bat, kick(), t, 1.0)
            i = int(t * SR); m = min(n, i + int(0.18 * SR))
            duck[i:m] = np.minimum(duck[i:m], 0.35 + 0.65 * np.linspace(0, 1, m - i))
            if k % 2 == 1: por(bat, clap(), t, 0.55)
            por(bat, hat(aberto=True), t + b / 2, 0.5)
            por(bat, hat(), t + b / 4, 0.25); por(bat, hat(), t + 3 * b / 4, 0.25)
        bassn, acorde = prog[(k // 4) % 4]
        # baixo em colcheias (offbeat)
        if not intro:
            for off in (0.5,):
                nb = int(b * 0.45 * SR)
                s = lp(saw(nota(bassn - 12), nb), 700) * env(nb, 0.003, 0.08, 0.5, 0.05)
                por(bx, s, t + off * b, 0.55)
        # acordes: stabs no contratempo ou pad no gancho
        if intro:
            if k % 4 == 0:
                nb = int(4 * b * SR)
                pad = sum(lp(saw(nota(m), nb, 0.004), 1200) for m in acorde) * env(nb, 0.6, 0.3, 0.8, 0.6)
                por(acL, pad, t, 0.12); por(acR, pad, t, 0.12)
        else:
            for off in (0.5, 1.5) if k % 2 == 0 else ():
                nb = int(0.22 * SR)
                st = sum(lp(saw(nota(m), nb, 0.006), 2600) for m in acorde) * env(nb, 0.004, 0.12, 0.3, 0.06)
                por(acL, st, t + off * b, 0.14); por(acR, st, t + off * b + 0.008, 0.14)
        # melodia em pluck a cada 2 compassos
        if not intro and (k % 8) in (0, 3, 6):
            mel = acorde[[2, 1, 0][(k % 8) // 3]] + 12
            p = pluck(nota(mel), b * 1.2)
            por(acL, p, t, 0.10); por(acR, p, t + 0.012, 0.10)
    por(fx, riser(T0 - 0.15), 0.05, 0.9)
    por(fx, impacto(), T0, 0.7)
    L = bat + bx * duck + acL * duck + fx
    R = bat + bx * duck + acR * duck + fx
    return mestre(L[:int(dur * SR)], R[:int(dur * SR)], dur), b

def trilha_B(dur):
    """Groove tropical / lo-fi 100 BPM em Ré maior: D Bm G A, marimba + baixo redondo + shaker."""
    bpm = 100; b = 60 / bpm; n = int(dur * SR) + SR
    bat = np.zeros(n); bx = np.zeros(n); mL = np.zeros(n); mR = np.zeros(n); fx = np.zeros(n)
    prog = [(50, [62, 66, 69]), (47, [59, 62, 66]), (43, [55, 59, 62]), (45, [57, 61, 64])]
    beats = int(dur / b) + 2
    padrao_kick = [0, 1.5, 2.5]          # dembow leve dentro de 4 tempos (em tempos)
    for k in range(0, beats, 4):
        t0 = k * b
        bassn, acorde = prog[(k // 4) % 4]
        intro = t0 < T0
        if not intro:
            for p in padrao_kick: por(bat, kick(0.3), t0 + p * b, 0.9)
            for p in (1, 3): por(bat, clap(0.2), t0 + p * b, 0.4)
            for s in range(16):
                ac = 0.22 if s % 2 else 0.12
                por(bat, hat(0.04), t0 + s * b / 4 + (0.012 if s % 2 else 0), ac)
            for p, d in ((0, 0.9), (1.5, 0.45), (2.5, 0.9), (3.5, 0.4)):
                nb = int(d * b * SR); tt = np.arange(nb) / SR
                s = np.sin(2 * np.pi * nota(bassn - 12) * tt) + 0.2 * np.sin(2 * np.pi * nota(bassn) * tt)
                por(bx, s * env(nb, 0.005, 0.1, 0.7, 0.06), t0 + p * b, 0.5)
        # marimba arpejada (em semicolcheias sincopadas)
        arp = [0, 2, 1, 2, 0, 1, 2, 1]
        for s, ix in enumerate(arp):
            if intro and s % 2: continue
            f = nota(acorde[ix] + 12)
            m = marimba(f, 0.5)
            pos = t0 + s * b / 2 + (b / 4 if s in (3, 6) else 0)
            g = 0.16 if not intro else 0.12
            por(mL, m, pos, g * (1.1 if ix != 1 else 0.8)); por(mR, m, pos + 0.01, g * (0.8 if ix != 1 else 1.1))
        # pad quente
        nb = int(4 * b * SR)
        pad = sum(lp(saw(nota(m), nb, 0.003), 900) for m in acorde) * env(nb, 0.4, 0.3, 0.7, 0.5)
        por(mL, pad, t0, 0.06); por(mR, pad, t0, 0.06)
    por(fx, riser(T0 - 0.15), 0.05, 0.7)
    por(fx, impacto(), T0, 0.55)
    L = bat + bx + mL + fx; R = bat + bx + mR + fx
    return mestre(L[:int(dur * SR)], R[:int(dur * SR)], dur), b

if __name__ == "__main__":
    qual, saida, dur = sys.argv[1], sys.argv[2], float(sys.argv[3])
    if len(sys.argv) > 4: T0 = float(sys.argv[4])
    x, b = (trilha_A if qual == "A" else trilha_B)(dur)
    wavfile.write(saida, SR, (x * 32767).astype(np.int16))
    print(saida, f"{dur}s", f"tempo={b:.4f}s")
