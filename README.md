# 🌸 Higan-Static（聶.NET 博客系统）

这是一个**超轻量静态博客系统**：

- 文章用 `posts/*.md` 写
- `build.py` 自动生成：
  - `posts.json`（首页 SPA 用）
  - `sitemap.xml`（SEO）
  - `p/<slug>/index.html`（每篇文章一个独立页面，利于收录和分享预览）
- 前端只靠一个 `index.html` 渲染（移动端/暗黑模式/Higan 风格）

你可以部署在：
- ✅ GitHub Pages
- ✅ Vercel
- ✅ Cloudflare Pages

> 新手建议：**Vercel 或 CF Pages**（省心、速度快、HTTPS 自动、绑定域名方便）

---

## 目录

- [项目结构](#项目结构)
- [快速开始（3分钟跑起来）](#快速开始3分钟跑起来)
- [写文章](#写文章)
- [本地预览](#本地预览)
- [部署方案一GitHub-Actions-生成-平台只托管推荐新手省改动](#部署方案一github-actions-生成-平台只托管推荐新手省改动)
- [部署方案二不用-actions让-vercelcf-pages-自己构建更干净](#部署方案二不用-actions让-vercelcf-pages-自己构建更干净)
- [部署到 GitHub Pages](#部署到-github-pages)
- [部署到 Vercel](#部署到-vercel)
- [部署到 Cloudflare Pages](#部署到-cloudflare-pages)
- [绑定自定义域名](#绑定自定义域名)
- [评论系统 Waline 配置](#评论系统-waline-配置)
- [常见问题](#常见问题)

---

## 项目结构

```
.
├─ index.html                 # 前端（SPA 首页 + 路由 + Waline 等）
├─ build.py                   # 构建脚本（生成 posts.json / sitemap / 独立文章页）
├─ posts/                     # 你的 Markdown 文章都放这里
│  ├─ 2026-02-06-你好世界.md
│  └─ guestbook.md            # 留言板（可选）
├─ p/                         # 构建产物：每篇文章一个目录
├─ posts.json                 # 构建产物：首页文章索引
├─ sitemap.xml                # 构建产物：站点地图
├─ robots.txt                 # 爬虫规则（可选）
├─ vercel.json                # Vercel 缓存策略（可选）
└─ .github/workflows/build.yml# GitHub Actions 自动构建（可选）
```

---

## 快速开始（3分钟跑起来）

### 1）Fork / 新建仓库
1. 在 GitHub 把本仓库 Fork 到你自己账号（或新建仓库后上传这些文件）。
2. 确保默认分支是 `main`。

### 2）写第一篇文章
在 `posts/` 下新建文件，例如：

`posts/2026-02-06-你好世界.md`

内容示例：

```md
---
title: 你好世界
date: 2026-02-06
category: 日常
tags: [随笔, 折腾]
top: false
---

这里开始写正文，支持 Markdown。
```

> `title/date/category/tags/top` 都是可选项，不写也能跑（会从文件名兜底）。

### 3）选择一种部署方式
- **最省事（推荐新手）**：用 GitHub Actions 先生成产物，再让 Vercel/CF Pages 托管（见下文“部署方案一”）
- **更干净（推荐强迫症）**：不要 Actions 回写产物，让 Vercel/CF Pages 在云端自己跑 `build.py`（见“部署方案二”）
- 如果你就想最简单：直接 GitHub Pages 也可以（见“部署到 GitHub Pages”）

---

## 写文章

### 1）文件名规则（推荐）
推荐用：

`YYYY-MM-DD-文章标题.md`

例如：

`2026-02-06-我今天把站又重构了.md`

好处：即使你不写 front matter，也能自动识别标题/日期。

### 2）Front Matter（可选，但推荐写）
放在文章最顶部：

```yaml
---
title: 文章标题
date: 2026-02-06
category: 分类名
tags: [标签1, 标签2]
top: true
---
```

字段说明：
- `title`：文章标题（不写则用文件名）
- `date`：日期（不写则尝试从文件名解析）
- `category`：分类（不写默认“默认”）
- `tags`：标签数组（可不写）
- `top`：是否置顶（`true/false`）

### 3）留言板（可选）
仓库自带逻辑支持留言板入口（菜单里通常会有“留言板”）：

- 新建 `posts/guestbook.md`
- 内容随便写（比如一段说明）
- 评论区通常依靠 Waline（见后文）

---

## 本地预览

### 方式 A：不构建，直接看首页（只看样式）
如果你只是想看 `index.html` 布局：

```bash
python3 -m http.server 8000
```

然后打开：`http://localhost:8000/`

> 注意：这时如果没有最新 `posts.json`，文章列表可能不完整。

### 方式 B：本地先构建再预览（推荐）
1）装依赖（只要一次）：

```bash
pip install pyyaml markdown
```

2）运行构建（建议把域名先写成 localhost）：

```bash
SITE_URL="http://localhost:8000" python3 build.py
```

3）启动本地静态服务器：

```bash
python3 -m http.server 8000
```

---

## 部署方案一：GitHub Actions 生成，平台只托管（推荐新手，省改动）

这一套最适合“我就想 push 文章就自动更新”的人：

- GitHub Actions 负责：
  - 跑 `build.py`
  - 把 `posts.json / sitemap.xml / p/` 提交回仓库
- Vercel / CF Pages 只负责“托管静态文件”（不需要构建）

### 你需要做的事情
1. 保留 `.github/workflows/build.yml`
2. 在 GitHub 开 Actions 写权限（非常关键）：
   - 仓库 **Settings → Actions → General → Workflow permissions**
   - 选择 **Read and write permissions**
3. 把 `build.yml` 里的 `SITE_URL` 改成你的站点域名（后文有位置）

然后你就可以：
- push `posts/**` → Actions 自动构建 → 平台自动部署

---

## 部署方案二：不用 Actions，让 Vercel/CF Pages 自己构建（更干净）

这一套适合“仓库里不想出现构建产物（p/ posts.json sitemap.xml）”的人：

- **不需要 `.github/workflows/build.yml`**
- 平台构建命令里跑 `python build.py`

注意：你这个项目构建产物在仓库根目录，所以平台的 **Output Directory** 要指向根目录（通常填 `.` 或留空，看平台要求）。

---

## 部署到 GitHub Pages

> 如果你用 Vercel/CF Pages，可以**跳过 GitHub Pages**（不用配 Pages）。

1）进入仓库：**Settings → Pages**  
2）Source 选：**Deploy from a branch**  
3）Branch 选：`main`  
4）Folder 选：`/(root)`  
5）保存后，等待 GitHub 给你一个访问地址

---

## 部署到 Vercel

### 方式 1（推荐配合“方案一”）：Vercel 只托管，不构建
1. 打开 Vercel → Add New → Project → 选择你的 GitHub 仓库
2. Framework 选 **Other**
3. Build Command：留空（或填 `echo "no build"`）
4. Output Directory：留空（默认根目录）
5. Deploy

### 方式 2（配合“方案二”）：Vercel 云端构建
在 Vercel 项目设置里填：
- Build Command：
  ```bash
  pip install pyyaml markdown && SITE_URL="https://你的域名" python3 build.py
  ```
- Output Directory：`.`（点，根目录）

---

## 部署到 Cloudflare Pages

### 方式 1（推荐配合“方案一”）：CF Pages 只托管
1. Cloudflare Dashboard → Pages → Create a project → Connect to Git
2. 选你的仓库
3. Build command：留空
4. Build output directory：留空（或填 `./`）
5. Deploy

### 方式 2（配合“方案二”）：CF Pages 云端构建
在构建设置里填：
- Build command：
  ```bash
  pip install pyyaml markdown && SITE_URL="https://你的域名" python3 build.py
  ```
- Build output directory：`./`（根目录）

---

## 绑定自定义域名

### Vercel / CF Pages（推荐）
平台里一般都有 “Domains” 页面：
1. 添加你的域名（例如 `blog.example.com`）
2. 按提示去你的 DNS 里加：
   - CNAME 到平台给的目标（Vercel/CF 会提示）
3. 开启 HTTPS（通常自动）

### GitHub Pages
如果你用 GitHub Pages：
1. Settings → Pages → Custom domain 填你的域名
2. DNS 按 GitHub 提示加记录
3. 建议勾选 **Enforce HTTPS**

---

## 构建脚本的 SITE_URL 需要在哪改？

你的 `build.py` 会用 `SITE_URL` 来生成：
- `sitemap.xml`
- 每篇文章页的 canonical / og:url 等

### 如果你用 GitHub Actions（方案一）
打开 `.github/workflows/build.yml`，找到这行：

```bash
SITE_URL='https://xn--7z0a.net' python3 build.py
```

把它改成你自己的域名，例如：

```bash
SITE_URL='https://blog.example.com' python3 build.py
```

---

## 评论系统 Waline 配置

在 `index.html` 里有类似这段（你可以搜索 `serverURL`）：

```js
Waline.init({
  el: '#waline',
  serverURL: 'https://waline.example.com/',
});
```

你需要做的事：
- 如果你有自己的 Waline 服务：把 `serverURL` 改成你自己的
- 如果你没有 Waline：可以先不管（评论区可能不显示或报错，但博客主体不受影响）

---

## 常见问题

### 1）Actions 构建失败：push 权限不足
现象：workflow 最后一步 `git push` 报错  
解决：
- 仓库 Settings → Actions → General
- Workflow permissions 设为 **Read and write permissions**

### 2）站点能打开但文章列表不更新
排查：
- 直接访问：`https://你的域名/posts.json` 看是否是最新内容
- 看平台部署日志是否成功

### 3）文章链接里有中文/空格，复制后偶尔打不开
你这个系统的 slug 策略是“尽量保留原文件名（含中文与空格）”，并且会生成兼容旧编码路径的跳转页。  
如果遇到客户端复制把空格改成 `+` 等情况：
- 尽量从文章页复制完整 URL
- 或把文件名中的空格改成 `-`（更稳）

---

## 许可证
按你的项目需要填写（可选）。
