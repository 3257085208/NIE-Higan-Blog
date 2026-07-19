from __future__ import annotations

import datetime as dt

from .common import POSTS_DIR, PRERENDER, as_int, canonical_url, count_words, esc, normalize_date, site, site_title, split_fm
from .markdown_render import md_to_html
from .page_render import inject_div, render_page, replace_article


def home_post_item(post):
    badge = '<span class="top-badge"><i class="fa-solid fa-fire"></i> 置顶</span>' if as_int(post.get("top")) >= 1000 else ""
    tags = "".join(f'<span class="tag-pill">#{esc(tag)}</span>' for tag in post.get("tags", []) if isinstance(post.get("tags"), list))
    tags_html = f'<div class="post-tags">{tags}</div>' if tags else ""
    return (
        f'<div class="post-item"><div class="post-date">{esc(post["date"])}</div>'
        f'<a href="{esc(post["url"])}" class="post-title-link">{esc(post["title"])}{badge}</a>{tags_html}</div>'
    )


def build_home(template, cfg, posts):
    site_cfg = site(cfg)
    title = site_title(cfg)
    tagline = str(site_cfg.get("tagline", "")).strip()
    page_title = f"{title} | {tagline}" if tagline else title
    meta_desc = str(site_cfg.get("description", "")) or f"{title} - A Geek's Blog"
    items = "\n".join(home_post_item(post) for post in [post for post in posts if post.get("category") != "说说"][:10])
    html = render_page(template, cfg, page_title=page_title, meta_desc=meta_desc, page_type="home", canonical_path="/")
    return html.replace(PRERENDER[0] + "\n" + PRERENDER[1], PRERENDER[0] + "\n" + items + "\n" + PRERENDER[1])




def _fill_span(html, span_id, value):
    empty = f'<span id="{span_id}"></span>'
    filled = f'<span id="{span_id}">{esc(value)}</span>'
    return html.replace(empty, filled, 1)


def _build_prev_next(posts, current):
    """Same DOM as assets/js/features/navigation.js renderPrevNext."""
    normal = [p for p in posts if p.get("category") != "说说"]
    try:
        idx = next(i for i, p in enumerate(normal) if p.get("url") == current.get("url"))
    except StopIteration:
        return ""
    newer = normal[idx - 1] if idx > 0 else None
    older = normal[idx + 1] if idx < len(normal) - 1 else None
    if not newer and not older:
        return ""

    def item(post, klass, hint):
        if not post:
            return '<div class="nav-item empty"></div>'
        return (
            f'<a href="{esc(post.get("url") or "/", True)}" class="nav-item {klass}">'
            f'<div class="nav-hint">{hint}</div>'
            f'<div class="nav-title">{esc(post.get("title") or "")}</div></a>'
        )

    return (
        '<div class="post-navigation">'
        + item(older, "nav-prev", '<i class="fa-solid fa-arrow-left"></i> 上一篇')
        + item(newer, "nav-next", '下一篇 <i class="fa-solid fa-arrow-right"></i>')
        + "</div>"
    )


def build_post(template, cfg, post, page_type="post", all_posts=None):
    site_cfg = site(cfg)
    title = str(site_cfg.get("title", "聶.NET"))
    page_title = f"{post['title']} | {title}"
    meta_desc = str(post.get("summary", "")).strip() or str(site_cfg.get("description", ""))
    keywords = ",".join(str(tag) for tag in post.get("tags", []) if isinstance(post.get("tags"), list))
    ld = {
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post["title"],
        "datePublished": post.get("date"),
        "dateModified": post.get("date"),
        "mainEntityOfPage": canonical_url(cfg, str(post.get("url", ""))),
        "author": {"@type": "Person", "name": site_cfg.get("statusName") or title},
        "publisher": {"@type": "Organization", "name": title},
        "description": meta_desc,
    }
    html = render_page(
        template,
        cfg,
        page_title=page_title,
        meta_desc=meta_desc,
        page_type=page_type,
        canonical_path=str(post.get("url", "")),
        og_type="article",
        show_view_id="article-view",
        keywords=keywords,
        ld=ld,
    )
    html = html.replace(
        '<h1 id="article-title" class="article-title"></h1>',
        f'<h1 id="article-title" class="article-title">{esc(post["title"])}</h1>',
        1,
    )
    html = _fill_span(html, "article-date", post.get("date") or "未知")
    html = _fill_span(html, "article-category", post.get("category") or "默认")
    tags = post.get("tags", []) if isinstance(post.get("tags"), list) else []
    if tags:
        html = _fill_span(html, "article-tags", ", ".join(str(t) for t in tags))
    html = _fill_span(html, "article-words", str(post.get("word_count") or 0))
    like_id = str(post.get("url") or "") or str(post.get("file") or "")
    html = html.replace(
        'class="like-btn" id="article-like-btn" style="cursor:pointer"',
        f'class="like-btn" id="article-like-btn" data-id="{esc(like_id, True)}" style="cursor:pointer"',
        1,
    )
    body_html = md_to_html(post.get("_raw_body", ""))
    html = html.replace(
        '<article id="article-content" class="markdown-body"></article>',
        f'<article id="article-content" class="markdown-body">{body_html}</article>',
        1,
    )
    if all_posts is not None and page_type == "post":
        nav = _build_prev_next(all_posts, post)
        if nav:
            marker = f'<article id="article-content" class="markdown-body">{body_html}</article>'
            html = html.replace(marker, marker + nav, 1)
    return html


def build_list_block(posts, mode="archive"):
    items = [post for post in posts if post.get("category") != "说说"]
    items.sort(key=lambda item: (item.get("date", ""), item.get("file", "")), reverse=True)
    groups = {}
    for post in items:
        date = str(post.get("date", ""))
        key = date[:7] if len(date) >= 7 and mode == "archive" else str(post.get("category", "默认分类"))
        groups.setdefault(key, []).append(post)
    parts = []
    for key in sorted(groups.keys(), reverse=(mode == "archive")):
        label = f"{key[:4]}年 {key[5:7]}月" if len(key) == 7 and mode == "archive" else key
        font_size = "font-size:1.5rem" if mode == "category" else ""
        parts.append(f'<div class="archive-year" style="{font_size}">{esc(label)}</div>')
        for post in groups[key]:
            date_text = str(post.get("date", ""))[8:10] if len(str(post.get("date", ""))) >= 10 and mode == "archive" else str(post.get("date", ""))
            suffix = "日" if mode == "archive" else ""
            parts.append(
                f'<div class="archive-item"><span class="archive-date">{esc(date_text) + suffix}</span>'
                f'<a href="{esc(post.get("url", "#"), True)}" class="archive-link">{esc(post.get("title", ""))}</a></div>'
            )
    return "\n".join(parts) or f'<div style="color:#999">暂无{"文章" if mode == "archive" else "分类"}...</div>'


def build_status_block(cfg, posts):
    site_cfg = site(cfg)
    status_posts = [post for post in posts if post.get("category") == "说说"]
    if not status_posts:
        return '<div style="color:#999">暂无动态...</div>'
    parts = []
    for post in status_posts:
        file_name = str(post.get("file", ""))
        parts.append(
            "\n".join(
                [
                    '<div class="status-item">',
                    f'  <img src="{esc(site_cfg.get("avatar", ""), True)}" class="status-avatar">',
                    '  <div class="status-main"><div class="status-header">',
                    f'      <span class="status-name">{esc(site_cfg.get("statusName") or site_cfg.get("title", ""))}</span>',
                    f'      <span class="status-time">{esc(post.get("date", ""))}</span>',
                    '    </div>',
                    f'    <div class="status-card markdown-body">{md_to_html(post.get("_raw_body", ""))}</div>',
                    '    <div class="status-actions">',
                    f'      <span class="status-btn like-btn" data-id="{esc(file_name)}"><i class="fa-regular fa-heart"></i> <span class="like-count">0</span></span>',
                    f'      <a href="{esc(post.get("url", ""), True)}" class="status-btn" style="text-decoration:none;"><i class="fa-regular fa-comment-dots"></i> 评论</a>',
                    '    </div></div></div>',
                ]
            )
        )
    return "\n".join(parts)


def build_view_page(template, cfg, *, page_type, page_title, meta_desc, canonical_path, show_view_id, archive_title=None, archive_html=None, status_html=None):
    html = render_page(template, cfg, page_title=page_title, meta_desc=meta_desc, page_type=page_type, canonical_path=canonical_path, show_view_id=show_view_id)
    if show_view_id == "archive-view" and archive_html is not None:
        if archive_title:
            html = html.replace(
                '<h2 id="archive-title" class="section-header" style="margin-top:0">归档</h2>',
                f'<h2 id="archive-title" class="section-header" style="margin-top:0">{esc(archive_title)}</h2>',
                1,
            )
        html = inject_div(html, "archive-content", archive_html)
    if show_view_id == "status-view" and status_html is not None:
        html = inject_div(html, "status-content", status_html)
    return html


def build_standalone(template, cfg, filename, default_title):
    markdown_path = POSTS_DIR / filename
    raw = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    front_matter, body = split_fm(raw)
    title = str(front_matter.get("title") or default_title).strip() or default_title
    date = dt.date.today().isoformat()
    if front_matter.get("date", ""):
        date = normalize_date(front_matter.get("date", ""), dt.date.today().isoformat())
    page_name = filename.rsplit(".", 1)[0]
    pseudo_post = {
        "file": filename,
        "title": title,
        "date": date,
        "category": default_title,
        "top": 0,
        "tags": front_matter.get("tags", []) if isinstance(front_matter.get("tags", []), list) else [],
        "summary": str(front_matter.get("summary") or default_title),
        "content": "",
        "word_count": count_words(body),
        "_raw_body": body,
        "url": f"/{page_name}/",
    }
    html = build_post(template, cfg, pseudo_post, page_type=page_name)
    return html.replace('<div class="article-meta">', '<div class="article-meta" style="display:none;">')


def build_friends(template, cfg):
    markdown_path = POSTS_DIR / "friends.md"
    raw = markdown_path.read_text(encoding="utf-8") if markdown_path.exists() else ""
    front_matter, body = split_fm(raw)
    html = build_standalone(template, cfg, "friends.md", "友情链接").replace('<div id="waline"></div>', "")
    friends = front_matter.get("friends", []) if isinstance(front_matter.get("friends", []), list) else []
    cards = ['<div class="friends-grid">']
    for friend in friends:
        if not isinstance(friend, dict):
            continue
        cards.append(
            f'<a href="{esc(friend.get("url", "#"), True)}" target="_blank" rel="noopener noreferrer" class="friend-card">'
            f'<img src="{esc(friend.get("avatar", ""), True)}" class="friend-avatar" alt="{esc(friend.get("name", "未命名"))}">'
            f'<div class="friend-info"><div class="friend-name">{esc(friend.get("name", "未命名"))}</div>'
            f'<div class="friend-desc">{esc(friend.get("bio", ""))}</div></div></a>'
        )
    cards.append("</div>")
    return replace_article(html, md_to_html(body) + "".join(cards))


def build_404(cfg):
    site_cfg = site(cfg)
    title = esc(site_cfg.get("title", "聶.NET"))
    desc = esc(site_cfg.get("description", ""))
    favicon = esc(site_cfg.get("favicon", ""))
    return (
        f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=1.0,user-scalable=no"><title>404 - {title}</title><link rel="shortcut icon" href="{favicon}"><link rel="stylesheet" href="/assets/app.css"></head><body><div style="text-align:center;padding:100px 20px;"><h1 style="font-size:8rem;color:var(--accent);">404</h1><h2>页面走丢了</h2><p>{desc}</p><a href="/" style="display:inline-block;margin-top:30px;padding:12px 28px;background:var(--tag-bg);border-radius:12px;font-weight:800;text-decoration:none;">返回首页</a></div></body></html>'
    )

