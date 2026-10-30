"""Ponte Python -> render3d.js. Garante o three.js instalado e converte caminhos absolutos para /abs."""
import json, os, subprocess, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))


def preparar():
    if not os.path.exists(os.path.join(AQUI, "node_modules", "three")):
        subprocess.run(["npm", "install", "--silent"], cwd=AQUI, check=True)


def celular(tela, pos, rot, s=1.0, fase=0.0, sombra=False):
    """tela: caminho da imagem 600x1300 (use tela.py para gerar a partir de um print)."""
    return {"tex": "/abs" + os.path.abspath(tela), "pos": pos, "rot": rot, "s": s, "fase": fase, "sombra": sombra}


def moeda(pos, rot=None, s=1.0):
    d = {"pos": pos, "s": s}
    if rot: d["rot"] = rot
    return d


def esfera(cor, pos, s=1.0):
    return {"tipo": "esfera", "cor": cor, "pos": pos, "s": s}


def renderizar(cenas, pasta_saida, frames=1, fps=24, porta=8790):
    """cenas = {nome: {w,h,fov,cam,phones,moedas,giro,flutua,frames?,fundo?}}.
    1 frame -> pasta_saida/nome.png ; N frames -> pasta_saida/nome/f0000.png ..."""
    preparar()
    for c in cenas.values():
        if c.get("fundo") and os.path.isabs(c["fundo"]): c["fundo"] = "/abs" + c["fundo"]
    fd, cfg = tempfile.mkstemp(suffix=".json"); os.close(fd)
    json.dump(cenas, open(cfg, "w"))
    subprocess.run(["node", "render3d.js", cfg, os.path.abspath(pasta_saida), str(frames), str(fps)],
                   cwd=AQUI, check=True, env={**os.environ, "PORTA": str(porta)})
    os.remove(cfg)
