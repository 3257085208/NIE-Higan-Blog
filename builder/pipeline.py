from __future__ import annotations

import json
import shutil

from .common import ASSETS_DIR, DIST, PUBLIC_DIR, TEMPLATE_HTML, asset_ver, load_config, site_title
from .content import assign_post_urls, load_posts
from .feed import build_rss, build_sitemap
from .page_render import write_html
from .site_pages import (
    build_404,
    build_friends,
    build_home,
    build_list_block,
    build_post,
    build_standalone,
    build_status_block,
    build_view_page,
)


def reset_dirs(*names):
    for name in names:
        path = DIST / name
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)


def copy_public_assets():
    if PUBLIC_DIR.exists():
        for item in PUBLIC_DIR.rglob("*"):
            if item.is_file():
                output = DIST / item.relative_to(PUBLIC_DIR)
                output.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, output)
    if ASSETS_DIR.exists():
        shutil.copytree(ASSETS_DIR, DIST / "assets", dirs_exist_ok=True)


def main():
    cfg = load_config()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True, exist_ok=True)
    copy_public_assets()
    cfg["_asset_version"] = asset_ver()
    (DIST / "config.js").write_text("window.SITE_CONFIG = " + json.dumps(cfg, ensure_ascii=False, indent=2) + ";\n", encoding="utf-8")

    posts = load_posts()
    assign_post_urls(posts)
    posts.sort(key=lambda post: (post.get("top", 0), post["date"], post["file"]), reverse=True)
    total_posts = len([post for post in posts if post.get("category") != "说说"])
    total_words = sum(int(post.get("word_count") or 0) for post in posts if post.get("category") != "说说")

    (DIST / "posts.json").write_text(
        json.dumps([{key: value for key, value in post.items() if key != "_raw_body"} for post in posts], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    reset_dirs("p", "archive", "category", "status", "guestbook", "changelog", "friends")

    for post in posts:
        write_html(DIST / "p" / post["slug"] / "index.html", build_post(TEMPLATE_HTML, cfg, post, all_posts=posts), total_posts, total_words)

    title = site_title(cfg)
    pages = [
        (
            DIST / "archive" / "index.html",
            build_view_page(
                TEMPLATE_HTML,
                cfg,
                page_type="archive",
                page_title=f"归档 - {title}",
                meta_desc=f"{title} 的归档",
                canonical_path="/archive/",
                show_view_id="archive-view",
                archive_title="归档",
                archive_html=build_list_block(posts, "archive"),
            ),
        ),
        (
            DIST / "category" / "index.html",
            build_view_page(
                TEMPLATE_HTML,
                cfg,
                page_type="category",
                page_title=f"分类 - {title}",
                meta_desc=f"{title} 的分类",
                canonical_path="/category/",
                show_view_id="archive-view",
                archive_title="分类",
                archive_html=build_list_block(posts, "category"),
            ),
        ),
        (
            DIST / "status" / "index.html",
            build_view_page(
                TEMPLATE_HTML,
                cfg,
                page_type="status",
                page_title=f"我的动态 - {title}",
                meta_desc=f"{title} 的动态",
                canonical_path="/status/",
                show_view_id="status-view",
                status_html=build_status_block(cfg, posts),
            ),
        ),
        (DIST / "guestbook" / "index.html", build_standalone(TEMPLATE_HTML, cfg, "guestbook.md", "留言板")),
        (DIST / "changelog" / "index.html", build_standalone(TEMPLATE_HTML, cfg, "changelog.md", "更新日志").replace('<div id="waline"></div>', "")),
        (DIST / "friends" / "index.html", build_friends(TEMPLATE_HTML, cfg)),
        (DIST / "index.html", build_home(TEMPLATE_HTML, cfg, posts)),
    ]
    for path, html in pages:
        write_html(path, html, total_posts, total_words)

    (DIST / "rss.xml").write_text(build_rss(cfg, posts), encoding="utf-8")
    (DIST / "sitemap.xml").write_text(build_sitemap(cfg, posts), encoding="utf-8")
    (DIST / "404.html").write_text(build_404(cfg), encoding="utf-8")
