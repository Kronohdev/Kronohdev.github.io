"""Gera uma página por jogo (saideira.html, coiotes-dawn.html, o-plano.html, unsworn.html) a partir de pesquisa.json.
Rodar de novo sempre que o pesquisa.json mudar."""
import html
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
dados = json.loads((RAIZ / "pesquisa.json").read_text(encoding="utf-8"))

# visual de cada página: cor de destaque, imagem do topo, fundo da página do itch e galeria (sem peças decorativas)
VISUAL = {
    "saideira": {"cor": "#e8462b", "topo": "assets/jogos/saideira/keyart.jpg", "fundo": "assets/jogos/saideira/fundo.jpg",
                 "galeria": ["shot4.png", "shot1.png", "trapaca.gif", "mascara.gif", "shot2.png", "shot3.png", "shot5.png",
                             "final_sai.gif", "final_fica.gif"]},
    "coiotes-dawn": {"cor": "#f0a63a", "topo": "assets/jogos/coiotes-dawn/capa.jpg", "fundo": "assets/jogos/coiotes-dawn/fundo.jpg",
                     "galeria": ["gif1.gif", "gif2.gif", "gif3.gif", "shot1.jpg", "shot2.jpg", "shot3.png", "grimorio.jpg",
                                 "controles.png"]},
    "o-plano": {"cor": "#d9c38a", "topo": "assets/jogos/o-plano/capa.jpg", "fundo": "assets/jogos/o-plano/fundo.jpg",
                "galeria": ["capa.jpg"]},
    "unsworn": {"cor": "#9fd3c7", "topo": "assets/jogos/unsworn/necromante_conceito.png", "fundo": "",
                "galeria": ["necromante_conceito.png", "necromante_opcoes.png", "madame_sevre_retrato.png",
                            "madame_sevre_figurino.png", "lys_conceito.jpg", "esbocos.jpg", "peca_necromante.png",
                            "peca_cortesao.png"]},
}

ROTULOS = {  # (en, pt)
    "genero": ("Genre", "Gênero"), "plataforma": ("Platforms", "Plataformas"), "engine": ("Engine", "Motor"),
    "idiomas": ("Languages", "Idiomas"), "duracao": ("Length", "Duração"), "evento": ("Made for", "Feito para"),
    "status": ("Status", "Status"), "data": ("Released", "Lançamento"), "atualizacao": ("Last update", "Última atualização"),
    "equipe": ("Team", "Equipe"), "jogar": ("Play on itch.io", "Jogar no itch.io"), "galeria": ("Gallery", "Galeria"),
    "sobre": ("About the game", "Sobre o jogo"), "ficha": ("Fact sheet", "Ficha"), "creditos": ("Credits", "Créditos"),
    "voltar": ("All games", "Todos os jogos"), "sem_build": ("In development: no public build yet.",
                                                             "Em desenvolvimento: ainda sem build pública."),
}


def t(chave):
    en, pt = ROTULOS[chave]
    return f'<span class="en">{en}</span><span class="pt">{pt}</span>'


def e(s):
    return html.escape(str(s or ""))


def limpa(s):
    """Tira as notas de tradução entre parênteses do fim das descrições."""
    s = s or ""
    for marca in (" (Tradução", " (Resumo/tradução", " (Tradução/resumo"):
        if marca in s:
            s = s[: s.index(marca)]
    return s


def ficha(j):
    linhas = []

    def add(chave, valor):
        if valor:
            linhas.append(f"<tr><td>{t(chave)}</td><td>{valor}</td></tr>")

    add("genero", e(", ".join(j.get("generos", []))))
    add("plataforma", e(", ".join(j.get("plataformas", []))))
    add("engine", e(j.get("engine", "").split(" (")[0]))
    add("idiomas", e(", ".join(j.get("idiomas", []))))
    add("duracao", e(j.get("duracao_media", "")))
    if j.get("evento"):
        ev = e(j["evento"].split(" (")[0])
        add("evento", f'<a href="{e(j["url_evento"])}">{ev}</a>' if j.get("url_evento") else ev)
    add("data", e((j.get("data_publicacao") or "").split(" (")[0]))
    add("atualizacao", e((j.get("data_atualizacao") or "").split(" (")[0]))
    return "\n".join(linhas)


EU = ("Neferoo", "Kauã Neves", "Kronohdev")


def nome(n):
    """Meu nome sempre aparece com o perfil do itch junto."""
    if n.split(" (")[0] in EU:
        return '<b>Kauã Neves</b> (<a href="https://neferoo.itch.io">Neferoo</a> no itch.io)'
    return f"<b>{e(n)}</b>"


def creditos(j):
    eq = j.get("equipe", {})
    det = eq.get("creditos_detalhados") or []
    if det:
        itens = "".join(f"<li>{nome(c['nome'])}: {e(c['funcao'])}</li>" for c in det)
    elif eq.get("autores_itch"):
        itens = "".join(f"<li>{nome(a)}</li>" for a in eq["autores_itch"])
    else:
        itens = f"<li>{nome('Kauã Neves')}</li>"
    return f'<section class="placa"><h2>{t("creditos")}</h2><ul class="creditos">{itens}</ul></section>'


def legenda(j, nome):
    for im in j.get("imagens", []):
        if im["arquivo"].endswith("/" + nome) or im["arquivo"].rsplit(".", 1)[0].endswith("/" + nome.rsplit(".", 1)[0]):
            return im["legenda"].split(" (")[0]
    return ""


def pagina(j):
    v = VISUAL[j["slug"]]
    galeria = "".join(
        f'<figure><img src="assets/jogos/{j["slug"]}/{n}" alt="{e(legenda(j, n))}" loading="lazy">'
        f'<figcaption>{e(legenda(j, n))}</figcaption></figure>' for n in v["galeria"])
    botao = (f'<a class="botao jogar" href="{e(j["url_jogar"])}">{t("jogar")} →</a>' if j.get("url_jogar")
             else f'<p class="aviso">{t("sem_build")}</p>')
    tags = "".join(f"<span>{e(x)}</span>" for x in (j.get("tags") or [])[:8])
    fundo = f'background-image:url("{v["fundo"]}")' if v["fundo"] else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(j["titulo"])} · NEFERO</title>
<meta name="description" content="{e(limpa(j.get("descricao_en"))[:160])}">
<meta property="og:title" content="{e(j["titulo"])} · NEFERO">
<meta property="og:image" content="{v["topo"]}">
<link rel="icon" href="assets/avatar.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,700;1,400&family=VT323&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<link rel="stylesheet" href="jogo.css">
</head>
<body class="lang-en pagina-jogo" style="--destaque:{v["cor"]};{fundo}">
<nav class="nav-jogo">
  <a href="index.html#games">← {t("voltar")}</a>
  <span class="nome-jogo">{e(j["titulo"])}</span>
  <button id="idioma" type="button" aria-label="Switch language">PT</button>
</nav>
<header class="capa-jogo">
  <img src="{v["topo"]}" alt="{e(j["titulo"])}">
  <div class="sobre-capa">
    <h1>{e(j["titulo"])}</h1>
    {f'<p class="tagline">{e(j["tagline"])}</p>' if j.get("tagline") else ""}
    <div class="tags">{tags}</div>
  </div>
</header>
<main>
  <div class="duas-colunas">
    <section class="placa">
      <h2>{t("sobre")}</h2>
      <p class="en">{e(limpa(j.get("descricao_en")))}</p>
      <p class="pt">{e(limpa(j.get("descricao_pt")))}</p>
      {botao}
    </section>
    <aside class="placa">
      <h2>{t("ficha")}</h2>
      <table class="ficha">{ficha(j)}</table>
    </aside>
  </div>
  <section>
    <h2 class="titulo">{t("galeria")}</h2>
    <div class="galeria">{galeria}</div>
  </section>
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


for j in dados["jogos"]:
    (RAIZ / f'{j["slug"]}.html').write_text(pagina(j), encoding="utf-8")
    print("ok", j["slug"])
