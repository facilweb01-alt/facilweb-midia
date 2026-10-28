---
name: ig-plan
description: >-
  Monta a semana no Instagram: o que postar, em qual formato, quando, e com
  quem engajar. Use quando o usuário disser "planeja minha semana", "o que eu
  posto", "calendário de conteúdo", "não tenho sobre o que postar", ou quiser
  um cronograma de postagens e uma lista de engajamento. Funciona para uma
  conta ou para a carteira de clientes de uma agência.
---

# ig-plan

A sala de controle. Todo o resto do pacote executa; esta decide o que vai ser
executado. Rode uma vez por semana, sempre no mesmo dia.

## Pasta da conta

Conta única: `~/.claude/instagram/`. Agência: `~/.claude/instagram/clientes/<cliente>/`.
Para agência, rode um plano por cliente e, se pedirem, um resumo da carteira no
fim (cliente, posts da semana, o que depende de aprovação do cliente).

## Entrada

Se existirem `voice.md`, `swipe.md` e `log.md` na pasta da conta, leia. O swipe
file é a evidência do próprio usuário, vinda do `/ig-viral`, sobre quais
fórmulas estão funcionando no nicho agora, e vale mais que qualquer coisa neste
arquivo. O log impede que o plano repita um tema das últimas duas semanas.

Se não existirem, peça quatro coisas e anote:

1. O que o usuário vende, e para quem.
2. Os três ou quatro temas pelos quais quer ser conhecido.
3. O que aconteceu de verdade nesta semana: uma ligação de cliente, um número,
   um erro, algo que construiu, uma discussão que teve. É daí que vêm os posts.
4. Dez contas para as quais vale ser visto.

## O que postar

De quatro a cinco posts por semana, pelo menos três deles Reels. Reel é o único
formato do Instagram que alcança com regularidade quem não segue a conta.
Carrossel aprofunda com quem já segue. Story é diário e é planejado à parte.

Misture ao longo da semana, nunca dois do mesmo tipo seguidos:

| tipo | quantidade | função |
| --- | --- | --- |
| **Prova** | 1 por semana | algo que aconteceu, com número. Reel. |
| **Ensino** | 1 a 2 por semana | uma coisa que o espectador faz hoje. Reel ou carrossel. |
| **Opinião** | 1 por semana | uma posição que pode custar seguidores. Reel. |
| **História** | 1 a cada 15 dias | uma cena com um custo. Reel. |
| **Oferta** | 1 a cada 15 dias | o que você vende, dito com clareza, sem pedir desculpa. Carrossel ou stories. |

Para cada espaço dê: o tema, o ângulo específico vindo do que aconteceu nesta
semana, o formato e o número da fórmula de hook do `ig-reel/hooks.json`. Não um
assunto, um ângulo. "Leilão" não é plano. "O apartamento que quase me custou
R$23 mil de condomínio atrasado" é um Reel.

## Datas do calendário brasileiro

Confira se a semana tem data que muda o comportamento do público: feriado
nacional ou local, Black Friday, Dia das Mães, Dia dos Namorados (12/6), volta
às aulas, 13º salário, IPTU, pagamento quinzenal. Use quando a data dá um
ângulo real ao tema do cliente; ignore quando seria forçado. Delivery em véspera
de feriado é ângulo; "feliz Dia do Contador" de uma conta de leilão não é.

## Quando postar

Poste quando o público está acordado e fora do trabalho. Para a maioria dos
públicos de consumo, é começo da noite no horário local; para público de
negócios, começo da manhã. Para restaurante e delivery, antes da fome: fim da
manhã e fim da tarde.

Mas diga com clareza: **o horário importa muito menos que os dois primeiros
segundos.** O Instagram continua mostrando um Reel por dias se ele performa, e
enterra um bem cronometrado que não performa. Se o usuário está otimizando
horário antes de os hooks funcionarem, está polindo a coisa errada, e você
deve dizer isso.

Use o fuso do público, não o do usuário, se forem diferentes. No Brasil isso
importa fora do horário de Brasília: Amazonas, Roraima, Rondônia, Mato
Grosso e Mato Grosso do Sul ficam uma hora atrás, e o Acre duas.

## A rodada de engajamento, que não é opcional

20 minutos por dia, antes de postar, não depois. Monte uma lista de 10:

- **5 de alcance**: contas com o público que o usuário quer, onde um bom
  comentário é visto. Comente cedo, antes de o fio ter 200 comentários.
- **3 pares**: mesmo tamanho, mesma área. É o grupo que retribui.
- **2 compradores**: gente que pode comprar de verdade. Comente por semanas
  antes de qualquer direct, e nunca venda em comentário.

Passe a lista para o `/ig-comment`.

## Saída

```
SEMANA DE 15/SET

SEG  só engajamento  (20 min, lista abaixo)
TER  19h30  REEL       PROVA    #5  Colapso de Tempo  - orçamento de 5h para 20 min
QUA  só stories + engajamento
QUI  19h00  CARROSSEL  ENSINO   Legenda Trabalho B    - as 4 cláusulas, uma por slide
SEX  19h30  REEL       OPINIÃO  #2  Comando Negativo  - pare de fazer reunião de diagnóstico
SÁB  -
DOM  18h00  REEL       HISTÓRIA #21 Começo no Meio    - o e-mail de reembolso

STORIES  todo dia, de 3 a 5 quadros, caixa de pergunta na quinta.

ENGAJAR  (5 alcance / 3 pares / 2 compradores)
  ...

Diga "escreve terça" e eu faço o rascunho.
```

Grave o plano em `plan.md` na pasta da conta para as outras skills lerem. Nada
é agendado nem postado em lugar nenhum. É um plano, e o usuário executa.
