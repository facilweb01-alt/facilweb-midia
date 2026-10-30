# Kit de Instagram, design 3D e vídeo (PT-BR)

Ferramentas usadas no @facilweb, agora genéricas para qualquer marca. A identidade vem de um `marca.json`.

```
kit/
  instalar.sh              dependências (Python, Playwright, three.js)
  lib/marca.py             lê o marca.json (cores, fonte, logo, @, site)
  lib/comp.py              composição quadro a quadro e camadas HTML
  instagram/               linters de legenda e gancho + MODELOS.md (agendamento, conferência, pesquisa, estratégia)
  design3d/                celulares 3D (three.js): carrossel.py, reel3d.py, tela.py
  video/                   melhorar.py, super_resolucao.py, reel_cinetico.py, musica.py, OPUSCLIP.md
  exemplos/                marca-facilweb.json, telas de exemplo e roteiros prontos
```

## Começo rápido
```bash
bash kit/instalar.sh
cp kit/exemplos/marca-facilweb.json minha-marca.json      # troque cores, logo, @ e site
python3 kit/design3d/tela.py print.png telas/cardapio.png # print do sistema -> tela do celular 3D
python3 kit/design3d/carrossel.py roteiro-carrossel.json  # carrossel 1080x1350 (JPEG + prévia)
python3 kit/design3d/reel3d.py roteiro-reel3d.json        # reel 3D 1080x1920
python3 kit/video/reel_cinetico.py roteiro-video.json     # edita vídeo bruto em reel (tela_cheia ou vitrine)
```
Acrescente `--previa` aos reels para ver um quadro de cada cena antes de renderizar tudo.

## Regras de padrão
- Logo em selo branco em toda peça.
- Celular nunca cortado; texto legível nas áreas seguras (topo 160 px e rodapé 300 px livres no 9:16).
- Vídeo termina com a marca, sem chamada na tela; a chamada fica na legenda (ex.: "Comenta QUERO").
- Todo vídeo passa pelo OpusClip (video/OPUSCLIP.md) para os efeitos sonoros antes da aprovação.
- Nada vai ao ar sem aprovação explícita do cliente.
- Legendas: `instagram/caption.py` (PRONTA), `instagram/detect.py` (APROVADO 70+), ganchos com `instagram/hookscore.py` (70+).

## Custos de tempo (2 CPUs)
- Carrossel de 8 slides: ~1 min.
- Reel 3D de 20 s: ~5 a 8 min (os celulares 3D são o mais lento).
- Reel de vídeo sem super-resolução: ~3 min. Com super-resolução: ~7 s por quadro usado (≈ 45 min para 20 s).
