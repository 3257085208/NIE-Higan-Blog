import { $, $$ } from './utils.js';

export function bindTemplateActions(app) {
  const overlay = $('#overlay');
  if (overlay) {
    overlay.addEventListener('click', () => app.toggleMenu(true));
  }

  $$('.menu-link').forEach(link => {
    if (link.dataset.closeMenu === '1') {
      link.addEventListener('click', () => app.toggleMenu(true));
    }
  });

  const brandLink = $('[data-home-link]');
  if (brandLink) {
    brandLink.addEventListener('click', () => {
      location.href = '/';
    });
  }

  const themeToggle = $('#theme-icon');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => app.toggleTheme());
  }

  const mobileMenuButton = $('.mobile-menu-btn');
  if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', () => app.toggleMenu());
  }

  const backButton = $('#float-back-btn');
  if (backButton) {
    backButton.addEventListener('click', () => {
      location.href = '/';
    });
  }

  const topButton = $('#float-top-btn');
  if (topButton) {
    topButton.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

