"""Telas extras (600x1300) para a semana 09-15/11/2026: WhatsApp, pedido, cozinha, mesas, pagamento e caixa.
Todas são ilustrações da conta de demonstração "Seu Delivery" (sem nome de cliente real)."""
import asyncio, os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "telas")
LAR = "#d96b0b"
BASE = """<style>*{margin:0;padding:0;box-sizing:border-box}body{width:600px;height:1300px;overflow:hidden;
font-family:Poppins,Inter,sans-serif;background:#f4f4f6;position:relative;color:#222}
.status{height:70px;display:flex;justify-content:space-between;align-items:center;padding:0 40px;font-weight:600;font-size:24px}
.zap{background:#075e54;color:#fff}</style>"""

def chat(nome, msg, hora, n, cor):
    return f"""<div style="display:flex;align-items:center;padding:20px 26px;border-bottom:1px solid #eee;background:#fff">
<div style="width:78px;height:78px;border-radius:50%;background:{cor};flex:none;margin-right:20px;color:#fff;font-weight:700;font-size:34px;
display:flex;align-items:center;justify-content:center">{nome[0]}</div>
<div style="flex:1;min-width:0"><div style="display:flex;justify-content:space-between"><b style="font-size:28px">{nome}</b>
<span style="font-size:20px;color:#25d366;font-weight:600">{hora}</span></div>
<div style="display:flex;justify-content:space-between;align-items:center;margin-top:6px"><span style="font-size:24px;color:#666;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:380px">{msg}</span>
<span style="background:#25d366;color:#fff;font-size:20px;font-weight:700;border-radius:20px;min-width:36px;height:36px;display:flex;align-items:center;justify-content:center;padding:0 8px">{n}</span></div></div></div>"""

CHATS = [("Ana", "é 1 calabresa e 1 frango", "20:14", 3, "#e67e22"), ("Bruno", "🎤 Áudio (0:40)", "20:13", 2, "#2980b9"),
         ("Carla", "manda o cardápio?", "20:13", 1, "#8e44ad"), ("Diego", "cadê meu pedido??", "20:12", 4, "#c0392b"),
         ("Elaine", "troco pra 100", "20:11", 2, "#16a085"), ("Fábio", "o endereço é aquele de sempre", "20:10", 1, "#d35400"),
         ("Gabi", "sem cebola, por favor", "20:10", 3, "#27ae60"), ("Hugo", "ainda dá tempo de mudar?", "20:09", 1, "#7f8c8d"),
         ("Iara", "foto do cardápio.jpg", "20:08", 2, "#2c3e50")]

TELAS = {
 "zap_caos": BASE + """<div class="status zap"><span>20:14</span><span>●●● ▮</span></div>
<div class="zap" style="height:100px;display:flex;align-items:center;justify-content:space-between;padding:0 30px;font-size:36px;font-weight:700">WhatsApp
<span style="background:#25d366;border-radius:30px;font-size:22px;padding:6px 16px">19 não lidas</span></div>""" + "".join(chat(*c) for c in CHATS),

 "pedido": BASE + """<div class="status zap"><span>20:14</span><span>●●● ▮</span></div>
<div class="zap" style="height:110px;display:flex;align-items:center;padding:0 30px;font-size:32px;font-weight:600">
<div style="width:64px;height:64px;border-radius:50%;background:#d96b0b;margin-right:20px"></div>Seu Delivery</div>
<div style="position:absolute;top:180px;bottom:0;left:0;right:0;background:#ece5dd"></div>
<div style="position:absolute;top:240px;left:30px;right:60px;background:#fff;border-radius:6px 26px 26px 26px;padding:30px;font-size:27px;line-height:1.5;box-shadow:0 2px 6px rgba(0,0,0,.1)">
<div style="font-weight:800;color:#d96b0b;font-size:30px">Novo pedido #1042</div>
<div style="border-top:2px dashed #ddd;margin:14px 0"></div>
1x Pizza Calabresa G<br><span style="color:#888">  sem cebola</span><br>1x Pizza Frango c/ Catupiry G<br>1x Refrigerante 2L
<div style="border-top:2px dashed #ddd;margin:14px 0"></div>
<b>Entrega:</b> Rua das Flores, 120<br><b>Pagamento:</b> Pix<br><b>Total:</b> R$ 118,00
<div style="text-align:right;font-size:22px;color:#999;margin-top:8px">20:14</div></div>
<div style="position:absolute;top:960px;left:0;right:0;text-align:center"><span style="background:#e1f3fb;color:#555;font-size:22px;padding:8px 20px;border-radius:12px">pedido feito pelo cardápio digital</span></div>
<div style="position:absolute;bottom:40px;left:0;right:0;text-align:center;font-size:20px;color:#999">exemplo · conta de demonstração</div>""",

 "cozinha": BASE + """<div style="position:absolute;inset:0;background:linear-gradient(180deg,#2b2f36,#16181c)"></div>
<div style="position:absolute;top:60px;left:60px;right:60px;height:90px;background:#3a3f48;border-radius:24px 24px 6px 6px;box-shadow:inset 0 -10px 0 #111"></div>
<div style="position:absolute;top:120px;left:90px;right:90px;background:#fffdf7;padding:40px 36px 60px;font-family:'Courier New',monospace;font-size:28px;line-height:1.55;color:#111;
box-shadow:0 20px 40px rgba(0,0,0,.5);clip-path:polygon(0 0,100% 0,100% 97%,95% 100%,90% 97%,85% 100%,80% 97%,75% 100%,70% 97%,65% 100%,60% 97%,55% 100%,50% 97%,45% 100%,40% 97%,35% 100%,30% 97%,25% 100%,20% 97%,15% 100%,10% 97%,5% 100%,0 97%)">
<div style="text-align:center;font-weight:900;font-size:36px">COZINHA</div><div style="text-align:center">Pedido #1042 · 20:14</div>
<div style="border-top:3px dashed #111;margin:18px 0"></div>
<b>1x PIZZA CALABRESA G</b><br>  >> SEM CEBOLA<br><b>1x PIZZA FRANGO C/ CATUPIRY G</b><br><b>1x REFRIGERANTE 2L</b>
<div style="border-top:3px dashed #111;margin:18px 0"></div>
ENTREGA<br>Rua das Flores, 120<br>PAGO NO PIX
<div style="border-top:3px dashed #111;margin:18px 0"></div><div style="text-align:center">Seu Delivery</div></div>""",

 "comanda": BASE + """<div class="status" style="background:#fff"><span>21:40</span><span>●●● ▮</span></div>
<div style="background:#d96b0b;color:#fff;height:120px;display:flex;align-items:center;padding:0 34px;font-size:40px;font-weight:800">Mesas</div>
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;padding:30px">""" + "".join(
    f"""<div style="height:150px;border-radius:22px;background:{'#d96b0b' if o else '#fff'};color:{'#fff' if o else '#333'};box-shadow:0 6px 16px rgba(0,0,0,.08);
display:flex;flex-direction:column;align-items:center;justify-content:center;font-weight:800;font-size:34px">{i:02d}<span style="font-size:20px;font-weight:600;opacity:.85">{'ocupada' if o else 'livre'}</span></div>"""
    for i, o in zip(range(1, 13), [1,0,1,1,0,0,1,0,1,0,0,1])) + """</div>
<div style="margin:10px 30px;background:#fff;border-radius:22px;padding:26px;font-size:26px;box-shadow:0 6px 16px rgba(0,0,0,.08)"><b>Mesa 07</b> · comanda aberta<br><span style="color:#888">4 itens lançados pelo garçom</span></div>""",

 "pos": BASE + """<div class="status" style="background:#fff"><span>21:52</span><span>●●● ▮</span></div>
<div style="background:#d96b0b;color:#fff;height:120px;display:flex;align-items:center;padding:0 34px;font-size:40px;font-weight:800">Mesa 07 · Pagamento</div>
<div style="text-align:center;margin-top:60px;font-size:28px;color:#777">Total da mesa</div>
<div style="text-align:center;font-size:84px;font-weight:900">R$ 86,50</div>
<div style="padding:40px 40px 0">""" + "".join(
    f"""<div style="height:120px;border-radius:24px;margin-bottom:24px;background:{c};color:#fff;font-size:38px;font-weight:800;display:flex;align-items:center;justify-content:center">{t}</div>"""
    for t, c in [("Débito", "#2c3e50"), ("Crédito", "#34495e"), ("Pix", "#16a085")]) + """</div>
<div style="margin:20px 40px;border:3px dashed #ccc;border-radius:22px;padding:24px;text-align:center;font-size:26px;color:#555">Comprovante impresso na maquininha</div>
<div style="position:absolute;bottom:40px;left:0;right:0;text-align:center;font-size:20px;color:#999">exemplo · conta de demonstração</div>""",

 "caixa": BASE + """<div class="status" style="background:#fff"><span>23:02</span><span>●●● ▮</span></div>
<div style="padding:30px 34px 10px;font-size:40px;font-weight:800">Fechamento do caixa</div>
<div style="padding:0 34px;font-size:24px;color:#888">Salão + delivery · hoje</div>
<div style="margin:30px;background:#fff;border-radius:24px;padding:10px 30px;box-shadow:0 8px 24px rgba(0,0,0,.08)">""" + "".join(
    f"""<div style="display:flex;justify-content:space-between;padding:24px 0;border-bottom:1px solid #eee;font-size:30px"><span>{a}</span><b>{b}</b></div>"""
    for a, b in [("Pix", "R$ 1.240,00"), ("Crédito", "R$ 980,50"), ("Débito", "R$ 615,00"), ("Dinheiro", "R$ 310,00")]) + """
<div style="display:flex;justify-content:space-between;padding:28px 0;font-size:34px;font-weight:900;color:#d96b0b"><span>Total</span><span>R$ 3.145,50</span></div></div>
<div style="margin:0 30px;display:flex;gap:20px"><div style="flex:1;background:#fff;border-radius:20px;padding:24px;font-size:24px;box-shadow:0 8px 24px rgba(0,0,0,.08)">Salão<br><b style="font-size:32px">38 comandas</b></div>
<div style="flex:1;background:#fff;border-radius:20px;padding:24px;font-size:24px;box-shadow:0 8px 24px rgba(0,0,0,.08)">Delivery<br><b style="font-size:32px">27 pedidos</b></div></div>
<div style="position:absolute;bottom:40px;left:0;right:0;text-align:center;font-size:20px;color:#999">exemplo · conta de demonstração</div>""",
}


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 600, "height": 1300})
        for k, html in TELAS.items():
            await pg.set_content('<!doctype html><meta charset=utf-8>' + html)
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=os.path.join(OUT, f"{k}.png"))
        await b.close()

asyncio.run(main())
