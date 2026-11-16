#!/bin/bash
# Junta o cartão final ao reel com fusão de 0,5 s (imagem e som). Uso: junta_cartao.sh reel.mp4 cartao.mp4 saida.mp4
set -e
d=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"); off=$(python3 -c "print(round($d-0.5,3))")
ffmpeg -v error -y -i "$1" -i "$2" -filter_complex "[0:v]fps=30,format=yuv420p[a];[1:v]fps=30,scale=1080:1920,format=yuv420p[b];[a][b]xfade=transition=fade:duration=0.5:offset=$off[v];[0:a][1:a]acrossfade=d=0.5[au]" \
  -map "[v]" -map "[au]" -c:v libx264 -preset veryfast -crf 20 -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$3"
echo "ok $3 $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$3")s $(du -h "$3" | cut -f1)"
