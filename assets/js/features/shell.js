import { SITE, $, applyTheme, isArticle, storageGet, storageSet } from '../utils.js';

export function loadTheme() {
  applyTheme(storageGet('theme', 'light'));
}

export function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || storageGet('theme', 'light');
  const next = current === 'light' ? 'dark' : 'light';
  storageSet('theme', next);
  applyTheme(next);
  const icon = $('#theme-icon');
  if (icon) {
    icon.style.transform = 'scale(0.8) rotate(-15deg)';
    setTimeout(() => {
      icon.style.transform = '';
    }, 150);
  }
}

export function checkGlobalBackBtn(state) {
  const button = $('#float-back-btn');
  if (!button) return;
  const listState = state.homeListState || {};
  if (document.body.getAttribute('data-page') !== 'home' || listState.q || (listState.page && listState.page > 1)) {
    button.style.display = 'flex';
  } else {
    button.style.display = 'none';
  }
}

export function initBackgroundSwitcher() {
  const stored = storageGet('site-bg', 'none');
  const saved = ['none', 'grid', 'dots'].includes(stored) ? stored : 'none';
  document.body.setAttribute('data-bg', saved);
  const group = $('#float-btn-group');
  if (!group || $('#float-bottom-btn')) return;

  const bottomBtn = document.createElement('button');
  bottomBtn.id = 'float-bottom-btn';
  bottomBtn.className = 'float-btn icon-button';
  bottomBtn.type = 'button';
  bottomBtn.title = '直达底部';
  bottomBtn.setAttribute('aria-label', '直达底部');
  bottomBtn.innerHTML = '<i class="fa-solid fa-arrow-down"></i>';
  bottomBtn.addEventListener('click', () => {
    window.scrollTo({ top: document.documentElement.scrollHeight, behavior: 'smooth' });
  });
  group.appendChild(bottomBtn);

  const wrap = document.createElement('div');
  wrap.className = 'bg-switcher-group';
  [
    { id: 'none', icon: 'fa-solid fa-square', title: '纯色模式' },
    { id: 'grid', icon: 'fa-solid fa-border-all', title: '网格模式' },
    { id: 'dots', icon: 'fa-solid fa-ellipsis', title: '点阵模式' }
  ].forEach(bg => {
    const button = document.createElement('button');
    button.type = 'button';
    button.className = `bg-switch-btn${saved === bg.id ? ' active' : ''}`;
    button.title = bg.title;
    button.setAttribute('aria-label', bg.title);
    button.innerHTML = `<i class="${bg.icon}"></i>`;
    button.addEventListener('click', () => {
      document.body.setAttribute('data-bg', bg.id);
      storageSet('site-bg', bg.id);
      wrap.querySelectorAll('.bg-switch-btn').forEach(item => item.classList.remove('active'));
      button.classList.add('active');
    });
    wrap.appendChild(button);
  });
  group.appendChild(wrap);
}

export function toggleMenu(state, forceClose = false) {
  const sidebar = $('#sidebar');
  const overlay = $('#overlay');
  if (!sidebar || !overlay) return;
  const willOpen = forceClose ? false : !sidebar.classList.contains('active');
  const menuButton = $('.mobile-menu-btn');
  if (menuButton) {
    menuButton.setAttribute('aria-expanded', willOpen ? 'true' : 'false');
    menuButton.setAttribute('aria-label', willOpen ? '关闭菜单' : '打开菜单');
  }
  sidebar.setAttribute('aria-hidden', willOpen ? 'false' : 'true');
  if (willOpen) {
    state._menuScrollY = window.scrollY;
    document.body.classList.add('menu-open');
    document.body.style.top = `-${state._menuScrollY}px`;
    sidebar.classList.add('active');
    overlay.classList.add('active');
    return;
  }
  sidebar.classList.remove('active');
  overlay.classList.remove('active');
  document.body.classList.remove('menu-open');
  window.scrollTo(0, Math.abs(parseInt(document.body.style.top || '0', 10)) || state._menuScrollY || 0);
  document.body.style.top = '';
}

export function handleScroll() {
  const scrollTop = window.scrollY || 0;
  const topButton = $('#float-top-btn');
  if (topButton) topButton.classList.toggle('visible', scrollTop > 300);
  const bottomButton = $('#float-bottom-btn');
  if (bottomButton) {
    bottomButton.classList.toggle('visible', document.documentElement.scrollHeight - window.innerHeight - scrollTop > 300);
  }
  if (isArticle()) {
    let progressBar = $('#reading-progress');
    if (!progressBar) {
      progressBar = document.createElement('div');
      progressBar.id = 'reading-progress';
      document.body.appendChild(progressBar);
    }
    const max = document.documentElement.scrollHeight - document.documentElement.clientHeight;
    progressBar.style.width = `${max > 0 ? (scrollTop / max) * 100 : 0}%`;
    progressBar.style.display = 'block';
    return;
  }
  const progressBar = $('#reading-progress');
  if (progressBar) progressBar.style.display = 'none';
}

export function startTimer() {
  const start = new Date(SITE.uptimeStart || '2026-01-21').getTime();
  const el = $('#uptime');
  if (!el || !start) return;
  const update = () => {
    el.innerText = Math.floor((Date.now() - start) / 86400000);
  };
  update();
  setInterval(update, 60000);
}
