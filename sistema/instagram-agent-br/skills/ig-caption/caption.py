#!/usr/bin/env python3
"""
caption.py - revisa uma legenda de Instagram em português e mostra exatamente
o que o feed mostra antes do "... mais".

O Instagram mostra uns 125 caracteres da legenda no feed e esconde o resto
atrás de um toque. Quase toda legenda que falha, falha ali: o hook está na
terceira frase, a primeira linha é um cumprimento, ou tudo abre numa hashtag.
Este script imprime essa janela numa caixa, para você ler como um desconhecido
rolando o feed, e depois faz as checagens que valem a pena.

O corte em 125 é aproximado. O número real muda com o aparelho, o tamanho da
fonte e onde caem as quebras de linha, e por isso você quer margem, não uma
legenda que termina exatamente no 125. Teste outro corte com --truncate.

Uso
  python3 caption.py legenda.txt
  python3 caption.py legenda.txt --keywords "leilão de imóveis,edital"
  pbpaste | python3 caption.py -
  python3 caption.py legenda.txt --json
"""

import argparse
import json
import re
import sys
import textwrap
import unicodedata

LIMIT = 2200             # limite rígido de legenda do Instagram.
TRUNCATE = 125           # mais ou menos onde o feed corta para "... mais".
HASHTAG_LIMIT = 5        # limite por post ou reel desde 18/12/2025 (antes era 30),
                         # anunciado pela conta @creators do Instagram.

HASHTAG_RE = re.compile(r"(?:^|\s)(#\w+)")
MENTION_RE = re.compile(r"(?:^|\s)(@[\w.]+)")
LINK_RE = re.compile(r"https?://\S+|\bwww\.\S+|\bwa\.me/\S*|\b[a-z0-9-]+\.(?:com\.br|com|net\.br|org\.br|br|co|io|net|org|ai|app|link)(?:/\S*)?\b",
                     re.IGNORECASE)
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿←-⇿️]")
CONCRETE_RE = re.compile(r"R\$\s?\d|\b\d[\d.,]*\b|(?<!^)\b[A-ZÀ-Ý][a-zà-ÿ]{2,}\b", re.MULTILINE)
UP = "A-ZÀÁÂÃÉÊÍÓÔÕÚÇ0-9"

ASKS = [
    (re.compile(r"\b(?i:coment[ae]r?|escrev[ae]|digit[ae]|mand[ae])\s+(?:(?i:a palavra|aqui|aí|só)\s+)?[\"“'«]?[" + UP + r"]{2,}\b"),
     "comentar palavra-chave"),
    (re.compile(r"(?i)\b(?:me )?(?:manda|mande|envia|envie) (?:um |uma )?(?:direct|dm|mensagem|inbox|direct pra mim)\b|\b(?:me )?chama no (?:direct|dm|privado|pv|whats|whatsapp|zap)\b|\bclica no botão (?:do )?whats\w*\b"),
     "chamar no direct/WhatsApp"),
    (re.compile(r"(?i)\bcham[ae] (?:a gente|nossa equipe|o time|nosso time|a equipe)?\s*no (?:direct|dm|whats|whatsapp|zap)\b|\bfale com (?:a gente|nossa equipe|um consultor)\b"),
     "chamar a equipe"),
    (re.compile(r"(?i)\b(?:solicite|solicita|peça|pede|agende|agenda|marque|marca) (?:já )?(?:uma |sua |a sua )?(?:demonstração|demo|teste|avaliação|visita|orçamento)\b|\bteste grátis\b"),
     "pedir demonstração/orçamento"),
    (re.compile(r"(?i)\bsalv[ae]r? (?:esse|este|essa|esta|o post|o vídeo|o carrossel|pra depois|para depois|aí)\b"),
     "salvar"),
    (re.compile(r"(?i)\bcompartilh[ae]r? (?:com|esse|este|essa|esta)\b|\b(?:manda|envia) (?:pra|para) (?:quem|alguém|aquele|aquela|um amigo|uma amiga|seu sócio)\b"),
     "compartilhar/enviar"),
    (re.compile(r"(?i)\bme segue\b|\bsegue (?:o perfil|a página|pra mais|para mais)\b|\bsiga (?:o perfil|@)"),
     "seguir"),
    (re.compile(r"(?i)\blink na (?:minha )?bio\b|\b(?:clica|clique|toca|toque) no link\b"),
     "link na bio"),
    (re.compile(r"(?i)\b(?:arrasta|arraste|desliza|deslize|passa|passe) (?:pro lado|para o lado|pra cima|pro próximo)\b"),
     "arrastar"),
    (re.compile(r"(?i)\bme (?:conta|diz|fala)\b|\bqual (?:você|vc) (?:escolheria|prefere|faria)\b|\be (?:você|vc)\?|\bcomenta (?:aqui|aí) (?:qual|o que|se|como)\b"),
     "responder pergunta"),
]

FILLER_TAGS = {
    "#viral", "#fyp", "#explore", "#explorar", "#explorepage", "#foryou", "#foryoupage",
    "#paravocê", "#paravoce", "#trending", "#instagood", "#love", "#amor", "#follow",
    "#like4like", "#likes", "#curtir", "#reels", "#reelsbrasil", "#reelsinstagram",
    "#viralreels", "#instadaily", "#instabrasil", "#brasil", "#sigoevolta", "#seguidores",
    "#tbt", "#foco", "#sucesso", "#gratidão", "#gratidao", "#motivação", "#motivacao",
}


def fold(text):
    """Minúsculas e sem acento: "Leilão" e "leilao" contam como o mesmo termo."""
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")


def visible_window(text, cut):
    """O que o feed mostra. O Instagram corta no meio da palavra, aqui também."""
    flat = text.strip()
    return flat if len(flat) <= cut else flat[:cut]


def render_box(window, truncated, out=sys.stdout, width=52):
    print("\n  O QUE O FEED MOSTRA", file=out)
    print("  +" + "-" * (width + 2) + "+", file=out)
    lines = []
    for raw in window.split("\n"):
        lines.extend(textwrap.wrap(raw, width) or [""])
    for line in lines[:8]:
        print(f"  | {line:<{width}} |", file=out)
    tail = "... mais" if truncated else "(cabe inteira)"
    print("  +" + "-" * (width + 2 - len(tail) - 2) + f" {tail} " + "+", file=out)


def analyse(text, cut=TRUNCATE, keywords=None):
    stripped = text.strip()
    chars = len(stripped)
    lines = stripped.split("\n")
    first_line = lines[0].strip() if lines else ""
    tags = HASHTAG_RE.findall(stripped)
    mentions = MENTION_RE.findall(stripped)
    links = LINK_RE.findall(stripped)
    emoji = EMOJI_RE.findall(stripped)
    window = visible_window(stripped, cut)
    truncated = chars > cut
    asks = [name for pattern, name in ASKS if pattern.search(stripped)]
    filler = [t for t in tags if t.lower() in FILLER_TAGS]
    keywords = [k.strip() for k in (keywords or []) if k.strip()]

    checks = []

    def add(name, status, detail):
        checks.append({"check": name, "status": status, "detail": detail})

    add("TAMANHO", "FALHA" if chars > LIMIT else "OK",
        f"{chars} / {LIMIT} caracteres" + (f", {chars - LIMIT} acima do limite" if chars > LIMIT else ""))

    if not first_line:
        add("1ª LINHA", "FALHA", "a legenda abre numa linha em branco")
    elif first_line.startswith(("#", "@")):
        add("1ª LINHA", "FALHA", "abre com hashtag ou menção, na única posição que vale uma frase")
    elif re.match(r"(?i)^\s*(?:oi|olá|ola|e aí|bom dia|boa tarde|boa noite|fala,? galera|salve)\b", first_line):
        add("1ª LINHA", "FALHA", "abre com cumprimento, gastando a janela visível em nada")
    elif len(first_line) > cut:
        add("1ª LINHA", "ALERTA",
            f"{len(first_line)} caracteres, então é cortada em {cut} no meio do pensamento. "
            "Tudo bem se o corte for um gancho, ruim se for uma oração subordinada")
    else:
        add("1ª LINHA", "OK", f"{len(first_line)} caracteres, aparece inteira")

    n_conc = len(CONCRETE_RE.findall(window))
    add("HOOK CONCRETO", "OK" if n_conc else "ALERTA",
        f"{n_conc} número(s) ou nome(s) na janela visível"
        + ("" if n_conc else " - nada verificável antes do toque"))

    if len(tags) > HASHTAG_LIMIT:
        add("HASHTAGS", "FALHA", f"{len(tags)} hashtags, acima do limite de {HASHTAG_LIMIT} do Instagram. "
                                 "As que passam da quinta não contam e o bloco parece velho")
    elif len(tags) == HASHTAG_LIMIT and filler:
        add("HASHTAGS", "ALERTA", f"{len(tags)} hashtags, no limite, e {len(filler)} genéricas. "
                                  "Gaste as cinco em temas")
    elif filler:
        add("HASHTAGS", "ALERTA", f"{len(tags)} hashtags, {len(filler)} genéricas "
                                  f"({', '.join(filler[:3])}). Essas não descrevem nada")
    else:
        add("HASHTAGS", "OK", f"{len(tags)} hashtag(s)" + (f": {' '.join(tags)}" if tags else ""))

    if not tags:
        add("POSIÇÃO TAGS", "OK", "sem hashtags para posicionar")
    elif any(re.search(r"(?:^|\s)" + re.escape(t) + r"\b", window) for t in tags):
        add("POSIÇÃO TAGS", "ALERTA", "tem hashtag dentro da janela visível, gastando espaço do feed com etiqueta")
    else:
        add("POSIÇÃO TAGS", "OK", "hashtags abaixo do corte")

    add("LINKS", "ALERTA" if links else "OK",
        f"{len(links)} link(s) na legenda, e legenda não é clicável. Leve pra bio ou pro direct"
        if links else "nenhum link morto no texto")

    if len(asks) == 1:
        add("UM PEDIDO", "OK", f"uma chamada para ação: {asks[0]}")
    elif not asks:
        add("UM PEDIDO", "ALERTA", "nenhuma chamada para ação. Decida pra que serve este post")
    else:
        add("UM PEDIDO", "ALERTA", f"{len(asks)} pedidos ({', '.join(asks)}). Dois pedidos é o mesmo que nenhum")

    density = len(emoji) * 100 / max(chars, 1)
    add("EMOJI", "ALERTA" if density > 4 else "OK",
        f"{len(emoji)} emoji, {density:.1f} a cada 100 caracteres" + (" - parece enfeite" if density > 4 else ""))

    if keywords:
        low = fold(stripped)
        found = [k for k in keywords if fold(k) in low]
        missing = [k for k in keywords if fold(k) not in low]
        in_window = [k for k in found if fold(k) in fold(window)]
        status = "OK" if not missing else ("ALERTA" if found else "FALHA")
        add("TERMOS DE BUSCA", status,
            f"{len(found)}/{len(keywords)} presentes"
            + (f", {len(in_window)} na janela visível" if found else "")
            + (f". Faltando: {', '.join(missing)}" if missing else ""))

    fails = sum(1 for c in checks if c["status"] == "FALHA")
    warns = sum(1 for c in checks if c["status"] == "ALERTA")
    verdict = "CORRIGIR" if fails else ("REVISAR" if warns else "PRONTA")
    return {"characters": chars, "limit": LIMIT, "truncate_at": cut, "visible": window,
            "truncated": truncated, "first_line_chars": len(first_line), "hashtags": tags,
            "mentions": mentions, "links": links, "emoji": len(emoji), "asks": asks,
            "checks": checks, "verdict": verdict}


def render(a, out=sys.stdout):
    head = (f"REVISÃO DE LEGENDA  ·  {a['characters']} / {a['limit']} caracteres  ·  "
            f"{len(a['hashtags'])} hashtags  ·  {len(a['asks'])} pedido(s)")
    print("\n" + head, file=out)
    print("=" * max(len(head), 62), file=out)
    render_box(a["visible"], a["truncated"], out=out)
    print("", file=out)
    for c in a["checks"]:
        print(f"  {c['status']:<6} {c['check']:<16} {c['detail']}", file=out)
    print("-" * max(len(head), 62), file=out)
    print(f"  VEREDITO  {a['verdict']}\n", file=out)


def main():
    ap = argparse.ArgumentParser(description="Revisa uma legenda de Instagram (PT-BR).")
    ap.add_argument("input", nargs="?", default="-", help="arquivo da legenda, ou - para stdin")
    ap.add_argument("--truncate", type=int, default=TRUNCATE,
                    help=f"caracteres mostrados antes do '... mais' (padrão {TRUNCATE})")
    ap.add_argument("--keywords", default="", help="termos de busca separados por vírgula")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.input == "-" else open(args.input, encoding="utf-8").read()
    a = analyse(raw, cut=args.truncate, keywords=args.keywords.split(","))
    if args.json:
        print(json.dumps(a, indent=2, ensure_ascii=False))
    else:
        render(a)
    sys.exit(0 if a["verdict"] == "PRONTA" else 1)


if __name__ == "__main__":
    main()
