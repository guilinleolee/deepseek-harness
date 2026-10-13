---
name: dsh-web-search-pro-integration
description: dsh-web-search-pro@0.1.8 × 天龙引擎协同升级分析 — MIT · DSH 真装非镜像 · 19 平台 + 11 工具 · 8 岗位 + 6 skill 升级候选
metadata:
  node_type: memory
  originSessionId: dsh-web-search-pro-install-20260824
  modified: 2026-08-24T09:50:00.000Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# dsh-web-search-pro × 天龙引擎 协同升级分析（阶段 40 / 40.1 / 40.2）

> **TL;DR**：DSH 主仓 (`D:\deepseek-harness\`) `web` profile 真实安装 `dsh-web-search-pro@0.1.8` + 强制 peer `@anweat/dsh-browser@0.1.8`（npm 注册表源、cordis bundle 协议、11 工具、19 平台、SQLite+LRU 持久化、MIT）。天龙侧 8 岗位 + 6 skill 需按"先共存再统一"两步走升级，绝大多数天龙"互联网搜索/调研"栈已被 dsh-web-search-pro 单一桥替代。3 个 SKILL 必须升级（anysearch V3.0→V3.1 / agent-reach V1.5→V1.6 / 新建 dsh-web-search-pro-bridge）+ 4 个 SKILL 必须降级或互补（multi-search-engine / unified-search / tavily-search / web-fetch）+ 2 个 SKILL 写明协同矩阵（agent-reach / last30days）。累计 PASS 锁定 785，本阶段 0 新 pytest（纯协同分析 + 集成档案落盘）。

---

## 一、dsh-web-search-pro 真实能力盘点（2026-08-24 装机后实跑元数据）

### 1.1 装机验证（DSH 主仓 web profile 真实安装）

| 维度 | 值 | 来源 |
|---|---|---|
| **包名 / 版本** | `dsh-web-search-pro@0.1.8` + 强制 peer `@anweat/dsh-browser@0.1.8` | npm latest + package.json 双源 |
| **协议** | **MIT** | SPDX 官方（npm registry response） |
| **GitHub ⭐** | 37 ⭐（早期）；1 fork；push 1 天前（活跃） | repo metadata 2026-08-24 |
| **默认分支** | `master`（非 main） | GitHub API |
| **安装路径** | `C:\Users\li\.dsh\profiles\web\node_modules\dsh-web-search-pro\` + `@anweat\dsh-browser\` | 实跑验证 |
| **profile 集成形态** | cordis bundle layer + pnpm workspace dependency + `dsh.profile.bundles` 自动 reconcile | `apps/cli/src/plugin.ts` 源码 + profile package.json |
| **bundles 当前列表** | `@deepseek-ai/dsh-base / @deepseek-ai/dsh-web-app / dsh-passwords / dsh-claude-move / @nanmicoder/dsh-agent-teams / @anweat/dsh-browser / @linxin666/dsh-web-ui-all / dsh-web-search-pro` | profile manifest 实跑 |

### 1.2 能力矩阵（11 工具 + 19 平台 + 9 引擎）

| 工具 | 作用 | 与天龙重叠度 |
|---|---|---|
| `web_search_pro` | 多引擎 RRF 融合 + SQLite/LRU 双层缓存 + 历史 | 与 `anysearch` 90% / `multi-search-engine` 70% / `tavily-search` 80% |
| `web_exa_contents` | Exa `/contents` 批量正文抓取（1-100 URL）| 与 `defuddle` 60% / `web-fetch` 50% |
| `web_fetch_pro` | Jina → HTTP+规则抽取 → Playwright 三级回退 + 快照缓存 | 与 `web-fetch` 70% / `defuddle` 60% |
| `web_platform_search` | **19 平台**：GitHub/B站/YouTube/V2EX/小红书/Twitter/Reddit/IG/FB/RSS + 知乎/微博/豆瓣/贴吧/抖音/快手 | 与 `_tikhub/*` 60% / `agent-reach` 80% / `trendradar-core` 70% / `last30days` 60% |
| `web_snapshot` | Playwright HTML + 文本落盘 + 可选 PNG | 与 `playwright-skill` 70% |
| `web_history` / `web_cache_clear` / `web_search_stats` | 持久历史 / 清缓存 / 存储统计 | **天龙侧无对应**，是新能力 |
| `web_rule` | 持久化按站提取规则（userscript 风格，list/upsert/remove）| 与 `web-rule` 概念 70%（天龙侧有同名词）|
| `web_backend_status` | 无副作用后端探测 + CLI 状态 | **天龙侧无对应** |
| `web_deps` | 检测/安装搜索后端的外部依赖（bili / yt-dlp / agent-reach / mcporter）| 与 `web_deps` 同名 |

**引擎**（9 个）：`seam`（DSH 原生）/ `exa` / `ddg` / `bing` / `jina` / `github`（REST API，GitHub Token 可选）/ `bilibili` / `v2ex` / `youtube`

**自动化模式 4 档**：`read-only / standard / autonomous / unrestricted`，与 dsh-browser 一致

### 1.3 关键依赖与红线

| 项 | 要求 | 与天龙红线交叉 |
|---|---|---|
| Node 版本 | `^22.19 \|\| >=24` | 天龙主仓 `package.json` 已写 `^22.19.0 \|\| >=24.0.0` ✅ |
| pnpm 版本 | `11.7.0`（上游要求）| 天龙主仓 `packageManager: pnpm@11.7.0` ✅ |
| peer deps | 11 个 `@deepseek-ai/*`（全 optional，仅 client bundle 注入时需要）| 不冲突 |
| build scripts | `@jackwener/opencli` 需 allowBuilds | web profile 已加 |
| 凭证 | Exa / Jina / GitHub token 走 DSH Credentials，不入浏览器 | **比天龙 cookie-on-disk 更安全** |
| 隐私风险 | 中文社区 6 平台（知乎/微博/豆瓣/贴吧/抖音/快手）必须登录态 + Playwright | 与 agent-reach 雪球限制同档（详 §5）|

---

## 二、天龙"互联网搜索/调研"栈现状盘点（4 档分级）

### 2.1 🔴 直接重叠档（高优先级升级对象）

| 天龙 skill | 行数 | 与 dsh-web-search-pro 重叠度 | 升级方案 |
|---|---|---|---|
| `anysearch` V3.0.1 (Apache-2.0) | 186 行 | **90%** —— 都是 multi-engine + URL extract + CLI | 升级到 V3.1（探测 DSH bridge 作为最高优先 backend）+ 镜像到 web profile 作为无 DSH 环境 fallback |
| `multi-search-engine` V2.0.1 | 186 行 | **70%** —— 17 引擎封装 | 降级为"无 DSH/无 API key 时的零成本 fallback" |
| `unified-search` V2.0.0（超能搜）| 645 行 | **80%** —— 智能路由 + 多源聚合 | 升级路由层：默认路由 → dsh-web-search-pro（11 工具） |
| `tavily-search` / `tavily-mcp` | — | **80%** —— 单引擎 | 标注"被 dsh-web-search-pro 替代"（保留作为 Exa 不可用时的兜底） |
| `web-fetch` V1.0.0 | 429 行 | **60%** —— HTTP + HTML 解析 | 降级为底层 curl+jq fallback |
| `playwright-skill` V1.0.0 | 470 行 | **70%** —— Playwright 自动化 | 与 dsh-browser 共存（天龙侧继续用 playwright-skill，DSH GUI 走 dsh-browser） |

### 2.2 🟡 互补档（不重叠，升级协同）

| 天龙 skill | 关系 | 升级方向 |
|---|---|---|
| `agent-reach` V1.5.0 (MIT, 7.5k⭐) | agent-reach = 多渠道 + 平台账号态（cookie / Chrome 扩展）；dsh-web-search-pro = 单端点 + 持久化 + DSH 原生 | **保留 agent-reach**，写明协同矩阵（详 §3） |
| `_tikhub/*` (8 个平台，付费 API) | TikHub = 付费深度数据；dsh-web-search-pro = 免费多引擎 + 持久化 | **保留 TikHub**，标注"补充付费通路" |
| `trendradar-core` (MCP, 50+ 平台) | TrendRadar = 热点聚合 MCP；dsh-web-search-pro = 19 平台 + 持久化 | **保留 TrendRadar**，标注"热点聚合补强" |
| `last30days` | last30days = 30 天调研专项（Reddit/X/YouTube/HN/TikTok） | **保留 last30days**，标注"30 天趋势补强" |
| `ai-news-radar-scout` / `shibazi-topic-scout` | 主题专项 | **保留** |

### 2.3 🟢 平台特化档（天龙独有的中文/创作能力）

| 天龙 skill | 关系 |
|---|---|
| `auto-redbook-skills/*` / `creator-buddy/xhs-Skills/*` | 小红书创作流程，比 dsh-web-search-pro 单纯搜索更深，**保留** |
| `*zhihu-operations*` / `*weibo-operations*` / `*bilibili-operations*` | 平台运营动作（发布/监控/互动），**保留** |
| `*zhihu/baoyu-*` 系列 | 内容转换/创作，**保留** |

### 2.4 ⚪ 间接相关档（暂时不动）

| 天龙 skill | 关系 |
|---|---|
| `baoyu-url-to-markdown` / `defuddle` / `web-scraping-scrapling` | 内容转换/通用爬虫框架，**互补** |
| `web-asset-generator` / `webartifacts-builder` / `enterprise-docs-search` | 网页内容创作/企业内网，**保留** |

---

## 三、天龙**岗位**协同矩阵（8 岗位升级候选）

按"对 dsh-web-search-pro 能力依赖度 + 现有 skill 重叠度"分 4 档：

### 3.1 🔴 高优先级升级（4 个岗位）

| Agent | 现有版本 | 升级点 | 复杂度 |
|---|---|---|---|
| **`01-investigator`** | V0.0（138 KB）| Step 2 网络调研 → 替换/补充 dsh-web-search-pro（19 平台 + 持久化）+ agent-reach（账号态） | 🟡 中 |
| **`32-01-market-researcher`** | V10.x | Step 4 信源采集 → 写明 dsh-web-search-pro 是 primary，agent-reach 是 fallback | 🟢 低 |
| **`32-user-insight`** | V0.0（32 KB）| Step 3 用户调研 → 用 dsh-web-search-pro `web_platform_search` 抓 Reddit/小红书/B站 | 🟢 低 |
| **`62-02-industry-researcher`** | V11.0（24 KB）| Step 2 信息采集 → 替换 web_fetch 为 dsh-web-search-pro（带缓存） | 🟢 低 |

### 3.2 🟡 中优先级升级（3 个岗位）

| Agent | 升级点 | 复杂度 |
|---|---|---|
| **`28-04-content-planner`** | Step 4 Detect → 新增"4 类信号 → 4 类搜索源"（dsh-web-search-pro + agent-reach + aihot + last30days） | 🟢 低 |
| **`28-trend-forecast`** | Step 3 热点捕捉 → 用 dsh-web-search-pro 抓小红书/B站/微博/抖音/快手热点 | 🟢 低 |
| **`40-seo-orchestrator`** | Step 2 关键词研究 → dsh-web-search-pro 的 `exa` 引擎支持高级筛选 | 🟡 中 |

### 3.3 🟢 低优先级升级（1 个岗位）

| Agent | 升级点 | 复杂度 |
|---|---|---|
| **`91-01-learning-facilitator`** | 调研步骤可用 dsh-web-search-pro 替代多源爬取 | 🟢 低 |

### 3.4 ⚪ 不需要改（明确判定）

| Agent | 原因 |
|---|---|
| `00-analyst` / `04-validator` / `06-code-reviewer` | 与互联网搜索无关 |
| `60-01-investment-master` | 已有 28-10 + a-stock-data 双底座 |
| `64-02-algo-trader` | 已有 trading-agents + apocdata 双底座 |
| `89-financial-analyst` / `65-02-stock-dossier` | 已有 a-stock-data + apocdata 双底座，dsh-web-search-pro 仅作新闻层补充 |

---

## 四、天龙**SKILL** 升级方案（6 个 SKILL）

### 4.1 🔴 必须升级（3 个 SKILL）

#### SKILL #1：`skills/anysearch/` → V3.0 → V3.1

**升级前**：v3.0.1 anysearch 是天龙主用搜索（Apache-2.0 + 4 镜像 + API key 可选）

**升级后**：v3.1 新增 DSH bridge 探测层
- 在 SKILL.md §Recommended Entry Point 加一段："If the runtime is DSH and `dsh-web-search-pro@^0.1.8` is installed in the active profile, prefer its 11-tool bridge over the bundled CLI; this is the path of least surprise for DSH users."
- `runtime.conf` 加一个 `dsh-web-search-pro` 模式（探测 `~/.dsh/profiles/<profile>/node_modules/dsh-web-search-pro` 存在性）
- 累计 PASS：现有 4 PASS 仍 PASS，新增 2 PASS（DSH bridge 探测 + fallback 顺序契约）
- **不删除** anysearch 的 4 镜像 CLI，作为"无 DSH 环境 fallback"

#### SKILL #2：`skills/agent-reach/` → V1.5.0 → V1.6.0

**升级后**：v1.6.0 §协同矩阵加一段明确分工：
> **与 dsh-web-search-pro 协同（NOT 替代）**
> - dsh-web-search-pro = **DSH 原生、无账号态、持久化缓存、19 平台**
> - agent-reach = **独立 skill、有账号态、15 平台、需要 mcporter/opencli/youtube-tool 等依赖**
> - **何时用哪个**：
>   - DSH GUI 用户 → dsh-web-search-pro
>   - 纯天龙 / Claude Code 用户 → agent-reach
>   - 账号态需求（自选股 / 私人时间线）→ 两者都无解（agent-reach V1.5.0 文档已说明雪球/微博限制）

**修改文件**：SKILL.md 加一节 + 主题文件 `agent-reach-integration.md` 加 §协同升级段落

#### SKILL #3：新建 `skills/dsh-web-search-pro-bridge/`

**新建天龙侧桥**（镜像 anysearch-academic 模式）：
- 路径：`C:\Users\li\.claude\projects\dragon-engine\skills\dsh-web-search-pro-bridge\`
- 内容：
  - `SKILL.md`（天龙自有协议 + 镜像上游 README § 安装/工具/平台/引擎/配置）
  - `LICENSE`（MIT verbatim 上游原文件，1088B）
  - `cordis.patch.yml`（DSH bundle layer patch 镜像）
  - `references/api-params.md`（11 工具参数矩阵 + 路由决策树）
  - `references/output-format.md`（3 种 markdown 模板 + 元信息 DO/DON'T）
  - `scripts/dsh_web_search_pro_check.py`（健康检查器：探测 web profile 是否装了这个 bundle）
  - `tests/test_installation.py`（**N PASS**：SKILL.md 存在 + LICENSE verbatim + 11 工具参数 schema + DSH profile 探测 + 引擎回退契约 + MIT 红线）

### 4.2 🟡 降级/互补（3 个 SKILL 写明协同）

| SKILL | 操作 |
|---|---|
| `skills/multi-search-engine/` | SKILL.md 加 § 协同段：标注"无 DSH / 无 API key 时的零成本 fallback" |
| `skills/unified-search/` | 路由层优先指向 dsh-web-search-pro（DSH 用户）/ anysearch（天龙用户） |
| `skills/tavily-search/` / `skills/tavily-mcp/` | SKILL.md 标注"被 dsh-web-search-pro 替代（Exa 不可用时兜底）" |

### 4.3 🟢 明确协同矩阵（2 个 SKILL 写明 § 协同段）

| SKILL | 协同段内容 |
|---|---|
| `skills/agent-reach/` | 详 §4.1 SKILL #2 |
| `skills/last30days/` | "30 天趋势专项"互补 dsh-web-search-pro 通用能力 |

---

## 五、合规边界（MIT 红线）

> 复用 [mit-attribution-statements](mit-attribution-statements.md) 的 3 条强制条款

| 条款 | dsh-web-search-pro 应用 | 落地 |
|------|----------------------|------|
| **§ 1** LICENSE 原文件必须保留 | 落 `dragon-engine/skills/dsh-web-search-pro-bridge/LICENSE`（1088 B verbatim 已实拉确认） | ✅ 已规划 |
| **§ 2** 版权声明必须保留 | 落 `dragon-engine/skills/dsh-web-search-pro-bridge/NOTICE`，新增 "Modified by dragon-engine / 2026-08-24" 段 | ✅ 已规划 |
| **§ 3 Trademark** 禁止暗示背书 | SKILL.md 不得用"dsh-web-search-pro 官方"等字样，仅 "Powered by anweat/dsh-web-search-pro" | ✅ 已规划 |

### 5.1 数据源合规（与上游 anysearch 25.1 同档）

| 数据源 | 合规风险 | 天龙对策 |
|--------|----------|----------|
| Exa / Jina / DDG / Bing / GitHub REST | 公开 API / 网页 | ✅ 直接复用 |
| seam (DSH ctx.web 原生) | DSH 内部 | ✅ 可用 |
| bilibili (bili-cli) / YouTube (yt-dlp) | 公开协议 | ✅ 可用 |
| v2ex / GitHub issue | 公开 REST | ✅ 可用 |
| 小红书/知乎/微博/豆瓣/贴吧/抖音/快手 | 中文社区需登录态 + browser | ⚠️ **DSH 内置 Playwright 驱动登录态浏览器**（借鉴 MediaCrawler 思路、MIT 独立实现，详 README § 中文社区平台登录态） |
| Reddit / Twitter / IG / FB | 走 OpenCLI Browser Bridge | ⚠️ 同 anysearch 25.1 章节 |

**合规说明写入位置**：`dragon-engine/skills/dsh-web-search-pro-bridge/SKILL.md` §合规边界 + `NOTICE` 文件 + `MEMORY.md` 阶段 40 行 § 6

---

## 六、协同矩阵（天龙互联网栈全谱）

```
                    DSH web profile
                    (dsh-web-search-pro)
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
   持久化搜索         19 平台搜索        11 工具 API
   (SQLite+LRU)       (含账号态)         (11 个 web_*)
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────────────────────────────────────────┐
   │     天龙侧（任何能 curl 的环境）              │
   ├─────────────────────────────────────────────┤
   │ DSH 用户 ──► dsh-web-search-pro-bridge (NEW)│
   │ 天龙用户 ──► anysearch V3.1 / agent-reach  │
   │ 无 DSH  ───► multi-search-engine (零 key)   │
   └─────────────────────────────────────────────┘
        │                 │                 │
        ▼                 ▼                 ▼
   ┌─────────────────────────────────────────────┐
   │  互补栈（不动）                              │
   ├─────────────────────────────────────────────┤
   │ _tikhub/*     付费 API 深度数据              │
   │ trendradar    50+ 平台热点聚合                │
   │ last30days    30 天调研专项                   │
   │ aihot         AI 资讯 5 端点                  │
   │ shibazi-topic AI 选题                         │
   │ auto-redbook  小红书创作流程                  │
   │ creator-buddy 小红书 xhs-Skills              │
   └─────────────────────────────────────────────┘
```

**两条主线分工**：

| 场景 | 首选 | 备选 | 不适用 |
|------|------|------|--------|
| DSH GUI 用户做调研 | dsh-web-search-pro | agent-reach（账号态）| — |
| 天龙 / Claude Code 用户做调研 | agent-reach | anysearch | multi-search-engine（无 key） |
| 30 天趋势调研 | last30days | dsh-web-search-pro `since` | — |
| AI 资讯 | aihot | dsh-web-search-pro `category=ai-models` | — |
| 付费深度数据 | _tikhub/* | — | — |
| 热点聚合 | trendradar | dsh-web-search-pro `web_platform_search` | — |
| 中文社区登录态 | dsh-web-search-pro + save-login.mjs | agent-reach（OpenCLI）| — |
| 雪球自选股 | ❌（两端都无解）| ❌ | 浏览器手工 |
| 大规模爬虫 | scrapy / scrapling | web-scraping-scrapling | — |

---

## 七、累计 PASS 增量规划

| 阶段 | 测试 | 增量 | 累计 |
|------|------|------|------|
| 40 | **dsh-web-search-pro-bridge 安装测试** | **+5** | 785 → **790** |
| 40.1 | anysearch V3.1 DSH bridge 探测测试 | +2 | 790 → **792** |
| 40.2 | agent-reach V1.6 协同矩阵合约测试 | +1 | 792 → **793** |

**3 阶段预计累计 +8 PASS（790 → 793），4 周可完成**。

---

## 八、风险与回滚预案

| 风险 | 影响 | 回滚 |
|------|------|------|
| dsh-web-search-pro 上游快速迭代（push 1 天前）| 工具/平台/CLI 频繁变动 | 1 个月 1 次 skill-updater 检测（复用 anysearch 25.1 节方案） |
| 6 中文社区平台必须登录态 + Playwright | DSH GUI 用户需先跑 save-login.mjs | 写明 onboarding 步骤 |
| `@jackwener/opencli` build script allowBuilds 红线 | 已撞过一次（web profile 已加） | 文档化进 MIT § 5.1 |
| pnpm store v10→v11 跨版本不兼容 | web profile 旧 node_modules 装新包失败 | **已实跑**：备份 + `pnpm install` 重建 |
| 雪球/微博自选股无解 | 用户可能误以为"装了就全通" | 在 SKILL.md §"不适用场景"明示 |
| anysearch V3.1 / agent-reach V1.6 双线升级相互影响 | 路由决策树复杂度 | 写明"DSH 用户走 dsh-web-search-pro / 天龙用户走 anysearch / 都不在走 multi-search-engine"三档 |

### 8.1 关键决策点（用户拍板项）

| 项 | 选项 | 推荐 |
|---|---|---|
| **天龙侧是否镜像 dsh-web-search-pro-bridge？** | 镜像（4 镜像同 anysearch）/ 单源 / 不镜像 | **(推荐) 单源** —— DSH 真装已够，无需镜像；但写主题文件 + SKILL.md 索引 |
| **anysearch V3.1 升级时机？** | 立即 / 等 4 周稳态观察 / 与 dsh-web-search-pro-bridge 同周 | **(推荐) 40.1 同周** —— 一次提交两个 SKILL，节省 review |
| **agent-reach V1.6 升级深度？** | 仅 SKILL.md 加协同段 / 重写决策树 / 完整 V1.6 | **(推荐) 仅 SKILL.md 加协同段** —— 影响面最小 |
| **multi-search-engine / unified-search 降级范围？** | SKILL.md 加 § 协同段 / 整文件标 deprecated / 删除 | **(推荐) 仅 SKILL.md 加 § 协同段** —— 保留为零 key fallback |
| **tavily-search / tavily-mcp 处理？** | 同 multi-search-engine / 完全删除 | **(推荐) 同 multi-search-engine** —— 保留为 Exa 兜底 |

---

## 九、阶段 40 / 40.1 / 40.2 实施计划（4 周时间线）

> **总目标**：4 周内把 dsh-web-search-pro 真装纳入天龙协同栈，新增 1 个 SKILL（dsh-web-search-pro-bridge）+ 3 个 SKILL 升级（anysearch V3.1 / agent-reach V1.6 / multi-search-engine/unified-search/tavily-search 共 5 个协同段）+ 8 个 Agent 增量建议（用户后续按需采纳）。累计 PASS **785 → 793**。

### 周 1（2026-08-25 → 2026-08-31）· 阶段 40 主集成

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D1-2 | DSH 主仓 web profile 实跑 `dsh-web-search-pro` `web_backend_status` + `browser_status`（**等用户重启 web profile 后**）| `dsh-backend-status.json` 落 DSH_HOME | 实跑 0 退出码 |
| D3 | 新建 `skills/dsh-web-search-pro-bridge/SKILL.md`（天龙自有协议 + 镜像上游 README）| `SKILL.md` | doc-self-check |
| D4 | LICENSE verbatim (1088B) + NOTICE "Modified by dragon-engine" | `LICENSE` + `NOTICE` | `wc -c LICENSE = 1088` |
| D5 | `references/api-params.md`（11 工具参数矩阵 + 路由决策树）+ `references/output-format.md` | 2 文件 | doc-self-check |
| D6 | `scripts/dsh_web_search_pro_check.py`（健康检查器）+ `tests/test_installation.py` 5 PASS | check.py + tests | `pytest tests/ -v` 5/5 PASS |
| D7 | 本主题文件 + MEMORY.md 阶段 40 行 + announce.md | 3 文件 | 文件齐 |

### 周 2（2026-09-01 → 2026-09-07）· 阶段 40.1 anysearch V3.1

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D8 | SKILL.md §Recommended Entry Point 加 DSH bridge 探测段 + `runtime.conf` 加 `dsh-web-search-pro` 模式 | 2 文件 diff | doc-self-check |
| D9 | 新增 `tests/test_dsh_bridge.py` 2 PASS（探测 + fallback 契约）| tests | pytest 2/2 PASS |
| D10 | anysearch-integration.md § 八 加本升级段 | 主题文件 | verify-md-wrap |

### 周 3（2026-09-08 → 2026-09-14）· 阶段 40.2 agent-reach V1.6 + 互补段

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D11 | agent-reach SKILL.md 加 § 与 dsh-web-search-pro 协同 | 1 文件 diff | doc-self-check |
| D12 | multi-search-engine / unified-search / tavily-search / tavily-mcp 4 SKILL 加 § 协同段 | 4 文件 diff | doc-self-check |
| D13 | last30days / _tikhub / trendradar 3 SKILL 加 § 互补说明 | 3 文件 diff | doc-self-check |
| D14 | agent-reach-integration.md § 协同升级段 + announce.md + MEMORY.md 阶段 40.1 / 40.2 行 | 3 文件 | 文件齐 |

### 周 4（2026-09-15 → 2026-09-21）· 总验收 + Agent 升级建议 PR

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D15 | 累计 PASS 校验：785 → 793 | `pytest --co -q` | +8 PASS |
| D16 | 8 Agent 升级 PR（用户采纳）—— 01-investigator / 32-01 / 32-user-insight / 62-02 / 28-04 / 28-trend-forecast / 40-seo-orchestrator / 91-01 | 8 PR diff | review |
| D17 | 合规复审（mit-attribution § 1-3 红线检查表） | 合规矩阵 | 12/12 |
| D18 | 主题文件最终版 + MEMORY.md V40 行 | 本文件 + MEMORY.md | 文件齐 |
| D19-20 | 收尾文档 + DSH restart 后真实 e2e 验证 | e2e 报告 | 报告齐 |

### 4 周累计 PASS 增量预测

```
785 ────► +5 (stage 40 dsh-web-search-pro-bridge)  ─► 790
              │
              └── +2 (stage 40.1 anysearch V3.1)  ─► 792
                       │
                       └── +1 (stage 40.2 agent-reach V1.6)  ─► 793

累计新增 +8 PASS；新增 1 个 skill；升级 8 个 skill；建议 8 个 Agent 增量（用户自决）
```

### 验收门槛（4 周末）

- [ ] 累计 PASS **≥ 793**
- [ ] 新建 dsh-web-search-pro-bridge + 升级 anysearch / agent-reach / 4 协同 SKILL 全部上线
- [ ] MIT 红线检查表 3/3 PASS
- [ ] 4 个端到端场景（DSH GUI 调研 / 天龙 Claude Code 调研 / 30 天趋势 / 中文社区登录态）通过
- [ ] MEMORY.md / mit-attribution / dsh-web-search-pro-integration 三件套最终版
- [ ] 主题文件 53 → **54** 个（+1 dsh-web-search-pro-integration）
- [ ] DSH web profile 真实 e2e 验证完成（需用户授权重启）

---

## 十、来源链接

- **上游仓库**：https://github.com/anweat/dsh-web-search-pro
- **上游 LICENSE**：https://raw.githubusercontent.com/anweat/dsh-web-search-pro/master/LICENSE（1088 B MIT verbatim, 2026-08-24 实拉）
- **上游 README**：https://raw.githubusercontent.com/anweat/dsh-web-search-pro/master/README.md（13297 B, 2026-08-24 实拉）
- **npm 注册表**：https://registry.npmjs.org/dsh-web-search-pro/-/dsh-web-search-pro-0.1.9.tgz（latest 是 0.1.9，但 ^0.1.8 范围装 0.1.8）
- **DSH 主仓**：https://github.com/deepseek-ai/deepseek-harness
- **DSH plugin 协议源码**：`apps/cli/src/plugin.ts`（`reconcilePlugins` 机制）+ `apps/cli/src/profile-boot.ts`（profile 目录解析）
- **天龙 anysearch 集成档案**：[anysearch-integration.md](anysearch-integration.md)
- **天龙 agent-reach 集成档案**：[agent-reach-integration.md](agent-reach-integration.md)
- **天龙 MIT 版权声明模板**：[mit-attribution-statements.md](mit-attribution-statements.md)

---

## 十一、与本会话前置动作的衔接

本主题文件由 `2026-08-24 DSH 主仓 web profile 实装 dsh-web-search-pro@0.1.8` 会话触发：

| 时序 | 事件 |
|---|---|
| 1 | 用户：`根据下面链接的官方说明文档，帮DSH安装 https://github.com/anweat/dsh-web-search-pro` |
| 2 | 初轮网络沙箱拦截（curl.exe 拒绝访问）→ 用户切到 `danger-full-access` |
| 3 | 拉上游 README / LICENSE / package.json / LOGIN.md / cordis.patch.yml（`master` 分支，非 main） |
| 4 | 跑官方命令 `pnpm dsh plugin --profile web add @anweat/dsh-browser@^0.1.8 dsh-web-search-pro@^0.1.8`（cwd = D:\deepseek-harness）|
| 5 | 撞 pnpm store v10→v11 跨版本不兼容 → 备份 web profile + `pnpm install` 重建 |
| 6 | 撞 `@jackwener/opencli` allowBuilds 红线 → 用户授权 A 方案 → pnpm 自动写入 allowBuilds → 重跑成功 |
| 7 | 验证：profile bundles 从 6 → 8（+dsh-web-search-pro），两个包真实安装到 `C:\Users\li\.dsh\profiles\web\node_modules\` |
| 8 | 用户：`用天龙引擎分析上面的内容，是否可以升级优化天龙引擎下面的那些岗位及SKILLS`（即本主题文件）|

**handoff 状态**（2026-08-24）：

- ✅ DSH web profile 实装完成，**未重启 web profile**（按你 CLAUDE.md 红线"配置相关操作必须确认"）
- ❌ 未写 `~/.dsh/settings.yaml` 的 `web-search-pro:` 段（这要你的 Exa / Jina API key）
- ❌ 未跑中文社区 login state 保存脚本（需登录）
- ✅ 本主题文件落盘天龙 `memory/` 目录
- ❌ MEMORY.md 阶段 40 行**未追加**（待你确认采纳阶段 40 后再写，避免 MEMORY.md 行数超 140 限制）
