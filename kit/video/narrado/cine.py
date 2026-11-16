"""Reel narrado (motor do Nutriforma, 11/2026): b-roll + celular 3D com telas reais + legenda palavra a palavra.

Uso (na pasta de trabalho do cliente):  python3 kit/video/narrado/cine.py r1/reel.json [--previa]
Pasta de trabalho:  broll/raw/<clip>.mp4 (vídeos de banco)  ·  estados/<tela>.png (prints do app, 1080 de largura)
                    marca/logo.png  ·  r1/voz.ssml → voz.py → r1/voz.json + r1/voz.wav
reel.json: {"nome", "voz", "wav", "musica": "A"|"B", "marca": {...}, "cenas": [...], "fim": {...}, "chaves": [...], "flashPal": [...]}
Cada cena vale do bookmark s<i> da narração até o próximo. Tipos: broll (clip, ini, zoom, cx), phone (tela, y0, y1, cam, cards), marca, fim.
RETOMAR=1 continua um render interrompido do último quadro salvo.
"""
import json, os, sys, subprocess, asyncio, signal, time

KIT = os.path.dirname(os.path.abspath(__file__))
BASE = os.environ.get("CINE_BASE") or os.getcwd()
FPS = 30
PORTA = int(os.environ.get("CINE_PORTA", "8811"))
os.chdir(BASE)


def sh(*a):
    subprocess.run(a, check=True)


def prepara():
    """Liga o motor (html, three.js e fontes do kit) dentro da pasta de trabalho, que é servida por http."""
    for nome, alvo in (("cine.html", f"{KIT}/cine.html"), ("three", f"{KIT}/node_modules/three"), ("fontes", f"{KIT}/node_modules/@fontsource-variable")):
        if not os.path.exists(alvo):
            sys.exit(f"falta {alvo}: rode bash kit/instalar.sh")
        if os.path.islink(nome) or not os.path.exists(nome):
            if os.path.islink(nome): os.remove(nome)
            os.symlink(alvo, nome)


def extrai(c, dur):
    pasta = f"broll/frames/{c['clip']}-{c['ini']}-{c.get('cx', 0.5)}"
    n = int(dur * FPS) + 8
    if os.path.isdir(pasta) and len(os.listdir(pasta)) >= n:
        return pasta, n
    os.makedirs(pasta, exist_ok=True)
    # gradação única para todo b-roll (une vídeos de bancos diferentes): contraste, saturação, sombras frias, vinheta
    grade = (f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920:(iw-1080)*{c.get('cx', 0.5)}:(ih-1920)/2,fps=30,"
             "eq=contrast=1.07:saturation=1.12:gamma=0.98,"
             "colorbalance=rs=-0.03:bs=0.04:rh=0.04:bh=-0.03,vignette=PI/5")
    sh("ffmpeg", "-v", "error", "-y", "-ss", str(c["ini"]), "-i", f"broll/raw/{c['clip']}.mp4", "-t", str(n / FPS + 0.1),
       "-vf", grade, "-q:v", "3", f"{pasta}/%04d.jpg")
    return pasta, len(os.listdir(pasta))


def monta(cfg, pasta):
    V = json.load(open(cfg["voz"]))
    m = {x["nome"]: x["t"] for x in V["marcas"]}
    total = V["dur"] + cfg.get("cauda", 1.6)
    cenas = []
    for i, c in enumerate(cfg["cenas"]):
        a = m[f"s{i+1}"] if i else 0.0
        b = m.get(f"s{i+2}", total)
        c = dict(c, a=a, b=b)
        if c["tipo"] == "broll":
            pf, n = extrai(c, b - a + 0.3)
            c["clip"] = os.path.basename(pf); c["n"] = n
        cenas.append(c)
    fim = dict(cfg["fim"], a=cenas[-1]["a"] if cenas[-1]["tipo"] == "fim" else total)
    tl = {"palavras": V["palavras"], "cenas": cenas, "total": total, "fim": fim, "chaves": cfg.get("chaves", []),
          "maxpal": cfg.get("maxpal", 4), "flashPal": cfg.get("flashPal", []), "marca": cfg.get("marca", {})}
    json.dump(tl, open(f"{pasta}/tl.json", "w"), ensure_ascii=False)
    return tl


async def render(pasta, tl, previa):
    from playwright.async_api import async_playwright
    srv = subprocess.Popen(["python3", "-m", "http.server", str(PORTA), "--bind", "127.0.0.1"], cwd=BASE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    try:
        async with async_playwright() as p:
            b = await p.chromium.launch(args=["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
            pg = await b.new_page(viewport={"width": 1080, "height": 1920})
            pg.on("console", lambda m: print("console:", m.text) if m.type in ("error", "warning") else None)
            pg.on("pageerror", lambda e: print("pageerror:", e))
            await pg.goto(f"http://127.0.0.1:{PORTA}/cine.html?tl=/{pasta}/tl.json")
            await pg.wait_for_function("window.pronto === true", timeout=60000)
            await pg.evaluate("document.fonts.ready")
            q = f"{pasta}/quadros"; os.makedirs(q, exist_ok=True)
            if previa:
                ts = []
                for c in tl["cenas"]:
                    ts += [c["a"] + 0.12, (c["a"] + c["b"]) / 2, c["b"] - 0.1]
                ts += [tl["fim"]["a"] + 1.2, tl["total"] - 0.05]
            else:
                ts = [f / FPS for f in range(int(tl["total"] * FPS))]
            ja = len(os.listdir(q)) if os.environ.get("RETOMAR") else 0
            for k, t in enumerate(ts):
                if k < ja - 1: continue
                await pg.evaluate(f"seek({t})")
                await pg.screenshot(path=f"{q}/{k+1:05d}.jpg", type="jpeg", quality=92)
                if k % 90 == 0: print("quadro", k, len(ts), flush=True)
            await b.close()
    finally:
        srv.send_signal(signal.SIGTERM); srv.wait()
    return len(ts)


def audio(cfg, pasta, total):
    mus = f"{pasta}/musica.wav"
    sh("python3", f"{KIT}/../musica.py", cfg.get("musica", "A"), mus, str(int(total) + 2))
    # voz na frente, música com ducking sob a voz, fade-out no final, -14 LUFS
    fc = (f"[0:a]aresample=48000,apad,atrim=0:{total},volume=1.0,asplit[v][v2];"
          f"[1:a]aresample=48000,atrim=0:{total},volume={cfg.get('vol_musica', 0.33)},afade=t=out:st={total-1.6}:d=1.6[m];"
          f"[m][v]sidechaincompress=threshold=0.04:ratio=6:attack=20:release=350[md];"
          f"[v2][md]amix=inputs=2:duration=longest:normalize=0,loudnorm=I=-14:TP=-1.2:LRA=9[o]")
    sh("ffmpeg", "-v", "error", "-y", "-i", cfg["wav"], "-i", mus, "-filter_complex", fc,
       "-map", "[o]", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", f"{pasta}/audio.m4a")


def main():
    cfgf = sys.argv[1]; previa = "--previa" in sys.argv
    cfg = json.load(open(cfgf)); pasta = os.path.dirname(cfgf)
    prepara()
    tl = monta(cfg, pasta)
    q = f"{pasta}/quadros"
    if os.path.isdir(q) and not os.environ.get("RETOMAR"): subprocess.run(["rm", "-rf", q])
    asyncio.run(render(pasta, tl, previa))
    if previa:
        sh("ffmpeg", "-v", "error", "-y", "-i", f"{q}/%05d.jpg", "-vf", "scale=270:480,tile=8x4:padding=6", "-frames:v", "1", f"{pasta}/previa.jpg")
        print("previa", f"{pasta}/previa.jpg"); return
    audio(cfg, pasta, tl["total"])
    out = f"{pasta}/{cfg.get('nome', 'reel')}.mp4"
    sh("ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", f"{q}/%05d.jpg", "-i", f"{pasta}/audio.m4a",
       "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", "-movflags", "+faststart", out)
    print("ok", out)


main()
