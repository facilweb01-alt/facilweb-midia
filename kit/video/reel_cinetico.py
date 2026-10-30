"""Edição profissional de um vídeo bruto (demonstração, bastidor, produto) em Reel/Story 1080x1920 a partir de um JSON.

Dois estilos:
  tela_cheia : vídeo ocupando a tela, palavra grande por passo, zoom de impacto, flash nas viradas, barra de progresso.
  vitrine    : vídeo num cartão inclinado sobre o fundo da marca, moedas/esferas 3D, título por passo e "lupas"
               (recortes ampliados da tela em momentos-chave).
Os dois: gancho nos 2 primeiros segundos, logo sempre visível, trechos acelerados, correção de cor e sombras,
super-resolução opcional (IA), música própria sem direitos autorais, final com a marca e SEM chamada na tela.

Uso: python3 reel_cinetico.py roteiro.json [--previa]
Roteiro (exemplo em exemplos/reel-cinetico-exemplo.json):
{
  "marca": "marca.json", "video": "bruto.mp4", "saida": "saida/reel.mp4",
  "estilo": "tela_cheia",                 # ou "vitrine"
  "musica": "A",                          # A animada, B calma, caminho de .wav, ou null
  "sr": true,                             # super-resolução: use quando o vídeo vier do WhatsApp/baixa resolução
  "gancho": {"trecho": [44.3, 46.1, 1.0],              # trecho de impacto mostrado atrás do texto (ini, fim, velocidade)
             "linhas": ["Pare de", "correr até", "o <span>caixa</span>"], "destaque": "sua mesa paga em 1 minuto",
             "pergunta": "Seu garçom ainda corre até o caixa?", "titulo": "Agora a mesa<br><span>paga em 1 minuto</span>"},
             # tela_cheia usa linhas+destaque; vitrine usa pergunta+titulo
  "passos": [{"ini": 0.5, "fim": 7.5, "vel": 3.0, "palavra": "MESA", "sub": "escolhe a mesa no app",
              "titulo": "Escolhe<br>a <span>mesa</span>"}],
             # um passo pode ter vários trechos: "trechos": [[ini, fim, vel], ...] no lugar de ini/fim/vel
  "lupas": [{"fonte": 24.0, "recorte": [0.23, 0.27, 0.74, 0.43], "passo": 3, "quando": 0.4, "etiqueta": "Sub-total na tela"}],
             # só no estilo vitrine; recorte em frações do quadro (x0, y0, x1, y1); "fonte" = segundo do vídeo original
  "selo_cartao": "TELA REAL DO SISTEMA",
  "final": {"kicker": "SISTEMA POS FÁCIL WEB", "titulo": "Tudo na<br><span>maquininha</span>",
            "texto": "Mesa, comanda, cardápio e pagamento."}
}
"""
import json, math, os, subprocess, sys
import cv2, numpy as np
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "lib")); sys.path.insert(0, AQUI); sys.path.insert(0, os.path.join(AQUI, "..", "design3d"))
import marca as M
from comp import png, colar, eo, eb, jan, girar, cartao, zoom_crop, gradiente, barra_progresso, flash, tremida, html_el, renderizar_camadas
from melhorar import melhorar_quadro

W, H, FPS = 1080, 1920, 24
FREEZE, D_FINAL = 0.4, 3.4


class Roteiro:
    def __init__(self, caminho):
        self.base = os.path.dirname(os.path.abspath(caminho))
        self.r = json.load(open(caminho, encoding="utf-8"))
        self.rel = lambda p: p if os.path.isabs(p) else os.path.join(self.base, p)
        self.m = M.carregar(self.rel(self.r["marca"]))
        self.video = self.rel(self.r["video"])
        self.saida = self.rel(self.r.get("saida", "saida/reel.mp4"))
        self.trab = os.path.splitext(self.saida)[0] + "_trabalho"
        self.cam = os.path.join(self.trab, "camadas"); self.qd = os.path.join(self.trab, "quadros")
        self.estilo = self.r.get("estilo", "tela_cheia")
        cap = cv2.VideoCapture(self.video); self.fps_src = cap.get(cv2.CAP_PROP_FPS) or 30; self.n_src = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)); cap.release()
        self.mapa, self.passos = self._mapa()
        self.t0 = self.passos[0][1]; self.tfim = self.passos[-1][2]; self.total = self.tfim + D_FINAL

    def _trecho(self, a, b, v):
        n = int(round((b - a) / v * FPS))
        return [min(int(round((a + k * v / FPS) * self.fps_src)), self.n_src - 1) for k in range(n)]

    def _mapa(self):
        mapa = []
        g = self.r["gancho"]
        if g.get("trecho"):
            t = self._trecho(*g["trecho"]); mapa += t + [t[-1]] * int(FREEZE * FPS)
        else:
            mapa += [self._trecho(*self._trechos(self.r["passos"][0])[0])[0]] * int(2.2 * FPS)
        passos = []
        for i, p in enumerate(self.r["passos"], 1):
            ini = len(mapa) / FPS
            for tr in self._trechos(p): mapa += self._trecho(*tr)
            passos.append((i, ini, len(mapa) / FPS))
        return mapa, passos

    @staticmethod
    def _trechos(p):
        return p.get("trechos") or [[p["ini"], p["fim"], p.get("vel", 2.0)]]

    # ---------- quadros do vídeo (melhorados e, se pedido, com super-resolução) ----------
    def quadros(self):
        os.makedirs(self.qd, exist_ok=True)
        precisa = set(self.mapa) | {int(round(l["fonte"] * self.fps_src)) for l in self.r.get("lupas", [])}
        falta = sorted(i for i in precisa if not os.path.exists(os.path.join(self.qd, f"{i:05d}.jpg")))
        if not falta: return
        sr = None
        if self.r.get("sr"):
            from super_resolucao import SR; sr = SR()
            print(f"super-resolução em {len(falta)} quadros (~{len(falta) * 7 // 60} min)", flush=True)
        tmp = os.path.join(self.trab, "desruido.mp4")
        if not os.path.exists(tmp):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", self.video, "-vf", "hqdn3d=4:3:6:4", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "12", tmp], check=True)
        cap = cv2.VideoCapture(tmp); alvo = set(falta); i = 0; feitos = 0
        while alvo:
            ok, f = cap.read()
            if not ok: break
            if i in alvo:
                q = melhorar_quadro(f, self.r.get("forca", 1.0)) if self.r.get("melhorar", True) else f
                q = sr.ampliar(q) if sr else q
                # cobre 1440x2560 (9:16) mantendo proporção
                hh, ww = q.shape[:2]; esc = max(1440 / ww, 2560 / hh)
                q = cv2.resize(q, (int(ww * esc), int(hh * esc)), interpolation=cv2.INTER_AREA if esc < 1 else cv2.INTER_LANCZOS4)
                if not sr: q = cv2.addWeighted(q, 1.5, cv2.GaussianBlur(q, (0, 0), 2.2), -0.5, 0)
                y0 = (q.shape[0] - 2560) // 2; x0 = (q.shape[1] - 1440) // 2
                cv2.imwrite(os.path.join(self.qd, f"{i:05d}.jpg"), q[y0:y0 + 2560, x0:x0 + 1440], [cv2.IMWRITE_JPEG_QUALITY, 94])
                alvo.discard(i); feitos += 1
                if sr and feitos % 25 == 0: print(feitos, "/", len(falta), flush=True)
            i += 1

    def q(self, idx):
        return cv2.imread(os.path.join(self.qd, f"{idx:05d}.jpg"))

    # ---------- camadas ----------
    def camadas(self):
        m, c, r = self.m, self.m["cores"], self.r
        logo = M.logo_data_uri(m)
        ex = M.css_vars(m) + f"span,.v{{color:{c['destaque']}}} .l{{color:{c['acento']}}}"
        selo_html = f'<img src="{logo}">' if logo else m["nome"]
        selo = lambda tam, pad, rad, mar: html_el(f'<div class="s">{selo_html}</div>', f".s{{width:{tam}px;height:{tam}px;padding:{pad}px;background:#fff;border-radius:{rad}px;margin:{mar}px;box-shadow:0 14px 34px rgba(0,0,0,.45);display:flex;align-items:center;justify-content:center;color:{c['primaria']};font-weight:900;text-align:center}} .s img{{width:100%;display:block}}", ex)
        PAL = f".w{{font-weight:900;font-size:150px;line-height:.95;letter-spacing:-3px;padding:20px 40px;text-shadow:0 10px 40px rgba(0,0,0,.55)}} .w i{{display:block;height:16px;background:{c['destaque']};border-radius:10px;margin-top:10px}}"
        SUB = f".b{{font-weight:700;font-size:50px;padding:14px 34px;background:{M.rgba(c['escura'],.88)};border-radius:22px;margin:20px;box-shadow:0 12px 30px rgba(0,0,0,.4)}}"
        it = {"selo": (selo(150, 13, 34, 30), False), "selo_g": (selo(300, 26, 66, 50), False),
              "handle": (html_el(f'<div class="h">{m.get("handle","")} · {m.get("site","")}</div>', ".h{font-size:34px;font-weight:600;opacity:.9;padding:10px}", ex), False)}
        g, f = r["gancho"], r.get("final", {})
        n = len(self.passos)
        for i, p in enumerate(r["passos"], 1):
            it[f"pal{i}"] = (html_el(f'<div class="w">{p.get("palavra","")}<i></i></div>', PAL, ex), False)
            it[f"sub{i}"] = (html_el(f'<div class="b">{p.get("sub","")}</div>', SUB, ex), False)
            it[f"chip{i}"] = (html_el(f'<div class="c">{i}/{n}</div>', f".c{{font-weight:900;font-size:44px;background:{c['acento']};padding:10px 28px;border-radius:40px;margin:20px}}", ex), False)
            it[f"tit{i}"] = (html_el(f'<div class="t"><div class="n">{i}</div><div class="x">{p.get("titulo", p.get("palavra",""))}</div></div>',
                f".t{{display:flex;align-items:center;gap:26px;padding:20px 30px}} .n{{width:120px;height:120px;border-radius:34px;background:{c['acento']};font-weight:900;font-size:76px;display:flex;align-items:center;justify-content:center;transform:rotate(-6deg)}} .x{{font-weight:900;font-size:76px;line-height:1;letter-spacing:-1px;text-shadow:0 8px 26px rgba(0,0,0,.4)}}", ex), False)
        for i, l in enumerate(g.get("linhas", [])):
            it[f"g_l{i}"] = (html_el(f'<div class="w">{l}</div>', PAL, ex), False)
        if g.get("destaque"):
            it["g_dest"] = (html_el(f'<div class="b"><span class="l">{g["destaque"]}</span></div>', SUB, ex), False)
        if g.get("pergunta") or g.get("titulo"):
            it["g_vit"] = (html_el(f'<div class="g"><div class="q">{g.get("pergunta","")}</div><h1>{g.get("titulo","")}</h1></div>',
                ".g{width:1000px;text-align:center;padding:30px} .q{display:inline-block;font-size:48px;font-weight:700;background:rgba(255,255,255,.12);border:2px solid rgba(255,255,255,.25);padding:16px 34px;border-radius:30px} h1{font-size:104px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:34px;text-shadow:0 10px 36px rgba(0,0,0,.5)}", ex), False)
        for k, l in enumerate(r.get("lupas", []), 1):
            if l.get("etiqueta"):
                it[f"etq{k}"] = (html_el(f'<div class="e">{l["etiqueta"]}</div>', f".e{{background:#fff;color:{c['escura']};font-weight:900;font-size:38px;border-radius:24px;padding:16px 28px;margin:20px}}", ex), False)
        if r.get("selo_cartao", "TELA REAL"):
            it["tag"] = (html_el(f'<div class="t">{r.get("selo_cartao", "TELA REAL")}</div>', f".t{{font-size:26px;font-weight:800;color:{c['escura']};background:{c['destaque']};padding:10px 24px;border-radius:30px;margin:16px}}", ex), False)
        kick = f'<div class="k">{f.get("kicker","")}</div>' if f.get("kicker") else ""
        bloco = f'{kick}<h1>{f.get("titulo", m["nome"])}</h1><p>{f.get("texto","")}</p>'
        css_final = f".k{{font-size:36px;font-weight:700;letter-spacing:6px;color:{c['destaque']}}} h1{{font-size:110px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:16px}} p{{font-size:44px;line-height:1.35;margin-top:34px}}"
        it["final_txt"] = (html_el(f'<div class="f">{bloco}</div>', ".f{width:1000px;text-align:center;padding:20px}" + css_final, ex), False)
        fundo = (f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0}}body{{width:{W}px;height:{H}px;position:relative;overflow:hidden}}'
                 f'{M.fundo_css(m, W, H)}</style></head><body>{M.fundo_html(m, W, H)}</body></html>')
        it["fundo"] = (fundo, True)
        renderizar_camadas(it, self.cam, W, H)
        if self.estilo == "vitrine":   # moedas e esferas 3D nas cores da marca
            import motor3d as m3d
            cen = {}
            for k, rot in enumerate([[1.2, 0, 0.4], [0.5, 0.3, 1.1], [1.5, 0.8, -0.3], [0.2, 1.2, 0.7]]):
                cen[f"spr_moeda{k}"] = {"w": 360, "h": 360, "fov": 28, "cam": [0, 0, 1.6], "phones": [], "moedas": [m3d.moeda([0, 0, 0], rot, 1.6)]}
            for k, cor in enumerate([c["destaque"], c["acento"]]):
                cen[f"spr_esfera{k}"] = {"w": 300, "h": 300, "fov": 28, "cam": [0, 0, 1.2], "phones": [], "moedas": [m3d.esfera(cor, [0, 0, 0], 1.6)]}
            m3d.renderizar(cen, self.cam)

    def L(self, n): return png(os.path.join(self.cam, n + ".png"))
    def tem(self, n): return os.path.exists(os.path.join(self.cam, n + ".png"))

    def passo_em(self, t):
        if not (self.t0 <= t < self.tfim): return None, None
        at = (None, None)
        for i, a, b in self.passos:
            if a <= t: at = (i, a)
        return at

    def idx(self, t): return self.mapa[min(int(t * FPS), len(self.mapa) - 1)]


class TelaCheia(Roteiro):
    def preparar(self):
        az = M.hex_bgr(self.m["cores"]["escura"])
        self.top = gradiente(W, 760, 0.85, 0.0, az); self.bot = gradiente(W, 520, 0.0, 0.75, az)
        self.fundo = cv2.imread(os.path.join(self.cam, "fundo.png"))[:H, :W]

    def quadro(self, f):
        t = f / FPS; p, ta = self.passo_em(t)
        z = 1.0 + 0.025 * math.sin(t * 0.9)
        if ta is not None:
            dt = t - ta; z += 0.13 * (eo(dt / 0.18) if dt < 0.18 else math.exp(-(dt - 0.18) * 2.2))
        if t < self.t0: z += 0.04 * t / self.t0
        img = zoom_crop(self.q(self.idx(min(t, self.tfim - 1 / FPS))), z, cy=1250)
        if self.t0 <= t < self.t0 + 0.25: img = tremida(img, (1 - (t - self.t0) / 0.25) * 14, t)
        colar(img, self.top, 0, 0); colar(img, self.bot, 0, H - 520)
        if t < self.t0:
            img = (img * 0.55).astype(np.uint8)
            n = len(self.r["gancho"].get("linhas", []))
            for i in range(n):
                e = jan(t, 0.12 + i * 0.33, 0.22)
                colar(img, self.L(f"g_l{i}"), W / 2, 600 + i * 160, e, 1.35 - 0.35 * eb(e), True)
            if self.tem("g_dest"):
                e = jan(t, 0.12 + n * 0.33 + 0.1, 0.25); colar(img, self.L("g_dest"), W / 2, 600 + n * 160 + 30, e, 0.8 + 0.2 * eb(e), True)
        elif t < self.tfim:
            dt = t - ta; e = eb(min(dt / 0.3, 1)); pal = self.L(f"pal{p}"); fit = min(1.0, 1040 / pal.shape[1])
            colar(img, pal, 20 - (1 - e) * 120, 360, min(dt / 0.15, 1), (0.85 + 0.15 * e) * fit)
            e2 = jan(t, ta + 0.18, 0.25); colar(img, self.L(f"sub{p}"), 30, 590 + (1 - eo(e2)) * 40, e2)
            colar(img, self.L(f"chip{p}"), W - 210, 210, min(dt / 0.2, 1))
            _, a, b = self.passos[p - 1]
            barra_progresso(img, p - 1, len(self.passos), (t - a) / (b - a), 1700, M.hex_bgr(self.m["cores"]["destaque"]))
        for vt in [self.t0] + [a for _, a, _ in self.passos[1:]]:
            if 0 <= t - vt < 0.12: img = flash(img, 0.55 * (1 - (t - vt) / 0.12))
        if t < self.tfim + 0.3: colar(img, self.L("selo"), 10, 160)
        if t >= self.tfim:
            dt = t - self.tfim; e = eo(dt / 0.45)
            pag = self.fundo.copy()
            colar(pag, self.L("selo_g"), W / 2, 470, 1, 1, True); colar(pag, self.L("final_txt"), W / 2, 960, 1, 1, True)
            colar(pag, self.L("handle"), W / 2, 1460, jan(dt, 0.6, 0.3), 1.25, True)
            y = int(H * (1 - e)); img[y:] = pag[:H - y]
        return img


class Vitrine(Roteiro):
    CW, CH, R = 760, 1351, 48

    def preparar(self):
        self.fundo = cv2.imread(os.path.join(self.cam, "fundo.png"))[:H, :W]
        m = np.zeros((self.CH, self.CW), np.uint8); R = self.R
        cv2.rectangle(m, (R, 0), (self.CW - R, self.CH), 255, -1); cv2.rectangle(m, (0, R), (self.CW, self.CH - R), 255, -1)
        for cx, cy in ((R, R), (self.CW - R, R), (R, self.CH - R), (self.CW - R, self.CH - R)): cv2.circle(m, (cx, cy), R, 255, -1, cv2.LINE_AA)
        self.mask = m; B = 10; self.B = B
        self.borda = cv2.dilate(cv2.copyMakeBorder(m, B, B, B, B, cv2.BORDER_CONSTANT, 0), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * B + 1, 2 * B + 1)))
        self.sombra = cv2.GaussianBlur(cv2.copyMakeBorder(self.borda, 80, 80, 80, 80, cv2.BORDER_CONSTANT, 0), (0, 0), 30)
        spr = sorted(f[:-4] for f in os.listdir(self.cam) if f.startswith("spr_"))
        rng = np.random.default_rng(4)
        self.sprites = [(spr[i % len(spr)], rng.uniform(40, 1040), rng.uniform(250, 1850), rng.uniform(0.35, 0.75), rng.uniform(0, 6), rng.uniform(0.5, 1.1)) for i in range(9)] if spr else []
        self.frente = [(spr[0], 1010, 760, 0.75, 0.0), (spr[-1], 90, 640, 0.6, 1.3), (spr[1 % len(spr)], 1000, 1560, 0.7, 2.1)] if spr else []
        self.lupas = []
        for k, l in enumerate(self.r.get("lupas", []), 1):
            im = self.q(int(round(l["fonte"] * self.fps_src))); hh, ww = im.shape[:2]
            x0, y0, x1, y1 = l["recorte"]; crop = im[int(y0 * hh):int(y1 * hh), int(x0 * ww):int(x1 * ww)]
            _, a, b = self.passos[l["passo"] - 1]; ini = a + l.get("quando", 0.4) * (b - a)
            self.lupas.append((cartao(crop, 560), ini, min(ini + 1.9, b + 0.2), k))

    def cartao_video(self, tt, z):
        im = zoom_crop(self.q(self.idx(tt)), z, cy=1260, w=self.CW, h=self.CH); B = self.B
        out = np.zeros((self.CH + 2 * B, self.CW + 2 * B, 4), np.uint8); out[:, :, :3] = 255; out[:, :, 3] = self.borda
        reg = out[B:B + self.CH, B:B + self.CW]; a = self.mask[:, :, None].astype(np.float32) / 255
        reg[:, :, :3] = (reg[:, :, :3] * (1 - a) + im * a).astype(np.uint8)
        return out

    def quadro(self, f):
        t = f / FPS; tt = min(t, self.tfim - 1 / FPS); img = self.fundo.copy(); chuva = max(0.0, t - self.tfim)
        for nome, x, y, s, fase, vel in self.sprites:
            yy = y + 30 * math.sin(t * vel + fase); xx = x + 20 * math.cos(t * vel * 0.7 + fase)
            if chuva > 0: yy = (yy + chuva * 1300) % 2100 - 100; xx = 80 + (int(x) % 2) * 920
            colar(img, self.L(nome), xx, yy, 0.95, s, True)
        p, ta = self.passo_em(t)
        if t < self.tfim + 0.5:
            sai = eo((t - self.tfim) / 0.5) if t >= self.tfim else 0; z = 1.0
            if ta is not None:
                dt = t - ta; z += 0.08 * (eo(dt / 0.2) if dt < 0.2 else math.exp(-(dt - 0.2) * 2))
            ang = -3.5 + 1.5 * math.sin(t * 0.8); esc = (0.92 + 0.08 * eo(t / 0.5)) * (1 - 0.4 * sai)
            g = girar(self.cartao_video(tt, z), ang, esc)
            sh = girar(np.dstack([np.zeros(self.sombra.shape + (3,), np.uint8), (self.sombra * 0.75).astype(np.uint8)]), ang, esc)
            cy = 1130 + 14 * math.sin(t * 1.1)
            colar(img, sh, 580, cy + 40, 1 - sai, 1, True); colar(img, g, 560, cy, 1 - sai, 1, True)
            for nome, fx, fy, fs, ff in self.frente:
                colar(img, self.L(nome), fx + 15 * math.cos(t * 0.9 + ff), fy + 40 * math.sin(t * 1.2 + ff), 1 - sai, fs, True)
            if self.t0 <= t < self.tfim and self.tem("tag"):
                colar(img, self.L("tag"), 260, 430 + 14 * math.sin(t * 1.1), jan(t, self.t0, 0.3), 1, True)
        if t < self.t0:
            img = (img * 0.42).astype(np.uint8); e = jan(t, 0.1, 0.35)
            if self.tem("g_vit"): colar(img, self.L("g_vit"), W / 2, 900 + (1 - eo(e)) * 60, e, 1, True)
        elif t < self.tfim:
            dt = t - ta; e = eb(min(dt / 0.35, 1))
            colar(img, self.L(f"tit{p}"), 20 - (1 - e) * 200, 190, min(dt / 0.2, 1))
            for card, ini, fim, k in self.lupas:
                if ini <= t < fim:
                    e = eb(jan(t, ini, 0.3)); s = 1 - jan(t, fim - 0.25, 0.25)
                    colar(img, girar(card, 5), 300, 1380, s, 0.3 + 0.7 * e, True)
                    if self.tem(f"etq{k}"): colar(img, self.L(f"etq{k}"), 300, 1380 + card.shape[0] / 2 + 60, s * jan(t, ini + 0.2, 0.25), 1, True)
        if 0 <= t - self.t0 < 0.15: img = flash(img, 0.5 * (1 - (t - self.t0) / 0.15))
        if t < self.tfim + 0.3: colar(img, self.L("selo"), W - 220, 160)
        if t >= self.tfim:
            colar(img, self.L("selo_g"), W / 2, 420, jan(t, self.tfim + 0.2, 0.35), 0.7 + 0.3 * eb(jan(t, self.tfim + 0.2, 0.35)), True)
            e2 = jan(t, self.tfim + 0.4, 0.35); colar(img, self.L("final_txt"), W / 2, 920 + (1 - eo(e2)) * 50, e2, 1, True)
            colar(img, self.L("handle"), W / 2, 1460, jan(t, self.tfim + 0.8, 0.3), 1.25, True)
        return img


def exportar(R):
    os.makedirs(os.path.dirname(R.saida), exist_ok=True)
    mus = R.r.get("musica", "A"); wav = None
    if mus in ("A", "B"):
        wav = os.path.join(R.trab, "trilha.wav")
        subprocess.run(["python3", os.path.join(AQUI, "musica.py"), mus, wav, f"{R.total:.3f}", f"{R.t0:.4f}"], check=True)
    elif mus: wav = R.rel(mus)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-"]
    cmd += (["-i", wav, "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"] if wav else
            ["-f", "lavfi", "-t", f"{R.total}", "-i", "anullsrc=r=44100:cl=stereo", "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-shortest"])
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-movflags", "+faststart", R.saida]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for f in range(int(round(R.total * FPS))): ff.stdin.write(R.quadro(f).tobytes())
    ff.stdin.close(); ff.wait()
    cv2.imwrite(os.path.splitext(R.saida)[0] + "-capa.jpg", R.quadro(int((R.t0 + 0.6) * FPS)), [cv2.IMWRITE_JPEG_QUALITY, 92])
    print("ok", R.saida, f"{R.total:.1f}s")


def previa(R):
    ts = [0.6, R.t0 - 0.2] + [a + 0.6 for _, a, _ in R.passos] + [R.tfim + 1.5]
    ims = [cv2.resize(R.quadro(int(t * FPS)), (270, 480), interpolation=cv2.INTER_AREA) for t in ts]
    while len(ims) % 6: ims.append(np.zeros((480, 270, 3), np.uint8))
    p = os.path.splitext(R.saida)[0] + "-previa.jpg"
    os.makedirs(os.path.dirname(p), exist_ok=True)
    cv2.imwrite(p, np.vstack([np.hstack(ims[i:i + 6]) for i in range(0, len(ims), 6)])); print("prévia", p)


if __name__ == "__main__":
    est = json.load(open(sys.argv[1], encoding="utf-8")).get("estilo", "tela_cheia")
    R = (Vitrine if est == "vitrine" else TelaCheia)(sys.argv[1])
    R.quadros(); R.camadas(); R.preparar(); previa(R)
    if "--previa" not in sys.argv: exportar(R)
