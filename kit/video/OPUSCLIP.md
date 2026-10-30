# Acabamento no OpusClip (AI Producer)

Todo vídeo editado passa pelo OpusClip antes de ir para aprovação. Ele coloca os efeitos sonoros da biblioteca
dele no tempo certo. Em vídeo com fala, ele também faz legendas e o corte das falas.

## Pré-requisitos
- Conector "AI Producer by OpusClip" ligado na conversa.
- Domínios liberados em claude.ai → Configurações → Capacidades: `producer.opus.pro`, `storage.googleapis.com`,
  `opus-lab.cdn.opuslab.ai`. Sem eles, use a URL pública do vídeo (ex.: raw.githubusercontent.com) e peça ao
  usuário para baixar o export pelo site.

## Passo a passo (ferramentas do conector)
1. `get_pricing` (ver se algo cobra; hoje tudo é grátis, menos restyle).
2. Subir o vídeo:
   - direto: `sign_upload` (filename, content_type video/mp4, size, sha256) e depois
     `curl -X PUT --upload-file video.mp4 -H "Content-Type: application/octet-stream" "<upload_url>"`, depois
     `start_transcribe_project` (video_ref, filename, sha256, prompt, aspect_ratio 9:16);
   - ou por link público: `start_project_from_attachment` com `file.download_url`.
3. `wait_task` até `done`.
4. `list_sound_effects` (project_id, limit 300). A resposta é grande: salve e filtre com jq/python.
   Guarde `project_revision` e `library_version`.
5. `place_sound_effects` numa chamada só, com `replace: true` e um `idempotency_key` (UUID novo).
6. `start_export` e depois `wait_task`.
7. `get_export_url` e baixar com cookie (o link troca um ticket por sessão e redireciona para a CDN):
   `curl -sSL -c j -b j -o final.mp4 "<download_url>"`. O link vale ~15 min e é de uso único: se falhar, chame
   `get_export_url` de novo.
8. Conferir a duração e o volume: `ffmpeg -i final.mp4 -af ebur128 -f null -`. Fica em torno de -18 LUFS.

## Regras dos efeitos (o que funcionou)
- Orçamento: no máximo duração/2,5 efeitos (ex.: 8 num vídeo de 20 s). Pelo menos 600 ms entre efeitos.
  A cada 10 s, deixe um trecho de 3 s sem nenhum efeito.
- Peso: som pesado (impacto, braam) só no gancho e no final. Nas viradas, whoosh curto. Em cartões e textos, pop.
- Paleta de 2 ou 3 famílias que se repetem. Os sons que já usamos e funcionaram:
  | uso | sound_id | nome | âncora |
  |---|---|---|---|
  | impacto do gancho | 9bd4187c | Punch - Warm Tight 01 | first_hit |
  | impacto suave | cd08d737 | Impact - Warm Soft Cloth 01 | first_hit |
  | virada de passo | 2b2f7db3 | Whoosh - Warm Snappy 02 | first_hit |
  | virada mais suave | 5c40f0a3 | Whoosh - Warm Smooth 01 | first_hit |
  | texto/cartão entrando | f7d9554f | Pop - Warm 01 | first_hit |
  | pop mais encorpado | e1c045f5 | Pop - Warm 03 | first_hit |
  | lupa / print da tela | 4980ac04 | Camera - Shutter 01 | first_hit |
  | dinheiro / valor | 1b4328ca | Cash Register - Kaching x2 01 | first_hit |
  | caixa registradora | bbec6f06 | Cash Register - Bright 01 | first_hit |
  | logo no final | 4005db58 | Braam - Warm Soft Long Tail 01 | peak (no instante em que a logo aparece) |
  | abertura suave | 6105fcc9 | Swoosh - Warm Slow 01 | peak |
  Confira os IDs com `list_sound_effects`: a biblioteca pode mudar de versão.
- Os tempos vêm do roteiro: início de cada passo, entrada das lupas, impacto do gancho, entrada da logo.
  Os scripts do kit imprimem esses tempos na prévia.

## Vídeo sem fala
O OpusClip avisa `speechless_source`: legenda e corte de fala não se aplicam. Use só os efeitos.
Não deixe ele inventar título nem cartão: o vídeo já sai pronto do kit.
