"""Semana 23-29/11/2026 @facilweb · mesmo padrão visual aprovado em 16/11 (v3).

Reaproveita CSS e componentes de ../2026-11-16/v3/gerar_v3.py (cupom, chat, janela com
tela real do sistema, tabela, lista) e a logomarca sistema/logo.png no selo branco em
TODAS as peças. Sem valor de mensalidade. CTA: Comenta QUERO -> teste grátis.

Uso: python3 gerar_semana.py   ->  saida/AAAA-MM-DD/carrossel-slide-NN.jpg e story-N.jpg
"""
import asyncio, importlib.util, os
from playwright.async_api import async_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v3", os.path.join(HERE, "..", "2026-11-16", "v3", "gerar_v3.py"))
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)
texto, cupom, chat, jan, pagina = v3.texto, v3.cupom, v3.chat, v3.jan, v3.pagina
OUT = os.path.join(HERE, "saida")


def cta(p):
    return ("escuro cta", texto("Quer ver no seu restaurante?", 'Comenta<br><span class="v">QUERO</span>', p, 110, 300,
                                '<div class="botao">COMENTA QUERO</div>') + jan("sis_cardapio", 560, 860, 460, 300, 4), "")


def lista(itens, top=560):
    return f'<ul class="lista" style="position:absolute;left:80px;right:80px;top:{top}px">' + "".join(
        f"<li><b>{i + 1}</b>{t}</li>" for i, t in enumerate(itens)) + "</ul>"


EX = "Exemplo: pedido de R$ 60, desconto de 20% e comissão de 27%. Confira a taxa do seu contrato."

# ---------------- TER 24/11 · Black Friday no seu link ----------------
P24 = [
    ("escuro", texto("Faltam 3 dias pra Black Friday", 'Você dá <span class="v">20%</span>.<br>O app leva <span class="m">27%</span>.', "", 96, 230)
     + cupom(230, 600, 640, "PEDIDO BLACK FRIDAY", "exemplo · no app", [("Pizza G", "R$ 60,00"), ("Desconto 20%", "- R$ 12,00", "neg"),
             ("Comissão 27%", "- R$ 12,96", "neg"), "-", ("Fica pra você", "R$ 35,04", "tot")], -3), EX),
    ("", texto("O que está em jogo", 'A promoção é sua.<br>O pedido <span class="m">também</span><br>pode ser.', "Monta a mesma Black Friday no seu cardápio digital, em 3 peças, e o pedido entra sem taxa.", 82)
     + '<div style="position:absolute;left:80px;top:860px;display:flex;gap:26px"><div style="background:#fff;border-radius:28px;padding:26px 34px;color:#c0392b;font-weight:700;font-size:48px;box-shadow:0 20px 40px rgba(10,30,80,.15)">27% <span style="font-size:24px;color:#555">no app</span></div>'
     + '<div style="background:#0A3D9E;border-radius:28px;padding:26px 34px;color:#fff;font-weight:700;font-size:48px;box-shadow:0 20px 40px rgba(10,30,80,.2)">0% <span style="font-size:24px;color:#cfe0ff">no seu link</span></div></div>',
     "Comissão de 27% como exemplo. Confira a do seu contrato."),
    ("", texto("", '<div class="num">01</div><br>Cria o cupom<br><span class="v">BLACK</span>', "No painel: valor do desconto, pedido mínimo e validade.", 76, 210)
     + jan("sis_cupons", 90, 740, 900, 440, -2, pos="left top"), ""),
    ("", texto("", '<div class="num">02</div><br>Liga a roleta<br>de <span class="v">desconto</span>', "O cliente gira e o desconto entra direto no pedido.", 76, 210)
     + jan("sis_roleta", 90, 740, 900, 440, 2, pos="center 30%"), ""),
    ("", texto("", '<div class="num">03</div><br>Divulga com o<br><span class="v">seu link</span>', "O sistema entrega o post com o print do seu cardápio e o seu link pra postar.", 76, 210)
     + jan("sis_posts", 90, 760, 900, 420, -2, pos="center 40%"), ""),
    ("", texto("Salva pra montar até quinta", 'Black Friday<br>no <span class="m">seu link</span>', "", 84)
     + lista(["Cupom BLACK no painel", "Roleta de desconto ligada", "Post com o seu link no ar"]), "No cardápio digital da Fácil Web não existe taxa por pedido."),
    cta("e a gente libera o teste grátis pra sua Black Friday rodar no seu cardápio."),
]
S24 = [
    ("escuro", texto("Faltam 3 dias", 'Sua Black Friday<br>vai rodar <span class="v">no app?</span>', "Desconto de 20% + comissão de 27% no mesmo pedido.", 92)
     + cupom(240, 1030, 600, "PEDIDO R$ 60", "exemplo", [("Desconto 20%", "- R$ 12,00", "neg"), ("Comissão 27%", "- R$ 12,96", "neg")], -3), ""),
    ("", texto("No seu cardápio", 'Cupom e roleta<br>com <span class="v">taxa zero</span>', "O cliente gira e o desconto entra no pedido.", 92)
     + jan("sis_roleta", 70, 920, 940, 560, -2, pos="center 30%"), ""),
    ("", texto("Post novo no perfil", 'As 3 peças da<br>Black Friday <span class="v">no feed</span>', "Comenta QUERO no post pra testar grátis.", 92)
     + jan("sis_cupons", 70, 960, 940, 520, 2), ""),
]

# ---------------- QUI 26/11 · Abandono de carrinho ----------------
CAR = [("Pizza G calabresa", "R$ 59,00"), ("Coca-Cola 2L", "R$ 15,00"), "-", ("Total", "R$ 74,00", "tot"), ("Status", "não finalizado", "neg")]
P26 = [
    ("", texto("Sexta, 21h07", '<span class="l">R$ 74</span> no carrinho<br>e o cliente <span class="m">sumiu?</span>', "", 88, 220)
     + cupom(230, 600, 640, "CARRINHO · SEU CARDÁPIO", "exemplo", CAR, -3), "Valores de exemplo."),
    ("", texto("Acontece toda noite", 'Escolheu, colocou<br>no carrinho e <span class="l">parou</span>', "Tocou o telefone, o filho chamou, a bateria acabou. O pedido fica parado e ninguém na loja fica sabendo.", 80)
     + chat(260, 650, 560, [("", "🍕 Pizza G calabresa adicionada", "21:05"), ("", "🥤 Coca-Cola 2L adicionada", "21:06"), ("", "… carrinho parado", "21:07")], titulo="Seu cardápio", badge="sem pedido", rot=3), ""),
    ("", texto("", '<div class="num">01</div><br>Liga o abandono<br>de <span class="v">carrinho</span>', "Uma marcação no painel e o sistema passa a acompanhar os carrinhos parados.", 76, 210)
     + jan("sis_carrinho", 90, 760, 900, 420, -2, pos="left top"), ""),
    ("", texto("", '<div class="num">02</div><br>O sistema avisa<br>o <span class="v">cliente</span>', "Lembra que os itens do carrinho estão esperando por ele.", 76, 210, col=True)
     + chat(600, 470, 410, [("robo", "Olá, Ana! Os itens do seu carrinho estão esperando por você. Aproveite!", "21:40")], titulo="Seu restaurante", badge="aviso", rot=3),
     "Exemplo com o texto padrão do sistema."),
    ("", texto("", '<div class="num">03</div><br>Se quiser,<br>dá um <span class="v">desconto</span>', "Você escolhe a % que entra no aviso pra ajudar a fechar o pedido.", 76, 210)
     + jan("sis_carrinho", 90, 760, 900, 420, 2, pos="left bottom"), ""),
    ("", texto("Salva e liga no painel", 'Carrinho parado<br>vira <span class="m">pedido</span>', "", 84)
     + lista(["Liga o abandono de carrinho", "O sistema avisa o cliente", "Desconto opcional em %"]), ""),
    cta("e a gente libera o teste grátis pra você ver o abandono de carrinho funcionando."),
]
S26 = [
    ("", texto("Já aconteceu aí?", '<span class="l">R$ 74</span> no carrinho<br>e <span class="m">nenhum pedido</span>', "", 92)
     + cupom(240, 950, 600, "CARRINHO", "exemplo", CAR, -3), ""),
    ("", texto("No sistema Fácil Web", 'O cliente recebe<br>um <span class="v">lembrete</span>', "Com desconto, se você quiser.", 92)
     + chat(150, 940, 780, [("robo", "Olá, Ana! Os itens do seu carrinho estão esperando por você. Aproveite!", "21:40")], titulo="Seu restaurante", badge="aviso", rot=-2), ""),
    ("", texto("Post novo no perfil", 'Abandono de carrinho<br><span class="v">no feed</span>', "Comenta QUERO no post pra testar grátis.", 92)
     + jan("sis_carrinho", 70, 960, 940, 520, 2), ""),
]

# ---------------- SEX 27/11 · Black Friday (só stories) ----------------
S27 = [
    ("escuro", texto("Hoje é Black Friday", 'Seu desconto tá<br>no <span class="v">seu link</span><br>ou no app?', "No seu cardápio digital, o pedido entra sem taxa.", 96)
     + jan("sis_roleta", 70, 1000, 940, 500, -2, pos="center 30%"), ""),
    ("", texto("Ainda dá tempo de ver", 'Cupom, roleta<br>e <span class="v">post pronto</span>', "O passo a passo tá no post de terça. Comenta QUERO lá pra testar grátis.", 92)
     + jan("sis_cupons", 70, 980, 940, 500, 2), ""),
]

# ---------------- SÁB 28/11 · Fidelidade depois da Black Friday ----------------
EXP = "Exemplo de regra: 1 ponto a cada R$ 20, cada ponto vale R$ 1, mínimo de 5 pontos pra troca. Você define a sua."
P28 = [
    ("verde", texto("Depois da Black Friday", 'Cliente novo?<br>Sem ponto, ele<br><span class="v">some em dezembro</span>', "", 92, 220)
     + cupom(300, 830, 560, "EXTRATO DE PONTOS", "exemplo · cliente Ana", [("Pedido 27/11", "R$ 60,00"), ("Pontos ganhos", "+ 3", "pos")], -3), EXP),
    ("", texto("O que está em jogo", 'Cliente de promoção<br><span class="l">não volta sozinho</span>', "Ele precisa de um motivo pra pedir de novo direto com você, e não no app.", 80)
     + chat(260, 820, 560, [("", "Pedido #2318 · 27/11", "Black Friday"), ("", "Dezembro: nenhum pedido", "—")], titulo="Cliente Ana", badge="sumiu", rot=3), ""),
    ("", texto("", '<div class="num">01</div><br>Cada pedido<br>gera <span class="v">pontos</span>', "Você define a regra: 1 ponto a cada R$ 20, por exemplo. Cada ponto vale R$ 1 na troca.", 76, 210)
     + jan("sis_pontos", 90, 780, 900, 400, -2, pos="left top"), ""),
    ("", texto("Na prática", 'Mais um pedido<br>e ela <span class="m">troca</span>', "", 82)
     + cupom(230, 520, 640, "EXTRATO DE PONTOS", "exemplo · cliente Ana", [("Pedido 27/11 · R$ 60", "+ 3", "pos"), ("Pedido 12/12 · R$ 40", "+ 2", "pos"), "-",
             ("Saldo", "5 pontos", "tot"), ("Vale na troca", "R$ 5,00", "pos")], 2), EXP),
    ("", texto("", '<div class="num">02</div><br>Validade e<br><span class="v">relatório</span>', "Você escolhe a validade dos pontos e vê quem tem ponto pra usar. É a desculpa certa pra chamar o cliente.", 76, 210)
     + jan("sis_pontos", 90, 820, 900, 360, 2, pos="right top"), ""),
    ("", texto("Salva pra configurar", 'Cliente da Black<br>Friday <span class="m">volta</span>', "", 84)
     + lista(["Liga os pontos de fidelidade", "Define R$ por ponto e validade", "Chama quem tem ponto pra usar"]), ""),
    cta("e a gente libera o teste grátis com os pontos de fidelidade no seu cardápio."),
]
S28 = [
    ("verde", texto("Pergunta de sábado", 'O cliente da Black<br>Friday vai <span class="v">voltar?</span>', "Responde no direct: SIM, NÃO SEI ou ESPERO QUE SIM.", 88)
     + '<div style="position:absolute;left:80px;right:80px;top:980px;display:grid;gap:30px">' + "".join(
         f'<div style="background:{c};color:{t};border-radius:36px;padding:40px;font-size:52px;font-weight:700;text-align:center;box-shadow:0 20px 40px rgba(0,0,0,.18)">{x}</div>'
         for x, c, t in [("SIM", "#0A3D9E", "#fff"), ("NÃO SEI", "#fff", "#c0392b"), ("ESPERO QUE SIM", "#F7941D", "#fff")]) + "</div>", ""),
    ("", texto("Motivo pra voltar", 'Cada pedido<br>vira <span class="v">ponto</span>', "E o ponto vira desconto no próximo pedido.", 92)
     + jan("sis_pontos", 70, 940, 940, 520, -2), ""),
    ("", texto("Post novo no perfil", 'Fidelidade depois da<br>Black Friday <span class="v">no feed</span>', "Comenta QUERO no post pra testar grátis.", 88)
     + cupom(240, 1000, 600, "EXTRATO DE PONTOS", "exemplo", [("Saldo", "5 pontos", "tot"), ("Vale na troca", "R$ 5,00", "pos")], 2), ""),
]

POSTS = {"2026-11-24": (P24, S24), "2026-11-26": (P26, S26), "2026-11-27": ([], S27), "2026-11-28": (P28, S28)}


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
