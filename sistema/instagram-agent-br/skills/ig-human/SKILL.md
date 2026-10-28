---
name: ig-human
description: >-
  Tira a impressão digital de máquina de qualquer rascunho em português:
  travessões, clichês de IA ("é crucial", "no mundo de hoje", "alavancar"),
  caracteres invisíveis, e dá nota num painel de cinco checagens antes de sair.
  Use sempre que um texto precisar soar humano, quando o usuário disser
  "humaniza", "isso parece IA?", "tira os travessões", "tá com cara de
  ChatGPT", ou antes de mostrar qualquer legenda, roteiro, comentário,
  resposta ou DM.
---

# ig-human

Duas ferramentas moram nesta pasta e as duas rodam. Use. Não avalie no olho.

```bash
python3 humanize.py rascunho.txt --report        # limpa e mostra o que mudou
python3 detect.py rascunho.txt                   # nota em cinco checagens
python3 detect.py antes.txt depois.txt           # prova a diferença
```

As duas leem `slop.json`: um léxico em **português do Brasil** com palavras e
expressões prontas e suas trocas, 18 classes de caracteres invisíveis, 11
trocas tipográficas e 17 tiques estruturais. O fim de cada lista é específico
de Instagram, o vocabulário que só aparece em legenda e locução ("para de rolar
o feed", "segue pra mais", "ativa o sininho", "marca alguém que precisa ver
isso"). O arquivo é feito para ser editado. Se o cliente usa de verdade uma
palavra que o léxico troca, tire do arquivo.

O léxico tem três tipos de entrada:

- `"replace": "texto"`: troca automática ("robusta" -> "sólida").
- `"replace": ""`: apaga ("vale ressaltar que").
- `"replace": null`: **só sinaliza**. São palavras ambíguas ("estratégico",
  "navegar", "virar a chave") em que a troca automática estragaria a frase.
  Essas voltam no relatório para você reescrever.

Não use este léxico em texto em inglês: ele troca por palavras em português.

## Por que isso importa mais no Instagram do que parece

Legenda é curta e roteiro é falado em voz alta. Uma linha com cara de texto
escrito numa legenda de 600 caracteres pesa mais do que a mesma linha num
artigo, e uma locução que ninguém falaria naturalmente aparece no primeiro
take. O sinal aqui não é um detector marcando o post. É uma pessoa passando
reto por algo que parece marca, ou um criador tropeçando no próprio roteiro.

## O que é corrigido automaticamente

**1. Caracteres invisíveis.** Zero-width, word joiner, hífen suave, BOM,
caracteres de tag Unicode, separadores invisíveis, espaços não separáveis e
estreitos. Teclado não produz isso. Sobrevivem ao copiar e colar e são a coisa
mais mecânica em texto gerado. O `humanize.py` apaga todos, inclusive qualquer
caractere de formatação Unicode que ele não conheça pelo nome.

**2. Tipografia.** Travessão vira vírgula, meia-risca vira hífen, aspas curvas
viram retas, reticências viram três pontos, marcador vira hífen. O travessão é
o que mais pesa: vira vírgula e depois a pontuação dupla que sobra é limpa.

**3. O léxico.** "crucial", "robusto", "alavancar", "potencializar", "no mundo
de hoje", "é importante ressaltar que", "desempenha um papel fundamental",
"divisor de águas", "conteúdo de valor", mais o bloco de Instagram. Trocados
por palavra simples ou apagados, preservando maiúsculas, flexão de gênero e
número, e sem tocar em URL.

## O que NÃO é corrigido automaticamente

Os tiques estruturais são **sinalizados, não reescritos**, porque mudar o
formato de uma frase pede julgamento:

- "Não é só X, é Y" e "não só X, mas também Y"
- "Não é sobre X. É sobre Y."
- Trincas (regra de três)
- Pergunta retórica numa linha só: "O resultado?"
- O preâmbulo: "nesse vídeo eu vou te mostrar"
- Abertura "Você sabia que..."
- Lista com emoji no lugar do marcador
- Três palavras gritadas seguidas
- Parede de hashtags (6 ou mais)
- Isca de seguir ou marcar: "segue pra mais", "marca aquele amigo que"

Essa lista é trabalho seu. Reescreva cada linha sinalizada à mão, mantendo o
sentido, e rode o `detect.py` de novo. É isso que leva a nota de REVISAR para
APROVADO, e é a parte que script nenhum faz.

## As cinco checagens

O `detect.py` dá nota de 0 a 100 em cinco sinais; maior é mais humano:

| checagem | o que mede | cara de máquina |
| --- | --- | --- |
| VARIAÇÃO | variação no tamanho das frases | toda frase do mesmo tamanho |
| CONCRETUDE | números, nomes, valores em R$ a cada 100 palavras | substantivo abstrato, sem número |
| CLICHÊS | ocorrências do léxico a cada 100 palavras | vocabulário pronto |
| DIGITAL | invisíveis, travessões, aspas curvas a cada mil caracteres | tipografia perfeita demais |
| VOZ | marcas de oralidade ("pra", "tá", "a gente", "né"), pessoa gramatical, tiques | nenhuma oralidade, revelações encenadas |

A VOZ é a principal diferença em relação ao original em inglês: português não
tem contração tipo "don't", então o sinal de fala humana é a oralidade
brasileira e o uso de "eu", "você", "a gente".

O veredito pesa a média em 60% e a **checagem mais fraca** em 40%, porque basta
um sinal. APROVADO precisa de 70+ no geral e nenhuma checagem abaixo de 55.

## Diga isso com honestidade

São cinco heurísticas locais inspiradas nos sinais que detectores públicos
usam. Rodam inteiramente na máquina do usuário e nada é enviado. **Não** são
GPTZero, Originality, Copyleaks, Winston nem Turnitin, não chamam essas APIs e
não prometem o veredito delas. Corrigir o que elas medem costuma mexer nesses
números, porque medem as mesmas coisas por baixo. Essa é a afirmação. Não faça
uma maior em nome do usuário, e nunca diga que um texto é "indetectável".

## Ordem das operações

1. `humanize.py rascunho.txt -o limpo.txt --report`
2. Leia os termos sinalizados e os tiques estruturais. Reescreva essas linhas.
3. `detect.py rascunho.txt limpo.txt` para mostrar antes e depois.
4. Se não deu APROVADO, corrija a checagem mais fraca indicada na saída e rode
   de novo. Duas rodadas é normal. Cinco quer dizer que o rascunho foi escrito
   por fórmula, e a solução é outro rascunho, não mais passadas.
5. Mostre ao usuário o texto limpo e a nota. Nunca só a nota.
