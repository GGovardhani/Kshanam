// ── Auto-set today's date on all date fields ──
document.addEventListener('DOMContentLoaded', () => {
  const today = new Date().toISOString().split('T')[0];
  document.querySelectorAll('input[type="date"]').forEach(el => {
    if (!el.value) el.value = today;
  });

  // ── Animate score bars on load ──
  document.querySelectorAll('.score-bar-fill, .life-bar-fill, .life-bar-remaining').forEach(bar => {
    const target = bar.style.width;
    bar.style.width = '0%';
    setTimeout(() => { bar.style.width = target; }, 200);
  });

  // ── Highlight active nav link ──
  const path = window.location.pathname;
  document.querySelectorAll('.nav-links a').forEach(link => {
    if (link.getAttribute('href') === path) {
      link.classList.add('active');
    }
  });

  // ── Priority checkbox visual toggle ──
  document.querySelectorAll('.priority-item input[type="checkbox"]').forEach(cb => {
    const label = cb.closest('.priority-item');
    if (cb.checked) label.style.borderColor = 'rgba(201,168,76,0.5)';
    cb.addEventListener('change', () => {
      label.style.borderColor = cb.checked
        ? 'rgba(201,168,76,0.5)'
        : 'rgba(255,255,255,0.07)';
      label.style.background = cb.checked
        ? 'rgba(201,168,76,0.08)'
        : 'rgba(255,255,255,0.03)';
    });
  });
});