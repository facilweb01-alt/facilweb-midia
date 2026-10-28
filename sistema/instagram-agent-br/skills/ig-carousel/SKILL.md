---
name: ig-carousel
description: >-
  Monta um carrossel de Instagram em português: a capa que ganha o arrasto, o
  texto slide a slide e os arquivos 1080x1350 para subir. Use quando o usuário
  disser "carrossel", "slides", "post de arrastar", "transforma isso num
  carrossel", ou tiver uma ideia em formato de lista ou de passos que morreria
  como imagem única.
---

# ig-carousel

Carrossel é o formato de maior permanência no grid, porque arrastar é
interação e rolar não é. Ele também ganha uma segunda chance: o Instagram pode
mostrar o carrossel de novo, começando num slide mais adiante, para quem não
interagiu da primeira vez. Então o slide dois também tem que se sustentar
sozinho.

O formato premia uma ideia quebrada em passos. Pune legenda cortada em
pedaços.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
Leia `voice.md` e, se existir, a identidade visual do cliente (cores, fontes).

## Quando usar em vez de Reel

Use carrossel quando a ideia tem **sequência e precisa ser relida**: passos,
um método com partes, um antes e depois, uma lista que vale print. Use Reel
quando a ideia tem movimento, rosto, ou uma entrega que precisa ser vista
acontecendo.

Se a ideia é uma afirmação só, não é nenhum dos dois. Passe para o `/ig-reel`
e diga isso.

## Estrutura

De 6 a 10 slides. O limite é 20, e 20 quase sempre é um livro que ninguém
termina. Abaixo de 5 o arrasto nem começa.

```
1         CAPA       o hook. 6 palavras ou menos, num tamanho legível em
                     miniatura no grid. Uma linha de promessa embaixo.
2         O QUE ESTÁ por que isso importa, numa frase. Este slide também é uma
          EM JOGO    segunda capa, então não pode ser preparação.
3 a N     UMA IDEIA POR SLIDE. Título de 3 a 7 palavras, no máximo 25
                     palavras embaixo. Se o slide precisa de parágrafo, são dois slides.
N+1       RESUMO     tudo como lista. É o slide que vira print.
ÚLTIMO    CTA        uma ação. Salvar, comentar uma palavra, ou seguir. Uma.
```

## Regras do texto

- **A capa é 80% do resultado.** Seis palavras. Grande. Nada no resto salva
  uma capa que ninguém arrasta.
- **Pense no corte do grid.** O grid do perfil corta num retângulo em pé, e a
  proporção exata já mudou mais de uma vez. Monte em 1080x1350 e mantenha o
  texto da capa bem no meio, longe dos 120 pixels de cada borda, e o corte deixa
  de importar.
- **Numere os slides** (3/8). A conclusão sobe quando a pessoa vê o fim.
- **Nenhum slide é parágrafo.** Se não cabe em 25 palavras, divida.
- **O slide de resumo é o que as pessoas printam e mandam.** Envio é o sinal
  mais forte que existe. Faça ele se sustentar sozinho, legível sem contexto.
- **O @ em todo slide**, pequeno, no canto de baixo. Print viaja sem você.
- **Texto alternativo na capa, no mínimo.** É lido por leitor de tela e pelo
  Instagram.

## Gerando os arquivos

O Instagram quer 1080x1350 (4:5), JPEG ou PNG, até 20 itens. Monte em HTML e
exporte cada slide:

```bash
# um <section> por slide, 1080x1350, page-break-after: always
# depois Chrome headless --screenshot por slide, ou qualquer HTML-para-imagem que você já usa
```

Escreva o HTML com `width:1080px; height:1350px`, uma cor de destaque só e
fonte de no mínimo 32px, porque isso é lido num celular a um terço do tamanho
real. Se o projeto ou o cliente tem skill de marca ou design system, use, e não
invente paleta.

Confira acentuação e cedilha na fonte escolhida antes de exportar: muita fonte
decorativa não tem "ã", "ç" ou "ê", e o slide sai com quadradinho no lugar.

## Saída

Primeiro o texto slide a slide, como lista numerada que o usuário lê em dez
segundos e edita antes de qualquer coisa ser renderizada. Depois a **legenda**,
que no carrossel é o Trabalho B do `/ig-caption`: a legenda trabalha aqui,
porque a capa já usou as seis palavras.

Passe os dois pelo `/ig-human`. Gere os arquivos só depois que o usuário
aprovar o texto.

```
CARROSSEL  ·  8 slides

1  CAPA    A CLÁUSULA DE R$18 MIL
           Uma linha que hoje vai em todo contrato meu.
2  JOGO    Aprovei o trabalho. Nove dias depois pediram o dinheiro de volta.
3          O QUE ELA DIZ
           Pagamento na entrega, não na aprovação.
...
7  RESUMO  As quatro linhas, em ordem.
8  CTA     Comenta CONTRATO que eu te mando a cláusula inteira.

Legenda: Trabalho B, hook na linha 1, um pedido, 3 hashtags.
```

Nada é enviado ao Instagram por padrão. O usuário posta. Se o conector oficial
da Meta estiver na sessão e o usuário pedir explicitamente para publicar, siga
a seção "Publicação" do `/ig-caption`: prévia completa, "sim" claro, uma
publicação só.
