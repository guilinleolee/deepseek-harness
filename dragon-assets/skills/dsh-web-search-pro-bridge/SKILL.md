---
name: dsh-web-search-pro-bridge
description: >
  Use when the runtime is DSH (DeepSeek Harness) and `dsh-web-search-pro@^0.1.8` +
  `@anweat/dsh-browser@^0.1.8` are installed in the active web profile — prefer
  their 11-tool bridge over the bundled CLI for routine web search / fetch /
  platform / snapshot work. This is the path of least surprise for DSH GUI users:
  single CLI, persistent SQLite+LRU cache, 19 platforms, 9 engines, userscript-style
  per-site extraction, Playwright rendering fallback.

  ALSO use as the canonical wrapper when you need to write or read from
  `~/.dsh/profiles/<name>/settings.yaml` under the `web-search-pro:` section, or
  reference upstream docs (anweat/dsh-web-search-pro MIT, 37 ⭐, v0.1.8).

  NOT a substitute for `agent-reach` (which carries account-bound platforms via
  cookie/Chrome-extension bridges), `anysearch` (which is the multi-mirror CLI for
  non-DSH environments), or `_tikhub/*` (paid-API deep data).

version: 1.0.0
license: MIT
upstream:
  repo: https://github.com/anweat/dsh-web-search-pro
  license: MIT (1088 B verbatim in LICENSE)
  stars: 37
  default_branch: master
  mirror_in_dsh_web_profile: ~/.dsh/profiles/web/node_modules/dsh-web-search-pro/
modified_by: dragon-engine / 2026-08-24
---

# dsh-web-search-pro-bridge · V1.0（天龙侧桥 · 阶段 40）

> **天龙侧桥**：DSH 主仓 web profile 已真实安装 `dsh-web-search-pro@0.1.8` + `@anweat/dsh-browser@0.1.8`。本 SKILL 不是镜像，是**天龙侧的引用/索引/包装层**——告诉 LLM 何时调用 DSH 真装的后端、如何调、参数怎么传、结果怎么呈现，以及与天龙既有 `agent-reach` / `anysearch` / `multi-search-engine` 的协同边界。

---

## 一、能力矩阵（11 工具 + 19 平台 + 9 引擎）

### 1.1 11 工具（按使用频度排序）

| 工具 | 作用 | 等价天龙 skill |
|---|---|---|
| `web_search_pro` | 多引擎 RRF 融合 + SQLite/LRU 双层缓存 + 历史 | `anysearch` / `multi-search-engine` |
| `web_fetch_pro` | Jina → HTTP+规则抽取 → Playwright 三级回退 + 快照缓存 | `web-fetch` / `defuddle` |
| `web_platform_search` | **19 平台** 搜索：GitHub/B站/YouTube/V2EX/小红书/Twitter/Reddit/IG/FB/RSS + 知乎/微博/豆瓣/贴吧/抖音/快手 | `agent-reach` / `_tikhub/*` / `trendradar-core` / `last30days` |
| `web_snapshot` | Playwright HTML + 文本落盘 + 可选 PNG | `playwright-skill` |
| `web_history` / `web_cache_clear` / `web_search_stats` | 持久历史 / 清缓存 / 存储统计 | —（天龙侧无对应）|
| `web_rule` | 持久化按站提取规则（userscript 风格，list/upsert/remove）| —（天龙侧无对应）|
| `web_exa_contents` | Exa `/contents` 批量正文抓取（1-100 URL）| `defuddle`（弱等价）|
| `web_backend_status` | 无副作用后端探测 + CLI 状态 | —（天龙侧无对应）|
| `web_deps` | 检测/安装搜索后端外部依赖（bili / yt-dlp / agent-reach / mcporter）| —（天龙侧无对应）|

### 1.2 9 引擎

| 引擎 | 备注 |
|---|---|
| `seam` | DSH ctx.web 原生（任何 DSH 用户默认可用） |
| `exa` | 高级筛选（`exaType` / 域名 include/exclude / 时间范围 / category）—— 需要 `EXA_API_KEY` |
| `ddg` | 默认匿名可用（推荐首选） |
| `bing` | 匿名可用 |
| `jina` | 需要 `JINA_API_KEY` 提升速率 |
| `github` | REST API，匿名受限，`$GITHUB_TOKEN` 提升限额并解锁代码搜索 |
| `bilibili` | 走 bili-cli（外部依赖） |
| `v2ex` | 公开 REST API |
| `youtube` | 走 yt-dlp（外部依赖） |

**默认顺序**：`ddg, bing, exa, seam, jina`（免费优先），失败自动回退；`multi` 并行融合。

### 1.3 19 平台

| 分类 | 平台 |
|---|---|
| **免账号态** | GitHub / B站 / YouTube / V2EX / RSS / Reddit / Twitter / Instagram / Facebook |
| **需账号态（DSH 内置 Playwright 驱动登录态浏览器）** | 小红书 / 知乎 / 微博 / 豆瓣 / 贴吧 / 抖音 / 快手 |

---

## 二、安装（DSH 主仓 web profile）

```bash
# cwd = D:\deepseek-harness (DSH 主仓根)
pnpm dsh plugin --profile web add @anweat/dsh-browser@^0.1.8 dsh-web-search-pro@^0.1.8
# 退出码 0
# 重启 web profile（profile 关闭 HMR，仅刷新网页不会重扫 client.js）
```

**安装后必须做的 3 步验证**（README L37-39）：

1. `browser_status` —— 确认 OpenCLI / Playwright / automationMode / usagePolicy 就绪
2. `web_backend_status` —— 确认 9 引擎 + 19 平台 + 4 个外部 CLI 就绪
3. 设置 → 插件 → 插件配置 —— 确认"Web Search Pro"和"浏览器自动化"两张卡片都加载

**前置条件**：

| 项 | 要求 |
|---|---|
| Node | `^22.19 \|\| >=24` |
| pnpm | `11.7.0` |
| 外部 CLI | `bili-cli` / `yt-dlp` / `agent-reach` / `mcporter`（用 `web_deps` 工具安装） |
| Playwright | 由 `@anweat/dsh-browser` 内置；缺 Chromium 时跑 `browser_install` |

---

## 三、何时用本桥（决策树）

```
用户在 DSH GUI 里?
├── 是 ──► 走 dsh-web-search-pro（本 SKILL 默认路由）
│           ├─ 需要账号态平台（小红书/知乎/...）?
│           │   ├─ 是 ──► 跑 save-login.mjs 一次性登录 → 走 browserBindings
│           │   └─ 否 ──► 直接 web_platform_search
│           ├─ 需要 Exa 高级筛选?
│           │   └─ 是 ──► web_search_pro(query, engines=['exa'], exaType=..., ...)
│           └─ 需要 30 天趋势调研?
│               └─ 是 ──► web_search_pro(query, since='30d ago')
└── 否（纯天龙 / Claude Code）──► 走 anysearch V3.1 / agent-reach / multi-search-engine
```

---

## 四、典型调用示例（11 工具）

### 4.1 web_search_pro（最常用）

```bash
# 默认（匿名档，多引擎自动回退）
dsh-web-search-pro web_search_pro '{"query":"DeepSeek Harness community feedback","fresh":false,"max_results":8}'

# 强制 Exa 高级筛选
dsh-web-search-pro web_search_pro '{
  "query":"AI hardware startups 2026",
  "engines":["exa"],
  "exaType":"deep",
  "category":"startup",
  "startPublishedDate":"2026-01-01T00:00:00Z",
  "max_results":5
}'

# 多引擎并行融合
dsh-web-search-pro web_search_pro '{"query":"a-stock data","engines":["ddg","bing","exa","seam","jina"],"multi":true}'
```

### 4.2 web_platform_search

```bash
# 小红书（需 login state）
dsh-web-search-pro web_platform_search '{"platform":"xiaohongshu","query":"咖啡测评","limit":10}'

# GitHub
dsh-web-search-pro web_platform_search '{"platform":"github","query":"dsh-browser","type":"repos","limit":5}'

# B站
dsh-web-search-pro web_platform_search '{"platform":"bilibili","query":"天龙引擎","type":"video","limit":8}'
```

### 4.3 web_fetch_pro（已知 URL 抓正文）

```bash
# 默认 Jina 优先
dsh-web-search-pro web_fetch_pro '{"url":"https://github.com/anweat/dsh-web-search-pro"}'

# 强制 Playwright 渲染
dsh-web-search-pro web_fetch_pro '{"url":"https://example.com","mode":"playwright"}'
```

### 4.4 web_exa_contents（Exa 批量抓正文）

```bash
dsh-web-search-pro web_exa_contents '{"urls":["https://example.com/a","https://example.com/b"]}'
```

### 4.5 web_snapshot（HTML + PNG）

```bash
# HTML + PNG
dsh-web-search-pro web_snapshot '{"url":"https://example.com","screenshot":true}'
# 仅 HTML（screenshot=false 时不生成 PNG，节省带宽）
dsh-web-search-pro web_snapshot '{"url":"https://example.com","screenshot":false}'
```

### 4.6 web_history / web_cache_clear / web_search_stats

```bash
# 看历史
dsh-web-search-pro web_history '{"kind":"search","limit":20}'

# 清指定查询缓存
dsh-web-search-pro web_cache_clear '{"queryId":"q-2026-08-24-001"}'

# 看存储统计
dsh-web-search-pro web_search_stats '{}'
```

### 4.7 web_rule（持久化按站规则）

```bash
# 列出所有规则
dsh-web-search-pro web_rule '{"action":"list"}'

# 新增一条知乎规则
dsh-web-search-pro web_rule '{
  "action":"upsert",
  "hostname":"zhihu.com",
  "contentSelectors":[".SearchResult-Card",".ContentItem-title"],
  "removeSelectors":[".TopbarMain"]
}'

# 删除
dsh-web-search-pro web_rule '{"action":"remove","hostname":"example.com"}'
```

### 4.8 web_backend_status / web_deps（诊断）

```bash
# 看后端是否 ready
dsh-web-search-pro web_backend_status '{}'

# 检测外部 CLI 依赖
dsh-web-search-pro web_deps '{"action":"check"}'
# 安装
dsh-web-search-pro web_deps '{"action":"install","backend":"yt-dlp","installer":"pipx"}'
```

---

## 五、配置（三层，越靠前越日常）

### 5.1 面板（GUI）

设置 → 插件 → 插件配置 → Web Search Pro
- Exa/Jina/GitHub 密钥走 DSH Credentials（面板只显示"已配置/未配置"，不读明文）
- platformRules / customPlatforms / browserBindings / Playwright 用 JSON 对象编辑器
- 浏览器审批自由度由 `@anweat/dsh-browser.automationMode` 管
- `allowProxyFakeIp` 仅用于 Clash/TUN fake-IP DNS 环境

### 5.2 `~/.dsh/settings.yaml`（热重载）

```yaml
web-search-pro:
  exaApiKeyEnv: EXA_API_KEY      # 推荐：运行环境或凭据服务
  jinaApiKeyEnv: JINA_API_KEY
  engines: [ddg, bing, exa, seam, jina]
  parallelEngines: false
  ttlSeconds: 3600
  searchMaxResults: 8
  browserBindings:
    zhihu: { authProfile: china-community }
    weibo: { authProfile: china-community }
  platformRules:
    zhihu:
      item: '.SearchResult-Card'
      title: '.ContentItem-title'
      link: '.ContentItem-title a'
      text: '.Highlight'
  customPlatforms:
    mybili:
      name: '我的B站'
      url: 'https://search.bilibili.com/all?keyword={query}'
      item: '.bili-video-card'
      title: '.bili-video-card__info--tit'
      link: 'a'
```

### 5.3 cordis patch + 环境变量

- `cordis.yml` 部署级默认值（见上游 `cordis.patch.yml`）
- `$EXA_API_KEY` / `$JINA_API_KEY` / `$GITHUB_TOKEN` 环境变量

---

## 六、自动化模式（4 档，与 dsh-browser 一致）

| 模式 | 隐藏/拒绝 | 一次性审批 | 直通 |
|------|-----------|-----------|------|
| `read-only` | ✅ 隐藏或拒绝所有 web 写操作 | — | — |
| `standard`（默认）| — | ✅ 交互/写 Recipe/外部脚本/OpenCLI/缓存规则变更/安装 | — |
| `autonomous` | — | 仅安装/外部脚本/通用 OpenCLI | ✅ 页面交互/写 Recipe/本地缓存规则变更 |
| `unrestricted`（隔离测试 profile）| — | — | ✅ 全部 |

**所有模式仍保留**：域名、参数、大小、步骤上限校验 + dsh-browser 调用缓冲 + 退避 + 爬取预算。

---

## 七、协同矩阵（不替代天龙既有栈）

| 场景 | 首选 | 备选 | 不适用 |
|------|------|------|--------|
| DSH GUI 用户做调研 | **dsh-web-search-pro（本 SKILL）** | agent-reach（账号态）| — |
| 纯天龙 / Claude Code 用户做调研 | agent-reach | anysearch V3.1 | multi-search-engine（无 key） |
| 30 天趋势调研 | last30days | dsh-web-search-pro `since` | — |
| AI 资讯 | aihot | dsh-web-search-pro `category=ai-models` | — |
| 付费深度数据 | _tikhub/* | — | — |
| 热点聚合 | trendradar-core | dsh-web-search-pro `web_platform_search` | — |
| 中文社区登录态 | dsh-web-search-pro + save-login.mjs | agent-reach（OpenCLI）| — |
| 雪球自选股 / 微博时间线（账号态） | ❌（两端都无解）| ❌ | 浏览器手工 |
| 大规模爬虫 | scrapy / scrapling | web-scraping-scrapling | — |

### 7.1 与 agent-reach 的明确分工（关键）

| 维度 | dsh-web-search-pro | agent-reach |
|------|---------------------|-------------|
| 形态 | DSH bundle plugin | 独立 skill + CLI 集合 |
| 平台数 | **19** | **15** |
| 持久化 | SQLite + LRU（开箱即用）| 无（每次拉）|
| 账号态 | DSH 内置 Playwright + save-login.mjs | mcporter / OpenCLI / Chrome 扩展 |
| 引擎 | 9 个（含 Exa/Seam/Jina）| 1 个（Exa via mcporter）+ 平台原生 |
| 凭证管理 | DSH Credentials（不入浏览器）| 用户手工（cookie 文件）|
| 适用人群 | DSH GUI 用户 | 纯天龙 / Claude Code 用户 |

### 7.2 与 anysearch V3.1 的协同（阶段 40.1 待做）

**anysearch V3.0.1 → V3.1 升级**：在 §Recommended Entry Point 加探测段——"If the runtime is DSH and `dsh-web-search-pro@^0.1.8` is installed in the active profile, prefer its 11-tool bridge over the bundled CLI"。anysearch 的 4 镜像 CLI 保留作为"无 DSH 环境 fallback"。

---

## 八、合规边界（MIT 红线）

- **LICENSE 原文件必须保留**：`dragon-engine/skills/dsh-web-search-pro-bridge/LICENSE`（1088 B verbatim 实拉确认）
- **版权声明必须保留**：`dragon-engine/skills/dsh-web-search-pro-bridge/NOTICE`，含 "Modified by dragon-engine / 2026-08-24" 段
- **Trademark**：SKILL.md 不得用"dsh-web-search-pro 官方"等字样，仅"Powered by anweat/dsh-web-search-pro"
- **数据源合规**（非上游协议，是第三方 API）：mootdx / 腾讯 / 新浪 / 东财 / 知乎 / 微博 / 雪球 / 抖音 等按上游 README § 平台与引擎 + § 中文社区平台登录态 合规边界

---

## 九、DON'T 护栏

1. ❌ 不要把 DSH `web-search-pro` 当成"装了就全通"——它需要 Exa/Jina key 才能用高级筛选，需要 save-login.mjs 才能用 6 中文社区
2. ❌ 不要在无 DSH 环境（纯 Claude Code / 纯 IDE）调用本 SKILL——会报 DSH profile 不存在，回退到 anysearch V3.1 / agent-reach
3. ❌ 不要在 `standard` 模式下批量爬取——会触发一次性审批 + 429/503 退避
4. ❌ 不要把 storageState JSON 上传仓库或分享——含登录凭据
5. ❌ 不要直接覆盖 `~/.dsh/profiles/web/cordis.yml`——它由 `pnpm dsh plugin` 自动管理
6. ❌ 不要绕过 web profile 重启——web profile 关闭 HMR，仅刷新网页不会重扫 `client.js`
7. ❌ 不要把 dsh-web-search-pro 用于"必须登录才能看"的内容（如雪球自选股 / 微博私人时间线）——这些功能在 web-search-pro 和 agent-reach 两端都无解，必须浏览器手工

---

## 十、上游参考（不重复）

- 上游仓库：https://github.com/anweat/dsh-web-search-pro
- 上游 README：https://raw.githubusercontent.com/anweat/dsh-web-search-pro/master/README.md
- 上游 LOGIN：https://raw.githubusercontent.com/anweat/dsh-web-search-pro/master/LOGIN.md
- 上游 LICENSE：https://raw.githubusercontent.com/anweat/dsh-web-search-pro/master/LICENSE（1088 B MIT）
- 上游 npm 包：https://registry.npmjs.org/dsh-web-search-pro
- DSH 主仓：https://github.com/deepseek-ai/deepseek-harness
- DSH plugin 协议源码：`apps/cli/src/plugin.ts`
- 天龙本主题文件：`memory/dsh-web-search-pro-integration.md`
- 天龙 anysearch 集成档案：`memory/anysearch-integration.md`
- 天龙 agent-reach 集成档案：`memory/agent-reach-integration.md`
- 天龙 MIT 版权声明模板：`memory/mit-attribution-statements.md`

---

## 十一、版本与变更

- **V1.0.0**（2026-08-24）：天龙侧桥 V1.0，与 DSH 主仓 web profile 实装版本（`dsh-web-search-pro@0.1.8` + `@anweat/dsh-browser@0.1.8`）同步
- 累计 PASS：**+5**（本 SKILL `tests/test_installation.py`）
