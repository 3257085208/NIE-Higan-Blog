# NIE-Higan-Blog

一套可以直接部署的轻量静态博客引擎。

使用 Markdown 写作，通过 Python 在构建期生成完整 HTML、RSS、站点地图和结构化数据。部署后的站点不需要 Python、Node.js、数据库或后台服务；评论、阅读量和点赞均为可选集成。

> 第一次使用建议先阅读本页完成本地构建，再按 [完整使用教程](docs/TUTORIAL.md) 配置域名、文章永久链接和部署平台。

## 目录

- [项目特点](#项目特点)
- [运行要求](#运行要求)
- [五分钟开始](#五分钟开始)
- [发布第一篇文章](#发布第一篇文章)
- [永久链接与文件改名](#永久链接与文件改名)
- [站点配置](#站点配置)
- [Markdown 扩展](#markdown-扩展)
- [构建与测试](#构建与测试)
- [部署](#部署)
- [目录结构](#目录结构)
- [安全与隐私](#安全与隐私)
- [常见问题](#常见问题)
- [进一步阅读](#进一步阅读)

## 项目特点

### 内容与页面

- 普通文章、说说（动态）、归档和分类
- 留言板、友情链接、更新日志三个独立页面
- 置顶文章、标签、摘要、字数统计、上一篇/下一篇
- 首页搜索与分页
- 构建期预渲染，禁用 JavaScript 后仍能阅读正文和主要页面

### 阅读体验

- 亮色/暗色主题与三种背景模式
- 阅读进度条、文章目录、代码复制
- Tabs、ANSI 终端输出、表格、任务列表、Admonition
- 移动端菜单、键盘焦点管理与基本无障碍支持
- 外链离站确认

### SEO 与分发

- 每个页面生成 canonical 和 Open Graph 元数据
- 文章生成 JSON-LD `BlogPosting`
- 自动生成 `rss.xml`、`sitemap.xml` 和 `robots.txt`
- 正文、文章元数据和上下篇均在构建期写入 HTML
- 永久 slug 与文件名、置顶权重和列表顺序解耦

### 安全与稳定性

- Markdown HTML 经过 Bleach 白名单清洗
- 生成内容会转义 HTML、属性和 JSON-LD 边界
- 本地保存固定版本的 Waline、Live2D 和字体资源
- `post-slugs.json` 防止文章 URL 因文件改名或排序变化而漂移
- 构建结果可重复；相同输入会产生相同输出
- 自带 GitHub Actions CI，覆盖 Python 3.10 和 3.12

运行依赖只有：`PyYAML`、`Markdown`、`bleach`、`tinycss2`。

## 运行要求

- Python 3.10 或更高版本，推荐 Python 3.12
- Git，可选但推荐
- 一个现代浏览器
- Node.js 不是构建依赖，只在 CI 中用于检查 JavaScript 语法

确认 Python 版本：

```bash
python --version
```

如果 Windows 上没有 `python` 命令，可以尝试 `py -3`；macOS/Linux 也可能需要使用 `python3`。

## 五分钟开始

### 1. 下载并进入项目

```bash
git clone https://github.com/3257085208/NIE-Higan-Blog.git
cd NIE-Higan-Blog
```

### 2. 创建虚拟环境

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 阻止激活脚本，可以只对当前窗口临时放行：

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

### 3. 安装依赖并构建

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python build.py
```

构建成功后，静态站点位于 `dist/`。

### 4. 本地预览

```bash
python -m http.server 8080 --directory dist
```

打开 <http://127.0.0.1:8080>。不要直接双击 `dist/index.html`，因为浏览器的 `file://` 模式无法正确加载根路径资源和 `posts.json`。

## 发布第一篇文章

在 `posts/` 下创建文件，例如：

```text
posts/2026-07-22-我的第一篇文章.md
```

内容：

```markdown
---
title: 我的第一篇文章
date: 2026-07-22
category: 日常
tags: [博客, 记录]
summary: 这是一段用于首页和搜索引擎的摘要。
slug: 20260722-01
top: 0
---

正文从这里开始。
```

同时在 `post-slugs.json` 中登记文件名和永久 slug：

```json
{
  "2026-07-22-我的第一篇文章.md": "20260722-01"
}
```

实际文件中要保留原有映射，只新增这一行。JSON 最后一项不能带多余逗号。

然后执行：

```bash
python -m unittest discover -s tests -v
python build.py
```

文章地址将固定为：

```text
/p/20260722-01/
```

### Front matter 字段

| 字段 | 是否必需 | 说明 |
| --- | --- | --- |
| `title` | 建议填写 | 页面标题；缺省时使用文件名 |
| `date` | 建议填写 | 推荐 `YYYY-MM-DD` |
| `category` | 否 | 默认 `文章`；填写 `说说` 时进入动态页 |
| `tags` | 否 | YAML 字符串数组 |
| `summary` | 否 | 首页和 SEO 摘要；普通文章缺省时自动截取正文 |
| `slug` | 新文章必需 | 唯一且永久，只允许字母、数字、点、下划线和连字符 |
| `top` | 否 | 数值越大排序越靠前；`>= 1000` 显示置顶标记 |

`guestbook.md`、`friends.md`、`changelog.md` 是特殊页面，不需要登记到 `post-slugs.json`。

## 永久链接与文件改名

`post-slugs.json` 是发布历史，不是可以随时重新生成的缓存文件。

已有文章同时存在 front matter `slug` 和映射时，两者必须一致。构建器会拒绝冲突，避免旧 URL、评论、点赞和搜索引擎索引被静默切换到新地址。

### 正确改名

假设原文件为：

```text
2026-07-22-旧标题.md -> 20260722-01
```

把文件改为 `2026-07-22-新标题.md` 后，只移动映射键，保留原值：

```json
{
  "2026-07-22-新标题.md": "20260722-01"
}
```

文章仍位于 `/p/20260722-01/`。如果忘记更新映射，测试或构建会失败，而不是生成一个意外的新 URL。

详细的新建、改名、删除和冲突处理流程见 [教程的永久链接章节](docs/TUTORIAL.md#6-永久链接与-post-slugsjson)。

## 站点配置

根目录的 `site.config.json` 会在构建时写入公开的 `dist/config.js`。常用字段：

| 配置 | 作用 |
| --- | --- |
| `site.title` | 站点名称 |
| `site.tagline` | 首页标题副标题 |
| `site.description` | 默认 SEO 描述 |
| `site.url` | 正式站点根 URL |
| `site.favicon` / `site.avatar` | 图标和头像 URL |
| `site.statusUrl` | 状态页地址 |
| `site.uptimeStart` | 站点运行天数起点 |
| `social` | 社交链接列表 |
| `externalLinkWhitelist` | 不显示离站确认的可信域名 |
| `integrations.pvApi` | 阅读量接口；留空则关闭 |
| `integrations.likeApi` | 点赞接口；留空则关闭 |
| `waline` | Waline 客户端配置 |

部署时建议设置 `SITE_URL`，它会覆盖 `site.url`，确保预览环境和正式环境分别生成正确的 canonical、RSS、sitemap 和 robots：

macOS/Linux：

```bash
SITE_URL='https://blog.example.com' python build.py
```

Windows PowerShell：

```powershell
$env:SITE_URL = 'https://blog.example.com'
python build.py
```

完整配置示例、点赞/PV 接口格式和 Waline 配置见 [完整教程](docs/TUTORIAL.md#4-配置站点)。

## Markdown 扩展

### Tabs

```markdown
:::: tabs
::: tab-item Linux
Linux 内容
:::
::: tab-item Windows
Windows 内容
:::
::::
```

### ANSI 终端块

````markdown
```ansi
\x1b[32mOK\x1b[0m build complete
```
````

ANSI 块需要包含真实 ANSI 转义字符；普通文本 `\x1b` 不会自动转换。

### Admonition

```markdown
!!! warning "注意"
    这里是提示内容，缩进四个空格。
```

原始 HTML 会经过白名单清洗，`script`、事件处理属性和危险协议会被移除。

## 构建与测试

完整测试：

```bash
python -m unittest discover -s tests -v
python -m compileall -q builder build.py
python build.py
```

检查 JSON 构建产物：

```bash
python -m json.tool dist/posts.json > /dev/null
python -m json.tool dist/redirects.json > /dev/null
```

不要手工编辑 `dist/`。每次构建都会删除并重新创建该目录。

## 部署

### Cloudflare Pages

| 项目 | 值 |
| --- | --- |
| Build command | `pip install -r requirements.txt && python build.py` |
| Build output directory | `dist` |
| Environment variable | `SITE_URL=https://你的域名` |

`public/_headers` 会复制到产物根目录，为 Cloudflare Pages 提供 CSP、安全响应头和缓存规则。

### Netlify/Vercel/静态服务器

核心原则相同：执行 `python build.py`，发布 `dist/`。不同平台需要分别设置构建命令、输出目录和 `SITE_URL`。

### GitHub Pages 注意事项

当前模板使用 `/assets/`、`/p/` 等根路径。它适合：

- `username.github.io` 用户/组织站点
- 配置了自定义域名的 Pages 站点

默认的 `username.github.io/repository/` 项目子路径不能直接使用，除非先为整个项目实现 `BASE_PATH` 支持。不要仅修改 `site.url` 来规避，因为 HTML、JavaScript 和资源路径仍是根路径。

更详细的平台配置和 Nginx 示例见 [部署章节](docs/TUTORIAL.md#10-部署)。

## 目录结构

```text
.
├── assets/                 # CSS、JavaScript、字体和本地第三方浏览器资源
├── builder/                # Python 静态站点生成器
├── docs/                   # 使用文档
├── posts/                  # Markdown 文章与特殊页面
├── public/                 # 复制到 dist 根目录的托管配置
├── src/                    # HTML 模板
├── tests/                  # 单元测试
├── build.py                # 构建入口
├── post-slugs.json         # 文件名到永久 slug 的发布历史
├── requirements.txt        # Python 运行依赖
├── site.config.json        # 站点公开配置
└── dist/                   # 构建产物，不提交 Git
```

## 安全与隐私

- `site.config.json`、Markdown、前端 JavaScript 和 `dist/` 都是公开内容。
- 不要把 API 密钥、数据库密码、私有 Token 或未脱敏个人信息写入仓库。
- 浏览器调用的点赞/PV 接口不能依靠前端隐藏密钥；服务端必须自行做限流、校验和滥用防护。
- 公开仓库会保留 Git 历史。误提交秘密后，仅删除当前文件并不足以完成撤销，还需要吊销密钥并清理历史。
- 第三方评论、头像、图片和远程样式会产生外部网络请求；上线前应检查自己的隐私政策和 CSP。

## 常见问题

### `missing permanent slug`

新文章没有 `slug`，或文件名没有登记到 `post-slugs.json`。两处填写相同 slug 后重试。

### `front matter slug ... conflicts with persisted slug`

文章中的 `slug` 与 `post-slugs.json` 不一致。已发布文章应保留映射里的旧值，不要为了标题或文件名变化而生成新 slug。

### `duplicate slug`

两篇文章使用了同一个永久 ID。为尚未发布的新文章选择另一个 slug；不要修改已发布文章的 slug。

### 样式或脚本没有更新

先重新运行 `python build.py`。构建器会生成内容哈希版本号；如果托管平台仍返回旧文件，再清理平台缓存。

### 评论、点赞或阅读量显示失败

检查 `site.config.json` 中的 URL、浏览器控制台、接口 CORS 和 `public/_headers` 中的 CSP。公共仓库默认使用示例地址，需要替换或留空关闭。

### 私有浏览/禁用本地存储

站点仍可阅读和使用主要功能，但主题、背景与点赞状态可能不会跨页面保存。

## 进一步阅读

- [完整安装、写作、配置、测试与部署教程](docs/TUTORIAL.md)
- [第三方浏览器资源与许可证](assets/vendor/THIRD_PARTY.md)
- [示例文章](posts/2026-01-21-welcome.md)

示例域名、头像、评论和统计接口仅用于展示。上线前请替换为自己的配置。
