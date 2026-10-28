#!/usr/bin/env python3
"""
run_tests.py - testes de regressão da versão PT-BR.

Roda as ferramentas sobre casos em português com resultado esperado conhecido.
Use depois de editar slop.json, hooks.json ou qualquer script:

  python3 tests/run_tests.py

Sai com código 0 se tudo passou.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, "skills")
for d in ("ig-reel", "ig-caption", "ig-human"):
    sys.path.insert(0, os.path.join(SK, d))

import hookscore      # noqa: E402
import beats          # noqa: E402
import caption        # noqa: E402
import humanize       # noqa: E402
import detect         # noqa: E402

LEX = humanize.load_lexicon(os.path.join(SK, "ig-human", "slop.json"))
HOOKS = json.load(open(os.path.join(SK, "ig-reel", "hooks.json"), encoding="utf-8"))

passed = failed = 0


def check(name, cond, info=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"  ok     {name}")
    else:
        failed += 1
        print(f"  FALHOU {name}  {info}")


print("\nhookscore.py")
strong = [
    "Perdi R$18.000 por causa de uma cláusula que faltou no contrato.",
    "Ninguém te conta que seus primeiros 30 reels vão flopar.",
    "Pare de postar três vezes por dia.",
]
weak = [
    "Oi gente, hoje eu queria falar sobre estratégia de conteúdo",
    "Nesse vídeo eu vou te mostrar como arrematar imóvel em leilão",
    "Hoje vamos falar um pouco sobre marketing digital e redes sociais para negócios",
    "Bom dia pessoal, tudo bem com vocês?",
]
for h in strong:
    _, score, verdict, _ = hookscore.run(h)
    check(f"forte >= 70: {h[:40]}", score >= 70, f"(nota {score:.1f})")
for h in weak:
    _, score, verdict, _ = hookscore.run(h)
    check(f"fraco < 30: {h[:40]}", score < 30, f"(nota {score:.1f})")
_, _, _, flags = hookscore.run("Oi gente, tudo bem?")
check("saudação vira eliminatório", any("Saudação" in f for f in flags))
_, _, _, flags = hookscore.run("Neste vídeo eu vou te ensinar a precificar")
check("preâmbulo vira eliminatório", any("Preâmbulo" in f for f in flags))
check("R$18.000 conta como uma palavra", len(hookscore.words("Perdi R$18.000 hoje")) == 3)

print("\nhooks.json")
by = {h["id"]: h for h in HOOKS["hooks"]}
pats = [(i, re.compile(by[i]["match"], re.IGNORECASE)) for i in HOOKS["classify_order"]]
check("26 fórmulas", len(by) == 26)
for h in HOOKS["hooks"]:
    got = next((i for i, p in pats if p.search(h["example"])), None)
    check(f"exemplo #{h['id']} {h['name']} se classifica", got == h["id"], f"(foi #{got})")
for t in ["Oi gente, hoje eu queria falar sobre estratégia", "Bom dia, tudo bem com vocês?",
          "Vou falar um pouco sobre o meu dia"]:
    got = next((i for i, p in pats if p.search(t)), None)
    check(f"frase comum não vira fórmula: {t[:35]}", got is None, f"(foi #{got})")

print("\nhumanize.py")
txt = ("No mundo acelerado de hoje, é crucial entender que o marketing desempenha um papel "
       "fundamental. Nesse sentido, vale ressaltar que uma estratégia robusta pode alavancar "
       "seus resultados.\n\nSegue pra mais conteúdo!\n")
clean, rep = humanize.humanize(txt, LEX)
check("nenhuma palavra em inglês inserida", not re.search(r"\b(?:important|look|use|solid)\b", clean), clean)
check("'robusta' vira 'sólida' (concordância)", "sólida" in clean, clean)
check("'segue pra mais conteúdo' some", "Segue" not in clean, clean)
check("sem pontuação órfã ('., ' ou '.!')", not re.search(r"\.,|\.!|^\s*[,!]", clean, re.M), clean)
check("frase recomeça com maiúscula", "Uma estratégia" in clean, clean)
clean2, rep2 = humanize.humanize("Arrematei por 52% da avaliação — e quase perdi tudo.\n", LEX)
check("travessão vira vírgula", "—" not in clean2 and ", e quase" in clean2, clean2)
_, rep3 = humanize.humanize("Precisamos navegar esse cenário com um planejamento estratégico.\n", LEX)
check("ambíguos só sinalizados", {f["find"] for f in rep3["flagged_words"]} >= {"navegar", "estratégico"})
_, rep4 = humanize.humanize("Nesse vídeo eu vou te mostrar como fazer.\n", LEX)
check("preâmbulo sinalizado", any("Preâmbulo" in s["name"] for s in rep4["structures"]))
check("URL intocada", "https://exemplo.com.br/robusto" in
      humanize.humanize("Veja https://exemplo.com.br/robusto agora.\n", LEX)[0])

print("\ndetect.py")
human = ("Arrematei um apê em Mangabeira por R$142 mil. A avaliação era R$271 mil.\n\n"
         "Parece ótimo, né? Quase deu errado. Eu não tinha lido a parte do edital que falava "
         "do condomínio atrasado, e eram R$23 mil de dívida que ficavam pra mim.\n\n"
         "O que salvou foi uma ligação pro síndico dois dias antes do leilão. Ele me mandou o "
         "extrato. Aí eu refiz a conta e baixei meu lance máximo.\n\n"
         "Hoje eu não dou lance sem essas três coisas: edital lido inteiro, extrato do "
         "condomínio e certidão de IPTU.\n")
machine = ("No mundo acelerado de hoje, é crucial entender que o marketing digital desempenha "
           "um papel fundamental. Não é só sobre vender, é sobre criar conexões. Nesse sentido, "
           "vale ressaltar que uma estratégia robusta e inovadora pode alavancar seus resultados "
           "de forma significativa.\n\nO resultado?\n\nMais clientes, mais vendas e mais "
           "crescimento.\n\nSegue pra mais conteúdo! 🚀\n")
_, h_score, h_verdict = detect.run(human, LEX)
_, m_score, m_verdict = detect.run(machine, LEX)
check("texto humano APROVADO", h_verdict == "APROVADO", f"({h_score:.1f})")
check("texto de IA SINALIZADO", m_verdict == "SINALIZADO", f"({m_score:.1f})")
check("oralidade conta 'pra', 'né', 'aí'", len(detect.ORAL.findall(human)) >= 3)

print("\ncaption.py")
a = caption.analyse("Arrematei um apê por 52% da avaliação.\n\nComenta EDITAL que eu te mando o checklist.\n"
                    "\n#leilao #imoveis #jp #paraiba #investimento #casa\n",
                    keywords=["leilão"])
names = {c["check"]: c["status"] for c in a["checks"]}
check("6 hashtags reprova", names["HASHTAGS"] == "FALHA")
check("'Comenta EDITAL' é um pedido", a["asks"] == ["comentar palavra-chave"], a["asks"])
check("busca ignora acento ('leilão' acha '#leilao')", names["TERMOS DE BUSCA"] == "OK")
a2 = caption.analyse("Oi gente! Hoje tem novidade.\n")
check("cumprimento na 1ª linha reprova", {c["check"]: c["status"] for c in a2["checks"]}["1ª LINHA"] == "FALHA")
a3 = caption.analyse("Me chama no direct que eu te explico.\n")
check("'me chama no direct' é pedido", "chamar no direct/WhatsApp" in a3["asks"], a3["asks"])
a4 = caption.analyse("Cardápio completo em www.restaurante.com.br hoje.\n")
check("link .com.br é detectado", len(a4["links"]) == 1, a4["links"])

a5 = caption.analyse("Solicite uma demonstração GRATUITA.\n\nOu chame nossa equipe no WhatsApp.\n")
check("demonstração + chamar equipe = 2 pedidos", len(a5["asks"]) == 2, a5["asks"])
_, rep5 = humanize.humanize("Chegou a hora de mudar.\n\n#FacilWeb #PDV Pizzaria Hamburgueria Lanchonete\n", LEX)
check("hashtag sem # sinalizada", any("sem #" in s["name"] for s in rep5["structures"]))
check("clichê de copy sinalizado", any(f["find"] == "chegou a hora de" for f in rep5["flagged_words"]))

print("\nbeats.py")
b = beats.analyse("Perdi R$18.000 num contrato.\nCláusula 4. Pagamento na entrega.\n"
                  "Essa troca vale R$18.000 pra mim.\n", target=15)
check("loop detectado no valor", any("r$18.000" in n for n in b["notes"]), b["notes"])
check("stopwords PT não contam como loop", not any("\"de" in n or ", de" in n for n in b["notes"]))

print(f"\n{passed} passaram, {failed} falharam\n")
sys.exit(1 if failed else 0)
