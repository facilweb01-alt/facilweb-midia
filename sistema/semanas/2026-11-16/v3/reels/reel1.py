"""Reel 1 · "Vendeu R$ 20 mil no app?" (Black Friday, conta da comissão). 22 s."""
from comum import foto, kb, jan, final
DUR = 22.0
CENAS = [
 dict(id="c1", a=0, b=3.6, musica="A", html=foto("dono.jpg") + '''
<div class="h" id="c1t" style="top:420px;font-size:112px;opacity:0">Vendeu<br><span class="v">R$ 20 mil</span><br>no app?</div>
<div class="num" id="c1n" style="left:70px;top:900px;font-size:200px;opacity:0">R$ <span id="c1v">0</span></div>''',
  js=kb("dono.jpg") + "entra('c1t',t,0.05);var e=document.getElementById('c1n');e.style.opacity=t>1.2?1:0;document.getElementById('c1v').textContent=Math.round(5400*Math.min(Math.max((t-1.2)/1.2,0),1)).toLocaleString('pt-BR');"),
 dict(id="c2", a=3.6, b=7.4, html='''<div class="claro"></div>
<div class="h escuro-txt" id="c2t" style="top:400px;font-size:92px;opacity:0">Em 12 meses:<br><span class="l">R$ 64.800</span></div>
<div class="cupom" id="c2c" data-rot="-3" style="left:150px;top:820px;width:780px;opacity:0"><div class="cab">SEU MÊS NO APP</div><div class="sub">exemplo · comissão de 27%</div><hr>
<div class="ln"><span>Vendas</span><span>R$ 20.000</span></div><div class="ln neg"><span>Comissão 27%</span><span>- R$ 5.400</span></div><hr><div class="ln tot neg"><span>Ficou no app</span><span>R$ 5.400</span></div></div>''',
  js="entra('c2t',t,0.05);var c=document.getElementById('c2c');var k=Math.min(Math.max((t-0.4)/0.9,0),1);c.style.opacity=k>0?1:0;c.style.clipPath='inset(0 0 '+(100-100*k)+'% 0)';c.style.transform='rotate(-3deg) translateY('+(-(1-k)*120)+'px)';"),
 dict(id="c3", a=7.4, b=11.2, html=foto("pizza.jpg") + '''
<div class="h" id="c3t" style="top:430px;font-size:100px;opacity:0">Black Friday<br>no app:</div>
<div class="h" id="c3u" style="top:760px;font-size:84px;opacity:0">o desconto é seu.<br>A comissão <span class="l">também</span>.</div>''',
  js=kb("pizza.jpg") + "entra('c3t',t,0.05);entra('c3u',t,0.9);"),
 dict(id="c4", a=11.2, b=15.2, html='<div class="claro"></div>' + '''
<div class="h escuro-txt" id="c4t" style="top:390px;font-size:88px;opacity:0">No seu cardápio,<br>a promoção é <span class="v">sua</span></div>''' + jan("c4j", "sis_roleta.jpg", 60, 820, 960, 600, -2, pos="center 30%"),
  js="entra('c4t',t,0.05);entra('c4j',t,0.5,0.6,140);var j=document.getElementById('c4j');if(t>0.5)j.style.transform='rotate(-2deg) scale('+(1+0.06*Math.min((t-1.1)/2.5,1)*(t>1.1))+')';"),
 dict(id="c5", a=15.2, b=19.0, html=foto("cliente.jpg", "claro") + '''
<div class="h" id="c5t" style="top:400px;font-size:92px;opacity:0">O pedido chega<br>no WhatsApp.<br><span class="v">Comissão zero.</span></div>''' + jan("c5j", "sis_cardapio.jpg", 120, 1000, 840, 470, 3, "Cardápio digital · tela real"),
  js=kb("cliente.jpg") + "entra('c5t',t,0.05);entra('c5j',t,0.8,0.6,140);"),
 final("c6", 19.0, 22.0, 'Seu delivery,<br><span class="v">seu lucro</span>', "Cardápio digital sem comissão por pedido"),
]
LEGENDAS = [
 (0.2, 3.5, "Vendeu <b>R$ 20 mil</b> no app? <b>R$ 5.400</b> viraram comissão."),
 (3.7, 7.3, "Num ano, são <b>R$ 64.800</b> que ficam no aplicativo."),
 (7.5, 11.1, "Na Black Friday, o desconto sai da sua margem e a taxa continua."),
 (11.3, 15.1, "No seu cardápio digital, a roleta de cupons roda <b>sem taxa</b>."),
 (15.3, 18.9, "O pedido chega completo no WhatsApp. <b>Comissão zero.</b>"),
]
