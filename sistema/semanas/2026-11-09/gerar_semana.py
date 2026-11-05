"""Artes da semana 09-15/11/2026 do @facilweb, no visual 3D aprovado (mesma identidade de criativos3d/carrossel_v2.py).
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
 "2026-11-10": {
   "c01": (tres("zap_caos", "cardapio", "cozinha"), "topo", None, "PARE DE CAÇAR<br>PEDIDO NO <span>WHATSAPP</span>", "Às 8 da noite de sexta, o pedido tem que chegar pronto."),
   "c02": (lateral("zap_caos"), "col", None, "Pedido picado <span>dá erro</span>", "Endereço numa mensagem, troco em outra, sabor num áudio. Um erro e a pizza volta pro forno."),
   "c03": (lateral("cardapio"), "col", "01", "O cliente monta <span>sozinho</span>", "Pelo cardápio digital no seu link. Escolhe, adiciona e finaliza."),
   "c04": (lateral("pedido"), "col", "02", "Chega <span>completo</span> no WhatsApp", "Itens, endereço e pagamento numa mensagem só."),
   "c05": (lateral("cozinha"), "col", "03", "Sai <span>impresso</span> na cozinha", "Ninguém copia pedido pro papel. A cozinha lê e começa."),
   "c06": (moedas(11, -0.95), "resumo", None, "Salva e mostra <span>pra equipe</span>", ["Cardápio digital no seu link", "Pedido completo no WhatsApp", "Impresso direto na cozinha"]),
   "c07": (lateral("cardapio"), "cta", None, "Comenta <span>QUERO</span>", "e a gente te mostra o pedido saindo impresso no seu restaurante."),
   "story-1": (story("zap_caos"), "story", None, "Sexta à noite é <span>assim</span> aí?", "Pedido no meio de 19 conversas, áudio, print e troco."),
   "story-2": (story("cozinha"), "story", None, "Ou chega <span>pronto</span> na cozinha?", "Com o cardápio digital, o pedido sai impresso sem ninguém copiar."),
   "story-3": (story("pedido"), "story", None, "Post novo no <span>perfil</span>", "O passo a passo tá lá. Comenta QUERO no post que a gente te mostra."),
 },
 "2026-11-12": {
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
 "2026-11-14": {
   "c01": (tres("comanda", "caixa", "pos"), "topo", None, "23H SOMANDO<br>COMANDA NA <span>CALCULADORA?</span>", "Seu caixa pode fechar já somado."),
   "c02": (moedas(47), "topo", None, "Comanda de papel <span>some</span>", "Rasura, molha, fica no bolso do avental. E o caixa não bate no fim da noite."),
   "c03": (lateral("comanda"), "col", "01", "Mesa e comanda <span>no sistema</span>", "O garçom abre a mesa e lança o pedido na maquininha."),
   "c04": (lateral("pos"), "col", "02", "Pagou na mesa, <span>registrou</span>", "Débito, crédito ou Pix ali mesmo, com comprovante impresso."),
   "c05": (lateral("caixa"), "col", "03", "Você <span>confere</span>, não soma", "Salão e delivery no mesmo sistema."),
   "c06": (lateral("cardapio"), "cta", None, "Comenta <span>QUERO</span>", "e a gente te mostra o fechamento do caixa funcionando."),
   "story-1": (story("comanda"), "story", None, "Sábado: o caixa vai fechar <span>que horas?</span>", "Comanda de papel, calculadora e uma mesa que ninguém lembra."),
   "story-2": (story("pos"), "story", None, "Pagou na mesa, <span>já tá no caixa</span>", "Débito, crédito ou Pix na maquininha, com comprovante."),
   "story-3": (story("caixa"), "story", None, "Post novo no <span>perfil</span>", "Comenta QUERO no post que a gente te mostra funcionando."),
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
        cfg = os.path.join(C3D, "cenas_semana_0911.json"); json.dump(cenas, open(cfg, "w"))
        subprocess.run(["node", "render3d.js", cfg, OUT3D], cwd=C3D, check=True, env={**os.environ, "PORTA": "8781"})
    asyncio.run(compor())
