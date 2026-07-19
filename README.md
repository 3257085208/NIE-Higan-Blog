# NIE-Higan-Blog

一套能直接上线的轻量静态博客。

用 Markdown 写文章，Python 一键构建，产物丢到 Cloudflare Pages、GitHub Pages 或任意静态空间就能跑。不依赖 Node，没有后台，也没有花里胡哨的运行时。

---

## 能做什么

- 文章、说说（动态）、归档、分类
- 友链、留言板、更新日志
- 亮色 / 暗色主题，阅读进度条，文章目录
- Tabs、ANSI 终端代码块、任务列表、代码复制
- 首页搜索分页、置顶、外链离开提示
- 构建期生成 RSS、sitemap、canonical、Open Graph、JSON-LD
- 文章 meta 与上下篇在构建时写进 HTML
- 评论可接 Waline（按需加载，需自备服务端）

依赖很少：`PyYAML`、`Markdown`、`bleach`、`tinycss2`。

---

## 快速开始

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

export SITE_URL='https://example.com'   # Windows: $env:SITE_URL='https://example.com'
python build.py
python -m http.server 8080 --directory dist
```

浏览器打开 http://127.0.0.1:8080

---

## 写文章

在 `posts/` 下新建 Markdown：

```markdown
---
title: 标题
date: 2026-07-19
category: 日常
tags: [折腾, 博客]
summary: 可选摘要
top: 0
---

正文从这里开始。
```

说明：

| 字段 | 作用 |
|------|------|
| `category: 说说` | 进入动态页，不计入首页文章统计 |
| `top >= 1000` | 显示置顶徽章 |
| `guestbook.md` / `friends.md` / `changelog.md` | 固定独立页 |

### Tabs

```markdown
:::: tabs
::: tab-item 其一
内容 A
:::
::: tab-item 其二
内容 B
:::
::::
```

### ANSI 终端块

在代码围栏语言处写 `ansi`，即可渲染带颜色的终端输出。

---

## 配置

改根目录 `site.config.json`：

- `site`：站名、简介、头像、域名等
- `social`：侧栏 / 首页社交链接
- `waline`：评论服务地址与选项

部署时建议设置环境变量 `SITE_URL`，会覆盖配置里的 `site.url`，保证 canonical / RSS / sitemap 域名正确。

点赞和阅读量默认指向示例 API（`assets/js/utils.js` 里的 `PV_API` / `LIKE_API`）。自己接服务就改这两个常量；不需要的话也可以在前端初始化里关掉。

---

## 部署

### Cloudflare Pages

| 项 | 值 |
|----|-----|
| Build command | `pip install -r requirements.txt && python build.py` |
| Output directory | `dist` |
| Environment | `SITE_URL=https://你的域名` |

### 其它

Vercel、GitHub Pages、Nginx、对象存储静态托管都一样：构建出 `dist/`，整包挂上去即可。

---

## 目录

```text
builder/    构建器（读 Markdown，吐静态站）
assets/     前端样式与脚本
src/        HTML 模板
posts/      文章与独立页
public/     robots、缓存头等
tests/      单元测试
build.py    入口
```

---

## 测试

```bash
python -m unittest discover -s tests -v
```

---

## 说明

示例配置和演示文章只是为了让你 clone 下来就能构建。上线前请换成自己的域名、头像、评论服务和正文。

爱怎么改怎么改，记得留个 star 就行。
