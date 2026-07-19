from __future__ import annotations

import datetime as dt

from .common import esc, rfc822, site
from .markdown_render import md_to_html


def build_rss(cfg, posts):
    site_cfg = site(cfg)
    title = str(site_cfg.get("title", "")) or "Blog"
    desc = str(site_cfg.get("description", "")) or title
    site_url = str(site_cfg.get("url", "")).rstrip("/")
    ns_atom = "http://www.w3.org/2005/Atom"
    ns_content = "http://purl.org/rss/1.0/modules/content/"
    normal_posts = sorted(
        [post for post in posts if post.get("category") != "说说"],
        key=lambda item: (item.get("date", ""), item.get("file", "")),
        reverse=True,
    )[:30]
    items = []
    for post in normal_posts:
        link = site_url + str(post.get("url", ""))
        raw = md_to_html(str(post.get("_raw_body", ""))).replace("]]>", "]]]]><![CDATA[>")
        categories = "".join(
            f"<category>{esc(category)}</category>"
            for category in ([post.get("category", "")] + (post.get("tags", []) if isinstance(post.get("tags"), list) else []))
            if category
        )
        items.append(
            f"<item><title>{esc(post.get('title', ''))}</title><link>{esc(link)}</link>"
            f'<guid isPermaLink="true">{esc(link)}</guid><pubDate>{rfc822(post.get("date", ""))}</pubDate>'
            f"<description><![CDATA[{str(post.get('summary', '')).replace(']]>',']]]]><![CDATA[>')}]]></description>"
            f"<content:encoded><![CDATA[{raw}]]></content:encoded>{categories}</item>"
        )
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="{ns_atom}" xmlns:content="{ns_content}">\n'
        f'<channel><title>{esc(title)}</title><link>{esc(site_url + "/")}</link><description>{esc(desc)}</description>'
        f'<language>zh-CN</language><atom:link href="{esc(site_url + "/rss.xml")}" rel="self" type="application/rss+xml" />'
        f'<lastBuildDate>{dt.datetime.now(dt.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S %z")}</lastBuildDate>'
        + "".join(items)
        + "\n</channel></rss>\n"
    )


def build_sitemap(cfg, posts):
    site_url = str(site(cfg).get("url", "")).rstrip("/")
    today = dt.date.today().isoformat()

    def node(path, lastmod):
        return f"<url><loc>{esc(site_url.rstrip('/') + path)}</loc><lastmod>{esc(lastmod)}</lastmod></url>"

    urls = [node("/", today)] + [node(path, today) for path in ("/archive/", "/category/", "/status/", "/guestbook/", "/changelog/", "/friends/")]
    for post in sorted(posts, key=lambda item: (item.get("date", ""), item.get("file", "")), reverse=True):
        url = str(post.get("url", ""))
        if url:
            urls.append(node(url, str(post.get("date") or today)))
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls)
        + "\n</urlset>\n"
    )

