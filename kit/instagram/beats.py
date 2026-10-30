#!/usr/bin/env python3
"""
beats.py - transforma um roteiro de Reel em português num beat sheet
cronometrado, antes de você gravar.

Estima quanto tempo cada linha leva pra ser dita, empilha em timecodes e
aponta as quatro coisas que matam um Reel na edição: hook que passa dos três
segundos, beat longo o bastante pro espectador sair, sequência de linhas sem
nada concreto e duração que não bate com o que você disse que ia fazer.

Os tempos são estimativa por contagem de palavras numa velocidade de fala. Dá
pra planejar a edição, não substitui gravar. O padrão aqui é 150 palavras por
minuto, que é uma fala brasileira natural (o português tem palavras mais
longas que o inglês). Cronometre você lendo um roteiro em voz alta e ajuste
com --wpm: a maioria das pessoas fica entre 130 e 180.

Uso
  python3 beats.py roteiro.txt
  python3 beats.py roteiro.txt --target 30
  python3 beats.py roteiro.txt --wpm 170 --target 45
  pbpaste | python3 beats.py -
  python3 beats.py roteiro.txt --json
"""

import argparse
import json
import re
import sys

WORD_RE = re.compile(r"[\w$%'’-]+")
SENT_RE = re.compile(r"[^.!?]+[.!?]*")
CONCRETE_RE = re.compile(r"R\$\s?\d|\b\d[\d.,]*\b|(?<!^)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b", re.MULTILINE)
SPOKEN_CONCRETE = re.compile(
    r"(?i)\b(?:dois|duas|três|quatro|cinco|seis|sete|oito|nove|dez|vinte|trinta|"
    r"quarenta|cinquenta|cem|mil|milhão|milhões|metade|dobro|reais)\b")
STOPWORDS = {
    "o", "a", "os", "as", "um", "uma", "uns", "umas", "e", "ou", "mas", "se",
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas", "por",
    "pelo", "pela", "pra", "pro", "para", "com", "sem", "que", "isso", "esse",
    "essa", "este", "esta", "aqui", "ali", "é", "foi", "era", "ser", "tá",
    "está", "são", "eu", "me", "meu", "minha", "você", "vc", "cê", "seu",
    "sua", "te", "a gente", "nós", "eles", "elas", "ele", "ela", "lhe", "não",
    "sim", "já", "só", "tem", "ter", "tinha", "vai", "vou", "faz", "fazer",
    "como", "quando", "mais", "muito", "tudo", "todo", "toda", "aí", "então",
    "né", "também", "ao", "à", "às", "aos",
}

HOOK_WINDOW = 3.0        # segundos. Depois disso o dedo já decidiu.
MAX_BEAT = 4.0           # segundos numa ideia sem mudança na tela.
ABSTRACT_RUN = 3         # beats seguidos sem nada verificável.


def normalise(text):
    # "R$18.000" é uma palavra só quando falado.
    return re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", text)


def words(text):
    return WORD_RE.findall(normalise(text))


def pretty(token):
    """Devolve o separador de milhar brasileiro para exibição."""
    return re.sub(r"(\d)(?=(\d{3})+$)", r"\1.", token)


def tc(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m)}:{s:04.1f}"


def concrete(text):
    return len(CONCRETE_RE.findall(text)) + len(SPOKEN_CONCRETE.findall(text))


def split_beats(raw, wps):
    """Uma linha é um beat, a não ser que seja longa demais pra ser um."""
    beats = []
    for line in [l.strip() for l in raw.splitlines()]:
        if not line:
            continue
        if len(words(line)) / wps <= MAX_BEAT * 1.5:
            beats.append(line)
            continue
        parts = [p.strip() for p in SENT_RE.findall(line) if p.strip()]
        buf = ""
        for part in parts:
            candidate = (buf + " " + part).strip()
            if buf and len(words(candidate)) / wps > MAX_BEAT:
                beats.append(buf)
                buf = part
            else:
                buf = candidate
        if buf:
            beats.append(buf)
    return beats


def analyse(raw, wpm=150, target=None):
    wps = wpm / 60.0
    beats = split_beats(raw, wps)
    if not beats:
        return None

    rows, clock = [], 0.0
    for i, text in enumerate(beats):
        n = len(words(text))
        dur = n / wps
        rows.append({"n": i + 1, "start": round(clock, 2), "dur": round(dur, 2), "words": n,
                     "text": text, "concrete": concrete(text), "label": "", "flags": []})
        clock += dur
    total = clock

    for r in rows:
        if r["n"] == 1 or r["start"] + r["dur"] <= HOOK_WINDOW:
            r["label"] = "HOOK"
    rows[-1]["label"] = "CTA" if rows[-1]["label"] != "HOOK" else "HOOK/CTA"
    half = total / 2
    for r in rows:
        if not r["label"] and r["start"] <= half < r["start"] + r["dur"]:
            r["label"] = "MEIO"

    notes = []
    if rows[0]["dur"] > HOOK_WINDOW:
        rows[0]["flags"].append(f"hook leva {rows[0]['dur']:.1f}s, passa dos {HOOK_WINDOW:.0f}s")
        notes.append(f"O beat 1 leva {rows[0]['dur']:.1f}s pra ser dito. Corte pra "
                     f"{int(HOOK_WINDOW * wps)} palavras ou menos, senão o hook chega depois "
                     "que a decisão já foi tomada.")
    if rows[0]["concrete"] == 0:
        notes.append("O beat 1 não tem número nem nome. Hook sem nada verificável é o que "
                     "leva scroll.")

    for r in rows:
        if r["dur"] > MAX_BEAT:
            r["flags"].append(f"{r['dur']:.1f}s num beat só")
    long_beats = [r["n"] for r in rows if r["dur"] > MAX_BEAT]
    if long_beats:
        notes.append(f"Beat(s) {', '.join(map(str, long_beats))} passam de {MAX_BEAT:.0f}s. "
                     "Divida a linha ou mude o que está na tela no meio dela. "
                     "Quadro parado é onde as pessoas saem.")

    run, start = 0, None
    for r in rows:
        if r["concrete"] == 0:
            run += 1
            start = start if start is not None else r["n"]
            if run == ABSTRACT_RUN:
                notes.append(f"Os beats {start} a {r['n']} não têm nada concreto. "
                             "Coloque um número, um nome ou um preço em um deles.")
        else:
            run, start = 0, None

    first = {w.lower() for w in words(rows[0]["text"]) if w.lower() not in STOPWORDS}
    last = {w.lower() for w in words(rows[-1]["text"]) if w.lower() not in STOPWORDS}
    loop = sorted(pretty(w) for w in first & last)
    if loop:
        notes.append(f"Loop: o último beat repete \"{', '.join(loop[:3])}\" do hook. "
                     "Segunda visualização é alcance de graça.")
    else:
        notes.append("Sem loop. O último beat não repete nenhuma palavra do hook, então o "
                     "vídeo termina chapado. Ecoar uma palavra do beat 1 é o replay mais barato que existe.")

    if target:
        delta = total - target
        if abs(delta) <= target * 0.1:
            notes.append(f"Duração no alvo ({total:.1f}s contra {target:g}s).")
        elif delta > 0:
            notes.append(f"{delta:.1f}s acima do alvo. Corte umas {int(delta * wps)} palavras.")
        else:
            notes.append(f"{-delta:.1f}s abaixo do alvo. Acrescente {int(-delta * wps)} palavras "
                         "ou grave curto. Curto costuma ser o certo.")

    return {"wpm": wpm, "target": target, "total_seconds": round(total, 2),
            "total_words": sum(r["words"] for r in rows), "beats": rows, "notes": notes}


def render(a, out=sys.stdout):
    head = (f"BEAT SHEET  ·  {a['total_words']} palavras  ·  ~{a['total_seconds']:.1f}s "
            f"a {a['wpm']:g} ppm" + (f"  ·  alvo {a['target']:g}s" if a["target"] else ""))
    print("\n" + head, file=out)
    print("=" * max(len(head), 72), file=out)
    for r in a["beats"]:
        label = f"{r['label']:<8}" if r["label"] else " " * 8
        print(f"  {tc(r['start'])}  {r['dur']:4.1f}s  {label}{r['text']}", file=out)
        for f in r["flags"]:
            print(f"  {'':>6}  {'':>5}  {'':<8}^ {f}", file=out)
    print("-" * max(len(head), 72), file=out)
    for n in a["notes"]:
        print(f"  - {n}", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Cronometra um roteiro de Reel em beat sheet (PT-BR).")
    ap.add_argument("input", nargs="?", default="-", help="arquivo do roteiro, ou - para stdin")
    ap.add_argument("--wpm", type=float, default=150, help="palavras por minuto (padrão 150)")
    ap.add_argument("--target", type=float, help="duração alvo em segundos")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, wpm=args.wpm, target=args.target)
    if not a:
        print("roteiro vazio", file=sys.stderr)
        sys.exit(2)
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0)


if __name__ == "__main__":
    main()
