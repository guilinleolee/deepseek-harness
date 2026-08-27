---
name: a-stock-data-integration
description: a-stock-data V3.4.0 + global-stock-data V1.0.1 集成档案 — Apache-2.0 · 43 端点 + 15 数据源 + 17 端点 + 5 数据源 · 阶段 25 财经数据底座
metadata: 
  node_type: memory
  originSessionId: a-stock-data-integration-20260721
  modified: 2026-07-21T10:30:55.312Z
heat: 0.7
last_ref_date: 2026-08-24
mneme_schema: v12.0
---


# a-stock-data / global-stock-data 集成档案 V1.0（阶段 25 / 25.1）

> **TL;DR**：同作者 [simonlin1212](https://github.com/simonlin1212) 同源同协议同范式的 3 件套 —— **a-stock-data V3.4.0**（Apache-2.0 ✅ · 7,555⭐ · 43 端点 + 15 数据源 · A 股全栈）、**global-stock-data V1.0.1**（Apache-2.0 ✅ · 1,199⭐ · 17 端点 + 5 数据源 · 美港股全栈）、**TradingAgents-astock**（Apache-2.0 ✅ · 2,530⭐ · 7 位分析师多 Agent 投研辩论框架），拟通过 **阶段 25 = a-stock-data-bridge** + **25.1 = global-stock-data-bridge** + **25.2 = trading-agents-astock** 集成进天龙引擎，并由新建 **28-10 财经数据底座师** 一岗统筹。这是天龙首次引入**真实行情 / 资金 / 筹码**金融数据底座，将填补 28-01 / 35-05 / 35-07 / aihot / neat-freak 在财经赛道的核心空缺。

---

## 一、实跑元数据（skill-updater V1.1.3 等价检测 · 2026-07-21）

### 1.1 三个上游仓库 API 字段（GitHub REST + raw LICENSE 直拉）

| 字段 | a-stock-data | global-stock-data | TradingAgents-astock |
|------|--------------|-------------------|----------------------|
| **license.spdx_id** | **Apache-2.0** 🟢 | **Apache-2.0** 🟢 | **Apache-2.0** 🟢 |
| **stars** | **7,555** ⭐（38 天内从 0 到 7.5k） | 1,199 | 2,530 |
| forks | 1,399 | 183 | 673 |
| 默认分支 | main | main | main |
| language | （Skill 风格 Markdown）| （Skill 风格 Markdown）| Python |
| 体积 | 213 KB | 207 KB | — |
| **端点 / 数据源** | **43 端点 + 15 数据源** | 17 端点 + 5 数据源 | 7 分析师 Agent |
| 出生日期 | 2026-05-11 | 2026-05-20 | — |
| 末 push | 2026-07-11（10 天前） | 2026-06-20 | 2026-07-10 |
| open_issues | 9 | 0 | — |

### 1.2 最近 commit 节选（验证上游活跃度）

```
a-stock-data:
  9ed665c 2026-07-11 feat: v3.4.0 接口质量修复 + 备用源韧性层（端点 40→43，数据源 13→15）
  8b11251 2026-07-10 docs: v3.3.1 收窄 description 触发范围 (#29) + 单文件形态定调 (#21/#22/#27)
  bcda405 2026-06-28 feat: 新增打板/ETF期权/舆情互动三层 (v3.3.0 · #13 #23 #15)
  8f72540 2026-06-28 fix: 修复 mootdx 分钟K线参数 + full_valuation EPS 取列 (#31 #28)
  e40d065 2026-06-20 fix: v3.2.4 — mootdx 0.11.x BESTIP 空串崩溃防护 (#26 / PR #7)

global-stock-data:
  d52a8a0 2026-06-20 fix: v1.0.1 — 5 处漏传 params（始终空数据）+ market_stock_list diff 为 dict 崩溃 (PR #1)
  ef9e72a 2026-06-20 fix: 5 处 requests.get 漏传 params 导致请求无参数 (#1)
  9b95390 2026-05-20 feat: 新增技术指标层 (MA/MACD/RSI/KDJ/布林带)
  00292c9 2026-05-20 v1.0: 美股港股全栈数据工具包首次开源发布
```

**结论**:
- ✅ **3 个仓库都是 Apache-2.0**（SPDX 官方确认 + LICENSE 头文件确认）
- ✅ 同作者 simonlin1212 5 月密集发布 3 个 SKU，**架构一致 / 数据风格一致 / 命名约定一致** —— 这是同一产品线的连续版本
- ⚠️ a-stock-data 已 V3.4.0（45 天迭代 4 个大版本），上游**仍极活跃**，建议天龙每 30 天跑一次 skill-updater 检测

---

## 二、镜像拓扑（待 stage 25 实装，本次仅规划）

| # | 路径 | 角色 |
|---|---|---|
| 1 | `dragon-engine/skills/a-stock-data-bridge/` | **真源**（拉链解压落盘） |
| 2 | `dragon-engine/skills/a-stock-data-bridge/SKILL.md` | 包装层（V3.4.0 → 43 端点 wrapper + `em_get()` 节流统一入口 + 15 源备胎策略） |
| 3 | `dragon-engine/skills/global-stock-data-bridge/` | 真源镜像（同 author / 同范式） |
| 4 | `dragon-engine/.claude/skills/a-stock-data-bridge/` | 项目级 Claude 配置镜像 |
| 5 | `dragon-engine/skills/async-task-pattern/` | 共用"金融限流原语"（≥1s + 抖动 + 会话复用 + 备胎切换） |
| 6 | `dragon-engine/agents/28-10-finance-data-base.md` | **新建岗位** · 财经数据底座师 V1.0 |

---

## 三、a-stock-data V3.4.0 能力矩阵（43 端点 × 15 数据源）

### 3.1 十层架构

```
L1  行情层    K线(MA5/10/20) · 五档盘口 · PE/PB/市值 · 指数/ETF 期权
L2  研报层    个股 + 行业研报列表 · PDF 下载 · 一致预期 · iwencai NL 搜索
L3  信号层    强势股 · 题材归因 · 北向资金 · 概念板块 · 资金流向 · 龙虎榜 · 解禁
L4  资金面    融资融券 · 大宗交易 · 股东户数 · 分红送 · 分钟级资金流
L5  新闻层    东财个股新闻 · 全球资讯
L6  基础数据  mootdx 季报 37 字段 · F10 九大类 · 财报三表
L7  公告层    巨潮 cninfo + mootdx 沪深北全量公告
L8  打板层    涨停板战法数据 · 龙头识别 · 板块联动
L9  ETF期权   ETF 净值 · 期权 Greeks · 隐含波动率
L10 舆情互动  雪球评论热榜 · 同花顺问财 · 互动易问答
```

### 3.2 防封 / 节流 / 备胎（**天龙必学**的关键设计）

| 原语 | 上游实现 | 天龙复用方式 |
|------|----------|--------------|
| **统一节流入口** | `em_get()` · 串行限流 ≥1s + 随机抖动 | 落 `async-task-pattern/rate_limiter.py` |
| **会话复用** | 全局 requests.Session · keep-alive | 落 `async-task-pattern/session_pool.py` |
| **优先级排序** | 通达信/腾讯不封 IP 优先 → 东财仅用于独有数据 | 落 `a-stock-data-bridge/source_priority.json` |
| **备胎降级** | V3.4.0 新增 **3 个官方备胎端点**（同源数据多入口）| 落 `a-stock-data-bridge/fallback.yaml` |
| **错误码识别** | mootdx 0.11.x BESTIP 空串崩溃 → 0.11.x 兼容 | 落 `a-stock-data-bridge/error_handlers/` |

---

## 四、stage 25 实施边界（拟）

### 4.1 集成层 (a-stock-data-bridge)

| 验收项 | 数量 | 备注 |
|------|------|------|
| 端点 wrapper | **43** | 1:1 映射 V3.4.0 |
| 数据源策略文件 | **15** | 优先级 + 备胎 + 节流参数 |
| pytest PASS | **≥5** | 端点 schema + 节流 + 备胎 + 错误处理 + 合规 |
| 累计 PASS 增量 | 606 → **≥611** | 仿照 anysearch +4 / +5 节奏 |

### 4.2 Agent 层 (28-10 财经数据底座师)

- 继承 `35-07 V1.0` 方法论(横纵分析)+ 继承 `28-04 V10.3` 选题思路
- 提供"投研底稿 → 文案/短视频数据图表"全链路
- 输出 4 类:① 个股深度底稿 ② 行业横评底稿 ③ 资金流事件底稿 ④ 公告事件底稿
- 与 28-01 V10.3 / 35-05 V10.3 / 35-07 V1.0 / 28-04 / aihot / neat-freak 6 个下游岗位对接

### 4.3 配套 Agent 升级（既有 Agent 增量改造）

| Agent | 升级点 | 复杂度 |
|------|--------|-------|
| **28-01 V10.3 → V10.4** | khazix-writer 加"财经场景子模块"：PE/市值/北向/龙虎榜作为论点 | 🟡 中 |
| **35-05 V10.3 → V10.4** | cinema-director 注入"行情 K 线 / 资金流向图 / 龙虎榜"作为可视化镜头脚本 | 🟡 中 |
| **35-07 V1.0 → V1.1** | hv-analysis 加"个股 vs 行业 vs 大盘"三维数据查询（走 a-stock-data 13+2 源）| 🟢 低 |
| **aihot V1.0 → V1.1** | 加"财经热度榜"（强势股 / 题材归因）| 🟢 低 |
| **neat-freak V1.0 → V1.1** | 加"财务三表 + 季报 37 字段"作行业背景知识库 | 🟢 低 |

---

## 五、合规边界（Apache-2.0 红线）

> 复用 [apache-attribution-statements](apache-attribution-statements.md) §一 的 3 条强制条款：

| 条款 | a-stock-data 应用 | 落地 |
|------|--------------------|------|
| **第 4(a) 条** 再分发必须附 `LICENSE` 原文件 | 落 `dragon-engine/skills/a-stock-data-bridge/LICENSE`（10,760 B 已实拉确认） | ✅ 已规划 |
| **第 4(d) 条** NOTICE 必须保留上游 NOTICE + Modified 标注 | 落 `dragon-engine/skills/a-stock-data-bridge/NOTICE`，新增 "Modified by dragon-engine / 2026-07-21" 段 | ✅ 已规划 |
| **第 6 条 Trademark** 禁止暗示背书 | 28-10 agent.md 不得用 "a-stock-data 官方" / "官方授权" 等字样，仅 "Powered by simonlin1212/a-stock-data" | ✅ 已规划 |

**附 a-stock-data NOTICE 实拉片段**（从 LICENSE 头确认 Apache-2.0 完整版）：

```
                                 Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/
   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION
   ...（10,760 B 完整 Apache-2.0 标准文本，已确认无修改）...
```

### 5.1 数据源合规（非上游协议，而是第三方 API）

| 数据源 | 合规风险 | 天龙对策 |
|--------|----------|----------|
| mootdx / 通达信 | 客户端协议，公开开源 | ✅ 可用 |
| 腾讯财经 / 新浪财经 | 公开网页 API | ⚠️ **仅投研底稿 · 不直接外发原始 HTML** |
| 东财 datacenter/push2 | 公开 API 但有反爬 | ✅ 必须串行 ≥1s + 备胎降级 |
| 同花顺 / iwencai | 公开 API + 反爬 | ✅ 同上 |
| 巨潮 cninfo | 官方公告源 | ✅ 可用 |
| 百度股市通 | 公开 API | ⚠️ 同腾讯 |
| 雪球评论热榜 | 需 cookie | ⚠️ 走 `agent-reach` 账号态通路 |
| 同花顺问财 | NL 搜索 | ✅ 公开 |

**合规说明写入位置**：`dragon-engine/skills/a-stock-data-bridge/SKILL.md` §合规边界 + `NOTICE` 文件 + 28-10 agent.md §12

---

## 六、协同矩阵（天龙首次引入真实金融数据底座）

```
a-stock-data-bridge (Apache-2.0 ✅ · 43 端点 · 15 源)
   ├─► 28-10 财经数据底座师 ⭐NEW V1.0  ←—— 本阶段新建
   ├─► 28-01 文案 V10.4 (khazix-writer 财经子模块)
   ├─► 28-04 内容策划师 (财经选题)
   ├─► 35-02 laoli V13.3 (财经博主人设)
   ├─► 35-05 短视频 V10.4 (行情镜头)
   ├─► 35-07 横纵研究员 V1.1 (数据底稿)
   ├─► aihot V1.1 (财经热度榜)
   └─► neat-freak V1.1 (财务三表)

global-stock-data-bridge (Apache-2.0 ✅ · 17 端点 · 5 源)
   └─► 同上 8 个对接 + 美港股赛道

TradingAgents-astock (Apache-2.0 ✅ · 7 分析师)
   └─► 35-07 V1.2 多 Agent 辩论框架（候选 25.2）

async-task-pattern
   └─► 金融限流原语 (≥1s + 抖动 + 会话复用 + 备胎) ← 复用 4.1 节 5 个原语
```

---

## 七、累计 PASS 增量规划

| 阶段 | 测试 | 增量 | 累计 |
|------|------|------|------|
| 25 | a-stock-data-bridge 5 PASS | +5 | **611** |
| 25.1 | global-stock-data-bridge 3 PASS | +3 | **614** |
| 25.2 | TradingAgents-astock 4 PASS（多 Agent 辩论用例）| +4 | **618** |
| 25.3 | tickflow-stock-panel 评估（若开源）| TBD | TBD |

---

## 八、风险与未决项

1. **a-stock-data 8 个数据源（腾讯/新浪/东财/同花顺/iwencai/百度/巨潮/mootdx）的协议边界** —— Apache-2.0 仅约束仓库代码本身，**不约束**其内部调用的第三方 API，合规风险需 28-10 agent 运行时自我拦截
2. **V3.4.0 V3.3.1 文档触发范围收窄**（commit `8b11251`）—— 上游已主动收敛 description 防误触发，天龙 SKILL.md 包装层需要继承此策略
3. **a-stock-data 仍在快速迭代**（10 天前仍有 commit）—— **建议每月一次 skill-updater 检测**，纳入 26 阶段"金融底座持续追踪"任务
4. **TradingAgents-astock 多 Agent 框架**与天龙 35-07 V1.0 5 步工作流是**部分重叠**（都是"研究 → 判断"），需评估是否替代或并联

---

## 九、来源链接

- a-stock-data: <https://github.com/simonlin1212/a-stock-data>
- a-stock-data LICENSE: <https://raw.githubusercontent.com/simonlin1212/a-stock-data/main/LICENSE>（10,760 B Apache-2.0 完整版，2026-07-21 实拉）
- global-stock-data: <https://github.com/simonlin1212/global-stock-data>
- TradingAgents-astock: <https://github.com/simonlin1212/TradingAgents-astock>
- 上游 SKILL 风格（AI Coding Assistant）: <https://github.com/simonlin1212/a-stock-data/blob/main/SKILL.md>

---

## 十、阶段 25 / 25.1 / 25.2 实施计划（4 周时间线）

> **总目标**：4 周内把 simonlin1212 三件套全栈接入天龙引擎，累计 PASS **606 → ≥622**，新增 1 个 Agent（28-10）+ 3 个 Skill（a-stock-data-bridge / global-stock-data-bridge / trading-agents-astock-wrapper）+ 5 个既有 Agent 增量改造。

### 周 1（2026-07-22 → 2026-07-28）· 阶段 25 主集成

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D1-2 | `a-stock-data-bridge` 真源镜像（拉链解压）+ LICENSE 三件套落盘 + NOTICE "Modified by dragon-engine / 2026-07-21" | `dragon-engine/skills/a-stock-data-bridge/{SKILL.md, README.md, LICENSE, NOTICE}` | `wc -c LICENSE = 10760` |
| D3 | 43 端点 1:1 wrapper + `em_get()` 节流统一入口 + source_priority.json + fallback.yaml | `em_base.py` + `endpoints/` | `python em_base.py --doc` 自检 |
| D4 | pytest 5 PASS（端点 schema / 节流 / 备胎 / 错误处理 / Apache NOTICE）| `tests/test_em_base.py` | `pytest tests/ -v` 5/5 PASS |
| D5 | 28-10 财经数据底座师 V1.0 agent.md 落盘（已 ✅） + 28-01 V10.4 增量（khazix-writer 财经子模块）+ 35-05 V10.4 增量（行情镜头） | `agents/28-10-finance-data-base.md` ✅ + `agents/28-01-v104-finance.md` + `agents/35-05-v104-finance.md` | 文档齐 |
| D6-7 | 集成测试：28-10 跑茅台（600519.SH）+ 苹果（AAPL，mock）→ 输出 4 类底稿 | `moutai_base.md` + `aapl_pe.json` | 5 项质检 + 1 视觉示意 |

### 周 2（2026-07-29 → 2026-08-04）· 阶段 25.1 美港股

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D8-9 | `global-stock-data-bridge` 真源镜像 + LICENSE + NOTICE | `dragon-engine/skills/global-stock-data-bridge/{SKILL.md, ...}` | 同 D1-2 |
| D10 | 17 端点 wrapper（含 MA/MACD/RSI/KDJ/布林带技术指标层）| `em_global.py` | pytest 3 PASS |
| D11 | 28-10 V1.0 → V1.1（增美港股赛道 4 类底稿） | `agents/28-10-v11-finance.md` | 文档齐 |
| D12-14 | 集成测试：苹果（AAPL）+ 阿里（BABA）+ 港股腾讯（0700.HK）| 3 个美港股底稿 | 3 PASS |

### 周 3（2026-08-05 → 2026-08-11）· 阶段 25.2 TradingAgents-astock

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D15-16 | `trading-agents-astock` 真源镜像 + LICENSE + NOTICE | `dragon-engine/skills/trading-agents-astock-wrapper/` | 同上 |
| D17 | 35-07 V1.0 → V1.1（加多 Agent 辩论框架）| `agents/35-07-v11-multidebate.md` | 文档齐 |
| D18 | pytest 4 PASS（7 分析师角色 + bull/bear debate + risk + decision）| `tests/test_trading_agents.py` | 4/4 PASS |
| D19-21 | 集成测试：3 个真实股票的多 Agent 辩论剧本 | 3 个 Markdown 辩论稿 | 1 人工 review + 3 PASS |

### 周 4（2026-08-12 → 2026-08-18）· 阶段 25.3 + 总验收

| 工作日 | 任务 | 交付物 | 验证 |
|---|---|---|---|
| D22 | `tickflow-stock-panel` 评估（开源协议 + 选股面板能力，如可用）| 评估报告 | go / no-go |
| D23 | 28-01 V10.4 / 35-05 V10.4 / 35-07 V1.1 / aihot V1.1 / neat-freak V1.1 5 个 Agent 升级 PR | 5 个新版 agent.md | `git diff` |
| D24 | 合规复审（apache-attribution §9.5 红线检查表 12 项）| 合规矩阵 | 12/12 |
| D25-26 | 累计 PASS 校验：606 → ≥618（+12 by stage 25/25.1/25.2） + MEMORY.md 更新 | MEMORY.md V25 row | `python pytest --co -q` |
| D27-28 | 文档归档 + 主题文件最终版 + announce.md | `a-stock-data-integration.md` V1.0 + announce.md | 文件齐 |

### 4 周时间线 · 累计 PASS 增量预测

```
606 ────► +5 (stage 25 a-stock-data-bridge)  ─► 611
              │
              └── +3 (stage 25.1 global-stock-data)  ─► 614
                       │
                       └── +4 (stage 25.2 trading-agents)  ─► 618
                                │
                                └── (stage 25.3 tickflow 评估 · 可选)

累计新增 ≥12 PASS；新增 ≥3 个 skill；新建 1 个 agent (28-10) + 改造 5 个 agent
```

### 关键决策点 · 用户拍板项

| 项 | 选项 | 推荐 |
|---|---|---|
| **D1 `runtime.conf`** | Node CLI / Python CLI / 双 CLI | **(推荐) 双 CLI** —— 与 anysearch 风格一致 + 便于 async-task-pattern 包装 |
| **D3 `em_get()` 节流参数** | ≥1s + 抖动 / ≥0.5s + 抖动 / ≥2s 严苛 | **(推荐) ≥1s + 抖动** —— 严格沿用上游默认值，避开反爬 |
| **D5 28-01 增量方式** | khazix-writer 加子模块 / 28-01 内嵌 28-10 / 拆 V10.4 | **(推荐) khazix-writer 子模块** —— 影响面最小 |
| **D11 28-10 V1.1** | 美港股 4 底稿 / 美港股 2 底稿 + 通用研报 | **(推荐) 美港股 4 底稿（与 A 股对齐）** |
| **D17 35-07 V1.1** | 完全替代 V1.0 5 步 / 与 V1.0 5 步并行 / 仅做补充辩论 | **(推荐) 并行** —— V1.0 5 步为主路径，V1.1 多 Agent 辩论为可选增强 |
| **D22 25.3 是否启动** | 启动 / 延后到 26 阶段 | **(推荐) 评估通过即启动（≤ 3 天），否则延后** |
| **D24 NOTICE 同步** | 全量同步 / 关键 NOTICE 同步 | **(推荐) 全量同步** —— 累计合规基线 |

### 风险与回滚预案

| 风险 | 影响 | 回滚 |
|------|------|------|
| 8-10 个第三方 API 反爬 | 数据缺失 | 走 3 官方备胎兜底 |
| Apache-2.0 NOTICE 漏写 | 协议违规 | D24 复审 + 红线检查表 |
| TradingAgents-astock 与 35-07 部分重叠 | 认知混乱 | V1.1 并行而非替代 |
| 35-05 V10.4 行情镜头素材缺失 | 文生视频失败 | 留 V10.3 兜底 |
| simonlin1212 上游快速迭代（10 天 1 commit） | 包装层落后 | 月度 skill-updater 检测 |

### 验收门槛（4 周末）

- [ ] 累计 PASS ≥618
- [ ] 新增 28-10 + 改造 5 agent 全部上线
- [ ] Apache-2.0 红线检查表 12/12 PASS
- [ ] 4 个端到端场景通过（茅台/苹果/多 Agent 辩论/合规底线）
- [ ] MEMORY.md / apache-attribution / a-stock-data-integration 三件套最终版
- [ ] 主题文件 27 → **30 个**（+3 + 改造文件）
- [ ] GitHub ⭐ 11,284+ 增量已记录

---

> **下次同步点**：周 1 末（D7, 2026-07-28）提交周报，含 5 PASS 实证 + 28-10 上线确认；如延期超过 3 天自动触发 §D27 复审。