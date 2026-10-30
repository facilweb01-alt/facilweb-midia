"""Camadas (PNG com transparência) das duas opções do vídeo POS. Cada elemento em arquivo próprio, recortado."""
import asyncio, base64, os
from playwright.async_api import async_playwright

OUT = "/home/claude/video-pos/camadas2"
LOGO = "data:image/png;base64," + base64.b64encode(open("/home/claude/marca/logo.png", "rb").read()).decode()

CSS = """*{margin:0;padding:0;box-sizing:border-box}html,body{background:transparent}
body{font-family:Poppins,sans-serif;color:#fff;display:inline-block}
#e{display:inline-block} .v{color:#8DC63F} .l{color:#F7941D}
"""

def el(html, css=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{css}</style></head><body><div id="e">{html}</div></body></html>'

SELO = el(f'<div class="s"><img src="{LOGO}"></div>',
          ".s{width:150px;height:150px;padding:13px;background:#fff;border-radius:34px;margin:30px;box-shadow:0 14px 34px rgba(0,0,0,.45)} .s img{width:100%;display:block}")
SELO_G = el(f'<div class="s"><img src="{LOGO}"></div>',
            ".s{width:300px;height:300px;padding:26px;background:#fff;border-radius:66px;margin:50px;box-shadow:0 24px 60px rgba(0,0,0,.45)} .s img{width:100%;display:block}")

# ---------- opção 1: tela cheia, tipografia cinética ----------
PAL = """.w{font-weight:900;font-size:150px;line-height:.95;letter-spacing:-3px;padding:20px 40px;
 text-shadow:0 10px 40px rgba(0,0,0,.55)} .w i{font-style:normal;display:block;height:16px;background:#8DC63F;border-radius:10px;margin-top:10px}"""
SUB = """.b{font-weight:700;font-size:50px;padding:14px 34px;background:rgba(4,29,85,.88);border-radius:22px;margin:20px;
 box-shadow:0 12px 30px rgba(0,0,0,.4)} .b span{color:#8DC63F}"""
CHIP = ".c{font-weight:900;font-size:44px;background:#F7941D;padding:10px 28px;border-radius:40px;margin:20px;box-shadow:0 10px 26px rgba(247,148,29,.5)}"
PASSOS1 = [("MESA", "escolhe a mesa no app"), ("COMANDA", "abre com o nome do cliente"), ("CARDÁPIO", "lança o pedido na hora"),
           ("PAGAMENTO", "débito, crédito ou <span>Pix</span>"), ("COMPROVANTE", "sai <span>impresso</span> ali na mesa")]
GANCHO1 = [el('<div class="w">Pare de</div>', PAL), el('<div class="w">correr até</div>', PAL),
           el('<div class="w">o <span class="v">caixa</span></div>', PAL)]
GANCHO1_SUB = el('<div class="b">sua mesa paga em <span class="l" style="color:#F7941D">1 minuto</span></div>', SUB)

FINAL1 = el(f"""<div class="f"><div class="s"><img src="{LOGO}"></div>
<div class="k">SISTEMA POS FÁCIL WEB</div><h1>Tudo na<br><span class="v">maquininha</span></h1>
<p>Mesa, comanda, cardápio e pagamento.<br>Com o <b>mesmo cardápio</b> do seu delivery.</p></div>""",
 """.f{width:1080px;height:1920px;padding-top:300px;text-align:center;background:radial-gradient(900px 800px at 50% 25%,#1f6bf0 0,rgba(31,107,240,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
 .s{width:280px;height:280px;padding:24px;background:#fff;border-radius:62px;margin:0 auto;box-shadow:0 24px 60px rgba(0,0,0,.4)} .s img{width:100%;display:block}
 .k{margin-top:60px;font-size:36px;font-weight:700;letter-spacing:6px;color:#8DC63F} h1{font-size:120px;font-weight:900;line-height:1;letter-spacing:-2px;margin-top:16px}
 p{font-size:44px;line-height:1.35;margin-top:34px;opacity:.95} p b{color:#8DC63F}""")
CTA = lambda t: el(f'<div class="c">{t}</div>', ".c{font-weight:800;font-size:60px;background:#F7941D;padding:28px 70px;border-radius:80px;margin:40px;box-shadow:0 16px 40px rgba(247,148,29,.55)}")
HANDLE = el('<div class="h">@facilweb · facilwebdelivery.com.br</div>', ".h{font-size:34px;font-weight:600;opacity:.85;padding:10px}")

# ---------- opção 2: vitrine com lupa ----------
FUNDO2 = el('<div class="f"><div class="g"></div><div class="a a1"></div><div class="a a2"></div><div class="o o1"></div><div class="o o2"></div></div>',
 """.f{position:relative;width:1080px;height:1920px;overflow:hidden;background:radial-gradient(900px 800px at 85% 5%,#1f6bf0 0,rgba(31,107,240,0) 70%),
 radial-gradient(800px 700px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
 .g{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
 background-size:60px 60px;mask-image:linear-gradient(180deg,transparent,#000 20%,#000 80%,transparent)}
 .a{position:absolute;border-radius:50%;border:3px solid rgba(141,198,63,.22)} .a1{width:1000px;height:1000px;left:-520px;top:-300px}
 .a2{width:760px;height:760px;right:-420px;bottom:-160px;border-color:rgba(247,148,29,.22)}
 .o{position:absolute;border-radius:50%;filter:blur(110px)} .o1{width:560px;height:560px;background:#8DC63F;opacity:.4;left:-220px;top:1250px}
 .o2{width:460px;height:460px;background:#F7941D;opacity:.3;right:-180px;top:700px}""")
TITULO2 = [("1", "Escolhe<br>a <span class='v'>mesa</span>"), ("2", "Abre a<br><span class='v'>comanda</span>"), ("3", "Lança pelo<br><span class='v'>cardápio</span>"),
           ("4", "Cobra <span class='v'>débito,</span><br><span class='v'>crédito ou Pix</span>"), ("5", "Comprovante<br><span class='v'>na hora</span>")]
def tit2(n, t):
    return el(f'<div class="t"><div class="n">{n}</div><div class="x">{t}</div></div>',
              """.t{display:flex;align-items:center;gap:26px;padding:20px 30px} .n{width:120px;height:120px;border-radius:34px;background:#F7941D;
              font-weight:900;font-size:76px;display:flex;align-items:center;justify-content:center;box-shadow:0 12px 30px rgba(247,148,29,.45);transform:rotate(-6deg)}
              .x{font-weight:900;font-size:76px;line-height:1;letter-spacing:-1px;text-shadow:0 8px 26px rgba(0,0,0,.4)}""")
LUPA_TXT = [("Pedido lançado", "Sub-total na tela"), ("Débito, crédito ou Pix", "escolhe e finaliza"), ("Comprovante", "impresso na maquininha")]
def etiqueta(a, b):
    return el(f'<div class="e"><b>{a}</b><span>{b}</span></div>',
              ".e{background:#fff;color:#041d55;border-radius:26px;padding:18px 30px;margin:20px;box-shadow:0 14px 34px rgba(0,0,0,.4)} .e b{display:block;font-size:40px;font-weight:900} .e span{font-size:30px;font-weight:600;color:#0A3D9E}")
GANCHO2 = el("""<div class="g"><div class="q">Seu garçom ainda corre<br>até o caixa?</div><h1>Agora a mesa<br><span class="v">paga em 1 minuto</span></h1></div>""",
 """.g{width:1000px;text-align:center;padding:30px} .q{display:inline-block;font-size:48px;font-weight:700;background:rgba(255,255,255,.12);border:2px solid rgba(255,255,255,.25);
 padding:16px 34px;border-radius:30px} h1{font-size:104px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:34px;text-shadow:0 10px 36px rgba(0,0,0,.5)}""")
SELO_TAG = el('<div class="t">TELA REAL DO SISTEMA</div>', ".t{font-size:26px;font-weight:800;color:#041d55;background:#8DC63F;padding:10px 24px;border-radius:30px;margin:16px;box-shadow:0 10px 24px rgba(0,0,0,.3)}")
FINAL2 = el("""<div class="f"><div class="k">SISTEMA POS FÁCIL WEB</div><h1>Cardápio e<br>pagamento<br><span class="v">na mesma maquininha</span></h1>
<p>O mesmo cardápio do seu delivery,<br>agora na mesa do cliente.</p></div>""",
 """.f{width:1000px;text-align:center;padding:20px} .k{font-size:36px;font-weight:700;letter-spacing:6px;color:#8DC63F}
 h1{font-size:100px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:20px;text-shadow:0 10px 36px rgba(0,0,0,.45)} p{font-size:44px;line-height:1.35;margin-top:34px}""")


async def main():
    os.makedirs(OUT, exist_ok=True)
    itens = {"selo": SELO, "selo_g": SELO_G, "gancho1_sub": GANCHO1_SUB, "final1": FINAL1, "cta_reels": CTA("COMENTA DEMO"),
             "cta_stories": CTA("RESPONDE DEMO"), "handle": HANDLE, "fundo2": FUNDO2, "gancho2": GANCHO2, "tag2": SELO_TAG, "final2": FINAL2}
    for i, g in enumerate(GANCHO1): itens[f"gancho1_{i}"] = g
    for i, (w, s) in enumerate(PASSOS1, 1):
        itens[f"p1_pal{i}"] = el(f'<div class="w">{w}<i></i></div>', PAL)
        itens[f"p1_sub{i}"] = el(f'<div class="b">{s}</div>', SUB)
        itens[f"p1_chip{i}"] = el(f'<div class="c">{i}/5</div>', CHIP)
    for i, (n, t) in enumerate(TITULO2, 1): itens[f"t2_{i}"] = tit2(n, t)
    for i, (a, b) in enumerate(LUPA_TXT, 1): itens[f"lupa_txt{i}"] = etiqueta(a, b)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for nome, html in itens.items():
            await pg.set_content(html); await pg.wait_for_timeout(120)
            await pg.locator("#e").screenshot(path=f"{OUT}/{nome}.png", omit_background=True)
        await b.close()
    print(len(itens), "camadas")

asyncio.run(main())
