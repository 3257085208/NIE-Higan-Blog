# NIE-Higan-Blog

> 轻量静态博客引擎 · Python 构建 · Markdown 写作 · 可托管在 Cloudflare Pages / 任意静态空间

这是 [聶.NET](https://www.niekaixiang.com) 背后引擎的 **公开脱敏演示版**。  
完整私有站点仓库（含真实配置与文章）不在此公开。

线上效果参考：https://www.niekaixiang.com

---

## 特性

- 纯静态输出，无 Node 构建链
- 文章 / 说说 / 归档 / 分类 / 友链 / 留言板 / 更新日志
- Tabs、ANSI 终端块、任务列表、代码复制
- 亮暗主题、阅读进度、TOC、外链提示
- 构建期 SEO：canonical、OG、JSON-LD、RSS、sitemap、文章 meta、prev/next
- Waline 评论按需加载（需自备服务端）
- 依赖极少：PyYAML / Markdown / bleach / tinycss2

---

## 快速开始

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
source .venv/bin/activate
pip install -r requirements.txt

export SITE_URL='https://example.com'   # Windows: $env:SITE_URL='https://example.com'
python build.py
python -m http.server 8080 --directory dist
```

打开 http://127.0.0.1:8080

---

## 写文章

在 `posts/` 新建：

```markdown
---
title: 标题
date: 2026-07-19
category: 日常
tags: [demo]
summary: 可选
top: 0
---

正文……
```

- `category: 说说` → 动态页
- `top >= 1000` → 置顶徽章
- 特殊文件：`guestbook.md` / `friends.md` / `changelog.md`

---

## 配置

编辑 `site.config.json`：

- `site.*` 站点信息
- `social` 社交链接
- `waline` 评论

环境变量 `SITE_URL` 可覆盖 `site.url`（影响 canonical / RSS / sitemap）。

前端点赞/PV 默认指向 `https://api.example.com/...`，请改 `assets/js/utils.js` 中的 `PV_API` / `LIKE_API`，或自己关掉相关初始化。

---

## 部署（Cloudflare Pages）

| 项 | 值 |
|----|-----|
| Build command | `pip install -r requirements.txt && python build.py` |
| Output | `dist` |
| Env | `SITE_URL=https://your.domain` |

---

## 测试

```bash
python -m unittest discover -s tests -v
```

---

## 目录

```text
builder/   静态站点生成器
assets/    前端 CSS/JS
src/       HTML 模板
posts/     Markdown 内容（演示文）
public/    robots / headers
tests/     unittest
```

---

## 与私有站的关系

| | 私有库 NIE | 本仓库 Higan |
|--|-----------|--------------|
| 用途 | 真实站点源码 | 秀肌肉 / 二次开发模板 |
| 配置 | 真实域名与密钥侧配置 | example.com 占位 |
| 文章 | 全部博文 | 少量演示文 |
| 联系方式 | 真实社交 | 脱敏 |

引擎代码同源；本仓库删除了个人联系方式、私有 API 域名与私人文章。

---

## License

引擎代码可用于学习与二次开发。  
演示文与品牌文案请勿伪造成官方站点。

花有重开日，人无再少年。
