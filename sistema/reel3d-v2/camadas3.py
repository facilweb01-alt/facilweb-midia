"""Camadas do reel 3D v2 @facilweb ("Seu delivery vendendo sozinho")."""
import asyncio, base64, os
from playwright.async_api import async_playwright

OUT = "/home/claude/reel3d-v2/camadas"
LOGO = "data:image/png;base64," + base64.b64encode(open("/home/claude/marca/logo.png", "rb").read()).decode()
CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{background:transparent}
body{font-family:Poppins,sans-serif;color:#fff;display:inline-block} #e{display:inline-block} .v{color:#8DC63F} .l{color:#F7941D}"""
def el(html, css=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{css}</style></head><body><div id="e">{html}</div></body></html>'

FUNDO = el('<div class="f"><div class="g"></div><div class="a a1"></div><div class="a a2"></div><div class="o o1"></div><div class="o o2"></div></div>',
 """.f{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(900px 800px at 85% 5%,#1f6bf0 0,rgba(31,107,240,0) 70%),
 radial-gradient(800px 700px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
 .g{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
 background-size:60px 60px;mask-image:linear-gradient(180deg,transparent,#000 20%,#000 80%,transparent)}
 .a{position:absolute;border-radius:50%;border:3px solid rgba(141,198,63,.22)} .a1{width:1000px;height:1000px;left:-520px;top:-300px}
 .a2{width:760px;height:760px;right:-420px;bottom:-160px;border-color:rgba(247,148,29,.22)}
 .o{position:absolute;border-radius:50%;filter:blur(110px)} .o1{width:560px;height:560px;background:#8DC63F;opacity:.35;left:-220px;top:1300px}
 .o2{width:460px;height:460px;background:#F7941D;opacity:.28;right:-180px;top:600px}""")
SELO = el(f'<div class="s"><img src="{LOGO}"></div>', ".s{width:150px;height:150px;padding:13px;background:#fff;border-radius:34px;margin:30px;box-shadow:0 14px 34px rgba(0,0,0,.45)} .s img{width:100%;display:block}")
SELO_G = el(f'<div class="s"><img src="{LOGO}"></div>', ".s{width:300px;height:300px;padding:26px;background:#fff;border-radius:66px;margin:50px;box-shadow:0 24px 60px rgba(0,0,0,.45)} .s img{width:100%;display:block}")
T = lambda txt, size=72, w=900, extra="": el(f'<div class="t">{txt}</div>', f".t{{width:{w}px;text-align:center;font-weight:900;font-size:{size}px;line-height:1.04;letter-spacing:-1px;padding:20px;text-shadow:0 10px 34px rgba(0,0,0,.5)}} {extra}")
CONT = lambda v: el(f'<div class="c">R$ {v}</div>', ".c{font-weight:900;font-size:210px;letter-spacing:-6px;color:#F7941D;padding:10px 30px;text-shadow:0 14px 50px rgba(247,148,29,.45),0 8px 0 rgba(4,29,85,.6)}")
NUM = lambda n: el(f'<div class="n">{n:02d}</div>', ".n{font-weight:900;font-size:430px;line-height:1;color:transparent;-webkit-text-stroke:4px rgba(141,198,63,.42);padding:10px}")
PAL = lambda w: el(f'<div class="w">{w}<i></i></div>', ".w{font-weight:900;font-size:128px;line-height:.95;letter-spacing:-3px;padding:20px 30px;text-shadow:0 10px 40px rgba(0,0,0,.55)} .w i{display:block;height:14px;width:62%;background:#8DC63F;border-radius:10px;margin-top:12px}")
SUB = lambda s: el(f'<div class="b">{s}</div>', ".b{font-weight:700;font-size:46px;padding:12px 30px;background:rgba(4,29,85,.86);border:2px solid rgba(255,255,255,.14);border-radius:22px;margin:20px;box-shadow:0 12px 30px rgba(0,0,0,.4)} .b span{color:#8DC63F}")
CHIP = lambda i: el(f'<div class="c">{i}/5</div>', ".c{font-weight:900;font-size:42px;background:#F7941D;padding:10px 26px;border-radius:40px;margin:20px;box-shadow:0 10px 26px rgba(247,148,29,.5)}")
ETQ = lambda a: el(f'<div class="e">{a}</div>', ".e{background:#fff;color:#041d55;font-weight:900;font-size:36px;border-radius:22px;padding:14px 26px;margin:20px;box-shadow:0 14px 34px rgba(0,0,0,.4)}")
HANDLE = el('<div class="h">@facilweb · facilwebdelivery.com.br</div>', ".h{font-size:40px;font-weight:600;opacity:.9;padding:10px}")

FERR = [("CARDÁPIO", "com a sua marca, <span>sem baixar app</span>", "O pedido entra pelo seu link"),
        ("ROLETA", "o cupom <span>já entra no pedido</span>", "Gira e ganha desconto"),
        ("PONTOS", "cada pedido <span>vira ponto</span>", "Ele volta pra trocar"),
        ("CARRINHO", "desistiu? <span>o WhatsApp chama</span>", "Recupera a venda sozinho"),
        ("ARTES", "prontas <span>pra postar</span>", "Com o seu cardápio e link")]

async def main():
    os.makedirs(OUT, exist_ok=True)
    it = {"fundo": FUNDO, "selo": SELO, "selo_g": SELO_G, "handle": HANDLE,
          "h_topo": T("Você paga", 74), "h_base": T("por mês de comissão<br>pro app de delivery?", 60),
          "h_nota": T("Exemplo: R$ 20 mil vendidos no app, comissão de 23%", 28, 900, ".t{font-weight:500;opacity:.75;letter-spacing:0}"),
          "b_1": T("E se esse dinheiro<br><span class='v'>ficasse com você?</span>", 84),
          "b_2": T("5 ferramentas que<br>vendem <span class='v'>sozinhas</span>", 84),
          "f_1": T("Seu delivery<br><span class='v'>vendendo sozinho</span>", 96),
          "f_2": T("Sem comissão por pedido", 52, 900, ".t{font-weight:700}"),
          "f_3": T("Sistema para restaurante <span class='l'>Fácil Web</span>", 40, 1000, ".t{font-weight:600}")}
    for i, (w, s, e) in enumerate(FERR, 1):
        it[f"num{i}"] = NUM(i); it[f"pal{i}"] = PAL(w); it[f"sub{i}"] = SUB(s); it[f"chip{i}"] = CHIP(i); it[f"etq{i}"] = ETQ(e)
    for k in range(30):
        v = round(4600 * (1 - (1 - k / 29) ** 3))
        it[f"cont{k:02d}"] = CONT(f"{v:,}".replace(",", "."))
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for n, h in it.items():
            await pg.set_content(h); await pg.wait_for_timeout(80)
            await pg.locator("#e").screenshot(path=f"{OUT}/{n}.png", omit_background=True)
        await b.close()
    print(len(it))

asyncio.run(main())
