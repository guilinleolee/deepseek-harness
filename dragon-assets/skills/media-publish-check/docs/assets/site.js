(() => {
  const supported = ["zh", "en"];
  const saved = localStorage.getItem("mpc-language");
  const initial = supported.includes(saved) ? saved : (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";

  function setLanguage(language) {
    document.documentElement.lang = language === "zh" ? "zh-CN" : "en";
    document.querySelectorAll(".language").forEach((section) => {
      section.hidden = section.dataset.language !== language;
    });
    document.querySelectorAll(".lang-switch").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });
    localStorage.setItem("mpc-language", language);
  }

  document.querySelectorAll(".lang-switch").forEach((button) => {
    button.addEventListener("click", () => setLanguage(button.dataset.language));
  });
  setLanguage(initial);
})();
