---
name: ig-caption
description: >-
  Escreve a legenda do Instagram em português: a linha que sobrevive ao corte
  do "... mais", o corpo, o pedido único, os termos de busca e até cinco
  hashtags, e revisa antes de sair. Use quando o usuário disser "escreve a
  legenda", "legenda pra esse post", "o que eu coloco na descrição", tiver um
  reel ou carrossel pronto e precisar do texto, ou perguntar sobre hashtags.
---

# ig-caption

Uma ferramenta mora nesta pasta e ela roda:

```bash
python3 caption.py legenda.txt
python3 caption.py legenda.txt --keywords "leilão de imóveis,edital"
```

Ela imprime a legenda do jeito que o feed imprime: os primeiros 125 caracteres
numa caixa, o resto atrás do toque. Leia essa caixa antes de ler qualquer outra
coisa que você escreveu.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
Leia `voice.md` de lá. Se houver vários clientes e não estiver claro qual, pergunte.

## Primeiro, decida qual é o trabalho desta legenda

É a decisão que estraga legenda quando é pulada.

**Trabalho A: o vídeo já fisgou.** Um Reel traz o próprio hook nos dois
primeiros segundos, falado e na tela. A legenda não é um segundo hook, e
competir com o vídeo é como se perde os dois. O trabalho dela é o pedido, o
contexto que faz o pedido fazer sentido, e as palavras que as pessoas buscam.

**Trabalho B: a legenda é o conteúdo.** Foto, imagem única, capa de carrossel
que abre um gancho. Aqui a primeira linha é o hook e funciona igual hook de
Reel: concreta, curta, e cortada num gancho, não no meio de uma oração.

Pergunte qual está escrevendo. Se o usuário tem um Reel com hook forte,
escreva A e diga por quê.

## O formato

```
Linha 1     125 caracteres visíveis. Trabalho A: o pedido, direto.
            Trabalho B: o hook.
            Nunca cumprimento, nunca hashtag, nunca emoji como primeiro caractere.
Corpo       parágrafos curtos, uma linha em branco entre eles. De dois a seis.
            É aqui que moram os termos de busca.
O pedido    um. Comentar uma palavra, salvar, ou chamar no direct. Um.
Hashtags    até cinco, numa linha própria no fim, ou nenhuma.
```

O limite é 2.200 caracteres e quase nada precisa de 2.200. Legenda que ganha o
toque e entrega 600 caracteres ganha da que entrega 1.800.

## Hashtags, com honestidade

Hashtag não é mais alavanca de alcance, e a plataforma deixou isso claro com
uma mudança de produto: **desde 18 de dezembro de 2025 o Instagram limita a
cinco hashtags por post**, antes eram trinta, orientando a usar poucas e
específicas em vez de muitas genéricas. Adam Mosseri já tinha dito no começo de
2025 que hashtag funciona como etiqueta de tema, não como distribuição.

Então: até cinco, específicas, como etiqueta. Se o cliente tem um bloco de
vinte salvo no bloco de notas, esse bloco virou peso morto e o revisor vai
reprovar.

`#viral`, `#fyp`, `#explorar`, `#reelsbrasil`, `#sucesso`, `#foco` não
descrevem nada. Corte.

## Termos de busca importam mais que hashtag agora

A busca do Instagram lê o texto da legenda. Então a frase pela qual o usuário
quer ser encontrado entra na legenda como alguém digitaria, numa frase normal.
"Leilão de imóveis em João Pessoa" como palavras na linha três, não
"#leilaodeimoveisjp" num bloco no fim. O revisor ignora acento ao conferir
("leilao" e "leilão" contam igual), mas escreva com acento, que é como as
pessoas leem.

Peça dois ou três desses termos e passe pro revisor:

```bash
python3 caption.py rascunho.txt --keywords "cardápio digital,delivery próprio"
```

## Regras

- **Sem link na legenda.** Legenda não é clicável. URL no texto é texto morto
  que diz "eu não uso essa plataforma". Bio ou direct.
- **Um pedido.** Dois pedidos é o mesmo que nenhum. O `caption.py` conta.
- **Palavra-chave precisa ser digitável.** Uma palavra, sem espaço, sem emoji,
  em maiúscula, e falada no vídeo também. `Comenta EDITAL` funciona.
  `Comenta "quero o guia do edital"` não.
- **No Brasil, a conversa costuma fechar no WhatsApp.** Se é o caso, o pedido
  pode ser o direct e o direct entrega o link do WhatsApp. Não ponha o número
  de telefone na legenda.
- **Escreva o primeiro comentário separado** se houver link. Diga isso no recibo.
- **Emoji como pontuação, não enfeite.** O revisor sinaliza acima de 4 a cada
  100 caracteres.
- **Texto alternativo vale 20 segundos.** Para carrossel e foto, escreva. É
  lido por leitor de tela e pelo Instagram.

## O ciclo

1. Decida Trabalho A ou B e diga qual.
2. Escreva.
3. Rode `/ig-human`. Legenda é curta, então clichê aparece mais aqui do que em
   qualquer outro lugar do pacote.
4. Rode `caption.py` com os termos de busca. Corrija toda FALHA. Decida cada
   ALERTA em voz alta, nunca em silêncio.
5. Entregue o bloco pronto pra copiar, e o recibo:

```
LEGENDA PRONTA
trabalho:   A - o reel carrega o hook
visível:    118 de 125 caracteres usados antes do corte
pedido:     um, comentar EDITAL
hashtags:   3
busca:      "leilão de imóveis" na linha 3, "edital" na linha 5
revisor:    PRONTA
```

## Publicação

Por padrão nada é publicado: o usuário cola a legenda.

Se a sessão tiver o conector oficial da Meta (ferramentas de Instagram como
`publish_instagram_media`) e o usuário **pedir explicitamente** para publicar,
isso usa a API oficial de publicação para contas profissionais, que é permitida
pelos Termos. Nesse caso: mostre a prévia final (mídia, legenda inteira, conta
de destino), espere um "sim, publica" claro nesta conversa, publique uma vez e
informe o link do post. A mídia precisa estar numa URL pública; se não estiver,
diga isso e pare. Nunca publique por iniciativa própria, nunca em lote, e nunca
use automação de navegador para postar.
