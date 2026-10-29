"""Monta o vídeo POS @facilweb 1080x1920: gancho, demonstração acelerada com passos e encerramento."""
import subprocess, sys

D = "/home/claude/video-pos"
C = f"{D}/camadas"
FPS = 30
# (início, fim, velocidade) no vídeo melhorado
TEASER = (44.3, 46.1, 1.0)
SEGS = [(0.5, 7.5, 2.3), (7.5, 19.0, 3.2), (19.0, 30.0, 2.4), (30.0, 40.0, 2.0), (40.0, 44.3, 2.0), (44.3, 46.1, 1.0)]
PASSO_DE_SEG = [1, 2, 3, 4, 5, 5]
FREEZE_TEASER, OUTRO = 0.4, 3.4


def cartao():
    """Gera o vídeo que vai dentro da moldura (780x1387)."""
    partes, filt = [], []
    todos = [TEASER] + SEGS
    for i, (a, b, v) in enumerate(todos):
        f = f"[0:v]trim={a}:{b},setpts=(PTS-STARTPTS)/{v},fps={FPS}"
        if i == 0:
            f += f",tpad=stop_mode=clone:stop_duration={FREEZE_TEASER}"
        if i == len(todos) - 1:
            f += f",tpad=stop_mode=clone:stop_duration={OUTRO}"
        filt.append(f + f"[s{i}]")
        partes.append(f"[s{i}]")
    filt.append("".join(partes) + f"concat=n={len(partes)}:v=1:a=0,"
                "scale=840:1494:flags=lanczos,unsharp=5:5:0.7:5:5:0,"
                "crop=780:1386:x='30+28*sin(t/2.7)':y='53+40*sin(t/3.3)',"
                "colorbalance=rs=0.03:gs=0.0:bs=-0.03:rm=0.02:bm=-0.02,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{D}/enh.mp4", "-filter_complex", ";".join(filt),
                    "-map", "[v]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", f"{D}/cartao.mp4"], check=True)


def tempos():
    t0 = TEASER[1] - TEASER[0] + FREEZE_TEASER
    janelas, t = [], t0
    for (a, b, v), p in zip(SEGS, PASSO_DE_SEG):
        d = (b - a) / v
        if janelas and janelas[-1][0] == p:
            janelas[-1][2] = t + d
        else:
            janelas.append([p, t, t + d])
        t += d
    return t0, t, janelas


def montar(final, saida):
    t0, tfim, janelas = tempos()
    total = tfim + OUTRO
    idx, k = {}, 0
    def add(n):
        nonlocal k; idx[n] = k; k += 1
    ins = []
    for n in ["fundo", "brilho_v", "brilho_l", "sombra"]:
        add(n); ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.2f}", "-i", f"{C}/{n}.png"]
    add("cartao"); ins += ["-i", f"{D}/cartao.mp4"]
    for n in ["mascara", "borda", "selo", "topo", "gancho", "passo1", "passo2", "passo3", "passo4", "passo5", final]:
        add(n); ins += ["-loop", "1", "-framerate", str(FPS), "-t", f"{total:.2f}", "-i", f"{C}/{n}.png"]
    add("audio"); ins += ["-f", "lavfi", "-t", f"{total:.2f}", "-i", "anullsrc=r=44100:cl=stereo"]

    f = []
    f.append(f"[{idx['fundo']}:v]format=rgba[bg]")
    f.append(f"[bg][{idx['brilho_v']}:v]overlay=x='-380+90*sin(t*0.5)':y='1150+70*cos(t*0.4)'[b1]")
    f.append(f"[b1][{idx['brilho_l']}:v]overlay=x='560+80*cos(t*0.45)':y='120+90*sin(t*0.35)'[b2]")
    f.append(f"[b2][{idx['sombra']}:v]overlay=0:0[b3]")
    f.append(f"[{idx['mascara']}:v]format=gray[m]")
    f.append(f"[{idx['cartao']}:v]format=rgba[cv];[cv][m]alphamerge[cm]")
    f.append(f"[b3][cm]overlay=150:360:shortest=1[b4]")
    f.append(f"[b4][{idx['borda']}:v]overlay=0:0[b5]")
    # título do topo durante a demonstração
    f.append(f"[{idx['topo']}:v]format=rgba,fade=in:st={t0:.2f}:d=0.4:alpha=1,fade=out:st={tfim - 0.3:.2f}:d=0.3:alpha=1[tp]")
    f.append(f"[b5][tp]overlay=0:0[b6]")
    ult = "b6"
    for p, a, b in janelas:
        f.append(f"[{idx[f'passo{p}']}:v]format=rgba,fade=in:st={a:.2f}:d=0.3:alpha=1[p{p}]")
        f.append(f"[{ult}][p{p}]overlay=x='if(lt(t-{a:.2f},0.35),-900+900*(t-{a:.2f})/0.35,0)':y=0:"
                 f"enable='between(t,{a:.2f},{b:.2f})'[q{p}]")
        ult = f"q{p}"
    # gancho no começo
    f.append(f"[{idx['gancho']}:v]format=rgba,fade=out:st={t0 - 0.3:.2f}:d=0.3:alpha=1[gc]")
    f.append(f"[{ult}][gc]overlay=0:0:enable='lt(t,{t0:.2f})'[g1]")
    # selo fixo (some no encerramento, que tem o selo grande)
    f.append(f"[g1][{idx['selo']}:v]overlay=0:0:enable='lt(t,{tfim + 0.5:.2f})'[g2]")
    f.append(f"[{idx[final]}:v]format=rgba,fade=in:st={tfim:.2f}:d=0.5:alpha=1[fn]")
    f.append(f"[g2][fn]overlay=0:0:enable='gte(t,{tfim:.2f})',format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + ins +
                   ["-filter_complex", ";".join(f), "-map", "[v]", "-map", f"{idx['audio']}:a",
                    "-t", f"{total:.2f}", "-r", str(FPS), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-movflags", "+faststart", saida], check=True)
    print(saida, f"{total:.2f}s", janelas)


if __name__ == "__main__":
    etapa = sys.argv[1] if len(sys.argv) > 1 else "tudo"
    if etapa in ("cartao", "tudo"):
        cartao()
    if etapa in ("montar", "tudo"):
        montar("final_reels", f"{D}/pos-facilweb-reels.mp4")
        montar("final_stories", f"{D}/pos-facilweb-stories.mp4")
