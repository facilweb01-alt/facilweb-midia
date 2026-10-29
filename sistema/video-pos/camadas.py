"""Camadas do vídeo POS @facilweb (1080x1920): fundo, moldura do vídeo, textos e encerramento."""
import asyncio, base64, os
from playwright.async_api import async_playwright

OUT = "/home/claude/video-pos/camadas"
LOGO = "data:image/png;base64," + base64.b64encode(open("/home/claude/marca/logo.png", "rb").read()).decode()
W, H = 1080, 1920
# área do vídeo dentro da arte
CX, CY, CW, CH, R = 150, 360, 780, 1386, 46

BASE = """*{margin:0;padding:0;box-sizing:border-box}body{width:1080px;height:1920px;overflow:hidden;position:relative;
font-family:Poppins,sans-serif;color:#fff;background:transparent}
h1{font-weight:900;letter-spacing:-1px;line-height:1.02} span.v{color:#8DC63F} span.l{color:#F7941D}
.selo{position:absolute;background:#fff;box-shadow:0 16px 44px rgba(0,0,0,.35)} .selo img{display:block;width:100%}
"""

def pagina(css, corpo):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{BASE}{css}</style></head><body>{corpo}</body></html>'

FUNDO = pagina("""body{background:radial-gradient(900px 800px at 85% 5%,#1f6bf0 0,rgba(31,107,240,0) 70%),
 radial-gradient(800px 700px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
.grade{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
 linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 60px;
 mask-image:linear-gradient(180deg,transparent,#000 25%,#000 80%,transparent)}
.anel{position:absolute;border-radius:50%;border:3px solid rgba(141,198,63,.25)}""",
 '<div class="grade"></div><div class="anel" style="width:900px;height:900px;left:-420px;top:-260px"></div>'
 '<div class="anel" style="width:700px;height:700px;right:-380px;bottom:-200px;border-color:rgba(247,148,29,.25)"></div>')

BRILHO = lambda cor, a: pagina(f"body{{width:900px;height:900px}} div{{position:absolute;inset:150px;border-radius:50%;background:{cor};filter:blur(120px);opacity:{a}}}", "<div></div>")

# sombra + brilho verde atrás do vídeo
SOMBRA = pagina(f""".c{{position:absolute;left:{CX}px;top:{CY}px;width:{CW}px;height:{CH}px;border-radius:{R}px;background:#041d55;
 box-shadow:0 40px 90px rgba(0,0,0,.55),0 0 0 14px rgba(141,198,63,.18),0 0 120px rgba(141,198,63,.35)}}""", '<div class="c"></div>')
BORDA = pagina(f""".c{{position:absolute;left:{CX - 6}px;top:{CY - 6}px;width:{CW + 12}px;height:{CH + 12}px;border-radius:{R + 6}px;
 border:6px solid #fff}} .v{{position:absolute;left:{CX + CW - 250}px;top:{CY - 26}px;background:#8DC63F;color:#041d55;font-weight:800;
 font-size:26px;padding:8px 22px;border-radius:30px;box-shadow:0 10px 24px rgba(0,0,0,.3)}}""",
 '<div class="c"></div><div class="v">SISTEMA REAL</div>')
MASCARA = pagina(f"body{{width:{CW}px;height:{CH}px;background:#000}} div{{position:absolute;inset:0;border-radius:{R}px;background:#fff}}", "<div></div>")

SELO = pagina(".selo{top:150px;left:70px;width:150px;height:150px;padding:13px;border-radius:34px}",
              f'<div class="selo"><img src="{LOGO}"></div>')
TOPO = pagina("h1{position:absolute;left:250px;right:50px;top:158px;font-size:58px}",
              '<h1>Cardápio e pagamento<br>na <span class="v">mesma maquininha</span></h1>')

GANCHO = pagina("""body{background:rgba(4,22,66,.55)} .t{position:absolute;left:70px;right:70px;top:640px;text-align:center;
 text-shadow:0 8px 30px rgba(0,0,0,.6)} h1{font-size:118px} p{font-size:58px;font-weight:700;margin-top:30px;white-space:nowrap}
 p b{background:#F7941D;padding:4px 22px;border-radius:18px;white-space:nowrap}""",
 '<div class="t"><h1>Pare de correr<br>até o <span class="v">caixa</span></h1><p>Sua mesa paga em <b>1 minuto</b></p></div>')

def passo(n, txt):
    return pagina(""".p{position:absolute;left:90px;top:1460px;display:flex;align-items:center;gap:22px;background:rgba(255,255,255,.97);
     color:#041d55;border-radius:70px;padding:16px 46px 16px 16px;box-shadow:0 18px 40px rgba(0,0,0,.4)}
     .n{width:92px;height:92px;border-radius:50%;background:#F7941D;color:#fff;font-weight:900;font-size:54px;display:flex;
     align-items:center;justify-content:center} .x{font-size:44px;font-weight:800;line-height:1.05}""",
     f'<div class="p"><div class="n">{n}</div><div class="x">{txt}</div></div>')

PASSOS = ["Escolhe a mesa", "Abre a comanda", "Lança pelo cardápio", "Cobra débito, crédito<br>ou Pix", "Comprovante na hora"]

def final(cta):
    return pagina("""body{background:radial-gradient(900px 800px at 50% 30%,#1f6bf0 0,rgba(31,107,240,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
     .selo{top:330px;left:50%;transform:translateX(-50%);width:300px;height:300px;padding:26px;border-radius:66px}
     .t{position:absolute;left:70px;right:70px;top:700px;text-align:center} .k{font-size:40px;font-weight:700;letter-spacing:6px;color:#8DC63F}
     h1{font-size:104px;margin-top:14px} p{font-size:46px;font-weight:500;margin-top:30px;line-height:1.3;opacity:.95}
     .chip{display:inline-block;margin-top:54px;background:#F7941D;font-weight:800;font-size:58px;padding:28px 66px;border-radius:80px;
     box-shadow:0 16px 40px rgba(247,148,29,.5)} .h{font-size:34px;font-weight:600;margin-top:40px;opacity:.85}""",
     f'<div class="selo"><img src="{LOGO}"></div><div class="t"><div class="k">SISTEMA POS</div>'
     '<h1>Tudo em<br><span class="v">um só lugar</span></h1>'
     '<p>Mesa, comanda, cardápio e pagamento<br>dentro da maquininha.</p>'
     f'<div class="chip">{cta}</div><div class="h">@facilweb · facilwebdelivery.com.br</div></div>')

CAPA = pagina("""body{background:transparent} .t{position:absolute;left:70px;right:70px;top:620px;text-align:center;text-shadow:0 8px 30px rgba(0,0,0,.7)}
 h1{font-size:120px} p{font-size:60px;font-weight:700;margin-top:30px} p b{background:#F7941D;padding:4px 22px;border-radius:18px}
 .f{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,22,66,.2),rgba(4,22,66,.75) 40%,rgba(4,22,66,.75) 60%,rgba(4,22,66,.2))}""",
 '<div class="f"></div><div class="t"><h1>Cardápio e<br>pagamento na<br><span class="v">maquininha</span></h1><p>Sistema <b>POS</b> Fácil Web</p></div>')


async def main():
    os.makedirs(OUT, exist_ok=True)
    itens = {"fundo": (FUNDO, W, H, False), "brilho_v": (BRILHO("#8DC63F", .55), 900, 900, True),
             "brilho_l": (BRILHO("#F7941D", .4), 900, 900, True), "sombra": (SOMBRA, W, H, True),
             "borda": (BORDA, W, H, True), "mascara": (MASCARA, CW, CH, False), "selo": (SELO, W, H, True),
             "topo": (TOPO, W, H, True), "gancho": (GANCHO, W, H, True), "capa_txt": (CAPA, W, H, True),
             "final_reels": (final("COMENTA DEMO"), W, H, False), "final_stories": (final("RESPONDE DEMO"), W, H, False)}
    for i, t in enumerate(PASSOS, 1):
        itens[f"passo{i}"] = (passo(i, t), W, H, True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for nome, (html, w, h, transp) in itens.items():
            pg = await b.new_page(viewport={"width": w, "height": h})
            await pg.set_content(html); await pg.wait_for_timeout(200)
            await pg.screenshot(path=f"{OUT}/{nome}.png", omit_background=transp)
            await pg.close()
        await b.close()

asyncio.run(main())
