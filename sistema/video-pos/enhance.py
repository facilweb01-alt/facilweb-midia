"""Melhora o vídeo do POS: levanta sombras, reduz o reflexo lavado na tela, contraste local e cor."""
import sys, cv2, numpy as np

def lut_sombras(lift=0.18, contraste=0.55):
    x = np.arange(256) / 255.0
    y = x + lift * x * (1 - x) ** 3 * 4          # levanta só as sombras profundas
    s = 0.5 - 0.5 * np.cos(np.pi * y)              # curva em S: devolve contraste aos meios-tons
    y = (1 - contraste) * y + contraste * s
    return np.clip(y * 255, 0, 255).astype(np.uint8)

LUT = lut_sombras()
CLAHE = cv2.createCLAHE(clipLimit=1.9, tileGridSize=(6, 10))

def melhora(bgr):
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = CLAHE.apply(l)                   # contraste local: tira o véu do reflexo na tela
    lf = l.astype(np.float32)
    base = cv2.GaussianBlur(lf, (0, 0), 18)
    lf = lf + 0.42 * (lf - base)         # "clarity": realça texto e bordas, reduz a névoa
    lf = lf - 0.25 * np.clip(base - 150, 0, None)  # abaixa áreas grandes estouradas (reflexo da janela)
    l = cv2.LUT(np.clip(lf, 0, 255).astype(np.uint8), LUT)

    lab = cv2.merge([l, a, b])
    out = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[..., 1] = np.clip(hsv[..., 1] * 1.2, 0, 255)
    out = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
    out = cv2.addWeighted(out, 1.0, np.zeros_like(out), 0, 0)  # leve brilho
    return out

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    if src.endswith(".png"):
        cv2.imwrite(dst, melhora(cv2.imread(src))); sys.exit()
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w, h = int(cap.get(3)), int(cap.get(4))
    vw = cv2.VideoWriter(dst, cv2.VideoWriter_fourcc(*"MJPG"), fps, (w, h))
    n = 0
    while True:
        ok, f = cap.read()
        if not ok: break
        vw.write(melhora(f)); n += 1
    vw.release(); print("frames", n, "fps", fps)
