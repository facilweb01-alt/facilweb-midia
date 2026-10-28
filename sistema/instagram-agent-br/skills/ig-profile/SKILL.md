---
name: ig-profile
description: >-
  Dá nota de 0 a 100 a um perfil de Instagram numa rubrica de 12 itens e
  reescreve as partes que perdem ponto: campo de nome, bio, link, destaques,
  três fixados, grid. Use quando o usuário disser "otimiza meu perfil",
  "arruma minha bio", "dá nota no meu Instagram", "por que ninguém me segue",
  ou colar o perfil e perguntar como ele está. Bom também como diagnóstico de
  entrada para cliente novo de agência.
---

# ig-profile

Quase todo mundo otimiza a coisa errada aqui. O perfil não é uma vitrine que
as pessoas passeiam. É uma **tela de decisão**, à qual se chega por um reel, e
ela tem uns três segundos para responder uma pergunta: tem mais disso aqui, e
é pra mim?

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
Grave a nota e a data em `log.md` dessa pasta para comparar na próxima rodada.

## Entrada

Peça para colar ou printar: o campo de nome, o @, a bio, para onde vai o link,
os nomes dos destaques, o que está fixado e as nove primeiras capas do grid. Um
print do topo do perfil mais as duas primeiras linhas do grid basta para uma
primeira passada.

Se o conector oficial da Meta estiver na sessão, dá para puxar bio, link e
posts recentes da conta profissional por lá, e pedir só o que faltar (destaques
e capas costumam faltar).

Não faça login no Instagram pelo usuário.

## Dê a nota

Leia `rubric.json` nesta pasta. Doze itens, 100 pontos, cada um com como é a
nota máxima e como costuma falhar. Pontue todo item, mostre a tabela, dê o
total. Seja honesto. A maioria dos perfis cai entre 30 e 49 na primeira
passada, e nota generosa não serve pra nada.

```
NOTA DO PERFIL  38/100

  campo de nome      2/12   só o nome, nenhuma palavra que alguém busca
  bio 1ª linha       3/12   três substantivos e um emoji de café
  três fixados       0/10   nada fixado
  destaques          2/8    "Aleatório", "Vida", "2023"
  legibilidade grid  4/8    seis das nove capas são um rosto no meio da frase
  ...
```

## Depois reescreva, nesta ordem

Corrija em ordem decrescente de pontos perdidos. Não reescreva tudo de uma vez,
o usuário tem que ir lá e mudar cada coisa.

**1. O campo de nome (30 caracteres).** A linha em negrito embaixo da foto, não
o @. É o campo que a busca do Instagram compara, e a maioria das contas põe só o
nome. Formato que funciona: `{Nome} | {o que faz, em palavras buscadas}`.
Inclua a cidade quando o negócio é local ("Ana | Leilão de imóveis JP"). Dê
três opções e conte os caracteres de cada uma.

**2. A primeira linha da bio.** Pra quem é e o que muda. Não cargo, não
adjetivo, não lista de identidades separadas por barra. O resto dos 150
caracteres leva uma prova ou uma oferta direta.

**3. Os três fixados.** Três espaços, três funções: a melhor prova, a explicação
mais clara da oferta, a melhor apresentação da pessoa. É a correção de maior
alavanca do perfil inteiro e leva quatro toques. Grid sem fixado mostra o que
foi postado por último, que é cara ou coroa.

**4. Destaques.** De quatro a seis, com nome das perguntas que um comprador
faz: Preços, Resultados, Como funciona, Depoimentos, Sobre. Não "Aleatório".
Apague o resto.

**5. O link.** Um destino que combina com o que a bio acabou de prometer. São
permitidos cinco; dois já é cardápio, e cardápio converte pior que porta. Se a
venda fecha no WhatsApp, o link certo costuma ser um `wa.me` com mensagem
pronta ("Oi, vim pelo Instagram e quero saber do..."), que também mostra de onde
o lead veio.

**6. Capas do grid.** As nove primeiras em miniatura. Capa de reel é escolhida,
não deixada como o primeiro quadro. Quatro palavras de texto numa capa tornam o
grid legível numa olhada.

## Saída

Tabela de nota, depois as reescritas como blocos prontos para copiar, na ordem
de correção, cada um passado pelo `/ig-human`. Dê a nota de novo no fim e mostre
a diferença com honestidade. Se a reescrita chega a 84 e não a 98, diga 84, e
diga o que falta, que normalmente é um grid, um hábito de story e um post para
fixar que ainda não existe. Nada disso é reescrita.

Nada é salvo no Instagram por esta skill. O usuário edita cada campo.
