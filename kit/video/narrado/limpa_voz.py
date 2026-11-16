"""Remove das legendas o texto de pronúncia (<sub alias="uótsap">WhatsApp</sub>) que vaza nos limites de palavra.
Uso: python3 kit/video/narrado/limpa_voz.py r1/voz.json  (rode depois do voz.py quando o SSML tiver <sub alias>)
Acrescente na lista PRONUNCIAS os apelidos que você usar."""
import json, re, sys
PRONUNCIAS = {"uótsap", "uotsap"}  # apelidos de pronúncia usados nos <sub alias>
f = sys.argv[1]; d = json.load(open(f)); out = []
for w in d["palavras"]:
    t = w["w"]
    if t.strip().lower() in PRONUNCIAS: continue
    t = re.sub(r'^[^>]*">\s*', "", t).replace('">', "")
    for a in PRONUNCIAS: t = re.sub(rf"\b{a}\s*", "", t)
    t = t.strip()
    if t: out.append(dict(w, w=t))
d["palavras"] = out; json.dump(d, open(f, "w"), ensure_ascii=False, indent=1)
print(" ".join(w["w"] for w in out))
