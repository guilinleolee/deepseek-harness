# API 参数矩阵 · dsh-web-search-pro V0.1.8

> **来源**：上游 README § 工具 + § 平台与引擎 + § 配置。**本文件为天龙侧参考**，调用时仍由 DSH LLM 工具层发起。
> **版本绑定**：V0.1.8（2026-08-24 实装版本）

---

## 一、路由决策树（11 工具）

```
用户需求是什么?
│
├─ 通用网页搜索 ──► web_search_pro
│   ├─ 已知单一引擎 ──► engines=['exa'] 或 engines=['ddg']
│   ├─ 多引擎回退 ──► 不传 engines，按 settings.yaml 默认顺序
│   ├─ 多引擎并行融合 ──► engines=[...], multi=true 或 parallelEngines=true
│   └─ 强制刷新 ──► fresh=true
│
├─ 已知 URL 抓正文（1-2 个）──► web_fetch_pro
│   ├─ 静态页 ──► mode='jina' 或 mode='http'（默认）
│   ├─ JS 重 ──► mode='playwright'
│   └─ 需要截图 ──► web_snapshot
│
├─ 已知 URL 批量（1-100 个）──► web_exa_contents（需 EXA_API_KEY）
│
├─ 平台搜索 ──► web_platform_search
│   ├─ GitHub ──► platform='github', type='repos'|'code'|'issues'
│   ├─ 小红书/知乎/微博/豆瓣/贴吧/抖音/快手 ──► 需 login state
│   ├─ B站 ──► 走 bili-cli（外部依赖）
│   ├─ YouTube ──► 走 yt-dlp（外部依赖）
│   └─ RSS ──► platform='rss', url=...
│
├─ 页面快照（HTML + 可选 PNG）──► web_snapshot
│
├─ 持久历史 ──► web_history / web_search_stats
├─ 清缓存 ──► web_cache_clear
├─ 按站规则 ──► web_rule（list/upsert/remove）
├─ 后端状态 ──► web_backend_status
└─ 外部依赖管理 ──► web_deps（check/install）
```

---

## 二、11 工具参数矩阵

### 2.1 web_search_pro

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `query` | string | ✅ | — | 搜索关键词 |
| `engines` | string[] | ❌ | settings.yaml 默认 | 引擎列表：`seam`/`exa`/`ddg`/`bing`/`jina`/`github`/`bilibili`/`v2ex`/`youtube` |
| `exaType` | string | ❌ | `auto` | 仅 `exa` 引擎：`instant`/`fast`/`auto`/`deep-lite`/`deep`/`deep-reasoning` |
| `max_results` | number | ❌ | 8 | 1-20 |
| `fresh` | boolean | ❌ | false | 强制刷新（绕过缓存）|
| `category` | string | ❌ | — | Exa：`company`/`research paper`/`news`/`tweet`/`personal site` 等 |
| `includeDomains` | string[] | ❌ | — | Exa 白名单 |
| `excludeDomains` | string[] | ❌ | — | Exa 黑名单 |
| `startPublishedDate` | string | ❌ | — | Exa ISO 时间下界 |
| `endPublishedDate` | string | ❌ | — | Exa ISO 时间上界 |
| `multi` | boolean | ❌ | false | 多引擎并行融合 |

### 2.2 web_fetch_pro

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `url` | string | ✅ | — | 目标 URL |
| `mode` | string | ❌ | `jina` | `jina` / `http` / `playwright` |
| `maxChars` | number | ❌ | 50000 | 输出字符上限 |
| `persist` | boolean | ❌ | true | 是否落快照到 SQLite |

### 2.3 web_platform_search

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `platform` | string | ✅ | — | 平台名（见 §3 平台表）|
| `query` | string | ✅ | — | 搜索关键词 |
| `count` | number | ❌ | 8 | 1-20 |
| `url` | string | ❌ | — | RSS 专用：feed URL |
| `authProfile` | string | ❌ | — | 命名 AuthProfile（需登录态平台）|
| `rulePack` | string | ❌ | — | 命名 RulePack（站点增强）|

### 2.4 web_exa_contents

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `urls` | string[] | ✅ | — | 1-100 个 URL |

### 2.5 web_snapshot

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `url` | string | ✅ | — | 目标 URL |
| `screenshot` | boolean | ❌ | true | 是否生成 PNG |

### 2.6 web_history

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `kind` | string | ❌ | `all` | `search`/`fetch`/`platform`/`snapshot`/`all` |
| `query` | string | ❌ | — | 子串过滤 |
| `engine` | string | ❌ | — | 按引擎 ID 过滤 |
| `platform` | string | ❌ | — | 按平台过滤 |
| `limit` | number | ❌ | 20 | 1-200 |
| `replay` | string | ❌ | — | queryId 回放 |
| `export` | boolean | ❌ | false | 导出 JSON 文件 |

### 2.7 web_cache_clear

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `olderThanDays` | number | ❌ | — | 清除 N 天前 |
| `engine` | string | ❌ | — | 按引擎 |
| `queryId` | string | ❌ | — | 清除单条查询 |

### 2.8 web_search_stats

无参数。返回 SQLite 表计数 + 配置引擎 + top queries。

### 2.9 web_rule

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `action` | string | ✅ | — | `list`/`upsert`/`remove`/`export`/`import` |
| `hostname` | string | upsert/remove 必填 | — | 站点 hostname |
| `contentSelectors` | string | upsert 必填 | — | CSS 选择器（逗号分隔）|
| `removeSelectors` | string | ❌ | — | 要移除的元素选择器 |
| `rulesJson` | string | import 必填 | — | JSON 数组 |

### 2.10 web_backend_status

无参数。返回配置引擎 + 健康探测 + cooldown 状态。

### 2.11 web_deps

| 参数 | 类型 | 必填 | 默认 | 说明 |
|------|------|------|------|------|
| `action` | string | ✅ | — | `check` / `install` |
| `backend` | string | install 必填 | — | `bili` / `yt-dlp` / `agent-reach` / `mcporter` |
| `installer` | string | ❌ | — | `winget` / `choco` / `uv` / `pipx` / `pip` / `npm` |

---

## 三、19 平台映射表

| platform 字符串 | 后端 | 账号态 | 外部依赖 | 备注 |
|-----------------|------|--------|----------|------|
| `github` | GitHub REST API | ❌ | ❌ | `$GITHUB_TOKEN` 提升限额并解锁 code 搜索 |
| `bilibili` | bili-cli | ❌ | ✅ bili-cli | 无需登录的搜索/视频信息 |
| `youtube` | yt-dlp | ❌ | ✅ yt-dlp | 视频元信息/字幕 |
| `v2ex` | 公开 REST | ❌ | ❌ | V2EX 热门/节点 |
| `rss` | 直接抓取 | ❌ | ❌ | 需 `url` 参数 |
| `xiaohongshu` | OpenCLI / Playwright | ✅ 需 save-login | ✅ opencli | 小红书图文 |
| `twitter` | OpenCLI | ✅ 需 Chrome 扩展 | ✅ opencli | 推文/用户 |
| `reddit` | OpenCLI | ✅ 需 Chrome 扩展 | ✅ opencli | 帖子/子版块 |
| `instagram` | OpenCLI | ✅ 需 Chrome 扩展 | ✅ opencli | 帖子/用户 |
| `facebook` | OpenCLI | ✅ 需 Chrome 扩展 | ✅ opencli | 主页/群组 |
| `zhihu` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 知乎问答 |
| `weibo` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 微博搜索/热门 |
| `douban` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 豆瓣电影/书评 |
| `tieba` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 百度贴吧 |
| `douyin` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 抖音 |
| `kuaishou` | Playwright + save-login | ✅ 需 save-login | ✅ dsh-browser | 快手 |
| `bilibili_dynamic` | OpenCLI | ✅ | ✅ opencli | B 站动态（账号态）|
| `xiaoyuzhou` | agent-reach | ❌ | ✅ agent-reach | 小宇宙播客（转写）|
| `linkedin` | agent-reach | ✅ 需 cookie | ✅ agent-reach | 领英 |

> **雪球 / 微信公众号**：未在本表——雪球自选股、微信文章均需账号态 + 阿里云 WAF 挑战，**两端都无解**（已实测）。

---

## 四、缓存指纹规则（重要：避免误清缓存）

不同选项组合使用不同缓存指纹：

| 维度 | 何时触发新缓存条目 |
|------|--------------------|
| `query` | ✅ 必触发 |
| `engines` 列表 | ✅ 触发（顺序也算）|
| `multi` 模式 | ✅ 触发（单 vs 多）|
| `exaType` | ✅ 触发（仅 Exa）|
| `category` | ✅ 触发（仅 Exa）|
| `includeDomains` / `excludeDomains` | ✅ 触发（仅 Exa）|
| `startPublishedDate` / `endPublishedDate` | ✅ 触发（仅 Exa）|
| `max_results` | ✅ 触发 |
| `fresh=true` | ❌ 强制重算不读缓存 |

---

## 五、错误码契约

| 错误 | 触发场景 | LLM 处置 |
|------|---------|---------|
| 429 | API 限流 | 自动退避 + 短时冷却；改用其他引擎 |
| 503 | 服务不可用 | 同上 |
| `backend_not_ready` | web_backend_status 检测未通过 | 提示用户装外部 CLI |
| `authProfile_required` | 平台需账号态 | 提示用户跑 save-login.mjs |
| `dsh_profile_not_found` | 当前不是 DSH 环境 | 回退到 anysearch / agent-reach |

---

## 六、限制与边界

| 项 | 限制 |
|---|---|
| web_exa_contents | 1-100 URL / 每次 |
| web_search_pro max_results | 1-20 |
| web_history limit | 1-200 |
| web_fetch_pro maxChars | 1000-50000 |
| web_snapshot | 单页 HTML + 可选 PNG |
| web_rule source/result caps | 用户脚本 64KB 上限 |
| browser_script | 64KB 上限 + `@grant none` 强制 + `@match` 必填 |
| 自动化模式 | 4 档（read-only/standard/autonomous/unrestricted）|
| 持久化 | SQLite + LRU 双层；TTL 默认 3600s |

---

## 七、上游参考

- 上游 README § 工具：https://github.com/anweat/dsh-web-search-pro#工具11-个
- 上游 README § 平台与引擎：https://github.com/anweat/dsh-web-search-pro#平台与引擎
- 上游 README § 外部依赖：https://github.com/anweat/dsh-web-search-pro#外部依赖按需
- 上游 package.json：https://github.com/anweat/dsh-web-search-pro/blob/master/package.json
