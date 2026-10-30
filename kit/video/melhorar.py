"""Melhora imagem de vídeo gravado no celular: tira ruído, levanta sombras, reduz o véu de reflexo em telas,
contraste local e cor. Também roda a super-resolução (IA) quando pedido.

Uso:
  python3 melhorar.py entrada.mp4 saida.mp4 [--sr] [--forca 1.0]
  --sr     amplia 4x com Real-ESRGAN (nítido de verdade, mas lento: ~7 s por quadro em 2 CPUs)
  --forca  intensidade do tratamento (0.5 suave, 1.0 padrão, 1.4 forte)
Como módulo: from melhorar import melhorar_quadro
"""
import argparse, os, subprocess, sys
import cv2, numpy as np


def _lut(lift=0.20, contraste=0.30):
    x = np.arange(256) / 255.0
    y = x + lift * x * (1 - x) ** 3 * 4              # levanta só as sombras
    s = 0.5 - 0.5 * np.cos(np.pi * y)
    y = (1 - contraste) * y + contraste * s           # curva em S nos meios-tons
    return np.clip(y * 255, 0, 255).astype(np.uint8)


def melhorar_quadro(bgr, forca=1.0, clarity=True):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=1.2 + 0.7 * forca, tileGridSize=(6, 10))
    l = clahe.apply(l)
    if clarity:
        lf = l.astype(np.float32); base = cv2.GaussianBlur(lf, (0, 0), 18)
        lf = lf + 0.42 * forca * (lf - base)                          # realça texto e bordas
        lf = lf - 0.25 * forca * np.clip(base - 150, 0, None)          # segura áreas estouradas (reflexo de janela)
        l = np.clip(lf, 0, 255).astype(np.uint8)
    l = cv2.LUT(l, _lut(0.20 * forca, 0.30 * min(forca, 1.2)))
    out = cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * (1 + 0.2 * forca), 0, 255)
    return cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)


def desruido(entrada, saida):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", entrada, "-vf", "hqdn3d=4:3:6:4", "-c:v", "libx264",
                    "-preset", "veryfast", "-crf", "12", "-c:a", "copy", saida], check=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("entrada"); ap.add_argument("saida")
    ap.add_argument("--sr", action="store_true"); ap.add_argument("--forca", type=float, default=1.0)
    a = ap.parse_args()
    tmp = a.saida + ".den.mp4"; desruido(a.entrada, tmp)
    cap = cv2.VideoCapture(tmp); fps = cap.get(cv2.CAP_PROP_FPS)
    sr = None
    if a.sr:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from super_resolucao import SR; sr = SR()
    w, h = int(cap.get(3)), int(cap.get(4))
    if sr: w, h = w * 4, h * 4
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}", "-r", f"{fps}",
                           "-i", "-", "-i", a.entrada, "-map", "0:v", "-map", "1:a?", "-c:a", "copy", "-c:v", "libx264", "-preset", "veryfast",
                           "-crf", "16", "-pix_fmt", "yuv420p", "-vf", "hqdn3d=2:1.5:3:2", a.saida], stdin=subprocess.PIPE)
    n = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        q = melhorar_quadro(f, a.forca)
        if sr: q = sr.ampliar(q)
        ff.stdin.write(q.tobytes()); n += 1
        if sr and n % 25 == 0: print(n, "quadros", flush=True)
    ff.stdin.close(); ff.wait(); os.remove(tmp); print("ok", a.saida, n, "quadros")
