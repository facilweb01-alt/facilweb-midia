"""Motor dos reels da semana 16-22/11 (@facilweb): cenas em HTML animadas por tempo, quadro a quadro no Chromium,
legenda na tela e trilha original. Logo no selo branco do começo ao fim; final só com a marca (sem chamada na tela).

Uso: python3 motor_reel.py reel1|reel2 [--previa]
"""
import asyncio, base64, json, os, subprocess, sys, shutil
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
V3 = os.path.dirname(HERE)
SIS = os.path.abspath(os.path.join(V3, "..", "..", ".."))
KIT = os.path.abspath(os.path.join(SIS, "..", "kit"))
FPS = 24


def uri(p):
    ext = p.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg"
    return f"data:{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()


LOGO = uri(os.path.join(SIS, "logo.png"))
F = lambda n: uri(os.path.join(V3, "fotos", n))
P = lambda n: uri(os.path.join(HERE, "pessoas", n)) if os.path.exists(os.path.join(HERE, "pessoas", n)) else ""

CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;position:relative;font-family:Poppins,sans-serif;background:#06235f;color:#fff}
.cena{position:absolute;inset:0;opacity:0;overflow:hidden}
.fundo{position:absolute;inset:-60px;background-size:cover;background-position:center}
.escurece{position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,22,66,.55) 0%,rgba(4,22,66,.15) 35%,rgba(4,22,66,.25) 60%,rgba(4,22,66,.92) 100%)}
.claro{position:absolute;inset:0;background:#F3F6FB}
.claro:after{content:"";position:absolute;inset:0;background-image:radial-gradient(rgba(10,61,158,.10) 2px,transparent 2px);background-size:34px 34px}
.azul{position:absolute;inset:0;background:radial-gradient(900px 800px at 90% 0%,#1f6bf0 0,rgba(31,107,240,0) 70%),linear-gradient(160deg,#0A3D9E,#06235f)}
.selo{position:absolute;top:190px;left:70px;width:120px;height:120px;padding:10px;background:#fff;border-radius:28px;box-shadow:0 12px 30px rgba(0,0,0,.3);z-index:20}
.selo img{width:100px;display:block}
.h{position:absolute;left:70px;right:70px;font-weight:700;letter-spacing:-2px;line-height:1.02;-webkit-text-stroke:1.5px currentColor;text-shadow:0 8px 30px rgba(0,0,0,.35)}
.h .v{color:#8DC63F}.h .l{color:#F7941D}
.escuro-txt{color:#0B1F4D;text-shadow:none}
.leg{position:absolute;left:60px;right:60px;bottom:330px;z-index:30;text-align:center}
.leg span{display:inline;background:#fff;color:#0B1F4D;font-weight:700;font-size:46px;line-height:1.55;padding:6px 18px;border-radius:14px;box-decoration-break:clone;-webkit-box-decoration-break:clone;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.leg span b{color:#0A3D9E;background:linear-gradient(transparent 60%,#8DC63F 60%)}
.barra{position:absolute;left:70px;right:70px;top:150px;height:8px;background:rgba(255,255,255,.25);border-radius:6px;z-index:25;overflow:hidden}
.barra i{display:block;height:100%;background:#8DC63F;border-radius:6px}
.jan{position:absolute;border-radius:26px;overflow:hidden;box-shadow:0 40px 90px rgba(0,0,0,.35);background:#fff;border:2px solid #DCE5F5}
.jan .bar{height:52px;background:#EEF2F9;display:flex;align-items:center;padding:0 20px;gap:10px;border-bottom:2px solid #DCE5F5}
.jan .bar i{width:16px;height:16px;border-radius:50%;background:#F7941D;display:block}.jan .bar i:nth-child(2){background:#8DC63F}.jan .bar i:nth-child(3){background:#0A3D9E}
.jan .bar span{margin-left:14px;font-size:22px;color:#6b7aa0;font-weight:600}
.jan img{display:block;width:100%;object-fit:cover;object-position:left top}
.cupom{position:absolute;background:#fff;color:#1d1d1d;font-family:'DejaVu Sans Mono',monospace;padding:46px 50px 66px;box-shadow:0 30px 70px rgba(0,0,0,.35);
 -webkit-mask:linear-gradient(#000,#000) top/100% calc(100% - 24px) no-repeat,conic-gradient(from -45deg at bottom,#0000,#000 1deg 89deg,#0000 90deg) bottom/40px 24px repeat-x}
.cupom .cab{text-align:center;font-weight:700;font-size:34px;letter-spacing:3px}.cupom .sub{text-align:center;font-size:22px;color:#666;margin-top:4px}
.cupom hr{border:0;border-top:3px dashed #bbb;margin:24px 0}.cupom .ln{display:flex;justify-content:space-between;font-size:36px;margin:14px 0}
.neg{color:#d23b2a;font-weight:700}.pos{color:#2e8b1f;font-weight:700}.tot{font-size:46px;font-weight:700}
.chat{position:absolute;background:#ECE5DD;border-radius:44px;padding:36px 32px;box-shadow:0 30px 80px rgba(0,0,0,.35);overflow:hidden}
.chat .top{margin:-36px -32px 26px;background:#075E54;color:#fff;padding:26px 32px;font-size:32px;font-weight:600;display:flex;justify-content:space-between}
.chat .top span{font-size:24px;background:#25D366;padding:2px 16px;border-radius:20px}
.bl{max-width:84%;font-size:36px;line-height:1.3;padding:18px 26px;border-radius:24px;margin:14px 0;background:#fff;color:#1d1d1d}
.bl small{display:block;font-size:20px;color:#8a8a8a;text-align:right;margin-top:4px}
.bl.eu{margin-left:auto;background:#DCF8C6}.bl.robo{margin-left:auto;background:#DCF8C6;border:3px solid #25D366}
.num{position:absolute;font-weight:700;color:#F7941D;-webkit-text-stroke:3px #F7941D;letter-spacing:-6px;text-shadow:0 10px 40px rgba(0,0,0,.4)}
.flash{position:absolute;inset:0;background:#fff;opacity:0;z-index:40;pointer-events:none}
.tag{position:absolute;background:#F7941D;color:#fff;font-weight:700;font-size:28px;padding:12px 26px;border-radius:40px;box-shadow:0 12px 26px rgba(247,148,29,.45);z-index:22}
"""

JS = """
const ease=t=>t<0?0:t>1?1:1-Math.pow(1-t,3);
const back=t=>{t=Math.min(Math.max(t,0),1);const c=1.70158;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2)};
const clamp=(x,a,b)=>Math.min(Math.max(x,a),b);
function el(id){return document.getElementById(id)}
function entra(id,t,t0,dur=0.45,dy=80,esc=false){const e=el(id);if(!e)return;const k=(t-t0)/dur;const a=back(k);e.style.opacity=clamp(k*2,0,1);
 e.style.transform=(e.dataset.rot?`rotate(${e.dataset.rot}deg) `:'')+`translateY(${(1-a)*dy}px)`+(esc?` scale(${0.6+0.4*a})`:'');}
function render(t){
 const D=window.DUR;document.querySelectorAll('.cena').forEach(c=>{const a=+c.dataset.a,b=+c.dataset.b;const vis=t>=a&&t<b;c.style.opacity=vis?1:0;
   if(vis&&window['C_'+c.id])window['C_'+c.id](t-a,b-a);});
 el('barra').style.width=(100*t/D)+'%';
 document.querySelectorAll('.cena').forEach(c=>{const a=+c.dataset.a;const f=el('flash');});
 const cuts=[...document.querySelectorAll('.cena')].map(c=>+c.dataset.a).filter(x=>x>0);let fl=0;cuts.forEach(x=>{const d=t-x;if(d>=0&&d<0.18)fl=Math.max(fl,0.55*(1-d/0.18))});el('flash').style.opacity=fl;
 document.querySelectorAll('[data-leg]').forEach(l=>{const a=+l.dataset.a,b=+l.dataset.b;const k=(t-a)/0.25;l.style.opacity=(t>=a&&t<b)?clamp(k,0,1):0;l.style.transform=`translateY(${(1-ease(k))*30}px)`});
}
"""


def pagina(cenas, legendas, dur):
    corpo = "".join(f'<div class="cena" id="{c["id"]}" data-a="{c["a"]}" data-b="{c["b"]}">{c["html"]}</div>' for c in cenas)
    legs = "".join(f'<div class="leg" data-leg="1" data-a="{a}" data-b="{b}" style="opacity:0"><span>{txt}</span></div>' for a, b, txt in legendas)
    js = "".join(f'window.C_{c["id"]}=function(t,d){{{c.get("js", "")}}};' for c in cenas)
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{corpo}{legs}
<div class="barra"><i id="barra"></i></div><div class="selo"><img src="{LOGO}"></div><div class="flash" id="flash"></div>
<script>window.DUR={dur};{JS}{js}</script></body></html>"""


async def renderizar(nome, cenas, legendas, dur, previa=False):
    out = os.path.join(HERE, "out", nome)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, "q"), exist_ok=True)
    html = os.path.join(out, "reel.html")
    open(html, "w").write(pagina(cenas, legendas, dur))
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto("file://" + html)
        await pg.wait_for_timeout(500)
        tempos = [c["a"] + (c["b"] - c["a"]) * 0.7 for c in cenas] if previa else [i / FPS for i in range(int(dur * FPS))]
        for i, t in enumerate(tempos):
            await pg.evaluate(f"render({t})")
            await pg.screenshot(path=os.path.join(out, "q", f"{i:05d}.jpg"), type="jpeg", quality=90)
        await b.close()
    if previa:
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", os.path.join(out, "q", "%05d.jpg"), "-vf", "scale=270:-1,tile=6x1", "-frames:v", "1", os.path.join(out, "previa.jpg")], check=True)
        return os.path.join(out, "previa.jpg")
    wav = os.path.join(out, "musica.wav")
    subprocess.run(["python3", os.path.join(KIT, "video", "musica.py"), cenas[0].get("musica", "A"), wav, str(dur)], check=True, capture_output=True)
    mp4 = os.path.join(HERE, f"{nome}.mp4")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-framerate", str(FPS), "-i", os.path.join(out, "q", "%05d.jpg"), "-i", wav,
                    "-af", f"afade=t=out:st={dur - 1.2}:d=1.2,volume=0.8", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "medium",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    capa = os.path.join(HERE, f"{nome}-capa.jpg")
    shutil.copy(os.path.join(out, "q", f"{int(1.6 * FPS):05d}.jpg"), capa)
    return mp4


if __name__ == "__main__":
    nome = sys.argv[1]
    mod = __import__(nome)
    r = asyncio.run(renderizar(nome, mod.CENAS, mod.LEGENDAS, mod.DUR, "--previa" in sys.argv))
    print(r)
