"""Converte o Real-ESRGAN general x4v3 (.pth) para ONNX sem torch e roda super-resolução em frames.

Rede SRVGGNetCompact: conv(3->64) PReLU, 32x [conv(64->64) PReLU], conv(64->48), PixelShuffle(4),
soma com a entrada ampliada (nearest).
"""
import pickle, sys, zipfile
import numpy as np

class _Storage:
    def __init__(self, key, dtype): self.key, self.dtype = key, dtype

def carregar_pth(caminho):
    z = zipfile.ZipFile(caminho)
    raiz = z.namelist()[0].split("/")[0]
    tipos = {"FloatStorage": np.float32, "HalfStorage": np.float16}

    def rebuild(storage, offset, size, stride, *a):
        buf = np.frombuffer(z.read(f"{raiz}/data/{storage.key}"), dtype=storage.dtype)
        n = int(np.prod(size)) if len(size) else 1
        arr = buf[offset:offset + max(n, 1)] if all(True for _ in [0]) else buf
        # tensores contíguos (caso destes pesos)
        return np.array(buf[offset:offset + n]).reshape(size).astype(np.float32)

    class U(pickle.Unpickler):
        def find_class(self, mod, name):
            if name == "_rebuild_tensor_v2": return rebuild
            if name.endswith("Storage"): return tipos.get(name, np.float32)
            if mod == "collections" and name == "OrderedDict":
                import collections; return collections.OrderedDict
            return super().find_class(mod, name)
        def persistent_load(self, pid):
            _, tipo, key, loc, n = pid
            return _Storage(key, tipo if isinstance(tipo, type) else np.float32)

    d = U(z.open(f"{raiz}/data.pkl")).load()
    return d.get("params", d.get("params_ema", d))

def montar_onnx(pesos, saida):
    import onnx
    from onnx import helper, TensorProto, numpy_helper
    nos, inits = [], []
    def init(nome, arr):
        inits.append(numpy_helper.from_array(arr.astype(np.float32), nome)); return nome
    ks = sorted({int(k.split(".")[1]) for k in pesos if k.startswith("body.")})
    x = "entrada"
    for i in ks:
        w = pesos.get(f"body.{i}.weight")
        if w is None: continue
        if w.ndim == 4:
            y = f"c{i}"
            nos.append(helper.make_node("Conv", [x, init(f"w{i}", w), init(f"b{i}", pesos[f"body.{i}.bias"])], [y],
                                        kernel_shape=[3, 3], pads=[1, 1, 1, 1]))
        else:  # PReLU
            y = f"p{i}"
            nos.append(helper.make_node("PRelu", [x, init(f"a{i}", w.reshape(-1, 1, 1))], [y]))
        x = y
    nos.append(helper.make_node("DepthToSpace", [x], ["ps"], blocksize=4, mode="CRD"))
    nos.append(helper.make_node("Resize", ["entrada", "", init("esc", np.array([1, 1, 4, 4], np.float32))], ["up"], mode="nearest"))
    nos.append(helper.make_node("Add", ["ps", "up"], ["saida"]))
    g = helper.make_graph(nos, "srvgg", [helper.make_tensor_value_info("entrada", TensorProto.FLOAT, [1, 3, None, None])],
                          [helper.make_tensor_value_info("saida", TensorProto.FLOAT, [1, 3, None, None])], inits)
    m = helper.make_model(g, opset_imports=[helper.make_opsetid("", 17)]); m.ir_version = 8
    onnx.save(m, saida)

if __name__ == "__main__":
    p = carregar_pth(sys.argv[1])
    print(len(p), "tensores", list(p)[:4])
    montar_onnx(p, sys.argv[2])
    print("ok", sys.argv[2])
