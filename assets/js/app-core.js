import { enhanceMarkdown } from './enhance.js';
import { initEasterEggs } from './features/effects.js';
import { initExternalLinkChecker, initLikes, initSelfHostedStats, initWaline } from './features/integrations.js';
import { fetchPostsIfNeeded, redirectHashPostToCanonical, redirectLegacyHashRoutes, renderPrevNext } from './features/navigation.js';
import { renderList } from './features/listing.js';
import { checkGlobalBackBtn, handleScroll, initBackgroundSwitcher, loadTheme, startTimer, toggleMenu, toggleTheme } from './features/shell.js';
import { SITE } from './utils.js';

export function createApp() {
  const state = {
    posts: [],
    _pendingHashPost: '',
    _homeListBound: false,
    _menuScrollY: 0
  };

  return {
    ...state,

    init() {
      if (redirectLegacyHashRoutes(this)) return;
      window.addEventListener('scroll', () => this.handleScroll());
      this.loadTheme();
      this.fetchPostsIfNeeded();
      this.startTimer();
      initSelfHostedStats();
      this.checkGlobalBackBtn();
      this.handleScroll();
      enhanceMarkdown();
      this.initBackgroundSwitcher();
      initWaline();
      initEasterEggs(this);
      initExternalLinkChecker(this);
      initLikes();
    },

    showExternalLinkModal(url) {
      const old = document.getElementById('ext-link-modal');
      if (old) old.remove();
      const modal = document.createElement('div');
      const previousFocus = document.activeElement;
      modal.id = 'ext-link-modal';
      modal.className = 'ext-modal-overlay';
      const siteName = String(SITE.title || '本站');
      const box = document.createElement('div');
      box.className = 'ext-modal-box';
      box.setAttribute('role', 'dialog');
      box.setAttribute('aria-modal', 'true');
      box.setAttribute('aria-labelledby', 'ext-modal-title');
      const title = document.createElement('div');
      title.className = 'ext-modal-title';
      title.id = 'ext-modal-title';
      const shield = document.createElement('i');
      shield.className = 'fa-solid fa-shield-halved';
      shield.style.cssText = 'color:var(--accent);margin-right:8px';
      title.append(shield, document.createTextNode(`即将离开 ${siteName}`));
      const content = document.createElement('div');
      content.className = 'ext-modal-content';
      content.append(document.createTextNode('您即将离开 '));
      const strong = document.createElement('b');
      strong.textContent = siteName;
      content.append(strong, document.createTextNode('，去往：'));
      const destination = document.createElement('div');
      destination.className = 'ext-modal-url';
      destination.textContent = url;
      const warning = document.createElement('div');
      warning.style.cssText = 'margin-top:12px;font-size:0.85rem;opacity:0.8';
      warning.textContent = '请注意您的账号和财产安全。';
      content.append(destination, warning);
      const actions = document.createElement('div');
      actions.className = 'ext-modal-actions';
      const cancel = document.createElement('button');
      cancel.className = 'ext-btn ext-btn-cancel';
      cancel.type = 'button';
      cancel.textContent = '取消';
      const proceed = document.createElement('button');
      proceed.className = 'ext-btn ext-btn-continue';
      proceed.type = 'button';
      proceed.textContent = '继续访问';
      actions.append(cancel, proceed);
      box.append(title, content, actions);
      modal.appendChild(box);
      const close = () => {
        modal.remove();
        previousFocus?.focus?.();
      };
      cancel.addEventListener('click', close);
      proceed.addEventListener('click', () => {
        window.open(url, '_blank', 'noopener,noreferrer');
        close();
      });
      modal.addEventListener('click', event => {
        if (event.target === modal) close();
      });
      modal.addEventListener('keydown', event => {
        if (event.key === 'Escape') {
          event.preventDefault();
          close();
          return;
        }
        if (event.key !== 'Tab') return;
        if (event.shiftKey && document.activeElement === cancel) {
          event.preventDefault();
          proceed.focus();
        } else if (!event.shiftKey && document.activeElement === proceed) {
          event.preventDefault();
          cancel.focus();
        }
      });
      document.body.appendChild(modal);
      cancel.focus();
    },

    checkGlobalBackBtn() {
      checkGlobalBackBtn(this);
    },

    redirectLegacyHashRoutes() {
      return redirectLegacyHashRoutes(this);
    },

    fetchPostsIfNeeded() {
      fetchPostsIfNeeded(this, ({ needList, needHash }) => {
        if (needHash) redirectHashPostToCanonical(this);
        if (needList) this.renderList();
        renderPrevNext(this);
      });
    },

    renderList() {
      renderList(this, () => this.checkGlobalBackBtn());
    },

    handleScroll,
    initBackgroundSwitcher,
    loadTheme,
    startTimer,
    toggleTheme,

    toggleMenu(forceClose = false) {
      toggleMenu(this, forceClose);
    }
  };
}
