"""Transforma um print de tela (celular ou recorte do sistema) na tela 600x1300 usada nos celulares 3D.

Uso: python3 tela.py print.png saida.png [--modo cobrir|caber] [--fundo #ffffff] [--topo 0]
  cobrir (padrão): preenche a tela inteira, cortando o que sobrar embaixo.
  caber: mostra o print inteiro, com faixas da cor de fundo.
  --topo N: pula N pixels do topo do print (ex.: barra do navegador).
"""
import argparse
from PIL import Image

ap = argparse.ArgumentParser()
ap.add_argument("entrada"); ap.add_argument("saida")
ap.add_argument("--modo", default="cobrir", choices=["cobrir", "caber"])
ap.add_argument("--fundo", default="#ffffff"); ap.add_argument("--topo", type=int, default=0)
a = ap.parse_args()
W, H = 600, 1300
im = Image.open(a.entrada).convert("RGB")
if a.topo: im = im.crop((0, a.topo, im.width, im.height))
tela = Image.new("RGB", (W, H), a.fundo)
if a.modo == "cobrir":
    esc = W / im.width; im = im.resize((W, max(1, int(im.height * esc))), Image.LANCZOS)
    if im.height < H:
        esc = H / im.height; im = im.resize((int(im.width * esc), H), Image.LANCZOS)
        x = (im.width - W) // 2; im = im.crop((x, 0, x + W, H))
    tela.paste(im.crop((0, 0, W, H)), (0, 0))
else:
    esc = min(W / im.width, H / im.height); im = im.resize((int(im.width * esc), int(im.height * esc)), Image.LANCZOS)
    tela.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
tela.save(a.saida); print("ok", a.saida)
