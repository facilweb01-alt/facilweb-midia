# Instagram Agent BR

Treze skills para o Claude operar uma conta de Instagram **em português do
Brasil**. Adaptação da [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill)
de Jake Schincariol (MIT), com os scripts, o léxico e as 26 fórmulas de hook
reescritos para a fala brasileira, suporte a várias contas (agência) e ao
conector oficial da Meta.

Uma skill escreve seu Reel a partir de 26 fórmulas de hook e dá nota ao hook
antes de você gastar um take. Outra vai atrás dos reels que estão funcionando no
seu nicho e ranqueia pelo quanto cada um superou a própria conta. Outra escreve
a legenda e mostra exatamente o que o feed mostra antes do "... mais". Outra dá
nota de 0 a 100 ao perfil e reescreve o que perdeu ponto. Outra planeja a
semana.

E uma é o humanizador, que é o motivo de o resto ser usável. Ela tira os
travessões, os clichês de IA em português ("é crucial", "no mundo de hoje",
"alavancar seus resultados") e os caracteres invisíveis de um rascunho, e dá
nota num painel de cinco checagens antes de você ver.

**Nada é postado sem você dizer sim.** As skills escrevem. Você posta.

## Por que existe uma versão BR

A versão original foi feita para inglês. Testada com texto em português, ela
quebrava nos pontos que importam:

| teste em português | original | esta versão |
| --- | --- | --- |
| "Perdi R$18.000 por causa de uma cláusula..." | 60 OK | **81 FORTE** |
| "Ninguém te conta que seus primeiros 30 reels vão flopar." | 40 FRACO | **81 FORTE** |
| "Pare de postar três vezes por dia." | 30 FRACO | **80 FORTE** |
| "Oi gente, hoje eu queria falar sobre..." (hook ruim) | 30, sem alerta | **10 FRACO + alerta de saudação** |
| Legenda humana bem escrita | 57 REVISAR (falso alarme) | **94 APROVADO** |
| Texto típico de IA | 28, 1 troca | **23 SINALIZADO, 10 trocas, 4 tiques** |
| Humanizar "é crucial verificar" | "é **important** verificar" (inglês no meio) | "precisa verificar" |
| "Comenta EDITAL que eu te mando" | 0 pedidos | 1 pedido (palavra-chave) |

No original, um hook bom e um hook ruim em português tiravam a mesma nota.

## Instalação

No Claude Code, como plugin a partir da pasta (ou de um repositório seu):

```
/plugin marketplace add ./instagram-agent-br
/plugin install instagram-agent-br
```

Ou copiando as skills:

```bash
cp -r instagram-agent-br/skills/ig-* ~/.claude/skills/
```

No app do Claude, cada pasta de `skills/` pode ser enviada como skill (zipe a
pasta da skill com o `SKILL.md` na raiz). Sem os scripts Python, `/ig-reel` e
`/ig-human` perdem a maior parte do valor; o resto funciona só com as
instruções.

Não instale junto com o pacote original em inglês: os comandos têm os mesmos
nomes (`/ig-reel` etc.).

Depois, gaste dez minutos no `templates/voice.md`.

## Uma conta ou várias (agência)

Todas as skills leem e gravam numa **pasta da conta**:

```
~/.claude/instagram/                     conta única
~/.claude/instagram/clientes/<cliente>/  uma pasta por cliente
    voice.md     a voz da conta (preencha primeiro)
    swipe.md     o que funciona no nicho, escrito pelo /ig-viral
    log.md       histórico de posts e notas, usado pelo /ig-audit
    plan.md      a semana, escrita pelo /ig-plan
```

Com mais de um cliente, a skill pergunta de qual conta é o trabalho antes de
começar. Um roteiro na voz do cliente errado é o erro mais caro que dá pra
cometer aqui.

## As treze

| comando | o que faz |
| --- | --- |
| `/ig-reel` | Uma ideia vira Reel. Três hooks de [26 fórmulas](skills/ig-reel/hooks.json), com nota, depois o roteiro, o texto de tela e o beat sheet cronometrado. |
| `/ig-viral` | Vai atrás do que funciona no nicho, ranqueia pelo múltiplo sobre a mediana de cada conta, nomeia a fórmula, escreve o swipe file. |
| `/ig-caption` | A legenda, revisada. Mostra os 125 caracteres que o feed mostra antes do toque. |
| `/ig-carousel` | Carrossel. A capa que ganha o arrasto, o texto dos slides e os arquivos 1080x1350. |
| `/ig-story` | A sequência do dia, qual figurinha faz o quê, e o funil de direct que começa com a pessoa se mexendo primeiro. |
| `/ig-profile` | Nota do perfil numa [rubrica de 12 itens](skills/ig-profile/rubric.json) de 0 a 100, e reescrita na ordem de correção. |
| `/ig-plan` | A semana. O que postar, formato, quando, e as 10 contas para engajar. Com datas do calendário brasileiro. |
| `/ig-human` | O humanizador. Dois scripts que rodam. Veja abaixo. |
| `/ig-comment` | Comentário em post dos outros. Nove tipos, escolhidos pelo que o post é. Nunca "🔥🔥🔥". |
| `/ig-reply` | O fio embaixo do seu post. Separa em palavra-chave / lead / substância / pergunta / apoio / ruído, e responde nessa ordem. |
| `/ig-dm` | A entrega da palavra-chave, a primeira mensagem, o pitch de collab, a passagem para o WhatsApp e os dois follow-ups. Dois. |
| `/ig-repurpose` | Um vídeo, podcast ou newsletter vira uma semana de reels e carrosséis independentes. |
| `/ig-audit` | Análise do que já foi postado. Ranqueia por múltiplo e envios por alcance, não views. Puxa os dados sozinho pelo conector da Meta. |

## As ferramentas que rodam

Sem dependências, sem rede, nada enviado. Rodam na sua máquina, no seu texto.

### Hooks

```bash
python3 skills/ig-reel/hookscore.py hooks.txt            # ranqueia suas opções
python3 skills/ig-reel/beats.py roteiro.txt --target 30  # cronometra antes de gravar
```

```
RANKING DE HOOKS
==============================================================================
->  81.4 FORTE  Perdi R$18.000 por causa de uma cláusula que faltou no cont...
        mais fraca: ALVO (70)
    81.4 FORTE  Ninguém te conta que seus primeiros 30 reels vão flopar.
        mais fraca: TENSÃO (70)
    80.2 FORTE  Pare de postar três vezes por dia.
        mais fraca: TENSÃO (70)
    13.2 FRACO  Nesse vídeo eu vou te mostrar como arrematar imóvel em leilão
        mais fraca: ABERTURA (0)
        eliminatório: Preâmbulo de vídeo. Apague e abra direto na entrega.
     9.6 FRACO  Oi gente, hoje eu queria falar sobre estratégia de conteúdo
        mais fraca: ABERTURA (0)
        eliminatório: Saudação. Ninguém abriu o feed pra ser cumprimentado.
```

O `beats.py` usa 150 palavras por minuto por padrão (fala brasileira natural;
o original usava 165, calibrado para inglês) e aponta hook acima de 3 segundos,
beat parado, sequência sem nada concreto e falta de loop.

### A legenda

```bash
python3 skills/ig-caption/caption.py legenda.txt --keywords "leilão de imóveis,edital"
```

```
  O QUE O FEED MOSTRA
  +------------------------------------------------------+
  | Arrematei um apartamento em João Pessoa por 52% do   |
  | valor de avaliação, e quase perdi tudo por não ler   |
  | o edital.                                            |
  +-------------------------------------------- ... mais +

  OK     1ª LINHA         112 caracteres, aparece inteira
  FALHA  HASHTAGS         6 hashtags, acima do limite de 5 do Instagram
  OK     UM PEDIDO        uma chamada para ação: comentar palavra-chave
  ALERTA TERMOS DE BUSCA  1/2 presentes. Faltando: leilão de imóveis
```

Entende os pedidos brasileiros ("comenta EDITAL", "me chama no direct",
"chama no whats", "salva esse post", "link na bio"), domínios `.com.br` e
`wa.me`, e compara termos de busca sem acento.

### O humanizador

```bash
python3 skills/ig-human/humanize.py rascunho.txt --report   # limpa e mostra cada troca
python3 skills/ig-human/detect.py rascunho.txt               # nota em cinco checagens
python3 skills/ig-human/detect.py antes.txt depois.txt       # prova a diferença
```

O léxico ([`slop.json`](skills/ig-human/slop.json)) tem 96 palavras e 95
expressões em português, com flexão de gênero e número ("robusta" vira "sólida",
não "sólido"), e 17 tiques estruturais ("não é só X, é Y", "o resultado?",
"você sabia que", "nesse vídeo eu vou te mostrar", "segue pra mais").

Novidade em relação ao original: entradas com `"replace": null` **só são
sinalizadas**. Palavras como "estratégico", "navegar" ou "virar a chave" mudam
de sentido conforme a frase, e trocar automaticamente estragaria o texto. Elas
voltam no relatório para reescrita.

A checagem de VOZ foi refeita: em vez de contar contrações do inglês ("don't"),
mede marcas de oralidade brasileira ("pra", "tá", "a gente", "né", "aí") e
pessoa gramatical.

### O swipe file

```bash
python3 skills/ig-viral/swipe.py coletado.tsv --out ~/.claude/instagram/swipe.md
```

Aceita colunas em português (`conta`, `seguidores`, `mediana`, `views`,
`hook`), ranqueia pelo múltiplo sobre a mediana e nomeia a fórmula com regex
para fala brasileira.

## Testes

```bash
python3 tests/run_tests.py
```

60 casos em português: hooks fortes e fracos, os 26 exemplos das fórmulas
classificando na própria fórmula, frases comuns que não devem virar fórmula,
humanização sem inserir inglês nem deixar pontuação órfã, texto humano
aprovado e texto de IA sinalizado, revisão de legenda e loop do beat sheet.
Rode depois de editar o léxico ou as fórmulas.

## Conector oficial da Meta (opcional)

Se a sessão do Claude tiver o conector da Meta com as ferramentas de
Instagram:

- `/ig-audit` e `/ig-profile` puxam posts e métricas da conta profissional pela
  API oficial, em vez de pedir prints.
- `/ig-caption` e `/ig-carousel` podem publicar pela API oficial de publicação,
  **só com pedido explícito**, depois de mostrar a prévia completa e receber um
  "sim, publica" na conversa. Uma publicação por vez, nunca em lote, nunca por
  iniciativa própria.

Sem o conector, tudo funciona do jeito original: você cola os dados e posta à
mão.

## As letras miúdas, que são a parte honesta

**Automação de navegador para postar, comentar, seguir ou mandar direct viola
os [Termos de Uso do Instagram](https://help.instagram.com/581066165581870) e
bloqueia conta.** Este pacote nunca faz isso. A única publicação possível é
pela API oficial, com sua aprovação a cada post.

**Resposta automática por palavra-chave no direct** é permitida pelas
ferramentas do próprio Instagram e por parceiros aprovados, e só dispara depois
que a pessoa comentou. Direct em massa para quem não interagiu não é.

**`/ig-viral` lê, não raspa.** Dez contas, uma dúzia de reels cada, em
velocidade humana, com você conduzindo o seu navegador. Nunca pede senha.

**O avaliador de hook pega hook ruim e não escolhe o vencedor.** No teste do
autor original (74 hooks reais em inglês), ele separou hook real de hook ruim
com AUC 0,83, mas separou acerto de erro do mesmo criador com AUC 0,56, quase
cara ou coroa. Esta versão aplica a mesma lógica ao português e passa nos
testes acima, mas ainda não foi medida contra um corpus grande de reels
brasileiros. Use para matar hook fraco antes de gravar e confie no gráfico de
retenção para o resto.

**As cinco checagens de detecção são heurísticas locais**, não GPTZero,
Originality, Copyleaks, Winston ou Turnitin. Ninguém pode prometer
"indetectável" com honestidade.

**Nada aqui inventa.** Nenhum número, cliente ou resultado inventado vai com o
nome de ninguém. Se falta um número, o rascunho volta com `{{seu número}}`.

**Números de plataforma envelhecem.** O limite de hashtags caiu de 30 para 5 em
dezembro de 2025. Se algo aqui contradiz o que o Instagram faz quando você ler,
o Instagram está certo.

## Arquivos

```
skills/ig-reel/hooks.json          26 fórmulas de hook em PT-BR: modelo, exemplo, versão de tela,
                                   pra que serve, como estraga, e regex para fala brasileira
skills/ig-reel/hookscore.py        o painel de cinco propriedades do hook
skills/ig-reel/beats.py            roteiro para beat sheet cronometrado
skills/ig-caption/caption.py       a prévia do corte e o revisor de legenda
skills/ig-human/slop.json          o léxico: 96 palavras, 95 expressões, 18 invisíveis, 17 tiques
skills/ig-human/humanize.py        as três passadas de limpeza
skills/ig-human/detect.py          o painel de cinco checagens
skills/ig-viral/swipe.py           ranking por múltiplo e classificação de fórmula
skills/ig-profile/rubric.json      a nota de 100 pontos do perfil
templates/voice.md                 a voz da conta. Preencha primeiro.
tests/run_tests.py                 60 testes de regressão em português
```

## Créditos e licença

Original: Jake Schincariol, [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill).
Adaptação para português do Brasil: Marcelo, Fácil Web.

MIT. Veja `LICENSE`, que mantém o aviso de copyright original.
