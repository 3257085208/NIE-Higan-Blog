from __future__ import annotations

import copy
import datetime as dt
import hashlib
import html
import json
import os
import re
from email.utils import format_datetime
from pathlib import Path

import bleach
import yaml
from bleach.css_sanitizer import CSSSanitizer
from bleach.html5lib_shim import Filter

ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
POSTS_DIR = ROOT / "posts"
PUBLIC_DIR = ROOT / "public"
ASSETS_DIR = ROOT / "assets"
TEMPLATE_HTML = (ROOT / "src" / "index.template.html").read_text(encoding="utf-8")
CONFIG_JSON = json.loads((ROOT / "site.config.json").read_text(encoding="utf-8"))
POST_SLUGS_JSON = ROOT / "post-slugs.json"
STANDALONE = ("guestbook.md", "changelog.md", "friends.md")
PRERENDER = "<!--PRERENDER:START-->", "<!--PRERENDER:END-->"

ALLOWED_TAGS = set(bleach.sanitizer.ALLOWED_TAGS) | {
    "article","br","button","code","col","colgroup","del","details","div","h1","h2","h3","h4","h5","h6",
    "hr","i","img","input","li","nav","ol","p","pre","section","span","strong","summary","table","tbody",
    "td","tfoot","th","thead","tr","ul",
}
ALLOWED_ATTRS = {
    "alt","checked","class","colspan","decoding","dir","disabled","height","hidden","href","id","loading","name","rel",
    "role","rowspan","src","style","tabindex","target","title","type","width"
}
CSS_SAN = CSSSanitizer(allowed_css_properties={
    "align-items","background","background-color","border","border-radius","color","display","font-weight","gap",
    "justify-content","line-height","margin","margin-bottom","margin-left","margin-right","margin-top","max-height",
    "max-width","object-fit","object-position","opacity","overflow","overflow-x","overflow-y","padding","padding-left",
    "text-align","text-decoration","vertical-align","width","white-space","word-break"
})

ESC_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


class ImageLoadingFilter(Filter):
    def __iter__(self):
        for token in super().__iter__():
            if token.get("type") in {"StartTag", "EmptyTag"} and token.get("name") == "img":
                token["data"][(None, "loading")] = "lazy"
                token["data"][(None, "decoding")] = "async"
            yield token


def esc(value, quote=False):
    return html.escape(str(value), quote=quote)


def as_int(value, default=0):
    try:
        return int(value or default)
    except (TypeError, ValueError):
        return default


def strip_bs(text):
    out = []
    for ch in text:
        if ch == "\b":
            if out:
                out.pop()
        else:
            out.append(ch)
    return "".join(out)


def strip_ansi(text):
    return ESC_RE.sub("", strip_bs(text))


def count_words(text):
    text = re.sub(r"```[\s\S]*?```", "", text)
    text = strip_ansi(text)
    for pattern in (":::: tabs", r"^::: tab-item .*?$", r"^:::$", r"^::::$"):
        text = re.sub(pattern, " ", text, flags=re.MULTILINE)
    return len(re.findall(r"[\u4e00-\u9fff]", text)) + len(re.findall(r"[A-Za-z0-9_]+", text))


def normalize_date(value, fallback):
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    if isinstance(value, dt.date):
        return value.isoformat()
    if isinstance(value, str):
        match = re.search(r"(\d{4}-\d{2}-\d{2})", value.strip())
        if match:
            return match.group(1)
    fallback_match = re.match(r"^(\d{4}-\d{2}-\d{2})", fallback)
    return fallback_match.group(1) if fallback_match else dt.date.today().isoformat()


def split_fm(text):
    lines = text.splitlines(keepends=True)
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                front_matter = yaml.safe_load("".join(lines[1:i])) or {}
                return (front_matter if isinstance(front_matter, dict) else {}), "".join(lines[i + 1:]).lstrip("\n")
    return {}, text


def sanitize(text):
    cleaner = bleach.Cleaner(
        tags=ALLOWED_TAGS,
        attributes=lambda tag, name, value: name in ALLOWED_ATTRS or name.startswith(("aria-", "data-")),
        protocols=["http", "https", "mailto", "tel", "tencent"],
        css_sanitizer=CSS_SAN,
        strip=True,
        filters=[ImageLoadingFilter],
    )
    return cleaner.clean(text)


def rfc822(date_string):
    try:
        date_obj = dt.date.fromisoformat(str(date_string))
    except (ValueError, TypeError):
        date_obj = dt.date.today()
    return format_datetime(dt.datetime(date_obj.year, date_obj.month, date_obj.day, tzinfo=dt.timezone.utc))


def load_config():
    cfg = copy.deepcopy(CONFIG_JSON) if isinstance(CONFIG_JSON, dict) else {}
    site_cfg = cfg.setdefault("site", {})
    if not isinstance(site_cfg, dict):
        cfg["site"] = site_cfg = {}
    env_url = os.environ.get("SITE_URL")
    if env_url:
        site_cfg["url"] = env_url.rstrip("/")
    return cfg


def load_post_slugs():
    if not POST_SLUGS_JSON.exists():
        return {}
    data = json.loads(POST_SLUGS_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in data.items()):
        raise ValueError("post-slugs.json must be an object mapping filenames to slugs")
    return data


def asset_ver():
    digest = hashlib.sha256()
    tracked_files = sorted(path for path in ASSETS_DIR.rglob("*") if path.is_file())
    tracked_files.extend((ROOT / "src" / "index.template.html", ROOT / "builder" / "pipeline.py"))
    for file_path in tracked_files:
        try:
            digest.update(file_path.relative_to(ROOT).as_posix().encode("utf-8"))
            digest.update(b"\0")
            digest.update(file_path.read_bytes())
            digest.update(b"\0")
        except OSError:
            pass
    return digest.hexdigest()[:16]


def render_social(cfg):
    items = cfg.get("social", []) if isinstance(cfg.get("social", []), list) else []
    parts = ['<span class="social-label">与我联系</span>']
    for item in items:
        if not isinstance(item, dict):
            continue
        href = str(item.get("href", "")).strip()
        title = str(item.get("title", "")).strip() or "Link"
        icon = str(item.get("iconClass", "")).strip()
        if not href or not icon:
            continue
        parts.append(
            f'<a href="{esc(href, True)}" class="social-icon-link" title="{esc(title, True)}"><i class="{esc(icon, True)}"></i></a>'
        )
    return "\n            ".join(parts)


def site(cfg):
    return cfg.get("site", {}) or {}


def site_title(cfg, default="Blog"):
    return str(site(cfg).get("title", default))


def canonical_url(cfg, path):
    return str(site(cfg).get("url", "")).rstrip("/") + path
