"""Celulares 3D (PNG transparente, recortado) com as telas reais do app, para artes e cartões.

Uso (na pasta de trabalho):  python3 kit/video/narrado/fones.py fones.json   → fones/<nome>.png
fones.json: {"hoje": ["hoje-full", 0, "direita"], "zap": ["whatsapp", 0, "esquerda"], ...}
  tela = estados/<tela>.png (print 1080 de largura) · rolagem em px · ângulo: direita | esquerda | frente
"""
import asyncio, json, os, signal, subprocess, sys, time
from PIL import Image

KIT = os.path.dirname(os.path.abspath(__file__))
ANG = {"direita": (0.05, -0.32, 0.02), "esquerda": (0.05, 0.32, -0.02), "frente": (0.03, -0.08, 0.0)}


async def main(cfg):
    from playwright.async_api import async_playwright
    for nome, alvo in (("fone.html", f"{KIT}/fone.html"), ("three", f"{KIT}/node_modules/three")):
        if not os.path.exists(nome): os.symlink(alvo, nome)
    os.makedirs("fones", exist_ok=True)
    srv = subprocess.Popen(["python3", "-m", "http.server", "8812", "--bind", "127.0.0.1"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = await b.new_page(viewport={"width": 1200, "height": 2000})
            pg.on("pageerror", lambda e: print("pageerror:", e))
            await pg.goto("http://127.0.0.1:8812/fone.html")
            await pg.wait_for_function("window.pronto === true", timeout=60000)
            for nome, (tela, y, ang) in cfg.items():
                rx, ry, rz = ANG.get(ang, ANG["direita"]) if isinstance(ang, str) else ang
                await pg.evaluate(f"foto({{tela:'{tela}', y:{y}, rx:{rx}, ry:{ry}, rz:{rz}}})")
                f = f"fones/{nome}.png"
                await pg.screenshot(path=f, omit_background=True)
                im = Image.open(f); im.crop(im.getbbox()).save(f)
                print(nome, Image.open(f).size, flush=True)
            await b.close()
    finally:
        srv.send_signal(signal.SIGTERM); srv.wait()


asyncio.run(main(json.load(open(sys.argv[1]))))
