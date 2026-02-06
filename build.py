"""
Build script for NIE static blog.

Generates:
  - posts.json (for the SPA homepage)
  - sitemap.xml
  - per-post standalone pages at /p/<slug>/index.html

Design goals:
  - Keep existing UI (fonts/CSS/layout) unchanged.
  - Add SEO-friendlier standalone pages without changing how you write posts.

URL / slug strategy (important):
  - Primary slug uses the raw filename stem (keeps Chinese + spaces) so copied links work on tools like itdog.
  - Legacy slug uses percent-encoding (quote) for backward compatibility.
  - For each post we generate:
      /p/<primary>/index.html   -> real page
      /p/<legacy>/index.html    -> tiny redirect page to /p/<primary>/  (only when legacy != primary)
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import quote

import yaml

try:
    import markdown  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("Missing dependency: markdown. Install with: pip install markdown") from e


ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
OUTPUT_POSTS_JSON = ROOT / "posts.json"
OUTPUT_SITEMAP = ROOT / "sitemap.xml"
PAGES_DIR = ROOT / "p"


def strip_front_matter(text: str) -> Tuple[Optional[re.Match[str]], str]:
    m = re.match(r"^\s*---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", text, re.DOTALL)
    if m:
        return m, text[m.end() :]
    return None, text


def make_summary(body: str, limit: int = 180) -> str:
    t = body
    t = re.sub(r"```[\s\S]*?```", " ", t)
    t = re.sub(r"`([^`]+)`", r"\1", t)
    t = re.sub(r"!\[[^\]]*\]\([^\)]*\)", " ", t)
    t = re.sub(r"\[([^\]]+)\]\([^\)]*\)", r"\1", t)
    t = re.sub(r"^\s*[>#\-\*\+\d\.]+\s*", "", t, flags=re.M)
    t = re.sub(r"\s+", " ", t).strip()
    return t[:limit]


def parse_post_file(md_path: Path) -> Dict[str, Any]:
    filename = md_path.name
    item: Dict[str, Any] = {
        "file": filename,
        "title": filename.replace(".md", ""),
        "date": "2020-01-01",
        "category": "默认",
        "tags": [],
        "word_count": 0,
        "content": "",  # only used for category=说说
        "summary": "",
        "top": 0,
    }

    m = re.match(r"(\d{4}-\d{2}-\d{2})-(.+)\.md", filename)
    if m:
        item["date"] = m.group(1)
        item["title"] = m.group(2)

    raw = md_path.read_text(encoding="utf-8")
    fm, body = strip_front_matter(raw)
    item["word_count"] = len(re.sub(r"\s+", "", body))

    if fm:
        meta = yaml.safe_load(fm.group(1))
        if meta and isinstance(meta, dict):
            if "title" in meta:
                item["title"] = str(meta["title"])
            if "date" in meta:
                item["date"] = str(meta["date"])
            if "category" in meta:
                item["category"] = str(meta["category"])
            if "tags" in meta:
                if isinstance(meta["tags"], list):
                    item["tags"] = meta["tags"]
                elif meta["tags"] is None:
                    item["tags"] = []
                else:
                    item["tags"] = [str(meta["tags"])]
            if "top" in meta:
                try:
                    item["top"] = int(meta["top"])
                except Exception:
                    item["top"] = 0

    item["summary"] = make_summary(body)

    # “说说”直接内联到 posts.json（保持你原逻辑）
    if item["category"] == "说说":
        item["content"] = body.strip()

    return item


def slug_primary(filename: str) -> str:
    """Primary slug: keep Chinese/spaces to make shared links 'human' and compatible with more tools."""
    stem = filename[:-3] if filename.lower().endswith(".md") else filename
    # safety: forbid path separators
    stem = stem.replace("/", "-").replace("\\", "-")
    return stem


def slug_legacy_encoded(filename: str) -> str:
    """Legacy slug: percent-encoded for backward compatibility with older generated URLs."""
    stem = filename[:-3] if filename.lower().endswith(".md") else filename
    return quote(stem, safe="")


def md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=["fenced_code", "tables", "sane_lists", "smarty"],
        output_format="html5",
    )


def _html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )


def _xml_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def _extract_inline_style_from_index(index_path: Path) -> str:
    html = index_path.read_text(encoding="utf-8")
    m = re.search(r"<style>([\s\S]*?)</style>", html)
    if not m:
        return ""
    return "<style>\n" + m.group(1).strip("\n") + "\n</style>"


def _extract_footer_from_index(index_path: Path) -> str:
    """Keep footer identical by copying the footer markup from index.html."""
    html = index_path.read_text(encoding="utf-8")
    m = re.search(r"(<footer>[\s\S]*?</footer>)", html)
    return m.group(1) if m else ""


def write_redirect_page(out_path: Path, target_path: str, site_url: str) -> None:
    """
    Write a tiny redirect page for legacy URLs.
    target_path should be a site-relative path like '/p/xxx/'.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canonical = site_url.rstrip("/") + target_path
    out_path.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta http-equiv="refresh" content="0; url={_html_escape(target_path)}">
  <link rel="canonical" href="{_html_escape(canonical)}">
  <meta name="robots" content="noindex">
  <title>Redirecting...</title>
</head>
<body>
  Redirecting to <a href="{_html_escape(target_path)}">{_html_escape(target_path)}</a>
  <script>location.replace({json.dumps(target_path)});</script>
</body>
</html>
""",
        encoding="utf-8",
    )


def build_post_page(
    *,
    site_url: str,
    post: Dict[str, Any],
    md_path: Path,
    out_path: Path,
    canonical_path: str,
) -> None:
    raw = md_path.read_text(encoding="utf-8")
    _, body = strip_front_matter(raw)
    html_body = md_to_html(body)

    title = str(post.get("title") or "")
    date = str(post.get("date") or "")
    category = str(post.get("category") or "")
    tags = post.get("tags") or []
    tags_text = ", ".join([str(t) for t in tags]) if isinstance(tags, list) else str(tags)
    words = int(post.get("word_count") or 0)
    summary = str(post.get("summary") or "")

    canonical = site_url.rstrip("/") + canonical_path
    safe_desc = (summary or "聶.NET - A Geek's Blog").replace('"', "&quot;")
    page_title = f"{title} - 聶.NET" if title else "聶.NET"

    style_block = _extract_inline_style_from_index(ROOT / "index.html")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <meta name="referrer" content="strict-origin-when-cross-origin">
  <meta name="description" content="{safe_desc}">
  <link rel="canonical" href="{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{_html_escape(title)}">
  <meta property="og:description" content="{_html_escape(safe_desc)}">
  <meta property="og:url" content="{canonical}">
  <title>{_html_escape(page_title)}</title>

  <link rel="shortcut icon" href="https://img.i8-mc.cn/file/V4PF4kwS.ico">
  <link rel="icon" href="https://img.i8-mc.cn/file/V4PF4kwS.ico">

  <link rel="dns-prefetch" href="//npm.elemecdn.com">
  <link rel="dns-prefetch" href="//cdn.staticfile.org.i8-mc.cn">
  <link rel="dns-prefetch" href="//cdn.jsdelivr.net.i8-mc.cn">

  <link rel="preload" href="https://cdn.staticfile.org.i8-mc.cn/github-markdown-css/5.2.0/github-markdown-light.min.css" as="style">
  <link rel="preload" href="https://cdn.staticfile.org.i8-mc.cn/font-awesome/6.4.2/css/all.min.css" as="style">

  <link rel="stylesheet" href="https://cdn.staticfile.org.i8-mc.cn/github-markdown-css/5.2.0/github-markdown-light.min.css">
  <link rel="stylesheet" href="https://cdn.staticfile.org.i8-mc.cn/font-awesome/6.4.2/css/all.min.css">
  <link href="https://blog-assets.i8-mc.cn/nunito/nunito.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net.i8-mc.cn/npm/@waline/client@v2/dist/waline.css" />

{style_block}
</head>
<body data-theme="light">

<div id="overlay" onclick="toggleMenu(true)"></div>

<nav id="sidebar">
  <div style="font-weight:900; font-size:1.6rem; color:var(--accent); margin-bottom:20px;">MENU</div>
  <a href="/" onclick="toggleMenu(true)" class="menu-link"><i class="fa-solid fa-house"></i> 首页</a>
  <a href="/#status" onclick="toggleMenu(true)" class="menu-link"><i class="fa-solid fa-feather"></i> 动态</a>
  <a href="/#category" onclick="toggleMenu(true)" class="menu-link"><i class="fa-solid fa-folder-open"></i> 分类</a>
  <a href="/#archive" onclick="toggleMenu(true)" class="menu-link"><i class="fa-solid fa-box-archive"></i> 归档</a>
  <a href="/#guestbook.md" onclick="toggleMenu(true)" class="menu-link"><i class="fa-solid fa-comment-dots"></i> 留言板</a>
  <a href="https://status.nkx.moe" target="_blank" class="menu-link"><i class="fa-solid fa-server"></i> 站点状态</a>
</nav>

<div class="container">
  <header>
    <div class="brand-area">
      <img src="https://img.i8-mc.cn/file/J0NJk8wH.jpeg" class="avatar" alt="avatar" onclick="location.href='/'">
      <div style="display:flex; align-items:center;">
        <span class="site-title" onclick="location.href='/'">聶.NET</span>
        <i id="theme-icon" class="fa-solid fa-sun theme-icon" onclick="toggleTheme()"></i>
      </div>
    </div>

    <nav class="pc-nav">
      <a href="/">首页</a>
      <span class="nav-divider">/</span>
      <a href="/#status">动态</a>
      <span class="nav-divider">/</span>
      <a href="/#category">分类</a>
      <span class="nav-divider">/</span>
      <a href="/#archive">归档</a>
      <span class="nav-divider">/</span>
      <a href="/#guestbook.md">留言</a>
      <span class="nav-divider">/</span>
      <a href="https://status.nkx.moe" target="_blank">状态</a>
    </nav>

    <div class="mobile-menu-btn" onclick="toggleMenu()">
      <i class="fa-solid fa-bars"></i>
    </div>
  </header>

  <div id="article-view">
    <div class="back-btn" onclick="location.href='/'">← 返回列表</div>
    <h1 class="article-title">{_html_escape(title)}</h1>
    <div class="article-meta">
      <span><i class="fa-regular fa-calendar"></i> {_html_escape(date)}</span>
      <span><i class="fa-regular fa-folder"></i> {_html_escape(category)}</span>
      <span><i class="fa-regular fa-hashtag"></i> {_html_escape(tags_text)}</span>
      <span><i class="fa-regular fa-file-word"></i> {words:,}</span>
    </div>
    <article class="markdown-body">{html_body}</article>

    <div style="margin-top:50px;">
      <div id="custom-toolbar">
        <button class="toolbar-btn" onclick="insertText('**','**')"><i class="fa-solid fa-bold"></i></button>
        <button class="toolbar-btn" onclick="insertText('*','*')"><i class="fa-solid fa-italic"></i></button>
        <button class="toolbar-btn" onclick="insertText('~~','~~')"><i class="fa-solid fa-strikethrough"></i></button>
        <button class="toolbar-btn" onclick="insertText('`','`')"><i class="fa-solid fa-code"></i></button>
        <button class="toolbar-btn" onclick="insertText('> ','')"><i class="fa-solid fa-quote-left"></i></button>
        <button class="toolbar-btn" onclick="insertText('[](',')')"><i class="fa-solid fa-link"></i></button>
      </div>
      <div id="waline"></div>
    </div>
  </div>

  {_extract_footer_from_index(ROOT / "index.html")}
</div>

<div id="float-btn-group">
  <div class="float-btn" onclick="window.scrollTo({{top:0, behavior:'smooth'}})" title="顶部"><i class="fa-solid fa-arrow-up"></i></div>
</div>

<script src="https://cdn.jsdelivr.net.i8-mc.cn/npm/@waline/client@v2/dist/waline.js"></script>
<script async src="https://busuanzi.ibruce.info.i8-mc.cn/busuanzi/2.3/busuanzi.pure.mini.js" onerror="console.warn('busuanzi load failed')"></script>

<script>
  // Theme
  function loadTheme() {{
    const t = localStorage.getItem('theme') || 'light';
    document.body.setAttribute('data-theme', t);
    const icon = document.getElementById('theme-icon');
    if (icon) icon.className = t==='light' ? 'fa-solid fa-sun theme-icon' : 'fa-solid fa-moon theme-icon';
  }}
  function toggleTheme() {{
    const cur = document.body.getAttribute('data-theme');
    const next = cur==='light'?'dark':'light';
    document.body.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    loadTheme();
  }}
  loadTheme();

  // iOS scroll lock menu (same UX as homepage)
  let _menuScrollY = 0;
  function toggleMenu(forceClose=false) {{
    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('overlay');
    if (!sidebar || !overlay) return;
    const isOpen = sidebar.classList.contains('active');
    const willOpen = forceClose ? false : !isOpen;
    if (willOpen) {{
      _menuScrollY = window.scrollY || 0;
      document.body.classList.add('menu-open');
      document.body.style.top = `-${{_menuScrollY}}px`;
      sidebar.classList.add('active');
      overlay.classList.add('active');
    }} else {{
      sidebar.classList.remove('active');
      overlay.classList.remove('active');
      document.body.classList.remove('menu-open');
      const y = _menuScrollY || 0;
      document.body.style.top = '';
      window.scrollTo(0, y);
    }}
  }}

  // Waline
  function initWaline(path) {{
    if (!window.Waline) return;
    Waline.init({{
      el: '#waline',
      serverURL: 'https://waline.nkx.moe/',
      path: path,
      dark: 'body[data-theme="dark"]',
      emoji: ['//cdn.jsdelivr.net.i8-mc.cn/npm/@waline/emojis@1.1.0/weibo'],
      login: 'false',
      pageview: true,
      search: false, imageUploader: false,
      locale: {{ placeholder: '此处支持 Markdown 语法...' }}
    }});
  }}
  initWaline({json.dumps(post.get("file"))});

  // Waline toolbar helpers
  function insertText(prefix, suffix) {{
    const textarea = document.querySelector('.wl-editor');
    if (!textarea) return;
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const text = textarea.value;
    textarea.value = text.substring(0, start) + prefix + text.substring(start, end) + suffix + text.substring(end);
    textarea.focus();
    textarea.selectionStart = start + prefix.length;
    textarea.selectionEnd = end + prefix.length;
  }}

  // Float button
  window.addEventListener('scroll', () => {{
    const btnGroup = document.getElementById('float-btn-group');
    if (!btnGroup) return;
    if (window.scrollY > 300) btnGroup.classList.add('visible');
    else btnGroup.classList.remove('visible');
  }});

  // Uptime (same as homepage)
  (function startTimer() {{
    const start = new Date('2026-01-21').getTime();
    setInterval(() => {{
      const now = Date.now();
      const el = document.getElementById('uptime');
      if (el) el.innerText = Math.floor((now-start)/86400000);
    }}, 1000);
  }})();

  // Footer stats (avoid showing 0 on standalone pages)
  (function loadFooterStats() {{
    const postsEl = document.getElementById('total-posts');
    const wordsEl = document.getElementById('total-words');
    if (!postsEl && !wordsEl) return;
    fetch('/posts.json?t=' + Date.now())
      .then(r => r.ok ? r.json() : null)
      .then(data => {{
        if (!data || !Array.isArray(data)) return;
        const realPosts = data.filter(p => p && p.category !== '说说');
        let totalWords = 0;
        data.forEach(p => totalWords += (p && p.word_count) ? p.word_count : 0);
        if (postsEl) postsEl.innerText = realPosts.length;
        if (wordsEl) wordsEl.innerText = totalWords.toLocaleString();
      }})
      .catch(() => {{}});
  }})();
</script>

</body>
</html>
""",
        encoding="utf-8",
    )


def main() -> None:
    site_url = os.environ.get("SITE_URL", "https://写你的域名").rstrip("/")

    if not POSTS_DIR.exists():
        raise SystemExit(f"posts directory not found: {POSTS_DIR}")

    # Clean previously generated standalone pages to avoid stale URLs.
    if PAGES_DIR.exists():
        shutil.rmtree(PAGES_DIR)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    posts: List[Dict[str, Any]] = []
    for md in sorted(POSTS_DIR.iterdir()):
        if md.suffix.lower() != ".md":
            continue
        # Keep behavior consistent with the SPA: don't include guestbook in index/sitemap/pages.
        if "guestbook" in md.name.lower():
            continue
        try:
            item = parse_post_file(md)
        except Exception as e:
            print(f"[WARN] Failed to process {md.name}: {e}")
            continue
        posts.append(item)

    posts.sort(
        key=lambda x: (int(x.get("top", 0)), str(x.get("date", "")), str(x.get("file", ""))),
        reverse=True,
    )

    # Add standalone page URL to each normal post (use PRIMARY slug)
    for p in posts:
        if p.get("category") == "说说":
            continue
        primary = slug_primary(str(p["file"]))
        p["url"] = f"/p/{primary}/"

    OUTPUT_POSTS_JSON.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    # Generate standalone pages + legacy redirects + sitemap
    url_nodes: List[str] = []
    for p in posts:
        if p.get("category") == "说说":
            continue

        filename = str(p["file"])
        primary = slug_primary(filename)
        legacy = slug_legacy_encoded(filename)

        canonical_path = f"/p/{primary}/"
        out_html = PAGES_DIR / primary / "index.html"

        # 1) Real page at primary URL
        build_post_page(
            site_url=site_url,
            post=p,
            md_path=POSTS_DIR / filename,
            out_path=out_html,
            canonical_path=canonical_path,
        )


        # sitemap only includes PRIMARY (canonical) URL
        lastmod = str(p.get("date") or "")
        loc = _xml_escape(site_url + canonical_path)
        url_nodes.append(f"<url><loc>{loc}</loc><lastmod>{_xml_escape(lastmod)}</lastmod></url>")

    today = dt.date.today().isoformat()
    sitemap = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
        "<urlset xmlns=\"http://www.sitemaps.org/schemas/sitemap/0.9\">\n"
        f"  <url><loc>{_xml_escape(site_url + '/')}</loc><lastmod>{_xml_escape(today)}</lastmod></url>\n"
        + "\n".join(["  " + n for n in url_nodes])
        + "\n</urlset>\n"
    )
    OUTPUT_SITEMAP.write_text(sitemap, encoding="utf-8")

    print(f"Generated {OUTPUT_POSTS_JSON} ({len(posts)} posts)")
    print(f"Generated {OUTPUT_SITEMAP} ({len(url_nodes)} urls)")
    print(f"Generated pages under {PAGES_DIR}/")


if __name__ == "__main__":
    main()
