"""Compositor quadro a quadro das duas opções do vídeo POS @facilweb (1080x1920, 24 fps).

Uso: python3 render.py 1|2 reels|stories saida.mp4 [--preview t1,t2,...]
"""
import math, os, subprocess, sys
import cv2, numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from edicao import FPS, SEGS, TEASER, FREEZE_TEASER, OUTRO, frames_fonte

D = "/home/claude/video-pos"
C2 = f"{D}/camadas2"
W, H = 1080, 1920

# ---------------- utilidades ----------------
_cache = {}
def png(nome):
    if nome not in _cache:
        im = cv2.imread(f"{C2}/{nome}.png", cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        _cache[nome] = im
    return _cache[nome]

def colar(dst, rgba, x, y, alpha=1.0, escala=1.0, centro=False):
    if alpha <= 0.01 or escala <= 0.01: return
    im = rgba
    if abs(escala - 1) > 1e-3:
        im = cv2.resize(rgba, None, fx=escala, fy=escala, interpolation=cv2.INTER_LINEAR if escala > 1 else cv2.INTER_AREA)
    h, w = im.shape[:2]
    if centro: x, y = x - w / 2, y - h / 2
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1: return
    sub = im[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (sub[:, :, 3:4].astype(np.float32) / 255) * alpha
    reg = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (reg * (1 - a) + sub[:, :, :3].astype(np.float32) * a).astype(np.uint8)

def ease_out(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def ease_back(x, s=1.7):
    x = min(max(x, 0), 1); x -= 1; return x * x * ((s + 1) * x + s) + 1
def janela(t, a, d=0.25):  # 0..1 de entrada
    return min(max((t - a) / d, 0), 1)

def lut_grade():
    x = np.arange(256) / 255.0
    y = x + 0.20 * x * (1 - x) ** 3 * 4             # levanta sombras
    s = 0.5 - 0.5 * np.cos(np.pi * y); y = 0.7 * y + 0.3 * s  # contraste nos meios-tons
    return np.clip(y * 255, 0, 255).astype(np.uint8)
LUT = lut_grade()

_fr = {}
def quadro_sr(idx):
    """Frame da super-resolução (1440x2560) com correção de cor e sombras."""
    if idx not in _fr:
        if len(_fr) > 6: _fr.pop(next(iter(_fr)))
        p = f"{D}/sr/{idx:05d}.jpg"
        im = cv2.imread(p)
        if im is None:  # fallback (só para prévia): original ampliado
            cap = cv2.VideoCapture(f"{D}/in/original.mp4"); cap.set(cv2.CAP_PROP_POS_FRAMES, idx); _, im = cap.read()
            im = cv2.resize(im, (1440, 2560), interpolation=cv2.INTER_LANCZOS4)
        lab = cv2.cvtColor(im, cv2.COLOR_BGR2LAB)
        lab[:, :, 0] = cv2.LUT(lab[:, :, 0], LUT)
        im = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        hsv = cv2.cvtColor(im, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.12, 0, 255)
        _fr[idx] = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    return _fr[idx]

def zoom_crop(im, z, cx=720, cy=1280, w=W, h=H):
    sh, sw = im.shape[:2]
    cw, ch = sw / z, sh / z
    x0 = min(max(cx - cw / 2, 0), sw - cw); y0 = min(max(cy - ch / 2, 0), sh - ch)
    M = np.float32([[w / cw, 0, -x0 * w / cw], [0, h / ch, -y0 * h / ch]])
    return cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_AREA if z < 1.5 else cv2.INTER_CUBIC)

def gradiente(h, de, ate, cor=(85, 29, 4)):
    a = np.linspace(de, ate, h)[:, None, None]
    return np.dstack([np.broadcast_to(np.array(cor, np.uint8), (h, W, 3)), np.broadcast_to((a * 255).astype(np.uint8), (h, W, 1))]).copy()

# ---------------- tempos ----------------
FONTE = frames_fonte()
N_PRINC = len(FONTE)
T0 = (int(round((TEASER[1] - TEASER[0]) * FPS)) + int(FREEZE_TEASER * FPS)) / FPS
def janelas_passos():
    js, t = [], T0
    for a, b, v, p in SEGS:
        d = int(round((b - a) / v * FPS)) / FPS
        if js and js[-1][0] == p: js[-1][2] = t + d
        else: js.append([p, t, t + d])
        t += d
    return js, t
PASSOS, TFIM = janelas_passos()
TOTAL = TFIM + OUTRO
N = int(round(TOTAL * FPS))

def snap(t, b):  # alinha ao tempo da música
    return round(t / b) * b

def idx_em(t):
    k = min(int(t * FPS), N_PRINC - 1)
    return FONTE[k]

# ---------------- opção 1: tela cheia + tipografia cinética ----------------
class Op1:
    BATIDA = 60 / 124
    def __init__(self, cta):
        self.cta = cta
        self.top = gradiente(760, 0.85, 0.0); self.bot = gradiente(520, 0.0, 0.75)
        self.passos = [(p, snap(a, self.BATIDA / 2), b) for p, a, b in PASSOS]
        self.passos[0] = (1, T0, self.passos[0][2])

    def passo_em(self, t):
        if not (T0 <= t < TFIM): return None, None
        atual = (None, None)
        for p, a, b in self.passos:
            if a <= t: atual = (p, a)
        return atual

    def quadro(self, f):
        t = f / FPS
        tt = min(t, TFIM - 1 / FPS)
        p, ta = self.passo_em(t)
        # zoom: soco no início de cada passo + respiração
        z = 1.0 + 0.025 * math.sin(t * 0.9)
        if ta is not None:
            dt = t - ta
            z += 0.13 * (ease_out(dt / 0.18) if dt < 0.18 else math.exp(-(dt - 0.18) * 2.2))
        if t < T0: z += 0.04 * t / T0
        cy = 1250
        if p == 5 or t < T0: cy = 1200
        img = zoom_crop(quadro_sr(idx_em(tt)), z, cy=cy)
        # tremida no impacto
        if T0 <= t < T0 + 0.25:
            k = (1 - (t - T0) / 0.25) * 14
            M = np.float32([[1, 0, k * math.sin(t * 90)], [0, 1, k * math.cos(t * 70)]])
            img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        colar(img, self.top, 0, 0); colar(img, self.bot, 0, H - 520)
        if t < T0:
            img = (img * 0.55).astype(np.uint8)
            for i, ti in enumerate((0.12, 0.45, 0.78)):
                e = janela(t, ti, 0.22)
                if e > 0: colar(img, png(f"gancho1_{i}"), W / 2, 600 + i * 160, e, 1.35 - 0.35 * ease_back(e), True)
            e = janela(t, 1.2, 0.25)
            colar(img, png("gancho1_sub"), W / 2, 1110, e, 0.8 + 0.2 * ease_back(e), True)
        elif t < TFIM:
            dt = t - ta
            e = ease_back(min(dt / 0.3, 1))
            pal = png(f"p1_pal{p}"); fit = min(1.0, 1040 / pal.shape[1])
            colar(img, pal, 20 - (1 - e) * 120, 360, min(dt / 0.15, 1), (0.85 + 0.15 * e) * fit)
            e2 = janela(t, ta + 0.18, 0.25)
            colar(img, png(f"p1_sub{p}"), 30, 590 + (1 - ease_out(e2)) * 40, e2)
            colar(img, png(f"p1_chip{p}"), W - 210, 210, min(dt / 0.2, 1))
            # barra de progresso dos 5 passos
            x0, y0, larg, gap = 70, 1700, 176, 12
            for i in range(5):
                xa = x0 + i * (larg + gap)
                sub = img[y0:y0 + 12, xa:xa + larg]; img[y0:y0 + 12, xa:xa + larg] = (sub * 0.6 + 255 * 0.4).astype(np.uint8)
                pa, aa, bb = self.passos[i]
                frac = 1.0 if t >= bb else max(0.0, (t - aa) / (bb - aa)) if t >= aa else 0
                if frac > 0: cv2.rectangle(img, (xa, y0), (xa + int(larg * frac), y0 + 12), (63, 198, 141), -1)
        # flash branco nas viradas
        for vt in [T0] + [a for _, a, _ in self.passos[1:]]:
            if 0 <= t - vt < 0.12:
                a = 0.55 * (1 - (t - vt) / 0.12); img = (img * (1 - a) + 255 * a).astype(np.uint8)
        # selo sempre
        if t < TFIM + 0.3: colar(img, png("selo"), 10, 160)
        # encerramento
        if t >= TFIM:
            dt = t - TFIM; e = ease_out(dt / 0.45)
            colar(img, png("final1"), 0, H * (1 - e))
            e2 = janela(t, TFIM + 0.55, 0.3)
            pulso = 1 + 0.05 * math.sin((t - TFIM) * 2 * math.pi / self.BATIDA) * (e2 >= 1)
            if self.cta: colar(img, png(self.cta), W / 2, 1420, e2, (0.6 + 0.4 * ease_back(e2)) * pulso, True)
            colar(img, png("handle"), W / 2, 1580 if self.cta else 1460, janela(t, TFIM + 0.6, 0.3), 1 if self.cta else 1.25, True)
        return img

# ---------------- opção 2: vitrine com lupa e moedas 3D ----------------
class Op2:
    BATIDA = 60 / 100
    CW, CH, R = 760, 1351, 48
    LUPAS = [  # (passo, quando dentro do passo (0..1), tempo fonte, recorte x0,y0,x1,y1 no frame 1440x2560)
        (3, 0.40, 24.0, (330, 670, 1080, 1110), 1),
        (4, 0.45, 36.0, (160, 700, 830, 1340), 2),
        (5, 0.15, 45.0, (0, 330, 820, 900), 3)]
    def __init__(self, cta):
        self.cta = cta
        self.fundo = cv2.imread(f"{C2}/fundo2.png")[:H, :W]
        m = np.zeros((self.CH, self.CW), np.uint8)
        cv2.rectangle(m, (self.R, 0), (self.CW - self.R, self.CH), 255, -1); cv2.rectangle(m, (0, self.R), (self.CW, self.CH - self.R), 255, -1)
        for cx, cy in ((self.R, self.R), (self.CW - self.R, self.R), (self.R, self.CH - self.R), (self.CW - self.R, self.CH - self.R)):
            cv2.circle(m, (cx, cy), self.R, 255, -1, cv2.LINE_AA)
        self.mask = cv2.GaussianBlur(m, (3, 3), 0)
        B = 10; mb = cv2.copyMakeBorder(m, B, B, B, B, cv2.BORDER_CONSTANT, 0)
        self.borda = cv2.dilate(mb, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * B + 1, 2 * B + 1)))
        self.B = B
        sh = cv2.GaussianBlur(cv2.copyMakeBorder(self.borda, 80, 80, 80, 80, cv2.BORDER_CONSTANT, 0), (0, 0), 30)
        self.sombra = sh
        rng = np.random.default_rng(4)
        self.sprites = []
        for i in range(9):
            nome = f"sprites/{['moeda0','moeda1','moeda2','moeda3','esfera0','esfera1'][i % 6]}"
            self.sprites.append((nome, rng.uniform(40, 1040), rng.uniform(250, 1850), rng.uniform(0.35, 0.75), rng.uniform(0, 6), rng.uniform(0.5, 1.1)))
        self.frente = [("sprites/moeda0", 1010, 760, 0.75, 0.0), ("sprites/esfera1", 90, 640, 0.6, 1.3),
                       ("sprites/moeda1", 1000, 1560, 0.7, 2.1), ("sprites/esfera0", 120, 1700, 0.55, 3.0)]
        self.passos = [(p, snap(a, self.BATIDA / 2), b) for p, a, b in PASSOS]
        self.passos[0] = (1, T0, self.passos[0][2])
        self.lupas = []
        for p, q, ts, (x0, y0, x1, y1), k in self.LUPAS:
            _, a, b = self.passos[p - 1]
            im = quadro_sr(int(round(ts * 29.916666)) if os.path.exists(f"{D}/sr/{int(round(ts * 29.916666)):05d}.jpg") else self._perto(ts))[y0:y1, x0:x1]
            larg = 560; esc = larg / im.shape[1]
            im = cv2.resize(im, None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)
            h, w = im.shape[:2]; b2 = 12
            card = np.full((h + 2 * b2, w + 2 * b2, 4), 255, np.uint8)
            card[b2:b2 + h, b2:b2 + w, :3] = im
            mm = np.zeros(card.shape[:2], np.uint8); r = 34
            cv2.rectangle(mm, (r, 0), (card.shape[1] - r, card.shape[0]), 255, -1); cv2.rectangle(mm, (0, r), (card.shape[1], card.shape[0] - r), 255, -1)
            for cx, cy in ((r, r), (card.shape[1] - r, r), (r, card.shape[0] - r), (card.shape[1] - r, card.shape[0] - r)): cv2.circle(mm, (cx, cy), r, 255, -1, cv2.LINE_AA)
            card[:, :, 3] = mm
            ini = a + q * (b - a)
            self.lupas.append((card, ini, min(ini + 1.9, b + 0.2), k))

    def _perto(self, ts):
        alvo = ts * 29.916666
        return min(set(FONTE), key=lambda i: abs(i - alvo))

    def cartao(self, t, tt, z=1.0):
        im = quadro_sr(idx_em(tt))
        im = zoom_crop(im, z, cy=1260, w=self.CW, h=self.CH)
        Bc = self.B
        out = np.zeros((self.CH + 2 * Bc, self.CW + 2 * Bc, 4), np.uint8)
        out[:, :, :3] = 255; out[:, :, 3] = self.borda
        reg = out[Bc:Bc + self.CH, Bc:Bc + self.CW]
        a = self.mask[:, :, None].astype(np.float32) / 255
        reg[:, :, :3] = (reg[:, :, :3] * (1 - a) + im * a).astype(np.uint8)
        return out

    def girar(self, rgba, ang, esc=1.0):
        h, w = rgba.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, esc)
        cos, sin = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * sin + w * cos), int(h * cos + w * sin)
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        return cv2.warpAffine(rgba, M, (nw, nh), flags=cv2.INTER_LINEAR, borderValue=(0, 0, 0, 0))

    def passo_em(self, t):
        if not (T0 <= t < TFIM): return None, None
        atual = (None, None)
        for p, a, b in self.passos:
            if a <= t: atual = (p, a)
        return atual

    def quadro(self, f):
        t = f / FPS; tt = min(t, TFIM - 1 / FPS)
        img = self.fundo.copy()
        # moedas e esferas 3D flutuando (atrás do cartão)
        chuva = max(0.0, t - TFIM)
        for i, (nome, x, y, s, fase, vel) in enumerate(self.sprites):
            yy = y + 30 * math.sin(t * vel + fase)
            xx = x + 20 * math.cos(t * vel * 0.7 + fase)
            if chuva > 0:
                yy = (yy + chuva * 1300 * (0.8 + 0.05 * i)) % 2100 - 100
                xx = 110 + (i % 2) * 860 + 40 * math.sin(i)   # no encerramento, só nas laterais
            colar(img, png(nome), xx, yy, 0.95, s, True)
        p, ta = self.passo_em(t)
        # cartão do vídeo
        if t < TFIM + 0.5:
            sai = ease_out((t - TFIM) / 0.5) if t >= TFIM else 0
            z = 1.0
            if ta is not None:
                dt = t - ta; z += 0.08 * (ease_out(dt / 0.2) if dt < 0.2 else math.exp(-(dt - 0.2) * 2))
            card = self.cartao(t, tt, z)
            ang = -3.5 + 1.5 * math.sin(t * 0.8)
            esc = (0.92 + 0.08 * ease_out(t / 0.5)) * (1 - 0.4 * sai)
            g = self.girar(card, ang, esc)
            sh = self.girar(np.dstack([np.zeros(self.sombra.shape + (3,), np.uint8), (self.sombra * 0.75).astype(np.uint8)]), ang, esc)
            cx, cy = 560, 1130 + 14 * math.sin(t * 1.1)
            colar(img, sh, cx + 20, cy + 40, 1 - sai, 1, True)
            colar(img, g, cx, cy, 1 - sai, 1, True)
            for nome, fx, fy, fs, ff in self.frente:
                colar(img, png(nome), fx + 15 * math.cos(t * 0.9 + ff), fy + 40 * math.sin(t * 1.2 + ff), 1 - sai, fs, True)
            if t >= T0 and t < TFIM:
                colar(img, png("tag2"), 260, 430 + 14 * math.sin(t * 1.1), janela(t, T0, 0.3), 1, True)
        if t < T0:
            img = (img * 0.42).astype(np.uint8)
            e = janela(t, 0.1, 0.35)
            colar(img, png("gancho2"), W / 2, 900 + (1 - ease_out(e)) * 60, e, 1, True)
        elif t < TFIM:
            dt = t - ta; e = ease_back(min(dt / 0.35, 1))
            colar(img, png(f"t2_{p}"), 20 - (1 - e) * 200, 190, min(dt / 0.2, 1))
            for card, ini, fim, k in self.lupas:
                if ini <= t < fim:
                    e = ease_back(janela(t, ini, 0.3)); s = 1 - janela(t, fim - 0.25, 0.25)
                    lx, ly = (300, 1380) if k != 3 else (300, 1300)
                    gl = self.girar(card, 5, 1.0)
                    colar(img, gl, lx, ly, s, 0.3 + 0.7 * e, True)
                    colar(img, png(f"lupa_txt{k}"), lx, ly + card.shape[0] / 2 + 60, s * janela(t, ini + 0.2, 0.25), 1, True)
        for vt in [T0]:
            if 0 <= t - vt < 0.15:
                a = 0.5 * (1 - (t - vt) / 0.15); img = (img * (1 - a) + 255 * a).astype(np.uint8)
        if t < TFIM + 0.3: colar(img, png("selo"), W - 220, 160)
        if t >= TFIM:
            e = janela(t, TFIM + 0.2, 0.35)
            colar(img, png("selo_g"), W / 2, 420, e, 0.7 + 0.3 * ease_back(e), True)
            e2 = janela(t, TFIM + 0.4, 0.35)
            colar(img, png("final2"), W / 2, 900 + (1 - ease_out(e2)) * 50, e2, 1, True)
            e3 = janela(t, TFIM + 0.8, 0.3)
            pulso = 1 + 0.05 * math.sin((t - TFIM) * 2 * math.pi / self.BATIDA) * (e3 >= 1)
            if self.cta: colar(img, png(self.cta), W / 2, 1400, e3, (0.6 + 0.4 * ease_back(e3)) * pulso, True)
            colar(img, png("handle"), W / 2, 1560 if self.cta else 1400, janela(t, TFIM + 0.8, 0.3), 1 if self.cta else 1.25, True)
        return img


if __name__ == "__main__":
    op, fmt, saida = sys.argv[1], sys.argv[2], sys.argv[3]
    cta = {"reels": "cta_reels", "stories": "cta_stories"}.get(fmt)  # "limpo" = sem chamada no final
    R = Op1(cta) if op == "1" else Op2(cta)
    if len(sys.argv) > 4 and sys.argv[4] == "--preview":
        ts = [float(x) for x in sys.argv[5].split(",")]
        ims = [cv2.resize(R.quadro(int(t * FPS)), (360, 640), interpolation=cv2.INTER_AREA) for t in ts]
        linhas = [np.hstack(ims[i:i + 4] + [np.zeros((640, 360, 3), np.uint8)] * (4 - len(ims[i:i + 4]))) for i in range(0, len(ims), 4)]
        cv2.imwrite(saida, np.vstack(linhas)); print("prévia", saida, f"T0={T0:.2f} TFIM={TFIM:.2f} TOTAL={TOTAL:.2f}"); sys.exit()
    musica = f"{D}/audio/trilha_{'A' if op == '1' else 'B'}.wav"
    subprocess.run(["python3", f"{D}/src/musica.py", "A" if op == "1" else "B", musica, f"{TOTAL:.3f}", f"{T0:.4f}"], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", musica, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
                           "-profile:v", "high", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for f in range(N):
        ff.stdin.write(R.quadro(f).tobytes())
        if f % 48 == 0: print(f, "/", N, flush=True)
    ff.stdin.close(); ff.wait(); print("ok", saida, f"{TOTAL:.2f}s")
