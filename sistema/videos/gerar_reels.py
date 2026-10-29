"""Reels animados do @facilweb (sem telas reais do sistema, só texto, formas e a logo).

Uso:  python3 gerar_reels.py [nome ...]      -> saida/<nome>.mp4 e saida/<nome>-capa.jpg
Identidade igual a ../gerar_artes_modelo.py: azul #0A3D9E, verde #8DC63F,
laranja #F7941D, Poppins, logo no selo branco em todos os quadros.
Área segura de Reel: texto entre y=420 e y=1450 (topo e rodapé ficam sob a interface).
"""
import asyncio, base64, os, subprocess, sys
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
LOGO = base64.b64encode(open(os.path.join(HERE, "..", "logo.png"), "rb").read()).decode()
AZUL, AZUL2, VERDE, LARANJA = "#0A3D9E", "#062a73", "#8DC63F", "#F7941D"
FPS = 30

CSS = f"""
*{{margin:0;padding:0;box-sizing:border-box}}
body{{width:1080px;height:1920px;overflow:hidden;font-family:Poppins,sans-serif;color:#fff;position:relative;
 background:{AZUL2}}}
.bg{{position:absolute;inset:-200px;background:radial-gradient(circle at 80% 15%,#1758d6 0,{AZUL} 38%,{AZUL2} 100%);
 animation:drift 12s ease-in-out infinite alternate}}
@keyframes drift{{from{{transform:translate(0,0) scale(1)}}to{{transform:translate(-60px,80px) scale(1.08)}}}}
.selo{{position:absolute;top:250px;left:50%;margin-left:-105px;width:210px;height:210px;background:#fff;border-radius:30px;
 display:flex;align-items:center;justify-content:center;box-shadow:0 12px 34px rgba(0,0,0,.3);z-index:5}}
.selo img{{width:170px}}
.cena{{position:absolute;left:100px;right:100px;top:560px;height:880px;display:flex;flex-direction:column;
 justify-content:center;align-items:center;text-align:center;opacity:0}}
h1{{font-weight:800;font-size:112px;line-height:1.04}} h2{{font-weight:800;font-size:84px;line-height:1.1}}
h1 span,h2 span,p span{{color:{VERDE}}}
p{{font-weight:500;font-size:56px;line-height:1.3;margin-top:36px}}
.barra{{width:160px;height:14px;border-radius:7px;background:{VERDE};margin-bottom:56px;transform-origin:left}}
.botao{{margin-top:70px;background:{LARANJA};font-weight:800;font-size:64px;padding:34px 80px;border-radius:80px}}
.handle{{position:absolute;bottom:430px;left:0;right:0;text-align:center;font-size:36px;opacity:.75;z-index:5}}
.prog{{position:absolute;top:500px;left:50%;transform:translateX(-50%);display:flex;gap:14px;z-index:5}}
.prog i{{width:46px;height:8px;border-radius:4px;background:rgba(255,255,255,.25);overflow:hidden;display:block}}
.prog i b{{display:block;height:100%;width:100%;background:{VERDE};transform:scaleX(0);transform-origin:left}}
/* elementos visuais genéricos (ilustração, não é tela do sistema) */
.pct{{font-size:260px;font-weight:800;position:relative;line-height:1;margin-bottom:30px}}
.pct:after{{content:"";position:absolute;left:-30px;right:-30px;top:50%;height:22px;background:{LARANJA};border-radius:11px;
 transform:rotate(-18deg) scaleX(var(--s,0))}}
.balao{{background:#fff;color:{AZUL};font-weight:600;font-size:44px;padding:22px 34px;border-radius:34px 34px 34px 8px;
 margin:10px 0;align-self:flex-start;opacity:0}}
.balao.d{{align-self:flex-end;background:{VERDE};color:#fff;border-radius:34px 34px 8px 34px}}
.cupom{{width:520px;background:#fff;color:#333;border-radius:10px 10px 0 0;padding:40px 44px;text-align:left;
 font-size:40px;font-weight:600;line-height:1.6;clip-path:inset(0 0 100% 0);margin-bottom:40px}}
.cupom hr{{border:0;border-top:4px dashed #bbb;margin:16px 0}}
.mesas{{display:grid;grid-template-columns:repeat(3,200px);gap:28px;margin-bottom:50px}}
.mesas div{{height:150px;border-radius:26px;background:rgba(255,255,255,.12);border:4px solid rgba(255,255,255,.35);
 display:flex;align-items:center;justify-content:center;font-size:52px;font-weight:800}}
.mesas div.on{{background:{VERDE};border-color:{VERDE}}}
"""

# cada cena: (duração em s, html)
REELS = {
"zero-comissao": [
 (2.6, '<div class="pct" style="--s:1">%</div><h1>TODO PEDIDO DO APP PAGA <span>COMISSÃO</span></h1>'),
 (2.6, '<h2>Até o pedido do cliente que <span>já te conhece</span></h2>'),
 (3.0, '<div class="barra"></div><h2>No seu delivery próprio</h2><p>o pedido é <span>100% seu</span></p>'),
 (3.0, '<h2>E o cliente fica no <span>seu cadastro</span></h2><p>não no do app</p>'),
 (3.0, '<h2>Cardápio digital + pedido pelo <span>WhatsApp</span></h2><p>Zero comissão</p>'),
 (4.0, '<h2>Quer ver funcionando?</h2><div class="botao">COMENTA DEMO</div>'),
],
"cardapio-digital": [
 (2.6, '<h1>AINDA ANOTA PEDIDO <span>MENSAGEM POR MENSAGEM</span>?</h1>'),
 (3.4, '<div style="width:100%;display:flex;flex-direction:column">'
       '<div class="balao">Boa noite, quero uma pizza</div><div class="balao d">Qual sabor?</div>'
       '<div class="balao">Meia calabresa, meia frango</div><div class="balao d">Tamanho?</div></div>'
       '<p>Cada pedido vira uma conversa</p>'),
 (3.0, '<div class="barra"></div><h2>Com cardápio digital o cliente <span>monta o pedido sozinho</span></h2>'),
 (3.0, '<h2>Escolhe, confirma, e o pedido chega <span>pronto</span></h2><p>Sem copiar mensagem</p>'),
 (4.0, '<h2>Quer ver funcionando?</h2><div class="botao">COMENTA DEMO</div>'),
],
"pedido-na-cozinha": [
 (2.6, '<h1>O PEDIDO <span>SE PERDEU</span> NO CAMINHO PRA COZINHA?</h1>'),
 (2.8, '<h2>Papel na mão, grito no balcão</h2><p>e o pedido sai <span>errado</span></p>'),
 (3.6, '<div class="cupom">PEDIDO<hr>1x Pizza grande<br>1x Refrigerante<hr>Entrega</div>'
       '<h2>O pedido <span>sai impresso</span> na cozinha</h2>'),
 (3.0, '<div class="barra"></div><h2>Impressão <span>automática</span> de pedidos</h2><p>no sistema da Fácil Web</p>'),
 (4.0, '<h2>Quer ver funcionando?</h2><div class="botao">COMENTA DEMO</div>'),
],
"mesas-e-pdv": [
 (2.6, '<h1>CONTA DA MESA <span>NA CALCULADORA</span>?</h1>'),
 (2.8, '<h2>Comanda de papel some</h2><p>e a conta <span>soma errado</span></p>'),
 (3.6, '<div class="mesas"><div class="on">1</div><div>2</div><div class="on">3</div>'
       '<div>4</div><div class="on">5</div><div>6</div></div>'
       '<h2>Cada mesa aberta na tela, com a <span>conta pronta</span></h2>'),
 (3.0, '<div class="barra"></div><h2>No fim da noite</h2><p><span>PDV e relatório do dia</span> prontos</p>'),
 (4.0, '<h2>Quer ver funcionando?</h2><div class="botao">COMENTA DEMO</div>'),
],
}

FADE = 0.35


def page(cenas):
    total = sum(d for d, _ in cenas)
    kf, html, t = [], [], 0.0
    for i, (d, inner) in enumerate(cenas):
        a, b = t / total * 100, (t + d) / total * 100
        fi, fo = (t + FADE) / total * 100, (t + d - FADE) / total * 100
        last = i == len(cenas) - 1
        kf.append(f"@keyframes c{i}{{0%{{opacity:0;transform:translateY(60px)}}{a:.3f}%{{opacity:0;transform:translateY(60px)}}"
                  f"{fi:.3f}%{{opacity:1;transform:none}}{(100 if last else fo):.3f}%{{opacity:1;transform:none}}"
                  + ("" if last else f"{b:.3f}%{{opacity:0;transform:translateY(-40px)}}100%{{opacity:0}}") + "}")
        # sub-elementos entram em sequência dentro da cena
        kf.append(f"@keyframes s{i}{{0%,{(t+0.3)/total*100:.3f}%{{opacity:0;transform:translateY(30px)}}"
                  f"{(t+0.7)/total*100:.3f}%,100%{{opacity:1;transform:none}}}}")
        kf.append(f"@keyframes p{i}{{0%,{a:.3f}%{{transform:scaleX(0)}}{b:.3f}%,100%{{transform:scaleX(1)}}}}")
        html.append(f'<div class="cena" style="animation:c{i} {total}s linear forwards" data-i="{i}" data-t="{t}">{inner}</div>')
        t += d
    prog = "".join(f'<i><b style="animation:p{i} {total}s linear forwards"></b></i>' for i in range(len(cenas)))
    js = """<script>
document.querySelectorAll('.cena').forEach(c=>{const t=+c.dataset.t,T=%s;let k=0;
 c.querySelectorAll('.balao').forEach(b=>{const s=(t+0.3+k*0.6)/T*100,e=(t+0.6+k*0.6)/T*100;k++;
  b.animate([{opacity:0,transform:'translateY(30px)',offset:0},{opacity:0,transform:'translateY(30px)',offset:s/100},
   {opacity:1,transform:'none',offset:e/100},{opacity:1,transform:'none',offset:1}],{duration:T*1000,fill:'forwards'})});
 c.querySelectorAll('.cupom').forEach(b=>b.animate([{clipPath:'inset(0 0 100%% 0)',offset:0},
   {clipPath:'inset(0 0 100%% 0)',offset:(t+0.2)/T},{clipPath:'inset(0 0 0 0)',offset:(t+1.6)/T},{clipPath:'inset(0 0 0 0)',offset:1}],
   {duration:T*1000,fill:'forwards'}));
 c.querySelectorAll('.barra').forEach(b=>b.animate([{transform:'scaleX(0)',offset:0},{transform:'scaleX(0)',offset:(t+0.2)/T},
   {transform:'scaleX(1)',offset:(t+0.8)/T},{transform:'scaleX(1)',offset:1}],{duration:T*1000,fill:'forwards'}));
 c.querySelectorAll('.botao').forEach(b=>b.animate([{transform:'scale(1)',offset:0},{transform:'scale(1)',offset:(t+0.8)/T},
   {transform:'scale(1.08)',offset:(t+1.2)/T},{transform:'scale(1)',offset:(t+1.6)/T},{transform:'scale(1.08)',offset:(t+2.4)/T},
   {transform:'scale(1)',offset:Math.min(1,(t+2.8)/T)},{transform:'scale(1)',offset:1}],{duration:T*1000,fill:'forwards'}));
});
document.getAnimations().forEach(a=>a.pause());
window.seek=s=>document.getAnimations().forEach(a=>a.currentTime=s*1000);
</script>""" % total
    return (f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}{"".join(kf)}</style></head><body>'
            f'<div class="bg"></div><div class="selo"><img src="data:image/png;base64,{LOGO}"></div>'
            f'<div class="prog">{prog}</div>{"".join(html)}<div class="handle">@facilweb</div>{js}</body></html>'), total


async def render(nome, cenas, pg):
    out = os.path.join(HERE, "saida"); os.makedirs(out, exist_ok=True)
    html, total = page(cenas)
    await pg.set_content(html)
    await pg.wait_for_timeout(400)
    n = int(total * FPS)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "mjpeg", "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                           "-shortest", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-profile:v", "high", "-r", str(FPS), "-c:a", "aac", "-b:a", "128k",
                           "-movflags", "+faststart", os.path.join(out, f"{nome}.mp4")], stdin=subprocess.PIPE)
    for f in range(n):
        await pg.evaluate(f"seek({f / FPS})")
        ff.stdin.write(await pg.screenshot(type="jpeg", quality=90))
    ff.stdin.close(); ff.wait()
    await pg.evaluate("seek(1.6)")
    await pg.screenshot(path=os.path.join(out, f"{nome}-capa.jpg"), type="jpeg", quality=92)


async def main(nomes):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        for nome in nomes:
            await render(nome, REELS[nome], pg)
            print("ok", nome)
        await b.close()

asyncio.run(main(sys.argv[1:] or list(REELS)))
