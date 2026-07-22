from __future__ import annotations

import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from builder import common
from builder.content import assign_post_urls, load_posts
from builder.feed import build_robots, build_sitemap
from builder.markdown_render import md_to_html
from builder.page_render import render_page
from builder.site_pages import build_404, build_home, build_post, build_status_block


class BuilderTests(unittest.TestCase):
    def test_count_words_strips_ansi_and_tabs_markup(self):
        text = (
            "你好 world\n"
            "```ansi\n\x1b[31mERROR\x1b[0m\b!\n```\n"
            ":::: tabs\n::: tab-item One\n内容\n:::\n::::\n"
        )
        self.assertEqual(common.count_words(text), 5)

    def test_assign_post_urls_creates_unique_slugs_per_date(self):
        posts = [
            {"date": "2026-02-01", "file": "b.md", "slug": "20260201-01"},
            {"date": "2026-02-01", "file": "a.md", "slug": "20260201-02"},
            {"date": "2026-01-31", "file": "c.md", "slug": "20260131-01"},
        ]
        assign_post_urls(posts)
        urls = {post["file"]: post["url"] for post in posts}
        self.assertEqual(urls["b.md"], "/p/20260201-01/")
        self.assertEqual(urls["a.md"], "/p/20260201-02/")
        self.assertEqual(urls["c.md"], "/p/20260131-01/")

    def test_persisted_slug_does_not_move_when_same_day_post_is_added(self):
        posts = [
            {"date": "2026-02-01", "file": "existing.md"},
            {"date": "2026-02-01", "file": "new-z.md", "slug": "20260201-02"},
        ]
        assign_post_urls(posts, {"existing.md": "20260201-01"})
        urls = {post["file"]: post["url"] for post in posts}
        self.assertEqual(urls["existing.md"], "/p/20260201-01/")
        self.assertEqual(urls["new-z.md"], "/p/20260201-02/")

    def test_invalid_or_duplicate_persisted_slugs_are_rejected(self):
        with self.assertRaises(ValueError):
            assign_post_urls([{"date": "2026-02-01", "file": "a.md"}], {"a.md": "../bad"})
        with self.assertRaises(ValueError):
            assign_post_urls(
                [{"date": "2026-02-01", "file": "a.md"}, {"date": "2026-02-01", "file": "b.md"}],
                {"a.md": "same", "b.md": "same"},
            )

    def test_front_matter_cannot_override_persisted_slug(self):
        posts = [{"date": "2026-02-01", "file": "a.md", "slug": "renamed"}]
        with self.assertRaises(ValueError):
            assign_post_urls(posts, {"a.md": "published"})
        assign_post_urls(posts, {"a.md": "renamed"})
        self.assertEqual(posts[0]["url"], "/p/renamed/")

    def test_slug_map_covers_every_current_post(self):
        posts = load_posts()
        slug_map = common.load_post_slugs()
        assign_post_urls(posts, slug_map)
        self.assertEqual({post["file"] for post in posts}, set(slug_map))
        self.assertEqual(len({post["slug"] for post in posts}), len(posts))

    def test_build_home_injects_prerender_content(self):
        template = """<!doctype html><title>__PAGE_TITLE__</title>__EXTRA_HEAD__<body data-page="__PAGE_TYPE__"><div id="home-view"><!--PRERENDER:START-->\n<!--PRERENDER:END--></div></body>"""
        cfg = {
            "_asset_version": "1",
            "site": {
                "title": "Test Blog",
                "tagline": "Static Test",
                "description": "desc",
                "url": "https://example.com",
            }
        }
        posts = [
            {"title": "文章 A", "date": "2026-06-01", "url": "/p/a/", "category": "文章", "top": 1000, "tags": ["Tag"]},
            {"title": "说说", "date": "2026-06-02", "url": "/p/b/", "category": "说说", "top": 0, "tags": []},
        ]
        html = build_home(template, cfg, posts)
        self.assertIn("文章 A", html)
        self.assertNotIn(">说说<", html)
        self.assertIn('data-page="home"', html)
        self.assertIn("置顶", html)

    def test_build_post_fills_meta_and_prev_next(self):
        template = """<!doctype html><title>__PAGE_TITLE__</title>__EXTRA_HEAD__
<body data-page="__PAGE_TYPE__"><div id="article-view" class="hidden">
<h1 id="article-title" class="article-title"></h1><div class="article-meta">
<span id="article-date"></span><span id="article-category"></span>
<span id="article-tags"></span><span id="article-words"></span>
<button id="article-like-btn"></button></div>
<article id="article-content" class="markdown-body"></article></div></body>"""
        cfg = {"_asset_version": "1", "site": {"title": "Blog", "description": "desc", "url": "https://example.com"}}
        posts = [
            {"title": "新文章", "date": "2026-06-02", "slug": "new", "url": "/p/new/", "category": "日常", "tags": ["Alpha", "Beta"], "summary": "摘要", "word_count": 12, "_raw_body": "你好 **世界**", "file": "new.md", "top": 0},
            {"title": "旧文章", "date": "2026-06-01", "slug": "old", "url": "/p/old/", "category": "日常", "tags": [], "summary": "旧", "word_count": 3, "_raw_body": "旧内容", "file": "old.md", "top": 0},
        ]
        html = build_post(template, cfg, posts[0], all_posts=posts)
        self.assertIn('id="article-date">2026-06-02</span>', html)
        self.assertIn('id="article-category">日常</span>', html)
        self.assertIn('id="article-tags">Alpha, Beta</span>', html)
        self.assertIn('id="article-words">12</span>', html)
        self.assertIn('data-id="/p/new/"', html)
        self.assertIn("旧文章", html)

    def test_prev_next_uses_chronology_instead_of_pinned_list_order(self):
        template = '<html><head>__EXTRA_HEAD__<title>__PAGE_TITLE__</title></head><body data-page="__PAGE_TYPE__"><div id="article-view" class="hidden"><h1 id="article-title" class="article-title"></h1><div class="article-meta"><span id="article-date"></span><span id="article-category"></span><span id="article-tags"></span><span id="article-words"></span><button id="article-like-btn"></button></div><article id="article-content" class="markdown-body"></article></div></body></html>'
        cfg = {"_asset_version": "1", "site": {"title": "Blog", "url": "https://example.com"}}
        posts = [
            {"title": "Pinned old", "date": "2026-01-01", "slug": "old", "url": "/p/old/", "file": "old.md", "top": 1000},
            {"title": "Newest", "date": "2026-01-03", "slug": "new", "url": "/p/new/", "file": "new.md", "top": 0},
            {"title": "Current", "date": "2026-01-02", "slug": "current", "url": "/p/current/", "file": "current.md", "top": 0},
        ]
        for post in posts:
            post.update(category="Daily", tags=[], summary="", word_count=1, _raw_body="body")
        html = build_post(template, cfg, posts[2], all_posts=posts)
        self.assertIn("Pinned old", html)
        self.assertIn("Newest", html)
        self.assertLess(html.index("Pinned old"), html.index("Newest"))

    def test_status_and_post_like_ids_use_the_same_url(self):
        cfg = {"_asset_version": "1", "site": {"title": "Blog", "url": "https://example.com", "avatar": "/avatar.jpg"}}
        post = {"title": "Status", "date": "2026-01-01", "slug": "status", "url": "/p/status/", "file": "status.md", "category": "说说", "tags": [], "summary": "", "word_count": 1, "_raw_body": "body", "top": 0}
        self.assertIn('data-id="/p/status/"', build_status_block(cfg, [post]))
        self.assertIn('data-id="/p/status/"', build_post(common.TEMPLATE_HTML, cfg, post))

    def test_markdown_images_are_lazy_and_async(self):
        html = md_to_html('![Alt](https://example.com/image.jpg)\n\n<img src="https://example.com/raw.jpg" alt="Raw">')
        self.assertEqual(html.count('loading="lazy"'), 2)
        self.assertEqual(html.count('decoding="async"'), 2)

    def test_404_uses_versioned_css_and_accessible_viewport(self):
        html = build_404({"_asset_version": "abc123", "site": {"title": "Blog", "description": "Missing"}})
        self.assertIn('/assets/app.css?v=abc123', html)
        self.assertIn('width=device-width,initial-scale=1.0', html)
        self.assertIn('<main', html)

    def test_build_sitemap_contains_core_pages_and_posts(self):
        cfg = {"site": {"url": "https://example.com"}}
        posts = [{"date": "2026-06-01", "file": "a.md", "url": "/p/a/"}]
        xml = build_sitemap(cfg, posts)
        self.assertIn("<loc>https://example.com/</loc>", xml)
        self.assertIn("<loc>https://example.com/archive/</loc>", xml)
        self.assertIn("<loc>https://example.com/p/a/</loc>", xml)

    def test_build_robots_uses_configured_site_url(self):
        robots = build_robots({"site": {"url": "https://preview.example.com/"}})
        self.assertIn("Sitemap: https://preview.example.com/sitemap.xml", robots)

    def test_asset_ver_tracks_nested_assets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets_dir = root / "assets"
            nested_dir = assets_dir / "css"
            src_dir = root / "src"
            nested_dir.mkdir(parents=True)
            src_dir.mkdir(parents=True)
            (assets_dir / "app.js").write_text("console.log('a')\n", encoding="utf-8")
            (assets_dir / "app.css").write_text('@import "./css/base.css";\n', encoding="utf-8")
            nested_asset = nested_dir / "base.css"
            nested_asset.write_text("body{color:#000}\n", encoding="utf-8")
            (src_dir / "index.template.html").write_text("<html></html>\n", encoding="utf-8")

            with mock.patch.object(common, "ASSETS_DIR", assets_dir), mock.patch.object(common, "ROOT", root):
                before = common.asset_ver()
                time.sleep(0.001)
                nested_asset.touch()
                touched = common.asset_ver()
                nested_asset.write_text("body{color:#111}\n", encoding="utf-8")
                after = common.asset_ver()

        self.assertEqual(before, touched)
        self.assertNotEqual(before, after)
        self.assertEqual(len(before), 16)
        self.assertTrue(all(char in "0123456789abcdef" for char in before))

    def test_sanitize_strips_script_and_event_handlers(self):
        dirty = '<p>ok</p><script>alert(1)</script><img src=x onerror=alert(1)>'
        clean = common.sanitize(dirty)
        self.assertIn("<p>ok</p>", clean)
        self.assertNotIn("script", clean.lower())
        self.assertNotIn("onerror", clean.lower())

    def test_json_ld_cannot_close_its_script_element(self):
        template = "<title>__PAGE_TITLE__</title>__EXTRA_HEAD__<body data-page=\"__PAGE_TYPE__\"></body>"
        cfg = {"_asset_version": "1", "site": {"url": "https://example.com"}}
        html = render_page(
            template,
            cfg,
            page_title="test",
            meta_desc="test",
            page_type="post",
            canonical_path="/p/test/",
            ld={"headline": "</script><script>window.pwned=1</script>"},
        )
        self.assertNotIn("</script><script>", html)
        self.assertIn("\\u003c/script", html)

    def test_tabs_ids_are_deterministic_and_scoped(self):
        source = ":::: tabs\n::: tab-item A\nOne\n:::\n::::"
        first = md_to_html(source, id_prefix="post-a")
        second = md_to_html(source, id_prefix="post-a")
        other = md_to_html(source, id_prefix="post-b")
        self.assertEqual(first, second)
        self.assertIn('data-tab-group="tabs-post-a-1"', first)
        self.assertIn('data-tab-group="tabs-post-b-1"', other)

    def test_dynamic_detail_has_server_rendered_metadata_and_canonical_like_id(self):
        cfg = {
            "_asset_version": "1",
            "site": {"title": "Test", "url": "https://example.com", "description": "desc"},
        }
        post = {
            "title": "动态",
            "date": "2026-07-22",
            "category": "说说",
            "tags": ["记录"],
            "word_count": 2,
            "url": "/p/20260722-01/",
            "slug": "20260722-01",
            "file": "status.md",
            "_raw_body": "正文",
        }
        html = build_post(common.TEMPLATE_HTML, cfg, post)
        self.assertIn('<span id="article-date">2026-07-22</span>', html)
        self.assertIn('<span id="article-category">说说</span>', html)
        self.assertIn('data-id="/p/20260722-01/"', html)

    def test_load_config_does_not_leak_environment_override(self):
        with mock.patch.dict(common.os.environ, {"SITE_URL": "https://preview.example.com"}, clear=True):
            self.assertEqual(common.load_config()["site"]["url"], "https://preview.example.com")
        with mock.patch.dict(common.os.environ, {}, clear=True):
            self.assertEqual(common.load_config()["site"]["url"], common.CONFIG_JSON["site"]["url"])


if __name__ == "__main__":
    unittest.main()
