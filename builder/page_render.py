from __future__ import annotations

import json
import re

from .common import canonical_url, esc, render_social, site


def json_for_html_script(value):
    return (
        json.dumps(value, ensure_ascii=False, separators=(",", ":"))
        .replace("&", r"\u0026")
        .replace("<", r"\u003c")
        .replace(">", r"\u003e")
        .replace("\u2028", r"\u2028")
        .replace("\u2029", r"\u2029")
    )


def apply_tpl(template, cfg, *, page_title, meta_desc, extra_head, page_type, asset_version):
    site_cfg = site(cfg)
    result = template
    replacements = {
        "__PAGE_TITLE__": esc(page_title),
        "__META_DESC__": esc(meta_desc, True),
        "__EXTRA_HEAD__": extra_head,
        "__FAVICON_URL__": esc(site_cfg.get("favicon", ""), True),
        "__AVATAR_URL__": esc(site_cfg.get("avatar", ""), True),
        "__SITE_TITLE__": esc(site_cfg.get("title", "")),
        "__INTRO_TEXT__": esc(site_cfg.get("intro", "")),
        "__STATUS_URL__": esc(site_cfg.get("statusUrl", ""), True),
        "__SOCIAL_LINKS_HTML__": render_social(cfg),
        "__FOOTER_YEAR__": esc(site_cfg.get("footerYear", "")),
        "__POWERED_BY__": esc(site_cfg.get("poweredBy", "")),
        "__PAGE_TYPE__": esc(page_type),
        "__ASSET_VERSION__": esc(asset_version, True),
    }
    for key, value in replacements.items():
        result = result.replace(key, value)
    return result


def show_view(html, view_id):
    html = html.replace('<div id="home-view">', '<div id="home-view" class="hidden">', 1)
    tag = "article-view" if view_id == "article-view" else view_id
    return html.replace(f'<div id="{tag}" class="hidden">', f'<div id="{tag}">', 1)


def inject_div(html, div_id, inner):
    match = re.search(rf'(<div\s+[^>]*id="{re.escape(div_id)}"[^>]*>)([\s\S]*?)(</div>)', html)
    return html[: match.start()] + match.group(1) + inner + match.group(3) + html[match.end() :] if match else html


def replace_article(html, inner):
    return re.sub(
        r'<article id="article-content" class="markdown-body">[\s\S]*?</article>',
        f'<article id="article-content" class="markdown-body">{inner}</article>',
        html,
        count=1,
    )


def write_html(path, html, total_posts=None, total_words=None):
    if total_posts is not None and total_words is not None:
        html = html.replace('<span id="total-posts">0</span>', f'<span id="total-posts">{total_posts}</span>')
        html = html.replace('<span id="total-words">0</span>', f'<span id="total-words">{total_words}</span>')
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(html, encoding="utf-8")


def render_page(template, cfg, *, page_title, meta_desc, page_type, canonical_path, og_type="website", show_view_id=None, keywords="", ld=None):
    canonical = canonical_url(cfg, canonical_path)
    head = [
        f'<link rel="canonical" href="{esc(canonical, True)}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{esc(page_title, True)}">',
        f'<meta property="og:description" content="{esc(meta_desc, True)}">',
        f'<meta property="og:url" content="{esc(canonical, True)}">',
    ]
    if keywords:
        head.append(f'<meta name="keywords" content="{esc(keywords, True)}">')
    if ld is not None:
        head.append(f'<script type="application/ld+json">{json_for_html_script(ld)}</script>')
    html = apply_tpl(
        template,
        cfg,
        page_title=page_title,
        meta_desc=meta_desc,
        extra_head="\n".join(head) + "\n",
        page_type=page_type,
        asset_version=cfg.get("_asset_version", "1"),
    )
    return show_view(html, show_view_id) if show_view_id else html
