from __future__ import annotations

import re

from .common import POSTS_DIR, STANDALONE, as_int, count_words, normalize_date, split_fm
from .markdown_render import md_to_plain


def parse_post(path):
    raw = path.read_text(encoding="utf-8")
    front_matter, body = split_fm(raw)
    title = str(front_matter.get("title", path.stem)).strip() or path.stem
    date = normalize_date(front_matter.get("date", ""), path.stem)
    category = str(front_matter.get("category", "文章")).strip() or "文章"
    tags = front_matter.get("tags", []) if isinstance(front_matter.get("tags", []), list) else []
    summary = str(front_matter.get("summary", "") or "").strip()
    if not summary and category != "说说":
        summary = md_to_plain(body)[:160]
    return {
        "file": path.name,
        "title": title,
        "date": date,
        "slug": str(front_matter.get("slug", "") or "").strip(),
        "category": category,
        "top": as_int(front_matter.get("top")),
        "tags": tags,
        "summary": summary,
        "content": body.strip() if category == "说说" else "",
        "word_count": count_words(body),
        "_raw_body": body,
    }


def load_posts():
    return [
        parse_post(md)
        for md in sorted(POSTS_DIR.iterdir())
        if md.suffix.lower() == ".md" and md.name.lower() not in STANDALONE
    ]


def assign_post_urls(posts, persisted=None):
    persisted = persisted or {}
    used = {}
    for post in posts:
        file_name = post.get("file", "")
        front_matter_slug = str(post.get("slug") or "").strip()
        persisted_slug = str(persisted.get(file_name, "") or "").strip()
        if front_matter_slug and persisted_slug and front_matter_slug != persisted_slug:
            raise ValueError(
                f"{file_name}: front matter slug {front_matter_slug!r} conflicts with persisted slug {persisted_slug!r}"
            )
        slug = persisted_slug or front_matter_slug
        if not slug:
            raise ValueError(f"{post.get('file', 'unknown post')}: missing permanent slug")
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", slug):
            raise ValueError(f"{post.get('file', 'unknown post')}: invalid slug {slug!r}")
        if slug in used:
            raise ValueError(f"duplicate slug {slug!r}: {used[slug]} and {post.get('file', 'unknown post')}")
        used[slug] = post.get("file", "unknown post")
        post["slug"] = slug
        post["url"] = f"/p/{post['slug']}/"
