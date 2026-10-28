"""Gera as artes da semana 29/10 a 31/10/2026 do @facilweb, todas com a logomarca.

Saída:
  carrossel/slide-01..08.png   1080x1350  (post de 29/10)
  reel/capa-reel-maroca.png    1080x1920  (capa do reel de 31/10)
  stories/story-01..03.png     1080x1920
"""
import asyncio, base64, os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "logo.png"), "rb").read()).decode()
AZUL, AZUL2, VERDE, LARANJA = "#0A3D9E", "#062a73", "#8DC63F", "#F7941D"

BASE_CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:Poppins,Inter,sans-serif;color:#fff;overflow:hidden;position:relative;
 background:radial-gradient(circle at 85% 10%,#1758d6 0,{AZUL} 40%,{AZUL2} 100%)}}
.selo{{position:absolute;background:#fff;border-radius:28px;display:flex;align-items:center;
 justify-content:center;box-shadow:0 10px 30px rgba(0,0,0,.25)}}
.selo img{{display:block}}
h1{{font-weight:800;line-height:1.02}} h1 span,h2 span{{color:{VERDE}}}
h2{{font-weight:800;line-height:1.1}}
p,li{{font-weight:500;line-height:1.35}} p b{{color:{VERDE};font-weight:700}}
.barra{{width:140px;height:12px;background:{VERDE};border-radius:6px}}
.botao{{display:inline-block;background:{LARANJA};color:#fff;font-weight:800;border-radius:60px}}
ol{{padding-left:60px}} li::marker{{color:{VERDE};font-weight:800}}
"""

# ---------------- carrossel 1080x1350 ----------------
FEED_CSS = BASE_CSS + f"""
body{{width:1080px;height:1350px}}
.selo{{top:60px;left:110px;width:150px;height:150px;padding:14px}} .selo img{{width:122px}}
.num{{position:absolute;top:110px;right:120px;font-size:30px;font-weight:600;opacity:.8}}
.wrap{{position:absolute;inset:260px 120px 170px 120px;display:flex;flex-direction:column;justify-content:center}}
.handle{{position:absolute;bottom:70px;left:120px;font-size:30px;opacity:.85}}
.site{{position:absolute;bottom:70px;right:120px;font-size:26px;opacity:.6}}
h1{{font-size:112px}} h2{{font-size:74px;margin-bottom:48px}}
p,li{{font-size:46px}} li{{margin-bottom:28px}}
.barra{{margin-bottom:52px}} .sub{{margin-top:52px;font-size:46px;font-weight:500;opacity:.92}}
.botao{{margin-top:70px;font-size:46px;padding:28px 56px;align-self:flex-start}}
"""

CARROSSEL = [
    ("capa", "4 JEITOS DE<br>PEDIDO <span>SEM<br>COMISSÃO</span>",
     "Como fazer o cliente pedir direto com você"),
    ("texto", "Faz a conta",
     "Todo pedido que entra pelo app paga comissão.<br><br><b>Todo pedido que entra pelo seu canal é seu.</b>"),
    ("item", "1. Cardápio no link da bio",
     "Quem te encontra no Instagram cai direto no seu cardápio, não no app."),
    ("item", "2. QR code na embalagem",
     "Quem pediu pelo app recebe, junto com a comida, o caminho pro seu cardápio."),
    ("item", "3. Cupom na 1ª compra direta",
     "Um desconto uma vez só, pro cliente experimentar pedir com você."),
    ("item", "4. WhatsApp que vende sozinho",
     "Cardápio digital no WhatsApp, e o pedido já sai impresso na cozinha."),
    ("resumo", "Salva pra fazer essa semana",
     "<ol><li>Cardápio no link da bio</li><li>QR code na embalagem</li>"
     "<li>Cupom na 1ª compra direta</li><li>WhatsApp com cardápio digital</li></ol>"),
    ("cta", "Comenta <span>DEMO</span>",
     "que a gente te mostra os 4 funcionando no sistema da Fácil Web."),
]


def feed_page(i, kind, title, body):
    if kind == "capa":
        inner = f'<div class="barra"></div><h1>{title}</h1><div class="sub">{body}</div>'
    elif kind == "cta":
        inner = f'<h2>{title}</h2><p>{body}</p><div class="botao">COMENTA DEMO</div>'
    elif kind == "resumo":
        inner = f'<h2>{title}</h2>{body}'
    else:
        inner = f'<div class="barra"></div><h2>{title}</h2><p>{body}</p>'
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FEED_CSS}</style></head><body>'
            f'<div class="selo"><img src="data:image/png;base64,{LOGO}"></div>'
            f'<div class="num">{i}/{len(CARROSSEL)}</div><div class="wrap">{inner}</div>'
            f'<div class="handle">@facilweb</div><div class="site">facilwebdelivery.com.br</div></body></html>')


# ---------------- vertical 1080x1920 (capa de reel e stories) ----------------
# Área segura: nada acima de y=250 nem abaixo de y=1600 (stories);
# a capa do reel aparece cortada no grid, então o texto fica no centro.
VERT_CSS = BASE_CSS + f"""
body{{width:1080px;height:1920px}}
.selo{{top:280px;left:50%;transform:translateX(-50%);width:230px;height:230px;padding:22px}}
.selo img{{width:186px}}
.wrap{{position:absolute;left:110px;right:110px;top:600px;bottom:330px;display:flex;
 flex-direction:column;justify-content:center;align-items:center;text-align:center}}
h1{{font-size:118px}} h2{{font-size:84px;margin-bottom:44px}}
p{{font-size:52px}}
.barra{{margin:0 auto 52px}}
.sub{{margin-top:52px;font-size:52px;font-weight:500;opacity:.92}}
.botao{{margin-top:64px;font-size:52px;padding:30px 64px}}
.sticker{{margin-top:64px;width:760px;height:260px;border:5px dashed rgba(255,255,255,.55);
 border-radius:36px;display:flex;align-items:center;justify-content:center;font-size:34px;opacity:.75}}
.handle{{position:absolute;bottom:340px;left:0;right:0;text-align:center;font-size:34px;opacity:.8}}
"""

VERTICAIS = [
    ("reel/capa-reel-maroca.png",
     '<div class="barra"></div><h1>NUNCA<br>TROCARAM<br>DE SISTEMA<br>EM <span>4 ANOS</span></h1>'
     '<div class="sub">Fomos no Maroca\'s, no Bessa, perguntar por quê</div>'),
    # Stories publicados pela API: a API não coloca figurinha (enquete, link, menção),
    # então cada story funciona sozinho. Resposta ao story chega no direct.
    ("stories/story-01.png",
     '<h2>Post <span>novo</span> no feed</h2>'
     '<p>4 jeitos de o cliente pedir direto com você, sem comissão</p>'
     '<div class="botao">Toque no @facilweb</div>'),
    ("stories/story-02.png",
     '<h2>Você ainda paga <span>comissão</span> em cada pedido?</h2>'
     '<p>Responde esse story com <b>SIM</b> ou <b>NÃO</b>.<br>A gente te conta o que fazer.</p>'),
    ("stories/story-03.png",
     '<h2>Quer ver o sistema <span>funcionando</span>?</h2>'
     '<p>Demonstração gratuita pelo WhatsApp</p>'
     '<div class="botao">Link na bio</div>'),
]


def vert_page(inner, handle=True):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{VERT_CSS}</style></head><body>'
            f'<div class="selo"><img src="data:image/png;base64,{LOGO}"></div>'
            f'<div class="wrap">{inner}</div>'
            + ('<div class="handle">@facilweb</div>' if handle else '') + '</body></html>')


async def main():
    for d in ("carrossel", "reel", "stories"):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for i, s in enumerate(CARROSSEL, 1):
            await pg.set_content(feed_page(i, *s))
            await pg.wait_for_timeout(150)
            await pg.screenshot(path=os.path.join(HERE, "carrossel", f"slide-{i:02d}.png"))
        await pg.set_viewport_size({"width": 1080, "height": 1920})
        for path, inner in VERTICAIS:
            await pg.set_content(vert_page(inner))
            await pg.wait_for_timeout(150)
            await pg.screenshot(path=os.path.join(HERE, path))
        await b.close()

asyncio.run(main())
