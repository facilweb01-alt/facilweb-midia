---
name: ig-dm
description: >-
  Escreve mensagens de direct no Instagram, em português, que recebem resposta:
  a entrega da palavra-chave, a primeira mensagem para quem interagiu, o pitch
  de collab, a passagem para o WhatsApp e os dois follow-ups. Use quando o
  usuário disser "manda direct pra essa pessoa", "o que eu mando", "mensagem de
  abordagem", "como faço follow-up", "pitch pra marca", ou estiver abordando
  alguém específico.
---

# ig-dm

O direct é o único lugar do Instagram onde o dinheiro muda de mão de verdade, e
também é onde a maioria das contas queima a boa vontade que o conteúdo ganhou.
A diferença está inteira em quem se mexeu primeiro.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
A mensagem sai na voz de `voice.md` dessa conta.

## Os três tipos de direct que valem escrever

**1. A resposta a quem levantou a mão.** Comentou a palavra-chave, respondeu a
enquete, respondeu um story, salvou e perguntou. A pessoa se mexeu primeiro.
São 90% dos directs que valem mandar, e convertem porque não são abordagem.

**2. A aproximação morna.** Alguém em cujos posts o usuário comenta de verdade
há semanas. Já existe uma linha de conversa.

**3. O pitch de collab ou de marca.** Uma proposta específica para uma conta
específica, com um motivo para ser ela.

Todo o resto é direct frio para desconhecido, que é o que todo mundo faz, e é
por isso que a taxa de resposta é o que é. Se o usuário pedir uma sequência
fria, diga com clareza que é a coisa de menor retorno que ele poderia fazer com
a mesma hora, e ofereça a alternativa: comentar nessas dez contas por duas
semanas antes. Depois escreva, se ele ainda quiser.

## Antes de escrever, pegue os detalhes

Pergunte numa pergunta só, agrupada:

1. **Quem**: @, o que faz, e o que postou ou fez que começou isso.
2. **O gatilho**: o motivo real para mandar hoje. Uma palavra-chave que
   comentou, um story que respondeu, um post que publicou. Não "tem o perfil do
   cliente ideal".
3. **O que o usuário quer**: uma conversa, uma venda, uma collab, uma
   indicação. Seja honesto internamente, mesmo que a mensagem não comece por aí.

Sem gatilho, não tem mensagem. Diga isso.

## A entrega da palavra-chave

O direct mais comum deste pacote e o mais fácil de estragar. A pessoa comentou
uma palavra. Está esperando a coisa. Então:

```
{nome}, tá aqui: {a coisa, ou o link}.

{uma linha sobre como usar}

{uma pergunta que ela responde em quatro palavras}
```

Mande a coisa **primeiro**, na mensagem um, sem condição. Post de palavra-chave
que entrega um "antes de te mandar, me conta o que você faz?" é isca e troca, e
a pessoa lembra. A pergunta no fim é o que começa a conversa, e é opcional pra
ela.

Resposta automática por palavra-chave é recurso permitido para conta
profissional, pelas ferramentas do próprio Instagram ou por parceiro aprovado
pela Meta. Usar isso é ok. Mandar direct em massa para quem não interagiu não
é, e é o caminho mais rápido para conta restrita.

## A primeira mensagem para alguém morno

- **De duas a quatro frases.** Tela cheia de texto é apagada.
- **Cite a coisa específica.** O comentário, o post, a resposta. Nas palavras
  da pessoa.
- **Dê antes de pedir.** Um número, um modelo, um nome, uma resposta.
- **Um pedido, pequeno.** "Vale uma conversa rápida?" ganha de "deixa eu te
  apresentar a plataforma".
- **Sem link e sem agenda na mensagem um.** Parece funil porque é.
- **Sem áudio para desconhecido.** No Brasil o áudio é ótimo e é para quem já
  conhece a voz do usuário. Para quem não conhece, é invasivo.

## A passagem para o WhatsApp

No Brasil, muita venda fecha no WhatsApp, não no direct. Faça a passagem só
quando a pessoa já respondeu e a conversa tem motivo para continuar:

- Pergunte antes: "Quer que eu te mande os detalhes no WhatsApp? Fica mais fácil
  de achar depois."
- Se ela disser sim, mande o link `wa.me` com mensagem pronta, não o número
  solto, e diga quem vai responder lá.
- Nunca peça o número da pessoa na primeira mensagem, e nunca adicione ninguém
  em grupo ou lista de transmissão sem a pessoa pedir.

## O pitch de collab

Quatro linhas, nesta ordem: o que você viu a pessoa fazer, a ideia específica,
o que ela ganha, o que você precisa dela. Post em collab aparece nos dois grids
e alcança os dois públicos, que é a maior mecânica de crescimento do Instagram
que não envolve pagar ninguém. Apresente assim e seja concreto sobre quem faz
o quê.

## Follow-ups

Dois. Esse é o número.

- **+4 dias**: acrescente algo novo. Nunca "só passando pra lembrar". Se não tem
  nada novo, não tem follow-up.
- **+10 dias**: a mensagem de fechamento. Diga que vai parar, e pare de verdade.
  Essa recebe uma fatia surpreendente das respostas, porque tira a pressão.

Depois pare. O terceiro não converte ninguém e custa o relacionamento.

## Nunca

- Nunca automatize directs de abordagem, e nunca use ferramenta que manda em
  horário programado para quem não interagiu. Viola os Termos de Uso do
  Instagram e restringe a conta.
- Nunca invente que assistiu algo, um contato em comum, ou qualquer coisa
  compartilhada.
- Nunca abra com "Oi! Uma pergunta rápida" e depois não pergunte nada.
- Nunca mande o pitch na mesma mensagem do elogio.

## Saída

A mensagem, a contagem de caracteres e os dois follow-ups com o dia de cada um,
tudo passado pelo `/ig-human`. O usuário manda cada uma à mão, ou pela própria
automação aprovada, só para respostas de palavra-chave.
