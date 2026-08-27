---
name: global-stock-data-bridge
description: 美股港股全栈数据底座桥接 — simonlin1212/global-stock-data V1.0.1 (Apache-2.0) 17 端点 + 5 数据源 + 7 层架构 + 技术指标层 (MA/MACD/RSI/KDJ/布林带)
version: 1.0
base_version: 0.0
category: data-center
department: 数据中心-财经底座部
license: Apache-2.0
upstream:
  name: simonlin1212/global-stock-data
  version: V1.0.1
  url: https://github.com/simonlin1212/global-stock-data
  license: Apache-2.0
  stars: 1199
  endpoints: 17
  sources: 5
  architecture: 7-layer
modified: 2026-07-27
modified_by: 天龙引擎 dragon-engine
triggers:
  - "[@美港股底座]"
  - "[@28-10]"
  - "美股数据"
  - "港股数据"
  - "US stock data"
  - "HK stock data"
  - "global-stock-data"
  - "美股 K 线"
  - "港股 K 线"
  - "AAPL 数据"
  - "TSLA 数据"
  - "腾讯 0700.HK"
  - "阿里 BABA"
  - "美股财报"
  - "港股财报"
  - "美股估值"
  - "PE ratio 美股"
  - "技术指标"
  - "MA / MACD / RSI / KDJ / 布林带"
  - "美股 ETF"
  - "港股 ETF"
---

# global-stock-data-bridge · 美港股全栈数据底座桥接 V1.0

> **TL;DR**：基于 [simonlin1212/global-stock-data V1.0.1](https://github.com/simonlin1212/global-stock-data)（Apache-2.0 ✅ · 1,199 ⭐ · 17 端点 + 5 数据源 + 7 层架构 + 技术指标层）二次开发。提供 `em_global_get()` 统一节流入口 + 17 端点 wrapper + 5 数据源备胎降级 + 美股/港股 4 类底稿（市值估值 / 财报三表 / 技术面 / 港股南向资金），供天龙 8 个下游岗位（28-10 V1.1 / 28-01 V10.4 / 28-04 / 35-02 V13.3 / 35-05 V10.4 / 35-07 V1.1 / aihot V1.1 / neat-freak V1.1）调用。

## 零 API key · 95% 免费

> **关键事实**：本 skill **5 个数据源中 4 个完全免 key**（Yahoo Finance / SEC EDGAR / HKEXnews / FRED），**仅 1 个需要 key**（Alpha Vantage，但有慷慨免费额度：5 calls/min + 500 calls/day）。
>
> 与 a-stock-data-bridge（A 股侧 100% 免 key）相比，美港股侧多了一个可选付费源（Alpha Vantage）。但即使完全不配任何 key，本 skill 的 16/17 端点仍可正常工作（仅 G03 分钟级需 Alpha Vantage）。

### 与 SaaS API 的对比

| 维度 | SaaS API（bloomberg / refinitiv）| global-stock-data（本 skill）|
|---|---|---|
| 模式 | 你调我的 server | 我直接爬公开 HTTP 端点 |
| API key | **必需**（鉴权） | **4/5 源不需要**（Alpha Vantage 可选）|
| 速率限制 | 严格配额 | 公开源礼貌节流（≥1s）|
| 月费 | $1,000 - $20,000 | **$0**（默认配置）/ $0（Alpha Vantage 免费额度）|
| 注册账号 | 必需 + 实名 + 机构认证 | **不需要** |
| 数据延迟 | 实时 | Yahoo 15min 延迟 / SEC EDGAR 实时 / FRED 1 天 |

### 5 个数据源清单

| 数据源 | 类型 | 是否需要 key | 免费状态 | 用途 |
|--------|------|------------|---------|------|
| **Yahoo Finance** | 公开爬取 | ❌ 不需要 | ✅ 完全免费 | 行情 + 估值 + 同业对比 |
| **SEC EDGAR** | 官方开放 | ❌ 不需要 | ✅ 完全免费 | 美股财报 + 10-K/10-Q/8-K 公告 |
| **HKEXnews** | 官方开放 | ❌ 不需要 | ✅ 完全免费 | 港股公告 + 财报 |
| **FRED** | 官方开放 | ❌ 不需要 | ✅ 完全免费 | 经济数据 + Beta 计算 |
| **Alpha Vantage** | 官方 API | ⚠️ **可选 key** | ✅ **免费 tier 慷慨**（5/min · 500/day）| 分钟级 OHLCV + 国际市场 |

### Alpha Vantage 免费额度（详细）

虽然需要 key，但完全够用：
- **免费 tier**：5 calls/min · 500 calls/day · **不需要付费**
- **注册地址**：https://www.alphavantage.co/support/#api-key （仅需邮箱）
- **本 skill 用法**：仅 G03 `intraday_ohlcv`（分钟级）和 G13 `global_news` 部分功能需此 key
- **不配 key 时**：默认 Yahoo Finance 兜底（15min 延迟），功能完整

### 软约束（礼貌请求，非付费墙）

唯一限制是**节流**——建议 ≥1s + 抖动（避免 IP 被 Yahoo 限速）。这不是 API 限制，是上游源网站的礼貌请求。**没有月配额 / 没有速率墙**（除 Alpha Vantage 的官方 tier 上限）。

### 一句话告诉用户

> "global-stock-data-bridge 跑 17 端点 95% 零 API key——SEC/HKEX/FRED/Yahoo 全免 key 直连，仅 Alpha Vantage（5/min 免费）可选配。pip install requests pandas PyYAML 即可。"

---

## L0: 一句话描述（≤15 字）

**美港股 17 端点全栈数据底座**

## L1: 使用场景

用户做**美股 / 港股 / 中概股 / 全球估值 / 技术面分析**内容时使用：

1. **7 层架构**：行情层 / 财务层 / 技术指标层 / 新闻层 / 公告层 / 估值层 / 同业对比层
2. **4 类底稿**：市值估值 / 财报三表 / 技术面分析 / 港股南向资金
3. **统一节流入口** `em_global_get()`：串行 ≥1s + 抖动 + 会话复用
4. **5 数据源备胎降级**：Yahoo Finance / Alpha Vantage / FRED / SEC / 港交所
5. **下游 8 岗位**：28-10 V1.1 主对接 + 7 个增量 Agent

## L2: 详细文档

### 7 层架构（美港股）

| 层 | 名称 | 端点数 | 数据源 |
|----|------|-------|--------|
| **L1** | 行情层 | OHLCV / 历史价格 / 实时报价 / 复权因子 | Yahoo Finance / Alpha Vantage |
| **L2** | 财务层 | 财报三表 / 季报 37 字段 / 12 个月财务摘要 | SEC / 公司公告 |
| **L3** | 技术指标层 | MA / MACD / RSI / KDJ / 布林带 | 计算层（基于 L1）|
| **L4** | 新闻层 | 全球财经新闻 / 个股新闻 / 公告 RSS | Reuters / Bloomberg / 公司 IR |
| **L5** | 公告层 | SEC 8-K / 10-Q / 港交所披露易 | SEC EDGAR / HKEXnews |
| **L6** | 估值层 | PE / PB / PS / EV/EBITDA / 股息率 / Beta | 计算层（基于 L2）|
| **L7** | 同业对比 | 同行业 PE / 估值历史百分位 / 板块排名 | Yahoo Finance / FRED |

### 17 端点总表（1:1 映射上游 V1.0.1）

| ID | 端点名 | 层 | 数据源（主/备 1/备 2）| 节流 | 说明 |
|----|--------|----|------|------|------|
| G01 | `quote_realtime` | L1 | Yahoo Finance / Alpha Vantage / FRED | ≥1s | 实时报价（含盘前盘后） |
| G02 | `historical_ohlcv` | L1 | Yahoo Finance / Alpha Vantage | ≥1s | 历史日线 / 周线 / 月线 |
| G03 | `intraday_ohlcv` | L1 | Alpha Vantage / Yahoo Finance | ≥1s | 分钟级 OHLCV |
| G04 | `adjusted_close` | L1 | Yahoo Finance | ≥1s | 复权因子 + 分红除权调整 |
| G05 | `financial_3statements` | L2 | SEC EDGAR / 公司 IR / Yahoo Finance | ≥1s | 财报三表（资产负债表/利润表/现金流量表） |
| G06 | `quarterly_37fields` | L2 | SEC EDGAR | ≥1s | 季报 37 字段 |
| G07 | `ttm_summary` | L2 | SEC EDGAR / 公司 IR | ≥1s | 12 个月滚动摘要 |
| G08 | `ma_indicator` | L3 | 计算层（基于 G02） | ≥1s | MA5/10/20/60/120/250 |
| G09 | `macd_indicator` | L3 | 计算层 | ≥1s | MACD（12,26,9） |
| G10 | `rsi_indicator` | L3 | 计算层 | ≥1s | RSI（14） |
| G11 | `kdj_indicator` | L3 | 计算层 | ≥1s | KDJ（9,3,3） |
| G12 | `bollinger_bands` | L3 | 计算层 | ≥1s | 布林带（20,2） |
| G13 | `global_news` | L4 | Reuters / Bloomberg / Yahoo Finance | ≥1s | 全球财经新闻 |
| G14 | `stock_news` | L4 | Reuters / 公司 IR | ≥1s | 个股新闻 |
| G15 | `sec_filing` | L5 | SEC EDGAR / HKEXnews | ≥2s | 公告检索（10-K/10-Q/8-K） |
| G16 | `valuation_ratios` | L6 | 计算层（基于 G05+G07） | ≥1s | PE/PB/PS/EV/EBITDA/股息率/Beta |
| G17 | `peer_compare` | L7 | Yahoo Finance / FRED | ≥1s | 同业对比 + 行业百分位 |

### 5 数据源优先级

| tier | 数据源 | 用途 | 反爬风险 |
|------|--------|------|----------|
| **1** | Yahoo Finance | 行情 + 估值 + 同业对比 | 中（建议 ≥1s） |
| **2** | Alpha Vantage | 行情 + 分钟级 + 国际市场 | 低（需 API key） |
| **3** | SEC EDGAR | 美股财报 + 公告 | 低（官方权威） |
| **4** | HKEXnews | 港股公告 + 财报 | 低（官方权威） |
| **5** | FRED | 经济数据 + Beta 计算 | 低 |

### 4 类底稿模板（与 28-10 V1.1 对齐）

| 类型 | 端点组合 | 产出 |
|------|----------|------|
| **市值估值底稿** | G01 + G04 + G16 + G17 | PE/PB/PS 历史百分位 + 同业对比 |
| **财报三表底稿** | G05 + G06 + G07 | 财报三表 + 季报 37 字段 + TTM |
| **技术面底稿** | G02 + G08-G12 | MA/MACD/RSI/KDJ/布林带 5 指标图 |
| **港股南向资金底稿** | G15 + G14 | 港股通净流入 + 个股榜单 |

### 退出码契约（em_global_check.py）

| 退出码 | 含义 |
|--------|------|
| 0 | [PASS] 5 必检全过 |
| 1 | [FAIL] 至少 1 项必检未过 |
| 2 | [WARN] 仅推荐项未过 |
| 3 | [ERROR] 调用方式错误 |

## 使用示例

```bash
# 1. 苹果（AAPL）市值估值底稿
python em_global.py --type valuation --symbol AAPL \
  --layers L1,L6,L7 \
  --output-md aapl_valuation.md

# 2. 阿里巴巴（BABA）财报三表底稿
python em_global.py --type financials --symbol BABA \
  --layers L2 \
  --output-md baba_financials.md

# 3. 腾讯（0700.HK）技术面底稿（含 MA/MACD/RSI/KDJ/布林带）
python em_global.py --type technical --symbol 0700.HK \
  --layers L1,L3 \
  --output-md tencent_technical.md

# 4. 5 项质检
python em_global_check.py aapl_valuation.md

# 5. 强制备胎降级
python em_global.py --type valuation --symbol AAPL \
  --force-fallback --dry-run

# 6. 端点 schema 自检
python em_global.py --doc --endpoint valuation_ratios
```

## 合规边界

> 本 skill 集成自上游 Apache-2.0 仓库，且调用 5 个第三方数据源（Yahoo Finance / Alpha Vantage / SEC EDGAR / HKEXnews / FRED）。
> **关键**：5 个源中 **4 个完全免 key**（Yahoo Finance / SEC EDGAR / HKEXnews / FRED），**仅 Alpha Vantage 可选**（免费 tier 5/min · 500/day 已够用）。详见上文"零 API key · 95% 免费"段。

| 数据源 | 协议状态 | 天龙对策 |
|--------|---------|----------|
| Yahoo Finance | 公开 API + 中反爬 | ⚠️ 仅投研底稿用，≥1s 节流（免 key）|
| Alpha Vantage | 公开 API（**可选 key**）| ⚠️ 仅 G03 分钟级需 key（免费 tier 够用）|
| SEC EDGAR | 官方权威 | ✅ 可用（免 key）|
| HKEXnews | 官方权威 | ✅ 可用（免 key）|
| FRED | 官方权威 | ✅ 可用（免 key）|

## Attribution

本 skill 集成自上游 [simonlin1212/global-stock-data](https://github.com/simonlin1212/global-stock-data) V1.0.1。

**上游版权**：simonlin1212, 2026
**上游 LICENSE**：Apache License 2.0 — 详见 [`./LICENSE`](./LICENSE) 或 https://www.apache.org/licenses/LICENSE-2.0
**上游 NOTICE**：[`./NOTICE`](./NOTICE)

**本 skill 修改**（按 Apache-2.0 §4(d)）：
1. 包装 17 端点为 Python wrapper，统一返回 Markdown + JSON 双产物
2. 新增 `em_global_get()` 统一节流入口（≥1s + 抖动 + 会话复用）
3. 新增 `source_priority.json`（5 数据源优先级映射）
4. 新增 `fallback.yaml`（备胎降级 + 错误码决策树）
5. 新增 4 类底稿模板（市值估值 / 财报三表 / 技术面 / 港股南向）
6. 新增 `em_global_check.py`（5 必检 + 3 推荐质检）
7. 新增技术指标层（L3）的计算层实现（基于 L1 历史数据）

按 Apache-2.0 §4(d)，本 skill 的 NOTICE 文件已保留上游 simonlin1212 的归属声明，并标注 "Modified by 天龙引擎 dragon-engine, 2026-07-27"。

**V1.1 增量修改**（天龙自研 · 2026-08-03）：

1. **零 key 文档化**：SKILL.md 加"零 API key · 95% 免费"段（5 源清单 + SaaS 对比 + Alpha Vantage 免费 tier 详解）
2. **合规边界明确化**：5 源中 4 个免 key（Yahoo / SEC / HKEX / FRED），1 个可选（Alpha Vantage）
3. **质检闭环**：5 必检 + 3 推荐 + 4 类退出码契约 + 5 pytest 单测

---

## 版本信息

- **Version**: 1.0
- **Base**: V0.0（新 skill）
- **Upgrade Date**: 2026-07-27
- **Upgrade Trigger**: simonlin1212/global-stock-data V1.0.1 集成（阶段 25.1）
- **Author**: 天龙引擎集成
- **License**: Apache-2.0（与上游一致）
- **Triggers**: 22 个新增关键词

---

## 与 a-stock-data-bridge 关系

| 维度 | a-stock-data-bridge（阶段 25）| global-stock-data-bridge（阶段 25.1）|
|------|-------------------------------|--------------------------------------|
| 覆盖市场 | A 股（沪深北）| 美股 + 港股 + 中概股 |
| 端点数 | 43 | 17 |
| 数据源 | 15 | 5 |
| 架构 | 10 层（行情/研报/信号/资金面/新闻/基础/公告/打板/ETF/舆情）| 7 层（行情/财务/技术/新闻/公告/估值/同业）|
| 节流入口 | `em_get()` ≥1s | `em_global_get()` ≥1s |
| 备胎数 | 3 官方 | 2-3 备胎（按端点）|
| 技术指标 | ❌ 无 | ✅ MA/MACD/RSI/KDJ/布林带（计算层）|

**协同关系**：同一作者同协议同范式，两 skill 共享 28-10 财经数据底座师（V1.1 起统一调用）。