"""Gera as artes da semana 02/11 a 08/11/2026 do @facilweb, todas com a logomarca.

Saída (JPEG) em ./saida-2026-11-02/<AAAA-MM-DD>/
"""
import asyncio, base64, os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = base64.b64encode(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logo.png"), "rb").read()).decode()
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


CARROSSEL_TER = [  # 03/11 9h30 · ENSINO
    ("capa", "QUANTO O APP <span>LEVOU</span> DE VOCÊ EM OUTUBRO?",
     "Faz essa conta com o extrato na mão"),
    ("texto", "A comissão vem descontada",
     "Por isso quase ninguém vê o total.<br><br><b>Você só vê o que caiu na conta.</b>"),
    ("item", "1. Abre o extrato de outubro",
     "No painel do app, puxa o relatório de repasses do mês inteiro."),
    ("item", "2. Soma tudo que é taxa",
     "A comissão e todas as outras taxas que aparecem descontadas."),
    ("item", "3. Divide pelos pedidos",
     "Agora você sabe quanto paga em <b>cada pedido</b> que entra pelo app."),
    ("item", "4. Multiplica por 12",
     "Esse é o valor que sai do seu caixa <b>num ano</b>, só em taxa."),
    ("resumo", "Salva pra fazer hoje",
     "<ol><li>Abre o extrato de outubro</li><li>Soma comissão e taxas</li>"
     "<li>Divide pelos pedidos</li><li>Multiplica por 12</li></ol>"),
    ("cta", "Comenta <span>DEMO</span>",
     "que a gente te mostra como trazer esse cliente pro seu canal, sem comissão."),
]

def braco(no_braco, no_sistema):
    return (f'<span class="lbl">NO BRAÇO</span><br>{no_braco}<br><br>'
            f'<span class="lbl v">NO SISTEMA</span><br><b>{no_sistema}</b>')

CARROSSEL_QUI = [  # 05/11 15h · ENSINO/OFERTA
    ("capa", "AINDA FAZ TUDO <span>NO BRAÇO</span>?",
     "5 tarefas do restaurante que o sistema faz por você"),
    ("texto", "Todo pedido anotado à mão é chance de erro",
     "Erro vira comida refeita, entrega atrasada e <b>cliente que não volta.</b>"),
    ("item", "1. Anotar pedido do WhatsApp",
     braco("copiar mensagem por mensagem.", "o cliente monta o pedido no cardápio digital.")),
    ("item", "2. Levar o pedido pra cozinha",
     braco("papel na mão.", "o pedido sai impresso na cozinha, sozinho.")),
    ("item", "3. Mesas e comandas",
     braco("comanda de papel e calculadora.", "cada mesa aberta na tela, com a conta pronta.")),
    ("item", "4. Fechar o caixa",
     braco("somar tudo no fim da noite.", "PDV e relatório do dia prontos.")),
    ("item", "5. Lembrar quem é cliente",
     braco("de memória.", "cadastro de clientes e fidelidade.")),
    ("resumo", "Tira do braço",
     "<ol><li>Pedido do WhatsApp</li><li>Pedido na cozinha</li><li>Mesas e comandas</li>"
     "<li>Fechamento de caixa</li><li>Cadastro de clientes</li></ol>"),
    ("cta", "Comenta <span>DEMO</span>",
     "que a gente te mostra as 5 funcionando, numa demonstração gratuita."),
]

EXTRA_CSS = f""".lbl{{font-size:30px;font-weight:700;letter-spacing:3px;opacity:.7}} .lbl.v{{color:{VERDE};opacity:1}}
.img1 .wrap{{inset:260px 120px 170px 120px}} .img1 h1{{font-size:120px}}"""

def feed_page(i, total, kind, title, body, numerar=True):
    if kind == "capa":
        inner = f'<div class="barra"></div><h1>{title}</h1><div class="sub">{body}</div>'
    elif kind == "cta":
        inner = f'<h2>{title}</h2><p>{body}</p><div class="botao">COMENTA DEMO</div>'
    elif kind == "resumo":
        inner = f'<h2>{title}</h2>{body}'
    else:
        inner = f'<div class="barra"></div><h2>{title}</h2><p>{body}</p>'
    num = f'<div class="num">{i}/{total}</div>' if numerar else ''
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{FEED_CSS}{EXTRA_CSS}</style></head><body>'
            f'<div class="selo"><img src="data:image/png;base64,{LOGO}"></div>'
            f'{num}<div class="wrap">{inner}</div>'
            f'<div class="handle">@facilweb</div><div class="site">facilwebdelivery.com.br</div></body></html>')

# 07/11 9h30 · OPINIÃO · imagem única
IMAGEM_SAB = ("capa", "VOCÊ NÃO PRECISA <span>SAIR DO APP</span>",
              "Precisa parar de depender só dele.")

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


STORIES = {
  "2026-11-03": [
    '<h2>Post <span>novo</span> no feed</h2><p>Quanto o app levou de você em outubro? A conta em 4 passos</p><div class="botao">Toque no @facilweb</div>',
    '<h2>Você sabe quanto pagou de <span>comissão</span> em outubro?</h2><p>Responde esse story com o valor, ou com <b>NÃO SEI</b>.<br>A gente te ajuda a fazer a conta.</p>',
    '<h2>Quer ver o pedido direto <span>funcionando</span>?</h2><p>Demonstração gratuita pelo WhatsApp</p><div class="botao">Link na bio</div>',
  ],
  "2026-11-05": [
    '<h2>Post <span>novo</span> no feed</h2><p>5 tarefas do restaurante que o sistema faz por você</p><div class="botao">Toque no @facilweb</div>',
    '<h2>Qual tarefa mais <span>come</span> o seu dia?</h2><p>Anotar pedido, comanda, caixa...<br>Responde esse story que a gente te mostra como tirar do braço.</p>',
    '<h2>Quer ver o sistema <span>funcionando</span>?</h2><p>Demonstração gratuita pelo WhatsApp</p><div class="botao">Link na bio</div>',
  ],
  "2026-11-07": [
    '<h2>Sair do app de uma vez? <span>Não precisa.</span></h2><p>Começa pelo cliente que já volta.<br>Post novo no feed.</p><div class="botao">Toque no @facilweb</div>',
    '<h2>Monta o seu <span>delivery próprio</span></h2><p>Demonstração gratuita pelo WhatsApp</p><div class="botao">Link na bio</div>',
  ],
}
def vert_page(inner, handle=True):
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{VERT_CSS}</style></head><body>'
            f'<div class="selo"><img src="data:image/png;base64,{LOGO}"></div>'
            f'<div class="wrap">{inner}</div>'
            + ('<div class="handle">@facilweb</div>' if handle else '') + '</body></html>')



OUT = os.path.join(HERE, "saida-2026-11-02")

async def shot(pg, html, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    await pg.set_content(html)
    await pg.wait_for_timeout(200)
    await pg.screenshot(path=path, type="jpeg", quality=92)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1350})
        for data, lista in (("2026-11-03", CARROSSEL_TER), ("2026-11-05", CARROSSEL_QUI)):
            for i, s in enumerate(lista, 1):
                await shot(pg, feed_page(i, len(lista), *s), os.path.join(OUT, data, f"carrossel-slide-{i:02d}.jpg"))
        await shot(pg, feed_page(1, 1, *IMAGEM_SAB, numerar=False), os.path.join(OUT, "2026-11-07", "imagem-opiniao.jpg"))
        await pg.set_viewport_size({"width": 1080, "height": 1920})
        for data, lista in STORIES.items():
            for i, inner in enumerate(lista, 1):
                await shot(pg, vert_page(inner), os.path.join(OUT, data, f"story-{i:02d}.jpg"))
        await b.close()

asyncio.run(main())
