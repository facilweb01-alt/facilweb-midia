#!/usr/bin/env python3
"""
hookscore.py - dá nota à primeira linha de um Reel, em português do Brasil,
nas cinco coisas que hooks fortes têm em comum, e ranqueia um lote deles.

O que é:  cinco heurísticas locais, calculadas na sua máquina só a partir do
texto. Medem propriedades que hooks que seguram atenção costumam ter: um
tamanho que se fala em menos de três segundos, algo concreto, algo em jogo, a
carga logo no começo e um espectador para quem a frase aponta.

O que NÃO é:  previsor de views. O original (em inglês) foi testado em 74
hooks reais: separa hook real de hook propositalmente ruim muito bem (AUC 0,83)
e quase não separa os acertos dos erros do mesmo criador (AUC 0,56, onde 0,50
é cara ou coroa). Esta versão aplica a mesma lógica à fala brasileira. Use para
o que ela mede bem: pegar saudação, preâmbulo, hook sem nada concreto e hook
que leva cinco segundos para ser dito. Entre dois hooks decentes, quem decide
é o gráfico de retenção, não este script.

Cada checagem vai de 0 a 100. Maior é melhor.

Uso
  python3 hookscore.py hooks.txt              # um hook por linha, ranqueados
  python3 hookscore.py --hook "Perdi R$18 mil por causa de uma cláusula."
  pbpaste | python3 hookscore.py -
  python3 hookscore.py hooks.txt --json
"""

import argparse
import json
import re
import statistics
import sys

WORD_RE = re.compile(r"[\w$%'’-]+")
NUMBER_RE = re.compile(
    r"R\$\s?\d[\d.,]*(?:\s?(?:mil|k|mi|milhões|milhão))?"         # dinheiro
    r"|\b\d[\d.,]*\s?"                                               # número, com
    r"(?:%|k\b|x\b|mil\b|h\b|hs?\b|horas?\b|min\b|minutos?\b"        # ou sem unidade
    r"|dias?\b|semanas?\b|meses\b|mês\b|anos?\b)?",
    re.IGNORECASE)
PROPER_RE = re.compile(r"(?<!^)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b")
HASHTAG_RE = re.compile(r"(?:^|\s)#\w+")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Hook falado diz o número por extenso. "Vinte mil" é tão concreto quanto
# "R$20.000". "Um/uma" e "primeiro" ficam de fora de propósito: na fala são
# enchimento muito mais vezes do que quantidade.
SPOKEN_NUMBERS = {
    "zero", "dois", "duas", "três", "tres", "quatro", "cinco", "seis", "sete",
    "oito", "nove", "dez", "onze", "doze", "quinze", "vinte", "trinta",
    "quarenta", "cinquenta", "sessenta", "setenta", "oitenta", "noventa",
    "cem", "cento", "duzentos", "trezentos", "quinhentos", "mil", "milhão",
    "milhões", "bilhão", "dúzia", "metade", "dobro", "triplo", "dobrou",
    "triplicou",
}
MONEY_WORDS = {
    "reais", "real", "conto", "contos", "pila", "pilas", "por cento",
    "faturamento", "faturei", "lucro", "salário", "aluguel", "prejuízo",
    "dívida", "dívidas", "multa", "comissão", "lance", "arrematei", "arremate",
}

# Palavras que põem algo em jogo. Hook sem nenhuma é afirmação; com uma, é
# motivo pra continuar assistindo.
STAKES = {
    "pare", "nunca", "errado", "errada", "erro", "erros", "erra",
    "perdi", "perder", "perdendo", "perdeu", "custou", "custa", "custar",
    "quebrei", "quebrou", "falhei", "falhou", "fracasso", "fracassei",
    "ninguém", "ninguem", "não", "nao", "nem", "jamais",
    "larguei", "demiti", "demitido", "apaguei", "apague", "matou", "mata",
    "substituiu", "substitui", "cortei", "corta", "grátis", "gratis",
    "paguei", "cobrei", "cobra", "economizei", "contratei",
    "proibido", "ilegal", "pior", "odeio", "odiava", "desperdicei",
    "desperdício", "golpe", "mentira", "mentiram", "verdade", "segredo",
    "escondido", "escondem", "roubaram", "roubei", "rouba",
    "antes", "até", "mas", "exceto", "problema", "risco", "perigo",
    "cuidado", "arrependo", "arrependi", "deveria", "ainda", "já", "só",
    "sem", "contra", "vs", "versus", "prejuízo", "dívida", "multa", "quase",
    "caro", "barato", "armadilha", "ninguém",
}

# Aberturas que gastam o primeiro segundo sem dizer nada.
WEAK_OPENERS = [
    "oi", "olá", "ola", "e aí", "eai", "fala", "galera", "gente", "pessoal",
    "bom dia", "boa tarde", "boa noite", "salve", "então", "entao", "bom",
    "bem", "hoje", "hoje eu", "basicamente", "sinceramente", "olha só",
    "tipo", "é", "ah", "eu queria", "eu quero", "eu vou", "vou falar",
    "vou te", "um dos", "uma das", "você sabia", "vc sabia", "vocês sabiam",
    "sabia que", "neste", "nesse", "no vídeo", "a questão", "muita gente",
    "existe", "existem", "isso é", "esse é", "quando se", "se você já",
    "sabe", "vamos", "bora",
]

# Imperativos que merecem a primeira posição.
IMPERATIVES = {
    "pare", "rouba", "roube", "copia", "copie", "apaga", "apague",
    "testa", "teste", "assiste", "assista", "lê", "leia", "salva", "salve",
    "usa", "use", "faz", "faça", "escreve", "escreva", "manda", "mande",
    "começa", "comece", "larga", "nunca", "sempre", "não", "olha",
    "olhe", "veja", "confere", "confira", "anota", "anote", "esquece",
    "esqueça", "cobra", "cobre", "chega",
}

DEALBREAKERS = [
    (re.compile(r"(?i)^\s*(?:para de rolar|pare de rolar|não role|não passa|não pula|para tudo|espera,? não)"),
     "Abre com \"para de rolar\". Pedir atenção prova que você ainda não ganhou."),
    (re.compile(r"(?i)\b(?:n[eo]ss?e vídeo|n[eo]ste vídeo|no vídeo de hoje|n[eo]ss?e reels?|hoje eu vou (?:te |lhes? )?(?:mostrar|ensinar|falar)|vou (?:te |lhes? )?(?:mostrar|ensinar) como)\b"),
     "Preâmbulo de vídeo. Apague e abra direto na entrega."),
    (re.compile(r"(?i)^\s*(?:oi|olá|ola|e aí|eai|fala,? (?:galera|pessoal|gente)|bom dia|boa tarde|boa noite|salve|tudo bem)\b"),
     "Saudação. Ninguém abriu o feed pra ser cumprimentado."),
    (HASHTAG_RE,
     "Hashtag no hook. Hashtag vai no fim da legenda, se for."),
    (EMOJI_RE,
     "Emoji no hook. Texto de tela no tamanho de hook tem espaço pra palavra ou pra emoji, não pros dois."),
]


def clamp(n):
    return max(0.0, min(100.0, n))


def normalise(text):
    # "R$18.000" e "18,000" são uma palavra só quando faladas.
    return re.sub(r"(?<=\d)[.,](?=\d{3}\b)", "", text)


def words(text):
    return WORD_RE.findall(normalise(text))


def low_words(text):
    return [w.lower().strip("'’-") for w in words(text)]


def check_length(text):
    """O hook precisa chegar antes do dedo se mexer. Uns dois segundos."""
    n = len(words(text))
    secs = n / 2.5                       # ~150 palavras por minuto em PT-BR
    chars = len(text.strip())
    if 5 <= n <= 12:
        score = 100.0
    elif n < 5:
        score = clamp(100 - (5 - n) * 20)
    else:
        score = clamp(100 - (n - 12) * 11)
    if chars > 65:                       # duas linhas de texto grande na tela
        score -= 12
    return clamp(score), f"{n} palavras, {chars} caracteres, ~{secs:.1f}s falado (ideal 5 a 12 palavras)"


def check_specificity(text):
    """Uma coisa concreta vale mais que três abstratas."""
    nums = [n.strip() for n in NUMBER_RE.findall(text) if n.strip()]
    propers = set(PROPER_RE.findall(text))
    low = low_words(text)
    spoken = [w for w in low if w in SPOKEN_NUMBERS or w in MONEY_WORDS]
    hits = len(nums) + len(propers) + len(spoken)
    score = 15.0 if hits == 0 else clamp(45 + hits * 30)
    found = ", ".join(nums[:2] + sorted(propers)[:2] + spoken[:2])
    return score, (f"{hits} marcador(es) concreto(s)" + (f": {found}" if found else
                   " - sem número, sem nome, nada verificável"))


def check_stakes(text):
    """Tensão, custo, negação. Algo que o espectador pode perder."""
    markers = sorted(set(x for x in low_words(text) if x in STAKES))
    if re.search(r"R\$\s?\d", text):
        markers.append("um preço")
    n = len(markers)
    score = {0: 20.0, 1: 70.0}.get(n, 100.0)
    detail = f"{n} marcador(es) de tensão" + (f": {', '.join(markers[:4])}" if markers else
                                             " - nada está em jogo nesta linha")
    return clamp(score), detail


def check_frontload(text):
    """A palavra interessante não pode estar na posição nove."""
    w = words(text)
    if not w:
        return 0.0, "vazio"
    low = [x.lower().strip("'’-") for x in w]
    opener = " ".join(low[:2])
    penalty, hit_opener = 0, None
    for weak in WEAK_OPENERS:
        if opener == weak or opener.startswith(weak + " ") or low[0] == weak:
            penalty, hit_opener = 30, weak
            break
    payload = None
    for i, token in enumerate(low):
        if (token in STAKES or token in SPOKEN_NUMBERS or token in MONEY_WORDS
                or re.match(r"(?:r\$)?\d", token) or (i and PROPER_RE.match(w[i]))):
            payload = i
            break
    if payload is None:
        base, where = 30.0, "nenhuma palavra de carga na linha"
    elif payload <= 3:
        base, where = 100.0, f"carga na palavra {payload + 1}"
    elif payload <= 6:
        base, where = 70.0, f"carga na palavra {payload + 1}, dá pra puxar pra frente"
    else:
        base, where = 40.0, f"carga na palavra {payload + 1}, tarde demais"
    detail = where + (f"; abertura fraca \"{hit_opener}\"" if hit_opener else "")
    return clamp(base - penalty), detail


def check_address(text):
    """Aponta pra um espectador, ou fica solto no ar."""
    low = text.lower()
    w = low_words(text)
    if re.search(r"\b(?:você|voce|vc|cê|ce|seu|sua|seus|suas|te|teu|tua|contigo)\b", low):
        return 100.0, "fala com o espectador"
    if w and w[0] in IMPERATIVES:
        return 90.0, f"abre no imperativo (\"{w[0]}\")"
    if re.search(r"\b(?:eu|meu|minha|meus|minhas|me|comigo|nós|nosso|nossa|a gente)\b", low) \
            or re.match(r"^\s*(?:perdi|ganhei|fiz|paguei|cobrei|arrematei|comprei|vendi|postei|testei|errei|passei|levei)\b", low):
        return 70.0, "primeira pessoa, sem espectador nomeado"
    return 35.0, "terceira pessoa, ninguém na sala"


CHECKS = ["TAMANHO", "CONCRETUDE", "TENSÃO", "ABERTURA", "ALVO"]


def run(text):
    results = {
        "TAMANHO": check_length(text),
        "CONCRETUDE": check_specificity(text),
        "TENSÃO": check_stakes(text),
        "ABERTURA": check_frontload(text),
        "ALVO": check_address(text),
    }
    flags = [msg for pattern, msg in DEALBREAKERS if pattern.search(text)]
    scores = [results[c][0] for c in CHECKS]
    # A propriedade mais fraca limita o hook: basta uma ruim pro dedo seguir.
    overall = clamp(statistics.mean(scores) * 0.6 + min(scores) * 0.4 - len(flags) * 15)
    verdict = "FORTE" if overall >= 70 and min(scores) >= 55 and not flags else (
        "OK" if overall >= 50 else "FRACO")
    return results, overall, verdict, flags


def bar(score, width=24):
    filled = round(score / 100 * width)
    return "#" * filled + "." * (width - filled)


def render_one(text, results, overall, verdict, flags, out=sys.stdout):
    print("\nNOTA DO HOOK", file=out)
    print("=" * 62, file=out)
    print(f"  \"{text.strip()}\"\n", file=out)
    for name in CHECKS:
        score, detail = results[name]
        print(f"  {name:<11} {bar(score)} {score:5.1f}", file=out)
        print(f"  {'':<11} {detail}", file=out)
    print("-" * 62, file=out)
    print(f"  {'NOTA':<11} {bar(overall)} {overall:5.1f}   {verdict}", file=out)
    for f in flags:
        print(f"\n  ELIMINATÓRIO  {f}", file=out)
    if verdict != "FORTE":
        weakest = min(CHECKS, key=lambda c: results[c][0])
        print(f"\n  Propriedade mais fraca: {weakest}. Corrija essa e rode de novo.", file=out)
    print("", file=out)


def render_table(rows, out=sys.stdout):
    print("\nRANKING DE HOOKS\n" + "=" * 78, file=out)
    for i, r in enumerate(rows, 1):
        mark = "->" if i == 1 else "  "
        hook = r["hook"] if len(r["hook"]) <= 62 else r["hook"][:59] + "..."
        print(f"{mark} {r['score']:5.1f} {r['verdict']:<6} {hook}", file=out)
        print(f"        mais fraca: {r['weakest']} ({r['checks'][r['weakest']]['score']:.0f})", file=out)
        for f in r["flags"]:
            print(f"        eliminatório: {f}", file=out)
    print("\nGrave o primeiro. Se o primeiro está abaixo de 50, nenhum desses é o hook.\n",
          file=out)


def main():
    ap = argparse.ArgumentParser(description="Nota de hook de Reel em cinco propriedades (PT-BR).")
    ap.add_argument("input", nargs="?", default="-", help="arquivo com um hook por linha, ou -")
    ap.add_argument("--hook", help="avalia um único hook passado na linha de comando")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.hook:
        lines = [args.hook]
    else:
        raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
        lines = [l.strip() for l in raw.splitlines() if l.strip()]
    if not lines:
        print("nada para avaliar", file=sys.stderr)
        sys.exit(2)

    payload = []
    for line in lines:
        results, overall, verdict, flags = run(line)
        payload.append({
            "hook": line,
            "checks": {k: {"score": round(v[0], 1), "detail": v[1]} for k, v in results.items()},
            "weakest": min(CHECKS, key=lambda c: results[c][0]),
            "flags": flags,
            "score": round(overall, 1),
            "verdict": verdict,
        })

    if args.json:
        print(json.dumps(payload if len(payload) > 1 else payload[0], indent=2, ensure_ascii=False))
        return

    if len(payload) == 1:
        render_one(lines[0], *run(lines[0]))
    else:
        render_table(sorted(payload, key=lambda r: -r["score"]))

    sys.exit(0 if max(p["score"] for p in payload) >= 70 else 1)


if __name__ == "__main__":
    main()
