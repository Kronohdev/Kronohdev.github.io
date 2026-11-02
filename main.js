// NEFERO · site: troca de idioma, repositórios e gráfico de commits puxados ao vivo.
const USUARIO = "Kronohdev";

// ---- idioma (lembra a escolha) ----
const botao = document.getElementById("idioma");
function aplicarIdioma(lang) {
  document.body.classList.toggle("lang-pt", lang === "pt");
  document.body.classList.toggle("lang-en", lang !== "pt");
  document.documentElement.lang = lang === "pt" ? "pt-BR" : "en";
  botao.textContent = lang === "pt" ? "EN" : "PT";
  localStorage.setItem("nefero-lang", lang);
}
botao.addEventListener("click", () => aplicarIdioma(document.body.classList.contains("lang-pt") ? "en" : "pt"));
aplicarIdioma(localStorage.getItem("nefero-lang") || (navigator.language.startsWith("pt") ? "pt" : "en"));

const t = (en, pt) => `<span class="en">${en}</span><span class="pt">${pt}</span>`;
const esc = (s) => String(s ?? "").replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

// ---- repositórios (API pública do GitHub) ----
async function carregarRepos() {
  const alvo = document.getElementById("lista-repos");
  try {
    const r = await fetch(`https://api.github.com/users/${USUARIO}/repos?per_page=100&sort=pushed`);
    if (!r.ok) throw new Error(r.status);
    const repos = (await r.json()).filter((x) => !x.fork && x.name !== USUARIO && x.name !== `${USUARIO}.github.io`);
    alvo.innerHTML = repos.slice(0, 12).map((x) => `
      <a class="cartao" href="${esc(x.html_url)}">
        <h3>${esc(x.name)}</h3>
        <p>${esc(x.description) || t("No description yet.", "Sem descrição ainda.")}</p>
        <div class="meta">${x.language ? `<span><i></i>${esc(x.language)}</span>` : ""}
          <span>★ ${x.stargazers_count}</span><span>⑂ ${x.forks_count}</span></div>
      </a>`).join("");
  } catch (e) {
    alvo.innerHTML = `<p class="carregando">${t("Couldn't load repositories right now.", "Não deu para carregar os repositórios agora.")}
      <a href="https://github.com/${USUARIO}?tab=repositories">github.com/${USUARIO}</a></p>`;
  }
}

// ---- gráfico de contribuições (redesenhado nas cores NEFERO) ----
async function carregarGrafico() {
  const alvo = document.getElementById("grafico");
  const total = document.getElementById("total-commits");
  try {
    const r = await fetch(`https://github-contributions-api.jogruber.de/v4/${USUARIO}?y=last`);
    if (!r.ok) throw new Error(r.status);
    const dados = await r.json();
    const dias = dados.contributions;
    const vazio = new Date(dias[0].date + "T00:00:00").getDay();   // alinha a primeira coluna no dia da semana
    let html = "<i style='visibility:hidden'></i>".repeat(vazio);
    html += dias.map((d) => `<i class="n${d.level}" title="${d.count} · ${d.date}"></i>`).join("");
    alvo.innerHTML = html;
    total.textContent = Object.values(dados.total).reduce((a, b) => a + b, 0);
  } catch (e) {
    total.textContent = "?";
    alvo.outerHTML = `<p class="carregando">${t("Graph unavailable right now.", "Gráfico indisponível agora.")}</p>`;
  }
}

// ---- últimos pushes ----
async function carregarAtividade() {
  const alvo = document.getElementById("atividade");
  try {
    const r = await fetch(`https://api.github.com/users/${USUARIO}/events/public?per_page=60`);
    if (!r.ok) throw new Error(r.status);
    const pushes = (await r.json()).filter((e) => e.type === "PushEvent").slice(0, 8);
    if (!pushes.length) throw new Error("vazio");
    alvo.innerHTML = pushes.map((e) => {
      const commits = e.payload.commits || [];
      const msg = commits.length ? commits[commits.length - 1].message.split("\n")[0] : "push";
      const data = new Date(e.created_at).toLocaleDateString(document.documentElement.lang);
      return `<li><span class="repo">${esc(e.repo.name.split("/")[1])}</span>${esc(msg)}
        ${commits.length > 1 ? `<em>(+${commits.length - 1})</em>` : ""}<span class="data">${data}</span></li>`;
    }).join("");
  } catch (e) {
    // sem eventos públicos de push: mostra os repositórios atualizados por último
    try {
      const r = await fetch(`https://api.github.com/users/${USUARIO}/repos?per_page=8&sort=pushed`);
      const repos = await r.json();
      alvo.innerHTML = repos.map((x) => `<li><span class="repo">${esc(x.name)}</span>${t("updated", "atualizado")}
        <span class="data">${new Date(x.pushed_at).toLocaleDateString(document.documentElement.lang)}</span></li>`).join("");
    } catch (e2) {
      alvo.innerHTML = `<li class="carregando">${t("No public pushes to show.", "Nenhum push público para mostrar.")}</li>`;
    }
  }
}

carregarRepos();
carregarGrafico();
carregarAtividade();
