"""Semana 16-22/11/2026 @facilweb · versão 3: sem mensalidade nas artes (pedido do Marcelo em 16/11), telas reais do sistema, teste grátis na chamada.

Novo padrão: fundo claro com azul Fácil Web, peças que imitam o dia a dia do restaurante
(cupom fiscal, conversa de WhatsApp, foto real da maquininha, tabela de comparação) e
logomarca sistema/logo.png no selo branco em TODAS as peças.

Uso: python3 gerar_v2.py   ->  saida/AAAA-MM-DD/carrossel-slide-NN.jpg e story-N.jpg
"""
import asyncio, base64, os
from playwright.async_api import async_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SIS = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
TELAS = os.path.join(SIS, "criativos3d", "telas")
OUT = os.path.join(HERE, "saida")


def b64(p, mime="image/png"):
    return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()


LOGO = b64(os.path.join(SIS, "logo.png"))
TELA = lambda n: b64(os.path.join(TELAS, n + ".png"))
FOTO = lambda n: b64(os.path.join(HERE, "fotos", n + ".jpg"), "image/jpeg")

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;overflow:hidden;position:relative;font-family:Poppins,sans-serif;color:#0B1F4D;background:#F3F6FB}
body.st{height:1920px}
body.escuro{background:radial-gradient(900px 700px at 90% 0%,#1f6bf0 0,rgba(31,107,240,0) 70%),linear-gradient(160deg,#0A3D9E,#06235f);color:#fff}
body.verde{background:linear-gradient(160deg,#8DC63F,#5c9a1c);color:#fff}
.pontos{position:absolute;inset:0;background-image:radial-gradient(rgba(10,61,158,.10) 2px,transparent 2px);background-size:34px 34px}
.escuro .pontos,.verde .pontos{background-image:radial-gradient(rgba(255,255,255,.10) 2px,transparent 2px)}
.faixa{position:absolute;left:0;top:0;width:22px;height:100%;background:#0A3D9E}
.escuro .faixa{background:#8DC63F}.verde .faixa{background:#0A3D9E}
.selo{position:absolute;top:56px;left:76px;width:118px;height:118px;padding:10px;background:#fff;border-radius:26px;box-shadow:0 10px 30px rgba(10,61,158,.22);border:2px solid #E3EAF6}
.selo img{width:94px;display:block}
.st .selo{top:250px;left:80px}
.pag{position:absolute;top:92px;right:76px;font-size:24px;font-weight:700;color:#0A3D9E;background:#fff;border:2px solid #DCE5F5;padding:6px 18px;border-radius:30px}
.escuro .pag,.verde .pag{color:#fff;background:rgba(255,255,255,.14);border-color:rgba(255,255,255,.25)}
.tag{display:inline-block;font-size:24px;font-weight:700;letter-spacing:2px;text-transform:uppercase;color:#F7941D;margin-bottom:18px}
.escuro .tag{color:#8DC63F}.verde .tag{color:#0A3D9E}
h1{font-weight:700;letter-spacing:-2px;line-height:1.02;-webkit-text-stroke:1.2px currentColor}
h1 .v{color:#8DC63F}.verde h1 .v{color:#0A3D9E}
h1 .m{background:linear-gradient(transparent 58%,#8DC63F 58%);padding:0 6px}
.escuro h1 .m{background:linear-gradient(transparent 58%,#F7941D 58%)}
h1 .l{color:#F7941D}
p{font-size:34px;line-height:1.32;font-weight:500;margin-top:22px;color:#33456e}
.escuro p,.verde p{color:#e9f0ff}
p b{color:#0A3D9E}.escuro p b{color:#8DC63F}
.txt{position:absolute;left:80px;right:80px;top:230px}
.st .txt{top:430px}
.rod{z-index:5;position:absolute;left:80px;right:80px;bottom:44px;display:flex;justify-content:space-between;font-size:24px;font-weight:600;color:#6b7aa0}
.escuro .rod,.verde .rod{color:rgba(255,255,255,.75)}
.st .rod{bottom:250px}
.nota{position:absolute;left:80px;right:80px;bottom:96px;font-size:21px;color:#8592b3;font-weight:500}
.escuro .nota{color:rgba(255,255,255,.6)}.verde .nota{color:rgba(255,255,255,.9)}
.cta p{max-width:560px}.col{right:500px!important}
.st .nota{bottom:300px}
/* cupom fiscal */
.cupom{position:absolute;background:#fff;color:#1d1d1d;font-family:'DejaVu Sans Mono',monospace;padding:42px 46px 60px;box-shadow:0 30px 70px rgba(0,0,0,.28);
 -webkit-mask:linear-gradient(#000,#000) top/100% calc(100% - 22px) no-repeat,conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) bottom/36px 22px repeat-x}
.cupom .cab{text-align:center;font-weight:700;font-size:30px;letter-spacing:3px}
.cupom .sub{text-align:center;font-size:20px;color:#666;margin-top:4px}
.cupom hr{border:0;border-top:3px dashed #bbb;margin:22px 0}
.cupom .ln{display:flex;justify-content:space-between;font-size:30px;margin:12px 0}
.cupom .neg{color:#d23b2a;font-weight:700}
.cupom .pos{color:#2e8b1f;font-weight:700}
.cupom .tot{font-size:40px;font-weight:700}
/* chat */
.chat{position:absolute;background:#ECE5DD;border-radius:40px;padding:34px 30px;box-shadow:0 30px 70px rgba(10,30,80,.25);overflow:hidden}
.chat .top{margin:-34px -30px 24px;background:#075E54;color:#fff;padding:24px 30px;font-size:28px;font-weight:600;display:flex;justify-content:space-between}
.chat .top span{font-size:22px;background:#25D366;padding:2px 14px;border-radius:20px}
.bl{max-width:82%;font-size:30px;line-height:1.3;padding:16px 22px;border-radius:22px;margin:12px 0;background:#fff;color:#1d1d1d;box-shadow:0 2px 0 rgba(0,0,0,.08);position:relative}
.bl small{display:block;font-size:19px;color:#8a8a8a;text-align:right;margin-top:4px}
.bl.eu{margin-left:auto;background:#DCF8C6}
.bl.robo{margin-left:auto;background:#DCF8C6;border:3px solid #25D366}
/* cartão de tela/foto */
.card{position:absolute;border-radius:36px;overflow:hidden;box-shadow:0 30px 70px rgba(10,30,80,.32);border:10px solid #fff;background:#fff}
.jan{position:absolute;border-radius:22px;overflow:hidden;box-shadow:0 30px 70px rgba(10,30,80,.30);background:#fff;border:2px solid #DCE5F5}
.jan .bar{height:44px;background:#EEF2F9;display:flex;align-items:center;padding:0 18px;gap:9px;border-bottom:2px solid #DCE5F5}
.jan .bar i{width:14px;height:14px;border-radius:50%;background:#F7941D;display:block}.jan .bar i:nth-child(2){background:#8DC63F}.jan .bar i:nth-child(3){background:#0A3D9E}
.jan .bar span{margin-left:14px;font-size:18px;color:#6b7aa0;font-weight:600}
.jan img{display:block;width:100%;object-fit:cover}
.card img{display:block;width:100%;height:100%;object-fit:cover;object-position:top}
.selinho{position:absolute;background:#F7941D;color:#fff;font-weight:700;font-size:24px;padding:10px 22px;border-radius:30px;box-shadow:0 10px 24px rgba(247,148,29,.4)}
.num{display:inline-flex;align-items:center;justify-content:center;width:92px;height:92px;border-radius:26px;background:#F7941D;color:#fff;font-weight:700;font-size:46px;margin-bottom:26px;transform:rotate(-6deg);box-shadow:0 12px 30px rgba(247,148,29,.4)}
/* tabela */
.tab{position:absolute;left:80px;right:80px;border-radius:30px;overflow:hidden;box-shadow:0 24px 60px rgba(10,30,80,.18);background:#fff}
.tab .lin{display:grid;grid-template-columns:1.05fr 1fr 1fr;font-size:28px;border-top:2px solid #EDF1F8}
.tab .lin div{padding:24px 22px;display:flex;align-items:center}
.tab .h{background:#0A3D9E;color:#fff;font-weight:700;border:0}
.tab .h div:nth-child(3){background:#8DC63F}
.tab .lin div:first-child{font-weight:600;color:#0B1F4D}
.tab .h div:first-child{color:#fff}
.tab .x{color:#c0392b;font-weight:600}.tab .ok{color:#2e8b1f;font-weight:700;background:#F3FAEA}
.botao{display:inline-block;margin-top:34px;background:#F7941D;color:#fff;font-weight:700;font-size:38px;padding:22px 48px;border-radius:60px;box-shadow:0 14px 30px rgba(247,148,29,.45)}
.lista{margin-top:40px;list-style:none}
.lista li{display:flex;align-items:center;font-size:36px;font-weight:600;margin-bottom:22px;background:#fff;border:2px solid #E3EAF6;border-radius:26px;padding:22px 26px;color:#0B1F4D}
.lista li b{flex:none;display:inline-flex;align-items:center;justify-content:center;width:62px;height:62px;border-radius:18px;background:#0A3D9E;color:#fff;margin-right:24px;font-size:30px}
.big{font-size:150px;font-weight:700;letter-spacing:-5px;line-height:1;color:#F7941D;-webkit-text-stroke:2px #F7941D}
"""


def cupom(x, y, w, cab, sub, linhas, rot=0, extra=""):
    ls = ""
    for l in linhas:
        if l == "-":
            ls += "<hr>"
        else:
            a, b, cls = (l + ("",))[:3]
            ls += f'<div class="ln {cls}"><span>{a}</span><span>{b}</span></div>'
    return f'<div class="cupom" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg);{extra}"><div class="cab">{cab}</div><div class="sub">{sub}</div><hr>{ls}</div>'


def chat(x, y, w, bolhas, titulo="WhatsApp", badge="19 não lidas", rot=0):
    bs = "".join(f'<div class="bl {c}">{t}<small>{h}</small></div>' for c, t, h in bolhas)
    return f'<div class="chat" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)"><div class="top">{titulo}<span>{badge}</span></div>{bs}</div>'


def card(src, x, y, w, rot=0, selo=None, sx=0, sy=0, h=None):
    s = f'<div class="selinho" style="left:{x + sx}px;top:{y + sy}px;transform:rotate({rot - 4}deg)">{selo}</div>' if selo else ""
    hh = f"height:{h}px;" if h else ""
    return f'<div class="card" style="left:{x}px;top:{y}px;width:{w}px;{hh}transform:rotate({rot}deg)"><img src="{src}"></div>{s}'


def jan(nome, x, y, w, h, rot=0, selo=None, sx=0, sy=0, pos="left top", titulo="Sistema Fácil Web · tela real"):
    s = f'<div class="selinho" style="left:{x + sx}px;top:{y + sy}px;transform:rotate({rot - 4}deg)">{selo}</div>' if selo else ""
    return f'<div class="jan" style="left:{x}px;top:{y}px;width:{w}px;transform:rotate({rot}deg)"><div class="bar"><i></i><i></i><i></i><span>{titulo}</span></div><img src="{FOTO(nome)}" style="height:{h}px;object-position:{pos}"></div>{s}'


def texto(tag, h1, p="", size=84, top=None, extra="", col=False):
    st = f"top:{top}px;" if top is not None else ""
    t = f'<div class="tag">{tag}</div>' if tag else ""
    pp = f"<p>{p}</p>" if p else ""
    return f'<div class="txt{" col" if col else ""}" style="{st}"><div>{t}<h1 style="font-size:{size}px">{h1}</h1>{pp}{extra}</div></div>'


def pagina(corpo, i=None, n=None, tema="", st=False, nota=""):
    pag = f'<div class="pag">{i}/{n}</div>' if i else ""
    nt = f'<div class="nota">{nota}</div>' if nota else ""
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body class="{tema} {'st' if st else ''}"><div class="pontos"></div><div class="faixa"></div>
<div class="selo"><img src="{LOGO}"></div>{pag}{corpo}{nt}
<div class="rod"><span>@facilweb</span><span>facilwebdelivery.com.br</span></div></body></html>"""


EX = "Exemplo com comissão de 27% sobre R$ 20 mil vendidos. Confira a taxa do seu contrato."


EX = "Exemplo com comissão de 27% sobre R$ 20 mil vendidos. Confira a taxa do seu contrato."
TG = '<div class="selinho" style="position:relative;display:inline-block;margin-top:26px;transform:rotate(-2deg);background:#8DC63F">Teste grátis pra restaurante novo</div>'

# ---------------- TER 17/11 · A conta da comissão (Black Friday) ----------------
P17 = [
    ("escuro", texto("A conta que o app não mostra", 'Vendeu <span class="v">R$ 20 mil</span><br>no app?', "", 92, 230)
     + cupom(240, 520, 660, "SEU MÊS NO APP", "exemplo · novembro", [("Vendas", "R$ 20.000"), ("Comissão 27%", "- R$ 5.400", "neg"), "-", ("Ficou no app", "R$ 5.400", "tot neg")], -4), EX),
    ("", texto("Num ano inteiro", 'São <span class="l">R$ 64.800</span><br>de comissão', "R$ 5.400 por mês, 12 meses. É um funcionário, uma reforma ou o seu capital de giro.", 84)
     + '<div style="position:absolute;left:80px;right:80px;top:600px;display:grid;grid-template-columns:repeat(4,1fr);gap:18px">'
     + "".join(f'<div style="background:#fff;border:2px solid #E3EAF6;border-radius:18px;padding:24px 0;text-align:center;font-weight:700;font-size:30px;color:#0A3D9E">{m}<div style="color:#d23b2a;font-size:26px;margin-top:4px">-5.400</div></div>' for m in ["JAN","FEV","MAR","ABR","MAI","JUN","JUL","AGO","SET","OUT","NOV","DEZ"]) + "</div>", EX),
    ("", texto("Black Friday no app", 'O desconto é seu.<br>A comissão <span class="m">também</span>.', "A promoção sai da sua margem e a taxa continua em cima de cada pedido, com desconto ou sem.", 80)
     + cupom(200, 760, 680, "PEDIDO #1042 · BLACK FRIDAY", "exemplo", [("Pizza G", "R$ 60,00"), ("Desconto 20%", "- R$ 12,00", "neg"), ("Comissão 27%", "- R$ 12,96", "neg"), "-", ("Sobra pra você", "R$ 35,04", "tot")], 2), ""),
    ("", texto("No seu canal", 'Promoção no seu<br>cardápio, <span class="v">taxa zero</span>', "O cliente gira a roleta de desconto, o cupom entra no pedido e não sai comissão nenhuma.", 80)
     + jan("sis_roleta", 120, 700, 840, 470, -2, pos="center 30%"), ""),
    ("", texto("Salva essa tabela", 'Quanto a comissão<br>de <span class="l">27%</span> leva', "", 80)
     + '<div class="tab" style="top:560px"><div class="lin h"><div>Vende por mês</div><div>Comissão 27%</div><div>No seu cardápio</div></div>'
     + "".join(f'<div class="lin"><div>{a}</div><div class="x">- {b}</div><div class="ok">R$ 0</div></div>' for a, b in [("R$ 10 mil", "R$ 2.700"), ("R$ 20 mil", "R$ 5.400"), ("R$ 40 mil", "R$ 10.800"), ("R$ 60 mil", "R$ 16.200")])
     + "</div>", "No cardápio digital da Fácil Web não existe taxa por pedido."),
    ("escuro cta", texto("Quer ver no seu restaurante?", 'Comenta<br><span class="v">QUERO</span>', "e a gente libera o teste grátis do seu cardápio digital, sem comissão por pedido.", 110, 300, '<div class="botao">COMENTA QUERO</div>') + jan("sis_cardapio", 560, 860, 460, 300, 4), ""),
]
S17 = [
    ("escuro", texto("Pergunta rápida", 'Quanto do seu<br>delivery fica <span class="v">no app?</span>', "Pega a fatura do mês e faz a conta: vendas x taxa.", 92)
     + cupom(240, 1050, 600, "FATURA DO APP", "exemplo", [("Vendas", "R$ 20.000"), ("Comissão", "- R$ 5.400", "neg")], -3), ""),
    ("", texto("Black Friday", 'O desconto é seu.<br>A comissão <span class="m">também</span>.', "No seu cardápio digital, a comissão é zero.", 88)
     + jan("sis_roleta", 70, 920, 940, 560, -2, pos="center 30%"), ""),
    ("", texto("Post novo no perfil", 'A conta completa<br>tá <span class="v">no feed</span>', "Salva a tabela e comenta QUERO no post pra testar grátis.", 92)
     + jan("sis_cardapio", 70, 960, 940, 520, 2), ""),
]

# ---------------- QUI 19/11 · Sexta, 20h no WhatsApp ----------------
P19 = [
    ("", texto("Sexta, 20h14", 'Você ainda anota<br>pedido <span class="m">picado?</span>', "", 88, 220)
     + chat(150, 560, 780, [("", "moço, cadê meu pedido??", "20:12"), ("", "é 1 calabresa e 1 frango", "20:13"), ("", "🎤 áudio 0:40", "20:13"), ("", "o endereço é aquele de sempre", "20:14"), ("", "troco pra 100", "20:14")], rot=-2), ""),
    ("", texto("O problema", 'Pedido picado<br>é o que <span class="l">dá erro</span>', "Endereço numa mensagem, troco em outra, sabor num áudio. Alguém copia pro papel e um erro faz a pizza voltar pro forno.", 78)
     + chat(260, 720, 560, [("", "e o refri?", "20:15"), ("", "esqueci, coloca uma coca 2L", "20:16"), ("", "cancela a de frango", "20:16")], badge="19 não lidas", rot=3), ""),
    ("", texto("", '<div class="num">01</div><br>O cliente monta<br><span class="v">sozinho</span>', "No seu cardápio digital: escolhe, adiciona e finaliza.", 76, 210)
     + jan("sis_cardapio", 90, 720, 900, 470, -2, pos='left top'), ""),
    ("", texto("", '<div class="num">02</div><br>O atendente virtual<br><span class="v">responde</span>', "No WhatsApp, até no pico de sexta. Tira a dúvida e manda o link do cardápio.", 76, 210, col=True)
     + chat(610, 440, 400, [("", "tá aberto?", "20:15"), ("robo", "Tá sim! Faz seu pedido por aqui: link do seu cardápio", "20:15")], titulo="Seu restaurante", badge="online", rot=3),
     "Exemplo de conversa."),
    ("", texto("", '<div class="num">03</div><br>Chega completo<br>no <span class="v">seu painel</span>', "Itens, endereço e pagamento num pedido só, e a impressão sai na cozinha.", 76, 210)
     + jan("sis_painel", 90, 740, 900, 440, 2, pos='left top'), ""),
    ("", texto("Salva e manda pra equipe", 'Sexta sem<br><span class="m">caçar pedido</span>', "", 82)
     + '<ul class="lista" style="position:absolute;left:80px;right:80px;top:560px"><li><b>1</b>Cliente monta no cardápio</li><li><b>2</b>Atendente virtual responde</li><li><b>3</b>Pedido completo no painel</li></ul>', ""),
    ("escuro cta", texto("Quer ver na sua loja?", 'Comenta<br><span class="v">QUERO</span>', "e a gente libera o seu teste grátis pra ver o pedido chegando completo.", 110, 300, '<div class="botao">COMENTA QUERO</div>') + jan("sis_cardapio", 560, 860, 460, 300, 4), ""),
]
S19 = [
    ("", texto("Sexta à noite é assim aí?", '19 conversas<br>e nenhum <span class="m">pedido pronto</span>', "", 88)
     + chat(150, 900, 780, [("", "cadê meu pedido??", "20:12"), ("", "🎤 áudio 0:40", "20:13"), ("", "troco pra 100", "20:14")], rot=-2), ""),
    ("", texto("Ou assim?", 'O cliente monta,<br><span class="v">você só prepara</span>', "Cardápio digital + atendente virtual no WhatsApp.", 88)
     + jan("sis_cardapio", 70, 920, 940, 560, -2, pos='left top'), ""),
    ("", texto("Post novo no perfil", 'O passo a passo<br>tá <span class="v">no feed</span>', "Comenta QUERO no post pra testar grátis.", 92)
     + jan("sis_painel", 70, 940, 940, 540, 2), ""),
]

# ---------------- SÁB 21/11 · App x canal próprio ----------------
P21 = [
    ("verde", texto("Faz a conta", 'Seu delivery ainda<br>paga <span class="v">27% por<br>pedido?</span>', "No seu cardápio digital, a taxa por pedido é zero.", 96, 220)
     + '<div style="position:absolute;left:80px;top:900px;display:flex;gap:26px"><div style="background:#fff;border-radius:28px;padding:26px 34px;color:#c0392b;font-weight:700;font-size:48px;box-shadow:0 20px 40px rgba(0,0,0,.18)">27% <span style="font-size:24px;color:#555">no app</span></div>'
     + '<div style="background:#0A3D9E;border-radius:28px;padding:26px 34px;color:#fff;font-weight:700;font-size:48px;box-shadow:0 20px 40px rgba(0,0,0,.18)">0% <span style="font-size:24px;color:#cfe0ff">no seu cardápio</span></div></div>',
     "Comissão de 27% como exemplo. Confira a taxa do seu contrato."),
    ("", texto("Lado a lado", 'App de delivery x<br><span class="v">seu canal</span>', "", 80)
     + '<div class="tab" style="top:500px"><div class="lin h"><div></div><div>App de delivery</div><div>Fácil Web</div></div>'
     + "".join(f'<div class="lin"><div>{a}</div><div class="x">{b}</div><div class="ok">{c}</div></div>' for a, b, c in [
         ("Taxa por pedido", "até 27%", "0%"), ("O cliente fica", "no app", "no seu cadastro"), ("Promoção", "você banca e paga taxa", "roleta e cupom no seu cardápio"),
         ("Pra começar", "cadastro e taxa", "teste grátis")]) + "</div>", "Taxa de app como exemplo. Confira a do seu contrato."),
    ("", texto("Não precisa sair de uma vez", 'O app vira<br><span class="m">vitrine</span>', "Quem te achou no app pode pedir direto da próxima vez: link na embalagem, QR code e pontos de fidelidade a cada pedido no seu cardápio.", 82)
     + jan("sis_pontos", 120, 800, 840, 380, -2, pos='left top'), ""),
    ("", texto("Salão também", 'A mesa paga<br><span class="v">na maquininha</span>', "Mesa, comanda, cardápio e pagamento no POS, com o mesmo cardápio do delivery.", 80)
     + card(FOTO("pos_11"), 140, 640, 800, -2, "Gravado com o sistema real", 40, -36, h=560), ""),
    ("", texto("Resumo pra salvar", 'Pedido próprio<br>em <span class="v">3 passos</span>', "", 82)
     + '<ul class="lista" style="position:absolute;left:80px;right:80px;top:560px"><li><b>1</b>Cardápio digital com o seu link</li><li><b>2</b>Link na bio, na embalagem e no WhatsApp</li><li><b>3</b>Pontos pra quem pede direto</li></ul>', ""),
    ("escuro cta", texto("Quer testar no seu restaurante?", 'Comenta<br><span class="v">QUERO</span>', "e a gente libera o seu teste grátis. Restaurante novo testa antes de decidir.", 110, 300, '<div class="botao">COMENTA QUERO</div>') + jan("sis_cardapio", 560, 860, 460, 300, 4), ""),
]
S21 = [
    ("verde", texto("Enquete rápida", 'Seu delivery hoje:<br><span class="v">app ou próprio?</span>', "Responde aqui no direct: APP, PRÓPRIO ou OS DOIS.", 88)
     + '<div style="position:absolute;left:80px;right:80px;top:900px;display:grid;gap:30px">' + "".join(f'<div style="background:{c};color:{t};border-radius:36px;padding:44px;font-size:56px;font-weight:700;text-align:center;box-shadow:0 20px 40px rgba(0,0,0,.18)">{x}</div>' for x, c, t in [("APP", "#fff", "#c0392b"), ("PRÓPRIO", "#0A3D9E", "#fff"), ("OS DOIS", "#F7941D", "#fff")]) + "</div>", ""),
    ("", texto("Sábado de salão cheio", 'A mesa paga<br><span class="v">sem fila</span>', "Débito, crédito ou Pix na maquininha.", 92)
     + card(FOTO("pos_11"), 120, 900, 840, -2, "Sistema real", 40, -36, h=720), ""),
    ("", texto("Post novo no perfil", 'App x canal próprio<br><span class="v">lado a lado</span>', "Comenta QUERO no post pra testar grátis.", 88)
     + jan("sis_pontos", 70, 960, 940, 460, 2), ""),
]

POSTS = {"2026-11-17": (P17, S17), "2026-11-19": (P19, S19), "2026-11-21": (P21, S21)}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for data, (slides, stories) in POSTS.items():
            os.makedirs(os.path.join(OUT, data), exist_ok=True)
            itens = [(f"carrossel-slide-{i + 1:02d}.jpg", s, False, i + 1) for i, s in enumerate(slides)]
            itens += [(f"story-{i + 1}.jpg", s, True, None) for i, s in enumerate(stories)]
            for nome, (tema, corpo, nota), st, i in itens:
                pg = await b.new_page(viewport={"width": 1080, "height": 1920 if st else 1350})
                await pg.set_content(pagina(corpo, i, len(slides), tema, st, nota))
                await pg.wait_for_timeout(250)
                tmp = os.path.join(OUT, data, "_t.png")
                await pg.screenshot(path=tmp)
                await pg.close()
                Image.open(tmp).convert("RGB").save(os.path.join(OUT, data, nome), quality=92)
                os.remove(tmp)
        await b.close()


if __name__ == "__main__":
    asyncio.run(main())
