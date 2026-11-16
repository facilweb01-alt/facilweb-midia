"""Reel 2 · "Sexta, 20h: 19 conversas" (pedido picado x cardápio + atendente virtual). 22 s."""
from comum import foto, kb, jan, final
DUR = 22.0
CHAT1 = '''<div class="chat" id="c2c" data-rot="-2" style="left:110px;top:760px;width:860px;opacity:0"><div class="top">WhatsApp<span>19 não lidas</span></div>
<div class="bl" id="b1" style="opacity:0">moço, cadê meu pedido??<small>20:12</small></div><div class="bl" id="b2" style="opacity:0">🎤 áudio 0:40<small>20:13</small></div>
<div class="bl" id="b3" style="opacity:0">o endereço é aquele de sempre<small>20:14</small></div><div class="bl" id="b4" style="opacity:0">troco pra 100<small>20:14</small></div></div>'''
CHAT2 = '''<div class="chat" id="c4c" data-rot="2" style="left:130px;top:860px;width:820px;opacity:0"><div class="top">Seu restaurante<span>online</span></div>
<div class="bl" id="r1" style="opacity:0">tá aberto?<small>20:15</small></div><div class="bl robo" id="r2" style="opacity:0">Tá sim! Faz seu pedido por aqui: link do seu cardápio<small>20:15</small></div></div>'''
CENAS = [
 dict(id="c1", a=0, b=3.4, musica="B", html=foto("cozinha.jpg") + '''
<div class="h" id="c1t" style="top:430px;font-size:118px;opacity:0">Sexta,<br><span class="l">20h</span>.</div>
<div class="h" id="c1u" style="top:800px;font-size:84px;opacity:0">19 conversas<br>no WhatsApp.</div>''',
  js=kb("cozinha.jpg") + "entra('c1t',t,0.05);entra('c1u',t,0.8);"),
 dict(id="c2", a=3.4, b=7.4, html='<div class="claro"></div><div class="h escuro-txt" id="c2t" style="top:400px;font-size:92px;opacity:0">Pedido picado<br>é o que <span class="l">dá erro</span></div>' + CHAT1,
  js="entra('c2t',t,0.05);entra('c2c',t,0.3,0.5,100);['b1','b2','b3','b4'].forEach((b,i)=>entra(b,t,0.7+i*0.55,0.35,40,true));"),
 dict(id="c3", a=7.4, b=11.4, html=foto("celular.jpg", "claro") + '''
<div class="h" id="c3t" style="top:400px;font-size:96px;opacity:0">O cliente<br>monta <span class="v">sozinho</span></div>''' + jan("c3j", "sis_cardapio.jpg", 80, 900, 920, 520, -2, "Cardápio digital · tela real"),
  js=kb("celular.jpg") + "entra('c3t',t,0.05);entra('c3j',t,0.6,0.6,140);"),
 dict(id="c4", a=11.4, b=15.4, html='<div class="claro"></div><div class="h escuro-txt" id="c4t" style="top:400px;font-size:90px;opacity:0">O atendente<br>virtual <span class="v">responde</span></div>' + CHAT2,
  js="entra('c4t',t,0.05);entra('c4c',t,0.3,0.5,100);entra('r1',t,0.8,0.35,40,true);entra('r2',t,1.6,0.4,40,true);"),
 dict(id="c5", a=15.4, b=19.0, html='<div class="claro"></div><div class="h escuro-txt" id="c5t" style="top:400px;font-size:90px;opacity:0">Chega completo<br>no <span class="v">seu painel</span></div>' + jan("c5j", "sis_painel.jpg", 60, 860, 960, 560, 2, "Painel Fácil Web · tela real"),
  js="entra('c5t',t,0.05);entra('c5j',t,0.5,0.6,140);"),
 final("c6", 19.0, 22.0, 'Sexta sem<br><span class="v">caçar pedido</span>', "Cardápio digital + atendente virtual no WhatsApp"),
]
LEGENDAS = [
 (0.2, 3.3, "Sexta, 20h: <b>19 conversas</b> no WhatsApp da loja."),
 (3.5, 7.3, "Sabor num áudio, endereço noutra mensagem, troco em outra."),
 (7.5, 11.3, "Com o cardápio digital, o cliente <b>monta o pedido sozinho</b>."),
 (11.5, 15.3, "Chamou no WhatsApp? O <b>atendente virtual</b> responde na hora."),
 (15.5, 18.9, "O pedido chega completo no painel e sai impresso na cozinha."),
]
