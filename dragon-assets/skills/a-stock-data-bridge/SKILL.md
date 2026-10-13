---
name: a-stock-data-bridge
description: A股全栈数据底座桥接 — simonlin1212/a-stock-data V3.4.0 (Apache-2.0) 43 端点 + 15 数据源的 wrapper + em_get() 节流统一入口 · 投研底稿供 28-10 / 28-01 / 35-05 / 35-07 下游
version: 1.0
base_version: 0.0
category: data-center
department: 数据中心-财经底座部
license: Apache-2.0  (与上游一致)
upstream:
  name: simonlin1212/a-stock-data
  version: V3.4.0
  url: https://github.com/simonlin1212/a-stock-data
  license: Apache-2.0
  stars: 7555
  endpoints: 43
  sources: 15
modified: 2026-07-21
modified_by: 天龙引擎 dragon-engine
triggers:
  - "[@财经底座]"
  - "[@28-10]"
  - "a-stock-data"
  - "A股数据"
  - "行情层"
  - "研报层"
  - "信号层"
  - "资金面"
  - "公告层"
  - "打板数据"
  - "龙虎榜"
  - "北向资金"
  - "融资融券"
  - "财报三表"
  - "投研底稿"
  - "财务底稿"
  - "个股深度"
  - "行业横评"
  - "资金流事件"
  - "公告事件"
  - "em_get"
  - "em_base"
---

# a-stock-data-bridge · A 股全栈数据底座桥接 V1.0

> **TL;DR**：基于 [simonlin1212/a-stock-data V3.4.0](https://github.com/simonlin1212/a-stock-data)（Apache-2.0 ✅ · 7,555 ⭐ · 43 端点 + 15 数据源）二次开发。提供 `em_get()` 统一节流入口 + 43 端点 wrapper + 3 官方备胎降级 + 5 层防封（≥1s 限流 + 抖动 + 会话复用 + 优先级排序 + 错误码识别），输出 4 类底稿（个股深度 / 行业横评 / 资金流事件 / 公告事件）供天龙 8 个下游岗位（28-10 / 28-01 V10.4 / 28-04 / 35-02 V13.3 / 35-05 V10.4 / 35-07 V1.1 / aihot V1.1 / neat-freak V1.1）调用。

## 零 API key · 零付费门槛

> **关键事实**：本 skill **完全不需要任何 API key**。全部 13 个公开数据源（Sina / 腾讯 / 东方财富 / 同花顺 / mootdx / 乌龟量化 / 网易 / 新浪财经 / 巨潮 cninfo 等）都是公开 HTTP 端点，**无需注册 / 无需鉴权 / 无需付费**。
>
> 这是它与 alpha vantage / polygon / tiingo 这类 SaaS API 的本质区别——**a-stock-data 不是中间商服务，是工具包**。

### 与 SaaS API 的对比

| 维度 | SaaS API（alpha vantage / polygon） | a-stock-data（本 skill） |
|---|---|---|
| 模式 | 你调我的 server | 我直接爬公开 HTTP 端点 |
| API key | **必需**（鉴权） | **不需要** |
| 速率限制 | 5/min 免费 · 1200/day 付费 | 仅礼貌节流（≥1s，无服务端墙）|
| 月费 | $25 - $200 | **$0** |
| 注册账号 | 必需 | 不需要 |
| 免费 tier | 是 | **整个数据集都是免费的**（不是"有免费额度"）|

### 13 个公开数据源清单（全部免 key）

| 数据源 | 类型 | 免费状态 | 用途 |
|--------|------|---------|------|
| **Sina** | HTTP | ✅ 免 key | 实时行情 |
| **腾讯** | HTTP | ✅ 免 key | 实时行情 |
| **东方财富** push2 | HTTP | ✅ 免 key | 研报 / 资金流 |
| **同花顺** | HTTP | ✅ 免 key | 财务数据 / 强势股 |
| **mootdx**（通达信）| TCP | ✅ 免 key | 标准行情协议 |
| **乌龟量化** | HTTP | ✅ 免 key | 历史数据 |
| **网易** | HTTP | ✅ 免 key | 资金流 |
| **新浪财经** | HTTP | ✅ 免 key | 公告 / 财报 |
| **巨潮 cninfo** | HTTP | ✅ 免 key（官方）| 公告原文 |
| **iwencai** 问财 | HTTP | ⚠️ 自然语言高级功能部分收费 | 选股筛选 |
| **百度** | HTTP | ✅ 免 key | K 线 / 概念板块 |
| **雪球** | HTTP | ⚠️ 需 cookie 态（走 agent-reach 通路）| 评论热榜 |
| **东财 datacenter** | HTTP | ✅ 免 key | 估值 / 同业对比 |

**13 个源中 12 个完全免费**——仅 iwencai 问财自然语言筛选的"高级筛选"和雪球账号态评论热榜有特殊要求。

### 软约束（礼貌请求，非付费墙）

唯一限制是**节流**——建议 ≥1s + 抖动（避免 IP 被公开网站限速）。这不是 API 限制，是上游源网站的礼貌请求。**没有月配额 / 没有速率墙 / 没有付费升级路径**。

### 一句话告诉用户

> "a-stock-data-bridge 跑 43 端点零 API key——13 个公开源直连，pip install requests pandas PyYAML 即可，无需注册任何服务。"

---

## L0: 一句话描述（≤15 字）

**A 股 43 端点全栈数据底座**

## L1: 使用场景

用户做**A股个股 / 行业 / 资金 / 公告**内容时使用：

1. **4 类底稿**：个股深度（L1+L3+L4+L6+L7）/ 行业横评（L2+L6+L9+L10）/ 资金流事件（L3+L4+L8）/ 公告事件（L6+L7）
2. **统一节流入口** `em_get()`：串行 ≥1s + 抖动 + 会话复用
3. **3 官方备胎降级**：主源失败自动切官方备胎（非静默）
4. **mootdx 0.11.x 兼容**：BESTIP 空串崩溃防护
5. **下游 8 岗位**：28-10 主对接 + 7 个增量 Agent

## L2: 详细文档

### 10 层架构（A 股）

| 层 | 名称 | 端点数 | 数据源 |
|----|------|-------|--------|
| **L1** | 行情层 | K线(含 MA5/10/20) · 五档盘口 · PE/PB/市值 · 指数/ETF | mootdx / 腾讯 / 百度 |
| **L2** | 研报层 | 个股 + 行业研报列表 · PDF 下载 · 一致预期 · iwencai NL 搜索 | 东财 / 同花顺 / iwencai |
| **L3** | 信号层 | 强势股 · 题材归因 · 北向资金 · 概念板块 · 资金流向 · 龙虎榜 · 解禁 | 同花顺 / 百度 / 东财 |
| **L4** | 资金面 | 融资融券 · 大宗交易 · 股东户数 · 分红送 · 分钟级资金流 | 东财 / push2 |
| **L5** | 新闻层 | 东财个股新闻 · 全球资讯 | 东财 |
| **L6** | 基础数据 | mootdx 季报 37 字段 · F10 九大类 · 财报三表 | mootdx / 东财 / 新浪 |
| **L7** | 公告层 | 巨潮 cninfo + mootdx 沪深北全量公告 | 巨潮 / mootdx |
| **L8** | 打板层 | 涨停板战法数据 · 龙头识别 · 板块联动 | 同花顺 / 东财 |
| **L9** | ETF期权 | ETF 净值 · 期权 Greeks · 隐含波动率 | 东财 / 上交所 |
| **L10** | 舆情互动 | 雪球评论热榜 · 同花顺问财 · 互动易问答 | 雪球 / 同花顺 |

### 5 层防封（V1.0 自主实现，对齐上游默认值）

```
请求 → [1] 节流门 (≥1s + 抖动)
       ├─ 触发限速 → [2] 退避重试 (max 3)
       ├─ 主源失败 → [3] 切备胎 (按优先级)
       ├─ 备胎失败 → [4] 标记数据缺失（不静默）
       └─ 错误码识别 → [5] 错误码决策树
           ├─ BESTIP 空串 → 切腾讯
           ├─ 参数缺失 → 自动补默认
           └─ 协议 404 → 标记 deprecated
```

### 端点封装总表（43 端点 · 1:1 映射上游 V3.4.0）

| ID | 端点名 | 层 | 数据源（主/备 1/备 2/备 3）| 节流 |
|----|--------|----|------|------|
| E01 | `kline_with_ma` | L1 | mootdx / 腾讯 / 百度 / 东财 | ≥1s |
| E02 | `five_level_quote` | L1 | 腾讯 / 百度 / 东财 / 新浪 | ≥1s |
| E03 | `pe_pb_market_cap` | L1 | 东财 / 新浪 / 腾讯 / 百度 | ≥1s |
| E04 | `index_etf_quote` | L1 | 东财 / 腾讯 / 百度 / 同花顺 | ≥1s |
| E05 | `minute_kline` | L1 | mootdx / 腾讯 / 百度 | ≥1s |
| E06 | `research_report_list` | L2 | 东财 / 同花顺 / iwencai | ≥1s |
| E07 | `research_report_pdf` | L2 | 东财 / 同花顺 / iwencai | ≥2s |
| E08 | `consensus_eps` | L2 | 东财 / 同花顺 | ≥1s |
| E09 | `iwencai_nl_search` | L2 | iwencai | ≥2s |
| E10 | `industry_report` | L2 | 东财 / 同花顺 | ≥1s |
| E11 | `strong_stock_signal` | L3 | 同花顺 / 百度 | ≥1s |
| E12 | `theme_attribution` | L3 | 同花顺 / 东财 | ≥1s |
| E13 | `north_bound_flow` | L3 | 东财 push2 / 同花顺 | ≥1s |
| E14 | `concept_sector_flow` | L3 | 东财 / 同花顺 | ≥1s |
| E15 | `money_flow_rank` | L3 | 东财 / 同花顺 | ≥1s |
| E16 | `dragon_tiger_list` | L3 | 东财 datacentre / 同花顺 | ≥1s |
| E17 | `restricted_unlock` | L3 | 东财 / 同花顺 | ≥1s |
| E18 | `margin_balance` | L4 | 东财 push2 / 同花顺 | ≥1s |
| E19 | `block_trade` | L4 | 东财 / 同花顺 | ≥1s |
| E20 | `shareholder_count` | L4 | 东财 / 同花顺 | ≥1s |
| E21 | `dividend_history` | L4 | 东财 / 同花顺 | ≥1s |
| E22 | `minute_money_flow` | L4 | 东财 push2 | ≥1s |
| E23 | `stock_news` | L5 | 东财 | ≥1s |
| E24 | `global_news` | L5 | 东财 | ≥1s |
| E25 | `quarterly_report_37fields` | L6 | mootdx / 东财 / 新浪 | ≥1s |
| E26 | `f10_nine_categories` | L6 | 东财 / 新浪 | ≥1s |
| E27 | `financial_3statements` | L6 | 东财 / 新浪 / mootdx | ≥1s |
| E28 | `cninfo_announcement` | L7 | 巨潮 / mootdx | ≥1s |
| E29 | `cninfo_pdf` | L7 | 巨潮 | ≥2s |
| E30 | `limit_up_board` | L8 | 同花顺 / 东财 | ≥1s |
| E31 | `limit_up_leader` | L8 | 同花顺 / 东财 | ≥1s |
| E32 | `sector_linkage` | L8 | 东财 / 同花顺 | ≥1s |
| E33 | `etf_nav` | L9 | 东财 | ≥1s |
| E34 | `etf_holdings` | L9 | 东财 | ≥1s |
| E35 | `option_chain` | L9 | 上交所 / 东财 | ≥2s |
| E36 | `option_greeks` | L9 | 上交所 / 东财 | ≥2s |
| E37 | `xueqiu_hot_rank` | L10 | 雪球（账号态走 agent-reach）| ≥2s |
| E38 | `iwencai_qa` | L10 | 同花顺问财 | ≥2s |
| E39 | `interactive_qa` | L10 | 巨潮 / 上交所互动易 | ≥1s |
| E40 | `valuation_full` | L6 | 东财 / 新浪 | ≥1s |
| E41 | `north_top10` | L3 | 东财 push2 | ≥1s |
| E42 | `south_bound_flow` | L3 | 东财 push2 | ≥1s |
| E43 | `tickflow_auction` | L8 | 同花顺 / 东财 | ≥1s |

### 4 类底稿模板（与 28-10 5 步工作流对齐）

| 类型 | 端点组合 | 产出 |
|------|----------|------|
| **个股深度** | L1+L3+L4+L6+L7（默认 8-12 端点） | 6-12 张数据表 + 时间轴 + 资金热力图 |
| **行业横评** | L2+L6+L9+L10 | 行业矩阵表 + ETF 资金流向 |
| **资金流事件** | L3+L4+L8 | 资金流向瀑布图 + 龙虎榜 / 北向 / 涨停识别 |
| **公告事件** | L6+L7 | 公告原文 + 财报三表对比 + 解读提要 |

### 退出码契约（em_check.py）

| 退出码 | 含义 |
|--------|------|
| 0 | [PASS] 5 项必检全过 |
| 1 | [FAIL] 至少 1 项必检未过 |
| 2 | [WARN] 仅推荐项未过 |
| 3 | [ERROR] 调用方式错误（参数 / 端点名 / 股票代码）|

## 使用示例

```bash
# 1. 个股深度底稿（贵州茅台）
python em_base.py --type stock \
  --symbol "600519.SH" \
  --layers L1,L3,L4,L6,L7 \
  --output-md moutai_base.md \
  --output-json moutai_base.json

# 2. 行业横评底稿（白酒板块）
python em_base.py --type industry \
  --industry "白酒" \
  --layers L2,L6,L9,L10

# 3. 资金流事件底稿（北向资金流入 TOP20）
python em_base.py --type event \
  --event "north_bound_top20" \
  --date 2026-07-21

# 4. 公告事件底稿（茅台 2026Q2 业绩公告）
python em_base.py --type announcement \
  --symbol "600519.SH" \
  --since "2026-07-01"

# 5. 5 项质检
python em_check.py moutai_base.md

# 6. 强制模拟主源失败（备胎降级测试）
python em_base.py --type stock --symbol "600519.SH" \
  --force-fallback \
  --dry-run

# 7. 端点 schema 自检（不实际发请求）
python em_base.py --doc --endpoint kline_with_ma
```

## 合规边界

> 本 skill 集成自上游 Apache-2.0 仓库，且自主调用 8-10 个第三方财经 API。**Apache-2.0 仅约束本 skill 自身代码，不约束第三方 API**。
> **关键**：本 skill **零 API key**——13 个公开数据源（Sina / 腾讯 / 东财 / 同花顺 / mootdx / 巨潮等）全部免 key 直连，详见上文"零 API key · 零付费门槛"段。

| API | 协议状态 | 天龙对策 |
|-----|---------|----------|
| mootdx / 通达信 | 客户端协议，公开开源 | ✅ 可用（免 key）|
| 腾讯 / 百度 / 新浪 | 公开网页 API | ⚠️ 仅投研底稿用，不直接外发原始 HTML（免 key）|
| 东财 datacenter/push2 | 公开 API + 反爬 | ⚠️ 必须节流 ≥1s + 备胎降级（免 key）|
| 同花顺 / iwencai | 公开 API + 反爬 | ⚠️ 同上（iwencai NL 高级筛选部分收费）|
| 巨潮 cninfo | 官方公告源 | ✅ 可用（免 key）|
| 雪球评论 | 需 cookie | ⚠️ 走 `agent-reach` 账号态通路，**不**与匿名摸底盘混用 |

## Attribution

本 skill 集成自上游 [simonlin1212/a-stock-data](https://github.com/simonlin1212/a-stock-data) V3.4.0。

**上游版权**：simonlin1212, 2026
**上游 LICENSE**：Apache License 2.0 — 详见 [`./LICENSE`](./LICENSE) 或 https://www.apache.org/licenses/LICENSE-2.0
**上游 NOTICE**：[`./NOTICE`](./NOTICE)

**本 skill 修改**（按 Apache-2.0 §4(d)）：
1. 包装 43 端点为 Python wrapper，统一返回 Markdown + JSON 双产物
2. 新增 `em_get()` 统一节流入口（≥1s + 抖动 + 会话复用）
3. 新增 `source_priority.json`（数据源优先级映射）
4. 新增 `fallback.yaml`（3 官方备胎 + 错误码决策树）
5. 新增 4 类底稿模板（个股 / 行业 / 资金 / 公告）
6. 新增 `em_check.py`（5 必检 + 3 推荐质检）

按 Apache-2.0 §4(d)，本 skill 的 NOTICE 文件已保留上游 simonlin1212 的归属声明，并标注 "Modified by 天龙引擎 dragon-engine, 2026-07-21"。

**V1.1 增量修改**（天龙自研 · 2026-08-03）：

1. **真源接通（P1）**：新增 `live_fetch.py`（43 端点路由表 → 上游 V3.4.0 真函数），把 `em_base.py` 的 stub `primary_call` 替换为真源调用
2. **节流实测**：`requirements.txt` 加 `pandas>=1.5.0` + `lxml>=4.9.0`（上游隐式依赖）
3. **质检闭环**：5 必检 + 3 推荐 + 4 类退出码契约 + 5 pytest 单测
4. **零 key 文档化**：SKILL.md 加"零 API key · 零付费门槛"段（13 源清单 + SaaS 对比 + 软约束说明）

---

## 版本信息

- **Version**: 1.0
- **Base**: V0.0（新 skill）
- **Upgrade Date**: 2026-07-21
- **Upgrade Trigger**: simonlin1212/a-stock-data V3.4.0 集成
- **Author**: 天龙引擎集成
- **License**: Apache-2.0（与上游一致）
- **Triggers**: 21 个新增关键词
