#!/usr/bin/env bash
# Instala o que o kit precisa (Linux com Python 3 e Node). Rode uma vez por sessão nova.
set -e
AQUI="$(cd "$(dirname "$0")" && pwd)"
PIP="pip install -q"
$PIP --help >/dev/null 2>&1 || true
python3 -c "import cv2, numpy, scipy, PIL" 2>/dev/null || $PIP --break-system-packages opencv-python-headless numpy scipy pillow 2>/dev/null || $PIP opencv-python-headless numpy scipy pillow
python3 -c "import playwright" 2>/dev/null || { $PIP --break-system-packages playwright 2>/dev/null || $PIP playwright; python3 -m playwright install chromium; }
node -e "require('playwright')" 2>/dev/null || (cd "$AQUI/design3d" && npm install --silent playwright)
(cd "$AQUI/design3d" && [ -d node_modules/three ] || npm install --silent)
# reel narrado (kit/video/narrado): three.js + fontes Unbounded e Instrument Sans, e o SDK de voz do Azure
(cd "$AQUI/video/narrado" && [ -d node_modules/@fontsource-variable/unbounded ] || npm install --silent)
python3 -c "import azure.cognitiveservices.speech" 2>/dev/null || $PIP --break-system-packages azure-cognitiveservices-speech 2>/dev/null || $PIP azure-cognitiveservices-speech
fc-list | grep -qi poppins || echo "Aviso: fonte Poppins não encontrada (instale para manter a identidade)."
command -v ffmpeg >/dev/null || echo "Aviso: instale o ffmpeg."
echo "kit pronto."
