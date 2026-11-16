from motor_reel import P, F, LOGO

def foto(nome, alt="azul"):
    u = P(nome)
    if not u:
        return f'<div class="{alt}"></div>'
    return f'<div class="fundo" id="kb_{nome.split(".")[0]}" style="background-image:url({u})"></div><div class="escurece"></div>'

def kb(nome, zoom=0.12):
    i = "kb_" + nome.split(".")[0]
    return f"var k=document.getElementById('{i}');if(k)k.style.transform='scale('+(1+{zoom}*t/d)+')';"

def jan(id_, img, x, y, w, h, rot=0, titulo="Sistema Fácil Web · tela real", pos="left top"):
    return f'<div class="jan" id="{id_}" data-rot="{rot}" style="left:{x}px;top:{y}px;width:{w}px;opacity:0"><div class="bar"><i></i><i></i><i></i><span>{titulo}</span></div><img src="{F(img)}" style="height:{h}px;object-position:{pos}"></div>'

def final(id_, a, b, linha1, linha2):
    html = f'''<div class="azul"></div>
<div id="{id_}_logo" style="position:absolute;left:390px;top:640px;width:300px;height:300px;padding:26px;background:#fff;border-radius:70px;box-shadow:0 30px 80px rgba(0,0,0,.35);opacity:0"><img src="{LOGO}" style="width:248px"></div>
<div class="h" id="{id_}_t" style="top:1020px;text-align:center;font-size:96px;opacity:0">{linha1}</div>
<div id="{id_}_s" style="position:absolute;left:0;right:0;top:1290px;text-align:center;font-size:40px;font-weight:600;opacity:0;color:#cfe0ff">{linha2}</div>
<div id="{id_}_h" style="position:absolute;left:0;right:0;top:1400px;text-align:center;font-size:34px;font-weight:600;opacity:0">@facilweb · facilwebdelivery.com.br</div>'''
    js = f"entra('{id_}_logo',t,0.1,0.55,60,true);entra('{id_}_t',t,0.6);entra('{id_}_s',t,0.9);entra('{id_}_h',t,1.1);"
    return dict(id=id_, a=a, b=b, html=html, js=js)

import os as _os
_FR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "frames")

def video(clip):
    return f'<img id="bv_{clip}" src="file://{_FR}/{clip}/0001.jpg" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover"><div class="escurece"></div>'

def vkb(clip, zoom=0.08):
    return (f"var v=document.getElementById('bv_{clip}');if(v){{var n=Math.min(Math.floor(t*24)+1,120);"
            f"v.src='file://{_FR}/{clip}/'+String(n).padStart(4,'0')+'.jpg';v.style.transform='scale('+(1+{zoom}*t/d)+')';}}")
