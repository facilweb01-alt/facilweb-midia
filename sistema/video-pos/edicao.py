"""Mapa da edição (compartilhado pelas duas opções): trechos do vídeo original e velocidades, saída 24 fps."""
FPS_SRC = 29.916666
FPS = 24
TEASER = (44.3, 46.1, 1.0)
SEGS = [  # (início, fim, velocidade, passo)
    (0.5, 7.5, 3.0, 1), (7.5, 19.0, 4.0, 2), (19.0, 30.0, 3.0, 3),
    (30.0, 40.0, 2.5, 4), (40.0, 44.3, 2.5, 5), (44.3, 46.1, 1.0, 5)]
FREEZE_TEASER, OUTRO = 0.4, 3.4

def frames_fonte():
    """Lista de índices de frame do original para cada frame de saída (teaser + principal)."""
    out = []
    def trecho(a, b, v):
        n = int(round((b - a) / v * FPS))
        return [min(int(round((a + k * v / FPS) * FPS_SRC)), 1379) for k in range(n)]
    t = trecho(*TEASER); out += t + [t[-1]] * int(FREEZE_TEASER * FPS)
    for a, b, v, _ in SEGS: out += trecho(a, b, v)
    return out

if __name__ == "__main__":
    f = frames_fonte(); print(len(f), "frames de saída,", len(set(f)), "únicos")
