document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
      document.querySelectorAll(".auth-panel").forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      document.getElementById(tab.dataset.target)?.classList.add("active");
    });
  });

  const dark = document.getElementById("dark-toggle");
  if (dark) {
    dark.addEventListener("change", () => {
      document.body.classList.toggle("dark-preview", dark.checked);
    });
  }

  setTimeout(() => {
    document.querySelectorAll(".flash").forEach(el => {
      el.style.transition = "opacity .4s";
      el.style.opacity = "0";
      setTimeout(() => el.remove(), 500);
    });
  }, 3500);
});
