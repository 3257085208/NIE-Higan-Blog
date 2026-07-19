from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from builder import common
from builder.content import assign_post_urls
from builder.feed import build_sitemap
from builder.site_pages import build_home, build_post


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
            {"date": "2026-02-01", "file": "b.md"},
            {"date": "2026-02-01", "file": "a.md"},
            {"date": "2026-01-31", "file": "c.md"},
        ]
        assign_post_urls(posts)
        urls = {post["file"]: post["url"] for post in posts}
        self.assertEqual(urls["b.md"], "/p/20260201-01/")
        self.assertEqual(urls["a.md"], "/p/20260201-02/")
        self.assertEqual(urls["c.md"], "/p/20260131-01/")

    def test_build_home_injects_prerender_content(self):
        template = """<!doctype html><title>__PAGE_TITLE__</title>__EXTRA_HEAD__<body data-page="__PAGE_TYPE__"><div id="home-view"><!--PRERENDER:START-->\n<!--PRERENDER:END--></div></body>"""
        cfg = {
            "_asset_version": "1",
            "site": {
                "title": "Higan",
                "tagline": "is NKX !",
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
<body data-page="__PAGE_TYPE__">
<div id="article-view" class="hidden">
<h1 id="article-title" class="article-title"></h1>
<div class="article-meta">
<span><i class="fa-regular fa-calendar"></i> <span id="article-date"></span></span>
<span><i class="fa-regular fa-folder"></i> <span id="article-category"></span></span>
<span><i class="fa-regular fa-hashtag"></i> <span id="article-tags"></span></span>
<span><i class="fa-regular fa-file-word"></i> <span id="article-words"></span> 字</span>
<span class="like-btn" id="article-like-btn" style="cursor:pointer"><i class="fa-regular fa-heart"></i> <span class="like-count">0</span> 赞</span>
</div>
<article id="article-content" class="markdown-body"></article>
</div>
</body>"""
        cfg = {
            "_asset_version": "1",
            "site": {
                "title": "Higan",
                "description": "desc",
                "url": "https://example.com",
                "statusName": "NKX",
            },
        }
        posts = [
            {
                "title": "新文章",
                "date": "2026-06-02",
                "url": "/p/new/",
                "category": "日常",
                "tags": ["Alpha", "Beta"],
                "summary": "摘要",
                "word_count": 12,
                "_raw_body": "你好 **世界**",
                "file": "new.md",
                "top": 0,
            },
            {
                "title": "旧文章",
                "date": "2026-06-01",
                "url": "/p/old/",
                "category": "日常",
                "tags": [],
                "summary": "旧",
                "word_count": 3,
                "_raw_body": "旧内容",
                "file": "old.md",
                "top": 0,
            },
        ]
        html = build_post(template, cfg, posts[0], all_posts=posts)
        self.assertIn('id="article-date">2026-06-02</span>', html)
        self.assertIn('id="article-category">日常</span>', html)
        self.assertIn('id="article-tags">Alpha, Beta</span>', html)
        self.assertIn('id="article-words">12</span>', html)
        self.assertIn('data-id="/p/new/"', html)
        self.assertIn("你好", html)
        self.assertIn("post-navigation", html)
        self.assertIn("旧文章", html)
        self.assertIn("/p/old/", html)

    def test_build_sitemap_contains_core_pages_and_posts(self):
        cfg = {"site": {"url": "https://example.com"}}
        posts = [{"date": "2026-06-01", "file": "a.md", "url": "/p/a/"}]
        xml = build_sitemap(cfg, posts)
        self.assertIn("<loc>https://example.com/</loc>", xml)
        self.assertIn("<loc>https://example.com/archive/</loc>", xml)
        self.assertIn("<loc>https://example.com/p/a/</loc>", xml)

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
                nested_asset.write_text("body{color:#111}\n", encoding="utf-8")
                after = common.asset_ver()

        self.assertNotEqual(before, after)
        self.assertEqual(len(before), 12)
        self.assertTrue(all(c in "0123456789abcdef" for c in before))

    def test_sanitize_strips_script(self):
        dirty = '<p>ok</p><script>alert(1)</script><img src=x onerror=alert(1)>'
        clean = common.sanitize(dirty)
        self.assertIn("<p>ok</p>", clean)
        self.assertNotIn("script", clean.lower())
        self.assertNotIn("onerror", clean.lower())


if __name__ == "__main__":
    unittest.main()
