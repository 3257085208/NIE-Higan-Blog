# NIE-Higan-Blog 完整使用教程

本文从空白环境开始，说明如何安装、配置、写作、维护永久链接、测试并部署 NIE-Higan-Blog。命令默认在项目根目录执行。

## 目录

1. [理解工作方式](#1-理解工作方式)
2. [准备环境](#2-准备环境)
3. [第一次构建](#3-第一次构建)
4. [配置站点](#4-配置站点)
5. [写普通文章和说说](#5-写普通文章和说说)
6. [永久链接与 post-slugs.json](#6-永久链接与-post-slugsjson)
7. [维护特殊页面](#7-维护特殊页面)
8. [Markdown 扩展](#8-markdown-扩展)
9. [评论、点赞和阅读量](#9-评论点赞和阅读量)
10. [部署](#10-部署)
11. [测试和发布检查](#11-测试和发布检查)
12. [升级与二次开发](#12-升级与二次开发)
13. [安全和隐私](#13-安全和隐私)
14. [故障排查](#14-故障排查)

## 1. 理解工作方式

项目分为内容源、构建器和静态产物三层：

```text
posts/*.md + site.config.json + assets/ + src/
                        |
                        | python build.py
                        v
                     dist/
                        |
                        | 上传到静态托管
                        v
                  浏览器直接访问
```

构建器会完成以下工作：

1. 读取 `site.config.json` 和 `post-slugs.json`。
2. 解析 `posts/*.md` 的 YAML front matter 和正文。
3. 校验每篇文章的永久 slug。
4. 清洗 Markdown 生成的 HTML。
5. 生成首页、文章、归档、分类、动态和独立页面。
6. 生成 canonical、Open Graph、JSON-LD、RSS、sitemap 和 robots。
7. 复制前端资源和 `public/` 托管配置。
8. 将最终结果写入 `dist/`。

部署环境只负责提供静态文件。Python 和构建依赖不会进入访问者浏览器。

### 哪些内容会公开

以下内容都应视为公开数据：

- `posts/` 中的所有正文和 front matter
- `site.config.json` 中的所有配置
- `assets/` 和 `src/` 中的前端代码
- 构建后的 `dist/config.js`、`posts.json` 和 HTML
- Git 仓库历史中的旧版本

因此不要在这些位置存放任何秘密。

## 2. 准备环境

### 2.1 安装 Python

要求 Python 3.10+，推荐 3.12。

macOS/Linux：

```bash
python3 --version
```

Windows PowerShell：

```powershell
py -3 --version
```

如果版本过低，请从操作系统包管理器或 <https://www.python.org/downloads/> 安装新版。Windows 安装器中建议勾选 `Add python.exe to PATH`。

### 2.2 获取代码

使用 Git：

```bash
git clone https://github.com/3257085208/NIE-Higan-Blog.git
cd NIE-Higan-Blog
```

也可以在 GitHub 下载 ZIP，解压后进入包含 `build.py` 的目录。

### 2.3 创建虚拟环境

虚拟环境可以避免博客依赖污染系统 Python。

macOS/Linux：

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell：

```powershell
py -3 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

Windows CMD：

```bat
py -3 -m venv .venv
.venv\Scripts\activate.bat
```

激活成功后，终端提示符通常会出现 `(.venv)`。

### 2.4 安装依赖

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

项目不要求安装 npm 包。Node.js 只用于可选的 JavaScript 语法检查。

## 3. 第一次构建

### 3.1 构建站点

```bash
python build.py
```

构建器每次都会重新创建 `dist/`，所以不要在 `dist/` 中直接修改文件。

典型输出结构：

```text
dist/
├── index.html
├── 404.html
├── archive/index.html
├── category/index.html
├── status/index.html
├── guestbook/index.html
├── friends/index.html
├── changelog/index.html
├── p/<slug>/index.html
├── assets/
├── config.js
├── posts.json
├── redirects.json
├── rss.xml
├── sitemap.xml
└── robots.txt
```

### 3.2 启动本地服务器

```bash
python -m http.server 8080 --directory dist
```

打开 <http://127.0.0.1:8080>。

停止服务器时，在终端按 `Ctrl+C`。

不要使用 `file:///.../dist/index.html` 预览。项目使用 `/assets/`、`/posts.json` 等根路径，必须通过 HTTP 服务器访问。

### 3.3 使用正确的本地域名元数据

普通本地预览可以直接构建。需要检查 canonical、RSS 或 sitemap 时，临时指定 URL：

macOS/Linux：

```bash
SITE_URL='http://127.0.0.1:8080' python build.py
```

Windows PowerShell：

```powershell
$env:SITE_URL = 'http://127.0.0.1:8080'
python build.py
```

构建正式版本时应改回真实的 HTTPS 域名。

## 4. 配置站点

配置文件是根目录的 `site.config.json`。它必须是合法 JSON，不能写注释，也不能在最后一项后保留逗号。

### 4.1 完整示例

```json
{
  "site": {
    "title": "My Blog",
    "tagline": "Notes and experiments",
    "description": "My personal static blog",
    "url": "https://blog.example.com",
    "favicon": "https://cdn.example.com/favicon.png",
    "avatar": "https://cdn.example.com/avatar.png",
    "intro": "Keep building.",
    "statusUrl": "https://status.example.com",
    "poweredBy": "Higan",
    "footerYear": 2026,
    "uptimeStart": "2026-01-01",
    "statusName": "My Blog"
  },
  "social": [
    {
      "title": "Email",
      "href": "mailto:me@example.com",
      "iconClass": "fa-solid fa-envelope"
    },
    {
      "title": "GitHub",
      "href": "https://github.com/example",
      "iconClass": "fa-brands fa-github"
    }
  ],
  "externalLinkWhitelist": [
    "example.com"
  ],
  "integrations": {
    "pvApi": "",
    "likeApi": ""
  },
  "waline": {
    "serverURL": "https://waline.example.com",
    "emoji": [
      "//cdn.jsdelivr.net/npm/@waline/emojis@1.1.0/weibo"
    ],
    "login": "disable",
    "pageview": true,
    "search": false,
    "imageUploader": false,
    "locale": {
      "placeholder": "支持 Markdown"
    }
  }
}
```

### 4.2 `site` 字段

| 字段 | 说明 |
| --- | --- |
| `title` | 导航、标题和结构化数据使用的站名 |
| `tagline` | 首页 `<title>` 中的补充文字 |
| `description` | 没有文章摘要时使用的默认描述 |
| `url` | 不带末尾 `/` 的站点根地址 |
| `favicon` | 浏览器图标 URL |
| `avatar` | 首页和动态头像 URL |
| `intro` | 首页简介 |
| `statusUrl` | 顶部导航中的状态页地址 |
| `poweredBy` | 页脚显示名称 |
| `footerYear` | 页脚年份 |
| `uptimeStart` | 运行天数起点，格式 `YYYY-MM-DD` |
| `statusName` | 动态卡片和文章作者名称 |

`favicon` 和 `avatar` 可以使用站内路径，例如 `/assets/images/avatar.webp`。如需这样做，请把文件放入 `assets/images/`。

### 4.3 `social`

每项包含：

- `title`：鼠标提示和可访问名称
- `href`：链接，例如 HTTPS、`mailto:`、`tel:`
- `iconClass`：Font Awesome 图标类

例：

```json
{
  "title": "Telegram",
  "href": "https://t.me/example",
  "iconClass": "fa-brands fa-telegram"
}
```

### 4.4 `externalLinkWhitelist`

外链默认显示离站确认。白名单中的域名及其子域名不会显示确认框。

推荐只填写主机名：

```json
"externalLinkWhitelist": ["example.com", "example.net"]
```

不要为了省事加入过宽的公共域名。

### 4.5 `SITE_URL` 环境变量

部署环境变量 `SITE_URL` 会覆盖 `site.url`。这适合共用同一份代码生成预览站和正式站：

```bash
SITE_URL='https://preview.example.com' python build.py
```

它会影响：

- canonical URL
- Open Graph URL
- JSON-LD 主页面 URL
- RSS 链接
- sitemap 链接
- robots 中的 sitemap 地址

## 5. 写普通文章和说说

### 5.1 文件名

推荐格式：

```text
YYYY-MM-DD-标题摘要.md
```

文件名用于内容管理和默认日期/标题回退，不直接决定正式文章 URL。正式 URL 由 slug 决定。

避免使用以下三个文件名，它们属于特殊页面：

- `guestbook.md`
- `friends.md`
- `changelog.md`

### 5.2 普通文章模板

```markdown
---
title: 使用 Higan 搭建静态博客
date: 2026-07-22
category: 教程
tags: [Higan, Python, 静态站]
summary: 从安装到部署的完整记录。
slug: 20260722-01
top: 0
---

## 开始

正文内容。
```

### 5.3 说说模板

```markdown
---
title: 说说
date: 2026-07-22
category: 说说
tags: []
slug: 20260722-02
top: 0
---

今天完成了一次博客升级。
```

说说会出现在 `/status/`，不会计入首页普通文章列表和普通文章字数统计，但仍有独立页面、永久 URL、点赞和评论路径。

### 5.4 字段规则

| 字段 | 类型 | 规则 |
| --- | --- | --- |
| `title` | 字符串 | 建议填写；缺省使用文件名 |
| `date` | 日期/字符串 | 推荐合法 `YYYY-MM-DD` |
| `category` | 字符串 | 精确等于 `说说` 时进入动态 |
| `tags` | 数组 | 例如 `[Python, 博客]` |
| `summary` | 字符串 | 普通文章缺省时自动生成约 160 字 |
| `slug` | 字符串 | 新文章必需，发布后不可修改 |
| `top` | 整数 | `>= 1000` 显示置顶徽章 |

### 5.5 日期和排序

文章列表按以下规则排序：

1. `top` 从大到小
2. 日期从新到旧
3. 文件名作为稳定的最终排序条件

上一篇/下一篇按日期和 slug 的时间顺序计算，不受置顶影响。

## 6. 永久链接与 `post-slugs.json`

这是维护博客时最重要的章节。

### 6.1 为什么需要映射文件

早期按日期和文件排序生成编号的方案存在三个问题：

- 同一天增加新文章可能让旧编号变化
- 修改置顶权重可能改变顺序
- 重命名文件可能改变 URL

现在每篇文章使用永久 slug：

```text
/p/<slug>/
```

`post-slugs.json` 记录“当前文件名 -> 已发布 slug”，构建器不会重新编号。

### 6.2 slug 格式

允许格式：

```text
[A-Za-z0-9][A-Za-z0-9._-]*
```

合法示例：

```text
20260722-01
hello-world
release_2.0
```

非法示例：

```text
/hello
../post
中文-slug
hello world
```

推荐继续使用 `YYYYMMDD-XX`，便于人工检查和避免冲突。

### 6.3 新增文章

1. 创建 Markdown。
2. 在 front matter 写入未使用的 slug。
3. 在 `post-slugs.json` 添加同一文件名和同一 slug。
4. 运行单元测试。
5. 构建并预览。

示例：

```json
{
  "2026-07-21-旧文章.md": "20260721-01",
  "2026-07-22-新文章.md": "20260722-01"
}
```

为什么两处都写：front matter 让文章本身具备明确身份，映射文件则保存整个站点的发布历史并供 CI 检查完整性。

### 6.4 重命名文章文件

假设原映射：

```json
"2026-07-22-旧标题.md": "20260722-01"
```

重命名文件后，将键改成新文件名，值保持不变：

```json
"2026-07-22-新标题.md": "20260722-01"
```

如果文章 front matter 中存在 slug，也必须继续使用 `20260722-01`。

结果：

- 正式地址 `/p/20260722-01/` 不变
- 评论路径不变
- 点赞 ID 不变
- canonical 和搜索引擎索引地址不变

由文件名形成的非标准旧路径不属于稳定公开 API。正式分享时始终使用 `/p/<slug>/`。

### 6.5 修改标题

只修改 `title`，不要修改 slug。标题、文件名和 URL 可以互相独立。

### 6.6 删除文章

1. 删除 Markdown 文件。
2. 从 `post-slugs.json` 删除对应键。
3. 运行测试和构建。
4. 如果旧 URL 需要继续存在，应保留一篇说明文章，或在托管平台配置明确的 301/410 规则。

构建器目前不会为已删除正文自动生成墓碑页面。

### 6.7 常见错误

`missing permanent slug`：

- 新文章没写 slug
- 映射文件漏了当前文件名
- 文件改名后映射键仍是旧文件名

`front matter slug ... conflicts with persisted slug`：

- 文章 slug 与已发布映射不同
- 正确做法通常是恢复映射中的旧值

`duplicate slug`：

- 两篇文章使用相同 slug
- 只能修改尚未发布的新文章；不要修改已发布文章来腾位置

### 6.8 不要做的事情

- 不要按文件列表重新生成整个映射
- 不要因为修改标题而更换 slug
- 不要复用已删除文章的 slug
- 不要通过调整 `top` 重新编号
- 不要忽略 CI 中的映射完整性失败

## 7. 维护特殊页面

特殊页面不进入普通文章 slug 映射。

### 7.1 留言板 `posts/guestbook.md`

可以直接写 Markdown。页面地址固定为 `/guestbook/`，配置 Waline 后显示评论区。

```markdown
有什么想说的，写在下面就好。
```

### 7.2 更新日志 `posts/changelog.md`

页面地址固定为 `/changelog/`，默认不显示评论区。

```markdown
---
title: 更新日志
date: 2026-07-22
---

## 2.1.0

- 增加新功能
- 修复构建问题
```

### 7.3 友情链接 `posts/friends.md`

页面地址固定为 `/friends/`。卡片数据位于 front matter：

```markdown
---
title: 友情链接
date: 2026-07-22
friends:
  - name: Example Blog
    bio: A static blog
    url: https://example.com
    avatar: https://example.com/avatar.png
---

欢迎交换友链。
```

外部 URL 会经过 HTML 属性转义，并受到全站外链提示逻辑影响。

## 8. Markdown 扩展

### 8.1 标准能力

支持常用 Markdown 以及：

- fenced code
- 表格
- 有序/无序列表
- 自动目录标题 ID
- 属性列表（最终仍经过 HTML 白名单）
- Admonition
- 删除线和智能标点
- 单换行转 `<br>`

### 8.2 任务列表

```markdown
- [x] 完成构建
- [ ] 部署站点
```

任务框是只读展示，不会保存用户勾选状态。

### 8.3 Tabs

```markdown
:::: tabs
::: tab-item macOS/Linux
使用 `source .venv/bin/activate`。
:::
::: tab-item Windows
使用 `.\.venv\Scripts\Activate.ps1`。
:::
::::
```

规则：

- 外层以 `:::: tabs` 开始，以 `::::` 结束
- 每一项以 `::: tab-item 标签` 开始，以 `:::` 结束
- 代码围栏中的 `:::` 不会提前结束标签
- 构建器会生成确定性的标签组 ID

### 8.4 ANSI 终端输出

使用语言名 `ansi`：

````markdown
```ansi
真实的 ANSI 彩色终端输出
```
````

支持常见 16 色前景/背景、粗体、斜体和下划线。控制字符会在转为 HTML 前处理，文本会转义。

### 8.5 Admonition

```markdown
!!! note "提示"
    内容必须缩进。
```

常用类型包括 `note`、`warning`、`danger`、`info`。

### 8.6 图片

```markdown
![替代文本](https://example.com/image.webp)
```

构建器会自动为图片加入 `loading="lazy"` 和 `decoding="async"`。请始终填写有意义的替代文本。

### 8.7 原始 HTML 和安全清洗

Markdown 允许有限原始 HTML，但生成结果会经过 Bleach：

- 删除 `script`
- 删除 `onclick`、`onerror` 等事件属性
- 限制 URL 协议
- 限制可用 CSS 属性
- 保留必要的 `aria-*` 和 `data-*`

如果某段复杂 HTML 在构建后消失，应先检查白名单，而不是关闭清洗器。

## 9. 评论、点赞和阅读量

这些功能都不是静态构建的必需项。

### 9.1 关闭集成

将接口留空：

```json
"integrations": {
  "pvApi": "",
  "likeApi": ""
}
```

如果不使用 Waline，可以删除 `waline` 配置，或在模板中移除相关容器。

### 9.2 阅读量 API 约定

浏览器请求：

```text
GET <pvApi>?path=site
GET <pvApi>?path=/p/20260722-01/
```

期望响应：

```json
{
  "pv": 123
}
```

接口应正确设置 CORS，并对 `path` 做长度限制和规范化。

### 9.3 点赞 API 约定

读取：

```text
GET <likeApi>?path=/p/20260722-01/&action=get
```

增加或取消：

```text
GET <likeApi>?path=/p/20260722-01/&action=inc
GET <likeApi>?path=/p/20260722-01/&action=dec
```

期望响应：

```json
{
  "likes": 12
}
```

客户端本地保存已点赞路径只是界面状态，不是安全机制。服务端仍需要：

- 限流
- 防止计数变成负数
- 校验 action 和 path
- 防自动化滥用
- 必要时使用 IP、匿名设备标识或登录身份去重

不要把服务端密钥写入前端 URL 或 `site.config.json`。

### 9.4 Waline

先部署自己的 Waline 服务端，再填写：

```json
"waline": {
  "serverURL": "https://waline.example.com",
  "emoji": ["//cdn.jsdelivr.net/npm/@waline/emojis@1.1.0/weibo"],
  "login": "disable",
  "pageview": true,
  "search": false,
  "imageUploader": false,
  "locale": {
    "placeholder": "支持 Markdown"
  }
}
```

客户端资源保存在 `assets/vendor/waline/`，但评论数据和接口仍由你的 Waline 服务端提供。

如果浏览器控制台出现连接被 CSP 拒绝，需要把自己的 Waline 域名加入 `public/_headers` 的：

- `form-action`
- `connect-src`

同时检查 Waline 服务端 CORS 配置。

## 10. 部署

正式部署前先构建：

```bash
SITE_URL='https://blog.example.com' python build.py
```

### 10.1 Cloudflare Pages

连接 GitHub 仓库后填写：

| 设置 | 值 |
| --- | --- |
| Framework preset | None |
| Build command | `pip install -r requirements.txt && python build.py` |
| Build output directory | `dist` |
| Environment variable | `SITE_URL=https://blog.example.com` |

如果平台选择 Python 版本，使用 3.10 或 3.12。

仓库中的 `public/_headers` 和 `public/_redirects` 会进入 `dist/`。修改评论或统计域名后，记得同步 CSP。

### 10.2 Netlify

常用设置：

```text
Build command: pip install -r requirements.txt && python build.py
Publish directory: dist
```

在环境变量中设置 `SITE_URL`。Netlify 也识别 `_headers` 文件。

### 10.3 Vercel

将 Build Command 设置为：

```text
pip install -r requirements.txt && python build.py
```

Output Directory 设置为：

```text
dist
```

同时配置 `SITE_URL`。不同 Vercel 运行时对 Python 构建工具的默认版本可能变化，部署日志中应确认 Python >= 3.10。

### 10.4 GitHub Pages

当前项目使用根路径资源，不直接支持 `https://username.github.io/repository/` 形式的项目子路径。

可以使用：

- `https://username.github.io/` 用户/组织站点
- 绑定自定义域名后的 Pages

仅把 `site.url` 设置成带 `/repository` 的地址无法解决问题，因为模板和 JavaScript 中的 `/assets/`、`/posts.json`、`/p/` 仍指向域名根目录。

### 10.5 Nginx

把 `dist/` 上传到服务器，例如 `/var/www/higan`：

```nginx
server {
    listen 443 ssl http2;
    server_name blog.example.com;

    root /var/www/higan;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```

`_headers` 是托管平台配置文件，Nginx 不会自动读取。需要在 Nginx 配置中自行设置 CSP、HSTS、缓存和其它响应头。

### 10.6 部署后检查

至少访问：

- `/`
- `/archive/`
- `/category/`
- `/status/`
- 一篇 `/p/<slug>/`
- `/guestbook/`
- `/rss.xml`
- `/sitemap.xml`
- 一个不存在路径，确认 404 和旧链接跳转行为

查看页面源代码，确认 canonical 使用正式域名。

## 11. 测试和发布检查

### 11.1 项目自带测试

```bash
python -m unittest discover -s tests -v
```

测试覆盖：

- 永久 slug 分配、冲突和完整性
- 同日新增文章时旧 URL 不移动
- front matter 不能覆盖已发布映射
- Markdown 清洗与 JSON-LD 转义
- Tabs ID 确定性
- 首页预渲染
- 文章元数据与上下篇
- sitemap、robots、404 和资源版本

### 11.2 编译和构建检查

```bash
python -m compileall -q builder build.py
python build.py
python -m json.tool dist/posts.json > /dev/null
python -m json.tool dist/redirects.json > /dev/null
```

Windows PowerShell 可把 `/dev/null` 替换为 `$null`：

```powershell
python -m json.tool dist/posts.json | Out-Null
python -m json.tool dist/redirects.json | Out-Null
```

### 11.3 可选开发检查

安装工具：

```bash
python -m pip install ruff bandit pip-audit coverage
```

运行：

```bash
ruff check .
bandit -q -r builder build.py
pip-audit --no-deps --disable-pip -r requirements.txt
coverage run -m unittest discover -s tests
coverage report
```

已安装 Node.js 时：

```bash
find assets -name '*.js' -print0 | xargs -0 -n1 node --check
```

Windows 可以逐个运行 `node --check`，或依赖仓库 CI 完成语法检查。

### 11.4 发布前清单

- [ ] 新文章 front matter 包含唯一 slug
- [ ] `post-slugs.json` 与普通文章/说说文件完全对应
- [ ] 没有修改已发布 slug
- [ ] `SITE_URL` 是正式 HTTPS 域名
- [ ] 示例头像、邮箱、评论和统计接口已替换或关闭
- [ ] CSP 包含实际使用的 Waline、PV 和点赞域名
- [ ] 单元测试全部通过
- [ ] 本地构建和预览正常
- [ ] 仓库中没有密钥和隐私信息
- [ ] 部署后 canonical、RSS、sitemap 正确

## 12. 升级与二次开发

### 12.1 修改样式

样式入口是 `assets/app.css`，它会导入 `assets/css/` 下的模块。

不要修改 `dist/assets/`。改完源文件后重新构建。资源内容哈希会自动改变查询参数，降低浏览器缓存旧版本的概率。

### 12.2 修改前端逻辑

主要文件：

```text
assets/app.js
assets/js/app-core.js
assets/js/dom-actions.js
assets/js/enhance.js
assets/js/features/
```

配置读取集中在 `assets/js/utils.js`。新增浏览器持久状态时，应处理 `localStorage` 被禁用或抛出异常的情况。

### 12.3 修改页面模板

模板位于：

```text
src/index.template.html
```

`__PAGE_TITLE__`、`__META_DESC__` 等占位符由构建器替换。删除或改名占位符前，应搜索 `builder/` 中的使用位置并补充测试。

### 12.4 修改构建器

Python 模块位于 `builder/`：

| 文件 | 职责 |
| --- | --- |
| `common.py` | 配置、路径、清洗、公共工具 |
| `content.py` | 文章解析和 slug 分配 |
| `markdown_render.py` | Markdown、Tabs、ANSI |
| `page_render.py` | 模板和元数据渲染 |
| `site_pages.py` | 各类页面内容 |
| `feed.py` | RSS、sitemap、robots |
| `pipeline.py` | 总构建流程 |

修改后至少运行单元测试、compileall 和两次构建对比。

### 12.5 从上游更新

更新前备份或提交自己的修改。尤其保留：

- `posts/`
- `post-slugs.json`
- `site.config.json`
- 自己修改的 `public/_headers`
- 自定义图片和样式

合并更新后，不要用上游示例 `post-slugs.json` 覆盖自己的发布历史。

## 13. 安全和隐私

### 13.1 配置不是秘密存储

`site.config.json` 会进入 `dist/config.js`。以下内容绝不能放进去：

- GitHub Token
- Cloudflare API Token
- 数据库密码
- Waline 服务端密钥
- 私有对象存储密钥
- 只允许服务端知道的签名密钥

浏览器必须调用需要公开访问的 API URL，认证和滥用防护应由服务端完成。

### 13.2 文章 HTML 清洗

构建器默认清洗 Markdown HTML。不要为了嵌入一段脚本而整体关闭清洗。更安全的做法是：

1. 在受控前端模块中实现功能。
2. 使用固定的数据属性传参。
3. 更新 CSP 和测试。
4. 避免允许任意脚本 URL。

### 13.3 内容安全策略

Cloudflare/Netlify 使用的 CSP 位于 `public/_headers`。

更换外部服务后检查：

- `script-src`
- `style-src`
- `font-src`
- `img-src`
- `connect-src`
- `form-action`

只添加实际需要的来源，不建议使用宽泛的 `*`。

### 13.4 公开仓库脱敏

发布公开仓库前扫描：

```bash
git grep -n -i -E 'token|secret|password|private.key|api.key'
```

这只能辅助检查，不能代替人工审阅。文章正文、历史提交、图片 EXIF 和远端构建日志也可能包含隐私。

## 14. 故障排查

### 14.1 `ModuleNotFoundError`

确认已激活虚拟环境并安装依赖：

```bash
python -m pip install -r requirements.txt
python -c "import yaml, markdown, bleach, tinycss2; print('ok')"
```

### 14.2 PowerShell 无法运行激活脚本

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
```

该设置只影响当前 PowerShell 窗口。

### 14.3 构建提示缺少 slug

检查：

1. 文件是否属于普通文章/说说，而不是三个特殊页面。
2. front matter 是否正确写在两个 `---` 之间。
3. `slug` 是否存在。
4. `post-slugs.json` 是否使用完整文件名（包含 `.md`）。

### 14.4 映射完整性测试失败

列出当前文章和映射：

```bash
ls posts
python -m json.tool post-slugs.json
```

映射应覆盖所有普通文章和说说，但不包含 `guestbook.md`、`friends.md`、`changelog.md`。

### 14.5 本地页面没有样式

不要直接打开文件。运行：

```bash
python -m http.server 8080 --directory dist
```

并访问 `http://127.0.0.1:8080/`。

### 14.6 部署后文章 404

确认托管平台：

- 上传的是 `dist/` 内容，而不是整个源代码目录
- 支持目录索引 `index.html`
- 没有把站点部署在未支持的项目子路径
- 没有错误的 SPA rewrite 覆盖物理文件

Nginx 应使用：

```nginx
try_files $uri $uri/ =404;
```

### 14.7 canonical 域名错误

检查部署环境中的 `SITE_URL`。环境变量优先级高于 `site.config.json`。

重新构建后查看：

```bash
grep -R 'rel="canonical"' dist/index.html dist/p | head
```

### 14.8 评论区不显示

确认：

- 当前页面是普通文章或留言板
- `waline.serverURL` 正确
- 浏览器网络请求没有 CORS 错误
- CSP 的 `connect-src` 和 `form-action` 包含 Waline 域名
- Waline 服务端可从公网访问

### 14.9 点赞或阅读量显示 `-`

这表示请求失败或响应格式不符合约定。检查：

- API URL
- HTTPS 混合内容
- CORS
- CSP `connect-src`
- 响应 HTTP 状态
- JSON 是否包含 `likes` 或 `pv`

### 14.10 浏览器仍显示旧资源

1. 重新运行 `python build.py`。
2. 确认 HTML 中资源 `?v=` 已变化。
3. 清理托管平台缓存。
4. 使用无痕窗口或禁用浏览器缓存复查。

### 14.11 GitHub Actions 没有运行测试

先查看 Actions 页面中的注释。常见外部原因包括：

- 仓库未启用 Actions
- 账户账单或消费额度限制
- 组织策略禁止工作流
- Actions 服务暂时异常

如果作业在开始前就被平台拒绝，这不等同于测试失败。仍应在本地运行完整测试，并处理账户设置后重新执行 CI。

---

完成配置后，建议保留一份自己的发布检查清单。这个项目最需要长期保护的文件是 `post-slugs.json`：内容和标题都可以改，已经公开的永久链接不要漂移。
