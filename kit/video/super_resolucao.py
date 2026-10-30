"""Super-resolução 4x com Real-ESRGAN (realesr-general-x4v3) rodando em ONNX, sem torch e sem GPU.
Na primeira vez baixa os pesos do GitHub (~5 MB) e monta o modelo ONNX em ~/.cache/kit-video/.

Uso como módulo:
  from super_resolucao import SR
  sr = SR(); grande = sr.ampliar(quadro_bgr)      # 4x
Custo: ~7 s por quadro de 480x854 em 2 CPUs. Processe só os quadros que vão para a edição.
Requisitos: pip install onnx onnxruntime (--break-system-packages se precisar).
"""
import os, subprocess, sys, urllib.request
import numpy as np

URL = "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/realesr-general-x4v3.pth"
CACHE = os.path.expanduser("~/.cache/kit-video")


def garantir_modelo():
    os.makedirs(CACHE, exist_ok=True)
    onnx_p = os.path.join(CACHE, "x4v3.onnx"); pth = os.path.join(CACHE, "realesr-general-x4v3.pth")
    if os.path.exists(onnx_p): return onnx_p
    try:
        import onnx, onnxruntime  # noqa
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--break-system-packages", "onnx", "onnxruntime"], check=True)
    if not os.path.exists(pth):
        try:
            urllib.request.urlretrieve(URL, pth)
        except Exception:
            subprocess.run(["curl", "-sSL", "-o", pth, URL], check=True)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from sr_onnx import carregar_pth, montar_onnx
    montar_onnx(carregar_pth(pth), onnx_p)
    return onnx_p


class SR:
    def __init__(self, threads=None):
        import onnxruntime as ort
        so = ort.SessionOptions()
        if threads: so.intra_op_num_threads = threads
        self.s = ort.InferenceSession(garantir_modelo(), so, providers=["CPUExecutionProvider"])

    def ampliar(self, bgr):
        x = (bgr[:, :, ::-1].astype(np.float32) / 255).transpose(2, 0, 1)[None]
        y = self.s.run(None, {"entrada": x})[0][0].transpose(1, 2, 0)
        return (np.clip(y, 0, 1) * 255).round().astype(np.uint8)[:, :, ::-1].copy()
