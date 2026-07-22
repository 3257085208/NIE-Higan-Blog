const LIVE2D_SRC = '/assets/vendor/live2d/autoload.js';

function initLive2D() {
  if (window.matchMedia && window.matchMedia('(max-width:768px)').matches) return;
  if (window.matchMedia && !window.matchMedia('(pointer:fine)').matches) return;
  if (window.__live2d_loaded) return;
  window.__live2d_loaded = 1;
  const script = document.createElement('script');
  script.src = LIVE2D_SRC;
  script.async = true;
  script.onerror = () => console.warn('Live2D load failed');
  document.body.appendChild(script);
}

function formatSeconds(value) {
  return value > 0 && Number.isFinite(value) ? value.toFixed(3) : '0.000';
}

function sampleRenderTimeFromNavigation(target) {
  const nav = performance.getEntriesByType?.('navigation')?.[0];
  let ms = null;
  if (nav?.domContentLoadedEventEnd) {
    ms = nav.domContentLoadedEventEnd - nav.startTime;
  } else if (performance.timing) {
    const timing = performance.timing;
    if (timing.domContentLoadedEventEnd && timing.navigationStart) {
      ms = timing.domContentLoadedEventEnd - timing.navigationStart;
    }
  }
  if (!(ms > 0)) return false;
  target.textContent = `渲染 ${formatSeconds(ms / 1000)} s`;
  return true;
}

function sampleRenderTimeFromFrames(target) {
  const start = performance.now();
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      target.textContent = `渲染 ${formatSeconds((performance.now() - start) / 1000)} s`;
    });
  });
}

function initRenderTimeLabel() {
  const target = document.getElementById('render-time-inline');
  if (!target) return;
  const run = () => {
    if (!sampleRenderTimeFromNavigation(target)) {
      sampleRenderTimeFromFrames(target);
    }
  };
  setTimeout(run, 0);
  window.addEventListener('hashchange', () => sampleRenderTimeFromFrames(target));
}

function initVisibilityTitle() {
  let resetTimer = null;
  let titleBeforeHidden = document.title;
  const getRestoreTitle = () => window.__title_before_hidden || titleBeforeHidden || document.title;

  document.addEventListener('visibilitychange', () => {
    if (resetTimer) {
      clearTimeout(resetTimer);
      resetTimer = null;
    }
    if (document.hidden) {
      titleBeforeHidden = document.title;
      window.__title_before_hidden = titleBeforeHidden;
      document.title = '你能不能不要走 QAQ';
      return;
    }
    document.title = '你回来啦！';
    resetTimer = setTimeout(() => {
      document.title = getRestoreTitle();
    }, 2000);
  });
}

export function initTemplateRuntime() {
  if (document.readyState === 'complete') {
    setTimeout(initLive2D, 300);
  } else {
    window.addEventListener('load', () => setTimeout(initLive2D, 300), { once: true });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initRenderTimeLabel, { once: true });
  } else {
    initRenderTimeLabel();
  }

  initVisibilityTitle();
}
