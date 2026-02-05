# Higan-Static 博客系统

这是一个轻量静态博客系统：你只需要把 Markdown 文章放进 `posts/`，其余全部由 **GitHub Actions（actions bot）自动构建**完成。

---

## 目录结构

```
.
├─ index.html                  # 前端首页（SPA）
├─ build.py                    # 构建脚本（由 Actions 调用）
├─ posts/                      # 文章目录（你只需要管这里）
├─ p/                          # 构建产物：每篇文章独立页面（自动生成）
├─ posts.json                  # 构建产物：首页文章索引（自动生成）
├─ sitemap.xml                 # 构建产物：站点地图（自动生成）
└─ .github/workflows/build.yml # Actions 工作流（自动构建入口）
```

> 你日常只需要改 `posts/` 里的 Markdown。`p/`、`posts.json`、`sitemap.xml` 都是自动生成的。

---

## 唯一构建方式：GitHub Actions（actions bot）

本项目**只支持一种构建方式**：当你更新 `posts/` 下的文章后，GitHub Actions 会自动运行：

- 安装依赖（`pyyaml`、`markdown`）
- 执行 `build.py`
- 自动生成/更新：
  - `posts.json`
  - `sitemap.xml`
  - `p/<slug>/index.html`
- 由 actions bot 自动提交这些构建产物

### 需要做的唯一一次设置：允许 Actions 写入仓库

进入仓库的设置页面，找到 Actions 的权限设置，把 **Workflow permissions** 设为 **Read and write**（允许 actions bot 推送构建产物）。

> 如果不打开写入权限，构建会跑完，但最后一步“提交生成文件”会失败。

---

## 写文章（两种方式）

你可以任选其一：

### 方式 A：先在本地写好 Markdown，再复制到 `posts/`

1. 在本地新建一个 `.md` 文件
2. 按下面的命名规则命名
3. 把文件内容复制到 GitHub 仓库的 `posts/` 目录（网页上传/拖拽都可以）
4. 提交后，Actions 会自动构建并更新站点

### 方式 B：直接在 GitHub 网页里写

1. 打开仓库的 `posts/` 目录
2. 新建文件（或编辑已有文件）
3. 粘贴 Markdown 内容并保存
4. 提交后，Actions 会自动构建并更新站点

---

## 文章命名规则

### 普通文章（推荐）
文件名建议使用：

`YYYY-MM-DD-文章标题.md`

例子：
- `2026-02-06-你好世界.md`
- `2026-02-10-我把站又重构了.md`

> 文件名中的日期会用于默认排序与展示（如果你没写 `date`）。

---

## 文章头部 Front Matter

每篇文章可以在最顶部写一段 YAML（可选，但强烈推荐）：

```yaml
---
title: 文章标题
date: 2026-02-06
category: 分类名
tags: [标签1, 标签2]
top: 10
---
```

字段说明：
- `title`：文章标题
- `date`：文章日期（建议写，格式 `YYYY-MM-DD`）
- `category`：分类
- `tags`：标签（可选）
- `top`：**文章排名**（数字越大越靠上）

> `top` 不是 true/false，而是**数字排名**：例如 `top: 100` 会比 `top: 10` 更靠前。

---

## 「说说」的写法（特殊规则）

「说说」是一种特殊分类，推荐按下面的固定格式来写。

### 文件名
必须是：

`YYYY-MM-DD-说说.md`

例如：
- `2026-02-06-说说.md`

### 内容格式（最上面固定这段）
说说文章的开头建议固定为：

```yaml
---
title: 说说
date: YYYY-MM-DD
category: 说说
---
```

### 然后下面直接写正文
例如：

```md
---
title: 说说
date: 2026-02-06
category: 说说
---

今天又在折腾 VPS，结果把 DNS 搞炸了……
```

---

## 常见问题

### 1）我更新了文章，但站点没更新
先去 Actions 页面看最新一次构建是否成功（绿色 ✅）。如果失败，最常见原因是：

- 没打开 “Read and write permissions”（actions bot 无法提交构建产物）

### 2）文章排序不对
检查文章顶部是否写了 `top`：

- `top` 数字越大越靠上
- 不写 `top` 的文章会按默认规则排序（通常按时间）

---

## License
（按你的选择填写，例如 MIT）
