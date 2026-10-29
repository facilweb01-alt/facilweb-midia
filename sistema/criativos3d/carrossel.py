"""Carrossel 3D @facilweb: gera cenas 3D (render3d.js) e compõe os slides 1080x1350 com texto e logo."""
import asyncio, base64, json, os, subprocess
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO = b64("" + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png") + "")
W, H = 1080, 1350


def phone(tex, pos, rot, s=1.0):
    return {"tex": f"telas/{tex}.png", "pos": pos, "rot": rot, "s": s}


def destaque(tex, lado):
    x = 0.55 if lado == "d" else -0.55
    ry = -0.42 if lado == "d" else 0.42
    return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone(tex, [x * 0.9, -0.8, 0], [0.1, ry, 0.06 if lado == "d" else -0.06], 1.08)],
            "moedas": [{"pos": [-x * 1.75, -0.75, 0.6], "rot": [1.1, 0.2, 0.5], "s": 1.1},
                       {"pos": [-x * 1.2, -1.2, 1.0], "rot": [0.5, 0.3, 1.1], "s": 0.8},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [x * 1.9, -0.25, 0.4], "s": 0.9},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [-x * 1.85, -1.3, 0.2], "s": 0.7}]}


def chuva():
    import random
    random.seed(7)
    m = []
    for i in range(26):
        m.append({"pos": [random.uniform(-1.3, 1.3), random.uniform(-1.45, -0.15), random.uniform(-0.8, 1.4)],
                  "rot": [random.uniform(0.3, 1.5), random.uniform(0, 3), random.uniform(-1, 1)],
                  "s": random.uniform(0.8, 1.3)})
    return m


CENAS = {
    "s01": {"w": W, "h": H, "fov": 28, "cam": [0, 0.1, 5.2],
            "phones": [phone("roleta", [-0.92, -1.05, -0.4], [0.05, 0.55, 0.12], 0.86),
                       phone("carrinho", [0.92, -1.05, -0.4], [0.05, -0.55, -0.12], 0.86),
                       phone("cardapio", [0, -0.98, 0.3], [0.08, -0.12, 0], 0.95)],
            "moedas": [{"pos": [-1.45, -0.25, 0.4], "s": 1.1}, {"pos": [1.45, -0.35, 0.6], "rot": [0.6, 0.4, 0.9], "s": 1},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [-1.3, -1.35, 0.7], "s": 1.0},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [1.25, -1.3, 0.9], "s": 0.7}]},
    "s02": {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": [], "moedas": chuva()},
    "s03": destaque("cardapio", "d"),
    "s04": destaque("roleta", "e"),
    "s05": destaque("pontos", "d"),
    "s06": destaque("carrinho", "e"),
    "s07": destaque("artes", "d"),
    "s08": {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone("economia", [0, -1.0, 0], [0.12, 0.25, -0.05], 0.98)],
            "moedas": [{"pos": [-1.2, -0.7, 0.7], "s": 1.1}, {"pos": [1.2, -0.5, 0.5], "rot": [0.6, 0.4, 0.9], "s": 1},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [-1.3, -1.35, 0.4], "s": 1}]},
}

# (número grande ao fundo, título, texto)
TEXTOS = {
    "s01": (None, "SEU DELIVERY<br>VENDENDO <span>SOZINHO</span>", "5 ferramentas que já vêm no sistema.<br><b>Sem comissão por pedido.</b>"),
    "s02": ("R$", "R$ 20 mil no app.<br><span>R$ 4.600</span> de comissão.", "Todo mês. Esse dinheiro pode ficar com você.<small>Exemplo com comissão de 23%.</small>"),
    "s03": ("01", "Cardápio digital<br><span>com a sua marca</span>", "O cliente pede pelo seu link, sem baixar app."),
    "s04": ("02", "Roleta de<br><span>desconto</span>", "Ele gira, ganha o cupom e o código já entra no pedido."),
    "s05": ("03", "Pontos de<br><span>fidelidade</span>", "Cada pedido vira ponto. Ele volta para trocar."),
    "s06": ("04", "Carrinho<br><span>abandonado</span>", "Desistiu? Meia hora depois o sistema chama de volta no WhatsApp."),
    "s07": ("05", "Artes prontas<br><span>pra postar</span>", "Com o seu cardápio no celular e o link do seu delivery."),
    "s08": (None, "Comenta <span>DEMO</span>", "e a gente te mostra as 5 funcionando<br>no seu restaurante."),
}

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;position:relative;font-family:Poppins,Inter,sans-serif;color:#fff;
 background:radial-gradient(900px 700px at 80% 0%,#1f6bf0 0,rgba(31,107,240,0) 70%),
 radial-gradient(700px 600px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(160deg,#0A3D9E,#041d55)}
.grade{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
 linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 60px;
 mask-image:linear-gradient(180deg,transparent,#000 30%,#000 70%,transparent)}
.brilho{position:absolute;border-radius:50%;filter:blur(90px);opacity:.55}
.num{position:absolute;right:70px;top:150px;font-size:330px;font-weight:900;line-height:1;color:transparent;
 -webkit-text-stroke:3px rgba(141,198,63,.35)}
.tres{position:absolute;inset:0}
.selo{position:absolute;top:60px;left:90px;width:140px;height:140px;padding:12px;background:#fff;border-radius:30px;
 box-shadow:0 14px 40px rgba(0,0,0,.35)}
.selo img{width:116px;display:block}
.pag{position:absolute;top:100px;right:95px;font-size:28px;font-weight:600;opacity:.75}
.txt{position:absolute;left:90px;right:90px;top:250px;text-shadow:0 6px 24px rgba(0,0,0,.35)}
h1{font-size:92px;line-height:1.02;font-weight:900;letter-spacing:-1px}
h1 span{color:#8DC63F}
p{font-size:40px;line-height:1.3;font-weight:500;margin-top:26px;max-width:880px}
p b{color:#8DC63F} small{display:block;font-size:24px;opacity:.65;margin-top:14px}
.rodape{position:absolute;left:0;right:0;bottom:0;height:170px;background:linear-gradient(180deg,rgba(4,22,66,0),rgba(4,22,66,.92) 60%)}
.handle{position:absolute;bottom:48px;left:90px;font-size:28px;font-weight:600;opacity:.9}
.site{position:absolute;bottom:48px;right:90px;font-size:24px;opacity:.65}
.chip{display:inline-block;margin-top:34px;background:#F7941D;font-weight:800;font-size:42px;padding:22px 48px;border-radius:60px;
 box-shadow:0 14px 30px rgba(247,148,29,.45)}
"""


def slide(i, nome, total):
    num, t, d = TEXTOS[nome]
    extra = '<div class="chip">COMENTA DEMO</div>' if nome == "s08" else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div class="grade"></div>
<div class="brilho" style="width:520px;height:520px;background:#8DC63F;left:-160px;top:820px"></div>
<div class="brilho" style="width:420px;height:420px;background:#F7941D;right:-140px;top:420px;opacity:.35"></div>
{f'<div class="num">{num}</div>' if num else ''}
<img class="tres" src="{b64(os.path.join(HERE, 'out3d', nome + '.png'))}">
<div class="selo"><img src="{LOGO}"></div><div class="pag">{i}/{total}</div>
<div class="txt"><h1>{t}</h1><p>{d}</p>{extra}</div>
<div class="rodape"></div><div class="handle">@facilweb</div><div class="site">facilwebdelivery.com.br</div></body></html>"""


async def compor():
    os.makedirs(os.path.join(HERE, "carrossel"), exist_ok=True)
    nomes = list(CENAS)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H})
        for i, n in enumerate(nomes, 1):
            await pg.set_content(slide(i, n, len(nomes)))
            await pg.wait_for_timeout(250)
            await pg.screenshot(path=os.path.join(HERE, "carrossel", f"slide-{i:02d}.png"))
        await b.close()


if __name__ == "__main__":
    json.dump(CENAS, open(os.path.join(HERE, "cenas_carrossel.json"), "w"))
    subprocess.run(["node", "render3d.js", "cenas_carrossel.json", "out3d"], cwd=HERE, check=True)
    asyncio.run(compor())
