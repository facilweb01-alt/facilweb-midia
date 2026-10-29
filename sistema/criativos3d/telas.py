"""Monta telas verticais de celular (600x1300) com recortes reais do sistema Fácil Web."""
import asyncio, base64, os
from PIL import Image
from playwright.async_api import async_playwright

S = os.path.join(os.path.dirname(os.path.abspath(__file__)), "prints")  # prints do painel, conta de demonstração
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "telas")
os.makedirs(OUT, exist_ok=True)


def crop(f, box, name):
    p = os.path.join(OUT, f"_{name}.png")
    im = Image.open(f"{S}/{f}").convert("RGB")
    if f == C:  # apaga a seta do mouse que ficou no print
        from PIL import ImageDraw
        ImageDraw.Draw(im).rectangle((675, 398, 705, 432), fill=(255, 255, 255))
    im.crop(box).save(p)
    return "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()


C = "screenshot-1793279257232-11.jpg"   # cardápio rolado
R = "screenshot-1793279257230-9.jpg"    # roleta
A = "screenshot-1793279282552-14.jpg"   # artes postagem
D = "screenshot-1793279155753-1.jpg"    # dashboard
chips = crop(C, (0, 0, 600, 100), "chips")
card1 = crop(C, (15, 326, 435, 486), "card1")
card2 = crop(C, (465, 326, 885, 486), "card2")
card3 = crop(C, (916, 326, 1336, 486), "card3")
nav = crop(C, (383, 520, 983, 607), "nav")
roleta = crop(R, (466, 30, 886, 446), "roleta")
fundo_roleta = crop(R, (300, 0, 1066, 607), "fundo")
arte1 = crop(A, (438, 98, 750, 410), "arte1")
arte2 = crop(A, (822, 98, 1134, 410), "arte2")
economia = crop(D, (250, 275, 587, 380), "economia")
link = crop(D, (984, 525, 1321, 607), "link")

BASE = """<style>*{margin:0;padding:0;box-sizing:border-box}body{width:600px;height:1300px;overflow:hidden;
font-family:Poppins,Inter,sans-serif;background:#f4f4f6;position:relative}
.status{height:70px;display:flex;justify-content:space-between;align-items:center;padding:0 40px;font-weight:600;font-size:24px}
img{display:block}</style>"""

TELAS = {
 "cardapio": f"""{BASE}<div class=status style="background:#fff"><span>9:41</span><span>●●● ▮</span></div>
 <div style="background:#d96b0b;height:150px;border-radius:0 0 36px 36px;display:flex;align-items:center;
 justify-content:center;color:#fff;font-weight:800;font-size:40px">Seu Delivery</div>
 <img src="{chips}" style="width:600px;margin-top:14px">
 <div style="padding:10px 20px 0;font-weight:700;color:#555;font-size:28px">Mais pedidos</div>
 <img src="{card1}" style="width:560px;margin:14px auto 0;border-radius:18px">
 <img src="{card2}" style="width:560px;margin:18px auto 0;border-radius:18px">
 <img src="{card3}" style="width:560px;margin:18px auto 0;border-radius:18px">
 <img src="{nav}" style="width:600px;position:absolute;bottom:0">""",
 "roleta": f"""{BASE}<img src="{fundo_roleta}" style="position:absolute;inset:0;width:600px;height:1300px;object-fit:cover;filter:blur(3px)">
 <div style="position:absolute;inset:0;background:rgba(0,0,0,.55)"></div>
 <img src="{roleta}" style="position:absolute;left:20px;top:380px;width:560px;border-radius:24px;box-shadow:0 20px 60px rgba(0,0,0,.5)">""",
 "pontos": f"""{BASE}<div class=status style="background:#fff"><span>9:41</span><span>●●● ▮</span></div>
 <div style="background:#d96b0b;height:150px;border-radius:0 0 36px 36px;display:flex;align-items:center;
 justify-content:center;color:#fff;font-weight:800;font-size:40px">Ganhe pontos</div>
 <div style="margin:30px 30px 0;background:#fff;border-radius:22px;padding:26px;font-size:30px;font-weight:700;color:#333;
 box-shadow:0 6px 20px rgba(0,0,0,.08)">Cada pedido vira ponto.<br><span style="color:#d96b0b">Troque por produtos.</span></div>
 <img src="{card2}" style="width:560px;margin:26px auto 0;border-radius:18px">
 <img src="{card3}" style="width:560px;margin:18px auto 0;border-radius:18px">
 <img src="{nav}" style="width:600px;position:absolute;bottom:0">""",
 "carrinho": f"""{BASE}<div class=status style="background:#075e54;color:#fff"><span>9:41</span><span>●●● ▮</span></div>
 <div style="background:#075e54;color:#fff;height:110px;display:flex;align-items:center;padding:0 30px;font-size:32px;font-weight:600">
 <div style="width:64px;height:64px;border-radius:50%;background:#d96b0b;margin-right:20px"></div>Seu Delivery</div>
 <div style="position:absolute;top:180px;bottom:0;left:0;right:0;background:#ece5dd"></div>
 <div style="position:absolute;top:300px;left:30px;right:90px;background:#fff;border-radius:6px 26px 26px 26px;padding:28px;
 font-size:30px;line-height:1.4;color:#222;box-shadow:0 2px 6px rgba(0,0,0,.1)">Olá, Ana! Os itens do seu carrinho estão
 esperando por você. Acabei de aplicar um desconto de 10% para você finalizar sua compra. Aproveite!
 <div style="text-align:right;font-size:22px;color:#999;margin-top:8px">19:32</div></div>
 <div style="position:absolute;top:700px;right:30px;background:#dcf8c6;border-radius:26px 6px 26px 26px;padding:24px 28px;
 font-size:30px;color:#222">Opa, vou finalizar agora! 😋
 <div style="text-align:right;font-size:22px;color:#999;margin-top:6px">19:33 ✓✓</div></div>""",
 "artes": f"""{BASE}<div class=status style="background:#fff"><span>9:41</span><span>●●● ▮</span></div>
 <div style="background:#fff;height:90px;display:flex;align-items:center;padding:0 30px;font-weight:700;font-size:34px">Instagram</div>
 <div style="background:#fff;padding:20px 30px;display:flex;align-items:center;font-weight:600;font-size:26px">
 <div style="width:56px;height:56px;border-radius:50%;background:#d96b0b;margin-right:16px"></div>seudelivery</div>
 <img src="{arte1}" style="width:600px">
 <div style="background:#fff;padding:22px 30px;font-size:26px;line-height:1.4;color:#222"><b>seudelivery</b> Faça seu pedido em nosso delivery 👉 link na bio</div>
 <img src="{arte2}" style="width:600px">""",
 "economia": f"""{BASE}<div class=status style="background:#fff"><span>9:41</span><span>●●● ▮</span></div>
 <div style="padding:30px;font-size:38px;font-weight:800;color:#222">Painel</div>
 <img src="{economia}" style="width:540px;margin:10px auto 0;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.15)">
 <img src="{link}" style="width:540px;margin:30px auto 0;border-radius:14px;box-shadow:0 10px 30px rgba(0,0,0,.15)">
 <div style="margin:40px 30px;font-size:24px;color:#999">Conta de demonstração</div>""",
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
