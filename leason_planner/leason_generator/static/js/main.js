document.addEventListener('DOMContentLoaded', () => {
  const toastContainer = document.getElementById('toast-container');

  function showToast(text, timeout = 3000) {
    if (!toastContainer) return;
    const t = document.createElement('div');
    t.className = 'toast';
    t.textContent = text;
    toastContainer.appendChild(t);
    setTimeout(() => t.classList.add('visible'), 10);
    setTimeout(() => {
      t.classList.remove('visible');
      setTimeout(() => toastContainer.removeChild(t), 300);
    }, timeout);
  }

  // Theme toggle (persist in localStorage)
  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const applyTheme = (dark) => {
      document.documentElement.classList.toggle('dark', dark);
      localStorage.setItem('lp-dark', dark ? '1' : '0');
      themeToggle.textContent = dark ? '☀️' : '🌙';
    };
    applyTheme(localStorage.getItem('lp-dark') === '1');
    themeToggle.addEventListener('click', () => applyTheme(!(localStorage.getItem('lp-dark') === '1')));
  }

  // Prevent double submit + show spinner
  const genForm = document.getElementById('generate-form');
  if (genForm) {
    const submitBtn = genForm.querySelector('button[type="submit"]');
    genForm.addEventListener('submit', () => {
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.dataset.orig = submitBtn.innerHTML;
        submitBtn.innerHTML = '<span class="spinner" aria-hidden="true"></span> Generating...';
      }
    });
  }

  // Copy generated plan to clipboard
  const copyBtn = document.getElementById('copy-plan');
  if (copyBtn) {
    copyBtn.addEventListener('click', async () => {
      const pre = document.querySelector('.lesson-plan pre');
      if (!pre) { showToast('Nothing to copy'); return; }
      try {
        await navigator.clipboard.writeText(pre.innerText);
        showToast('Copied to clipboard');
      } catch {
        showToast('Copy failed');
      }
    });
  }

  // Toggle recent plans collapse
  document.querySelectorAll('.toggle-recent').forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.dataset.target;
      const el = document.getElementById(targetId);
      if (!el) return;
      const collapsed = el.classList.toggle('collapsed');
      btn.textContent = collapsed ? 'Show recent plans' : 'Hide recent plans';
    });
  });

  // Small success toast on page load if a message element exists (optional)
  const serverMessage = document.getElementById('server-msg');
  if (serverMessage && serverMessage.textContent.trim()) {
    showToast(serverMessage.textContent.trim());
  }
});