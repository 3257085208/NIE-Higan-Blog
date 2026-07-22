from __future__ import annotations

import re
from contextvars import ContextVar

import markdown

from .common import esc, sanitize, strip_ansi, strip_bs

SGR_RE = re.compile(r"\x1b\[([0-9;]*)m")
BLOCK_COUNTER = ContextVar("markdown_block_counter", default=None)
SGR_MAP = {}
for code in range(30, 38):
    SGR_MAP[code] = ("fg", str(code - 30))
for code in range(40, 48):
    SGR_MAP[code] = ("bg", str(code - 40))
for code in range(90, 98):
    SGR_MAP[code] = ("fg", str(code - 90 + 8))
for code in range(100, 108):
    SGR_MAP[code] = ("bg", str(code - 100 + 8))


def block_id(prefix="md"):
    counter = BLOCK_COUNTER.get()
    if counter is None:
        counter = ["", 0]
        BLOCK_COUNTER.set(counter)
    counter[1] += 1
    scope = f"-{counter[0]}" if counter[0] else ""
    return f"{prefix}{scope}-{counter[1]}"


def md_to_html(text, *, nl2br=True, id_prefix=""):
    safe_prefix = re.sub(r"[^A-Za-z0-9_-]", "-", str(id_prefix)).strip("-")
    token = BLOCK_COUNTER.set([safe_prefix, 0]) if BLOCK_COUNTER.get() is None else None
    try:
        text = render_tabs(text)
        text = render_ansi_fences(text)
        extensions = ["fenced_code", "tables", "sane_lists", "smarty", "toc", "attr_list", "admonition"]
        if nl2br:
            extensions.append("nl2br")
        html = markdown.markdown(
            text,
            extensions=extensions,
            extension_configs={"toc": {"permalink": False}},
            output_format="html5",
        )
        html = re.sub(
            r'<li>\s*\[ \]\s+',
            '<li class="task-list-item" style="list-style:none;"><input type="checkbox" disabled style="margin:0 0.2em 0.25em -1.6em;vertical-align:middle;"> ',
            html,
        )
        html = re.sub(
            r'<li>\s*\[(x|X)\]\s+',
            '<li class="task-list-item" style="list-style:none;"><input type="checkbox" disabled checked style="margin:0 0.2em 0.25em -1.6em;vertical-align:middle;"> ',
            html,
        )
        return sanitize(html)
    finally:
        if token is not None:
            BLOCK_COUNTER.reset(token)


def md_to_plain(text):
    text = strip_ansi(text)
    for pattern in (
        ":::: tabs",
        r"^::: tab-item .*?$",
        r"^:::$",
        r"^::::$",
        r"```[\s\S]*?```",
        r"`[^`]*`",
        r"!\[[^\]]*\]\([^)]*\)",
        r"\[[^\]]*\]\([^)]*\)",
        r"[#>*_~]",
    ):
        text = re.sub(pattern, " ", text, flags=re.MULTILINE if pattern.startswith("^") else 0)
    return re.sub(r"\s+", " ", text).strip()


def ansi_to_html(text):
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    state = {"bold": False, "italic": False, "underline": False, "fg": None, "bg": None}
    rows, parts = [], []

    def flush():
        rows.append('<div style="white-space:pre">' + ("".join(parts) if parts else "<span> </span>") + "</div>")
        parts.clear()

    def segment(value):
        if not value:
            return
        value = strip_bs(value)
        if not value:
            return
        classes = " ".join(
            f"xterm-{key}" if current is True else f"xterm-{key}-{current}"
            for key, current in state.items()
            if current is True or (key in ("fg", "bg") and current is not None)
        )
        parts.append(f'<span class="{classes}">{esc(value)}</span>' if classes else f"<span>{esc(value)}</span>")

    last = 0
    for match in SGR_RE.finditer(text):
        for i, line in enumerate(text[last:match.start()].split("\n")):
            if i:
                flush()
            segment(line)
        for code in (int(value) or 0 for value in (match.group(1) or "0").split(";")):
            if code == 0:
                state.update(bold=False, italic=False, underline=False, fg=None, bg=None)
            elif code in (1, 3, 4):
                state[{1: "bold", 3: "italic", 4: "underline"}[code]] = True
            elif code in (22, 23, 24):
                state[{22: "bold", 23: "italic", 24: "underline"}[code]] = False
            elif code in (39, 49):
                state["fg" if code == 39 else "bg"] = None
            elif code in SGR_MAP:
                kind, value = SGR_MAP[code]
                state[kind] = value
        last = match.end()
    for i, line in enumerate(text[last:].split("\n")):
        if i:
            flush()
        segment(line)
    flush()
    return "".join(rows)


def render_ansi_fences(text):
    def repl(match):
        rows = ansi_to_html(match.group(1).strip("\n"))
        return (
            '\n<div class="terminal-container embedMode"><div class="terminal-padding">'
            '<div class="xterm-wrapper" style="max-height:unset;"><div dir="ltr" class="terminal xterm nsk-terminal">'
            '<div class="xterm-viewport"></div><div class="xterm-scrollable-element" role="presentation">'
            f'<div class="xterm-screen"><div class="xterm-rows" aria-hidden="true">{rows}</div></div>'
            '<div class="invisible scrollbar horizontal" aria-hidden="true"></div>'
            '<div class="invisible scrollbar vertical" aria-hidden="true"></div></div></div></div></div></div>\n'
        )

    return re.sub(r"```ansi\s*\n([\s\S]*?)```", repl, text, flags=re.IGNORECASE)


def render_tabs(markdown_text):
    lines = markdown_text.splitlines()
    out, i = [], 0
    while i < len(lines):
        if lines[i].strip() == ":::: tabs":
            rendered, next_index = parse_tabs(lines, i)
            if rendered is not None:
                out.append(rendered)
                i = next_index
                continue
        out.append(lines[i])
        i += 1
    return "\n".join(out)


def parse_tabs(lines, start):
    tabs, i, current_label, current_lines, in_code, found = [], start + 1, None, [], False, False
    while i < len(lines):
        stripped = lines[i].strip()
        if stripped.startswith("```"):
            in_code = not in_code
        if current_label is None:
            if stripped.startswith("::: tab-item"):
                current_label = stripped[len("::: tab-item"):].strip() or f"标签 {len(tabs) + 1}"
                current_lines = []
                i += 1
                continue
            if stripped == "::::":
                found = True
                i += 1
                break
            if stripped == "":
                i += 1
                continue
            return None, start
        else:
            if not in_code and stripped == ":::":
                tabs.append((current_label, "\n".join(current_lines).strip("\n")))
                current_label, current_lines = None, []
                i += 1
                continue
            current_lines.append(lines[i])
            i += 1
    if current_label is not None or not found or not tabs:
        return None, start
    group_id = block_id("tabs")
    parts = []
    for index, (label, body) in enumerate(tabs):
        active = " is-active" if index == 0 else ""
        emoji_match = re.match(r"^([\U0001F300-\U0001FAFF\u2600-\u27BF]+)\s*(.*)$", label.strip())
        emoji, title = (
            (emoji_match.group(1).strip(), (emoji_match.group(2) or "").strip() or label.strip())
            if emoji_match else ("", label.strip())
        )
        icon_html = f'<span class="emoji">{esc(emoji)}</span>' if emoji else ""
        selected = "true" if index == 0 else "false"
        parts.append(
            f'<div class="nsk-magic-tab-title{active}" data-tab-index="{index}" data-tab-group="{group_id}" role="button" tabindex="0" aria-selected="{selected}">{icon_html}{esc(title)}</div>'
        )
        parts.append(
            f'<div class="nsk-magic-tab-body{active}" data-tab-index="{index}" data-tab-group="{group_id}">{md_to_html(body, nl2br=False)}</div>'
        )
    return f'\n<div class="nsk-magic-tabs enabled" data-tab-group="{group_id}">{"".join(parts)}</div>\n', i
