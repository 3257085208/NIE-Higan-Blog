export const CFG = window.SITE_CONFIG || {};
export const SITE = CFG.site || {};
export const PV_API = 'https://api.example.com/api/pv';
export const LIKE_API = 'https://api.example.com/api/like';

export const safeParse = (value, fallback) => {
  try { return JSON.parse(value); } catch { return fallback; }
};

export function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}


export const $ = (selector, root) => (root || document).querySelector(selector);
export const $$ = (selector, root) => [...(root || document).querySelectorAll(selector)];
export const isArticle = () => document.body?.getAttribute('data-page') === 'post' || !!($('#article-view') && !$('#article-view').classList.contains('hidden'));

let moduleCache;
export function importOnce(src) {
  if (!moduleCache) moduleCache = new Map();
  if (!moduleCache.has(src)) moduleCache.set(src, import(src));
  return moduleCache.get(src);
}

export function loadCSSOnce(href) {
  if (!href || $(`link[href="${href}"]`)) return;
  const link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = href;
  document.head.appendChild(link);
}

export async function copyText(text) {
  if (!text) return false;
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(text);
      return true;
    }
  } catch {}
  try {
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '1');
    textarea.style.cssText = 'position:fixed;top:-1000px';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    const ok = document.execCommand('copy');
    document.body.removeChild(textarea);
    return !!ok;
  } catch {
    return false;
  }
}

export function unlockThemeTransition() {
  requestAnimationFrame(() => {
    document.documentElement.style.backgroundColor = '';
    document.documentElement.classList.remove('no-theme-transition');
  });
}

export function applyTheme(theme) {
  const value = (theme === 'dark' || theme === 'night') ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', value);
  document.documentElement.style.colorScheme = value;
  if (document.body) document.body.setAttribute('data-theme', value);
  const icon = $('#theme-icon');
  if (icon) {
    icon.className = value === 'light'
      ? 'fa-solid fa-sun theme-icon icon-button'
      : 'fa-solid fa-moon theme-icon icon-button';
  }
  return value;
}
