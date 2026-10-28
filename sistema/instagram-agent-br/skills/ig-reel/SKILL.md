---
name: ig-reel
description: >-
  Escreve um Reel de Instagram em português a partir de uma ideia crua: opções
  de hook tiradas de 26 fórmulas, o roteiro falado, o texto de tela e um beat
  sheet cronometrado, na voz do próprio criador e com nota antes de gravar. Use
  sempre que o usuário quiser um Reel, roteiro de vídeo curto, um hook, uma
  locução, "faz um reel sobre X", "o que eu falo nesse vídeo", ou estiver prestes
  a gravar sem a primeira frase.
---

# ig-reel

Transforma uma ideia crua num Reel que alguém assiste até o fim.

Duas ferramentas moram nesta pasta e as duas rodam de verdade. Use. Não avalie
o hook no olho e não chute a duração.

```bash
python3 hookscore.py hooks.txt              # ranqueia suas opções de hook
python3 hookscore.py --hook "uma linha"     # nota de um hook só
python3 beats.py roteiro.txt --target 30    # beat sheet cronometrado antes de gravar
```

As duas são calibradas para português do Brasil: entendem "R$18 mil", "cê",
"pra", saudações ("oi gente", "fala galera") e preâmbulos ("nesse vídeo eu vou
te mostrar"). Não use para roteiro em inglês.

## Pasta da conta

Tudo que esta skill lê e grava fica na pasta da conta:

- Conta única: `~/.claude/instagram/`
- Agência com várias contas: `~/.claude/instagram/clientes/<cliente>/`

Se existir a pasta `clientes/` com mais de um cliente e o usuário não disse de
qual é o Reel, pergunte antes de qualquer outra coisa. Roteiro na voz errada
não serve pra nada.

## Antes de escrever

1. Leia `voice.md` da pasta da conta. É o perfil de voz: como a pessoa fala na
   câmera, o que nunca diz, com quem está falando. Se não existir, peça **três
   reels dela**, transcreva ou leia, deduza a voz e escreva o arquivo a partir
   de `templates/voice.md`. Roteiro na voz errada é inutilizável, porque ela
   tem que falar em voz alta.
2. Leia `hooks.json` nesta pasta. 26 fórmulas, cada uma com modelo, exemplo
   preenchido, versão de tela, pra que serve e como costuma ser estragada.
3. Se a ideia é rala, não encha linguiça. Faça uma pergunta só, agrupada: o
   que aconteceu, com quem, e quanto custou ou rendeu. Um Reel precisa de uma
   coisa específica e verdadeira. Consiga isso antes de escrever.
4. Se existir `swipe.md` na pasta da conta, leia. O `/ig-viral` escreve esse
   arquivo, e ele é a evidência do próprio usuário sobre quais fórmulas estão
   funcionando no nicho agora. Vale mais que os padrões deste arquivo.

## O formato

Um Reel é decidido nos dois primeiros segundos e mantido nos cinco seguintes.

```
0:00 - 0:02   HOOK        a afirmação. Fala e texto de tela, escritos separados.
                          Movimento no primeiro quadro, não um rosto parado.
0:02 - 0:07   O QUE ESTÁ  por que isso importa pra quem está assistindo. Uma linha.
              EM JOGO
0:07 - ...    O CORPO     uma ideia por beat, e o quadro muda a cada beat.
ÚLTIMOS 3s    A ENTREGA   entrega o que o hook prometeu, depois o pedido único.
ÚLTIMA LINHA  O LOOP      repete uma palavra do hook pra o replay encaixar.
```

Duração: de 15 a 45 segundos é a faixa que funciona. Reel vai até 3 minutos e
quase ninguém deveria usar. Abaixo de 7 segundos o loop infla a contagem e mais
nada.

## O ciclo

**1. Escolha três hooks, não um.** Passe a ideia pelo `hooks.json`, escolha
três fórmulas que realmente servem e escreva a fala e o texto de tela de cada
uma. Fórmulas diferentes, não três versões da mesma.

**2. Dê nota.** Ponha as três falas num arquivo, uma por linha, e rode
`hookscore.py`. Mostre o ranking ao usuário. Se o primeiro está abaixo de 50,
você ainda não tem o hook e nenhuma edição resolve.

**3. Escreva o roteiro** no hook vencedor. Português falado, do jeito que a
pessoa fala de verdade: "pra", "tá", "a gente", frases curtas. Nenhuma frase
que ela precisaria ensaiar.

**4. Cronometre.** Rode `beats.py roteiro.txt --target {duração}`. Corrija
todo aviso: hook passando de 3 segundos, beat acima de 4 segundos, sequência de
beats sem nada concreto, falta de loop. Rode de novo até limpar. Se o usuário
fala rápido ou devagar, ajuste com `--wpm` (padrão 150).

**5. Humanize.** Passe o roteiro pelo `/ig-human` antes de mostrar. Frase com
cara de texto escrito fica óbvia no instante em que alguém fala em voz alta.

**6. Entregue o bloco.** O roteiro num bloco de código, o texto de tela numa
lista separada com tempos, e então:

```
REEL PRONTO
hook:        #3 Ninguém Te Conta, nota 81 FORTE
duração:     28,4s em 9 beats a 150 ppm
tela:        6 cartelas
humanizador: 4 marcas removidas, nota humana 81 APROVADO
legenda:     rode /ig-caption em seguida

Responda "sim" para registrar, ou diga o que mudar.
```

**7. Publicação.** Esta skill produz um roteiro; o usuário grava. No "sim",
acrescente em `log.md` da pasta da conta a data, a fórmula usada e a primeira
linha, pra o `/ig-audit` ter histórico depois.

## Texto de tela é um roteiro separado

Escreva separado, sempre. Ele é lido antes de ser ouvido.

- **Seis palavras ou menos por cartela.** É lido à distância de um braço por
  alguém que ainda não está ouvindo.
- **A cartela do hook aparece no quadro 1**, não depois de um segundo de
  silêncio.
- **Fique dentro da área segura.** Num quadro 1080x1920, nada acima de y=230 ou
  abaixo de y=1440, e os 230 pixels da direita livres. A interface fica por
  cima de tudo fora disso: legenda, botões, faixa de áudio.
- **Nunca ponha o hook onde fica a legenda.** É a parte de baixo do quadro e
  fica coberta.
- **Legende o corpo do vídeo.** A maioria assiste sem som primeiro.

## Regras que fazem diferença

- **Uma ideia por Reel.** Se o roteiro tem duas, são dois Reels. Diga isso.
- **Número em vez de adjetivo.** "R$4.200" ganha de "muito dinheiro". Se o
  usuário não deu número, peça em vez de escrever em volta do buraco.
- **Corte a introdução.** Sem "oi gente", sem "nesse vídeo", sem nome, sem
  vinheta. O vídeo começa na frase que você chegaria no sexto segundo.
- **Mude o quadro a cada beat.** Plano parado por 8 segundos é onde as pessoas
  saem, e o `beats.py` vai avisar.
- **Um pedido no fim.** Comentar uma palavra, salvar, ou seguir. Um.
- **Nunca invente.** Nada de métrica, cliente, faturamento ou resultado
  inventado em nome do usuário, nem como placeholder. Se precisa de um número e
  ele não existe, deixe `{{seu número}}` no roteiro e sinalize.
- **Não escreva roteiro em cima de áudio em alta que o usuário não pode usar.**
  Conta comercial tem biblioteca de áudio restrita. Se a ideia pede a voz do
  próprio usuário, diga isso.

## Exemplo

```
/ig-reel a gente cortou o tempo de orçamento de 5 horas pra 20 minutos com um modelo
```

```
HOOKS  (com nota)
  86  FORTE  #5  Colapso de Tempo    "Orçamento me levava cinco horas. Hoje leva vinte minutos."
                                     tela: 5 HORAS -> 20 MIN
  71  FORTE  #1  Confissão de Custo  "Eu cobrava quatro horas por semana só de formatação. Por dois anos."
                                     tela: 2 ANOS JOGADOS FORA
  54  OK     #9  Roube Isso          "Rouba o modelo de orçamento que fez isso."
                                     tela: ROUBA ISSO

Gravando o #5: a proporção é crível, lê numa olhada na tela,
e o número é seu.
```
