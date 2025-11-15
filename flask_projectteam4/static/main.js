// 다크모드 기능
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


if (!window.__EWHA_MAIN_JS_LOADED__) {
  window.__EWHA_MAIN_JS_LOADED__ = true;

  // 폼 제출 처리
  document.addEventListener("submit", e => {
    const form = e.target;
    const path = window.location.pathname.toLowerCase();
    const action = (form.getAttribute("action") || "").toLowerCase();
    const method = (form.getAttribute("method") || "get").toLowerCase();

    // 로그인, POST 요청, register/review/submit 은 Flask에서 처리
    if (path.startsWith("/login") || action.includes("/login")) return;
    if (method === "post") return;
    if (action.includes("/register") || action.includes("/review/submit")) return;

    // 중복 alert 방지 락
    if (window.__EWHA_SUBMIT_LOCK__) return;
    window.__EWHA_SUBMIT_LOCK__ = true;

    e.preventDefault();
    e.stopPropagation();
    e.stopImmediatePropagation();

    alert("제출되었습니다!");

    setTimeout(() => {
      window.__EWHA_SUBMIT_LOCK__ = false;
    }, 800);
  }, { capture: true });
}

// 버튼 클릭 애니메이션
document.addEventListener("click", e => {
  if (e.target.classList.contains("btn")) {
    e.target.style.transform = "scale(0.96)";
    setTimeout(() => e.target.style.transform = "scale(1)", 100);
  }
});

