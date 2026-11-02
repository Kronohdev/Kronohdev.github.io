// páginas de jogo: idioma (compartilhado com o resto do site) e zoom da galeria
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

const zoom = document.getElementById("zoom");
document.querySelectorAll(".galeria img").forEach((img) => {
  img.addEventListener("click", () => { zoom.querySelector("img").src = img.src; zoom.style.display = "flex"; });
});
zoom.addEventListener("click", () => { zoom.style.display = "none"; });
document.addEventListener("keydown", (ev) => { if (ev.key === "Escape") zoom.style.display = "none"; });
