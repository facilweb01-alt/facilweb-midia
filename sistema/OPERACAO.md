# Operação semanal do Instagram @facilweb

Este arquivo é lido pela tarefa agendada que roda toda quinta. Responda sempre
em português do Brasil.

## Contas e IDs

- Instagram: @facilweb, `instagram_user_id` = 17841448285791740
- Conta de anúncios usada para rotear o conector da Meta: act_1140642248391947
- Hospedagem pública das artes: este repositório,
  `https://raw.githubusercontent.com/facilweb01-alt/facilweb-midia/main/<pasta>/<arquivo>.jpg`

## Regras fixas (não negociáveis)

1. **Toda arte leva a logomarca** (`sistema/logo.png`) num selo branco. Sem logo, não sai.
2. **Nada é publicado sem a aprovação explícita do Marcelo na conversa.** A
   aprovação vale para o pacote da semana mostrado a ele, e só para ele.
3. Publicar só pela API oficial (`publish_instagram_media`), nunca por navegador.
4. Nada inventado: número, cliente ou resultado só se estiver em `conta/voice.md`
   ou se o Marcelo informar.
5. Toda legenda passa por `instagram-agent-br/skills/ig-caption/caption.py`
   (veredito PRONTA) e por `ig-human/detect.py` (APROVADO, nota 70+).

## Limites da API

- Imagens em JPEG, num endereço público. Carrossel de 2 a 10 itens.
- Stories saem sem figurinhas (enquete, link, menção): cada story funciona sozinho.
- Reel precisa do vídeo editado enviado pelo Marcelo. Sem vídeo, não entra.

## Fluxo da semana

1. Ler `conta/voice.md`, `conta/plan.md`, `conta/log.md` e as skills em
   `instagram-agent-br/skills/` (principalmente ig-plan, ig-carousel, ig-caption, ig-human).
2. Montar a semana seguinte (segunda a domingo): 3 a 4 posts no feed, stories nos
   dias de post, CTA com palavra-chave DEMO. Horários: 9h30 ou 15h (horário de Brasília).
3. Gerar as artes com `gerar_artes_modelo.py` como base (mesma identidade:
   azul #0A3D9E, verde #8DC63F, laranja #F7941D, fonte Poppins, logo no selo).
   Carrossel 1080x1350, stories e capas 1080x1920. Exportar em JPEG.
4. Enviar ao Marcelo: prévia das artes, legendas e o calendário com horários.
5. Esperar a aprovação. Se pedir ajuste, ajustar e mostrar de novo.
6. Aprovado: commitar os JPEGs em `AAAA-MM-DD/` (data do post), dar push, conferir
   que cada URL pública responde, e criar uma tarefa agendada de execução única
   para cada publicação, no horário do calendário, com a URL, o tipo de mídia e a
   legenda exata. Usar `skip_if_recently_published: true`.
7. Atualizar `conta/plan.md` e `conta/log.md` e commitar.
