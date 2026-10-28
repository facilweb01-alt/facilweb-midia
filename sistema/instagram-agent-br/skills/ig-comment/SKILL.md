---
name: ig-comment
description: >-
  Escreve comentários em posts e reels de outras pessoas no Instagram, em
  português, que soam como uma pessoa com opinião e não como robô. Use quando o
  usuário colar um post ou reel e quiser um comentário, disser "comenta nisso",
  "engaja nesse", "o que eu falo aqui", ou quiser um lote para a rodada diária
  de engajamento.
---

# ig-comment

Comentar é o tempo mais bem gasto do dia no Instagram e o mais fácil de fazer
mal. Um comentário no topo de um reel com 40 mil views é visto por mais gente
do que a maioria dos posts da própria conta, e é o único lugar onde um
desconhecido toca direto pra um perfil.

Comentário genérico é pior que nenhum. Gasta um toque que não leva a lugar
nenhum e marca a conta como "grupo de engajamento" para a única pessoa cuja
opinião importava, que é o criador.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
O comentário sai na voz de `voice.md` dessa conta.

## Entrada

O usuário cola o texto do post ou reel, ou um print, com o nome da conta. Se
mandar uma URL que você não consegue abrir, peça que cole. Não use navegador
para raspar o feed e não poste nada.

## Os nove tipos de comentário

Escolha pelo que o post realmente é. Nunca vá direto no tipo 1.

| # | tipo | quando | formato |
| --- | --- | --- | --- |
| 1 | **Acrescenta um dado** | o post faz uma afirmação que você sustenta com número | "Aqui foi igual: 40% de..." |
| 2 | **O caso que faltou** | o post está certo mas incompleto | "Isso vale até {condição}." |
| 3 | **Discorda com respeito** | você acha mesmo que está errado | concorda com algo primeiro, depois a bifurcação |
| 4 | **Estica uma linha** | uma linha do post é a boa | cita ela e constrói em cima |
| 5 | **A pergunta de verdade** | o post pulou a parte difícil | uma pergunta, específica |
| 6 | **O recibo** | você já fez o que ele descreveu | o que aconteceu, duas frases |
| 7 | **A correção** | tem um erro factual | esteja certo, seja breve, seja gentil, tenha certeza |
| 8 | **O reenquadramento** | fatos certos, moldura errada | "Outro jeito de ler isso:" |
| 9 | **A frase curta** | o post não precisa de nada, você quer presença | menos de 10 palavras, tem que ser engraçada ou verdadeira |

## Regras

- **De uma a três frases.** Comentário é lido numa coluna estreita embaixo de
  um vídeo. Parágrafo é recolhido atrás do "mais" e ninguém toca.
- **Nunca abra com** "Ótimo post", "Amei", "Verdade", "Isso 👏", "Precisava ler
  isso hoje", "Que conteúdo!", ou o primeiro nome do criador com ponto de
  exclamação. São todos invisíveis.
- **Nada de comentário só com emoji** e nada de emoji como primeiro caractere.
- **Nunca repita o reel.** Todo mundo que está vendo acabou de assistir.
- **Uma ideia.** Comentário com dois pontos soa como sequestro do post.
- **Diga a coisa específica.** Se o comentário caberia embaixo de qualquer post
  sobre o assunto, não é comentário, é ruído.
- **Nunca vender.** Nem a oferta, nem o link, nem "dá uma olhada no meu
  perfil", nem "te chamei no direct". É o jeito mais rápido de ser bloqueado
  justamente pela pessoa que você queria alcançar.
- **Cedo importa mais aqui do que em qualquer lugar.** Comentário na primeira
  hora de um reel que depois viaja vai junto com ele.

## Saída

Dê **duas opções de tipos diferentes**, com rótulo, mais uma linha dizendo qual
você postaria e por quê. Passe as duas pelo `/ig-human` antes: comentário é
curto, então um travessão ou uma expressão pronta pesa proporcionalmente mais
do que numa legenda.

```
OPÇÕES DE COMENTÁRIO  (no reel do @conta sobre preço)

[6 · Recibo]
A gente subiu 40% em março do ano passado e perdeu exatamente um cliente, o que
ocupava metade do direct. Levei oito meses pra perder o medo disso.

[3 · Discorda com respeito]
Concordo com a âncora. Onde eu discordo é fazer isso no meio do projeto. A gente
tentou e custou uma renovação que estava tranquila.

Posta o primeiro. Ele cede alguma coisa e tem um número.
```

## Modo lote

Para uma rodada de engajamento, peça de 5 a 10 posts colados numa mensagem só,
devolva um comentário para cada num bloco único, e mantenha uma anotação em
`log.md` da pasta da conta de quem já recebeu comentário nesta semana. Comentar
nas mesmas três contas todo dia é visível e parece exatamente o que é.

## Nunca

Não poste automaticamente, não automatize comentários e não use navegador para
publicar em nome do usuário. Engajamento automatizado viola os Termos de Uso do
Instagram e bloqueia conta. Esta skill escreve o comentário. O usuário posta.
