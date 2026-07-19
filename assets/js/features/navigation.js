import { $, isArticle } from '../utils.js';

export function redirectLegacyHashRoutes(state) {
  const raw = location.hash ? location.hash.slice(1) : '';
  if (!raw) return false;
  const hash = decodeURIComponent(raw);
  const map = { archive: '/archive/', category: '/category/', status: '/status/', guestbook: '/guestbook/' };
  if (map[hash]) {
    location.replace(map[hash]);
    return true;
  }
  state._pendingHashPost = hash;
  return false;
}

export function redirectHashPostToCanonical(state) {
  const hash = state._pendingHashPost;
  if (!hash || !state.posts?.length) return;
  for (const key of [hash, decodeURIComponent(hash)]) {
    const hit = state.posts.find(post =>
      post?.file === key ||
      post?.file?.replace(/\.md$/i, '') === key ||
      post?.slug === key ||
      post?.url?.replace(/\/$/, '') === key.replace(/\/$/, '')
    );
    if (hit?.url) {
      location.replace(hit.url);
      break;
    }
  }
  state._pendingHashPost = '';
}

export function renderPrevNext(state) {
  const articleView = $('#article-view');
  if (!articleView || !state.posts?.length) return;
  const normalPosts = state.posts.filter(post => post?.category !== '说说');
  if (!normalPosts.length) return;
  const currentPath = location.pathname.replace(/\/$/, '');
  const currentIndex = normalPosts.findIndex(post => post.url?.replace(/\/$/, '') === currentPath);
  if (currentIndex === -1) return;
  const current = normalPosts[currentIndex];

  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el && !el.innerText) el.innerText = value || '';
  };

  setText('article-date', current.date || '未知');
  setText('article-category', current.category || '默认');
  setText('article-words', current.word_count || '0');

  const articleTags = $('#article-tags');
  if (articleTags && !articleTags.innerText) {
    articleTags.innerText = current.tags?.length ? current.tags.join(', ') : '';
    if (!current.tags?.length && articleTags.parentElement) {
      articleTags.parentElement.style.display = 'none';
    }
  }

  if ($('.post-navigation')) return;
  const newer = currentIndex > 0 ? normalPosts[currentIndex - 1] : null;
  const older = currentIndex < normalPosts.length - 1 ? normalPosts[currentIndex + 1] : null;
  if (!newer && !older) return;

  const makeItem = (post, klass, hint) => {
    if (!post) {
      const empty = document.createElement('div');
      empty.className = 'nav-item empty';
      return empty;
    }
    const anchor = document.createElement('a');
    anchor.href = post.url || '/';
    anchor.className = `nav-item ${klass}`;
    anchor.innerHTML = `<div class="nav-hint">${hint}</div><div class="nav-title"></div>`;
    anchor.querySelector('.nav-title').textContent = post.title || '';
    return anchor;
  };

  const nav = document.createElement('div');
  nav.className = 'post-navigation';
  nav.append(
    makeItem(older, 'nav-prev', '<i class="fa-solid fa-arrow-left"></i> 上一篇'),
    makeItem(newer, 'nav-next', '下一篇 <i class="fa-solid fa-arrow-right"></i>')
  );
  const articleContent = $('#article-content');
  if (articleContent?.parentNode) articleContent.parentNode.insertBefore(nav, articleContent.nextSibling);
  else articleView.appendChild(nav);
}

export function fetchPostsIfNeeded(state, onReady) {
  const pageType = document.body?.getAttribute('data-page') || '';
  const needList = !!$('#posts-container') && pageType === 'home';
  const needHash = !!state._pendingHashPost;
  if (!needList && !needHash && !isArticle()) return;

  fetch('/posts.json', { cache: 'no-store' })
    .then(response => (response.ok ? response.json() : []))
    .then(data => {
      if (Array.isArray(data)) state.posts = data;
      onReady({ needList, needHash });
    })
    .catch(error => console.warn('posts.json load failed', error));
}

