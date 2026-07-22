import { $, $$ } from './utils.js';

export function bindTemplateActions(app) {
  const overlay = $('#overlay');
  const mobileMenuButton = $('.mobile-menu-btn');
  const closeMenu = () => {
    app.toggleMenu(true);
    mobileMenuButton?.focus();
  };
  if (overlay) {
    overlay.addEventListener('click', closeMenu);
  }

  $$('.menu-link').forEach(link => {
    if (link.dataset.closeMenu === '1') {
      link.addEventListener('click', () => app.toggleMenu(true));
    }
  });

  const themeToggle = $('#theme-icon');
  if (themeToggle) {
    themeToggle.addEventListener('click', () => app.toggleTheme());
  }

  if (mobileMenuButton) {
    mobileMenuButton.addEventListener('click', () => {
      app.toggleMenu();
      if ($('#sidebar')?.classList.contains('active')) {
        $('#sidebar .menu-link')?.focus();
      }
    });
  }

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape' && $('#sidebar')?.classList.contains('active')) closeMenu();
  });

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

