---
name: ig-viral
description: >-
  Vai atrás dos reels que estão funcionando agora no nicho do usuário, ranqueia
  pelo quanto cada um superou a própria conta, nomeia a fórmula de hook de cada
  um e transforma isso num swipe file pronto pra gravar. Use quando o usuário
  disser "acha vídeos virais", "o que tá funcionando agora", "o que estão
  postando no meu nicho", "faz engenharia reversa dessa conta", "monta um swipe
  file", "por que esse reel bombou", ou perguntar o que fazer a seguir sem ter
  evidência pra responder.
---

# ig-viral

A skill de pesquisa. Todas as outras escrevem; esta vai e olha. Rode uma vez
por mês, não todo dia. Fórmula dura uma estação.

Uma ferramenta mora nesta pasta e ela roda:

```bash
python3 swipe.py coletado.tsv --out <pasta da conta>/swipe.md
```

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
O swipe file é por cliente: nicho de delivery e nicho de leilão não se misturam.

## A ideia que faz isso valer a pena

**View bruta não é evidência.** Uma conta com dois milhões de seguidores
fazendo 400 mil views teve uma terça fraca. Uma conta com quatro mil seguidores
fazendo 400 mil views achou alguma coisa, e essa coisa é copiável.

Então tudo aqui é ranqueado pelo **múltiplo sobre a mediana**: views divididas
pela mediana recente daquela conta. Acima de 3x é sinal. Abaixo de 1,5x é o dia
normal daquela conta e não ensina nada, por maior que o número pareça.

Colete contas **até umas 10x o tamanho do usuário**. Fórmula que funciona com 2
milhões de seguidores muitas vezes funciona porque são 2 milhões.

## Passo 1: escolher as contas

Peça ao usuário de 6 a 12 contas, ou proponha e peça aprovação:

- **4 diretas**: mesmo nicho, mesma oferta, um pouco à frente.
- **4 adjacentes**: nicho diferente, mesmo público. É daqui que o formato é
  emprestado antes de alguém do nicho ter.
- **2 a 4 grandes**: contas muito maiores, só pelo formato, nunca pelo ritmo ou
  pelo tom.

Prefira contas brasileiras para as diretas: o hook que funciona em português
tem ritmo diferente do americano traduzido. Peça também que o usuário abra a
própria **coleção de Salvos**. É o corpus mais rápido e relevante que existe e
já vem filtrado pelo gosto dele.

## Passo 2: ir olhar

Use a ferramenta de navegação que esta sessão realmente tem: navegador do app,
extensão no Chrome do próprio usuário, ou uso do computador. Não existe API
para isso e não precisa, porque o volume é pequeno o bastante pra ler.

**Regras inegociáveis:**

- **Nunca faça login no Instagram pelo usuário e nunca peça senha.** Se a
  página pede login, quem já está logado é o usuário. Conduza o navegador dele
  com ele presente, ou peça que cole as informações.
- **Isso é leitura, não raspagem.** Dez contas, uma dúzia de reels cada, em
  velocidade humana. Coleta automatizada em volume viola os Termos de Uso do
  Instagram e bloqueia conta. Não construa crawler, não use serviço de scraping
  e não rode isso em loop em segundo plano.
- **Copie a fórmula, nunca o vídeo.** O formato do hook, a estrutura, a
  duração, o padrão de cortes. Não o roteiro, não a voz, não a edição.
  Atribua cada linha do swipe file à conta de onde veio.

**O que capturar por reel**, nas palavras do criador:

| campo | observação |
| --- | --- |
| conta | o @ |
| seguidores | do perfil |
| mediana | olhe os últimos 12 reels e pegue a view do meio |
| views | deste reel |
| hook | a primeira linha, falada ou na tela, literal, com erro e tudo |
| tela | a primeira cartela de texto, se for diferente |
| duração | segundos |
| cta | o que pediram no final |

A mediana é a mais importante. Sem ela, você volta a ranquear por número de
seguidores, que é justamente o que esta skill existe pra impedir.

**Quando o Instagram não mostra o bastante:** a mesma gramática de hook roda no
YouTube Shorts, onde views e legendas automáticas são públicas e não há login.
É um segundo corpus legítimo, e o hook falado é mais fácil de pegar:

```bash
# views dos shorts de um canal
python3 -m yt_dlp --flat-playlist --playlist-end 40 -J \
  "https://www.youtube.com/@CANAL/shorts" > canal.json

# a primeira frase falada de um short, das legendas automáticas em português
python3 -m yt_dlp --skip-download --write-auto-subs --sub-langs "pt.*" \
  --sub-format json3 -o hook "https://www.youtube.com/watch?v=ID_DO_VIDEO"
```

Pegue toda palavra da legenda com tempo abaixo de 3,0 segundos. Esse é o hook
como foi dito, não como foi escrito.

## Passo 3: ranquear

Preencha um arquivo separado por TAB com cabeçalho (colunas em português ou
inglês) e rode o script:

```
conta	seguidores	mediana	views	hook
@alguem	48000	11000	412000	ninguém te conta que seus 30 primeiros reels vão flopar
```

```bash
python3 swipe.py coletado.tsv --out <pasta da conta>/swipe.md
```

Ele calcula o múltiplo, nomeia a fórmula de hook usando as mesmas 26 fórmulas
de onde o `/ig-reel` escreve (com regex para fala brasileira), dá nota a cada
hook com o `hookscore.py` e mostra o que separa o terço de cima do terço de
baixo.

## Passo 4: dizer o que significa, com cuidado

Relate três coisas e só:

1. **Quais fórmulas aparecem demais** no terço de cima, com contagem. Duas
   fórmulas aparecendo quatro vezes cada em seis contas é achado. Uma
   aparecendo duas vezes não é.
2. **O que o terço de cima tem em comum na estrutura** que o de baixo não tem:
   tamanho do hook, se a entrega é visual, se o primeiro quadro se mexe, onde
   está o pedido.
3. **As linhas sem fórmula.** Todo hook que o classificador não nomeou é ruído
   ou uma fórmula que ainda não está no `hooks.json`. Leia à mão. É a coluna
   mais valiosa da saída e é por isso que o script mostra a contagem. Se achar
   um formato novo que se repete, proponha acrescentar ao `hooks.json`.

Depois diga o tamanho da amostra e a confiança com palavras simples. Quarenta
reels em seis contas sustentam uma afirmação. Doze não, e dizer isso é a
diferença entre pesquisa e horóscopo.

## Passo 5: virar algo pra gravar

Para as três fórmulas do topo, escreva **a versão do usuário**: a história
dele, o número dele, no formato que está funcionando. Entregue cada uma ao
`/ig-reel` com o número da fórmula já escolhido.

Nunca devolva "faz um reel igual esse". Devolva uma linha de hook que ele
poderia falar amanhã.

## Saída

```
SWIPE  ·  38 reels  ·  7 contas  ·  base: mediana da conta

OUTLIERS (acima de 3x)
  38,4x  hook 86  #3  Ninguém Te Conta   @conta_a   412.000  (mediana 10.700)
  11,2x  hook 79  #9  Roube Isso         @conta_c   180.000  (mediana 16.100)
  ...

O QUE ESTÁ APARECENDO DEMAIS
  #3 Ninguém Te Conta   x5 no terço de cima, 0 no de baixo
  #2 Comando Negativo   x4
  tamanho mediano do hook: 8 palavras em cima, 19 embaixo

SEM FÓRMULA (6)
  Dois deles têm o mesmo formato e ele não está no hooks.json: um hook que
  abre lendo em voz alta o comentário de outra pessoa. Vale acrescentar.

SUA VERSÃO
  #3  "Ninguém te conta que os primeiros 20 lances são pra perder."
  ...
```

Grave o swipe file em `swipe.md` na pasta da conta. O `/ig-reel` e o `/ig-plan`
leem esse arquivo, que é o ponto: depois que isto roda uma vez, o resto do
pacote trabalha com a evidência do próprio usuário em vez de padrões.

Nada é postado, seguido, curtido ou mandado por esta skill. Ela lê.
