"""Super-resolução (Real-ESRGAN x4v3 via ONNX) nos frames usados da edição; salva JPEG 1440x2560."""
import os, sys, cv2, numpy as np, onnxruntime as ort, time
modelo, video, pasta = sys.argv[1:4]
os.makedirs(pasta, exist_ok=True)
so = ort.SessionOptions(); so.intra_op_num_threads = 2
s = ort.InferenceSession(modelo, so, providers=["CPUExecutionProvider"])
cap = cv2.VideoCapture(video); fps = cap.get(cv2.CAP_PROP_FPS)
sys.path.insert(0, os.path.dirname(__file__)); from edicao import frames_fonte
precisa = set(frames_fonte())
i, feitos, t0 = 0, 0, time.time()
while True:
    ok, f = cap.read()
    if not ok: break
    if i in precisa and not os.path.exists(f"{pasta}/{i:05d}.jpg"):
        x = (f[:, :, ::-1].astype(np.float32) / 255).transpose(2, 0, 1)[None]
        y = s.run(None, {"entrada": x})[0][0].transpose(1, 2, 0)
        o = (np.clip(y, 0, 1) * 255).round().astype(np.uint8)[:, :, ::-1]
        cv2.imwrite(f"{pasta}/tmp.jpg", cv2.resize(o, (1440, 2560), interpolation=cv2.INTER_AREA), [cv2.IMWRITE_JPEG_QUALITY, 94]); os.replace(f"{pasta}/tmp.jpg", f"{pasta}/{i:05d}.jpg")
        feitos += 1
        if feitos % 25 == 0: print(i, feitos, f"{(time.time()-t0)/feitos:.1f}s/frame", flush=True)
    i += 1
print("fim", feitos, flush=True)
