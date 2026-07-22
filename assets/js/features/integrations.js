import { CFG, LIKE_API, PV_API, SITE, $, $$, isArticle, loadCSSOnce, importOnce, safeParse } from '../utils.js';

export function initExternalLinkChecker(app) {
  const configured = Array.isArray(CFG.externalLinkWhitelist) ? CFG.externalLinkWhitelist : [];
  const whitelist = [...configured, SITE.url, location.hostname]
    .map(domain => {
      try {
        const value = String(domain || '');
        return new URL(value.includes('://') ? value : `https://${value}`).hostname.toLowerCase();
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
  if (!LIKE_API) return;
  let local = safeParse(localStorage.getItem('nie_likes') || '[]', []);
  if (!Array.isArray(local)) local = [];

  const bind = () => {
    $$('.like-btn').forEach(button => {
      if (button.dataset.likeBound || button.closest('.hidden')) return;
      button.dataset.likeBound = '1';
      const id = button.getAttribute('data-id') || location.pathname;
      const icon = $('i', button);
      const countEl = $('.like-count', button);
      if (local.includes(id)) {
        button.classList.add('liked');
        button.setAttribute('aria-pressed', 'true');
        if (icon) icon.className = 'fa-solid fa-heart';
      }
      fetch(`${LIKE_API}?path=${encodeURIComponent(id)}&action=get`, { cache: 'no-store' })
        .then(response => {
          if (!response.ok) throw new Error(`Like API returned ${response.status}`);
          return response.json();
        })
        .then(data => {
          if (countEl) countEl.innerText = data.likes || 0;
        })
        .catch(error => {
          if (countEl) countEl.innerText = '-';
          console.warn('Like count load failed', error);
        });
      button.onclick = async event => {
        event.stopPropagation();
        const liked = button.classList.contains('liked');
        button.disabled = true;
        try {
          const response = await fetch(`${LIKE_API}?path=${encodeURIComponent(id)}&action=${liked ? 'dec' : 'inc'}`, { cache: 'no-store' });
          if (!response.ok) throw new Error(`Like API returned ${response.status}`);
          const data = await response.json();
          button.classList.toggle('liked', !liked);
          button.setAttribute('aria-pressed', liked ? 'false' : 'true');
          if (icon) icon.className = liked ? 'fa-regular fa-heart' : 'fa-solid fa-heart';
          if (countEl) countEl.innerText = data.likes || 0;
          local = liked ? local.filter(item => item !== id) : [...new Set([...local, id])];
          localStorage.setItem('nie_likes', JSON.stringify(local));
        } catch (error) {
          console.warn('Like update failed', error);
        } finally {
          button.disabled = false;
        }
      };
    });
  };

  bind();
  new MutationObserver(bind).observe($('#status-content') || document.body, { childList: true, subtree: true });
}

export function initSelfHostedStats() {
  if (!PV_API) return;
  const setPV = (path, elId) => {
    fetch(`${PV_API}?path=${encodeURIComponent(path)}`, { cache: 'no-store' })
      .then(response => {
        if (!response.ok) throw new Error(`PV API returned ${response.status}`);
        return response.json();
      })
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
  loadCSSOnce('/assets/vendor/waline/waline.css');
  importOnce('/assets/vendor/waline/waline.js')
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
