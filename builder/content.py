from __future__ import annotations

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


def assign_post_urls(posts):
    counter = {}
    for post in sorted(posts, key=lambda item: (item["date"], item["file"]), reverse=True):
        date = post["date"]
        counter[date] = counter.get(date, 0) + 1
        post["slug"] = f"{date.replace('-', '')}-{counter[date]:02d}"
        post["url"] = f"/p/{post['slug']}/"

