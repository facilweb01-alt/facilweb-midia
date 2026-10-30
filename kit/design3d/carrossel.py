"""Carrossel 3D para Instagram (1080x1350) a partir de um JSON. Funciona para qualquer marca (marca.json).

Uso: python3 carrossel.py roteiro.json
Saída: <saida>/slide-01.jpg ... (JPEG pronto para a API do Instagram) + <saida>/previa.jpg

Roteiro (exemplo completo em exemplos/carrossel-exemplo.json):
{
  "marca": "marca.json",
  "saida": "saida/carrossel",
  "slides": [
    {"tipo": "capa", "titulo": "SEU DELIVERY<br>VENDENDO <span>SOZINHO</span>", "texto": "...", "telas": ["a.png", "b.png", "c.png"]},
    {"tipo": "numero", "grande": "R$", "titulo": "...", "texto": "...", "nota": "Exemplo com comissão de 23%."},
    {"tipo": "lateral", "num": "01", "titulo": "Cardápio <span>digital</span>", "texto": "...", "tela": "cardapio.png"},
    {"tipo": "cta", "titulo": "Comenta <span>QUERO</span>", "texto": "...", "chip": "COMENTA QUERO", "tela": "painel.png"},
    {"tipo": "texto", "titulo": "...", "texto": "..."}
  ]
}
<span> no título pinta a palavra com a cor de destaque; <b> no texto também.
Telas: imagens 600x1300 (gere com tela.py). Caminhos relativos ao JSON.
Regras do layout: o celular nunca é cortado; texto em coluna à esquerda nos slides laterais;
logo em selo branco em todo slide; rodapé com @ e site.
"""
import base64, json, os, random, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lib"))
import marca as M
from comp import renderizar_camadas
import motor3d as m3d

W, H = 1080, 1350


def cena_slide(s, base, cores, idx):
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    t = s["tipo"]
    moedas_lado = [m3d.moeda([0.05, -0.85, 0.8], [1.1, 0.2, 0.5], 0.9), m3d.esfera(cores["destaque"], [1.0, 0.55, 0.4], 0.8),
                   m3d.esfera(cores["acento"], [0.95, -0.9, 0.5], 0.6)]
    if t in ("lateral", "cta") and s.get("tela"):
        return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": [m3d.celular(rel(s["tela"]), [0.52, -0.12, 0], [0.06, -0.38, 0.03], 1.0)],
                "moedas": moedas_lado if s.get("moedas", True) else []}
    if t == "capa" and s.get("telas"):
        tl = [rel(x) for x in s["telas"]][:3]
        if len(tl) == 1:
            ph = [m3d.celular(tl[0], [0, -0.52, 0.25], [0.07, -0.1, 0], 0.68)]
        else:
            ph = [m3d.celular(tl[1 % len(tl)], [-0.6, -0.56, -0.4], [0.05, 0.5, 0.1], 0.6),
                  m3d.celular(tl[2 % len(tl)], [0.6, -0.56, -0.4], [0.05, -0.5, -0.1], 0.6),
                  m3d.celular(tl[0], [0, -0.52, 0.25], [0.07, -0.1, 0], 0.68)]
        return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": ph,
                "moedas": [m3d.moeda([-1.05, 0.05, 0.5], None, 0.9), m3d.moeda([1.05, -0.05, 0.6], [0.6, 0.4, 0.9], 0.85),
                           m3d.esfera(cores["destaque"], [-0.95, -0.95, 0.7], 0.8), m3d.esfera(cores["acento"], [0.95, -0.95, 0.8], 0.6)]}
    if t == "numero" and s.get("moedas", True):
        random.seed(idx)
        return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": [],
                "moedas": [m3d.moeda([random.uniform(-1.2, 1.2), random.uniform(-1.15, -0.25), random.uniform(-0.6, 1.2)],
                                     [random.uniform(0.3, 1.5), random.uniform(0, 3), random.uniform(-1, 1)], random.uniform(0.8, 1.25)) for _ in range(22)]}
    return None


def css(m):
    c = m["cores"]
    return M.css_vars(m) + M.fundo_css(m, W, H) + f"""
body{{width:{W}px;height:{H}px;overflow:hidden;position:relative;color:#fff}}
.tres{{position:absolute;inset:0}}
.selo{{position:absolute;top:60px;left:80px;width:130px;height:130px;padding:11px;background:#fff;border-radius:28px;box-shadow:0 14px 40px rgba(0,0,0,.35)}} .selo img{{width:108px;display:block}}
.selo.txt{{display:flex;align-items:center;justify-content:center;color:{c['primaria']};font-weight:900;font-size:22px;text-align:center}}
.pag{{position:absolute;top:96px;right:80px;font-size:26px;font-weight:700;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:6px 18px;border-radius:30px}}
h1{{font-weight:900;letter-spacing:-1px;line-height:1.02;text-shadow:0 6px 24px rgba(0,0,0,.35)}} h1 span{{color:{c['destaque']}}}
p{{line-height:1.3;font-weight:500;margin-top:24px}} p b{{color:{c['destaque']}}} small{{display:block;font-size:24px;opacity:.65;margin-top:14px}}
.col{{position:absolute;left:80px;width:470px;top:300px}} .col h1{{font-size:76px}} .col p{{font-size:34px}}
.num{{display:inline-flex;align-items:center;justify-content:center;min-width:96px;height:96px;padding:0 16px;border-radius:28px;background:{c['acento']};font-weight:900;font-size:50px;
 margin-bottom:30px;box-shadow:0 12px 30px {M.rgba(c['acento'],.45)};transform:rotate(-6deg)}}
.topo{{position:absolute;left:80px;right:80px;top:240px;text-align:center}} .topo h1{{font-size:92px}} .topo p{{font-size:38px;max-width:820px;margin-left:auto;margin-right:auto}}
.meio{{position:absolute;left:90px;right:90px;top:50%;transform:translateY(-50%);text-align:center}} .meio h1{{font-size:96px}} .meio p{{font-size:40px}}
.big{{position:absolute;right:60px;top:180px;font-size:330px;font-weight:900;line-height:1;color:transparent;-webkit-text-stroke:3px {M.rgba(c['destaque'],.3)}}}
.chip{{display:inline-block;margin-top:36px;background:{c['acento']};font-weight:800;font-size:38px;padding:20px 44px;border-radius:60px;box-shadow:0 14px 30px {M.rgba(c['acento'],.45)}}}
.rodape{{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(180deg,{M.rgba(c['escura'],0)},{M.rgba(c['escura'],.92)} 65%)}}
.handle{{position:absolute;bottom:46px;left:80px;font-size:28px;font-weight:700}} .site{{position:absolute;bottom:46px;right:80px;font-size:24px;opacity:.7}}
"""


def html_slide(m, s, i, total, img3d):
    logo = M.logo_data_uri(m)
    selo = f'<div class="selo"><img src="{logo}"></div>' if logo else f'<div class="selo txt">{m["nome"]}</div>'
    t = s["tipo"]
    tit, txt = s.get("titulo", ""), s.get("texto", "")
    nota = f"<small>{s['nota']}</small>" if s.get("nota") else ""
    if t in ("lateral", "cta"):
        badge = f'<div class="num">{s["num"]}</div>' if s.get("num") else ""
        chip = f'<div class="chip">{s["chip"]}</div>' if s.get("chip") else ""
        corpo = f'<div class="col">{badge}<h1>{tit}</h1><p>{txt}{nota}</p>{chip}</div>'
    elif t == "texto":
        corpo = f'<div class="meio"><h1>{tit}</h1><p>{txt}{nota}</p></div>'
    else:
        grande = f'<div class="big">{s["grande"]}</div>' if s.get("grande") else ""
        corpo = f'{grande}<div class="topo"><h1>{tit}</h1><p>{txt}{nota}</p></div>'
    tres = f'<img class="tres" src="data:image/png;base64,{base64.b64encode(open(img3d, "rb").read()).decode()}">' if img3d else ""
    rod = f'<div class="rodape"></div><div class="handle">{m.get("handle","")}</div><div class="site">{m.get("site","")}</div>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>*{{margin:0;padding:0;box-sizing:border-box}}{css(m)}</style></head><body>'
            f'{M.fundo_html(m, W, H)}{tres}{selo}<div class="pag">{i}/{total}</div>{corpo}{rod}</body></html>')


def main(roteiro):
    base = os.path.dirname(os.path.abspath(roteiro))
    r = json.load(open(roteiro, encoding="utf-8"))
    m = M.carregar(os.path.join(base, r["marca"]) if not os.path.isabs(r["marca"]) else r["marca"])
    saida = os.path.join(base, r.get("saida", "saida/carrossel")); os.makedirs(saida, exist_ok=True)
    pasta3d = os.path.join(saida, "_3d")
    cenas = {}
    for i, s in enumerate(r["slides"], 1):
        c = cena_slide(s, base, m["cores"], i)
        if c: cenas[f"s{i:02d}"] = c
    if cenas: m3d.renderizar(cenas, pasta3d)
    itens = {}
    total = len(r["slides"])
    for i, s in enumerate(r["slides"], 1):
        img = os.path.join(pasta3d, f"s{i:02d}.png")
        itens[f"slide-{i:02d}"] = (html_slide(m, s, i, total, img if os.path.exists(img) else None), True)
    renderizar_camadas(itens, saida, W, H)
    from PIL import Image
    ims = []
    for i in range(1, total + 1):
        p = os.path.join(saida, f"slide-{i:02d}.png")
        im = Image.open(p).convert("RGB"); im.save(p[:-4] + ".jpg", quality=92); os.remove(p); ims.append(im)
    # prévia em grade
    col = 4; lw = 360; lh = int(lw * H / W); lin = (total + col - 1) // col
    prev = Image.new("RGB", (col * lw + (col + 1) * 10, lin * lh + (lin + 1) * 10), "white")
    for k, im in enumerate(ims):
        prev.paste(im.resize((lw, lh)), (10 + (k % col) * (lw + 10), 10 + (k // col) * (lh + 10)))
    prev.save(os.path.join(saida, "previa.jpg"), quality=88)
    print("ok", saida, total, "slides")


if __name__ == "__main__":
    main(sys.argv[1])
