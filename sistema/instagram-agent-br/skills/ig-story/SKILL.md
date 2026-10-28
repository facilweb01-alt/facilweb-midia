---
name: ig-story
description: >-
  Escreve os Stories do dia no Instagram, em português: a sequência quadro a
  quadro, qual figurinha usar onde, e a que leva as pessoas para o direct. Use
  quando o usuário disser "stories", "o que eu posto no story", "sequência de
  story", "ideia de enquete", "não tenho o que postar no story", ou quiser
  vender algo sem fazer um post sobre isso.
---

# ig-story

Story não é um feed menor. O feed é como desconhecidos te acham. O story é como
quem já te segue decide se você é alguém de quem vale comprar, e é a única
superfície do Instagram onde um toque vira conversa num movimento só.

Ninguém fora dos seus seguidores vê isso, então o trabalho é completamente
outro: profundidade, não alcance.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.

## O formato do dia

De três a sete quadros por dia. Depois de uns sete, a taxa de pular sobe e os
últimos quadros tocam pra ninguém, que é exatamente onde as pessoas põem o
pedido.

```
1       A ABERTURA   algo acontecendo hoje, com um rosto ou uma mão.
2-3     O MEIO       o conteúdo de verdade: o processo, o resultado, o erro.
4       O PEDIDO     uma figurinha. Enquete, caixa de pergunta, quiz ou link.
5       O FECHO      a resposta, o resultado, ou a preparação de amanhã.
```

Ponha o pedido no quadro 4, não no 7. A conclusão cai a cada toque e o pedido
tem que ser visto por quem ainda está ali.

## As figurinhas, e para que cada uma serve de verdade

| figurinha | função | use quando |
| --- | --- | --- |
| **Enquete** | o toque mais barato que existe | quer volume de resposta, não informação |
| **Caixa de pergunta** | colher as palavras exatas que as pessoas usam | precisa de ideia de conteúdo ou de objeção, literal |
| **Quiz** | ensinar deixando a pessoa errar | existe um equívoco comum no nicho |
| **Controle deslizante** | termômetro de humor | nada importante. Divertido, pouco valor |
| **Link** | a única superfície clicável além da bio | existe um lugar real para ir (incluindo o WhatsApp) |
| **Contagem regressiva** | um prazo que dá para ativar lembrete | lançamento, live, data de leilão, fim de promoção |
| **Sua vez** | alcance além dos seguidores, às vezes | o pedido é algo que qualquer um do nicho responde |

A caixa de pergunta é a mais subestimada da lista. Cada resposta é uma legenda,
um hook de Reel ou uma abertura de direct escrita nas palavras do público.
Passe para o `/ig-reel` como fórmula #16.

## Regras

- **Rosto ou mão no primeiro quadro.** Texto em fundo colorido é pulado, e o
  primeiro quadro decide se o resto é assistido.
- **Uma ideia por quadro.** Ler parágrafo em story não é algo que alguém faz.
- **Texto no meio.** Em 1080x1920, nada acima de y=250 ou abaixo de y=1600. A
  linha do perfil fica em cima e a barra de resposta embaixo.
- **Fale com uma pessoa.** "Você", no singular. Story é o mais perto de direct
  que existe sem ser direct.
- **Não repostar o próprio post no story sem comentário.** É o quadro mais
  ignorado da plataforma. Se vai apontar para um post, diga o que aconteceu nos
  comentários e por que vale voltar lá.
- **Venda no story, não no post.** Três quadros de contexto, um de oferta, um
  de prova. Essa sequência vende mais que um post no feed sobre a mesma coisa e
  não custa alcance.

## O funil de direct, feito com honestidade

A sequência que funciona: um story que nomeia um problema, uma caixa de
pergunta ou enquete que deixa a pessoa dizer "sou eu", e então uma resposta a
cada pessoa que respondeu. A conversa começa porque ela falou primeiro. Se a
conversa evoluir, a passagem para o WhatsApp segue as regras do `/ig-dm`.

Resposta automática por palavra-chave no direct é um recurso real e permitido
para conta profissional, pelas ferramentas do próprio Instagram e por parceiros
aprovados pela Meta. Mandar direct em massa para quem não interagiu não é, e é
o que restringe conta. A regra é simples: **ela age primeiro, depois você
responde.**

## Saída

Os quadros em ordem, cada um com o que está na tela, o que é falado e qual
figurinha, mais o que fazer com as respostas:

```
STORIES  ·  terça  ·  5 quadros

1  [selfie, andando]     "Terceiro pedido de reembolso do ano. Mesmo motivo."
2  [gravação de tela]    a cláusula, destacada
3  [falando]             "Aprovação é sentimento. Entrega é data."
4  [enquete]             "Já levou calote por aprovação atrasada?"  Já / Ainda não
5  [texto sobre foto]    "Responde aqui que eu te mando a cláusula."

Depois: todo mundo que votar "Já" recebe uma resposta. Esse é o funil inteiro.
```

Nada é postado. O usuário posta.
