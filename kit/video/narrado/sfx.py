"""Planeja os efeitos sonoros do OpusClip a partir do tl.json que o cine.py gera.
Uso: python3 kit/video/narrado/sfx.py r1 > r1/sfx.json   (depois: place_sound_effects com essa lista)
Regras: punch no 1º quadro, whoosh nas viradas, impacto suave nas cenas de marca, obturador nas palavras de flash,
pop nos cartões azuis (até 2), braam na logo final; 600 ms entre efeitos e no máximo duração/2,5.
Confira os sound_id com list_sound_effects (a biblioteca muda de versão)."""
import json, sys
r = sys.argv[1]
tl = json.load(open(f"{r}/tl.json"))
PUNCH, SOFT, SNAP, SMOOTH, POP, POP3, SHUT, BRAAM = "9bd4187c", "cd08d737", "2b2f7db3", "5c40f0a3", "f7d9554f", "e1c045f5", "4980ac04", "4005db58"
hits = [dict(sound_id=PUNCH, at_ms=60, anchor="first_hit")]
cenas = tl["cenas"]
for i, c in enumerate(cenas[1:], 1):
    a = int(c["a"] * 1000)
    if c["tipo"] == "fim":
        hits.append(dict(sound_id=BRAAM, at_ms=a + 70, anchor="peak")); continue
    if c["tipo"] == "marca":
        hits.append(dict(sound_id=SOFT, at_ms=a + 10, anchor="first_hit")); continue
    hits.append(dict(sound_id=SNAP if i % 2 else SMOOTH, at_ms=a, anchor="first_hit"))
for w in tl["palavras"]:
    if w["w"].lower().strip(".,?!") in tl.get("flashPal", []):
        hits.append(dict(sound_id=SHUT, at_ms=int(w["a"] * 1000) + 10, anchor="first_hit"))
# pops: o card azul (número grande) de até 2 cenas de celular
n = 0
for c in cenas:
    if c["tipo"] != "phone" or n >= 2: continue
    for k in c.get("cards", []):
        if k.get("azul"):
            hits.append(dict(sound_id=POP3 if n else POP, at_ms=int((c["a"] + k["t"] * (c["b"] - c["a"])) * 1000) + 30, anchor="first_hit", gain_db=-3)); n += 1; break
hits.sort(key=lambda h: h["at_ms"])
ok = []
for h in hits:  # mínimo de 600 ms entre efeitos (o pesado ganha)
    if ok and h["at_ms"] - ok[-1]["at_ms"] < 600:
        if h["sound_id"] in (BRAAM, SHUT): ok[-1] = h
        continue
    ok.append(h)
lim = int(tl["total"] / 2.5)
while len(ok) > lim:
    pops = [h for h in ok if h["sound_id"] in (POP, POP3)]
    if not pops: break
    ok.remove(pops[-1])
print(json.dumps(ok))
