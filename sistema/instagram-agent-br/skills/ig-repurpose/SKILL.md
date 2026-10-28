---
name: ig-repurpose
description: >-
  Transforma um conteúdo longo (vídeo de YouTube, podcast, live, newsletter,
  post de blog, aula, ligação com cliente) numa semana de reels e carrosséis em
  português. Use quando o usuário disser "reaproveita isso", "transforma em
  reels", "tenho um vídeo/podcast/transcrição", "corta isso", ou colar algo
  longo e quiser no Instagram.
---

# ig-repurpose

Um bom conteúdo longo tem de quatro a seis posts dentro. A maioria tira um e
joga o resto fora.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.

## Entrada

Uma transcrição, um artigo, uma newsletter, um roteiro, um resumo de reunião,
uma live. Se o usuário mandar uma URL e esta sessão tiver ferramenta de
transcrição, use; senão, peça para colar. Leia tudo antes de extrair qualquer
coisa.

Se a fonte é um vídeo do próprio usuário, peça o arquivo também. Reel feito com
a filmagem dele ganha de Reel feito com as palavras dele lidas de novo.

## Extraia, não resuma

Resumo de vídeo não é Reel. Ninguém quer o resumo. Percorra o conteúdo e tire
as coisas que se sustentam sozinhas:

| tirar | o que é |
| --- | --- |
| **Afirmações** | toda frase que começaria uma discussão |
| **Números** | todo valor, custo, duração, porcentagem |
| **Histórias** | todo momento com uma pessoa, uma cena e um custo |
| **Mecanismos** | todo "o jeito que isso funciona de verdade é..." |
| **Erros** | toda admissão de algo que deu errado |
| **Frases** | toda frase que já é citável do jeito que está |

Liste o que encontrou, com contagens, antes de escrever qualquer coisa. Se o
conteúdo rende menos de quatro itens, ele é ralo, e quatro posts espremidos
dele também vão ser. Diga isso.

## Depois escolha o formato de cada extração

Nem tudo é Reel.

- **Afirmação, erro, história** viram Reel. Precisam de voz e de rosto.
- **Mecanismo, lista numerada** viram carrossel. Precisam ser relidos.
- **Frase citável** vira quadro de story, não post.

## Depois monte a semana

Cada extração vira um post e cada post se sustenta sozinho. O espectador não
viu a fonte e nunca vai ver. Nunca escreva "como eu falei no meu último vídeo".
O post é a coisa.

Atribua uma fórmula de hook do `ig-reel/hooks.json` a cada um e varie. Cinco
posts de uma fonte com o mesmo formato de hook parece fábrica de conteúdo,
porque é.

Se a fonte é vídeo do próprio usuário, **use a filmagem de verdade**. O trecho
em que ele disse a coisa, com a reação real, ganha de regravar sempre. Corte na
frase, não na respiração.

Ordene a semana para a afirmação mais forte ir primeiro, a história cair no meio
e o mecanismo ir por último, quando quem gostou dos anteriores está esperando.

## Saída

```
FONTE: "Por que a gente acabou com a reunião de diagnóstico" (podcast de 42 min, 8.900 palavras)

ACHEI  5 afirmações, 9 números, 3 histórias, 4 mecanismos, 2 erros, 7 frases citáveis

SEMANA
TER  REEL       #2  Comando Negativo  Pare de fazer reunião de diagnóstico
                                      use o trecho em 14:20, ele ri no final
QUA  CARROSSEL  Legenda Trabalho B    O formulário de 4 perguntas que substituiu a reunião
SEX  REEL       #21 Começo no Meio    "...e nove dias depois ele pediu reembolso"
DOM  REEL       #5  Colapso de Tempo  Seis horas por semana de volta, um link apagado

Diga "escreve terça" e eu faço o rascunho.
```

Depois escreva sob pedido, um de cada vez, cada um passando pelo `/ig-reel` e
pelo `/ig-human`. Não despeje quatro roteiros prontos de uma vez. Vão soar
todos iguais e o usuário não vai gravar nenhum.
