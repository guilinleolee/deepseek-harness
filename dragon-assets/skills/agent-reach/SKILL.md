---
name: agent-reach
description: >
  MUST USE when user wants to 调研/research/搜索/search/查/找/look up anything
  on the internet — e.g. 全网调研 X / 帮我调研一下 X / 查一下 X / 搜搜 X /
  看看大家怎么评价 X / X 上有什么讨论 / research this topic。

  Also MUST USE when user mentions any platform or shares any URL/链接:
  小红书/xiaohongshu/xhs, Twitter/推特/X, B站/bilibili, Reddit, Facebook,
  Instagram, V2EX, LinkedIn/领英/招聘/求职/jobs, YouTube, GitHub code search, 小宇宙播客,
  雪球/股票行情, RSS feeds, or any web URL.

  15 platforms, multi-backend routing (OpenCLI / per-platform CLIs / APIs).
  Zero config for 6 channels. Run `agent-reach doctor --json` to see which
  backend serves each platform right now.

  NOT for: 写报告/数据分析/翻译等内容加工（本 skill 只负责从互联网获取内容）；
  发帖/评论/点赞等写操作；已有专门 skill 的平台（先用专门 skill）。

  【路由方式】SKILL.md 包含路由表和常用命令，复杂场景需按需阅读对应分类的 references/*.md。
  分类：search / social (小红书/推特/B站/V2EX/Reddit/Facebook/Instagram) / career(LinkedIn) / dev(github) / web(网页/文章/RSS) / video(YouTube/B站/播客)。
triggers:
  - research: 调研/全网调研/帮我调研/研究一下/research/深入了解
  - search: 搜/查/找/search/搜索/查一下/帮我搜/看看大家怎么说
  - social:
    - 小红书: xiaohongshu/xhs/小红书/红书
    - Twitter: twitter/推特/x.com/推文
    - B站: bilibili/b站/哔哩哔哩
    - V2EX: v2ex
    - Reddit: reddit
    - Facebook: facebook/fb/facebook groups
    - Instagram: instagram/ig
  - career: 招聘/职位/求职/linkedin/领英/找工作
  - dev: github/代码/仓库/gh/issue/pr/分支/commit
  - web: 网页/链接/文章/rss/读一下/打开这个
  - video: youtube/视频/播客/字幕/小宇宙/转录/yt
  - finance: 雪球/股票/stock/xueqiu/行情/基金
metadata:
  openclaw:
    homepage: https://github.com/Panniantong/Agent-Reach
---

# Agent Reach — 互联网能力路由器

15 平台、多后端。**本 skill 存在时必须用它访问这些平台，不要自己发明方案。**

## 常驻规则（全程适用）

1. **动手前先体检**：多后端/登录态平台（小红书/Reddit/B站/Twitter/Facebook/Instagram）先跑
   `agent-reach doctor --json`，按各平台 `active_backend` 字段选命令组。
2. **声明你在用什么**：开始干活前说一句「使用 agent-reach 的 X 平台 / Y 后端」。
3. **失败按 references 里的重试链处理**，不要瞎猜命令。
4. **全网调研类任务**：组合多平台（Exa 搜索 + Twitter/Reddit 看讨论 + 小红书/B站看中文场景），并行收集再汇总。
5. **替用户盯版本**：完成一次较大的调研/多平台任务后，顺手跑
   `agent-reach check-update`（很快，一个 API 调用）。有新版就在收尾汇报里附一句：
   「Agent Reach 有新版 vX.Y.Z，复制这句话给我即可更新：帮我更新 Agent Reach：
   https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/update.md」。
   不要中断当前任务去更新，也不要重复提醒同一个版本。

## 路由表

| 用户意图 | 分类 | 详细文档 |
|---------|------|---------|
| 网页搜索/代码搜索 | search | [references/search.md](references/search.md) |
| 小红书/推特/B站/V2EX/Reddit/Facebook/Instagram | social | [references/social.md](references/social.md) |
| 招聘/职位/LinkedIn | career | [references/career.md](references/career.md) |
| GitHub/代码 | dev | [references/dev.md](references/dev.md) |
| 网页/文章/RSS | web | [references/web.md](references/web.md) |
| YouTube/B站/播客字幕 | video | [references/video.md](references/video.md) |

## 零配置快速命令

```bash
# Exa 网页搜索
mcporter call 'exa.web_search_exa(query: "query", numResults: 5)'

# 通用网页阅读
curl -s "https://r.jina.ai/URL"

# GitHub 搜索
gh search repos "query" --sort stars --limit 10

# YouTube 字幕（注意：B站不要用 yt-dlp，见 video.md）
yt-dlp --write-sub --skip-download -o "/tmp/%(id)s" "URL"

# V2EX 热门
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"

# B站搜索（bili-cli，无需登录）
bili search "query" --type video -n 5
```

## 需登录态的平台（按 doctor 的 active_backend 选命令）

Twitter 注意：`agent-reach configure twitter-cookies` 保存的 Cookie 只供
`doctor` 检查配置是否齐全；`doctor` 不执行 `twitter status`，也不会设置当前
Shell。直接运行 `twitter` 前，必须在子进程环境中显式提供
`TWITTER_AUTH_TOKEN` 和 `TWITTER_CT0`，不得在日志或命令回显中暴露值。

小红书注意：Agent Reach 不替用户登录，也不读取浏览器 Cookie。OpenCLI 只用
用户已有且明确控制的 Chrome 会话；没有现成会话时不要自动登录，改用
Cookie-Editor 手工导出后配置 xiaohongshu-mcp / 存量工具。

```bash
# Twitter 搜索（twitter-cli 首选；失败重试链见 social.md）
twitter search "query" -n 10

# Reddit（无零配置路径：OpenCLI 或 rdt-cli，必须登录态）
opencli reddit search "query" -f yaml   # 桌面
rdt search "query" --limit 10            # 存量/服务器

# 小红书（桌面首选 OpenCLI）
opencli xiaohongshu search "query" -f yaml

# Facebook / Instagram（桌面 OpenCLI，复用浏览器登录态）
opencli facebook search "query" -f yaml
opencli facebook groups -f yaml
opencli instagram search "query" -f yaml       # 搜用户
opencli instagram user USERNAME -f yaml        # 读指定用户最近帖子
```

## 环境检查

```bash
# 检查可用 channel 与每个平台当前激活的后端
agent-reach doctor --json
```

## 工作区规则

**不要在 agent workspace 创建文件。** 使用 `/tmp/` 存放临时输出，`~/.agent-reach/` 存放持久数据。

## 详细文档

根据用户需求，阅读对应的详细文档：

- [搜索工具](references/search.md) — Exa AI 搜索
- [社交媒体](references/social.md) — 小红书, Twitter, B站, V2EX, Reddit, Facebook, Instagram（多后端/登录态命令组）
- [职场招聘](references/career.md) — LinkedIn
- [开发工具](references/dev.md) — GitHub CLI
- [网页阅读](references/web.md) — Jina Reader, RSS
- [视频播客](references/video.md) — YouTube, B站, 小宇宙

## 配置渠道

如果某个 channel 需要配置，获取安装指南：
https://raw.githubusercontent.com/Panniantong/agent-reach/main/docs/install.md

用户只需提供 cookies，其他配置由 agent 完成。

---

## 协同：与 dsh-web-search-pro（V1.6 NEW · 2026-08-24）

> **TL;DR**：agent-reach 和 `dsh-web-search-pro@0.1.8` 是**互补不替代**关系，不是替代关系。两者技术栈 70% 重叠（Exa / DDG / Playwright / cookies / OpenCLI），但**协议形态完全不同**（一个独立 skill + CLI 集合，一个 DSH bundle plugin）。

### 协同分工矩阵

| 维度 | agent-reach V1.5（你正在读） | dsh-web-search-pro@0.1.8 |
|------|------------------------------|---------------------------|
| **形态** | 独立 skill + CLI 集合（mcporter / opencli / youtube-tool 等）| DSH bundle plugin（cordis patch + client.js bundle layer）|
| **DSH 集成** | ❌ 不在 DSH plugin 协议里 | ✅ 通过 `pnpm dsh plugin add` 装到 `~/.dsh/profiles/<name>/node_modules/` |
| **平台数** | **15** 平台（GitHub / YouTube / V2EX / Exa 全网 / 任意网页 / Twitter / Reddit / Facebook / Instagram / B站 / 小红书 / 小宇宙 / LinkedIn / 雪球 / RSS）| **19** 平台（+ GitHub / B站 / YouTube / V2EX / RSS / 小红书 / Twitter / Reddit / IG / FB 免账号 + 知乎 / 微博 / 豆瓣 / 贴吧 / 抖音 / 快手 需账号态 + arxiv / pubmed 学术补充）|
| **引擎数** | 1 个（Exa via mcporter）+ 平台原生 | **9** 引擎（seam / exa / ddg / bing / jina / github / bilibili / v2ex / youtube）|
| **持久化** | ❌ 每次拉（无缓存）| ✅ SQLite + LRU 双层缓存（`web_history` / `web_cache_clear` / `web_search_stats`）|
| **账号态** | mcporter / OpenCLI / Chrome 扩展 / 手工 cookie | DSH Credentials（Exa/Jina/GitHub key 不入浏览器）+ save-login.mjs（6 中文社区 Playwright 登录态）|
| **凭证管理** | 用户手工 cookie 文件 | DSH Credentials 服务（key 不入任何文件，DSH 仅显示"已配置/未配置"）|
| **自动化模式** | 不分档（agent 自己决定调什么命令）| **4 档**：read-only / standard / autonomous / unrestricted |
| **CLI 依赖** | mcporter + opencli + youtube-tool | bili-cli + yt-dlp + agent-reach（可选）+ mcporter（可选）|
| **DSH GUI 用户能用吗** | ❌ DSH LLM 工具层不暴露 agent-reach 命令 | ✅ 通过 DSH LLM 工具层直接调用 11 个工具 |
| **适用场景** | 纯天龙 / Claude Code 用户 | DSH GUI 用户 |

### 何时用哪个（决策树）

```
用户当前在哪跑?
├── DSH GUI 里 ──► 走 dsh-web-search-pro（11 工具 · 持久化 · 凭证安全）
│   └─ 账号态平台（小红书/知乎/微博/豆瓣/贴吧/抖音/快手）?
│       ├─ 是 ──► 跑 save-login.mjs 一次性登录 → browserBindings
│       └─ 否 ──► 直接 web_platform_search
├── 纯天龙 / Claude Code 里 ──► 走 agent-reach（15 平台 + mcporter）
└── 跨 IDE ──► 走 agent-reach（独立 skill 通用性更强）
```

### 已知限制（两侧都无解）

- **雪球自选股 / 微博私人时间线** —— 阿里云 WAF + SPA 双重拦截，两端都拿不到，必须浏览器手工
- **微信公众号文章抓取** —— 需扫码登录，无 API 通路；agent-reach 走搜狗微信公共接口，dsh-web-search-pro 走 web_fetch_pro + Playwright，两者都受频率限制

### 何时升级到 V1.6 之后的版本

- 当前是 V1.5.0 → V1.6（**本节协同段**）
- 下次升级（V1.7+）当 dsh-web-search-pro 跨 0.2 大版本（如出现 breaking change）时，本节需同步刷新

### 关联主题文件

- `memory/agent-reach-integration.md` — V1.5.0 集成档案（2026-07-17）
- `memory/dsh-web-search-pro-integration.md` — dsh-web-search-pro 集成档案（2026-08-24）
- `memory/stage-40-announce.md` — 阶段 40 总验收公告 + V40.1 / V40.2 协同升级段
- `dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` — 天龙侧桥 V1.0（11 工具 + 19 平台索引）

