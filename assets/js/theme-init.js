try {
  const saved = localStorage.getItem('theme') || 'light';
  const dark = saved === 'dark' || saved === 'night';
  const root = document.documentElement;
  root.setAttribute('data-theme', dark ? 'dark' : 'light');
  root.style.colorScheme = dark ? 'dark' : 'light';
  root.style.backgroundColor = dark ? '#1a202c' : '#ffffff';
  root.classList.add('no-theme-transition');
} catch {}
