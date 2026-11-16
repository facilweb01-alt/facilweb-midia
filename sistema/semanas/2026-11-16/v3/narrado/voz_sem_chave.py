"""Tempos de narração estimados (sem a chave do Azure): gera voz.json com palavras e bookmarks e um voz.wav mudo,
para o cine.py montar legenda e cenas. Quando a chave chegar, rode kit/video/narrado/voz.py no mesmo SSML.
Uso: python3 voz_sem_chave.py r1/voz.ssml r1/voz.wav r1/voz.json"""
import re, sys, json, wave
ssml, wav, js = sys.argv[1:4]
txt = open(ssml).read()
txt = re.sub(r'<sub alias="[^"]*">([^<]*)</sub>', r'\1', txt)
partes = re.split(r'<bookmark mark="(s\d+)"/>', txt)
t, pal, bm = 0.15, [], []
for i in range(1, len(partes), 2):
    bm.append({"nome": partes[i], "t": round(t, 3)})
    frase = re.sub(r"<[^>]+>", " ", partes[i + 1]).split()
    for w in frase:
        d = 0.1 + 0.044 * len(w)
        pal.append({"w": w, "a": round(t, 3), "d": round(d, 3)})
        t += d + (0.28 if re.search(r"[.?!]$", w) else 0.1 if w.endswith(",") else 0.03)
    t += 0.2
dur = round(t + 0.2, 3)
with wave.open(wav, "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(48000); f.writeframes(b"\0\0" * int(48000 * dur))
json.dump({"palavras": pal, "marcas": bm, "dur": dur}, open(js, "w"), ensure_ascii=False, indent=1)
print("ok", len(pal), "palavras", dur, "s (estimado, sem voz)")
