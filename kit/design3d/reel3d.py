"""Reel 3D vertical (1080x1920, 24 fps) a partir de um JSON: gancho com contador, celulares 3D com as telas
reais do produto, zoom de lupa em cada item, barra de progresso, final com a marca (sem chamada na tela).

Uso: python3 reel3d.py roteiro.json [--previa]
Roteiro (exemplo em exemplos/reel3d-exemplo.json):
{
  "marca": "marca.json", "saida": "saida/reel3d.mp4", "musica": "A",      # A (animada), B (calma), caminho .wav, ou null
  "gancho": {"tipo": "contador", "topo": "Você paga", "prefixo": "R$ ", "valor": 4600,
             "base": "por mês de comissão<br>pro app de delivery?", "nota": "Exemplo: ..."},
     # ou {"tipo": "texto", "titulo": "Pare de perder<br><span>pedido</span>", "texto": "..."}
  "ponte": ["E se esse dinheiro<br><span>ficasse com você?</span>", "5 ferramentas que<br>vendem <span>sozinhas</span>"],
  "ponte_telas": ["cardapio.png", "roleta.png", "carrinho.png"],
  "itens": [{"palavra": "CARDÁPIO", "sub": "com a sua marca, <span>sem baixar app</span>",
             "etiqueta": "O pedido entra pelo seu link", "tela": "cardapio.png", "recorte": [10, 380, 590, 625]}],
  "final": {"titulo": "Seu delivery<br><span>vendendo sozinho</span>", "linha1": "Sem comissão por pedido",
            "linha2": "Sistema para restaurante <span>Fácil Web</span>"}
}
Tempos: gancho 2,0 s; ponte 2,2 s (opcional); cada item 2,6 s; final 3,2 s. Itens: 3 a 6 funciona melhor.
recorte = área da tela (600x1300) que aparece ampliada na lupa; omita para usar o terço de cima.
Depois: passar no OpusClip para os efeitos sonoros (ver video/OPUSCLIP.md).
"""
import json, math, os, subprocess, sys
import cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "lib")); sys.path.insert(0, os.path.join(AQUI, "..", "video"))
import marca as M
from comp import png, colar, eo, eb, jan, girar, cartao, barra_progresso, flash, tremida, chicote, html_el, renderizar_camadas
import motor3d as m3d

W, H, FPS = 1080, 1920, 24
D_GANCHO, D_PONTE, D_ITEM, D_FINAL = 2.0, 2.2, 2.6, 3.2


class Reel:
    def __init__(self, roteiro):
        self.base = os.path.dirname(os.path.abspath(roteiro))
        self.r = json.load(open(roteiro, encoding="utf-8"))
        rel = lambda p: p if os.path.isabs(p) else os.path.join(self.base, p)
        self.rel = rel
        self.m = M.carregar(rel(self.r["marca"]))
        self.saida = rel(self.r.get("saida", "saida/reel3d.mp4"))
        self.trab = os.path.splitext(self.saida)[0] + "_trabalho"
        self.cam = os.path.join(self.trab, "camadas"); self.fr = os.path.join(self.trab, "frames3d")
        self.itens = self.r["itens"]; self.tem_ponte = bool(self.r.get("ponte"))
        self.t_ponte = D_GANCHO; self.t_itens = D_GANCHO + (D_PONTE if self.tem_ponte else 0)
        self.t_final = self.t_itens + D_ITEM * len(self.itens); self.total = self.t_final + D_FINAL

    # ---------- camadas de texto ----------
    def camadas(self):
        m, c = self.m, self.m["cores"]; logo = M.logo_data_uri(m)
        ex = M.css_vars(m) + f".v,span{{color:{c['destaque']}}} .l{{color:{c['acento']}}}"
        T = lambda txt, size=72, w=900, extra="": html_el(f'<div class="t">{txt}</div>', f".t{{width:{w}px;text-align:center;font-weight:900;font-size:{size}px;line-height:1.04;letter-spacing:-1px;padding:20px;text-shadow:0 10px 34px rgba(0,0,0,.5)}} {extra}", ex)
        selo = lambda tam, pad, rad, mar: html_el(f'<div class="s">{"<img src=" + chr(34) + logo + chr(34) + ">" if logo else m["nome"]}</div>',
            f".s{{width:{tam}px;height:{tam}px;padding:{pad}px;background:#fff;border-radius:{rad}px;margin:{mar}px;box-shadow:0 14px 34px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;color:{c['primaria']};font-weight:900;font-size:{tam//6}px;text-align:center}} .s img{{width:100%;display:block}}", ex)
        it = {"selo": (selo(150, 13, 34, 30), False), "selo_g": (selo(300, 26, 66, 50), False),
              "handle": (html_el(f'<div class="h">{m.get("handle","")} · {m.get("site","")}</div>', ".h{font-size:40px;font-weight:600;opacity:.9;padding:10px}", ex), False)}
        g = self.r["gancho"]
        if g.get("tipo", "contador") == "contador":
            it["h_topo"] = (T(g.get("topo", ""), 74), False)
            it["h_base"] = (T(g.get("base", ""), 60), False)
            it["h_nota"] = (T(g.get("nota", ""), 28, 900, ".t{font-weight:500;opacity:.75;letter-spacing:0}"), False)
            for k in range(30):
                v = round(g["valor"] * (1 - (1 - k / 29) ** 3))
                txt = f"{g.get('prefixo','')}{v:,}".replace(",", ".") + g.get("sufixo", "")
                it[f"cont{k:02d}"] = (html_el(f'<div class="c">{txt}</div>', f".c{{font-weight:900;font-size:210px;letter-spacing:-6px;color:{c['acento']};padding:10px 30px;text-shadow:0 14px 50px {M.rgba(c['acento'],.45)},0 8px 0 rgba(0,0,0,.35)}}", ex), False)
        else:
            it["h_titulo"] = (T(g.get("titulo", ""), 110), False)
            it["h_texto"] = (T(g.get("texto", ""), 52, 900, ".t{font-weight:700}"), False)
        for i, p in enumerate(self.r.get("ponte", [])[:2], 1):
            it[f"ponte{i}"] = (T(p, 84), False)
        for i, x in enumerate(self.itens, 1):
            it[f"num{i}"] = (html_el(f'<div class="n">{i:02d}</div>', f".n{{font-weight:900;font-size:430px;line-height:1;color:transparent;-webkit-text-stroke:4px {M.rgba(c['destaque'],.42)};padding:10px}}", ex), False)
            it[f"pal{i}"] = (html_el(f'<div class="w">{x["palavra"]}<i></i></div>', f".w{{font-weight:900;font-size:{128 if len(x['palavra']) <= 9 else 104}px;line-height:.95;letter-spacing:-3px;padding:20px 30px;text-shadow:0 10px 40px rgba(0,0,0,.55)}} .w i{{display:block;height:14px;width:62%;background:{c['destaque']};border-radius:10px;margin-top:12px}}", ex), False)
            it[f"sub{i}"] = (html_el(f'<div class="b">{x.get("sub","")}</div>', f".b{{font-weight:700;font-size:46px;padding:12px 30px;background:{M.rgba(c['escura'],.86)};border:2px solid rgba(255,255,255,.14);border-radius:22px;margin:20px;box-shadow:0 12px 30px rgba(0,0,0,.4)}}", ex), False)
            it[f"chip{i}"] = (html_el(f'<div class="c">{i}/{len(self.itens)}</div>', f".c{{font-weight:900;font-size:42px;background:{c['acento']};padding:10px 26px;border-radius:40px;margin:20px;box-shadow:0 10px 26px {M.rgba(c['acento'],.5)}}}", ex), False)
            if x.get("etiqueta"):
                it[f"etq{i}"] = (html_el(f'<div class="e">{x["etiqueta"]}</div>', f".e{{background:#fff;color:{c['escura']};font-weight:900;font-size:36px;border-radius:22px;padding:14px 26px;margin:20px;box-shadow:0 14px 34px rgba(0,0,0,.4)}}", ex), False)
        f = self.r.get("final", {})
        it["f_1"] = (T(f.get("titulo", m["nome"]), 96), False)
        it["f_2"] = (T(f.get("linha1", ""), 52, 900, ".t{font-weight:700}"), False)
        it["f_3"] = (T(f.get("linha2", ""), 40, 1000, ".t{font-weight:600}"), False)
        fundo = (f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0}}body{{width:{W}px;height:{H}px;position:relative;overflow:hidden}}'
                 f'{M.fundo_css(m, W, H)}</style></head><body>{M.fundo_html(m, W, H)}</body></html>')
        it["fundo"] = (fundo, True)
        renderizar_camadas(it, self.cam, W, H)

    # ---------- celulares 3D ----------
    def frames3d(self):
        base = {"w": 720, "h": 1280, "fov": 28, "cam": [0, 0, 5.2], "giro": 0.28, "flutua": 0.0, "moedas": []}
        cenas = {}
        for i, x in enumerate(self.itens, 1):
            ry = -0.38 if i % 2 else 0.38
            cenas[f"t{i}"] = dict(base, frames=int(D_ITEM * FPS) + 1, phones=[m3d.celular(self.rel(x["tela"]), [0, 0, 0], [0.06, ry, 0], 1.0)])
        if self.tem_ponte and self.r.get("ponte_telas"):
            tl = [self.rel(p) for p in self.r["ponte_telas"]]
            cenas["trio"] = dict(base, giro=0.12, frames=int(D_PONTE * FPS) + 1, phones=[
                m3d.celular(tl[1 % len(tl)], [-0.62, -0.05, -0.6], [0.05, 0.5, 0.08], 0.8, 1.5),
                m3d.celular(tl[2 % len(tl)], [0.62, -0.05, -0.6], [0.05, -0.5, -0.08], 0.8, 3.0),
                m3d.celular(tl[0], [0, 0, 0.2], [0.06, -0.1, 0], 0.9)])
        c = self.m["cores"]   # moedas e esferas 3D nas cores da marca, usadas como enfeite
        for k, rot in enumerate([[1.2, 0, 0.4], [0.5, 0.3, 1.1], [1.5, 0.8, -0.3], [0.2, 1.2, 0.7]]):
            cenas[f"spr_moeda{k}"] = {"w": 360, "h": 360, "fov": 28, "cam": [0, 0, 1.6], "phones": [], "moedas": [m3d.moeda([0, 0, 0], rot, 1.6)]}
        for k, cor in enumerate([c["destaque"], c["acento"]]):
            cenas[f"spr_esfera{k}"] = {"w": 300, "h": 300, "fov": 28, "cam": [0, 0, 1.2], "phones": [], "moedas": [m3d.esfera(cor, [0, 0, 0], 1.6)]}
        m3d.renderizar(cenas, self.fr, 1, FPS)

    # ---------- composição ----------
    def preparar(self):
        self.fundo = cv2.imread(os.path.join(self.cam, "fundo.png"))[:H, :W]
        self.sprites = sorted(os.path.join(self.fr, f) for f in os.listdir(self.fr) if f.startswith("spr_") and f.endswith(".png"))
        rng = np.random.default_rng(11)
        self.chuva = [(self.sprites[i % len(self.sprites)], rng.uniform(60, 1020), rng.uniform(-1900, -100), rng.uniform(0.35, 0.8), rng.uniform(900, 1500)) for i in range(16)] if self.sprites else []
        self.flut = [(self.sprites[i % len(self.sprites)], rng.uniform(40, 1040), rng.uniform(300, 1800), rng.uniform(0.3, 0.55), rng.uniform(0, 6)) for i in range(7)] if self.sprites else []
        self.cards = {}
        for i, x in enumerate(self.itens, 1):
            im = cv2.imread(self.rel(x["tela"]), cv2.IMREAD_UNCHANGED)
            x0, y0, x1, y1 = x.get("recorte", [0, 0, im.shape[1], im.shape[0] // 3])
            lado = 1 if i % 2 else -1
            self.cards[i] = girar(cartao(im[y0:y1, x0:x1], 520 if (x1 - x0) / max(y1 - y0, 1) > 1.2 else 440), 4 * -lado)
        self.viradas = [D_GANCHO] + ([self.t_ponte + 1.1] if self.tem_ponte else []) + [self.t_itens + i * D_ITEM for i in range(len(self.itens))] + [self.t_final]
        self.cor_barra = M.hex_bgr(self.m["cores"]["destaque"])

    def L(self, n): return png(os.path.join(self.cam, n + ".png"))

    def fone(self, nome, k):
        p = os.path.join(self.fr, nome, f"f{k:04d}.png")
        return png(p) if os.path.exists(p) else None

    def quadro(self, f):
        t = f / FPS; img = self.fundo.copy(); L = self.L
        for nome, x, y, s, fase in self.flut:
            colar(img, png(nome), x + 18 * math.cos(t * 0.8 + fase), y + 26 * math.sin(t * 1.1 + fase), 0.85, s, True)
        if t < D_GANCHO:
            img = (img * 0.55).astype(np.uint8)
            for nome, x, y0, s, vel in self.chuva:
                colar(img, png(nome), x, y0 + t * vel, 0.95, s, True)
            if self.r["gancho"].get("tipo", "contador") == "contador":
                colar(img, L("h_topo"), W / 2, 560, jan(t, 0.05, 0.2), 0.9 + 0.1 * eb(jan(t, 0.05, 0.25)), True)
                k = int(min(max((t - 0.25) / 1.2, 0), 1) * 29)
                colar(img, L(f"cont{k:02d}"), W / 2, 790, jan(t, 0.2, 0.15), 1.0 + 0.06 * math.sin(t * 20) * (k < 29), True)
                colar(img, L("h_base"), W / 2, 1040, jan(t, 0.85, 0.25), 1, True)
                colar(img, L("h_nota"), W / 2, 1230, jan(t, 1.2, 0.3), 1, True)
            else:
                colar(img, L("h_titulo"), W / 2, 760, jan(t, 0.05, 0.2), 1.25 - 0.25 * eb(jan(t, 0.05, 0.3)), True)
                colar(img, L("h_texto"), W / 2, 1060, jan(t, 0.7, 0.3), 1, True)
        elif t < self.t_itens:
            dt = t - self.t_ponte
            tr = self.fone("trio", min(int(dt * FPS), int(D_PONTE * FPS)))
            if tr is not None:
                colar(img, tr, W / 2, 1300 + (1 - eo(dt / 0.5)) * 700, 1, 1.5, True)
            p1 = dt < 1.1 or not os.path.exists(os.path.join(self.cam, "ponte2.png"))
            a = self.t_ponte + (0.05 if p1 else 1.1)
            colar(img, L("ponte1" if p1 else "ponte2"), W / 2, 520, jan(t, a, 0.2), 0.85 + 0.15 * eb(jan(t, a, 0.3)), True)
        elif t < self.t_final:
            i = int((t - self.t_itens) // D_ITEM) + 1; dt = (t - self.t_itens) - (i - 1) * D_ITEM
            lado = 1 if i % 2 else -1
            colar(img, L(f"num{i}"), W - 560 if lado > 0 else 40, 640, 0.9 * jan(dt, 0.05, 0.3))
            fr = self.fone(f"t{i}", min(int(dt * FPS), int(D_ITEM * FPS)))
            if fr is not None:
                e = eb(dt / 0.38, 1.3); esc = 1.38 * (1.12 - 0.12 * eo(dt / 0.45))
                colar(img, fr, W / 2 + lado * (1 - e) * 900, 1265 + 14 * math.sin(t * 1.4), 1, esc, True)
            e = eb(min(dt / 0.3, 1))
            colar(img, L(f"pal{i}"), 20 - (1 - e) * 140, 385, min(dt / 0.15, 1))
            e2 = jan(dt, 0.18, 0.25); colar(img, L(f"sub{i}"), 30, 590 + (1 - eo(e2)) * 40, e2)
            colar(img, L(f"chip{i}"), W - 200, 190, jan(dt, 0.0, 0.2))
            ini, fim = 1.0, D_ITEM - 0.15
            if ini <= dt < fim:
                e = eb(jan(dt, ini, 0.3)); sai = 1 - jan(dt, fim - 0.2, 0.2)
                card = self.cards[i]; cx = 300 if lado > 0 else W - 300
                colar(img, card, cx, 1380, sai, 0.3 + 0.7 * e, True)
                if os.path.exists(os.path.join(self.cam, f"etq{i}.png")):
                    colar(img, L(f"etq{i}"), cx, 1380 + card.shape[0] / 2 + 50, sai * jan(dt, ini + 0.2, 0.25), 1, True)
            barra_progresso(img, i - 1, len(self.itens), dt / D_ITEM, 1720, self.cor_barra)
            if dt < 0.14: img = chicote(img, 60 * (1 - dt / 0.14))
        else:
            dt = t - self.t_final
            colar(img, L("selo_g"), W / 2, 480, jan(dt, 0.05, 0.3), 0.6 + 0.4 * eb(jan(dt, 0.05, 0.4)), True)
            colar(img, L("f_1"), W / 2, 870 + (1 - eo(jan(dt, 0.3, 0.35))) * 50, jan(dt, 0.3, 0.3), 1, True)
            colar(img, L("f_2"), W / 2, 1090, jan(dt, 0.6, 0.3), 1, True)
            colar(img, L("f_3"), W / 2, 1180, jan(dt, 0.8, 0.3), 1, True)
            colar(img, L("handle"), W / 2, 1420, jan(dt, 1.0, 0.3), 1, True)
        if D_GANCHO <= t < D_GANCHO + 0.25: img = tremida(img, (1 - (t - D_GANCHO) / 0.25) * 16, t)
        for vt in self.viradas:
            if 0 <= t - vt < 0.1: img = flash(img, 0.45 * (1 - (t - vt) / 0.1))
        if t < self.t_final + 0.2: colar(img, L("selo"), 10, 160)
        return img

    def exportar(self):
        os.makedirs(os.path.dirname(self.saida), exist_ok=True)
        mus = self.r.get("musica", "A"); wav = None
        if mus in ("A", "B"):
            wav = os.path.join(self.trab, "trilha.wav")
            subprocess.run(["python3", os.path.join(AQUI, "..", "video", "musica.py"), mus, wav, f"{self.total}", f"{D_GANCHO}"], check=True)
        elif mus:
            wav = self.rel(mus)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
        cmd += (["-i", wav, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"] if wav else
                ["-f", "lavfi", "-t", f"{self.total}", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-shortest"])
        cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p", "-movflags", "+faststart", self.saida]
        ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for f in range(int(self.total * FPS)): ff.stdin.write(self.quadro(f).tobytes())
        ff.stdin.close(); ff.wait()
        cv2.imwrite(os.path.splitext(self.saida)[0] + "-capa.jpg", self.quadro(int(1.6 * FPS)), [cv2.IMWRITE_JPEG_QUALITY, 92])
        print("ok", self.saida, f"{self.total:.1f}s")

    def previa(self):
        ts = [0.5, 1.6, self.t_ponte + 0.5, self.t_itens + 0.6] + [self.t_itens + i * D_ITEM + 1.6 for i in range(len(self.itens))] + [self.t_final + 1.5]
        ims = [cv2.resize(self.quadro(int(t * FPS)), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
        while len(ims) % 6: ims.append(np.zeros((480, 270, 3), np.uint8))
        p = os.path.splitext(self.saida)[0] + "-previa.jpg"
        cv2.imwrite(p, np.vstack([np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)])); print("prévia", p)


if __name__ == "__main__":
    R = Reel(sys.argv[1])
    R.camadas(); R.frames3d(); R.preparar()
    R.previa()
    if "--previa" not in sys.argv: R.exportar()
