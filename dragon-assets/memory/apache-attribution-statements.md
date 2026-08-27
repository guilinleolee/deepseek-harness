---
name: apache-attribution-statements
description: Apache-2.0 版权归属与 NOTICE 模板 — 适用于 anysearch / html-anything / 后续 Apache-2.0 skill 集成
metadata: 
  node_type: memory
  originSessionId: c1efa305-2588-4e5a-8f9c-cbb8419a94ef
  modified: 2026-07-29T22:49:05.198Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# Apache-2.0 版权归属与 NOTICE 模板 V1.0

> **触发场景**：天龙引擎集成 **Apache-2.0** 上游 skill（区别于 MIT 零红线与 AGPL 强约束）时，需要在以下场景给出归属：
> 1. **`SKILL.md` 内部 `## Attribution` 段落**（agent 加载时能看见）
> 2. **publisher 生成 PNG/PDF/HTTP 网页**的 footer / 致谢
> 3. **MEMORY.md 阶段行的来源链接**

---

## 一、Apache-2.0 LICENSE 红线（与 MIT / AGPL 对照）

| 维度 | Apache-2.0 | MIT ✅ | AGPL ⚠️ |
|---|---|---|---|
| 修改后分发 | ✅ 允许，需注 "Modified" | ✅ 允许 | ✅ 允许 |
| **NOTICE 文件附带** | ✅ **强制**（含 attributions / 项目名 / copyright）| ❌ 无要求 | ✅ 强制 |
| 专利授权 | ✅ 明确 | ❌ 无 | ✅ 明确 |
| Trademark 使用 | ⚠️ 禁止（未授权前）| ⚠️ 禁止 | ⚠️ 禁止 |
| SaaS 网络分发 | ✅ 无传染 | ✅ 无传染 | 🔴 **传染**（必须开源派生网络服务）|
| 商用 | ✅ | ✅ | ✅ |

**Apache-2.0 关键条款**（来自 `LICENSE` 文本）：
1. **第 4(a) 条**：受方再分发时必须附带 `LICENSE` 原文件
2. **第 4(d) 条**：若上游含 `NOTICE` 文件，受方再分发的 NOTICE 必须保留上游 NOTICE 内容，并加 "Modified" 标注（如有修改）
3. **第 6 条 Trademark**：禁止使用上游商标（"Apache" / "OpenAI" / "AnySearch" / "Kiro" / "GitHub" 等）暗示背书

---

## 二、Apache-2.0 NOTICE 模板（适用于 anysearch-skill 等）

**任何复用上游 Apache-2.0 代码 / 资源的发布物（PNG / PDF / 网页 / 数据库记录 / Publisher 入库）** 都应在致谢处附：

```
Powered by AnySearch (Apache-2.0)
Copyright 2026 AnySearch Team (https://github.com/anysearch-ai/anysearch-skill)
Source: https://github.com/anysearch-ai/anysearch-skill (Apache-2.0)
Modifications: <如有修改，简述；无修改则写 "No modifications">
This product includes software developed by AnySearch Team
(https://github.com/anysearch-ai/anysearch-skill).
```

**注意事项**：
- 不得使用 "AnySearch" 商标暗示天龙与 AnySearch 有官方背书 / 隶属关系
- 不得在产品名 / 域名 / 应用名中包含 "AnySearch" / "anysearch-" 前缀
- 允许在 changelog / release notes / SKILL.md 的 `## Attribution` 中描述 "本 skill 基于 AnySearch Skill 二次开发"

---

## 三、SKILL.md `## Attribution` 模板

天龙自研包装层（如 `anysearch-academic`）继承上游 Apache-2.0 时，必须在 `SKILL.md` 末尾含：

```markdown
## Attribution

本 skill 集成自上游 [anysearch-ai/anysearch-skill](https://github.com/anysearch-ai/anysearch-skill)（v2.1.0 · Apache-2.0）。

**上游版权**：AnySearch Team, 2026
**上游 LICENSE**：Apache License 2.0 — 详见 [`./LICENSE`](./LICENSE) 或 https://www.apache.org/licenses/LICENSE-2.0
**上游 NOTICE**：[`./NOTICE`](./NOTICE)
**本 skill 修改**：<列出所有改动；若未改动源代码，写 "未修改上游代码，仅通过 Node CLI 子进程调用">

按 Apache-2.0 §4(d)，本 skill 的 NOTICE 文件已保留上游 AnySearch Team 的归属声明。
```

---

## 四、Publisher 致谢集成

`multi-platform-publisher` 与 `blogger-poster.mjs`（guizang V2.0 pipeline）若生成图 / 文包含 anysearch 检索结果，建议在 footer 加：

```
检索数据来源：AnySearch Skill (Apache-2.0)
https://github.com/anysearch-ai/anysearch-skill
```

**不强制**：仅当内容**直接呈现上游 API 返回数据**（如股票报价、文章正文引用）时需要；纯使用上游能力而数据已经过加工的，可不附。

---

## 五、MEMORY 阶段行写法（参考已存表）

```
| 23 | **anysearch V1.0** | [anysearch-ai/anysearch-skill](https://github.com/anysearch-ai/anysearch-skill)（4,446 ⭐ · Apache-2.0 · 4 端 CLI · JSON-RPC 2.0）| [anysearch-integration.md](anysearch-integration.md) + [apache-attribution §](apache-attribution-statements.md) + `dragon-engine/skills/anysearch/`（3 处镜像 + 4 PASS） |
```

**对照 AGPL 写法**（阶段 18）：
```
| 18 | **guizang V1.0 + AGPL 红线 + map-component 合并** ⚠️ | [op7418/guizang-social-card-skill](https://github.com/op7418/guizang-social-card-skill)（5.1k ⭐）| [guizang-social-card-integration.md](guizang-social-card-integration.md) + [agpl-attribution-statements.md](agpl-attribution-statements.md) ... |
```

---

## 六、Apache-2.0 skill 集成红线检查表

集成一个新的 Apache-2.0 上游前，逐项打勾：

- [ ] 上游 `LICENSE` 文件已落盘到本地 skill 目录
- [ ] 上游 `NOTICE` 文件已落盘到本地 skill 目录
- [ ] SKILL.md `## Attribution` 段落已写入（按本文件 §三）
- [ ] MEMORY 阶段行已含 license 类型标注（`Apache-2.0`）
- [ ] 主题文件（如 `xxx-integration.md`）含"已知 license 红线"小节
- [ ] 任何 publisher 输出物的 footer 在必要时附带归属（按本文件 §四）
- [ ] 商标名未在产品名 / 域名 / 应用名中出现
- [ ] 若修改了源代码：`NOTICE` 中加 "Modified by 天龙引擎，2026-MM-DD" 行

---

## 七、与现有合规文档的关系

| 文件 | License 类型 | 触发 skill |
|---|---|---|
| [mit-attribution-statements.md](mit-attribution-statements.md) | MIT | generative-media-skills · xhs-visual-director-skill |
| [agpl-attribution-statements.md](agpl-attribution-statements.md) | AGPL | guizang V1.0 |
| **apache-attribution-statements.md**（本文件）| Apache-2.0 | anysearch V1.0 · html-anything V1.0 · **a-stock-data V1.0 ⭐NEW · global-stock-data V1.0 · TradingAgents-astock V1.0（阶段 25 / 25.1 / 25.2）** |

**新增 Apache skill 时**：直接复制本文件结构，替换上游名与 repo 链接。

---

## 八、关键事实（filesystem ground truth）

- 本文件创建于 **2026-07-20**，首次使用为 **anysearch V1.0 集成**
- 上游 `LICENSE` / `NOTICE` 文件已落盘在 `dragon-engine/skills/anysearch/{LICENSE, NOTICE}`
- html-anything V1.0 集成（阶段 17）当时未补 Apache-2.0 NOTICE 模板——**2026-07-27 经调查改判为不适用**（见 §九）
- **2026-07-27 阶段 23 配 key 后**：anysearch 4 镜像全部补 `.gitignore`（保护 `.env` 与 `runtime.conf` 不被 git 误 add）

## 九、html-anything V1.1 NOTICE 追溯 → **不适用**（2026-07-27 调查结论）

> **§七原 TODO**："html-anything V1.0 集成（阶段 17）当时未补 Apache-2.0 NOTICE 模板——下次升级 V1.1 时补本文件 §七追溯回填"

### 9.1 调查发现

`html-anything`（[nexu-io/html-anything](https://github.com/nexu-io/html-anything) 7.8k⭐ · Apache-2.0）实际**不是一个分发的 skill**，而是 **Web 应用**（Next.js 16 + Turbopack · 33 MB · 75 模板 · iframe 沙盒）。

`dragon-engine/skills/` 下没有 `html-anything` 或 `html-anything-bridge/` 目录——只有 `html-anything-integration.md`（memory 主题文件）+ 安装在 `C:/Users/li/html-anything/`（用户家目录根）。

### 9.2 Apache-2.0 §4(d) NOTICE 义务**不触发**

| 维度 | 检查结果 |
|---|---|
| 上游 LICENSE 是否落盘 | ✅ `C:/Users/li/html-anything/LICENSE`（721 bytes，上游 Apache-2.0 标准文本） |
| 上游 NOTICE 是否存在 | ❌ **上游仓库根目录无 NOTICE 文件** |
| Apache-2.0 §4(d) 是否强制 NOTICE 附带 | ❌ **§4(d) 只在 upstream 含 NOTICE 时才要求保留**；本项目未再分发 upstream 代码，仅作为本地 reference clone |

**结论**：html-anything 是天龙引擎的"上游参照系"（按 memory 主题文件第 71 行："html-anything 不是天龙的协同项,而是 baoyu-skills + huashu-design 的'上游参照系'"），不涉及 Apache-2.0 NOTICE 强制义务。

### 9.3 V1.1 升级时的唯一动作

若未来真要"分发"html-anything 二次开发的 skill（例如 stage 18 风格的 `html-anything-bridge`），需要：
1. 镜像 `LICENSE` 到 skill 目录
2. 若上游补出 NOTICE → 镜像 NOTICE 并加 "Modified by 天龙引擎，YYYY-MM-DD" 行
3. SKILL.md `## Attribution` 段落写入（按本文件 §三）

**当前不动作**：阶段 17 之后未实际发布 html-anything 二次开发版（仅克隆 upstream reference + 写 integration 主题文件），NOTICE 义务追溯不适用。
- **2026-07-21 阶段 25 增量**：a-stock-data / global-stock-data / TradingAgents-astock 三件套同一作者同协议（Apache-2.0 ✅）同范式，§九 给统一模板；同作者多仓情况下 NOTICES 模板按 §九 批量化处理

---

## 九、simonlin1212 三件套专属 NOTICE 模板（阶段 25 / 25.1 / 25.2）

> **适用范围**：[simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) V3.4.0 · [simonlin1212/global-stock-data](https://github.com/simonlin1212/global-stock-data) V1.0.1 · [simonlin1212/TradingAgents-astock](https://github.com/simonlin1212/TradingAgents-astock) V1.x，**三件套同作者同协议（Apache-2.0）同范式**。
>
> 实跑发现：3 个仓库 LICENSE 头都是 10KB+ 完整 Apache-2.0 标准文本，star 数合计 **11,284 ⭐**（7,555 + 1,199 + 2,530），是 Apache-2.0 上游最大规模的一次集成。

### 9.1 三件套统一归属段（写入每个 skill 的 NOTICE 末尾）

```
─────────────────────────────────────────────
本项目（Dragon-Engine a-stock-data-bridge / global-stock-data-bridge / trading-agents-astock-wrapper）

Powered by simonlin1212/a-stock-data V3.4.0 (Apache-2.0)
Copyright 2026 simonlin1212 (https://github.com/simonlin1212/a-stock-data)
Source: https://github.com/simonlin1212/a-stock-data
License: Apache-2.0 (https://www.apache.org/licenses/LICENSE-2.0)

另外可能含：
Powered by simonlin1212/global-stock-data V1.0.1 (Apache-2.0)
Source: https://github.com/simonlin1212/global-stock-data

Powered by simonlin1212/TradingAgents-astock (Apache-2.0)
Source: https://github.com/simonlin1212/TradingAgents-astock

Modifications: Wrapped 43/17/7 endpoints into dragon-engine SKILL.md + bash CLI;
added em_get() unified throttle entry + 3 official fallback sources;
built 28-10 finance-data-base agent for downstream (28-01 / 35-05 / 35-07).
Modified by 天龙引擎 dragon-engine, 2026-07-21.

This product includes software developed by simonlin1212
(https://github.com/simonlin1212).
─────────────────────────────────────────────
```

### 9.2 simonlin1212 三件套 vs 其他 Apache-2.0 上游差异

| 维度 | 通用 Apache-2.0（anysearch / html-anything）| simonlin1212 三件套 |
|------|-------------------------------------------|----------------------|
| 内部调用第三方 API | 一般无 | ⚠️ **8-10 个第三方财经 API**（mootdx / 腾讯 / 百度 / 东财 / 同花顺 / iwencai / 巨潮 / 雪球 / SEC / 港交所）—— **这些第三方协议不受 Apache-2.0 保护** |
| upstream NOTICE 状态 | 通常无 | 三件套均未提供显式 NOTICE 文件 —— **Apache-2.0 LICENSE 仅 4(a) 要求附 LICENSE 文本，不强制 NOTICE** |
| Trademark 风险 | 低（项目名少见）| ⚠️ "a-stock-data" 中含 "stock-data" 通词，主题文件路径要避开 "a-stock-data-official" 等暗示 |
| 数据合规 | 通常无 | ⚠️ 投研底稿 vs 二次外发 须严格区分（§9.3） |

### 9.3 simonlin1212 三件套合规红线（**比通用 Apache-2.0 多 3 项**）

1. ✅ 通用 Apache-2.0 红线（§一 3 条）—— **同样适用**
2. 🆕 **第三方 API 边界** —— mootdx/腾讯/百度/东财/同花顺/iwencai/雪球/SEC 等的协议属上游**仓库之外**的依赖，**Apache-2.0 不覆盖**；天龙须在 SKILL.md `## 合规边界` 段落明示"仅投研底稿用，不直接外发原始 HTML"
3. 🆕 **数据源协议独立判定** —— 涉及 personal data（雪球 cookie 态）须走 `agent-reach` 账号态通路，不与匿名摸底盘混用
4. 🆕 **多源备胎韧性** —— V3.4.0 新增 3 官方备胎端点，**这 3 个备胎本身就是上游数据，不是天龙二次封装** —— NOTICE 段落不必为 3 备胎单独归属

### 9.4 实拉证据（2026-07-21 GitHub REST + raw LICENSE）

```
a-stock-data:    Apache-2.0 ✅ · 7,555 ⭐ · 43 endpoints + 15 sources · LICENSE 10,760 B (头: "Apache License Version 2.0, January 2004")
global-stock-data: Apache-2.0 ✅ · 1,199 ⭐ · 17 endpoints + 5 sources  · LICENSE 同 2.0 头
TradingAgents-astock: Apache-2.0 ✅ · 2,530 ⭐ · 7 analyst agents         · LICENSE 同 2.0 头
末 commit: 9ed665c (a-stock-data, 2026-07-11) · d52a8a0 (global, 2026-06-20) · TradingAgents 仍活跃
```

### 9.5 红线检查表（阶段 25 增量）

集成 simonlin1212 三件套前，逐项打勾：

- [ ] §9.1 统一归属段已写入每个 skill 的 NOTICE 末尾
- [ ] §9.2 三件套单独 NOTICE 与统一段同时存在（不替代）
- [ ] §9.3 第三方法规边界已写入 SKILL.md `## 合规边界`
- [ ] agent-reach / 雪球账号态不进入 a-stock-data 路径（数据源 vs 账号态严格分离）
- [ ] MEMORY.md 已含阶段 25 行 + Apache-2.0 标注（✅ 已落）
- [ ] apache-attribution-statements.md §七表格已含三件套（✅ 已落）
- [ ] 28-10 agent.md 已含 "Apache-2.0 NOTICE 三件套" 引用（✅ 已落）

### 9.6 与阶段 25 主题文件的对应

| 本文件 § | 主题文件 § | 内容 |
|---|---|---|
| 9.1 NOTICE 模板 | [a-stock-data-integration.md](a-stock-data-integration.md) §五 | 完整 Apache-2.0 红线 3 条 |
| 9.2 三方 API 差异 | a-stock-data-integration.md §5.1 表 | 8 第三方 API 合规矩阵 |
| 9.3 增量红线 | a-stock-data-integration.md §八 | 风险与未决项 |
| 9.4 实拉证据 | a-stock-data-integration.md §一 | skill-updater 等价检测结果 |
| 9.5 红线检查表 | （覆盖通用检查表 §六 + 增量 4 项） | 共 8+4 = 12 项 |
| 9.6 协同关系 | a-stock-data-integration.md §六 | 8 个下游岗位 + apache-attribution 三件套 |