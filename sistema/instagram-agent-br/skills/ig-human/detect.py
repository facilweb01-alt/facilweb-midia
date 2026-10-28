#!/usr/bin/env python3
"""
detect.py - painel de cinco checagens que dá nota a quanto um rascunho em
português parece escrito por máquina.

O que é:  cinco heurísticas locais inspiradas nos sinais que detectores
públicos de IA medem: variação no tamanho das frases, concretude, vocabulário
pronto, impressão digital tipográfica e voz. Tudo é calculado na sua máquina,
só a partir do texto. Nada é enviado.

O que NÃO é:  GPTZero, Originality, Copyleaks, Winston ou Turnitin. Não chama
essas APIs e não promete o veredito delas. Pega as coisas em que todas se
baseiam, e por isso corrigi-las costuma mexer nos números delas também, mas a
única afirmação honesta é a desta linha.

A VOZ em português não usa contrações do inglês ("don't"): mede marcas de
oralidade brasileira ("pra", "tá", "a gente", "né") e pessoa gramatical.

Cada checagem devolve uma nota HUMANA de 0 a 100. Maior é melhor.

Uso
  python3 detect.py rascunho.txt
  pbpaste | python3 detect.py -
  python3 detect.py rascunho.txt --json
  python3 detect.py antes.txt depois.txt      # compara dois rascunhos
"""

import argparse
import json
import os
import re
import statistics
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LEX = os.path.join(HERE, "slop.json")

SENT_RE = re.compile(r"[^.!?\n]+[.!?]*")
WORD_RE = re.compile(r"[^\W\d_]+(?:['’-][^\W\d_]+)*")
# Marcas de oralidade: o equivalente brasileiro das contrações do inglês.
ORAL = re.compile(r"(?<!\w)(?:pra|pro|pros|pras|prum|pruma|tá|tô|tava|tamo|tão|cê|né|a gente|"
                  r"aí|daí|tipo|beleza|vc|vcs|tb|tbm|nossa|olha|sabe|cara|bora|vamo|"
                  r"tranquilo|ué|poxa|caramba|enfim|pois é)(?!\w)", re.IGNORECASE)
PRONOUNS = re.compile(r"(?<!\w)(?:eu|me|meu|minha|meus|minhas|comigo|nós|nosso|nossa|nossos|"
                      r"a gente|você|vocês|vc|cê|seu|sua|seus|suas|te|teu|tua|contigo)(?!\w)",
                      re.IGNORECASE)
NUMBERS = re.compile(r"R\$\s?\d|\b\d[\d.,]*%?|\b(?:mil|milhão|milhões|metade|dobro)\b",
                     re.IGNORECASE)
PROPER = re.compile(r"(?<![.!?]\s)(?<!^)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b", re.MULTILINE)


def clamp(n):
    return max(0.0, min(100.0, n))


def scale(value, human, machine):
    """Map value onto 0-100 where `human` -> 100 and `machine` -> 0."""
    if human == machine:
        return 50.0
    return clamp((value - machine) / (human - machine) * 100)


def sentences(text):
    return [s.strip() for s in SENT_RE.findall(text) if len(s.split()) > 2]


def words(text):
    return WORD_RE.findall(text)


def check_burstiness(text):
    """Humans vary sentence length hard. Models write even."""
    lens = [len(s.split()) for s in sentences(text)]
    if len(lens) < 4:
        return 50.0, "curto demais pra julgar"
    mean = statistics.mean(lens)
    cv = statistics.pstdev(lens) / mean if mean else 0
    score = scale(cv, human=0.70, machine=0.22)
    return score, f"variação {cv:.2f} em {len(lens)} frases (ideal 0,55+)"


def check_specificity(text):
    """Numbers, names and concrete nouns. Slop is abstract."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "curto demais pra julgar"
    per100 = 100 / len(w)
    hits = len(NUMBERS.findall(text)) + len(set(PROPER.findall(text)))
    density = hits * per100
    score = scale(density, human=6.0, machine=0.5)
    return score, f"{hits} marcadores concretos, {density:.1f} a cada 100 palavras (ideal 4+)"


def check_slop(text, lex):
    """Stock vocabulary density against the lexicon."""
    w = words(text)
    if not w:
        return 50.0, "vazio"
    hits, found = 0, []
    for entry in lex["words"] + lex["phrases"]:
        pattern = re.compile(r"(?<!\w)" + re.escape(entry["find"]).replace(r"\ ", r"\s+") + r"(?!\w)",
                             re.IGNORECASE)
        n = len(pattern.findall(text))
        if n:
            hits += n
            found.append(entry["find"])
    density = hits * 100 / len(w)
    score = scale(density, human=0.0, machine=4.0)
    detail = f"{hits} termos prontos, {density:.1f} a cada 100 palavras"
    if found:
        detail += " (" + ", ".join(sorted(found)[:4]) + (", ..." if len(found) > 4 else "") + ")"
    return score, detail


def check_fingerprint(text):
    """Characters a phone keyboard does not produce."""
    invisible = sum(1 for c in text if unicodedata.category(c) == "Cf")
    em = text.count("—")
    curly = sum(text.count(c) for c in "‘’“”")
    ellip = text.count("…")
    nbsp = sum(text.count(c) for c in "   ")
    total = invisible * 4 + em * 2 + curly + ellip + nbsp
    per1k = total * 1000 / max(len(text), 1)
    score = scale(per1k, human=0.0, machine=12.0)
    detail = (f"{invisible} invisível, {em} travessão, {curly} aspa curva, "
              f"{ellip} reticências, {nbsp} espaço rígido")
    return score, detail


def check_voice(text, lex):
    """Oralidade, pessoa e os formatos que modelos usam por padrão."""
    w = words(text)
    if len(w) < 25:
        return 50.0, "curto demais pra julgar"
    per100 = 100 / len(w)
    contractions = len(ORAL.findall(text)) * per100
    person = len(PRONOUNS.findall(text)) * per100
    tells = 0
    names = []
    for s in lex["structures"]:
        try:
            n = len(re.compile(s["regex"], re.MULTILINE).findall(text))
        except re.error:
            continue
        if n:
            tells += n
            names.append(s["id"])
    bullets = [len(b.split()) for b in re.findall(r"(?m)^\s*[-*•]\s+(.+)$", text)]
    uniform = (len(bullets) >= 3 and statistics.pstdev(bullets) < 1.6)
    score = (scale(contractions, human=2.0, machine=0.0) * 0.30
             + scale(person, human=6.0, machine=1.0) * 0.40
             + clamp(100 - tells * 22) * 0.30)
    if uniform:
        score -= 12
        names.append("marcadores-iguais")
    detail = (f"{contractions:.1f} marcas de oralidade, {person:.1f} pronomes pessoais "
              f"a cada 100 palavras, {tells} tique(s) estrutural(is)")
    if names:
        detail += " [" + ", ".join(names[:4]) + "]"
    return clamp(score), detail


CHECKS = ["VARIAÇÃO", "CONCRETUDE", "CLICHÊS", "DIGITAL", "VOZ"]


def run(text, lex):
    results = {}
    results["VARIAÇÃO"] = check_burstiness(text)
    results["CONCRETUDE"] = check_specificity(text)
    results["CLICHÊS"] = check_slop(text, lex)
    results["DIGITAL"] = check_fingerprint(text)
    results["VOZ"] = check_voice(text, lex)
    scores = [results[c][0] for c in CHECKS]
    # The weakest check drags the verdict: a detector only needs one signal.
    overall = statistics.mean(scores) * 0.6 + min(scores) * 0.4
    verdict = "APROVADO" if overall >= 70 and min(scores) >= 55 else (
        "REVISAR" if overall >= 50 else "SINALIZADO")
    return results, overall, verdict


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render(results, overall, verdict, label=None, out=sys.stdout):
    title = "PAINEL DE DETECÇÃO DE IA" + (f"  -  {label}" if label else "")
    print("\n" + title, file=out)
    print("=" * max(len(title), 62), file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<13} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<13} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'NOTA HUMANA':<13} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    if verdict != "APROVADO":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Sinal mais fraco: {weakest}. Corrija esse primeiro.", file=out)
    print("", file=out)


def main():
    ap = argparse.ArgumentParser(description="Nota de quanto um rascunho parece escrito por máquina (PT-BR).")
    ap.add_argument("input", nargs="?", default="-", help="arquivo, ou - para stdin")
    ap.add_argument("compare", nargs="?", help="segundo arquivo, para mostrar antes/depois")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--lexicon", default=LEX)
    args = ap.parse_args()

    lex = json.load(open(args.lexicon, encoding="utf-8"))
    read = lambda p: sys.stdin.read() if p == "-" else open(p, encoding="utf-8").read()

    targets = [(args.input, read(args.input))]
    if args.compare:
        targets.append((args.compare, read(args.compare)))

    payload = []
    for name, text in targets:
        results, overall, verdict = run(text, lex)
        payload.append({
            "source": name,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "human_score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if args.compare else payload[0], indent=2, ensure_ascii=False))
        return

    for (name, text), p in zip(targets, payload):
        results, overall, verdict = run(text, lex)
        render(results, overall, verdict, label=os.path.basename(name) if args.compare else None)
    if args.compare:
        a, b = payload
        delta = b["human_score"] - a["human_score"]
        print(f"  {a['human_score']:.1f} {a['verdict']}  ->  "
              f"{b['human_score']:.1f} {b['verdict']}   ({delta:+.1f})\n")

    sys.exit(0 if payload[-1]["verdict"] == "APROVADO" else 1)


if __name__ == "__main__":
    main()
