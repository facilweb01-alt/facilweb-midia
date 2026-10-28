---
name: ig-reply
description: >-
  Cuida dos comentários embaixo dos reels e posts do próprio usuário: escreve
  respostas, em português, para os que valem resposta, organizados por quais
  valem. Use quando o usuário colar os comentários, disser "responde esses",
  "cuida dos meus comentários", "fulano disse X no meu reel", ou estiver lidando
  com crítica, hater ou lead nos comentários.
---

# ig-reply

O fio de comentários embaixo do próprio post é onde o alcance é decidido. Toda
resposta é mais uma interação no post, as respostas da primeira hora fazem a
maior parte do trabalho, e no Instagram uma resposta pode ser um Reel, que é a
jogada mais subutilizada da plataforma.

Mas o valor não é igual entre comentários, então esta skill organiza antes de
escrever.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
As respostas saem na voz de `voice.md` dessa conta.

## Entrada

O usuário cola os comentários, de preferência com os @. Print serve. Se o
conector oficial da Meta estiver na sessão e oferecer leitura de comentários
dos posts, pode puxar por lá. Não raspe o fio com navegador.

## Triagem primeiro

Separe cada comentário em um de seis grupos e diga as contagens:

| grupo | o que é | o que recebe |
| --- | --- | --- |
| **PALAVRA-CHAVE** | a palavra que você pediu para comentar | a coisa prometida, à mão ou pela ferramenta aprovada |
| **LEAD** | alguém descrevendo o problema que você resolve | uma resposta de verdade em público, depois uma porta |
| **SUBSTÂNCIA** | acrescenta dado, discorda, estende | a resposta mais longa do fio |
| **PERGUNTA** | uma dúvida que muita gente tem | vira Reel, não só resposta |
| **APOIO** | "🔥", "top demais", uma marcação | uma curtida, e de 3 a 8 palavras no máximo |
| **RUÍDO** | venda, spam, má-fé, provocação | nada, ou uma linha e fim |

Escreva nessa ordem e pare quando o valor acabar.

## A jogada que a maioria perde

Se uma pergunta nos comentários é uma que outras trinta pessoas também têm,
**responda com um Reel**. O Instagram anexa o comentário ao vídeo novo como
figurinha, quem perguntou é notificado, e uma pergunta com demanda real vira um
post com o hook já escrito. Sinalize toda PERGUNTA que se qualifica e passe ao
`/ig-reel` como fórmula #16.

## Como responder

- **Responda a pergunta de verdade.** Se alguém pergunta como, diga como, na
  resposta. Não mande para o direct para ouvir uma resposta que podia estar ali.
- **Use o nome da pessoa uma vez**, no começo, sem ponto de exclamação.
- **Acompanhe o tamanho.** Comentário de quatro palavras não ganha resposta de
  quatro linhas.
- **Para crítico:** conceda a parte verdadeira primeiro, nas palavras dele,
  depois mantenha a posição. Nunca apague, nunca fique na defensiva, nunca
  responda duas vezes no mesmo fio.
- **Para hater:** nada. Resposta é alcance, e alcance é o que ele veio buscar.
  Oculte o comentário se for ofensivo. Os controles de comentário do Instagram
  existem e usar não é perder.
- **Para lead:** responda completo em público. A porta é uma frase no fim e é
  uma oferta de ajuda, não um pitch. A resposta pública é o que faz a próxima
  pessoa te chamar no direct. Se a conversa precisa de dado pessoal (endereço,
  telefone, valor da dívida), leve para o direct e diga por quê.

## Comentários de palavra-chave

Se o post usou pedido de palavra-chave, esses comentários são o motivo do post.
Cada um é uma pessoa que levantou a mão. Responda a cada um, depois mande o que
foi prometido. Se o usuário tem automação configurada pelas ferramentas do
próprio Instagram ou por parceiro aprovado pela Meta, diga isso e deixe rodar;
se não, as respostas são manuais e tudo bem nesse volume. Nunca mande direct em
massa para quem não comentou.

## Saída

Um bloco, agrupado por grupo, cada resposta pronta para copiar e já humanizada:

```
RESPOSTAS  ·  84 comentários  ·  41 PALAVRA-CHAVE, 2 LEAD, 3 SUBSTÂNCIA, 2 PERGUNTA, 34 APOIO, 2 RUÍDO

PALAVRA-CHAVE  (41)  mandar a cláusula. Uma linha cada, mesmo carinho, sem copiar e colar.

LEAD
@perfil - "aconteceu exatamente isso com a gente em junho"
> O que resolveu pra nós foi tirar o gatilho do pagamento da aprovação. Se
> ajudar, te mando o texto da cláusula.

PERGUNTA -> REEL
@perfil - "e se o cliente se recusar a assinar?"
  34 curtidas nesse comentário. Isso é Reel, não resposta. Fórmula #16.

RUÍDO  (2)  ignorados. Responder dá alcance pra eles.
```

Depois, a trava: nada é postado até o usuário dizer sim. Ele cola as respostas.
