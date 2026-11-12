"""Artes da semana 16-22/11/2026 do @facilweb, no visual 3D aprovado (mesma identidade de criativos3d/carrossel_v2.py).
Toda peça leva a logomarca sistema/logo.png no selo branco.

Uso: python3 gerar_semana.py            (renderiza 3D + compõe)
     python3 gerar_semana.py --so-compor
Saída: saida/AAAA-MM-DD/*.jpg (carrossel 1080x1350, stories 1080x1920)
"""
import asyncio, base64, json, os, random, subprocess, sys
from playwright.async_api import async_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIS = os.path.abspath(os.path.join(HERE, "..", ".."))
C3D = os.path.join(SIS, "criativos3d")
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO = b64(os.path.join(SIS, "logo.png"))
OUT3D, OUT = os.path.join(HERE, "out3d"), os.path.join(HERE, "saida")

def phone(tex, pos, rot, s=1.0): return {"tex": f"telas/{tex}.png", "pos": pos, "rot": rot, "s": s, "sombra": False}
def lateral(tex):
    return {"w": 1080, "h": 1350, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone(tex, [0.52, -0.12, 0], [0.06, -0.38, 0.03], 1.0)],
            "moedas": [{"pos": [0.05, -0.85, 0.8], "rot": [1.1, 0.2, 0.5], "s": 0.9},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [1.0, 0.55, 0.4], "s": 0.8},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [0.95, -0.9, 0.5], "s": 0.6}]}
def tres(a, b, c, y=-0.56):
    return {"w": 1080, "h": 1350, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone(a, [-0.6, y, -0.4], [0.05, 0.5, 0.1], 0.6), phone(c, [0.6, y, -0.4], [0.05, -0.5, -0.1], 0.6),
                       phone(b, [0, y + 0.04, 0.25], [0.07, -0.1, 0], 0.68)],
            "moedas": [{"pos": [-1.05, 0.05, 0.5], "s": 0.9}, {"pos": [1.05, -0.05, 0.6], "rot": [0.6, 0.4, 0.9], "s": 0.85},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [-0.95, -0.95, 0.7], "s": 0.8},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [0.95, -0.95, 0.8], "s": 0.6}]}
def moedas(seed, ymax=-0.25):
    random.seed(seed)
    return {"w": 1080, "h": 1350, "fov": 28, "cam": [0, 0, 5.2], "phones": [],
            "moedas": [{"pos": [random.uniform(-1.2, 1.2), random.uniform(-1.15, ymax), random.uniform(-0.6, 1.2) if ymax > -0.5 else random.uniform(-0.6, 0.4)],
                        "rot": [random.uniform(0.3, 1.5), random.uniform(0, 3), random.uniform(-1, 1)], "s": random.uniform(0.8, 1.25)} for _ in range(18)]}
def story(tex):
    return {"w": 1080, "h": 1920, "fov": 28, "cam": [0, 0, 5.2],
            "phones": [phone(tex, [0.03, -0.33, 0], [0.06, -0.32, 0.03], 0.62)],
            "moedas": [{"pos": [-0.62, -0.15, 0.7], "rot": [1.1, 0.2, 0.5], "s": 0.9},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [0.62, -0.05, 0.4], "s": 0.8},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [-0.55, -0.75, 0.6], "s": 0.6}]}

# (tipo, número/selo, título, texto)
POSTS = {
 "2026-11-17": {
   "c01": (tres("roleta", "cardapio", "pedido"), "topo", None, "SEU DESCONTO<br>AINDA PAGA <span>COMISSÃO?</span>", "Na Black Friday, a promoção pode rodar no seu canal."),
   "c02": (moedas(17), "topo", None, "Promoção no app <span>custa 2 vezes</span>", "O desconto sai da sua margem. A comissão continua saindo de cada pedido."),
   "c03": (lateral("roleta"), "col", "01", "O cliente <span>gira a roleta</span>", "No seu cardápio digital, antes de finalizar o pedido."),
   "c04": (lateral("pedido"), "col", "02", "O código entra <span>no pedido</span>", "Chega pronto no WhatsApp, com o desconto aplicado."),
   "c05": (lateral("cardapio"), "col", "03", "Comissão <span>zero</span>", "O pedido é do seu link. O cliente fica no seu cadastro."),
   "c06": (moedas(29, -0.95), "resumo", None, "Black Friday <span>no seu canal</span>", ["Roleta de desconto no cardápio", "Código direto no pedido", "Comissão zero"]),
   "c07": (lateral("roleta"), "cta", None, "Comenta <span>QUERO</span>", "e a gente te mostra a roleta funcionando no seu cardápio."),
   "story-1": (story("roleta"), "story", None, "Black Friday <span>dia 27</span>", "Sua promoção vai rodar no app ou no seu cardápio?"),
   "story-2": (story("pedido"), "story", None, "Girou, ganhou, <span>pediu</span>", "O código da roleta entra direto no pedido. Comissão zero."),
   "story-3": (story("cardapio"), "story", None, "Post novo no <span>perfil</span>", "O passo a passo tá lá. Comenta QUERO no post que a gente te mostra."),
 },
 "2026-11-19": {
   "c01": (tres("cardapio", "pontos", "carrinho"), "topo", None, "CLIENTE FIEL<br>PAGANDO <span>COMISSÃO?</span>", "Quem já pediu 3 vezes com você pode pedir direto."),
   "c02": (moedas(23), "topo", None, "O app traz <span>gente nova</span>.", "Isso tem valor. O problema é quem já te conhece continuar pedindo por lá."),
   "c03": (lateral("cardapio"), "col", "01", "Mostra o <span>seu link</span>", "Na embalagem, no Instagram e no WhatsApp. É ali que ele pede da próxima vez."),
   "c04": (lateral("pontos"), "col", "02", "Dá motivo pra <span>voltar</span>", "Cada pedido direto vira ponto pra trocar."),
   "c05": (lateral("carrinho"), "col", "03", "Chama de volta <span>no WhatsApp</span>", "Desistiu no meio? O sistema manda a mensagem com o desconto que você definir."),
   "c06": (moedas(31, -0.95), "resumo", None, "O app fica pra <span>quem não te conhece</span>", ["Seu link em todo lugar", "Pontos pra voltar", "Mensagem pra quem desistiu"]),
   "c07": (lateral("economia"), "cta", None, "Comenta <span>QUERO</span>", "e a gente te mostra como montar o seu delivery próprio."),
   "story-1": (story("cardapio"), "story", None, "Seu cliente fiel <span>ainda pede pelo app?</span>", "Pedindo direto com você, a comissão fica no seu caixa."),
   "story-2": (story("pontos"), "story", None, "Pontos de <span>fidelidade</span>", "Cada pedido pelo seu cardápio vira ponto. Ele volta pra trocar."),
   "story-3": (story("carrinho"), "story", None, "Post novo no <span>perfil</span>", "3 jeitos de trazer esse cliente pro seu canal. Comenta QUERO no post."),
 },
 "2026-11-21": {
   "c01": (tres("artes", "cardapio", "pedido"), "topo", None, "POSTOU ÀS 19H<br>E <span>NENHUM PEDIDO?</span>", "Falta o caminho até o seu cardápio."),
   "c02": (moedas(53), "topo", None, "Quem vê o prato <span>tá com fome agora</span>", "Se precisa pedir cardápio e perguntar preço, desiste no meio do caminho."),
   "c03": (lateral("artes"), "col", "01", "Um link <span>com o seu nome</span>", "O cardápio digital tem o link do seu restaurante."),
   "c04": (lateral("cardapio"), "col", "02", "Bio, story e <span>status</span>", "O link vai onde o cliente vê a foto do prato."),
   "c05": (lateral("pedido"), "col", "03", "Chega <span>completo</span> no WhatsApp", "Itens, endereço e pagamento numa mensagem só."),
   "c06": (moedas(61, -0.95), "resumo", None, "Post bom <span>termina em pedido</span>", ["Link próprio do cardápio", "Na bio, no story e no status", "Pedido completo no WhatsApp"]),
   "c07": (lateral("cardapio"), "cta", None, "Comenta <span>QUERO</span>", "e a gente te mostra o seu link pronto pra usar no Instagram."),
   "story-1": (story("artes"), "story", None, "Seu post do prato <span>vira pedido?</span>", "Ou o cliente tem que mandar mensagem pedindo o cardápio?"),
   "story-2": (story("pedido"), "story", None, "Tocou no link, <span>pediu</span>", "O pedido chega completo no WhatsApp."),
   "story-3": (story("artes"), "story", None, "Post novo no <span>perfil</span>", "3 passos pro seu Instagram virar pedido. Comenta QUERO no post."),
 },
}

CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;position:relative;font-family:Poppins,sans-serif;color:#fff;
 background:radial-gradient(900px 700px at 85% 10%,#1f6bf0 0,rgba(31,107,240,0) 70%),radial-gradient(700px 600px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(160deg,#0A3D9E,#041d55)}
body.st{height:1920px}
.grade{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
 background-size:60px 60px;mask-image:linear-gradient(180deg,transparent,#000 25%,#000 75%,transparent)}
.brilho{position:absolute;border-radius:50%;filter:blur(90px)}
.anel{position:absolute;border-radius:50%;border:3px solid rgba(141,198,63,.2)}
.tres{position:absolute;inset:0}
.selo{position:absolute;top:60px;left:80px;width:130px;height:130px;padding:11px;background:#fff;border-radius:28px;box-shadow:0 14px 40px rgba(0,0,0,.35)} .selo img{width:108px;display:block}
.st .selo{top:270px}
.pag{position:absolute;top:96px;right:80px;font-size:26px;font-weight:700;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.2);padding:6px 18px;border-radius:30px}
h1{font-weight:900;letter-spacing:-1px;line-height:1.02;text-shadow:0 6px 24px rgba(0,0,0,.35)} h1 span{color:#8DC63F}
p{line-height:1.3;font-weight:500;margin-top:24px;text-shadow:0 4px 16px rgba(0,0,0,.3)} p b{color:#8DC63F}
.col{position:absolute;left:80px;width:470px;top:300px} .col h1{font-size:72px} .col p{font-size:34px}
.num{display:inline-flex;align-items:center;justify-content:center;width:96px;height:96px;border-radius:28px;background:#F7941D;font-weight:900;font-size:50px;
 margin-bottom:30px;box-shadow:0 12px 30px rgba(247,148,29,.45);transform:rotate(-6deg)}
.topo{position:absolute;left:80px;right:80px;top:240px;text-align:center} .topo h1{font-size:88px} .topo p{font-size:38px;max-width:840px;margin-left:auto;margin-right:auto}
.res{position:absolute;left:80px;right:80px;top:250px} .res h1{font-size:76px;text-align:center}
.res ol{list-style:none;margin-top:50px;counter-reset:n} .res li{counter-increment:n;display:flex;align-items:center;font-size:42px;font-weight:700;margin-bottom:30px;
 background:rgba(255,255,255,.1);border:1px solid rgba(255,255,255,.18);border-radius:28px;padding:26px 30px}
.res li:before{content:counter(n);flex:none;display:inline-flex;align-items:center;justify-content:center;width:70px;height:70px;border-radius:20px;background:#F7941D;
 font-weight:900;margin-right:28px}
.chip{display:inline-block;margin-top:36px;background:#F7941D;font-weight:800;font-size:38px;padding:20px 44px;border-radius:60px;box-shadow:0 14px 30px rgba(247,148,29,.45)}
.stx{position:absolute;left:80px;right:80px;top:470px;text-align:center} .stx h1{font-size:84px} .stx p{font-size:40px}
.rodape{position:absolute;left:0;right:0;bottom:0;height:150px;background:linear-gradient(180deg,rgba(4,22,66,0),rgba(4,22,66,.9) 65%)}
.handle{position:absolute;bottom:46px;left:80px;font-size:28px;font-weight:700} .site{position:absolute;bottom:46px;right:80px;font-size:24px;opacity:.7}
.st .handle{top:300px;bottom:auto;left:auto;right:80px} .st .site{top:345px;bottom:auto;left:auto;right:80px} .st .rodape{display:none}
"""

def html(nome, item, i, total, png3d):
    _, tipo, num, t, d = item
    st = tipo == "story"
    if tipo == "col" or tipo == "cta":
        badge = f'<div class="num">{num}</div>' if num else ""
        chip = '<div class="chip">COMENTA QUERO</div>' if tipo == "cta" else ""
        txt = f'<div class="col">{badge}<h1>{t}</h1><p>{d}</p>{chip}</div>'
    elif tipo == "resumo":
        txt = f'<div class="res"><h1>{t}</h1><ol>{"".join(f"<li>{x}</li>" for x in d)}</ol></div>'
    elif tipo == "story":
        txt = f'<div class="stx"><h1>{t}</h1><p>{d}</p></div>'
    else:
        txt = f'<div class="topo"><h1>{t}</h1><p>{d}</p></div>'
    pag = "" if st else f'<div class="pag">{i}/{total}</div>'
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body class="{'st' if st else ''}">
<div class="grade"></div><div class="anel" style="width:900px;height:900px;left:-470px;top:-330px"></div>
<div class="brilho" style="width:520px;height:520px;background:#8DC63F;opacity:.4;left:-200px;top:{1400 if st else 900}px"></div>
<div class="brilho" style="width:420px;height:420px;background:#F7941D;opacity:.3;right:-160px;top:380px"></div>
<img class="tres" src="{b64(png3d)}">
<div class="selo"><img src="{LOGO}"></div>{pag}{txt}
<div class="rodape"></div><div class="handle">@facilweb</div><div class="site">facilwebdelivery.com.br</div></body></html>"""

def chave(data, nome): return f"{data.replace('-', '')}_{nome.replace('-', '')}"

async def compor():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for data, itens in POSTS.items():
            os.makedirs(os.path.join(OUT, data), exist_ok=True)
            slides = [n for n in itens if n.startswith("c")]
            for n, item in itens.items():
                st = item[1] == "story"
                pg = await b.new_page(viewport={"width": 1080, "height": 1920 if st else 1350})
                i = slides.index(n) + 1 if not st else 0
                await pg.set_content(html(n, item, i, len(slides), os.path.join(OUT3D, chave(data, n) + ".png")))
                await pg.wait_for_timeout(300)
                png = os.path.join(OUT, data, "_tmp.png"); await pg.screenshot(path=png); await pg.close()
                nomearq = f"carrossel-slide-{i:02d}.jpg" if not st else f"{n}.jpg"
                Image.open(png).convert("RGB").save(os.path.join(OUT, data, nomearq), quality=92); os.remove(png)
        await b.close()

if __name__ == "__main__":
    if "--so-compor" not in sys.argv:
        cenas = {chave(d, n): it[0] for d, its in POSTS.items() for n, it in its.items()}
        cfg = os.path.join(C3D, "cenas_semana_1611.json"); json.dump(cenas, open(cfg, "w"))
        subprocess.run(["node", "render3d.js", cfg, OUT3D], cwd=C3D, check=True, env={**os.environ, "PORTA": "8781"})
    asyncio.run(compor())
