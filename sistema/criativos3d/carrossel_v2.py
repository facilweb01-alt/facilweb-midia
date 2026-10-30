"""Carrossel 3D v2 @facilweb (1080x1350): celular inteiro à direita, texto em coluna à esquerda, nada cortado."""
import asyncio, base64, json, os, subprocess
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO = b64("/home/claude/marca/logo.png")
W, H = 1080, 1350
OUT3D, OUT = os.path.join(HERE, "out3d_v2"), os.path.join(HERE, "carrossel_v2")

def phone(tex, pos, rot, s=1.0): return {"tex": f"telas/{tex}.png", "pos": pos, "rot": rot, "s": s, "sombra": False}
def lateral(tex):
    return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone(tex, [0.52, -0.12, 0], [0.06, -0.38, 0.03], 1.0)],
            "moedas": [{"pos": [0.05, -0.85, 0.8], "rot": [1.1, 0.2, 0.5], "s": 0.9},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [1.0, 0.55, 0.4], "s": 0.8},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [0.95, -0.9, 0.5], "s": 0.6}]}
import random
random.seed(7)
CENAS = {
    "s01": {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone("roleta", [-0.6, -0.56, -0.4], [0.05, 0.5, 0.1], 0.6), phone("carrinho", [0.6, -0.56, -0.4], [0.05, -0.5, -0.1], 0.6),
                       phone("cardapio", [0, -0.52, 0.25], [0.07, -0.1, 0], 0.68)],
            "moedas": [{"pos": [-1.05, 0.05, 0.5], "s": 0.9}, {"pos": [1.05, -0.05, 0.6], "rot": [0.6, 0.4, 0.9], "s": 0.85},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [-0.95, -0.95, 0.7], "s": 0.8}, {"tipo": "esfera", "cor": "#F7941D", "pos": [0.95, -0.95, 0.8], "s": 0.6}]},
    "s02": {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": [],
            "moedas": [{"pos": [random.uniform(-1.2, 1.2), random.uniform(-1.15, -0.25), random.uniform(-0.6, 1.2)],
                        "rot": [random.uniform(0.3, 1.5), random.uniform(0, 3), random.uniform(-1, 1)], "s": random.uniform(0.8, 1.25)} for _ in range(22)]},
    "s03": lateral("cardapio"), "s04": lateral("roleta"), "s05": lateral("pontos"), "s06": lateral("carrinho"), "s07": lateral("artes"),
    "s08": lateral("economia"),
}
TEXTOS = {
    "s01": (None, "SEU DELIVERY<br>VENDENDO <span>SOZINHO</span>", "5 ferramentas que já vêm no sistema. <b>Sem comissão por pedido.</b>"),
    "s02": ("R$", "R$ 20 mil no app.<br><span>R$ 4.600</span> de comissão.", "Todo mês. Esse dinheiro pode ficar com você.<small>Exemplo com comissão de 23%.</small>"),
    "s03": ("01", "Cardápio digital <span>com a sua marca</span>", "O cliente pede pelo seu link, sem baixar app."),
    "s04": ("02", "Roleta de <span>desconto</span>", "Ele gira, ganha o cupom e o código já entra no pedido."),
    "s05": ("03", "Pontos de <span>fidelidade</span>", "Cada pedido vira ponto. Ele volta para trocar."),
    "s06": ("04", "Carrinho <span>abandonado</span>", "Desistiu? Meia hora depois o sistema chama de volta no WhatsApp."),
    "s07": ("05", "Artes prontas <span>pra postar</span>", "Com o seu cardápio no celular e o link do seu delivery."),
    "s08": (None, "Comenta <span>QUERO</span>", "e a gente te mostra as 5 funcionando no seu restaurante."),
}
CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;position:relative;font-family:Poppins,sans-serif;color:#fff;
 background:radial-gradient(900px 700px at 85% 10%,#1f6bf0 0,rgba(31,107,240,0) 70%),radial-gradient(700px 600px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(160deg,#0A3D9E,#041d55)}
.grade{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
 background-size:60px 60px;mask-image:linear-gradient(180deg,transparent,#000 25%,#000 75%,transparent)}
.brilho{position:absolute;border-radius:50%;filter:blur(90px)}
.anel{position:absolute;border-radius:50%;border:3px solid rgba(141,198,63,.2)}
.tres{position:absolute;inset:0}
.selo{position:absolute;top:60px;left:80px;width:130px;height:130px;padding:11px;background:#fff;border-radius:28px;box-shadow:0 14px 40px rgba(0,0,0,.35)} .selo img{width:108px;display:block}
.pag{position:absolute;top:96px;right:80px;font-size:26px;font-weight:700;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:6px 18px;border-radius:30px}
h1{font-weight:900;letter-spacing:-1px;line-height:1.02;text-shadow:0 6px 24px rgba(0,0,0,.35)} h1 span{color:#8DC63F}
p{line-height:1.3;font-weight:500;margin-top:24px} p b{color:#8DC63F} small{display:block;font-size:24px;opacity:.65;margin-top:14px}
.col{position:absolute;left:80px;width:470px;top:300px} .col h1{font-size:76px} .col p{font-size:34px}
.num{display:inline-flex;align-items:center;justify-content:center;width:96px;height:96px;border-radius:28px;background:#F7941D;font-weight:900;font-size:50px;
 margin-bottom:30px;box-shadow:0 12px 30px rgba(247,148,29,.45);transform:rotate(-6deg)}
.topo{position:absolute;left:80px;right:80px;top:240px;text-align:center} .topo h1{font-size:92px} .topo p{font-size:38px;max-width:820px;margin-left:auto;margin-right:auto}
.big{position:absolute;right:60px;top:180px;font-size:330px;font-weight:900;line-height:1;color:transparent;-webkit-text-stroke:3px rgba(141,198,63,.3)}
.chip{display:inline-block;margin-top:36px;background:#F7941D;font-weight:800;font-size:38px;padding:20px 44px;border-radius:60px;box-shadow:0 14px 30px rgba(247,148,29,.45)}
.rodape{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(180deg,rgba(4,22,66,0),rgba(4,22,66,.9) 65%)}
.handle{position:absolute;bottom:46px;left:80px;font-size:28px;font-weight:700} .site{position:absolute;bottom:46px;right:80px;font-size:24px;opacity:.7}
"""

def slide(i, nome, total):
    num, t, d = TEXTOS[nome]
    lateral = nome in ("s03", "s04", "s05", "s06", "s07", "s08")
    if lateral:
        badge = f'<div class="num">{num}</div>' if num else ""
        chip = '<div class="chip">COMENTA QUERO</div>' if nome == "s08" else ""
        txt = f'<div class="col">{badge}<h1>{t}</h1><p>{d}</p>{chip}</div>'
        big = ""
    else:
        txt = f'<div class="topo"><h1>{t}</h1><p>{d}</p></div>'
        big = '<div class="big">R$</div>' if nome == "s02" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="grade"></div><div class="anel" style="width:900px;height:900px;left:-470px;top:-330px"></div>
<div class="brilho" style="width:520px;height:520px;background:#8DC63F;opacity:.4;left:-200px;top:900px"></div>
<div class="brilho" style="width:420px;height:420px;background:#F7941D;opacity:.3;right:-160px;top:380px"></div>{big}
<img class="tres" src="{b64(os.path.join(OUT3D, nome + '.png'))}">
<div class="selo"><img src="{LOGO}"></div><div class="pag">{i}/{total}</div>{txt}
<div class="rodape"></div><div class="handle">@facilweb</div><div class="site">facilwebdelivery.com.br</div></body></html>"""

async def compor():
    os.makedirs(OUT, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": W, "height": H})
        for i, n in enumerate(CENAS, 1):
            await pg.set_content(slide(i, n, len(CENAS))); await pg.wait_for_timeout(250)
            await pg.screenshot(path=os.path.join(OUT, f"slide-{i:02d}.png"))
        await b.close()

if __name__ == "__main__":
    import sys
    if "--so-compor" not in sys.argv:
        json.dump(CENAS, open(os.path.join(HERE, "cenas_carrossel_v2.json"), "w"))
        subprocess.run(["node", "render3d.js", "cenas_carrossel_v2.json", OUT3D], cwd=HERE, check=True, env={**os.environ, "PORTA": "8775"})
    asyncio.run(compor())
