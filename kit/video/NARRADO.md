# Reel narrado com celular 3D (padrão Nutriforma, nov/2026)

Reel 9:16 de 15 a 30 s com:
- narração feminina neural (Azure, grátis);
- cenas reais de banco (Pexels) com a mesma gradação de cor;
- celular 3D mostrando as telas reais do app, com cartões que entram no tempo da fala;
- legenda grande palavra a palavra, com palavras-chave na cor de destaque;
- final com a marca e, quando for oferta, um cartão animado com a chamada.

Foi o formato aprovado para os reels 1 a 12 e para os tutoriais do Nutriforma. Tudo fica em `kit/video/narrado/`.

## Pasta de trabalho
```
trabalho/
  broll/raw/<clip>.mp4      vídeos de banco (nome curto: salada, mercado1, fotoprato…)
  broll/usados.txt          clipes que já foram ao ar (regra: cada cena de banco entra UMA vez)
  estados/<tela>.png        prints reais do app (1080 de largura; a tela rola de y0 a y1 dentro do celular)
  marca/logo.png            símbolo da marca (fundo transparente) · marca/trio.png (3 celulares do final, opcional)
  r1/voz.ssml               narração com <bookmark mark="sN"/> no início de cada cena
  r1/reel.json              roteiro (copie kit/video/narrado/exemplo/reel.json)
```

## 1. Roteiro e narração
- Escreva a fala primeiro, frases curtas, de 1 a 2 por cena. Gancho de dor ou curiosidade nos 2 primeiros segundos. Final: nome da marca + uma linha.
- SSML: voz `pt-BR-FranciscaNeural`, `<prosody rate="+6%">`, `<break time="200ms"/>` entre frases, `<bookmark mark="s1"/>` … `sN` (cena N começa no bookmark N).
- Pronúncia: `<sub alias="uótsap">WhatsApp</sub>`. Depois do `voz.py`, rode `limpa_voz.py` para tirar o apelido das legendas.
- Sites falados por extenso: "nutriforma ponto com ponto br, barra site".
```bash
python3 kit/video/narrado/voz.py r1/voz.ssml r1/voz.wav r1/voz.json   # chave do Azure em ~/.azure-voz (o cliente cola; nunca mostre)
python3 kit/video/narrado/limpa_voz.py r1/voz.json                    # só se usou <sub alias>
```
Azure Free F0 = 500 mil caracteres/mês grátis. O cliente recusou voz paga (ElevenLabs). Kokoro (local) fica só como reserva.

## 2. Cenas (reel.json)
- `marca`: `nome`, `selo`, `url`, `logo` e `cores` (fundo, primaria, escura, clara, destaque, acento). Isso pinta selo, barra de progresso, cartões, legenda e final.
- Tipos de cena:
  - `broll`: `clip`, `ini` (segundo do vídeo), `zoom` [início, fim], `cx` (0 a 1, onde cortar o horizontal).
  - `phone`: `tela`, `y0`/`y1` (rolagem), `cam` (entra · orbita · …) e `cards` [{x, y, t (0 a 1 da cena), txt, sub, big, azul, cor, r}].
  - `marca`: só tipografia sobre o fundo da marca.
  - `fim`.
- Palavras de legenda: `chaves` ganham a cor de destaque, `flashPal` ganham o clarão branco e `maxpal` define quantas palavras aparecem por vez (4).
- Ritmo que funcionou: 2 b-rolls de dor → 2 ou 3 celulares com cartões (números grandes em cartão azul) → fim. Varie o estilo entre posts: o cliente rejeita "sempre igual".
- Prévia sempre antes:
```bash
python3 kit/video/narrado/cine.py r1/reel.json --previa   # r1/previa.jpg: 3 quadros por cena
python3 kit/video/narrado/cine.py r1/reel.json            # r1/<nome>.mp4 1080x1920 30 fps, música com ducking, -14 LUFS
```
Render de ~5 a 10 min por reel (2 CPUs): rode em segundo plano. Se cair, `RETOMAR=1` continua do último quadro.

## 3. B-roll do Pexels
- Busque pela página do Pexels (WebSearch/WebFetch) e prefira vídeos verticais HD com pessoa real, comida brasileira e luz quente.
- Baixe pelo arquivo direto: `https://videos.pexels.com/video-files/<id>/<arquivo>.mp4`, que responde daqui. Anote `nome id/arquivo` em `broll/lista.txt`.
- Antes de usar, confira `broll/usados.txt`. Depois de aprovado, acrescente o clipe lá.
- Não use celular mostrando outra coisa que não comida (natureza, rede social) nem cenas de antes/depois.

## 4. Celulares 3D para artes e cartões
```bash
python3 kit/video/narrado/fones.py fones.json   # {"hoje": ["hoje-full", 0, "direita"], ...} → fones/<nome>.png recortado
```
`trio.png` (3 celulares do final) é composto a partir desses PNGs.

## 5. Cartão final de oferta (anúncio x post)
Quando o vídeo vende algo (teste grátis, oferta), ele termina num cartão animado de 2,5 a 3,5 s, em duas versões:
- **anúncio**: "Toque no botão e comece 👇", para o botão do anúncio;
- **post**: "Link na bio 👆".
```bash
node kit/video/narrado/cartao.mjs cartao.json anuncio 3.2 cartao-anuncio.mp4 [narracao.wav]
node kit/video/narrado/cartao.mjs cartao.json post 3.2 cartao-post.mp4 [narracao.wav]
bash kit/video/narrado/junta_cartao.sh r1/reel.mp4 cartao-anuncio.mp4 anuncio-reel-1.mp4   # fusão de 0,5 s
bash kit/video/narrado/junta_cartao.sh r1/reel.mp4 cartao-post.mp4 post-reel-1.mp4
```
A narração do cartão (ex.: "Teste 24 horas grátis, sem cartão") sai do `voz.py` com um SSML curto.

## 6. Efeitos sonoros no OpusClip
```bash
python3 kit/video/narrado/sfx.py r1 > r1/sfx.json   # lista pronta para place_sound_effects (tempos tirados do tl.json)
```
Depois siga `OPUSCLIP.md`: sign_upload → PUT → start_transcribe_project → wait_task → list_sound_effects (confira os ids) → place_sound_effects (replace: true) → start_export → get_export_url → baixar com cookie.

## 7. Conferência
- Prévia e alguns quadros em tamanho real.
- Volume com `ffmpeg -af ebur128` (por volta de -14 LUFS).
- Duração e áreas seguras: nada importante nos 160 px do topo nem nos 300 px de baixo.
- Não ouço o áudio: diga que voz e música foram conferidas por volume e tempo e peça para o cliente escutar.
