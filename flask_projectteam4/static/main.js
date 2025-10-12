// main.js — Ewha Market 공통 스크립트

// ========== 🌙 다크모드 기능 ==========
function applyTheme(theme) {
  document.body.setAttribute("data-theme", theme);
  const toggleBtn = document.getElementById("darkToggle");
  if (toggleBtn) {
    toggleBtn.textContent = theme === "dark" ? "라이트 모드" : "다크 모드";
  }
}

function toggleTheme() {
  const current = document.body.getAttribute("data-theme");
  const next = current === "dark" ? "light" : "dark";
  localStorage.setItem("theme", next);
  applyTheme(next);
}

document.addEventListener("DOMContentLoaded", () => {
  const saved = localStorage.getItem("theme") || "light";
  applyTheme(saved);
  const btn = document.getElementById("darkToggle");
  if (btn) btn.addEventListener("click", toggleTheme);
});

// ========== 🔄 폼 제출 방지 / 메시지 ==========
document.addEventListener("submit", e => {
  e.preventDefault();
  alert("제출되었습니다!");
});

// ========== 💬 버튼 클릭 애니메이션 ==========
document.addEventListener("click", e => {
  if (e.target.classList.contains("btn")) {
    e.target.style.transform = "scale(0.96)";
    setTimeout(() => e.target.style.transform = "scale(1)", 100);
  }
});
