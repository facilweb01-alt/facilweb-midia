# Modelos prontos: publicação automática, conferência e pesquisa

## 1. Prompt da tarefa agendada de PUBLICAÇÃO (uma por post)
Crie com a ferramenta de tarefa agendada (execução única, `run_once_at` em UTC; Brasília = UTC-3).
Nome: "Instagram <@conta>: <tipo> <dd/mm> <hh>h"

```
Responda em português do Brasil. Tarefa: publicar no Instagram <@conta> o <tipo> "<título>", APROVADO
explicitamente por <cliente> em <data>. Publique exatamente o que está abaixo, sem alterar nada.

Use a ferramenta da integração Meta Ads `publish_instagram_media` com:
- instagram_user_id: <ID>
- media_type: <IMAGE | CAROUSEL | REELS | STORIES>
- share_to_feed: true            (só REELS)
- skip_if_recently_published: true
- image_url / video_url / children: <URLs públicas JPEG/MP4>
- cover_url: <capa JPEG>         (só REELS)
- caption (exatamente este texto, com as quebras de linha):
<legenda aprovada>

Se a ferramenta pedir account_id, use <act_...>.

Regras: publique uma única vez. Se falhar, NÃO tente outro caminho, não use navegador e não altere o
conteúdo: informe a <cliente> o erro exato e como publicar manualmente (arquivo e legenda). Ao final,
informe o link do post publicado.
```

## 2. Prompt da tarefa de CONFERÊNCIA (20 min depois de cada post do feed)
```
Responda em português do Brasil. Tarefa: conferir se o <tipo> publicado hoje (<data>, por volta das <hh>h
de Brasília) no Instagram <@conta> saiu com a legenda certa. Somente leitura: NÃO publique, não apague e
não altere nada.
1. `get_instagram_posts` com instagram_account_id <ID>, account_id <act_...>, time_range last_7d.
2. Ache o post e compare a legenda com a esperada:
<legenda>
3. Igual: termine em silêncio. Diferente ou sem legenda: avise <cliente> com o link e a legenda pronta para
colar (3 pontinhos > Editar). Não apareceu: avise que não foi publicado e qual tarefa olhar.
```
Story não tem legenda: não precisa de conferência.

## 3. Prompt da tarefa SEMANAL de planejamento (recorrente, ex.: quinta 8h56)
```
Responda sempre em português do Brasil. Você cuida do Instagram <@conta> (<negócio>). Tarefa semanal:
montar a semana seguinte, mostrar para aprovação e, só depois do OK explícito, agendar tudo.
1. Clone <repositório>. Leia OPERACAO.md, conta/voice.md, conta/plan.md, conta/log.md.
2. Puxe os posts da última semana (get_instagram_posts) e registre as métricas em conta/log.md.
3. Monte 3 a 4 posts no feed + stories, com artes do kit (design3d/ e video/), logo em toda peça,
   legendas aprovadas pelos linters (caption.py PRONTA, detect.py APROVADO 70+, hookscore 70+).
4. Mostre prévia, legendas e calendário. NÃO publique nem agende sem aprovação explícita.
5. Aprovado: suba os arquivos, confira as URLs, crie as tarefas de publicação e de conferência.
```

## 4. Pesquisa de concorrência (Biblioteca de Anúncios da Meta)
1. Abra no navegador: `https://www.facebook.com/ads/library/?active_status=active&ad_type=all&country=BR&q=<termo>&media_type=all`
   com termos do nicho (ex.: "sistema para delivery", "cardápio digital", "<concorrente>").
2. Leia a página (texto da página, não print). Anúncios ativos há mais tempo e com várias versões são os que
   estão dando resultado: anote o gancho, a oferta, o formato (vídeo, carrossel), a chamada e há quanto tempo
   estão no ar.
3. No Instagram dos 3 a 5 concorrentes, veja os 12 últimos posts: quais formatos têm mais comentários e
   visualizações. Instagram trava abas com facilidade: se travar, não insista, use a biblioteca de anúncios e
   uma busca na web.
4. Registre em `pesquisa-concorrencia.md`: tabela de ganchos com dor + número, ofertas, formatos, lacunas que
   ninguém está ocupando, e 10 ganchos adaptados para a marca (nota 70+ no hookscore).

## 5. Estrutura da estratégia de crescimento e vendas (documento)
1. Diagnóstico: seguidores, alcance médio, posts com melhor resultado, nota do perfil (bio, link, destaques).
2. Público e dores, em palavras do cliente.
3. Posicionamento: a frase que diferencia (ex.: "sem comissão por pedido").
4. Pilares de conteúdo (4): ensino (resolve uma dor), prova (cliente real, tela real), bastidor/produto,
   opinião (tira o público do muro).
5. Funil: gancho → conteúdo → palavra-chave nos comentários (ex.: QUERO) → direct com a entrega → demonstração
   → venda. Responder todo comentário na primeira hora.
6. Ritmo: 3 a 4 posts no feed por semana, stories nos dias de post, reels de 15 a 30 s.
7. Metas de 30 dias e o que medir: alcance de não seguidores, salvamentos, envios, comentários com a
   palavra-chave, conversas no direct, demonstrações marcadas.
8. Calendário da primeira semana com ganchos prontos.
