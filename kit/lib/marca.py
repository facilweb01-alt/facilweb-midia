"""Identidade visual de qualquer projeto, lida de um marca.json.

Exemplo (exemplos/marca-facilweb.json):
{
  "nome": "Fácil Web", "handle": "@facilweb", "site": "facilwebdelivery.com.br",
  "logo": "logo-facilweb.png",
  "cores": {"primaria": "#0A3D9E", "escura": "#041d55", "destaque": "#8DC63F", "acento": "#F7941D", "clara": "#1f6bf0"},
  "fonte": "Poppins"
}
Caminhos relativos (logo) são resolvidos a partir da pasta do marca.json.
"""
import base64, json, os

PADRAO = {"nome": "", "handle": "", "site": "", "logo": None, "fonte": "Poppins",
          "cores": {"primaria": "#0A3D9E", "escura": "#041d55", "destaque": "#8DC63F", "acento": "#F7941D", "clara": "#1f6bf0"}}


def carregar(caminho):
    with open(caminho, encoding="utf-8") as f:
        m = json.load(f)
    out = {**PADRAO, **m, "cores": {**PADRAO["cores"], **m.get("cores", {})}}
    if out.get("logo") and not os.path.isabs(out["logo"]):
        out["logo"] = os.path.join(os.path.dirname(os.path.abspath(caminho)), out["logo"])
    return out


def logo_data_uri(m):
    if not m.get("logo") or not os.path.exists(m["logo"]):
        return None
    ext = os.path.splitext(m["logo"])[1].lower().strip(".") or "png"
    return f"data:image/{'jpeg' if ext in ('jpg', 'jpeg') else ext};base64," + base64.b64encode(open(m["logo"], "rb").read()).decode()


def css_vars(m):
    c = m["cores"]
    return (f":root{{--pri:{c['primaria']};--esc:{c['escura']};--dest:{c['destaque']};--acen:{c['acento']};--clara:{c['clara']}}}"
            f"body{{font-family:'{m['fonte']}',Poppins,Inter,sans-serif}}")


def hex_bgr(h):
    h = h.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


def rgba(h, a):
    h = h.lstrip("#")
    return f"rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})"


def fundo_css(m, w, h):
    """Fundo padrão: degradê da cor primária para a escura, com grade e brilhos nas cores de destaque e acento."""
    c = m["cores"]
    return f""".fundo{{position:absolute;inset:0;background:radial-gradient({int(w*.85)}px {int(h*.42)}px at 85% 6%,{c['clara']} 0,{rgba(c['clara'],0)} 70%),
 radial-gradient({int(w*.75)}px {int(h*.36)}px at 0% 100%,{c['escura']} 0,{rgba(c['escura'],0)} 70%),linear-gradient(165deg,{c['primaria']},{c['escura']})}}
.grade{{position:absolute;inset:0;background-image:linear-gradient(rgba(255,255,255,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.05) 1px,transparent 1px);
 background-size:60px 60px;mask-image:linear-gradient(180deg,transparent,#000 22%,#000 78%,transparent)}}
.anel{{position:absolute;border-radius:50%;border:3px solid {rgba(c['destaque'],.22)}}}
.brilho{{position:absolute;border-radius:50%;filter:blur(110px)}}"""


def fundo_html(m, w, h):
    c = m["cores"]
    return (f'<div class="fundo"></div><div class="grade"></div>'
            f'<div class="anel" style="width:{int(w*.92)}px;height:{int(w*.92)}px;left:{-int(w*.47)}px;top:{-int(h*.16)}px"></div>'
            f'<div class="anel" style="width:{int(w*.7)}px;height:{int(w*.7)}px;right:{-int(w*.39)}px;bottom:{-int(h*.08)}px;border-color:{rgba(c["acento"],.22)}"></div>'
            f'<div class="brilho" style="width:{int(w*.52)}px;height:{int(w*.52)}px;background:{c["destaque"]};opacity:.35;left:{-int(w*.2)}px;top:{int(h*.68)}px"></div>'
            f'<div class="brilho" style="width:{int(w*.42)}px;height:{int(w*.42)}px;background:{c["acento"]};opacity:.28;right:{-int(w*.17)}px;top:{int(h*.31)}px"></div>')
