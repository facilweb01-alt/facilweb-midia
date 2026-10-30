"""Utilidades de composição quadro a quadro (OpenCV/numpy) e de camadas HTML (Playwright)."""
import asyncio, math, os
import cv2, numpy as np

_cache = {}


def png(caminho):
    """Carrega PNG (com alfa) uma vez só."""
    if caminho not in _cache:
        im = cv2.imread(caminho, cv2.IMREAD_UNCHANGED)
        if im is None:
            raise FileNotFoundError(caminho)
        if im.shape[2] == 3:
            im = np.dstack([im, np.full(im.shape[:2], 255, np.uint8)])
        _cache[caminho] = im
    return _cache[caminho]


def colar(dst, rgba, x, y, alpha=1.0, escala=1.0, centro=False):
    """Cola uma imagem RGBA sobre dst (BGR) com opacidade e escala."""
    if alpha <= 0.01 or escala <= 0.01:
        return
    H, W = dst.shape[:2]
    im = rgba if abs(escala - 1) < 1e-3 else cv2.resize(
        rgba, None, fx=escala, fy=escala, interpolation=cv2.INTER_LINEAR if escala > 1 else cv2.INTER_AREA)
    h, w = im.shape[:2]
    if centro:
        x, y = x - w / 2, y - h / 2
    x, y = int(round(x)), int(round(y))
    x0, y0, x1, y1 = max(x, 0), max(y, 0), min(x + w, W), min(y + h, H)
    if x0 >= x1 or y0 >= y1:
        return
    sub = im[y0 - y:y1 - y, x0 - x:x1 - x]
    a = (sub[:, :, 3:4].astype(np.float32) / 255) * alpha
    reg = dst[y0:y1, x0:x1].astype(np.float32)
    dst[y0:y1, x0:x1] = (reg * (1 - a) + sub[:, :, :3] * a).astype(np.uint8)


def eo(x):  # ease out
    x = min(max(x, 0), 1); return 1 - (1 - x) ** 3


def eb(x, s=1.7):  # ease back (passa um pouco e volta)
    x = min(max(x, 0), 1) - 1; return x * x * ((s + 1) * x + s) + 1


def jan(t, a, d=0.25):  # 0..1 entre a e a+d
    return min(max((t - a) / d, 0), 1)


def girar(rgba, ang, esc=1.0):
    h, w = rgba.shape[:2]
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, esc)
    c, s = abs(M[0, 0]), abs(M[0, 1])
    nw, nh = int(h * s + w * c), int(h * c + w * s)
    M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
    return cv2.warpAffine(rgba, M, (nw, nh), borderValue=(0, 0, 0, 0))


def cartao(img, larg=500, borda=12, raio=34):
    """Recorte com borda branca e cantos arredondados (o 'zoom de lupa')."""
    esc = larg / img.shape[1]
    im = cv2.resize(img[:, :, :3], None, fx=esc, fy=esc, interpolation=cv2.INTER_AREA)
    h, w = im.shape[:2]
    card = np.full((h + 2 * borda, w + 2 * borda, 4), 255, np.uint8)
    card[borda:borda + h, borda:borda + w, :3] = im
    m = np.zeros(card.shape[:2], np.uint8); H2, W2 = m.shape; r = raio
    cv2.rectangle(m, (r, 0), (W2 - r, H2), 255, -1); cv2.rectangle(m, (0, r), (W2, H2 - r), 255, -1)
    for cx, cy in ((r, r), (W2 - r, r), (r, H2 - r), (W2 - r, H2 - r)):
        cv2.circle(m, (cx, cy), r, 255, -1, cv2.LINE_AA)
    card[:, :, 3] = m
    return card


def zoom_crop(im, z, cx=None, cy=None, w=1080, h=1920):
    sh, sw = im.shape[:2]
    cx = sw / 2 if cx is None else cx; cy = sh / 2 if cy is None else cy
    cw, ch = sw / z, sh / z
    if cw / ch > w / h: cw = ch * w / h
    else: ch = cw * h / w
    x0 = min(max(cx - cw / 2, 0), sw - cw); y0 = min(max(cy - ch / 2, 0), sh - ch)
    M = np.float32([[w / cw, 0, -x0 * w / cw], [0, h / ch, -y0 * h / ch]])
    return cv2.warpAffine(im, M, (w, h), flags=cv2.INTER_AREA if w < cw else cv2.INTER_CUBIC)


def gradiente(w, h, de, ate, cor_bgr):
    a = np.linspace(de, ate, h)[:, None, None]
    return np.dstack([np.broadcast_to(np.array(cor_bgr, np.uint8), (h, w, 3)),
                      np.broadcast_to((a * 255).astype(np.uint8), (h, w, 1))]).copy()


def barra_progresso(img, i, total, frac, y=1720, cor_bgr=(63, 198, 141)):
    W = img.shape[1]; gap = 12; x0 = 70; larg = int((W - 2 * x0 - gap * (total - 1)) / total)
    for j in range(total):
        xa = x0 + j * (larg + gap); sub = img[y:y + 12, xa:xa + larg]
        img[y:y + 12, xa:xa + larg] = (sub * 0.6 + 255 * 0.4).astype(np.uint8)
        f = 1.0 if j < i else (frac if j == i else 0)
        if f > 0: cv2.rectangle(img, (xa, y), (xa + int(larg * f), y + 12), cor_bgr, -1)


def flash(img, intensidade):
    if intensidade <= 0: return img
    return (img * (1 - intensidade) + 255 * intensidade).astype(np.uint8)


def tremida(img, forca, t):
    if forca <= 0: return img
    M = np.float32([[1, 0, forca * math.sin(t * 90)], [0, 1, forca * math.cos(t * 70)]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]), borderMode=cv2.BORDER_REFLECT)


def chicote(img, forca):
    """Motion blur horizontal (transição rápida)."""
    k = int(forca) | 1
    return cv2.blur(img, (k, 1)) if k > 1 else img


# ---------- camadas HTML -> PNG transparente ----------
CSS_BASE = """*{margin:0;padding:0;box-sizing:border-box}html,body{background:transparent}
body{color:#fff;display:inline-block} #e{display:inline-block}"""


def html_el(corpo, css, extra_css=""):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS_BASE}{extra_css}{css}</style></head><body><div id="e">{corpo}</div></body></html>'


async def _render(itens, pasta, w, h):
    from playwright.async_api import async_playwright
    os.makedirs(pasta, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={"width": w, "height": h})
        for nome, (html, inteiro) in itens.items():
            await pg.set_content(html); await pg.wait_for_timeout(80)
            if inteiro:
                await pg.screenshot(path=os.path.join(pasta, nome + ".png"), omit_background=True)
            else:
                await pg.locator("#e").screenshot(path=os.path.join(pasta, nome + ".png"), omit_background=True)
        await b.close()


def renderizar_camadas(itens, pasta, w=1080, h=1920):
    """itens = {nome: (html, pagina_inteira: bool)}"""
    asyncio.run(_render(itens, pasta, w, h))
