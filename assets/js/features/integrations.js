import { CFG, LIKE_API, PV_API, $, $$, isArticle, loadCSSOnce, importOnce, safeParse } from '../utils.js';

export function initExternalLinkChecker(app) {
  const whitelist = ['example.com', location.hostname]
    .map(domain => {
      try {
        return new URL(`https://${domain}`).hostname.toLowerCase();
      } catch {
        return String(domain || '').toLowerCase();
      }
    })
    .filter(Boolean);

  document.addEventListener('click', event => {
    const anchor = (event.target?.closest ? event.target : event.target?.parentElement)?.closest?.('a');
    if (!anchor) return;
    const href = (anchor.getAttribute('href') || '').trim();
    if (!href || href.startsWith('#') || /^(mailto|tel):/i.test(href)) return;
    if (/^javascript:/i.test(href)) {
      event.preventDefault();
      return;
    }
    try {
      const url = new URL(href, location.origin);
      if (url.origin === location.origin) return;
      if (!whitelist.some(domain => url.hostname.toLowerCase() === domain || url.hostname.toLowerCase().endsWith(`.${domain}`))) {
        event.preventDefault();
        app.showExternalLinkModal(url.href);
      }
    } catch {
      event.preventDefault();
    }
  });
}

export function initLikes() {
  let local = safeParse(localStorage.getItem('nie_likes') || '[]', []);
  if (!Array.isArray(local)) local = [];

  const bind = () => {
    $$('.like-btn').forEach(button => {
      if (button.dataset.likeBound) return;
      button.dataset.likeBound = '1';
      const id = button.getAttribute('data-id') || location.pathname;
      const icon = $('i', button);
      const countEl = $('.like-count', button);
      if (local.includes(id)) {
        button.classList.add('liked');
        if (icon) icon.className = 'fa-solid fa-heart';
      }
      fetch(`${LIKE_API}?path=${encodeURIComponent(id)}&action=get`)
        .then(response => response.json())
        .then(data => {
          if (countEl) countEl.innerText = data.likes || 0;
        });
      button.onclick = event => {
        event.stopPropagation();
        const liked = button.classList.contains('liked');
        button.classList.toggle('liked');
        if (icon) icon.className = liked ? 'fa-regular fa-heart' : 'fa-solid fa-heart';
        fetch(`${LIKE_API}?path=${encodeURIComponent(id)}&action=${liked ? 'dec' : 'inc'}`)
          .then(response => response.json())
          .then(data => {
            if (countEl) countEl.innerText = data.likes || 0;
          });
        local = liked ? local.filter(item => item !== id) : [...local, id];
        localStorage.setItem('nie_likes', JSON.stringify(local));
      };
    });
  };

  bind();
  new MutationObserver(bind).observe($('#status-content') || document.body, { childList: true, subtree: true });
}

export function initSelfHostedStats() {
  const setPV = (path, elId) => {
    fetch(`${PV_API}?path=${encodeURIComponent(path)}`)
      .then(response => response.json())
      .then(data => {
        const el = document.getElementById(elId);
        if (el) el.innerText = data.pv;
      })
      .catch(() => {
        const el = document.getElementById(elId);
        if (el) el.innerText = '-';
      });
  };

  setPV('site', 'site-pv');
  if (isArticle()) setPV(location.pathname, 'article-pv');
}

export function initWaline() {
  const walineCfg = CFG.waline;
  const root = $('#waline');
  const pageType = document.body?.getAttribute('data-page') || '';
  if (!walineCfg || !root || !['post', 'guestbook'].includes(pageType)) return;
  loadCSSOnce('https://cdn.jsdelivr.net.i8-mc.cn/npm/@waline/client/dist/waline.css');
  importOnce('https://cdn.jsdelivr.net.i8-mc.cn/npm/@waline/client/dist/waline.mjs')
    .then(({ init }) => {
      if (typeof init !== 'function' || root.dataset.inited === '1') return;
      root.dataset.inited = '1';
      init({
        el: '#waline',
        serverURL: walineCfg.serverURL,
        path: location.pathname,
        emoji: walineCfg.emoji,
        login: walineCfg.login,
        pageview: walineCfg.pageview,
        search: walineCfg.search,
        imageUploader: walineCfg.imageUploader,
        locale: walineCfg.locale,
        dark: '[data-theme="dark"]'
      });
    })
    .catch(error => console.warn('Waline load failed', error));
}

