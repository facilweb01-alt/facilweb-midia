"""Reel 3D @facilweb (1080x1920): cenas animadas em 3D + fundo + texto, montadas com ffmpeg."""
import asyncio, base64, json, os, random, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
b64 = lambda p: "data:image/png;base64," + base64.b64encode(open(p, "rb").read()).decode()
LOGO = b64("" + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logo.png") + "")
W, H, FPS = 1080, 1920, 24


def phone(tex, pos, rot, s=1.0, fase=0):
    return {"tex": f"telas/{tex}.png", "pos": pos, "rot": rot, "s": s, "fase": fase}


def um(tex, lado):
    x = 0.32 if lado == "d" else -0.32
    return {"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "giro": 0.32, "flutua": 0.04,
            "phones": [phone(tex, [x, -0.62, 0], [0.08, -0.3 if lado == "d" else 0.3, 0], 0.9)],
            "moedas": [{"pos": [-x * 3.2, -0.2, 0.6], "s": 1.1}, {"pos": [x * 3.0, -1.05, 0.8], "s": 0.9},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [-x * 2.6, -1.0, 0.5], "s": 0.9},
                       {"tipo": "esfera", "cor": "#F7941D", "pos": [x * 2.8, 0.05, 0.3], "s": 0.7}]}


random.seed(3)
CENAS = {
    "c1": dict(d=2.6, cfg={"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "giro": 0.12, "flutua": 0.05,
            "phones": [phone("roleta", [-0.62, -0.75, -0.5], [0.05, 0.5, 0.1], 0.72, 1.5),
                       phone("carrinho", [0.62, -0.75, -0.5], [0.05, -0.5, -0.1], 0.72, 3.0),
                       phone("cardapio", [0, -0.68, 0.3], [0.08, -0.1, 0], 0.82)],
            "moedas": [{"pos": [-0.75, -0.05, 0.9], "s": 1}, {"pos": [0.8, -1.25, 0.9], "s": 0.9},
                       {"tipo": "esfera", "cor": "#8DC63F", "pos": [0.78, -0.05, 0.8], "s": 0.8}]}),
    "c2": dict(d=3.0, cfg={"w": W, "h": H, "fov": 28, "cam": [0, 0, 5.2], "phones": [],
            "moedas": [{"pos": [random.uniform(-0.8, 0.8), random.uniform(-1.3, -0.1), random.uniform(-0.6, 1.4)],
                        "rot": [random.uniform(0.3, 1.5), random.uniform(0, 3), random.uniform(-1, 1)],
                        "s": random.uniform(0.8, 1.3)} for _ in range(22)]}),
    "c3": dict(d=2.6, cfg=um("cardapio", "d")),
    "c4": dict(d=2.6, cfg=um("roleta", "e")),
    "c5": dict(d=2.6, cfg=um("pontos", "d")),
    "c6": dict(d=2.6, cfg=um("carrinho", "e")),
    "c7": dict(d=2.6, cfg=um("artes", "d")),
    "c8": dict(d=3.2, cfg={**um("economia", "d"), "phones": [phone("economia", [0, -0.65, 0], [0.1, 0.2, 0], 0.9)]}),
}

TEXTOS = {
    "c1": (None, "SEU DELIVERY<br>VENDENDO<br><span>SOZINHO</span>", "Sem comissão por pedido"),
    "c2": ("R$", "R$ 20 mil no app =<br><span>R$ 4.600</span><br>de comissão", "Todo mês.<small>Exemplo com comissão de 23%</small>"),
    "c3": ("01", "Cardápio digital<br><span>com a sua marca</span>", "O cliente pede pelo seu link"),
    "c4": ("02", "Roleta de<br><span>desconto</span>", "O cupom já entra no pedido"),
    "c5": ("03", "Pontos de<br><span>fidelidade</span>", "Cada pedido vira ponto"),
    "c6": ("04", "Carrinho<br><span>abandonado</span>", "30 min depois, chama de volta"),
    "c7": ("05", "Artes prontas<br><span>pra postar</span>", "Com o seu cardápio e o seu link"),
    "c8": (None, "Quer ver no seu<br>restaurante?", "Comenta <b>DEMO</b>"),
}

BG = """*{margin:0;padding:0;box-sizing:border-box}body{width:1080px;height:1920px;overflow:hidden;position:relative;
font-family:Poppins,Inter,sans-serif;color:#fff;background:transparent}
.fundo{position:absolute;inset:0;background:radial-gradient(900px 800px at 85% 5%,#1f6bf0 0,rgba(31,107,240,0) 70%),
 radial-gradient(800px 700px at 0% 100%,#0b2c80 0,rgba(11,44,128,0) 70%),linear-gradient(165deg,#0A3D9E,#041d55)}
.grade{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),
 linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);background-size:60px 60px;
 mask-image:linear-gradient(180deg,transparent,#000 30%,#000 75%,transparent)}
.brilho{position:absolute;border-radius:50%;filter:blur(100px);opacity:.5}
.num{position:absolute;right:60px;top:430px;font-size:380px;font-weight:900;line-height:1;color:transparent;
 -webkit-text-stroke:3px rgba(141,198,63,.33)}
.selo{position:absolute;top:240px;left:50%;transform:translateX(-50%);width:170px;height:170px;padding:15px;background:#fff;
 border-radius:36px;box-shadow:0 16px 44px rgba(0,0,0,.35)} .selo img{width:140px;display:block}
.txt{position:absolute;left:80px;right:80px;top:460px;text-align:center;text-shadow:0 6px 26px rgba(0,0,0,.4)}
h1{font-size:104px;line-height:1.02;font-weight:900;letter-spacing:-1px} h1 span{color:#8DC63F}
p{font-size:52px;font-weight:600;margin-top:28px} p b{color:#8DC63F}
small{display:block;font-size:28px;opacity:.65;font-weight:500;margin-top:12px}
.chip{display:inline-block;margin-top:30px;background:#F7941D;font-weight:800;font-size:54px;padding:26px 60px;border-radius:70px;
 box-shadow:0 14px 34px rgba(247,148,29,.5)}
.rodape{position:absolute;left:0;right:0;bottom:0;height:330px;background:linear-gradient(180deg,rgba(4,22,66,0),rgba(4,22,66,.9) 70%)}
"""


def fundo_html(nome):
    num = TEXTOS[nome][0]
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BG}</style></head><body><div class="fundo"></div>'
            '<div class="grade"></div><div class="brilho" style="width:560px;height:560px;background:#8DC63F;left:-200px;top:1250px"></div>'
            '<div class="brilho" style="width:460px;height:460px;background:#F7941D;right:-160px;top:760px;opacity:.33"></div>'
            + (f'<div class="num">{num}</div>' if num else '') + '</body></html>')


def frente_html(nome):
    _, t, d = TEXTOS[nome]
    chip = '<div class="chip">COMENTA DEMO</div>' if nome == "c8" else ""
    p = "" if nome == "c8" else f"<p>{d}</p>"
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{BG}</style></head><body>'
            '<div class="rodape"></div>'
            f'<div class="selo"><img src="{LOGO}"></div><div class="txt"><h1>{t}</h1>{p}{chip}</div></body></html>')


async def camadas():
    os.makedirs(os.path.join(HERE, "reel"), exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": W, "height": H})
        for n in CENAS:
            await pg.set_content(fundo_html(n)); await pg.wait_for_timeout(150)
            await pg.screenshot(path=os.path.join(HERE, "reel", f"{n}_fundo.png"))
            await pg.set_content(frente_html(n)); await pg.wait_for_timeout(150)
            await pg.screenshot(path=os.path.join(HERE, "reel", f"{n}_frente.png"), omit_background=True)
        await b.close()


def montar():
    clips = []
    for n, c in CENAS.items():
        out = os.path.join(HERE, "reel", f"{n}.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                        "-framerate", str(FPS), "-i", f"reel3d/{n}/f%04d.jpg",
                        "-loop", "1", "-t", str(c["d"]), "-i", f"reel/{n}_frente.png",
                        "-filter_complex",
                        "[1:v]format=rgba,fade=in:st=0.15:d=0.35:alpha=1[t];"
                        "[0:v]scale=1080:1920:flags=lanczos[b];[b][t]overlay=0:0:shortest=1,format=yuv420p[v]",
                        "-map", "[v]", "-r", str(FPS), "-t", str(c["d"]), "-c:v", "libx264", "-preset", "veryfast",
                        "-crf", "18", out], cwd=HERE, check=True)
        clips.append((out, c["d"]))
    fade = 0.35
    args, filt, prev, off = [], [], "0:v", 0.0
    for p_, _ in clips:
        args += ["-i", p_]
    for i in range(1, len(clips)):
        off += clips[i - 1][1] - fade
        filt.append(f"[{prev}][{i}:v]xfade=transition=slideleft:duration={fade}:offset={off:.2f}[x{i}]")
        prev = f"x{i}"
    total = sum(d for _, d in clips) - fade * (len(clips) - 1)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + args +
                   ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", ";".join(filt), "-map", f"[{prev}]", "-map", f"{len(clips)}:a",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-shortest", "-movflags", "+faststart", "reel-3d.mp4"], cwd=HERE, check=True)


if __name__ == "__main__":
    etapa = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if etapa in ("camadas", "tudo"):
        asyncio.run(camadas())
    if etapa in ("3d", "tudo"):
        cfgs = {n: {**c["cfg"], "frames": int(c["d"] * FPS), "fundo": f"reel/{n}_fundo.png"} for n, c in CENAS.items()}
        json.dump(cfgs, open(os.path.join(HERE, "cenas_reel.json"), "w"))
        subprocess.run(["node", "render3d.js", "cenas_reel.json", "reel3d", "1", str(FPS)], cwd=HERE, check=True)
    if etapa in ("montar", "tudo"):
        montar()
