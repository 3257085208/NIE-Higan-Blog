import { $$, unlockThemeTransition } from './js/utils.js';
import { createApp } from './js/app-core.js';
import { bindTemplateActions } from './js/dom-actions.js';
import { initTemplateRuntime } from './js/template-runtime.js';

const app = createApp();
window.app = app;

$$('.back-btn').forEach(button => {
  if (button.tagName?.toLowerCase() !== 'a') button.onclick = () => location.href = '/';
});

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    bindTemplateActions(app);
    initTemplateRuntime();
    app.init();
    unlockThemeTransition();
  });
} else {
  bindTemplateActions(app);
  initTemplateRuntime();
  app.init();
  unlockThemeTransition();
}
