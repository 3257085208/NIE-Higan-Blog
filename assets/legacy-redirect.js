(async () => {
  const safeDecode = value => {
    try { return decodeURIComponent(value); } catch { return value; }
  };
  const candidates = new Set([
    location.pathname,
    safeDecode(location.pathname),
    location.hash ? location.hash.slice(1) : '',
    location.hash ? safeDecode(location.hash.slice(1)) : ''
  ]);
  const safeInternalUrl = value => {
    try {
      const url = new URL(String(value || ''), location.origin);
      if (url.origin !== location.origin || !url.pathname.startsWith('/')) return '';
      return `${url.pathname}${url.search}${url.hash}`;
    } catch {
      return '';
    }
  };
  try {
    const response = await fetch('/redirects.json', { cache: 'no-store' });
    if (!response.ok) return;
    const redirects = await response.json();
    for (const candidate of candidates) {
      if (candidate && typeof redirects[candidate] === 'string') {
        const target = safeInternalUrl(redirects[candidate]);
        if (target) {
          location.replace(target);
          return;
        }
      }
    }
  } catch (error) {
    console.warn('Legacy redirect lookup failed', error);
  }
})();
