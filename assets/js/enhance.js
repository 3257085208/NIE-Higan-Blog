import { $, $$, copyText } from './utils.js';

export function enhanceCodeBlocks(root) {
  $$('.markdown-body pre', root).forEach(pre => {
    if (pre.dataset.enhanced) return;
    pre.dataset.enhanced = '1';
    const code = $('code', pre);
    if (!code) return;
    const button = document.createElement('button');
    button.className = 'md-copy-btn';
    button.type = 'button';
    button.setAttribute('aria-label', '复制代码');
    button.innerHTML = '<i class="fa-regular fa-copy"></i>';
    button.addEventListener('click', async () => {
      if (!(await copyText(code.innerText || code.textContent || ''))) return;
      button.classList.add('copied');
      button.innerHTML = '<i class="fa-solid fa-check"></i>';
      setTimeout(() => {
        button.classList.remove('copied');
        button.innerHTML = '<i class="fa-regular fa-copy"></i>';
      }, 1400);
    });
    pre.appendChild(button);
  });
}

export function enhanceTables(root) {
  $$('.markdown-body table', root).forEach(table => {
    if (table.parentElement?.classList.contains('md-table-wrap')) return;
    const wrap = document.createElement('div');
    wrap.className = 'md-table-wrap';
    table.parentNode.insertBefore(wrap, table);
    wrap.appendChild(table);
  });
}

export function enhanceTabs(root) {
  $$('.nsk-magic-tabs', root).forEach(group => {
    if (group.dataset.enhanced) return;
    group.dataset.enhanced = '1';
    const buttons = $$(':scope > .nsk-magic-tab-title', group);
    const panels = $$(':scope > .nsk-magic-tab-body', group);
    if (!buttons.length || !panels.length) return;
    const activate = index => {
      buttons.forEach(button => {
        const on = +button.getAttribute('data-tab-index') === index;
        button.classList.toggle('is-active', on);
        button.setAttribute('aria-selected', on ? 'true' : 'false');
        button.tabIndex = on ? 0 : -1;
      });
      panels.forEach(panel => {
        const on = +panel.getAttribute('data-tab-index') === index;
        panel.classList.toggle('is-active', on);
        panel.hidden = !on;
      });
    };
    buttons.forEach(button => {
      const index = +button.getAttribute('data-tab-index');
      button.addEventListener('click', () => activate(index));
      button.addEventListener('keydown', event => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          activate(index);
        }
      });
    });
    activate(+((buttons.find(button => button.classList.contains('is-active')) || buttons[0]).getAttribute('data-tab-index')) || 0);
  });
}

export function enhanceStatusImages(root) {
  $$('.status-card', root).forEach(card => {
    if (card.dataset.imagesEnhanced) return;
    card.dataset.imagesEnhanced = '1';
    const images = $$('img', card);
    if (!images.length) return;
    const grid = document.createElement('div');
    grid.className = `status-image-grid count-${images.length}`;
    images.forEach(image => {
      const item = document.createElement('div');
      item.className = 'status-image-item';
      const next = document.createElement('img');
      next.src = image.src;
      next.alt = image.alt || 'status image';
      next.loading = 'lazy';
      next.addEventListener('click', event => {
        event.stopPropagation();
        const overlay = document.createElement('div');
        overlay.className = 'status-lightbox-overlay';
        const lightboxImage = document.createElement('img');
        lightboxImage.src = next.src;
        lightboxImage.alt = next.alt;
        lightboxImage.className = 'status-lightbox-img';
        overlay.appendChild(lightboxImage);
        overlay.onclick = () => overlay.remove();
        document.body.appendChild(overlay);
      });
      item.appendChild(next);
      grid.appendChild(item);
      image.remove();
    });
    $$('p', card).forEach(paragraph => {
      const text = paragraph.innerHTML.replace(/<br\s*\/?>/gi, '').trim();
      if (!text) paragraph.remove();
      else paragraph.innerHTML = paragraph.innerHTML.replace(/(<br\s*\/?>\s*)+$/gi, '');
    });
    card.appendChild(grid);
  });
}

export function buildTOC() {
  const article = $('#article-content');
  if (!article) return;
  const headers = $$('h1, h2, h3, h4', article);
  if (!headers.length || $('.toc-container')) return;
  const container = document.createElement('div');
  container.className = 'toc-container';
  container.innerHTML = '<div class="toc-title"><i class="fa-solid fa-list-ul"></i> 文章目录</div>';
  const list = document.createElement('ul');
  list.className = 'toc-list';
  const links = [];
  headers.forEach(header => {
    if (!header.id) header.id = 'h-' + Math.random().toString(36).substr(2, 5);
    const level = header.tagName.replace('H', '');
    const link = document.createElement('a');
    link.href = `#${header.id}`;
    link.className = 'toc-link';
    link.innerText = header.innerText.replace(/^[#\s]+/, '');
    link.title = header.innerText;
    link.addEventListener('click', event => {
      event.preventDefault();
      const target = document.getElementById(header.id);
      if (target) window.scrollTo({ top: target.getBoundingClientRect().top + window.scrollY - 80, behavior: 'smooth' });
    });
    const item = document.createElement('li');
    item.className = `toc-item toc-level-${level}`;
    item.appendChild(link);
    list.appendChild(item);
    links.push({ id: header.id, link });
  });
  container.appendChild(list);
  document.body.appendChild(container);
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      links.forEach(item => item.link.classList.remove('active'));
      const current = links.find(item => item.id === entry.target.id);
      if (current) current.link.classList.add('active');
    });
  }, { rootMargin: '-80px 0px -70% 0px' });
  headers.forEach(header => observer.observe(header));
}

export function enhanceMarkdown(root = document) {
  enhanceCodeBlocks(root);
  enhanceTables(root);
  enhanceTabs(root);
  buildTOC();
  enhanceStatusImages(root);
}

