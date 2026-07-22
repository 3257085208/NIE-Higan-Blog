import { $, $$, safeInternalUrl } from '../utils.js';

function createPostItem(post, index) {
  const node = document.createElement('div');
  node.className = 'post-item';
  node.style.opacity = '0';
  node.style.animation = `fadeInUp 0.4s cubic-bezier(0.2,0.8,0.2,1) ${index * 0.05}s forwards`;

  const date = document.createElement('div');
  date.className = 'post-date';
  date.textContent = post.date || '';

  const link = document.createElement('a');
  link.href = safeInternalUrl(post.url);
  link.className = 'post-title-link';
  link.textContent = post.title || '';
  if (+post.top >= 1000) {
    const badge = document.createElement('span');
    badge.className = 'top-badge';
    const icon = document.createElement('i');
    icon.className = 'fa-solid fa-fire';
    badge.append(icon, document.createTextNode(' 置顶'));
    link.appendChild(badge);
  }
  node.append(date, link);

  if (Array.isArray(post.tags) && post.tags.length) {
    const tags = document.createElement('div');
    tags.className = 'post-tags';
    post.tags.forEach(value => {
      const tag = document.createElement('button');
      tag.type = 'button';
      tag.className = 'tag-pill tag-filter';
      tag.textContent = `#${value}`;
      tags.appendChild(tag);
    });
    node.appendChild(tags);
  }
  return node;
}

function bindListEvents(state, rerender, onStateChange) {
  if (state._homeListBound) return;
  state._homeListBound = true;

  const input = $('#home-search-input');
  const clearBtn = $('#home-search-clear');
  const prevBtns = $$('#home-pager-prev, .home-pager-prev-btn');
  const nextBtns = $$('#home-pager-next, .home-pager-next-btn');
  const container = $('#posts-container');

  if (input) {
    input.addEventListener('input', () => {
      state.homeListState.q = input.value || '';
      state.homeListState.page = 1;
      rerender();
    });
  }

  if (clearBtn && input) {
    clearBtn.addEventListener('click', () => {
      input.value = '';
      state.homeListState.q = '';
      state.homeListState.page = 1;
      rerender();
      input.focus();
    });
  }

  prevBtns.forEach(button => button.addEventListener('click', () => {
    if (button.classList.contains('disabled')) return;
    state.homeListState.page = Math.max(1, state.homeListState.page - 1);
    rerender();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }));

  nextBtns.forEach(button => button.addEventListener('click', () => {
    if (button.classList.contains('disabled')) return;
    state.homeListState.page += 1;
    rerender();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }));

  container?.addEventListener('click', event => {
    const pill = event.target?.closest?.('.tag-filter');
    if (!pill) return;
    const tag = (pill.textContent || '').replace(/^#/, '').trim();
    if (!tag || !input) return;
    input.value = tag;
    state.homeListState.q = tag;
    state.homeListState.page = 1;
    rerender();
  });

  if (typeof onStateChange === 'function') onStateChange();
}

export function renderList(state, onStateChange) {
  const container = $('#posts-container');
  if (!container) return;
  if (!state.homeListState) state.homeListState = { q: '', page: 1, perPage: 10 };

  bindListEvents(state, () => renderList(state, onStateChange), onStateChange);

  const listState = state.homeListState;
  const input = $('#home-search-input');
  const clearBtn = $('#home-search-clear');
  const prevBtns = $$('#home-pager-prev, .home-pager-prev-btn');
  const nextBtns = $$('#home-pager-next, .home-pager-next-btn');
  const infos = $$('#home-pager-info, .home-pager-info-txt');

  const normalPosts = (state.posts || []).filter(post => post?.category !== '说说');
  const normalize = value => (value || '').toString().toLowerCase();
  const tokens = normalize(listState.q).trim().split(/\s+/).filter(Boolean);

  let filtered = normalPosts;
  if (tokens.length) {
    filtered = normalPosts.filter(post => {
      const blob = [
        normalize(post.title),
        normalize(post.category),
        (post.tags || []).map(normalize).join(' '),
        normalize(post.summary || ''),
        normalize(post.content || ''),
        normalize(post.file || '')
      ].join(' ');
      return tokens.every(token => blob.includes(token));
    });
  }

  const perPage = listState.perPage || 10;
  const totalPages = Math.max(1, Math.ceil(filtered.length / perPage));
  listState.page = Math.min(Math.max(1, listState.page), totalPages);
  const start = (listState.page - 1) * perPage;
  const pagePosts = filtered.slice(start, start + perPage);

  if (listState.q || listState.page > 1 || state._clientRendered) {
    state._clientRendered = true;
    container.innerHTML = '';
    if (!pagePosts.length) {
      const empty = document.createElement('div');
      empty.className = 'empty-list-message';
      empty.textContent = '没有找到匹配的文章';
      container.appendChild(empty);
    } else {
      pagePosts.forEach((post, index) => container.appendChild(createPostItem(post, index)));
    }
  }

  if (clearBtn && input) clearBtn.classList.toggle('hidden', !(input.value?.trim()));
  infos.forEach(info => {
    info.innerText = `${listState.page}/${totalPages} · ${filtered.length}篇`;
  });
  prevBtns.forEach(button => {
    const disabled = listState.page <= 1;
    button.classList.toggle('disabled', disabled);
    button.disabled = disabled;
    button.setAttribute('aria-disabled', String(disabled));
  });
  nextBtns.forEach(button => {
    const disabled = listState.page >= totalPages;
    button.classList.toggle('disabled', disabled);
    button.disabled = disabled;
    button.setAttribute('aria-disabled', String(disabled));
  });

  if (typeof onStateChange === 'function') onStateChange();
}
