"""Gera uma página por projeto (power-pplay.html, akuanduba.html, pesquisa.html, dnd-builder.html, athena-nba.html)
a partir de projetos.json. Rodar de novo sempre que o projetos.json mudar.

Os textos do JSON são pares [en, pt] e podem ter HTML simples (strong, em, code, a). O código dos blocos
"codigo" é escapado aqui. Cada projeto tem a sua cor de destaque (--destaque), como as páginas de jogo."""
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
dados = json.loads((RAIZ / "projetos.json").read_text(encoding="utf-8"))

ROTULOS = {  # (en, pt)
    "sobre": ("About", "Sobre"), "ficha": ("Fact sheet", "Ficha"), "creditos": ("Credits", "Créditos"),
    "voltar": ("All projects", "Todos os projetos"), "galeria": ("Gallery", "Galeria"),
    "agradecimentos": ("Thanks", "Agradecimentos"),
}


def t(par):
    """Par [en, pt] (ou chave de ROTULOS) em spans; texto simples vale para os dois idiomas."""
    if isinstance(par, str):
        par = ROTULOS.get(par, (par, par))
    en, pt = par
    if en == pt:
        return en
    return f'<span class="en">{en}</span><span class="pt">{pt}</span>'


def p(par, classe=""):
    c = f" {classe}" if classe else ""
    en, pt = par
    return f'<p class="en{c}">{en}</p><p class="pt{c}">{pt}</p>'


def e(s):
    return html.escape(str(s or ""))


def nome(n):
    """Meu nome sempre aparece com o perfil do itch e do GitHub junto."""
    if n == "EU":
        return ('<b>Kauã Neves</b> (<a href="https://neferoo.itch.io">Neferoo</a> '
                + t(["on itch.io", "no itch.io"]) + ' / <a href="https://github.com/Kronohdev">Kronohdev</a> '
                + t(["on GitHub", "no GitHub"]) + ")")
    return f"<b>{e(n)}</b>"


def valor(v):
    return t(v) if isinstance(v, list) else v


def titulo_secao(s, faixa=False):
    if not s.get("titulo"):
        return ""
    return f'<h2 class="titulo">{t(s["titulo"])}</h2>' if faixa else f"<h2>{t(s['titulo'])}</h2>"


def intro(s):
    return p(s["intro"], "intro") if s.get("intro") else ""


# ---- tipos de seção ----

def sec_texto(s, j):
    corpo = "".join(p(x) for x in s["paragrafos"])
    if s.get("formulas"):
        corpo += '<dl class="formulas">' + "".join(
            f'<div><dt>{f["f"]}</dt><dd>{t(f["d"])}</dd></div>' for f in s["formulas"]) + "</dl>"
    return f'<section class="placa">{titulo_secao(s)}{corpo}</section>'


def sec_cartoes(s, j):
    itens = "".join(f'<div class="bloco"><h3>{t(i["t"])}</h3>{p(i["d"])}</div>' for i in s["itens"])
    n = len(s["itens"])
    colunas = 4 if n % 4 == 0 else 3 if n % 3 == 0 else 4   # evita linha final pela metade
    return (f'<section>{titulo_secao(s, True)}{intro(s)}'
            f'<div class="blocos" style="--colunas:{colunas}">{itens}</div></section>')


def sec_numeros(s, j):
    itens = "".join(
        f'<div class="numero"><b>{t([i["valor"], i.get("valor_pt", i["valor"])])}</b><span>{t(i["rotulo"])}</span></div>'
        for i in s["itens"])
    return f'<section>{titulo_secao(s, True)}<div class="numeros">{itens}</div></section>'


def sec_codigo(s, j):
    blocos = "".join(
        f'<figure class="codigo"><figcaption>{t(b["legenda"])}</figcaption>'
        f'<pre><code>{e(chr(10).join(b["linhas"]))}</code></pre></figure>' for b in s["blocos"])
    return f'<section class="placa">{titulo_secao(s)}{intro(s)}<div class="codigos">{blocos}</div></section>'


def sec_pipeline(s, j):
    passos = "".join(f'<li><b>{t(x["t"])}</b>{p(x["d"])}</li>' for x in s["passos"])
    nota = p(s["nota"], "nota") if s.get("nota") else ""
    return f'<section class="placa">{titulo_secao(s)}{intro(s)}<ol class="pipeline">{passos}</ol>{nota}</section>'


def sec_barras(s, j):
    linhas = []
    for i in s["itens"]:
        classe = "barra nossa" if i.get("destaque") else "barra"
        linhas.append(
            f'<div class="{classe}"><span class="rotulo">{t(i["rotulo"])}</span>'
            f'<span class="trilho" title="{e(i["rotulo"][0])}: {e(i["texto"][0])}"><i style="width:{i["valor"]}%"></i></span>'
            f'<span class="valor">{t(i["texto"])}</span></div>')
    escala = ('<div class="barra eixo" aria-hidden="true"><span></span><span class="escala"><span>0</span><span>25</span>'
              '<span>50</span><span>75</span><span>100%</span></span><span></span></div>')
    nota = p(s["nota"], "nota") if s.get("nota") else ""
    return (f'<section class="placa">{titulo_secao(s)}{intro(s)}'
            f'<div class="barras">{"".join(linhas)}{escala}</div>{nota}</section>')


def sec_tabela(s, j):
    cab = "".join(f"<th>{t(c)}</th>" for c in s["colunas"])
    corpo = "".join("<tr>" + "".join(f"<td>{valor(c)}</td>" for c in linha) + "</tr>" for linha in s["linhas"])
    return (f'<section class="placa">{titulo_secao(s)}{intro(s)}'
            f'<div class="tabela-envoltorio"><table class="resultados"><thead><tr>{cab}</tr></thead>'
            f'<tbody>{corpo}</tbody></table></div></section>')


def sec_figura(s, j):
    corpo = "".join(p(x) for x in s["paragrafos"])
    src = f'assets/projetos/{j["slug"]}/{s["arquivo"]}'
    return (f'<section class="placa figura-lado"><div>{titulo_secao(s)}{corpo}</div>'
            f'<figure class="galeria uma"><img src="{src}" alt="{e(s["legenda"][0])}" loading="lazy">'
            f'<figcaption>{t(s["legenda"])}</figcaption></figure></section>')


def sec_galeria(s, j):
    itens = "".join(
        f'<figure><img src="assets/projetos/{j["slug"]}/{i["arquivo"]}" alt="{e(i["legenda"][0])}" loading="lazy">'
        f'<figcaption>{t(i["legenda"])}</figcaption></figure>' for i in s["itens"])
    return f'<section>{titulo_secao(s, True)}<div class="galeria">{itens}</div></section>'


SECOES = {"texto": sec_texto, "cartoes": sec_cartoes, "numeros": sec_numeros, "codigo": sec_codigo,
          "pipeline": sec_pipeline, "barras": sec_barras, "tabela": sec_tabela, "figura": sec_figura,
          "galeria": sec_galeria}


def ficha(j):
    return "\n".join(f"<tr><td>{t(r['k'])}</td><td>{valor(r['v'])}</td></tr>" for r in j["ficha"])


def botoes(j):
    return "".join(
        f'<a class="botao{" roxo" if b.get("roxo") else " jogar"}" href="{e(b["url"])}">{t(b["rotulo"])} →</a> '
        for b in j.get("botoes", []))


def creditos(j):
    itens = "".join(f"<li>{nome(c['nome'])}: {t(c['funcao'])}</li>" for c in j["creditos"])
    agradece = p(j["agradecimentos"]) if j.get("agradecimentos") else ""
    return f'<section class="placa"><h2>{t("creditos")}</h2><ul class="creditos">{itens}</ul>{agradece}</section>'


def pagina(j):
    titulo_en = j["titulo"]
    titulo = t([titulo_en, j.get("titulo_pt", titulo_en)])
    tags = "".join(f"<span>{e(x)}</span>" for x in j.get("tags", []))
    secoes = "\n  ".join(SECOES[s["tipo"]](s, j) for s in j["secoes"])
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(titulo_en)} · NEFERO</title>
<meta name="description" content="{e(j["tagline"][0])}">
<meta property="og:title" content="{e(titulo_en)} · NEFERO">
<meta property="og:description" content="{e(j["tagline"][0])}">
<meta property="og:image" content="{j["emblema"]}">
<link rel="icon" href="assets/avatar.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="jogo.css">
<link rel="stylesheet" href="projeto.css">
</head>
<body class="lang-en pagina-jogo pagina-projeto" style="--destaque:{j["cor"]}">
<nav class="nav-jogo">
  <a href="projetos.html">← {t("voltar")}</a>
  <span class="nome-jogo">{titulo}</span>
  <button id="idioma" type="button" aria-label="Switch language">PT</button>
</nav>
<header class="capa-projeto">
  <div class="emblema {j["emblema_tipo"]}"><img src="{j["emblema"]}" alt="{e(titulo_en)}"></div>
  <div class="sobre-capa">
    <h1>{titulo}</h1>
    {p(j["tagline"], "tagline")}
    <div class="tags">{tags}</div>
  </div>
</header>
<main>
  <div class="duas-colunas">
    <section class="placa">
      <h2>{t("sobre")}</h2>
      {"".join(p(x) for x in j["sobre"])}
      {botoes(j)}
    </section>
    <aside class="placa">
      <h2>{t("ficha")}</h2>
      <table class="ficha">{ficha(j)}</table>
    </aside>
  </div>
  {secoes}
  {creditos(j)}
</main>
<footer>
  <img src="assets/bando.gif" alt="" class="faixa pixel">
  <p><a href="index.html">NEFERO</a> · Kauã Neves</p>
</footer>
<div id="zoom"><img alt=""></div>
<script src="jogo.js"></script>
</body>
</html>
"""


for j in dados["projetos"]:
    (RAIZ / f'{j["slug"]}.html').write_text(pagina(j), encoding="utf-8")
    print("ok", j["slug"])
