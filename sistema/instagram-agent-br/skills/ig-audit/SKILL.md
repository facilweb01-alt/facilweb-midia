---
name: ig-audit
description: >-
  Análise pós-postagem do que o usuário já publicou: quais reels funcionaram de
  verdade, por quê, e o que parar de fazer. Use quando o usuário colar os
  insights ou posts antigos e perguntar "o que tá funcionando", "por que esse
  flopou", "analisa meus números", "audita meu conteúdo", ou quiser saber do que
  fazer mais. Puxa os dados sozinho quando o conector oficial da Meta estiver
  conectado.
---

# ig-audit

A única fonte honesta do que funciona para uma conta é a própria conta. Toda
regra de todo guia de Instagram, inclusive as deste pacote, é uma suposição
inicial. Os últimos 30 posts do usuário são a evidência.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
Se houver vários clientes, pergunte qual conta está sendo auditada.

## Entrada

**Se a sessão tiver o conector oficial da Meta** (ferramentas de Instagram como
`get_instagram_accounts`, `get_instagram_posts` e
`get_instagram_account_insights`), use primeiro. Liste as contas, confirme com o
usuário qual é a certa, e puxe os posts dos últimos 60 a 90 dias com as métricas
disponíveis. Isso é leitura pela API oficial e não exige nada além da permissão
que o usuário já deu. Salve os números brutos num arquivo e faça as contas em
código, não de cabeça.

**Sem conector**, peça o que o usuário tiver:

- Insights por post: views, alcance, interações, tempo de exibição,
  salvamentos, compartilhamentos, seguidores ganhos e a fatia de alcance de não
  seguidores. Print serve.
- Ou o gráfico de retenção dos melhores e piores reels recentes. Esse print
  vale mais que todo o resto junto.
- Ou só os posts e as views, que dá para uma primeira passada.

Leia também `log.md` da pasta da conta se existir, porque ele registra qual
fórmula de hook cada post usou.

## O que medir de verdade

View bruta é o número menos útil da tela, porque depende principalmente de
quantas pessoas já seguem a conta. Calcule estes e mostre a conta:

| métrica | como | o que diz |
| --- | --- | --- |
| **Múltiplo sobre a mediana** | views / mediana de views da própria conta | se foi acerto de verdade ou um dia normal |
| **Alcance de não seguidores** | % do alcance vindo de quem não segue | se viajou ou não |
| **Retenção aos 3s** | quem ficou aos 3s / quem começou | se o hook funcionou. É a nota do hook. |
| **Tempo médio de exibição** | direto dos insights | se o meio funcionou |
| **Envios por alcance** | compartilhamentos / alcance | o sinal mais forte que dá pra conquistar. Envio é alguém colocando o nome em jogo. |
| **Seguidores por alcance** | seguidores ganhos / alcance | se o perfil converteu a atenção |

Ranqueie pelo múltiplo e pelos envios por alcance, não por views. Um reel com
4 mil views e 90 envios ganhou do de 60 mil views e 11 envios.

## Depois, achar o padrão

Com os cinco de cima e os cinco de baixo lado a lado, procure o que separa os
dois grupos, e esteja disposto a concluir algo que o usuário não vai gostar:

- **Retenção aos 3 segundos.** Se os de cima e os de baixo diferem aqui, é o
  hook e nada mais, e todo o resto é distração.
- **Fórmula do hook.** Quais números do `ig-reel/hooks.json` estão no topo?
- **Formato.** Reel, carrossel, imagem única.
- **Duração.** Agrupe em menos de 15s, 15 a 30s, 30 a 60s, mais de 60s.
- **Tema.**
- **Se o usuário respondeu comentários na primeira hora.**
- **Dia e horário.** Confira isso **por último** e só se os outros não
  mostrarem nada. Quase nunca é a causa e é onde as pessoas querem que seja.

Diga o achado como afirmação com a evidência junto, e diga o quanto confia.
Com 30 posts dá pra ver padrão. Com 6 não dá, e dizer isso é melhor que
inventar um.

## A distinção que economiza meses

**Reel que tem view e não dá seguidor não é reel fracassado, é problema de
perfil.** Reel que não tem view é problema de hook. Separe os dois antes de
recomendar qualquer coisa. Se o alcance de não seguidores é alto e seguidores
por alcance é baixo, pare de reescrever hook e vá para o `/ig-profile`.

## Saída

```
AUDITORIA  ·  31 posts  ·  12/jun a 05/set  ·  mediana 4.100 views

TOP 5 POR MÚLTIPLO
  18,2x  #3  Ninguém Te Conta    74.600 views  62% não seguidores  ret@3s 71%  128 envios
   6,4x  #1  Confissão de Custo  26.300 views  48% não seguidores  ret@3s 64%   71 envios
  ...

BOTTOM 5
   0,3x  #11 Lista               1.200 views    9% não seguidores  ret@3s 31%    2 envios
  ...

O QUE OS DADOS DIZEM
1. Retenção aos 3 segundos é a história toda. Top 5 com média de 66%, bottom
   5 com 33%. Todo o resto que te preocupa vem depois dos dois primeiros segundos.
2. Os posts em que você foi quem se deu mal: média de 8,1x contra 0,9x de todo
   o resto. n=5. Sinal mais forte aqui, e nem é perto.
3. Lista de ferramentas dá view e mais nada. Muito alcance, zero envio, zero
   seguidor. Três dos seus cinco piores.
4. Dia da semana não mostra nada. Terça e sexta estão dentro do ruído. Pare de
   otimizar isso.

PARE: listas de ferramenta.
FAÇA MAIS: os que têm um custo que você pagou e um número junto.
```

Depois entregue as conclusões ao `/ig-plan`, para a próxima semana ser montada
sobre a evidência do próprio usuário e não sobre padrões, e ao `/ig-viral`,
para o swipe file ser filtrado pelas fórmulas que funcionam nesta conta.

Para cliente de agência, ofereça transformar a auditoria num relatório que ele
possa ler (documento ou slides), sem jargão e com as três decisões no topo.
