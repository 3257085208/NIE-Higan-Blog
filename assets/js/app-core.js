import { enhanceMarkdown } from './enhance.js';
import { initEasterEggs } from './features/effects.js';
import { initExternalLinkChecker, initLikes, initSelfHostedStats, initWaline } from './features/integrations.js';
import { fetchPostsIfNeeded, redirectHashPostToCanonical, redirectLegacyHashRoutes, renderPrevNext } from './features/navigation.js';
import { renderList } from './features/listing.js';
import { checkGlobalBackBtn, handleScroll, initBackgroundSwitcher, loadTheme, startTimer, toggleMenu, toggleTheme } from './features/shell.js';

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
      modal.id = 'ext-link-modal';
      modal.className = 'ext-modal-overlay';
      modal.innerHTML = '<div class="ext-modal-box"><div class="ext-modal-title"><i class="fa-solid fa-shield-halved" style="color:var(--accent);margin-right:8px"></i>即将离开 Higan</div><div class="ext-modal-content">您即将离开本站，去往：<div class="ext-modal-url"></div><div style="margin-top:12px;font-size:0.85rem;opacity:0.8">请注意您的账号和财产安全。</div></div><div class="ext-modal-actions"><button class="ext-btn ext-btn-cancel" type="button">取消</button><button class="ext-btn ext-btn-continue" type="button">继续访问</button></div></div>';
      modal.querySelector('.ext-modal-url').textContent = url;
      modal.querySelector('.ext-btn-cancel').addEventListener('click', () => modal.remove());
      modal.querySelector('.ext-btn-continue').addEventListener('click', () => {
        window.open(url, '_blank', 'noopener,noreferrer');
        modal.remove();
      });
      document.body.appendChild(modal);
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

