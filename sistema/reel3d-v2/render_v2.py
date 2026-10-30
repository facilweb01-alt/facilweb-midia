"""Reel 3D v2 @facilweb — "Seu delivery vendendo sozinho" (1080x1920, 24 fps). Compositor quadro a quadro."""
import math, os, subprocess, sys
import cv2, numpy as np

D = "/home/claude/reel3d-v2"; C = f"{D}/camadas"; SP = "/home/claude/video-pos/camadas2/sprites"
TELAS = "/home/claude/criativos3d/telas"
W, H, FPS = 1080, 1920, 24
T_HOOK, T_PONTE, T_FERR, DUR_F, T_FIM, TOTAL = 2.0, 2.0, 4.2, 2.6, 17.2, 20.4
BATIDA = 60 / 124

_c = {}
def png(caminho):
    if caminho not in _c:
        p = caminho if caminho.startswith("/") else f"{C}/{caminho}.png"
        im = cv2.imread(p, cv2.IMREAD_UNCHANGED)
        if im.shape[2] == 3: im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        _c[caminho] = im
    return _c[caminho]

def colar(dst, rgba, x, y, alpha=1.0, escala=1.0, centro=False):
    if alpha <= 0.01 or escala <= 0.01: return
    im = rgba if abs(escala - 1) < 1e-3 else cv2.resize(rgba, None, fx=escala, fy=escala, interpolation=cv2.INTER_LINEAR if escala > 1 else cv2.INTER_AREA)
    h, w = im.shape[:2]
    if centro: x, y = x - w / 2, y - h / 2
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1: return
    sub = im[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (sub[:, :, 3:4].astype(np.float32) / 255) * alpha
    reg = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (reg * (1 - a) + sub[:, :, :3] * a).astype(np.uint8)

def eo(x): x = min(max(x, 0), 1); return 1 - (1 - x) ** 3
def eb(x, s=1.7):
    x = min(max(x, 0), 1) - 1; return x * x * ((s + 1) * x + s) + 1
def jan(t, a, d=0.25): return min(max((t - a) / d, 0), 1)

def girar(rgba, ang):
    h, w = rgba.shape[:2]; M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, 1.0)
    c, s = abs(M[0, 0]), abs(M[0, 1]); nw, nh = int(h * s + w * c), int(h * c + w * s)
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(rgba, M, (nw, nh), borderValue=(0, 0, 0, 0))

def cartao(img, larg=500, b=12, r=34):
    esc = larg / img.shape[1]; im = cv2.resize(img[:, :, :3], None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)
    h, w = im.shape[:2]; card = np.full((h + 2 * b, w + 2 * b, 4), 255, np.uint8); card[b:b + h, b:b + w, :3] = im
    m = np.zeros(card.shape[:2], np.uint8); H2, W2 = m.shape
    cv2.rectangle(m, (r, 0), (W2 - r, H2), 255, -1); cv2.rectangle(m, (0, r), (W2, H2 - r), 255, -1)
    for cx, cy in ((r, r), (W2 - r, r), (r, H2 - r), (W2 - r, H2 - r)): cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    card[:, :, 3] = m; return card

# recortes de cada tela para a "lupa" (x0, y0, x1, y1 na tela 600x1300)
LUPA = {1: ("cardapio", (10, 380, 590, 625)), 2: ("roleta", (60, 380, 540, 940)), 3: ("pontos", (20, 240, 580, 400)),
        4: ("carrinho", (20, 290, 540, 830)), 5: ("artes", (0, 250, 600, 800))}
LADO = {1: 1, 2: -1, 3: 1, 4: -1, 5: 1}   # 1 = celular entra pela direita
SPRITES = ["moeda0", "moeda1", "moeda2", "moeda3", "esfera0", "esfera1"]

class Reel:
    def __init__(self):
        self.fundo = cv2.imread(f"{C}/fundo.png")[:H, :W]
        self.cards = {}
        for k, (tela, (x0, y0, x1, y1)) in LUPA.items():
            im = cv2.imread(f"{TELAS}/{tela}.png", cv2.IMREAD_UNCHANGED)[y0:y1, x0:x1]
            self.cards[k] = girar(cartao(im, 520 if k not in (2, 4) else 440), 4 * -LADO[k])
        rng = np.random.default_rng(11)
        self.chuva = [(SPRITES[i % 6], rng.uniform(60, 1020), rng.uniform(-1900, -100), rng.uniform(0.35, 0.8), rng.uniform(900, 1500)) for i in range(16)]
        self.flut = [(SPRITES[i % 6], rng.uniform(40, 1040), rng.uniform(300, 1800), rng.uniform(0.3, 0.55), rng.uniform(0, 6)) for i in range(7)]
        self.viradas = [T_HOOK, 3.1] + [T_FERR + i * DUR_F for i in range(5)] + [T_FIM]

    def fone(self, nome, k):
        p = f"{D}/fr/{nome}/f{k:04d}.png"
        return png(p) if os.path.exists(p) else None

    def quadro(self, f):
        t = f / FPS
        img = self.fundo.copy()
        for nome, x, y, s, fase in self.flut:   # moedas 3D ao fundo
            colar(img, png(f"{SP}/{nome}.png"), x + 18 * math.cos(t * 0.8 + fase), y + 26 * math.sin(t * 1.1 + fase), 0.85, s, True)
        if t < T_HOOK:
            img = (img * 0.55).astype(np.uint8)
            for nome, x, y0, s, vel in self.chuva:
                colar(img, png(f"{SP}/{nome}.png"), x, y0 + t * vel, 0.95, s, True)
            colar(img, png("h_topo"), W / 2, 560, jan(t, 0.05, 0.2), 0.9 + 0.1 * eb(jan(t, 0.05, 0.25)), True)
            k = int(min(max((t - 0.25) / 1.2, 0), 1) * 29)
            colar(img, png(f"cont{k:02d}"), W / 2, 790, jan(t, 0.2, 0.15), 1.0 + 0.06 * math.sin(t * 20) * (k < 29), True)
            colar(img, png("h_base"), W / 2, 1040, jan(t, 0.85, 0.25), 1, True)
            colar(img, png("h_nota"), W / 2, 1230, jan(t, 1.2, 0.3), 1, True)
        elif t < T_FERR:
            dt = t - T_PONTE
            k = min(int(dt * FPS), 52); tr = self.fone("trio", k)
            if tr is not None:
                e = eo(dt / 0.5)
                colar(img, tr, W / 2, 1300 + (1 - e) * 700, 1, 1.5, True)
            if t < 3.1: colar(img, png("b_1"), W / 2, 520, jan(t, T_PONTE + 0.05, 0.2), 0.85 + 0.15 * eb(jan(t, T_PONTE + 0.05, 0.3)), True)
            else: colar(img, png("b_2"), W / 2, 520, jan(t, 3.1, 0.2), 0.85 + 0.15 * eb(jan(t, 3.1, 0.3)), True)
        elif t < T_FIM:
            i = int((t - T_FERR) // DUR_F) + 1; dt = (t - T_FERR) - (i - 1) * DUR_F
            lado = LADO[i]
            colar(img, png(f"num{i}"), W - 560 if lado > 0 else 40, 640, 0.9 * jan(dt, 0.05, 0.3))
            fr = self.fone(f"t{i}", min(int(dt * FPS), 62))
            if fr is not None:
                e = eb(dt / 0.38, 1.3)
                esc = 1.38 * (1.12 - 0.12 * eo(dt / 0.45))
                colar(img, fr, W / 2 + lado * (1 - e) * 900, 1265 + 14 * math.sin(t * 1.4), 1, esc, True)
            e = eb(min(dt / 0.3, 1))
            colar(img, png(f"pal{i}"), 20 - (1 - e) * 140, 385, min(dt / 0.15, 1))
            e2 = jan(dt, 0.18, 0.25); colar(img, png(f"sub{i}"), 30, 590 + (1 - eo(e2)) * 40, e2)
            colar(img, png(f"chip{i}"), W - 200, 190, jan(dt, 0.0, 0.2))
            ini, fim = 1.0, DUR_F - 0.15
            if ini <= dt < fim:
                e = eb(jan(dt, ini, 0.3)); sai = 1 - jan(dt, fim - 0.2, 0.2)
                card = self.cards[i]; cx = 300 if lado > 0 else W - 300
                colar(img, card, cx, 1380, sai, 0.3 + 0.7 * e, True)
                colar(img, png(f"etq{i}"), cx, 1380 + card.shape[0] / 2 + 50, sai * jan(dt, ini + 0.2, 0.25), 1, True)
            # barra de progresso
            x0, y0, larg, gap = 70, 1720, 176, 12
            for j in range(5):
                xa = x0 + j * (larg + gap); sub = img[y0:y0 + 12, xa:xa + larg]
                img[y0:y0 + 12, xa:xa + larg] = (sub * 0.6 + 255 * 0.4).astype(np.uint8)
                frac = 1.0 if j + 1 < i else (dt / DUR_F if j + 1 == i else 0)
                if frac > 0: cv2.rectangle(img, (xa, y0), (xa + int(larg * frac), y0 + 12), (63, 198, 141), -1)
            if dt < 0.14:   # chicote (motion blur horizontal) na entrada de cada ferramenta
                k = int(60 * (1 - dt / 0.14)) | 1
                img = cv2.blur(img, (k, 1))
        else:
            dt = t - T_FIM
            colar(img, png("selo_g"), W / 2, 480, jan(dt, 0.05, 0.3), 0.6 + 0.4 * eb(jan(dt, 0.05, 0.4)), True)
            colar(img, png("f_1"), W / 2, 870 + (1 - eo(jan(dt, 0.3, 0.35))) * 50, jan(dt, 0.3, 0.3), 1, True)
            colar(img, png("f_2"), W / 2, 1090, jan(dt, 0.6, 0.3), 1, True)
            colar(img, png("f_3"), W / 2, 1180, jan(dt, 0.8, 0.3), 1, True)
            colar(img, png("handle"), W / 2, 1420, jan(dt, 1.0, 0.3), 1, True)
        # tremida no impacto do gancho
        if T_HOOK <= t < T_HOOK + 0.25:
            k = (1 - (t - T_HOOK) / 0.25) * 16
            M = np.float32([[1, 0, k * math.sin(t * 90)], [0, 1, k * math.cos(t * 70)]])
            img = cv2.warpAffine(img, M, (W, H), borderMode=cv2.BORDER_REFLECT)
        for vt in self.viradas:
            if 0 <= t - vt < 0.1:
                a = 0.45 * (1 - (t - vt) / 0.1); img = (img * (1 - a) + 255 * a).astype(np.uint8)
        if t < T_FIM + 0.2: colar(img, png("selo"), 10, 160)
        return img

if __name__ == "__main__":
    R = Reel()
    if len(sys.argv) > 2 and sys.argv[1] == "--preview":
        ts = [float(x) for x in sys.argv[2].split(",")]
        ims = [cv2.resize(R.quadro(int(t * FPS)), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
        while len(ims) % 6: ims.append(np.zeros((480, 270, 3), np.uint8))
        cv2.imwrite(sys.argv[3], np.vstack([np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)])); sys.exit()
    saida = sys.argv[1]
    mus = f"{D}/trilha.wav"
    subprocess.run(["python3", "/home/claude/video-pos/src/musica.py", "A", mus, f"{TOTAL}", f"{T_HOOK}"], check=True)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-i", mus, "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", saida], stdin=subprocess.PIPE)
    for f in range(int(TOTAL * FPS)):
        ff.stdin.write(R.quadro(f).tobytes())
    ff.stdin.close(); ff.wait(); print("ok", saida)
